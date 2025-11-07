import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, Tuple
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS
import exif

logger = logging.getLogger(__name__)


class ExifExtractor:
    def __init__(self):
        self.cache = {}

    def extract_metadata(self, file_path: str) -> Dict[str, Any]:
        file_path_obj = Path(file_path)

        if str(file_path_obj) in self.cache:
            return self.cache[str(file_path_obj)]

        metadata = {
            "file_path": str(file_path_obj),
            "file_name": file_path_obj.name,
            "file_size": file_path_obj.stat().st_size if file_path_obj.exists() else 0,
            "file_extension": file_path_obj.suffix.lower(),
            "file_modified": (
                datetime.fromtimestamp(file_path_obj.stat().st_mtime)
                if file_path_obj.exists()
                else None
            ),
            "file_created": (
                datetime.fromtimestamp(file_path_obj.stat().st_ctime)
                if file_path_obj.exists()
                else None
            ),
        }

        try:
            if self._is_supported_image(file_path_obj):
                exif_data = self._extract_exif_data(file_path_obj)
                metadata.update(exif_data)

                gps_data = self._extract_gps_data(file_path_obj)
                if gps_data:
                    metadata["gps"] = gps_data

                additional_data = self._extract_additional_metadata(file_path_obj)
                metadata.update(additional_data)
        except Exception as e:
            logger.warning(f"Error extracting metadata from {file_path_obj}: {e}")

        self.cache[str(file_path_obj)] = metadata
        return metadata

    def _is_supported_image(self, file_path: Path) -> bool:
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
        }
        return file_path.suffix.lower() in supported_extensions

    def _extract_exif_data(self, file_path: Path) -> Dict[str, Any]:
        exif_dict = {}

        try:
            with open(file_path, "rb") as f:
                img = exif.Image(f)

                if img.has_exif:
                    if hasattr(img, "datetime_original"):
                        exif_dict["datetime_original"] = self._parse_datetime(
                            img.datetime_original
                        )
                    if hasattr(img, "datetime_digitized"):
                        exif_dict["datetime_digitized"] = self._parse_datetime(
                            img.datetime_digitized
                        )
                    if hasattr(img, "datetime"):
                        exif_dict["datetime"] = self._parse_datetime(img.datetime)

                    if hasattr(img, "make"):
                        exif_dict["camera_make"] = img.make
                    if hasattr(img, "model"):
                        exif_dict["camera_model"] = img.model
                    if hasattr(img, "lens_make"):
                        exif_dict["lens_make"] = img.lens_make
                    if hasattr(img, "lens_model"):
                        exif_dict["lens_model"] = img.lens_model

                    if hasattr(img, "f_number"):
                        exif_dict["f_number"] = img.f_number
                    if hasattr(img, "exposure_time"):
                        exif_dict["exposure_time"] = img.exposure_time
                    if hasattr(img, "photographic_sensitivity"):
                        exif_dict["iso"] = img.photographic_sensitivity
                    if hasattr(img, "focal_length"):
                        exif_dict["focal_length"] = img.focal_length

                    if hasattr(img, "orientation"):
                        exif_dict["orientation"] = img.orientation
                    if hasattr(img, "software"):
                        exif_dict["software"] = img.software
                    if hasattr(img, "artist"):
                        exif_dict["artist"] = img.artist
                    if hasattr(img, "copyright"):
                        exif_dict["copyright"] = img.copyright

        except Exception as e:
            logger.debug(
                f"Could not extract EXIF with exif library from {file_path}: {e}"
            )

            try:
                image = Image.open(file_path)
                exif_data = image._getexif()

                if exif_data:
                    for tag_id, value in exif_data.items():
                        tag = TAGS.get(tag_id, tag_id)

                        if tag == "DateTimeOriginal":
                            exif_dict["datetime_original"] = self._parse_datetime(value)
                        elif tag == "DateTimeDigitized":
                            exif_dict["datetime_digitized"] = self._parse_datetime(
                                value
                            )
                        elif tag == "DateTime":
                            exif_dict["datetime"] = self._parse_datetime(value)
                        elif tag == "Make":
                            exif_dict["camera_make"] = value
                        elif tag == "Model":
                            exif_dict["camera_model"] = value
                        elif tag == "LensMake":
                            exif_dict["lens_make"] = value
                        elif tag == "LensModel":
                            exif_dict["lens_model"] = value
                        elif tag == "FNumber":
                            exif_dict["f_number"] = value
                        elif tag == "ExposureTime":
                            exif_dict["exposure_time"] = value
                        elif tag == "ISOSpeedRatings":
                            exif_dict["iso"] = value
                        elif tag == "FocalLength":
                            exif_dict["focal_length"] = value
                        elif tag == "Orientation":
                            exif_dict["orientation"] = value
                        elif tag == "Software":
                            exif_dict["software"] = value
                        elif tag == "Artist":
                            exif_dict["artist"] = value
                        elif tag == "Copyright":
                            exif_dict["copyright"] = value

                image.close()
            except Exception as e2:
                logger.debug(f"Could not extract EXIF with PIL from {file_path}: {e2}")

        return exif_dict

    def _extract_gps_data(self, file_path: Path) -> Optional[Dict[str, Any]]:
        gps_data = {}

        try:
            with open(file_path, "rb") as f:
                img = exif.Image(f)

                if img.has_exif:
                    if hasattr(img, "gps_latitude") and hasattr(img, "gps_longitude"):
                        lat = self._convert_gps_coordinates(
                            img.gps_latitude,
                            (
                                img.gps_latitude_ref
                                if hasattr(img, "gps_latitude_ref")
                                else "N"
                            ),
                        )
                        lon = self._convert_gps_coordinates(
                            img.gps_longitude,
                            (
                                img.gps_longitude_ref
                                if hasattr(img, "gps_longitude_ref")
                                else "E"
                            ),
                        )

                        if lat and lon:
                            gps_data["latitude"] = lat
                            gps_data["longitude"] = lon

                    if hasattr(img, "gps_altitude"):
                        gps_data["altitude"] = img.gps_altitude
                    if hasattr(img, "gps_timestamp"):
                        gps_data["timestamp"] = img.gps_timestamp
                    if hasattr(img, "gps_speed"):
                        gps_data["speed"] = img.gps_speed
                    if hasattr(img, "gps_direction"):
                        gps_data["direction"] = img.gps_direction

        except Exception as e:
            logger.debug(
                f"Could not extract GPS with exif library from {file_path}: {e}"
            )

            try:
                image = Image.open(file_path)
                exif_data = image._getexif()

                if exif_data:
                    for tag_id, value in exif_data.items():
                        tag = TAGS.get(tag_id, tag_id)

                        if tag == "GPSInfo":
                            gps_info = {}
                            for gps_tag_id, gps_value in value.items():
                                gps_tag = GPSTAGS.get(gps_tag_id, gps_tag_id)
                                gps_info[gps_tag] = gps_value

                            if "GPSLatitude" in gps_info and "GPSLongitude" in gps_info:
                                lat = self._convert_gps_coordinates_pil(
                                    gps_info["GPSLatitude"],
                                    gps_info.get("GPSLatitudeRef", "N"),
                                )
                                lon = self._convert_gps_coordinates_pil(
                                    gps_info["GPSLongitude"],
                                    gps_info.get("GPSLongitudeRef", "E"),
                                )

                                if lat and lon:
                                    gps_data["latitude"] = lat
                                    gps_data["longitude"] = lon

                            if "GPSAltitude" in gps_info:
                                gps_data["altitude"] = gps_info["GPSAltitude"]
                            if "GPSTimeStamp" in gps_info:
                                gps_data["timestamp"] = gps_info["GPSTimeStamp"]
                            if "GPSSpeed" in gps_info:
                                gps_data["speed"] = gps_info["GPSSpeed"]
                            if "GPSImgDirection" in gps_info:
                                gps_data["direction"] = gps_info["GPSImgDirection"]

                image.close()
            except Exception as e2:
                logger.debug(f"Could not extract GPS with PIL from {file_path}: {e2}")

        return gps_data if gps_data else None

    def _extract_additional_metadata(self, file_path: Path) -> Dict[str, Any]:
        metadata = {}

        try:
            image = Image.open(file_path)
            metadata["width"] = image.width
            metadata["height"] = image.height
            metadata["mode"] = image.mode
            metadata["format"] = image.format

            if hasattr(image, "info"):
                info = image.info
                if "dpi" in info:
                    metadata["dpi"] = info["dpi"]
                if "compression" in info:
                    metadata["compression"] = info["compression"]

            image.close()
        except Exception as e:
            logger.debug(f"Could not extract additional metadata from {file_path}: {e}")

        return metadata

    def _parse_datetime(self, datetime_string: str) -> Optional[datetime]:
        if not datetime_string:
            return None

        formats = [
            "%Y:%m:%d %H:%M:%S",
            "%Y-%m-%d %H:%M:%S",
            "%Y/%m/%d %H:%M:%S",
            "%Y:%m:%d %H:%M:%S.%f",
            "%Y-%m-%dT%H:%M:%S",
            "%Y-%m-%dT%H:%M:%S.%f",
            "%Y-%m-%dT%H:%M:%SZ",
        ]

        for fmt in formats:
            try:
                return datetime.strptime(datetime_string, fmt)
            except ValueError:
                continue

        logger.debug(f"Could not parse datetime: {datetime_string}")
        return None

    def _convert_gps_coordinates(self, coord_tuple: Tuple, ref: str) -> Optional[float]:
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

    def _convert_gps_coordinates_pil(
        self, coord_tuple: Tuple, ref: str
    ) -> Optional[float]:
        try:
            degrees = coord_tuple[0]
            minutes = coord_tuple[1]
            seconds = coord_tuple[2]

            if isinstance(degrees, tuple):
                degrees = degrees[0] / degrees[1]
            if isinstance(minutes, tuple):
                minutes = minutes[0] / minutes[1]
            if isinstance(seconds, tuple):
                seconds = seconds[0] / seconds[1]

            decimal = float(degrees) + float(minutes) / 60 + float(seconds) / 3600

            if ref in ["S", "W"]:
                decimal = -decimal

            return decimal
        except (TypeError, ValueError, ZeroDivisionError) as e:
            logger.debug(f"Could not convert GPS coordinates: {e}")
            return None

    def get_capture_datetime(self, metadata: Dict[str, Any]) -> Optional[datetime]:
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
        self.cache.clear()
