import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


class SessionDetector:
    def __init__(self, config: dict[str, Any]):
        self.config = config
        self.session_config = config.get("session_detection", {})
        self.time_gap_minutes = self.session_config.get("time_gap_minutes", 30)
        self.min_photos_per_session = self.session_config.get("min_photos_per_session", 3)
        self.same_location_threshold_km = self.session_config.get("same_location_threshold_km", 1.0)
        self.enable_location_grouping = self.session_config.get("enable_location_grouping", True)

    def detect_sessions(self, photos_metadata: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Detect shooting sessions from a list of photo metadata"""
        if not photos_metadata:
            return []

        # Sort photos by capture time
        sorted_photos = sorted(photos_metadata, key=lambda x: self._get_capture_time(x) or datetime.min)

        sessions = []
        current_session = []
        last_capture_time = None

        for photo in sorted_photos:
            capture_time = self._get_capture_time(photo)

            if not capture_time:
                # Handle photos without timestamps separately
                continue

            if last_capture_time is None or self._is_same_session(
                last_capture_time, capture_time, current_session, photo
            ):
                current_session.append(photo)
            else:
                # End current session and start new one
                if len(current_session) >= self.min_photos_per_session:
                    sessions.append(self._create_session_info(current_session))

                current_session = [photo]

            last_capture_time = capture_time

        # Add final session
        if len(current_session) >= self.min_photos_per_session:
            sessions.append(self._create_session_info(current_session))

        # Add session numbers and names
        for i, session in enumerate(sessions, 1):
            session["session_number"] = i
            session["session_name"] = self._generate_session_name(session, i)

        logger.info(f"Detected {len(sessions)} shooting sessions from {len(photos_metadata)} photos")
        return sessions

    def _get_capture_time(self, metadata: dict[str, Any]) -> datetime | None:
        """Extract capture time from metadata"""
        time_fields = [
            "datetime_original",
            "datetime_digitized",
            "datetime",
            "file_modified",
        ]

        for field in time_fields:
            if field in metadata and metadata[field]:
                if isinstance(metadata[field], datetime):
                    return metadata[field]
                elif isinstance(metadata[field], str):
                    try:
                        return datetime.fromisoformat(metadata[field])
                    except ValueError:
                        continue

        return None

    def _is_same_session(
        self,
        last_time: datetime,
        current_time: datetime,
        current_session: list[dict[str, Any]],
        current_photo: dict[str, Any],
    ) -> bool:
        """Determine if current photo belongs to the same session"""
        # Check time gap
        time_diff = current_time - last_time
        if time_diff > timedelta(minutes=self.time_gap_minutes):
            return False

        # Check location proximity if enabled and available
        if self.enable_location_grouping and current_session:
            if not self._is_same_location(current_session, current_photo):
                return False

        return True

    def _is_same_location(self, current_session: list[dict[str, Any]], current_photo: dict[str, Any]) -> bool:
        """Check if current photo is at the same location as session"""
        current_gps = current_photo.get("gps")
        if not current_gps:
            return True  # No GPS data, assume same location

        # Get average location of current session
        session_locations = []
        for photo in current_session:
            photo_gps = photo.get("gps")
            if photo_gps and "latitude" in photo_gps and "longitude" in photo_gps:
                session_locations.append((photo_gps["latitude"], photo_gps["longitude"]))

        if not session_locations:
            return True  # No GPS data in session

        # Calculate average session location
        avg_lat = sum(lat for lat, lon in session_locations) / len(session_locations)
        avg_lon = sum(lon for lat, lon in session_locations) / len(session_locations)

        # Check distance from current photo to session average
        current_lat = current_gps.get("latitude")
        current_lon = current_gps.get("longitude")

        if current_lat is None or current_lon is None:
            return True

        distance_km = self._calculate_distance(avg_lat, avg_lon, current_lat, current_lon)
        return distance_km <= self.same_location_threshold_km

    def _calculate_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate distance between two GPS coordinates in kilometers"""
        import math

        # Haversine formula
        earth_radius_km = 6371  # Earth radius in km

        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lon = math.radians(lon2 - lon1)

        a = math.sin(delta_lat / 2) ** 2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon / 2) ** 2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

        return earth_radius_km * c

    def _create_session_info(self, session_photos: list[dict[str, Any]]) -> dict[str, Any]:
        """Create session information from list of photos"""
        start_time = self._get_capture_time(session_photos[0])
        end_time = self._get_capture_time(session_photos[-1])

        # Calculate session statistics
        cameras = set()
        lenses = set()
        locations = []
        total_size = 0

        for photo in session_photos:
            if photo.get("camera_model"):
                cameras.add(photo["camera_model"])
            if photo.get("lens_model"):
                lenses.add(photo["lens_model"])
            if photo.get("gps"):
                gps = photo["gps"]
                if "latitude" in gps and "longitude" in gps:
                    locations.append((gps["latitude"], gps["longitude"]))
            if photo.get("file_size"):
                total_size += photo["file_size"]

        # Calculate session location (average of all GPS points)
        session_location = None
        session_location_name = None
        if locations:
            avg_lat = sum(lat for lat, lon in locations) / len(locations)
            avg_lon = sum(lon for lat, lon in locations) / len(locations)
            session_location = {"latitude": avg_lat, "longitude": avg_lon}

            # Use location from first photo with location info
            for photo in session_photos:
                if photo.get("location"):
                    session_location_name = photo["location"].get("display_name")
                    break

        duration = None
        if start_time and end_time:
            duration = end_time - start_time

        return {
            "photos": session_photos,
            "photo_count": len(session_photos),
            "start_time": start_time,
            "end_time": end_time,
            "duration": duration,
            "cameras_used": list(cameras),
            "lenses_used": list(lenses),
            "location": session_location,
            "location_name": session_location_name,
            "total_size_mb": round(total_size / (1024 * 1024), 2) if total_size else 0,
            "file_paths": [photo["file_path"] for photo in session_photos],
        }

    def _generate_session_name(self, session: dict[str, Any], session_number: int) -> str:
        """Generate a descriptive name for the session"""
        start_time = session["start_time"]
        location_name = session.get("location_name")

        if not start_time:
            return f"Session_{session_number:02d}"

        date_str = start_time.strftime("%Y%m%d")
        time_str = start_time.strftime("%H%M")

        if location_name:
            # Clean location name for filename
            clean_location = self._clean_name_for_filename(location_name)
            return f"{date_str}_{time_str}_{clean_location}"
        else:
            return f"{date_str}_{time_str}_Session_{session_number:02d}"

    def _clean_name_for_filename(self, name: str) -> str:
        """Clean name to be suitable for filename"""
        import re

        # Remove special characters and replace spaces with underscores
        clean = re.sub(r"[^\w\s-]", "", name.strip())
        clean = re.sub(r"[\s]+", "_", clean)
        return clean[:30]  # Limit length

    def organize_by_sessions(
        self,
        sessions: list[dict[str, Any]],
        base_output_dir: str,
        session_folder_pattern: str = "{session_name}",
        dry_run: bool = False,
    ) -> dict[str, Any]:
        """Organize photos into session-based folder structure"""
        result = {
            "sessions_processed": 0,
            "files_organized": 0,
            "folders_created": [],
            "errors": [],
        }

        base_path = Path(base_output_dir)

        for session in sessions:
            try:
                session_folder_name = session_folder_pattern.format(**session)
                session_path = base_path / session_folder_name

                if dry_run:
                    logger.info(f"[DRY RUN] Would create session folder: {session_path}")
                    logger.info(f"[DRY RUN] Would organize {session['photo_count']} photos")
                else:
                    session_path.mkdir(parents=True, exist_ok=True)
                    result["folders_created"].append(str(session_path))

                result["sessions_processed"] += 1
                result["files_organized"] += session["photo_count"]

            except Exception as e:
                error_msg = f"Error organizing session {session.get('session_name', 'unknown')}: {e}"
                result["errors"].append(error_msg)
                logger.error(error_msg)

        return result

    def get_session_statistics(self, sessions: list[dict[str, Any]]) -> dict[str, Any]:
        """Generate statistics about detected sessions"""
        if not sessions:
            return {"total_sessions": 0}

        total_photos = sum(session["photo_count"] for session in sessions)
        total_duration = timedelta()
        cameras = set()
        locations = set()

        for session in sessions:
            if session.get("duration"):
                total_duration += session["duration"]
            cameras.update(session.get("cameras_used", []))
            if session.get("location_name"):
                locations.add(session["location_name"])

        avg_photos_per_session = total_photos / len(sessions) if sessions else 0
        avg_duration = total_duration / len(sessions) if sessions else timedelta()

        return {
            "total_sessions": len(sessions),
            "total_photos": total_photos,
            "avg_photos_per_session": round(avg_photos_per_session, 1),
            "total_duration": total_duration,
            "avg_session_duration": avg_duration,
            "unique_cameras": len(cameras),
            "unique_locations": len(locations),
            "cameras_used": list(cameras),
            "locations_visited": list(locations),
        }
