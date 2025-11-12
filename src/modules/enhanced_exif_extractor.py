import logging
import re
import warnings
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import exif
from PIL import Image
from PIL.ExifTags import TAGS

# Suppress specific warnings from the old exif library
warnings.filterwarnings(
    "ignore",
    category=RuntimeWarning,
    message="ASCII tag contains.*fewer bytes than specified",
)

logger = logging.getLogger(__name__)

# Try to import pyexiftool
try:
    import exiftool

    EXIFTOOL_AVAILABLE = True
    logger.info("PyExifTool available - using for enhanced EXIF extraction")
except ImportError:
    EXIFTOOL_AVAILABLE = False
    logger.warning("PyExifTool not available - falling back to basic EXIF extraction")

# Import video metadata extractor
try:
    from .enhanced_video_extractor import EnhancedVideoExtractor

    VIDEO_EXTRACTION_AVAILABLE = True
    logger.info("Enhanced video extraction available")
except ImportError:
    VIDEO_EXTRACTION_AVAILABLE = False
    logger.warning("Enhanced video extraction not available")


class EnhancedExifExtractor:
    def __init__(self):
        self.cache = {}
        self.exiftool_session = None
        self._initialize_exiftool()
        self.exiftool_available = EXIFTOOL_AVAILABLE and self.exiftool_session is not None

        # Initialize video extractor
        if VIDEO_EXTRACTION_AVAILABLE:
            self.video_extractor = EnhancedVideoExtractor()
        else:
            self.video_extractor = None

        # Define video file extensions
        self.video_extensions = {
            ".mp4",
            ".mov",
            ".avi",
            ".mkv",
            ".wmv",
            ".flv",
            ".webm",
            ".m4v",
            ".mpg",
            ".mpeg",
            ".mpeg4",
            ".3gp",
            ".asf",
            ".rm",
            ".rmvb",
            ".vob",
            ".ts",
            ".mts",
            ".m2ts",
            ".mxf",
            ".dv",
            ".dvr-ms",
            ".wtv",
            ".ogv",
            ".f4v",
            ".swf",
            ".qt",
            ".movie",
            ".mpe",
            ".m1v",
            ".m2v",
            ".mpv2",
            ".mp2v",
            ".dat",
        }

    def _initialize_exiftool(self):
        """Initialize ExifTool session if available"""
        global EXIFTOOL_AVAILABLE
        if EXIFTOOL_AVAILABLE:
            try:
                self.exiftool_session = exiftool.ExifToolHelper()
                logger.debug("ExifTool session initialized successfully")
            except Exception as e:
                logger.warning(f"Failed to initialize ExifTool: {e}")
                self.exiftool_session = None
                EXIFTOOL_AVAILABLE = False

    def __del__(self):
        """Clean up ExifTool session"""
        if self.exiftool_session:
            try:
                self.exiftool_session.terminate()
            except Exception:
                pass

    def extract_metadata(self, file_path: str) -> Dict[str, Any]:
        """Extract comprehensive metadata using appropriate extractor (photo/video)"""
        file_path_obj = Path(file_path)

        if str(file_path_obj) in self.cache:
            return self.cache[str(file_path_obj)]

        # Check if this is a video file
        if file_path_obj.suffix.lower() in self.video_extensions:
            return self._extract_video_metadata(file_path_obj)

        # Base metadata for images
        metadata = {
            "file_path": str(file_path_obj),
            "file_name": file_path_obj.name,
            "file_size": file_path_obj.stat().st_size if file_path_obj.exists() else 0,
            "file_extension": file_path_obj.suffix.lower(),
            "file_modified": (
                datetime.fromtimestamp(file_path_obj.stat().st_mtime) if file_path_obj.exists() else None
            ),
            "file_created": (datetime.fromtimestamp(file_path_obj.stat().st_ctime) if file_path_obj.exists() else None),
        }

        if not file_path_obj.exists():
            self.cache[str(file_path_obj)] = metadata
            return metadata

        try:
            if EXIFTOOL_AVAILABLE and self.exiftool_session:
                # Use PyExifTool for comprehensive extraction
                exiftool_metadata = self._extract_with_exiftool(file_path_obj)
                metadata.update(exiftool_metadata)
            else:
                # Fallback to original methods
                if self._is_supported_image(file_path_obj):
                    legacy_metadata = self._extract_with_legacy_methods(file_path_obj)
                    metadata.update(legacy_metadata)

        except Exception as e:
            logger.warning(f"Error extracting metadata from {file_path_obj}: {e}")
            # Try fallback method if ExifTool fails
            if EXIFTOOL_AVAILABLE and self._is_supported_image(file_path_obj):
                try:
                    legacy_metadata = self._extract_with_legacy_methods(file_path_obj)
                    metadata.update(legacy_metadata)
                except Exception as e2:
                    logger.warning(f"Fallback extraction also failed for {file_path_obj}: {e2}")

        self.cache[str(file_path_obj)] = metadata
        return metadata

    def _extract_with_exiftool(self, file_path: Path) -> Dict[str, Any]:
        """Extract metadata using PyExifTool"""
        try:
            # Get all metadata from ExifTool
            exif_data = self.exiftool_session.get_metadata([str(file_path)])[0]

            metadata = {}

            # Date/Time extraction with priority order
            datetime_fields = [
                "EXIF:DateTimeOriginal",
                "EXIF:CreateDate",
                "EXIF:DateTime",
                "XMP:DateTimeOriginal",
                "QuickTime:CreateDate",
                "File:FileModifyDate",
            ]

            for field in datetime_fields:
                if field in exif_data:
                    dt = self._parse_exiftool_datetime(exif_data[field])
                    if dt:
                        if field == "EXIF:DateTimeOriginal":
                            metadata["datetime_original"] = dt
                        elif field == "EXIF:CreateDate":
                            metadata["datetime_digitized"] = dt
                        elif field == "EXIF:DateTime":
                            metadata["datetime"] = dt

                        # Set the first valid datetime as the primary one
                        if "datetime_original" not in metadata:
                            metadata["datetime_original"] = dt
                        break

            # Camera information with enhanced detection
            camera_make = exif_data.get("EXIF:Make", exif_data.get("MakerNotes:Make", ""))
            camera_model = exif_data.get("EXIF:Model", exif_data.get("MakerNotes:Model", ""))

            if camera_make:
                metadata["camera_make"] = str(camera_make).strip()
            if camera_model:
                metadata["camera_model"] = str(camera_model).strip()

            # Lens information (much better with ExifTool)
            lens_fields = [
                "EXIF:LensModel",
                "EXIF:LensInfo",
                "MakerNotes:LensType",
                "MakerNotes:Lens",
                "XMP:Lens",
            ]

            for field in lens_fields:
                if field in exif_data:
                    lens_info = str(exif_data[field]).strip()
                    if lens_info and lens_info != "Unknown":
                        metadata["lens_model"] = lens_info
                        break

            # Technical settings
            technical_mappings = {
                "f_number": ["EXIF:FNumber", "EXIF:Aperture"],
                "exposure_time": ["EXIF:ExposureTime", "EXIF:ShutterSpeed"],
                "iso": ["EXIF:ISO", "EXIF:SensitivityType"],
                "focal_length": ["EXIF:FocalLength"],
                "orientation": ["EXIF:Orientation"],
                "flash": ["EXIF:Flash"],
                "metering_mode": ["EXIF:MeteringMode"],
                "exposure_mode": ["EXIF:ExposureMode"],
                "white_balance": ["EXIF:WhiteBalance"],
                "scene_mode": ["EXIF:SceneType"],
            }

            for key, fields in technical_mappings.items():
                for field in fields:
                    if field in exif_data:
                        value = exif_data[field]
                        if isinstance(value, (int, float)) or (
                            isinstance(value, str) and value.replace(".", "").isdigit()
                        ):
                            try:
                                metadata[key] = float(value) if "." in str(value) else int(value)
                            except (ValueError, TypeError):
                                metadata[key] = value
                        break

            # Image dimensions
            if "EXIF:ImageWidth" in exif_data:
                metadata["width"] = int(exif_data["EXIF:ImageWidth"])
            if "EXIF:ImageHeight" in exif_data:
                metadata["height"] = int(exif_data["EXIF:ImageHeight"])

            # GPS information (much more comprehensive)
            gps_data = self._extract_gps_with_exiftool(exif_data)
            if gps_data:
                metadata["gps"] = gps_data

            # Professional metadata
            metadata.update(self._extract_professional_metadata(exif_data))

            # Software and processing info
            if "EXIF:Software" in exif_data:
                metadata["software"] = str(exif_data["EXIF:Software"]).strip()
            if "EXIF:Artist" in exif_data:
                metadata["artist"] = str(exif_data["EXIF:Artist"]).strip()
            if "EXIF:Copyright" in exif_data:
                metadata["copyright"] = str(exif_data["EXIF:Copyright"]).strip()

            # Color space and quality info
            if "EXIF:ColorSpace" in exif_data:
                metadata["color_space"] = str(exif_data["EXIF:ColorSpace"])
            if "EXIF:Quality" in exif_data:
                metadata["quality"] = str(exif_data["EXIF:Quality"])

            logger.debug(f"Extracted {len(metadata)} metadata fields with ExifTool from {file_path}")
            return metadata

        except Exception as e:
            logger.error(f"ExifTool extraction failed for {file_path}: {e}")
            return {}

    def _extract_gps_with_exiftool(self, exif_data: Dict) -> Optional[Dict[str, Any]]:
        """Extract GPS data using ExifTool"""
        gps_data = {}

        # GPS coordinates
        if "EXIF:GPSLatitude" in exif_data and "EXIF:GPSLongitude" in exif_data:
            try:
                lat = float(exif_data["EXIF:GPSLatitude"])
                lon = float(exif_data["EXIF:GPSLongitude"])

                # Apply GPS reference directions
                if exif_data.get("EXIF:GPSLatitudeRef") == "S":
                    lat = -lat
                if exif_data.get("EXIF:GPSLongitudeRef") == "W":
                    lon = -lon

                gps_data["latitude"] = lat
                gps_data["longitude"] = lon
            except (ValueError, TypeError) as e:
                logger.debug(f"Error parsing GPS coordinates: {e}")

        # GPS altitude
        if "EXIF:GPSAltitude" in exif_data:
            try:
                altitude = float(exif_data["EXIF:GPSAltitude"])
                if exif_data.get("EXIF:GPSAltitudeRef") == "1":  # Below sea level
                    altitude = -altitude
                gps_data["altitude"] = altitude
            except (ValueError, TypeError):
                pass

        # GPS timestamp
        if "EXIF:GPSTimeStamp" in exif_data:
            gps_data["timestamp"] = str(exif_data["EXIF:GPSTimeStamp"])

        # GPS speed and direction
        if "EXIF:GPSSpeed" in exif_data:
            try:
                gps_data["speed"] = float(exif_data["EXIF:GPSSpeed"])
            except (ValueError, TypeError):
                pass

        if "EXIF:GPSImgDirection" in exif_data:
            try:
                gps_data["direction"] = float(exif_data["EXIF:GPSImgDirection"])
            except (ValueError, TypeError):
                pass

        # GPS satellites and precision
        if "EXIF:GPSSatellites" in exif_data:
            gps_data["satellites"] = str(exif_data["EXIF:GPSSatellites"])

        if "EXIF:GPSDOP" in exif_data:
            try:
                gps_data["precision"] = float(exif_data["EXIF:GPSDOP"])
            except (ValueError, TypeError):
                pass

        return gps_data if gps_data else None

    def _extract_professional_metadata(self, exif_data: Dict) -> Dict[str, Any]:
        """Extract professional/advanced metadata fields"""
        metadata = {}

        # Focus information
        focus_fields = {
            "focus_mode": ["EXIF:FocusMode", "MakerNotes:FocusMode"],
            "focus_distance": ["EXIF:SubjectDistance", "MakerNotes:FocusDistance"],
            "af_area_mode": ["MakerNotes:AFAreaMode"],
            "af_point": ["MakerNotes:AFPoint", "MakerNotes:AFPointSelected"],
        }

        for key, fields in focus_fields.items():
            for field in fields:
                if field in exif_data:
                    metadata[key] = str(exif_data[field])
                    break

        # Image quality and processing
        quality_fields = {
            "image_quality": ["MakerNotes:Quality", "MakerNotes:ImageQuality"],
            "noise_reduction": ["MakerNotes:NoiseReduction"],
            "vignette_control": ["MakerNotes:VignetteControl"],
            "active_d_lighting": ["MakerNotes:ActiveDLighting"],
            "hdr": ["MakerNotes:HDR"],
            "picture_control": ["MakerNotes:PictureControl"],
        }

        for key, fields in quality_fields.items():
            for field in fields:
                if field in exif_data:
                    metadata[key] = str(exif_data[field])
                    break

        # Shooting information
        shooting_fields = {
            "shooting_mode": ["MakerNotes:ShootingMode", "EXIF:ExposureProgram"],
            "bracketing": ["MakerNotes:BracketSet", "MakerNotes:BracketMode"],
            "multiple_exposure": ["MakerNotes:MultipleExposure"],
            "interval_shooting": ["MakerNotes:IntervalShooting"],
        }

        for key, fields in shooting_fields.items():
            for field in fields:
                if field in exif_data:
                    metadata[key] = str(exif_data[field])
                    break

        # Lens corrections
        correction_fields = {
            "lens_correction": ["MakerNotes:LensCorrection"],
            "distortion_control": ["MakerNotes:DistortionControl"],
            "chromatic_aberration": ["MakerNotes:ChromaticAberration"],
            "auto_iso": ["MakerNotes:AutoISO"],
        }

        for key, fields in correction_fields.items():
            for field in fields:
                if field in exif_data:
                    metadata[key] = str(exif_data[field])
                    break

        # Flash information
        if "EXIF:Flash" in exif_data:
            flash_value = exif_data["EXIF:Flash"]
            metadata["flash_fired"] = bool(int(flash_value) & 1) if isinstance(flash_value, (int, str)) else False

        flash_fields = {
            "flash_mode": ["MakerNotes:FlashMode"],
            "flash_compensation": [
                "EXIF:FlashCompensation",
                "MakerNotes:FlashCompensation",
            ],
            "flash_power": ["MakerNotes:FlashOutput"],
        }

        for key, fields in flash_fields.items():
            for field in fields:
                if field in exif_data:
                    value = exif_data[field]
                    if key == "flash_compensation" or key == "flash_power":
                        try:
                            metadata[key] = float(value)
                        except (ValueError, TypeError):
                            metadata[key] = str(value)
                    else:
                        metadata[key] = str(value)
                    break

        return metadata

    def _parse_exiftool_datetime(self, datetime_string: str) -> Optional[datetime]:
        """Parse datetime from ExifTool output"""
        if not datetime_string:
            return None

        # Clean the datetime string
        datetime_string = str(datetime_string).strip()

        # ExifTool formats
        formats = [
            "%Y:%m:%d %H:%M:%S",
            "%Y-%m-%d %H:%M:%S",
            "%Y/%m/%d %H:%M:%S",
            "%Y:%m:%d %H:%M:%S.%f",
            "%Y-%m-%d %H:%M:%S.%f",
            "%Y-%m-%dT%H:%M:%S",
            "%Y-%m-%dT%H:%M:%S.%f",
            "%Y-%m-%dT%H:%M:%SZ",
            "%Y:%m:%d %H:%M:%S%z",
            "%Y-%m-%d %H:%M:%S%z",
        ]

        for fmt in formats:
            try:
                return datetime.strptime(datetime_string, fmt)
            except ValueError:
                continue

        # Try parsing with timezone info
        try:
            # Remove timezone info for basic parsing
            clean_dt = re.sub(r"[+-]\d{2}:\d{2}$", "", datetime_string)
            return datetime.strptime(clean_dt, "%Y:%m:%d %H:%M:%S")
        except ValueError:
            pass

        logger.debug(f"Could not parse datetime: {datetime_string}")
        return None

    def is_image_file(self, file_path: str) -> bool:
        """Check if file is a supported image type"""
        return self._is_supported_image(Path(file_path))

    def _is_supported_image(self, file_path: Path) -> bool:
        """Check if file type is supported"""
        supported_extensions = {
            ".jpg",
            ".jpeg",
            ".png",
            ".gif",
            ".bmp",
            ".tiff",
            ".tif",
            ".heic",
            ".heif",
            ".raw",
            ".cr2",
            ".cr3",
            ".nef",
            ".arw",
            ".orf",
            ".dng",
            ".raf",
            ".rw2",
            ".pef",
            ".srw",
            ".x3f",
            ".3fr",
            ".ari",
            ".bay",
            ".crw",
            ".dcr",
            ".erf",
            ".fff",
            ".iiq",
            ".k25",
            ".kdc",
            ".mef",
            ".mos",
            ".mrw",
            ".nrw",
            ".ptx",
            ".r3d",
            ".rwl",
            ".sr2",
            ".srf",
        }
        return file_path.suffix.lower() in supported_extensions

    def _extract_with_legacy_methods(self, file_path: Path) -> Dict[str, Any]:
        """Fallback to legacy EXIF extraction methods"""
        logger.debug(f"Using legacy EXIF extraction for {file_path}")

        metadata = {}

        # Try with exif library first
        try:
            with open(file_path, "rb") as f:
                img = exif.Image(f)

                if img.has_exif:
                    if hasattr(img, "datetime_original"):
                        metadata["datetime_original"] = self._parse_exiftool_datetime(img.datetime_original)
                    if hasattr(img, "datetime_digitized"):
                        metadata["datetime_digitized"] = self._parse_exiftool_datetime(img.datetime_digitized)
                    if hasattr(img, "datetime"):
                        metadata["datetime"] = self._parse_exiftool_datetime(img.datetime)

                    # Camera info
                    if hasattr(img, "make"):
                        metadata["camera_make"] = img.make
                    if hasattr(img, "model"):
                        metadata["camera_model"] = img.model
                    if hasattr(img, "lens_model"):
                        metadata["lens_model"] = img.lens_model

                    # Technical settings
                    if hasattr(img, "f_number"):
                        metadata["f_number"] = img.f_number
                    if hasattr(img, "exposure_time"):
                        metadata["exposure_time"] = img.exposure_time
                    if hasattr(img, "photographic_sensitivity"):
                        metadata["iso"] = img.photographic_sensitivity
                    if hasattr(img, "focal_length"):
                        metadata["focal_length"] = img.focal_length
                    if hasattr(img, "orientation"):
                        metadata["orientation"] = img.orientation

                    # Other info
                    if hasattr(img, "software"):
                        metadata["software"] = img.software
                    if hasattr(img, "artist"):
                        metadata["artist"] = img.artist
                    if hasattr(img, "copyright"):
                        metadata["copyright"] = img.copyright

                    # GPS data
                    if hasattr(img, "gps_latitude") and hasattr(img, "gps_longitude"):
                        lat = self._convert_gps_coordinates(
                            img.gps_latitude,
                            (img.gps_latitude_ref if hasattr(img, "gps_latitude_ref") else "N"),
                        )
                        lon = self._convert_gps_coordinates(
                            img.gps_longitude,
                            (img.gps_longitude_ref if hasattr(img, "gps_longitude_ref") else "E"),
                        )

                        if lat and lon:
                            gps_data = {"latitude": lat, "longitude": lon}
                            if hasattr(img, "gps_altitude"):
                                gps_data["altitude"] = img.gps_altitude
                            metadata["gps"] = gps_data

        except Exception as e:
            logger.debug(f"Exif library extraction failed: {e}")

        # Try with PIL as final fallback
        try:
            image = Image.open(file_path)

            if not metadata.get("width"):
                metadata["width"] = image.width
            if not metadata.get("height"):
                metadata["height"] = image.height

            metadata["mode"] = image.mode
            metadata["format"] = image.format

            # Try to get EXIF with PIL
            exif_data = image._getexif()
            if exif_data and not metadata.get("camera_model"):  # Only if we don't have it already
                for tag_id, value in exif_data.items():
                    tag = TAGS.get(tag_id, tag_id)

                    if tag == "Make" and not metadata.get("camera_make"):
                        metadata["camera_make"] = value
                    elif tag == "Model" and not metadata.get("camera_model"):
                        metadata["camera_model"] = value
                    elif tag == "DateTime" and not metadata.get("datetime"):
                        metadata["datetime"] = self._parse_exiftool_datetime(value)

            image.close()

        except Exception as e:
            logger.debug(f"PIL extraction failed: {e}")

        return metadata

    def _convert_gps_coordinates(self, coord_tuple: Tuple, ref: str) -> Optional[float]:
        """Convert GPS coordinates to decimal degrees"""
        try:
            if isinstance(coord_tuple, (list, tuple)) and len(coord_tuple) >= 3:
                degrees = float(coord_tuple[0])
                minutes = float(coord_tuple[1])
                seconds = float(coord_tuple[2])
            else:
                return None

            decimal = degrees + minutes / 60 + seconds / 3600

            if ref in ["S", "W"]:
                decimal = -decimal

            return decimal
        except (TypeError, ValueError) as e:
            logger.debug(f"Could not convert GPS coordinates: {e}")
            return None

    def get_capture_datetime(self, metadata: Dict[str, Any]) -> Optional[datetime]:
        """Get the best available capture datetime"""
        date_sources = [
            "datetime_original",
            "datetime_digitized",
            "datetime",
            "file_modified",
            "file_created",
        ]

        for source in date_sources:
            if source in metadata and metadata[source]:
                return metadata[source]

        return None

    def clear_cache(self):
        """Clear the metadata cache"""
        self.cache.clear()

    def get_supported_formats(self) -> List[str]:
        """Get list of supported file formats"""
        if EXIFTOOL_AVAILABLE:
            return [
                # Common formats
                "jpg",
                "jpeg",
                "png",
                "gif",
                "bmp",
                "tiff",
                "tif",
                "heic",
                "heif",
                "webp",
                # RAW formats
                "raw",
                "cr2",
                "cr3",
                "nef",
                "arw",
                "orf",
                "dng",
                "raf",
                "rw2",
                "pef",
                "srw",
                "x3f",
                "3fr",
                "ari",
                "bay",
                "crw",
                "dcr",
                "erf",
                "fff",
                "iiq",
                "k25",
                "kdc",
                "mef",
                "mos",
                "mrw",
                "nrw",
                "ptx",
                "r3d",
                "rwl",
                "sr2",
                "srf",
                # Video formats (basic metadata)
                "mp4",
                "mov",
                "avi",
                "mkv",
                "m4v",
            ]
        else:
            return [
                "jpg",
                "jpeg",
                "png",
                "gif",
                "bmp",
                "tiff",
                "tif",
                "heic",
                "heif",
                "raw",
                "cr2",
                "cr3",
                "nef",
                "arw",
                "orf",
                "dng",
                "raf",
                "rw2",
                "pef",
                "srw",
                "x3f",
            ]

    def get_extraction_method(self) -> str:
        """Get the current extraction method being used"""
        if EXIFTOOL_AVAILABLE and self.exiftool_session:
            return "PyExifTool (Professional)"
        else:
            return "Legacy (Basic)"

    def get_exiftool_version(self) -> Optional[str]:
        """Get ExifTool version if available"""
        if EXIFTOOL_AVAILABLE and self.exiftool_session:
            try:
                version_info = self.exiftool_session.get_version()
                return version_info
            except Exception:
                return "Unknown"
        return None

    def _extract_video_metadata(self, file_path: Path) -> Dict[str, Any]:
        """Extract metadata from video files using enhanced video extractor"""
        if self.video_extractor:
            try:
                metadata = self.video_extractor.extract_metadata(str(file_path))

                # Add media type indicator
                metadata["media_type"] = "video"

                # Map some video metadata to standard field names for compatibility
                if "video_width" in metadata:
                    metadata["width"] = metadata["video_width"]
                if "video_height" in metadata:
                    metadata["height"] = metadata["video_height"]
                if "container_format" in metadata:
                    metadata["format"] = metadata["container_format"]

                # Cache the result
                self.cache[str(file_path)] = metadata
                return metadata

            except Exception as e:
                logger.warning(f"Video metadata extraction failed for {file_path}: {e}")

        # Fallback to basic file metadata if video extraction fails
        metadata = {
            "file_path": str(file_path),
            "file_name": file_path.name,
            "file_size": file_path.stat().st_size if file_path.exists() else 0,
            "file_extension": file_path.suffix.lower(),
            "file_modified": (datetime.fromtimestamp(file_path.stat().st_mtime) if file_path.exists() else None),
            "file_created": (datetime.fromtimestamp(file_path.stat().st_ctime) if file_path.exists() else None),
            "media_type": "video",
            "format": file_path.suffix[1:].upper() if file_path.suffix else "Unknown",
        }

        self.cache[str(file_path)] = metadata
        return metadata
