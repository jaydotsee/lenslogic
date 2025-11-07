import hashlib
import json
import logging
import shutil
import time
from datetime import datetime
from pathlib import Path
from typing import Any

from send2trash import send2trash

logger = logging.getLogger(__name__)


class BackupManager:
    def __init__(self, config: dict[str, Any]):
        self.config = config
        self.backup_config = config.get("backup", {})
        self.verification_enabled = self.backup_config.get("enable_verification", True)
        self.incremental_mode = self.backup_config.get("incremental_mode", True)
        self.checksum_cache_file = self.backup_config.get("checksum_cache", ".lenslogic_checksums.json")
        self.backup_destinations = self.backup_config.get("destinations", [])
        self.exclude_patterns = self.backup_config.get("exclude_patterns", [])

        self.checksum_cache = self._load_checksum_cache()

    def _load_checksum_cache(self) -> dict[str, dict[str, Any]]:
        """Load checksum cache from file"""
        try:
            if Path(self.checksum_cache_file).exists():
                with open(self.checksum_cache_file) as f:
                    return json.load(f)
        except Exception as e:
            logger.warning(f"Could not load checksum cache: {e}")

        return {}

    def _save_checksum_cache(self):
        """Save checksum cache to file"""
        try:
            with open(self.checksum_cache_file, "w") as f:
                json.dump(self.checksum_cache, f, indent=2, default=str)
        except Exception as e:
            logger.warning(f"Could not save checksum cache: {e}")

    def calculate_file_checksum(self, file_path: str, algorithm: str = "sha256") -> str | None:
        """Calculate checksum for a file"""
        file_path_obj = Path(file_path)

        if not file_path_obj.exists():
            return None

        # Check cache first
        file_key = str(file_path_obj)
        file_stat = file_path_obj.stat()
        file_signature = f"{file_stat.st_size}_{file_stat.st_mtime}"

        if file_key in self.checksum_cache:
            cached_data = self.checksum_cache[file_key]
            if cached_data.get("signature") == file_signature:
                return cached_data.get("checksum")

        # Calculate checksum
        try:
            hasher = hashlib.new(algorithm)

            with open(file_path_obj, "rb") as f:
                for chunk in iter(lambda: f.read(65536), b""):
                    hasher.update(chunk)

            checksum = hasher.hexdigest()

            # Cache the result
            self.checksum_cache[file_key] = {
                "checksum": checksum,
                "signature": file_signature,
                "algorithm": algorithm,
                "calculated_at": datetime.now().isoformat(),
            }

            return checksum

        except Exception as e:
            logger.error(f"Error calculating checksum for {file_path_obj}: {e}")
            return None

    def verify_backup(self, source_dir: str, backup_dir: str, quick_mode: bool = False) -> dict[str, Any]:
        """Verify backup integrity against source"""
        source_path = Path(source_dir)
        backup_path = Path(backup_dir)

        result = {
            "verified_files": 0,
            "missing_files": [],
            "corrupted_files": [],
            "extra_files": [],
            "verification_errors": [],
            "verification_time": 0,
            "integrity_score": 0.0,
        }

        if not source_path.exists():
            result["verification_errors"].append(f"Source directory does not exist: {source_path}")
            return result

        if not backup_path.exists():
            result["verification_errors"].append(f"Backup directory does not exist: {backup_path}")
            return result

        start_time = time.time()

        try:
            # Get all files from source
            source_files = self._get_file_list(source_path)
            backup_files = self._get_file_list(backup_path)

            # Convert to relative paths for comparison
            source_relatives = {f.relative_to(source_path): f for f in source_files}
            backup_relatives = {f.relative_to(backup_path): f for f in backup_files}

            # Find missing files
            missing = set(source_relatives.keys()) - set(backup_relatives.keys())
            result["missing_files"] = [str(f) for f in missing]

            # Find extra files
            extra = set(backup_relatives.keys()) - set(source_relatives.keys())
            result["extra_files"] = [str(f) for f in extra]

            # Verify existing files
            common_files = set(source_relatives.keys()) & set(backup_relatives.keys())

            for rel_path in common_files:
                source_file = source_relatives[rel_path]
                backup_file = backup_relatives[rel_path]

                if quick_mode:
                    # Quick verification using size and modification time
                    if not self._quick_file_compare(source_file, backup_file):
                        result["corrupted_files"].append(str(rel_path))
                else:
                    # Full checksum verification
                    if not self._full_file_compare(source_file, backup_file):
                        result["corrupted_files"].append(str(rel_path))

                result["verified_files"] += 1

            # Calculate integrity score
            total_expected = len(source_relatives)
            verified_intact = result["verified_files"] - len(result["corrupted_files"])
            result["integrity_score"] = (verified_intact / total_expected * 100) if total_expected > 0 else 0

        except Exception as e:
            result["verification_errors"].append(f"Verification error: {e}")
            logger.error(f"Backup verification error: {e}")

        result["verification_time"] = time.time() - start_time
        self._save_checksum_cache()

        return result

    def _get_file_list(self, directory: Path) -> list[Path]:
        """Get list of all files in directory, excluding patterns"""
        files = []

        for file_path in directory.rglob("*"):
            if file_path.is_file():
                # Check exclude patterns
                if not self._should_exclude_file(file_path):
                    files.append(file_path)

        return files

    def _should_exclude_file(self, file_path: Path) -> bool:
        """Check if file should be excluded based on patterns"""
        file_str = str(file_path)

        for pattern in self.exclude_patterns:
            if pattern in file_str:
                return True

        # Exclude common cache and system files
        exclude_names = {".DS_Store", "Thumbs.db", ".lenslogic_checksums.json"}
        if file_path.name in exclude_names:
            return True

        return False

    def _quick_file_compare(self, file1: Path, file2: Path) -> bool:
        """Quick file comparison using size and modification time"""
        try:
            stat1 = file1.stat()
            stat2 = file2.stat()

            return stat1.st_size == stat2.st_size and abs(stat1.st_mtime - stat2.st_mtime) < 2  # 2 second tolerance
        except Exception:
            return False

    def _full_file_compare(self, file1: Path, file2: Path) -> bool:
        """Full file comparison using checksums"""
        try:
            checksum1 = self.calculate_file_checksum(str(file1))
            checksum2 = self.calculate_file_checksum(str(file2))

            return checksum1 == checksum2 and checksum1 is not None
        except Exception:
            return False

    def incremental_sync(self, source_dir: str, destination_dirs: list[str], dry_run: bool = False) -> dict[str, Any]:
        """Perform incremental sync to multiple destinations"""
        source_path = Path(source_dir)

        result = {
            "source_scanned": 0,
            "destinations": {},
            "total_copied": 0,
            "total_updated": 0,
            "total_deleted": 0,
            "total_errors": 0,
            "sync_time": 0,
        }

        if not source_path.exists():
            result["error"] = f"Source directory does not exist: {source_path}"
            return result

        start_time = time.time()

        try:
            # Scan source files
            source_files = self._get_file_list(source_path)
            result["source_scanned"] = len(source_files)

            # Create source file index
            source_index = {}
            for file_path in source_files:
                rel_path = file_path.relative_to(source_path)
                source_index[rel_path] = {
                    "path": file_path,
                    "size": file_path.stat().st_size,
                    "mtime": file_path.stat().st_mtime,
                    "checksum": None,  # Calculate on demand
                }

            # Sync to each destination
            for dest_dir in destination_dirs:
                logger.info(f"Starting sync to destination: {dest_dir}")
                try:
                    dest_result = self._sync_to_destination(source_path, source_index, dest_dir, dry_run)
                    result["destinations"][dest_dir] = dest_result

                    result["total_copied"] += dest_result["files_copied"]
                    result["total_updated"] += dest_result["files_updated"]
                    result["total_deleted"] += dest_result["files_deleted"]
                    result["total_errors"] += len(dest_result["errors"])

                    logger.info(
                        f"Completed sync to {dest_dir}: {dest_result['files_copied']} copied, {dest_result['files_updated']} updated"
                    )

                except Exception as e:
                    logger.error(f"Failed to sync to destination {dest_dir}: {e}")
                    # Create error result for this destination
                    error_result = {
                        "files_copied": 0,
                        "files_updated": 0,
                        "files_deleted": 0,
                        "files_skipped": 0,
                        "errors": [f"Destination sync failed: {e}"],
                    }
                    result["destinations"][dest_dir] = error_result
                    result["total_errors"] += 1

        except Exception as e:
            result["error"] = f"Sync error: {e}"
            logger.error(f"Incremental sync error: {e}")

        result["sync_time"] = time.time() - start_time
        self._save_checksum_cache()

        return result

    def _sync_to_destination(
        self, source_path: Path, source_index: dict, dest_dir: str, dry_run: bool
    ) -> dict[str, Any]:
        """Sync source to a single destination"""
        dest_path = Path(dest_dir)

        result = {
            "files_copied": 0,
            "files_updated": 0,
            "files_deleted": 0,
            "files_skipped": 0,
            "errors": [],
        }

        try:
            # Create destination if it doesn't exist
            if not dry_run:
                dest_path.mkdir(parents=True, exist_ok=True)

            # Get existing files in destination
            dest_files = {}
            if dest_path.exists():
                for file_path in self._get_file_list(dest_path):
                    rel_path = file_path.relative_to(dest_path)
                    dest_files[rel_path] = {
                        "path": file_path,
                        "size": file_path.stat().st_size,
                        "mtime": file_path.stat().st_mtime,
                    }

            # Process source files
            for rel_path, source_info in source_index.items():
                dest_file_path = dest_path / rel_path

                if rel_path in dest_files:
                    # File exists, check if update needed
                    dest_info = dest_files[rel_path]

                    if self._needs_update(source_info, dest_info):
                        # Update needed
                        if dry_run:
                            logger.info(f"[DRY RUN] Would update: {dest_file_path}")
                        else:
                            if self._copy_file(source_info["path"], dest_file_path):
                                result["files_updated"] += 1
                            else:
                                result["errors"].append(f"Failed to update: {rel_path}")
                    else:
                        result["files_skipped"] += 1
                else:
                    # New file, copy it
                    if dry_run:
                        logger.info(f"[DRY RUN] Would copy: {dest_file_path}")
                    else:
                        if self._copy_file(source_info["path"], dest_file_path):
                            result["files_copied"] += 1
                        else:
                            result["errors"].append(f"Failed to copy: {rel_path}")

            # Handle files that exist in destination but not in source
            for rel_path in dest_files:
                if rel_path not in source_index:
                    dest_file_path = dest_path / rel_path

                    if dry_run:
                        logger.info(f"[DRY RUN] Would delete: {dest_file_path}")
                    else:
                        try:
                            if self.backup_config.get("use_trash", True):
                                send2trash(str(dest_file_path))
                            else:
                                dest_file_path.unlink()
                            result["files_deleted"] += 1
                        except Exception as e:
                            result["errors"].append(f"Failed to delete {rel_path}: {e}")

        except Exception as e:
            result["errors"].append(f"Destination sync error: {e}")

        return result

    def _needs_update(self, source_info: dict, dest_info: dict) -> bool:
        """Check if destination file needs updating"""
        # Check size first (quick)
        if source_info["size"] != dest_info["size"]:
            return True

        # Check modification time
        if abs(source_info["mtime"] - dest_info["mtime"]) > 2:  # 2 second tolerance
            return True

        # If sizes and times are similar, assume no update needed
        # For thorough checking, could add checksum comparison here
        return False

    def _copy_file(self, source_path: Path, dest_path: Path) -> bool:
        """Copy file with error handling"""
        try:
            dest_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source_path, dest_path)
            return True
        except Exception as e:
            logger.error(f"Error copying {source_path} to {dest_path}: {e}")
            return False

    def get_backup_status(self, source_dir: str, backup_dirs: list[str]) -> dict[str, Any]:
        """Get status of all configured backups"""
        status = {
            "source_directory": source_dir,
            "backup_destinations": [],
            "overall_status": "unknown",
            "last_sync": None,
            "recommendations": [],
        }

        source_path = Path(source_dir)
        if not source_path.exists():
            status["overall_status"] = "error"
            status["recommendations"].append(f"Source directory does not exist: {source_dir}")
            return status

        all_good = True

        for backup_dir in backup_dirs:
            backup_path = Path(backup_dir)

            backup_status = {
                "path": backup_dir,
                "exists": backup_path.exists(),
                "accessible": False,
                "last_modified": None,
                "size_mb": 0,
                "file_count": 0,
                "status": "unknown",
            }

            if backup_path.exists():
                try:
                    backup_status["accessible"] = True

                    # Get basic stats
                    files = self._get_file_list(backup_path)
                    backup_status["file_count"] = len(files)

                    if files:
                        total_size = sum(f.stat().st_size for f in files)
                        backup_status["size_mb"] = round(total_size / (1024 * 1024), 2)

                        latest_mtime = max(f.stat().st_mtime for f in files)
                        backup_status["last_modified"] = datetime.fromtimestamp(latest_mtime)

                    backup_status["status"] = "ok"

                except Exception as e:
                    backup_status["status"] = "error"
                    backup_status["error"] = str(e)
                    all_good = False
            else:
                backup_status["status"] = "missing"
                all_good = False
                status["recommendations"].append(f"Create backup directory: {backup_dir}")

            status["backup_destinations"].append(backup_status)

        if all_good:
            status["overall_status"] = "good"
        elif any(b["status"] == "ok" for b in status["backup_destinations"]):
            status["overall_status"] = "partial"
            status["recommendations"].append("Some backups are missing or inaccessible")
        else:
            status["overall_status"] = "critical"
            status["recommendations"].append("No accessible backups found")

        return status

    def cleanup_old_backups(self, backup_dir: str, keep_days: int = 30, dry_run: bool = False) -> dict[str, Any]:
        """Clean up old backup files"""
        backup_path = Path(backup_dir)

        result = {
            "files_deleted": 0,
            "space_freed_mb": 0,
            "files_kept": 0,
            "errors": [],
        }

        if not backup_path.exists():
            result["errors"].append(f"Backup directory does not exist: {backup_dir}")
            return result

        cutoff_time = time.time() - (keep_days * 24 * 60 * 60)

        try:
            for file_path in self._get_file_list(backup_path):
                if file_path.stat().st_mtime < cutoff_time:
                    file_size = file_path.stat().st_size

                    if dry_run:
                        logger.info(f"[DRY RUN] Would delete old backup: {file_path}")
                    else:
                        try:
                            if self.backup_config.get("use_trash", True):
                                send2trash(str(file_path))
                            else:
                                file_path.unlink()

                            result["files_deleted"] += 1
                            result["space_freed_mb"] += file_size / (1024 * 1024)
                        except Exception as e:
                            result["errors"].append(f"Failed to delete {file_path}: {e}")
                else:
                    result["files_kept"] += 1

        except Exception as e:
            result["errors"].append(f"Cleanup error: {e}")

        return result

    def restore_from_backup(
        self,
        backup_dir: str,
        restore_dir: str,
        file_patterns: list[str] | None = None,
        preserve_structure: bool = True,
        overwrite_newer: bool = True,
        dry_run: bool = False,
    ) -> dict[str, Any]:
        """Restore files from backup to specified directory"""
        backup_path = Path(backup_dir)
        restore_path = Path(restore_dir)

        result = {
            "files_restored": 0,
            "files_skipped": 0,
            "total_size_restored": 0,
            "errors": [],
            "restore_time": 0,
        }

        if not backup_path.exists():
            result["errors"].append(f"Backup directory does not exist: {backup_dir}")
            return result

        start_time = time.time()

        try:
            # Get all files from backup
            backup_files = self._get_file_list(backup_path)

            if not backup_files:
                result["errors"].append("No files found in backup directory")
                return result

            # Filter files by patterns if specified
            if file_patterns:
                filtered_files = []
                for file_path in backup_files:
                    for pattern in file_patterns:
                        if pattern.lower() in str(file_path).lower():
                            filtered_files.append(file_path)
                            break
                backup_files = filtered_files

            # Restore files
            for backup_file in backup_files:
                try:
                    if preserve_structure:
                        # Maintain directory structure relative to backup root
                        rel_path = backup_file.relative_to(backup_path)
                        restore_file_path = restore_path / rel_path
                    else:
                        # Flatten all files to restore directory
                        restore_file_path = restore_path / backup_file.name

                    # Check if file already exists
                    if restore_file_path.exists() and not overwrite_newer:
                        # Compare timestamps to decide whether to restore
                        backup_mtime = backup_file.stat().st_mtime
                        restore_mtime = restore_file_path.stat().st_mtime

                        if backup_mtime <= restore_mtime:
                            result["files_skipped"] += 1
                            continue

                    if dry_run:
                        logger.info(f"[DRY RUN] Would restore: {backup_file} -> {restore_file_path}")
                        result["files_restored"] += 1
                    else:
                        # Create parent directories
                        restore_file_path.parent.mkdir(parents=True, exist_ok=True)

                        # Copy file
                        shutil.copy2(backup_file, restore_file_path)

                        result["files_restored"] += 1
                        result["total_size_restored"] += backup_file.stat().st_size

                        logger.info(f"Restored: {backup_file} -> {restore_file_path}")

                except Exception as e:
                    error_msg = f"Failed to restore {backup_file}: {e}"
                    result["errors"].append(error_msg)
                    logger.error(error_msg)

        except Exception as e:
            result["errors"].append(f"Restore error: {e}")
            logger.error(f"Restore from backup error: {e}")

        result["restore_time"] = time.time() - start_time
        return result

    def list_backup_contents(self, backup_dir: str, show_details: bool = False) -> dict[str, Any]:
        """List contents of a backup directory with optional details"""
        backup_path = Path(backup_dir)

        result = {
            "backup_path": backup_dir,
            "exists": backup_path.exists(),
            "files": [],
            "total_files": 0,
            "total_size": 0,
            "last_modified": None,
            "errors": [],
        }

        if not backup_path.exists():
            result["errors"].append(f"Backup directory does not exist: {backup_dir}")
            return result

        try:
            backup_files = self._get_file_list(backup_path)
            result["total_files"] = len(backup_files)

            if backup_files:
                total_size = 0
                latest_mtime = 0

                for file_path in backup_files:
                    try:
                        stat = file_path.stat()
                        size = stat.st_size
                        mtime = stat.st_mtime

                        total_size += size
                        latest_mtime = max(latest_mtime, mtime)

                        if show_details:
                            rel_path = file_path.relative_to(backup_path)
                            result["files"].append(
                                {
                                    "path": str(rel_path),
                                    "size": size,
                                    "modified": datetime.fromtimestamp(mtime).isoformat(),
                                    "extension": file_path.suffix.lower(),
                                }
                            )

                    except Exception as e:
                        result["errors"].append(f"Error reading {file_path}: {e}")

                result["total_size"] = total_size
                if latest_mtime > 0:
                    result["last_modified"] = datetime.fromtimestamp(latest_mtime)

        except Exception as e:
            result["errors"].append(f"Error listing backup contents: {e}")

        return result

    def get_restore_candidates(self, backup_dirs: list[str]) -> dict[str, Any]:
        """Get information about available restore sources"""
        candidates = {
            "available_backups": [],
            "unavailable_backups": [],
            "recommended_backup": None,
            "total_backups": len(backup_dirs),
        }

        backup_info = []
        unavailable_info = []

        for backup_dir in backup_dirs:
            info = self.list_backup_contents(backup_dir)
            info["backup_dir"] = backup_dir

            if info["exists"] and info["total_files"] > 0:
                backup_info.append(info)
            else:
                # Track unavailable backups for debugging
                unavailable_info.append(
                    {
                        "backup_dir": backup_dir,
                        "exists": info["exists"],
                        "total_files": info["total_files"],
                        "errors": info["errors"],
                    }
                )

        # Sort by last modified (most recent first)
        backup_info.sort(key=lambda x: x.get("last_modified") or datetime.min, reverse=True)

        candidates["available_backups"] = backup_info
        candidates["unavailable_backups"] = unavailable_info

        if backup_info:
            candidates["recommended_backup"] = backup_info[0]["backup_dir"]

        return candidates
