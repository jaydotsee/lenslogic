#!/usr/bin/env python3

import argparse
import logging
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

from modules.backup_manager import BackupManager
from modules.config_wizard import ConfigurationWizard
from modules.duplicate_detector import DuplicateDetector
from modules.enhanced_exif_extractor import EnhancedExifExtractor
from modules.file_renamer import FileRenamer
from modules.folder_organizer import FolderOrganizer
from modules.geolocation import GeolocationService
from modules.image_processor import ImageProcessor
from modules.interactive_menu import InteractiveMenu
from modules.session_detector import SessionDetector
from modules.statistics_generator import StatisticsGenerator
from modules.xmp_analyzer import XMPAnalyzer
from utils.branding import print_logo
from utils.config_manager import ConfigManager
from utils.progress_tracker import ProgressTracker


class LensLogic:
    def __init__(self, config_path: Optional[str] = None, args: Optional[Dict[str, Any]] = None):
        self.config_manager = ConfigManager(config_path)

        # Store custom destination separately - don't save to config
        self.custom_destination = None
        if args:
            self.custom_destination = args.get("custom_destination")
            # Remove custom_destination before passing to config manager
            config_args = {k: v for k, v in args.items() if k != "custom_destination"}
            self.config_manager.update_from_args(config_args)

        self.config = self.config_manager.config
        self.setup_logging()

        self.progress_tracker = ProgressTracker(verbose=self.config.get("general", {}).get("verbose", True))

        self.exif_extractor = EnhancedExifExtractor()
        self.file_renamer = FileRenamer(self.config)
        self.folder_organizer = FolderOrganizer(self.config)
        self.geolocation_service = GeolocationService(self.config)
        self.duplicate_detector = DuplicateDetector(self.config)
        self.interactive_menu = InteractiveMenu(self.config_manager, self.progress_tracker)
        self.image_processor = ImageProcessor(self.config)
        self.session_detector = SessionDetector(self.config)
        self.statistics_generator = StatisticsGenerator(self.config)
        self.backup_manager = BackupManager(self.config)
        self.config_wizard = ConfigurationWizard(self.config_manager)
        self.xmp_analyzer = XMPAnalyzer(console=self.progress_tracker.console)

    def setup_logging(self):
        log_file = self.config.get("general", {}).get("log_file", "lenslogic.log")
        verbose = self.config.get("general", {}).get("verbose", True)

        log_level = logging.DEBUG if verbose else logging.INFO

        logging.basicConfig(
            level=log_level,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler(sys.stdout) if verbose else logging.NullHandler(),
            ],
        )

    def organize_photos(self, dry_run: bool = False, custom_destination: Optional[str] = None):
        source_dir = Path(self.config.get("general", {}).get("source_directory", "."))

        # Use custom destination if provided, or class custom_destination, otherwise use config destination
        if custom_destination:
            dest_dir = Path(custom_destination)
            self.progress_tracker.print_info(f"Using custom destination: {dest_dir}")
        elif self.custom_destination:
            dest_dir = Path(self.custom_destination)
            self.progress_tracker.print_info(f"Using custom destination: {dest_dir}")
        else:
            dest_dir = Path(self.config.get("general", {}).get("destination_directory", "./organized"))
        preserve_originals = self.config.get("general", {}).get("preserve_originals", True)
        skip_duplicates = self.config.get("general", {}).get("skip_duplicates", True)
        create_sidecar = self.config.get("features", {}).get("create_sidecar", True)

        if not source_dir.exists():
            self.progress_tracker.print_error(f"Source directory does not exist: {source_dir}")
            return False

        if dry_run:
            self.progress_tracker.print_info("Running in DRY RUN mode - no files will be modified")

        files = self._collect_files(source_dir)

        if not files:
            self.progress_tracker.print_warning("No supported files found in source directory")
            return False

        self.progress_tracker.print_info(f"Found {len(files)} files to process")

        if skip_duplicates and self.config.get("features", {}).get("remove_duplicates", True):
            duplicates = self.duplicate_detector.find_duplicates([str(f) for f in files])
            if duplicates:
                self.progress_tracker.print_info(f"Found {len(duplicates)} duplicate groups")

        self.progress_tracker.start_processing(len(files), "Organizing")

        success_count = 0
        failed_files = []

        for file_path in files:
            try:
                self.progress_tracker.update_file(str(file_path), "Processing")

                metadata = self.exif_extractor.extract_metadata(str(file_path))

                if self.config.get("geolocation", {}).get("enabled", True):
                    metadata = self.geolocation_service.add_location_to_metadata(metadata)

                location_info = metadata.get("location", {}) if metadata.get("location") else {}

                dest_folder = self.folder_organizer.determine_destination_path(
                    str(file_path), metadata, str(dest_dir), location_info
                )

                new_filename = self.file_renamer.generate_new_name(str(file_path), metadata, str(dest_folder))

                if dry_run:
                    # Build dry run message with geolocation info if available
                    dry_run_msg = f"{file_path.name} → {dest_folder}/{new_filename}"

                    # Add GPS coordinates if available
                    if metadata.get("gps"):
                        gps = metadata["gps"]
                        lat = gps.get("latitude", 0)
                        lon = gps.get("longitude", 0)
                        dry_run_msg += f"\n    📍 GPS: {lat:.4f}, {lon:.4f}"

                        if gps.get("altitude"):
                            dry_run_msg += f" (alt: {gps['altitude']}m)"

                    # Add location info if available
                    if location_info:
                        location_parts = []
                        if location_info.get("city"):
                            location_parts.append(location_info["city"])
                        if location_info.get("country"):
                            location_parts.append(location_info["country"])

                        if location_parts:
                            dry_run_msg += f"\n    🗺️  Location: {', '.join(location_parts)}"

                    self.progress_tracker.print_dry_run(dry_run_msg)
                    success_count += 1
                else:
                    result = self.folder_organizer.organize_file(
                        str(file_path),
                        dest_folder,
                        new_filename,
                        dry_run=False,
                        preserve_original=preserve_originals,
                    )

                    if result["success"]:
                        success_count += 1

                        if create_sidecar:
                            self.folder_organizer.create_sidecar_files(
                                str(file_path),
                                str(dest_folder / new_filename),
                                metadata,
                                dry_run=False,
                            )

                        self.progress_tracker.file_processed(
                            success=True,
                            action="copy" if preserve_originals else "move",
                            size=file_path.stat().st_size,
                            skipped=result.get("skipped", False),
                        )
                    else:
                        failed_files.append((str(file_path), result.get("error", "Unknown error")))
                        self.progress_tracker.file_processed(success=False)

            except Exception as e:
                logging.error(f"Error processing {file_path}: {e}")
                failed_files.append((str(file_path), str(e)))
                self.progress_tracker.file_processed(success=False)

        self.progress_tracker.stop_processing()
        self.progress_tracker.print_summary()

        if failed_files:
            self.progress_tracker.print_warning(f"\n{len(failed_files)} files failed to process:")
            for file, error in failed_files[:10]:
                self.progress_tracker.print_error(f"  • {Path(file).name}: {error}")
            if len(failed_files) > 10:
                self.progress_tracker.print_info(f"  ... and {len(failed_files) - 10} more")

        return success_count > 0

    def _collect_files(self, source_dir: Path) -> List[Path]:
        files = []

        all_extensions = set()
        all_extensions.update("." + ext for ext in self.config.get("file_types", {}).get("images", []))
        all_extensions.update("." + ext for ext in self.config.get("file_types", {}).get("raw", []))
        all_extensions.update("." + ext for ext in self.config.get("file_types", {}).get("videos", []))

        for extension in all_extensions:
            files.extend(source_dir.rglob(f"*{extension}"))
            files.extend(source_dir.rglob(f"*{extension.upper()}"))

        return sorted(set(files))

    def analyze_library(self):
        source_dir = self.config.get("general", {}).get("source_directory", ".")
        stats = self.folder_organizer.get_statistics(source_dir)

        if "error" in stats:
            self.progress_tracker.print_error(stats["error"])
            return

        table = self.progress_tracker.create_statistics_table(stats)
        self.progress_tracker.console.print(table)

        if stats.get("file_types"):
            self.progress_tracker.console.print("\n[bold]File Type Distribution:[/bold]")
            for ext, count in sorted(stats["file_types"].items(), key=lambda x: x[1], reverse=True)[:10]:
                self.progress_tracker.console.print(f"  {ext}: {count} files")

    def export_gps_locations(self, output_path: Optional[str] = None):
        if not output_path:
            output_path = "photo_locations.kml"

        source_dir = Path(self.config.get("general", {}).get("source_directory", "."))
        files = self._collect_files(source_dir)

        photos_with_location = []

        self.progress_tracker.print_info(f"Extracting GPS data from {len(files)} files...")

        for file_path in files:
            metadata = self.exif_extractor.extract_metadata(str(file_path))

            if metadata.get("gps"):
                photos_with_location.append(
                    {
                        "file": str(file_path),
                        "gps": metadata["gps"],
                        "datetime_original": metadata.get("datetime_original"),
                        "camera_model": metadata.get("camera_model"),
                    }
                )

        if photos_with_location:
            for photo in photos_with_location:
                coords = self.geolocation_service.extract_gps_from_metadata({"gps": photo["gps"]})
                if coords:
                    lat, lon = coords
                    location = self.geolocation_service.get_location_info(lat, lon)
                    if location:
                        photo["location"] = location

            self.geolocation_service.export_kml(photos_with_location, output_path)
            self.progress_tracker.print_success(f"Exported {len(photos_with_location)} locations to {output_path}")
        else:
            self.progress_tracker.print_warning("No photos with GPS data found")

    def run_interactive(self):
        while True:
            action = self.interactive_menu.main_menu()

            if action == "organize":
                if self.interactive_menu.confirm_action("Start organizing?"):
                    self.organize_photos(dry_run=False)
                    input("\nPress Enter to continue...")

            elif action == "organize_custom":
                custom_dest = self.interactive_menu.get_custom_destination()
                if custom_dest and self.interactive_menu.confirm_action(f"Start organizing to {custom_dest}?"):
                    self.organize_photos(dry_run=False, custom_destination=custom_dest)
                    input("\nPress Enter to continue...")

            elif action == "configure":
                while self.interactive_menu.configure_menu():
                    pass

            elif action == "source":
                source = self.interactive_menu.get_user_input(
                    "Enter source directory:",
                    self.config_manager.get("general.source_directory", "."),
                )
                if source:
                    self.config_manager.set("general.source_directory", source)

            elif action == "destination":
                destination = self.interactive_menu.get_user_input(
                    "Enter destination directory:",
                    self.config_manager.get("general.destination_directory", "./organized"),
                )
                if destination:
                    self.config_manager.set("general.destination_directory", destination)

            elif action == "preview":
                self.organize_photos(dry_run=True)
                input("\nPress Enter to continue...")

            elif action == "analyze":
                self.analyze_library()
                input("\nPress Enter to continue...")

            elif action == "analyze_xmp":
                library_path = self.interactive_menu.get_user_input(
                    "Enter library directory path (or press Enter for source directory):",
                    self.config.get("general", {}).get("source_directory", "."),
                )
                output_path = self.interactive_menu.get_user_input("Enter output directory for reports (optional):", "")
                if library_path:
                    self.analyze_xmp_library(library_path, output_path or None)
                input("\nPress Enter to continue...")

            elif action == "export_gps":
                output = self.interactive_menu.get_user_input("Enter output file path:", "photo_locations.kml")
                if output:
                    self.export_gps_locations(output)
                input("\nPress Enter to continue...")

            elif action == "advanced":
                while self.interactive_menu.advanced_menu():
                    pass

            elif action == "explain_config":
                self.interactive_menu.explain_config_settings()
                input("\nPress Enter to continue...")

            elif action == "backup":
                while self.interactive_menu.backup_restore_menu():
                    pass

            elif action == "save":
                self.config_manager.save_user_config()
                self.progress_tracker.print_success("Configuration saved")
                input("\nPress Enter to continue...")

            elif action == "exit":
                self.progress_tracker.print_info("Goodbye!")
                break

    def generate_advanced_statistics(self, output_dir: Optional[str] = None):
        """Generate comprehensive statistics with charts"""
        source_dir = self.config.get("general", {}).get("source_directory", ".")
        files = self._collect_files(Path(source_dir))

        if not files:
            self.progress_tracker.print_warning("No files found for analysis")
            return

        # Extract metadata for all files
        self.progress_tracker.print_info(f"Analyzing {len(files)} files for statistics...")
        photos_metadata = []

        self.progress_tracker.start_processing(len(files), "Extracting metadata")

        for file_path in files:
            try:
                self.progress_tracker.update_file(str(file_path), "Analyzing")
                metadata = self.exif_extractor.extract_metadata(str(file_path))

                # Add location info if available
                if self.config.get("geolocation", {}).get("enabled", True):
                    metadata = self.geolocation_service.add_location_to_metadata(metadata)

                photos_metadata.append(metadata)
                self.progress_tracker.file_processed(success=True)

            except Exception as e:
                logging.error(f"Error analyzing {file_path}: {e}")
                self.progress_tracker.file_processed(success=False)

        self.progress_tracker.stop_processing()

        # Generate statistics
        stats = self.statistics_generator.generate_library_statistics(photos_metadata)

        # Display statistics
        self.statistics_generator.display_statistics(stats)

        # Generate charts
        if output_dir or self.config.get("statistics", {}).get("enable_charts", True):
            chart_dir = output_dir or self.config.get("statistics", {}).get("chart_output_dir", "charts")
            charts = self.statistics_generator.generate_charts(stats, chart_dir)

            if charts:
                self.progress_tracker.print_success(f"Generated {len(charts)} charts in {chart_dir}/")
                for chart in charts:
                    self.progress_tracker.print_info(f"  • {Path(chart).name}")

    def detect_sessions(self, organize_by_sessions: bool = False):
        """Detect and optionally organize photos by shooting sessions"""
        source_dir = self.config.get("general", {}).get("source_directory", ".")
        files = self._collect_files(Path(source_dir))

        if not files:
            self.progress_tracker.print_warning("No files found for session detection")
            return

        # Extract metadata for session detection
        self.progress_tracker.print_info(f"Analyzing {len(files)} files for sessions...")
        photos_metadata = []

        for file_path in files:
            try:
                metadata = self.exif_extractor.extract_metadata(str(file_path))
                photos_metadata.append(metadata)
            except Exception as e:
                logging.error(f"Error extracting metadata from {file_path}: {e}")

        # Detect sessions
        sessions = self.session_detector.detect_sessions(photos_metadata)

        if not sessions:
            self.progress_tracker.print_warning("No sessions detected")
            return

        # Display session information
        self.progress_tracker.print_success(f"Detected {len(sessions)} shooting sessions:")

        for session in sessions:
            duration_str = ""
            if session.get("duration"):
                duration = session["duration"]
                hours = int(duration.total_seconds() // 3600)
                minutes = int((duration.total_seconds() % 3600) // 60)
                duration_str = f" ({hours}h {minutes}m)" if hours else f" ({minutes}m)"

            location_str = f" at {session['location_name']}" if session.get("location_name") else ""

            self.progress_tracker.print_info(
                f"  • {session['session_name']}: {session['photo_count']} photos{duration_str}{location_str}"
            )

        # Show session statistics
        session_stats = self.session_detector.get_session_statistics(sessions)
        self.progress_tracker.print_info("\nSession Statistics:")
        self.progress_tracker.print_info(f"  • Average photos per session: {session_stats['avg_photos_per_session']}")
        self.progress_tracker.print_info(f"  • Cameras used: {session_stats['unique_cameras']}")
        self.progress_tracker.print_info(f"  • Locations visited: {session_stats['unique_locations']}")

        # Optionally organize by sessions
        if organize_by_sessions:
            dest_dir = self.config.get("general", {}).get("destination_directory", "./organized")
            result = self.session_detector.organize_by_sessions(
                sessions,
                dest_dir,
                "{session_name}",
                dry_run=self.config.get("general", {}).get("dry_run", False),
            )

            self.progress_tracker.print_success(
                f"Organized {result['files_organized']} files into {result['sessions_processed']} session folders"
            )

    def optimize_for_social_media(self, platform: str, format_type: str = "post", output_dir: Optional[str] = None):
        """Optimize photos for social media platforms"""
        source_dir = self.config.get("general", {}).get("source_directory", ".")
        files = self._collect_files(Path(source_dir))

        if not files:
            self.progress_tracker.print_warning("No files found for optimization")
            return

        # Filter to image files only
        image_files = [f for f in files if f.suffix.lower() in {".jpg", ".jpeg", ".png", ".tiff", ".heic", ".heif"}]

        if not image_files:
            self.progress_tracker.print_warning("No image files found for social media optimization")
            return

        self.progress_tracker.print_info(f"Optimizing {len(image_files)} images for {platform} ({format_type})")

        # Process images
        results = self.image_processor.batch_optimize_for_social_media(
            [str(f) for f in image_files],
            platform,
            format_type,
            output_dir or "./optimized",
            dry_run=self.config.get("general", {}).get("dry_run", False),
        )

        # Report results
        successful = sum(1 for r in results if r["optimized"])
        failed = len(results) - successful

        self.progress_tracker.print_success(f"Successfully optimized {successful} images")
        if failed > 0:
            self.progress_tracker.print_warning(f"Failed to optimize {failed} images")

        # Show output directory
        if results and results[0].get("output_path"):
            output_path = Path(results[0]["output_path"]).parent
            self.progress_tracker.print_info(f"Optimized images saved to: {output_path}")

    def backup_photos(self, destinations: Optional[List[str]] = None, verify: bool = True):
        """Backup organized photos to specified destinations"""
        # Backup the organized photos (destination directory), not the source directory
        source_dir = self.config.get("general", {}).get("destination_directory", "./organized")

        if not destinations:
            destinations = self.config.get("backup", {}).get("destinations", [])

        if not destinations:
            self.progress_tracker.print_warning("No backup destinations configured")
            self.progress_tracker.print_info("Use --config-wizard to set up backup destinations")
            return

        # Perform incremental sync
        self.progress_tracker.print_info(f"Starting backup to {len(destinations)} destination(s)...")

        result = self.backup_manager.incremental_sync(
            source_dir,
            destinations,
            dry_run=self.config.get("general", {}).get("dry_run", False),
        )

        # Report results
        self.progress_tracker.print_success("Backup completed:")
        self.progress_tracker.print_info(f"  • Files copied: {result['total_copied']}")
        self.progress_tracker.print_info(f"  • Files updated: {result['total_updated']}")
        self.progress_tracker.print_info(f"  • Files deleted: {result['total_deleted']}")

        if result["total_errors"] > 0:
            self.progress_tracker.print_warning(f"  • Errors: {result['total_errors']}")

        # Verify backups if requested
        if verify and self.config.get("backup", {}).get("enable_verification", True):
            self.progress_tracker.print_info("\nVerifying backups...")

            for dest in destinations:
                verification = self.backup_manager.verify_backup(source_dir, dest, quick_mode=True)

                if verification["integrity_score"] >= 95:
                    self.progress_tracker.print_success(f"✓ {dest}: {verification['integrity_score']:.1f}% integrity")
                else:
                    self.progress_tracker.print_warning(f"⚠ {dest}: {verification['integrity_score']:.1f}% integrity")

                    if verification["missing_files"]:
                        self.progress_tracker.print_warning(f"    Missing files: {len(verification['missing_files'])}")
                    if verification["corrupted_files"]:
                        self.progress_tracker.print_warning(
                            f"    Corrupted files: {len(verification['corrupted_files'])}"
                        )

    def run_config_wizard(self, quick: bool = False):
        """Run the configuration wizard"""
        if quick:
            success = self.config_wizard.quick_setup()
        else:
            success = self.config_wizard.run_wizard()

        if success:
            # Reload configuration
            self.config_manager.load_config()
            self.config = self.config_manager.config
            self.progress_tracker.print_success("Configuration wizard completed successfully!")
        else:
            self.progress_tracker.print_info("Configuration wizard cancelled or failed")

    def analyze_xmp_library(self, library_path: Optional[str] = None, output_dir: Optional[str] = None):
        """Analyze photo library using XMP sidecar files"""
        if not library_path:
            library_path = self.config.get("general", {}).get("source_directory", ".")

        # Ensure library_path is a string before converting to Path
        library_path = str(library_path) if library_path else "."
        library_path_obj = Path(library_path)
        if not library_path_obj.exists():
            self.progress_tracker.print_error(f"Library directory does not exist: {library_path}")
            return

        self.progress_tracker.print_info(f"🔍 Analyzing XMP library at: {library_path}")

        try:
            # Perform analysis
            analysis = self.xmp_analyzer.analyze_library(str(library_path), output_dir)

            # Display results
            self.xmp_analyzer.display_analysis(analysis)

            # Show summary
            summary = analysis.get("summary", {})
            if summary.get("total_files", 0) > 0:
                self.progress_tracker.print_success(f"✅ Analysis complete! Processed {summary['total_files']} files")
                if output_dir:
                    self.progress_tracker.print_info(f"📄 Detailed reports saved to: {output_dir}")
            else:
                self.progress_tracker.print_warning("No XMP files found in the specified directory")

        except Exception as e:
            self.progress_tracker.print_error(f"Analysis failed: {e}")

    def show_exif_info(self):
        """Display metadata extraction capabilities and information"""
        self.progress_tracker.print_info("Metadata Extraction Information:")

        # Image metadata information
        method = self.exif_extractor.get_extraction_method()
        self.progress_tracker.print_info(f"  • Image Method: {method}")

        version = self.exif_extractor.get_exiftool_version()
        if version:
            self.progress_tracker.print_info(f"  • ExifTool Version: {version}")

        supported_formats = self.exif_extractor.get_supported_formats()
        self.progress_tracker.print_info(f"  • Image Formats: {len(supported_formats)} types")

        # Show some example formats
        raw_formats = [fmt for fmt in supported_formats if fmt in ["nef", "cr2", "cr3", "arw", "orf", "dng"]]
        self.progress_tracker.print_info(f"  • RAW Formats: {', '.join(raw_formats[:10])}")

        # Video metadata information
        if hasattr(self.exif_extractor, "video_extractor") and self.exif_extractor.video_extractor:
            video_extractor = self.exif_extractor.video_extractor
            video_method = video_extractor.get_extraction_method()
            self.progress_tracker.print_info(f"  • Video Method: {video_method}")

            video_formats = video_extractor.get_supported_formats()
            self.progress_tracker.print_info(f"  • Video Formats: {len(video_formats)} types")

            # Show some example video formats
            common_video = [fmt for fmt in video_formats if fmt in ["mp4", "mov", "avi", "mkv", "webm", "mxf"]]
            self.progress_tracker.print_info(f"  • Video Examples: {', '.join(common_video[:10])}")

            mediainfo_version = video_extractor.get_mediainfo_version()
            if mediainfo_version:
                self.progress_tracker.print_info(f"  • MediaInfo Version: {mediainfo_version}")
        else:
            self.progress_tracker.print_info("  • Video Method: Not available")
            self.progress_tracker.print_info("  • Video Formats: Limited support")

        # Test extraction on a sample file if available
        source_dir = self.config.get("general", {}).get("source_directory", ".")
        files = self._collect_files(Path(source_dir))

        if files:
            sample_file = files[0]
            self.progress_tracker.print_info(f"\n  • Testing with: {sample_file.name}")

            try:
                metadata = self.exif_extractor.extract_metadata(str(sample_file))

                # Show key metadata
                if metadata.get("camera_make") or metadata.get("camera_model"):
                    camera = f"{metadata.get('camera_make', '')} {metadata.get('camera_model', '')}".strip()
                    self.progress_tracker.print_info(f"    Camera: {camera}")

                if metadata.get("lens_model"):
                    self.progress_tracker.print_info(f"    Lens: {metadata['lens_model']}")

                if metadata.get("datetime_original"):
                    self.progress_tracker.print_info(f"    Date: {metadata['datetime_original']}")

                if metadata.get("gps"):
                    self.progress_tracker.print_info("    GPS: Available")

                # Count metadata fields
                fields_count = len(
                    [k for k, v in metadata.items() if v is not None and k not in ["file_path", "file_name"]]
                )
                self.progress_tracker.print_info(f"    Metadata Fields: {fields_count}")

            except Exception as e:
                self.progress_tracker.print_warning(f"    Test failed: {e}")
        else:
            self.progress_tracker.print_info("\n  • No files found to test with")


def main():
    parser = argparse.ArgumentParser(
        description="LensLogic - Smart photo organization powered by metadata",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    # Basic options
    parser.add_argument("-s", "--source", type=str, help="Source directory containing photos")
    parser.add_argument(
        "-d",
        "--destination",
        type=str,
        help="Destination directory for organized photos",
    )
    parser.add_argument(
        "--custom-destination",
        type=str,
        help="Custom destination directory for this run only (overrides config)",
    )
    parser.add_argument("-c", "--config", type=str, help="Path to configuration file")
    parser.add_argument("--dry-run", action="store_true", help="Preview changes without modifying files")
    parser.add_argument("-p", "--pattern", type=str, help="File naming pattern")
    parser.add_argument("-f", "--folder-structure", type=str, help="Folder organization structure")
    parser.add_argument(
        "--create-xmp",
        action="store_true",
        help="Create XMP sidecar files with metadata",
    )
    parser.add_argument("--no-xmp", action="store_true", help="Disable XMP sidecar file creation")
    parser.add_argument("--no-preserve", action="store_true", help="Move files instead of copying")
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose output")
    parser.add_argument("--quiet", action="store_true", help="Suppress output except errors")

    # Analysis and statistics
    parser.add_argument("--analyze", action="store_true", help="Analyze library statistics")
    parser.add_argument(
        "--analyze-xmp",
        action="store_true",
        help="Analyze library using XMP sidecar files",
    )
    parser.add_argument(
        "--xmp-library",
        type=str,
        help="Library directory for XMP analysis (default: source directory)",
    )
    parser.add_argument(
        "--xmp-output",
        type=str,
        help="Output directory for detailed XMP analysis reports",
    )
    parser.add_argument(
        "--advanced-stats",
        action="store_true",
        help="Generate comprehensive statistics with charts",
    )
    parser.add_argument("--chart-dir", type=str, help="Directory for generated charts")

    # Session detection
    parser.add_argument("--detect-sessions", action="store_true", help="Detect shooting sessions")
    parser.add_argument("--organize-sessions", action="store_true", help="Organize photos by sessions")

    # Social media optimization
    parser.add_argument(
        "--social-media",
        type=str,
        choices=["instagram", "facebook", "twitter", "linkedin"],
        help="Optimize images for social media platform",
    )
    parser.add_argument(
        "--social-format",
        type=str,
        default="post",
        help="Social media format (post, story, cover, etc.)",
    )
    parser.add_argument("--social-output", type=str, help="Output directory for social media files")

    # Backup and sync
    parser.add_argument("--backup", action="store_true", help="Backup photos to configured destinations")
    parser.add_argument("--backup-to", type=str, nargs="+", help="Backup to specific destinations")
    parser.add_argument("--verify-backup", action="store_true", help="Verify backup integrity")

    # Configuration
    parser.add_argument("--config-wizard", action="store_true", help="Run configuration wizard")
    parser.add_argument("--quick-setup", action="store_true", help="Run quick configuration setup")
    parser.add_argument("--reset-config", action="store_true", help="Reset configuration to defaults")

    # Legacy options
    parser.add_argument(
        "--export-gps",
        type=str,
        metavar="FILE",
        help="Export GPS locations to KML file",
    )
    parser.add_argument("--interactive", "-i", action="store_true", help="Launch interactive menu")
    parser.add_argument("--save-config", action="store_true", help="Save current configuration")
    parser.add_argument("--logo", action="store_true", help="Display LensLogic logo")
    parser.add_argument("--exif-info", action="store_true", help="Show EXIF extraction capabilities")

    args = parser.parse_args()

    args_dict = {
        "source": args.source,
        "destination": args.destination,
        "custom_destination": args.custom_destination,
        "dry_run": args.dry_run,
        "verbose": args.verbose and not args.quiet,
        "pattern": args.pattern,
        "folder_structure": args.folder_structure,
        "preserve_originals": not args.no_preserve,
        "create_xmp": args.create_xmp,
        "no_xmp": args.no_xmp,
    }

    args_dict = {k: v for k, v in args_dict.items() if v is not None}

    # Handle logo display
    if args.logo:
        print_logo("full")
        return

    # Handle configuration wizard
    if args.config_wizard or args.quick_setup or args.reset_config:
        organizer = LensLogic(config_path=args.config, args=args_dict)

        if args.config_wizard:
            organizer.run_config_wizard(quick=False)
        elif args.quick_setup:
            organizer.run_config_wizard(quick=True)
        elif args.reset_config:
            organizer.config_wizard.reset_configuration()
        return

    organizer = LensLogic(config_path=args.config, args=args_dict)

    # Handle different modes of operation
    if args.interactive:
        organizer.run_interactive()

    elif args.analyze:
        organizer.analyze_library()

    elif args.analyze_xmp:
        organizer.analyze_xmp_library(args.xmp_library, args.xmp_output)

    elif args.advanced_stats:
        organizer.generate_advanced_statistics(args.chart_dir)

    elif args.detect_sessions:
        organizer.detect_sessions(organize_by_sessions=args.organize_sessions)

    elif args.social_media:
        organizer.optimize_for_social_media(args.social_media, args.social_format, args.social_output)

    elif args.backup:
        organizer.backup_photos(args.backup_to, verify=True)

    elif args.backup_to:
        organizer.backup_photos(args.backup_to, verify=args.verify_backup)

    elif args.verify_backup:
        if args.backup_to:
            destinations = args.backup_to
        else:
            destinations = organizer.config.get("backup", {}).get("destinations", [])

        if not destinations:
            organizer.progress_tracker.print_warning("No backup destinations to verify")
        else:
            # Verify against organized photos (destination directory), not source directory
            source_dir = organizer.config.get("general", {}).get("destination_directory", "./organized")
            for dest in destinations:
                verification = organizer.backup_manager.verify_backup(source_dir, dest, quick_mode=False)
                organizer.progress_tracker.print_info(
                    f"Verification complete for {dest}: {verification['integrity_score']:.1f}% integrity"
                )

    elif args.export_gps:
        organizer.export_gps_locations(args.export_gps)

    elif args.save_config:
        organizer.config_manager.save_user_config()
        print("Configuration saved successfully")

    elif args.exif_info:
        organizer.show_exif_info()

    elif args.source or args.custom_destination or args.dry_run:
        # Direct organization with CLI arguments
        dry_run = args_dict.get("dry_run", False)
        custom_dest = args_dict.get("custom_destination")

        if dry_run:
            organizer.progress_tracker.print_info("Running in DRY RUN mode - no files will be modified")

        organizer.organize_photos(dry_run=dry_run, custom_destination=custom_dest)

    else:
        # Default action: launch interactive mode
        organizer.run_interactive()


if __name__ == "__main__":
    main()
