import logging
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class FolderOrganizer:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.org_config = config.get('organization', {})
        self.folder_structure = self.org_config.get('folder_structure', '{year}/{month:02d}/{day:02d}')
        self.folder_structure_with_location = self.org_config.get('folder_structure_with_location', '{year}/{month:02d}/{day:02d}/{city}')
        self.folder_structure_templates = self.org_config.get('folder_structure_templates', {})
        self.separate_raw = self.org_config.get('separate_raw', True)
        self.raw_folder = self.org_config.get('raw_folder', 'RAW')
        self.jpg_folder = self.org_config.get('jpg_folder', 'JPG')
        self.video_folder = self.org_config.get('video_folder', 'VIDEOS')
        self.unknown_folder = self.org_config.get('unknown_folder', 'UNKNOWN')

        # Geolocation configuration
        self.geo_config = config.get('geolocation', {})
        self.location_components = self.geo_config.get('location_components', 'city')

        self.file_types = config.get('file_types', {})
        self.raw_extensions = set('.' + ext.lower() for ext in self.file_types.get('raw', []))
        self.image_extensions = set('.' + ext.lower() for ext in self.file_types.get('images', []))
        self.video_extensions = set('.' + ext.lower() for ext in self.file_types.get('videos', []))

    def determine_destination_path(self, file_path: str, metadata: Dict[str, Any],
                                 base_destination: str, location_info: Optional[Dict[str, str]] = None) -> Path:
        file_path_obj = Path(file_path)
        extension = file_path_obj.suffix.lower()

        capture_datetime = self._get_datetime_from_metadata(metadata)
        if not capture_datetime:
            capture_datetime = datetime.now()
            logger.warning(f"No datetime found for {file_path_obj}, using current time")

        folder_path = self._format_folder_structure(capture_datetime, metadata, location_info)

        file_type_folder = self._determine_file_type_folder(extension)

        base_path = Path(base_destination)

        if self.separate_raw and file_type_folder:
            destination = base_path / file_type_folder / folder_path
        else:
            destination = base_path / folder_path

        return destination

    def _get_datetime_from_metadata(self, metadata: Dict[str, Any]) -> Optional[datetime]:
        date_sources = self.org_config.get('date_sources', [
            'datetime_original',
            'datetime_digitized',
            'datetime',
            'file_modified',
            'file_created'
        ])

        for source in date_sources:
            if source in metadata and metadata[source]:
                if isinstance(metadata[source], datetime):
                    return metadata[source]
                elif isinstance(metadata[source], str):
                    try:
                        return datetime.fromisoformat(metadata[source])
                    except ValueError:
                        continue

        return None

    def _format_folder_structure(self, capture_datetime: datetime,
                                metadata: Dict[str, Any],
                                location_info: Optional[Dict[str, str]] = None) -> str:
        variables = {
            'year': capture_datetime.year,
            'month': capture_datetime.month,
            'day': capture_datetime.day,
            'hour': capture_datetime.hour,
            'date': capture_datetime.strftime('%Y%m%d'),
            'year_month': capture_datetime.strftime('%Y-%m'),
            'month_name': capture_datetime.strftime('%B'),
            'month_short': capture_datetime.strftime('%b'),
            'weekday': capture_datetime.strftime('%A'),
            'week': capture_datetime.strftime('%W'),
        }

        camera_make = (metadata.get('camera_make') or '').strip()
        camera_model = (metadata.get('camera_model') or '').strip()
        if camera_model or camera_make:
            variables['camera'] = self._simplify_camera_name_enhanced(camera_make, camera_model)
        else:
            variables['camera'] = ''

        # Handle location data and choose appropriate folder structure
        if location_info and self.geo_config.get('add_location_to_folder', False):
            # Add location variables with configurable components
            location_vars = self._prepare_location_variables(location_info)
            variables.update(location_vars)

            # Use location-aware folder structure based on components setting
            folder_structure = self.folder_structure_templates.get(
                self.location_components,
                self.folder_structure_with_location
            )
        else:
            # Use regular folder structure without location
            folder_structure = self.folder_structure

        try:
            folder_path = folder_structure.format(**variables)

            folder_path = folder_path.replace('//', '/')
            folder_path = folder_path.strip('/')

            return folder_path
        except KeyError as e:
            logger.error(f"Invalid folder structure variable: {e}")
            return f"{variables['year']}/{variables['month']:02d}/{variables['day']:02d}"
        except Exception as e:
            logger.error(f"Error formatting folder structure: {e}")
            return f"{variables['year']}/{variables['month']:02d}/{variables['day']:02d}"

    def _prepare_location_variables(self, location_info: Dict[str, str]) -> Dict[str, str]:
        """Prepare location variables based on configuration"""
        result = {}

        # Get location data with fallbacks
        city = (location_info.get('city') or '').strip() if location_info else ''
        country = (location_info.get('country') or '').strip() if location_info else ''

        # Apply location component configuration
        if self.location_components == 'city':
            result['city'] = city
            result['location'] = city
        elif self.location_components == 'country':
            result['country'] = country
            result['location'] = country
        elif self.location_components == 'city_country':
            if city and country:
                result['location'] = f"{city}, {country}"
            elif city:
                result['location'] = city
            elif country:
                result['location'] = country
            else:
                result['location'] = ''
            result['city'] = city
            result['country'] = country
        elif self.location_components == 'country_city':
            if city and country:
                result['location'] = f"{country}, {city}"
            elif country:
                result['location'] = country
            elif city:
                result['location'] = city
            else:
                result['location'] = ''
            result['city'] = city
            result['country'] = country
        else:
            # Default to city only
            result['city'] = city
            result['location'] = city

        # Always provide individual components for template flexibility
        result['city'] = city
        result['country'] = country

        return result

    def _determine_file_type_folder(self, extension: str) -> Optional[str]:
        if not self.separate_raw:
            return None

        if extension in self.raw_extensions:
            return self.raw_folder
        elif extension in self.image_extensions:
            return self.jpg_folder
        elif extension in self.video_extensions:
            return self.video_folder
        else:
            return self.unknown_folder

    def _simplify_camera_name(self, camera_name: str) -> str:
        from utils.camera_slugger import get_camera_slug

        # Get custom mappings from config
        custom_mappings = self.config.get('naming', {}).get('camera_names', {})

        # Use the new slugger with enhanced pattern matching
        return get_camera_slug('', camera_name, custom_mappings)

    def _simplify_camera_name_enhanced(self, camera_make: str, camera_model: str) -> str:
        from utils.camera_slugger import get_camera_slug

        # Get custom mappings from config
        custom_mappings = self.config.get('naming', {}).get('camera_names', {})

        # Use the new slugger with both make and model for better pattern matching
        return get_camera_slug(camera_make, camera_model, custom_mappings)

    def organize_file(self, source_path: str, destination_folder: Path,
                     new_filename: str, dry_run: bool = False,
                     preserve_original: bool = True) -> Dict[str, Any]:
        source = Path(source_path)
        destination = destination_folder / new_filename

        result = {
            'source': str(source),
            'destination': str(destination),
            'action': 'copy' if preserve_original else 'move',
            'success': False,
            'error': None,
            'skipped': False
        }

        if not source.exists():
            result['error'] = f"Source file does not exist: {source}"
            logger.error(result['error'])
            return result

        if destination.exists():
            if self._is_same_file(source, destination):
                result['skipped'] = True
                result['success'] = True
                result['error'] = "File already exists at destination (same file)"
                logger.info(f"Skipping {source}, already at destination")
                return result
            else:
                result['error'] = f"Different file already exists at destination: {destination}"
                logger.warning(result['error'])
                return result

        if dry_run:
            result['success'] = True
            result['dry_run'] = True
            logger.info(f"[DRY RUN] Would {result['action']} {source} to {destination}")
            return result

        try:
            destination_folder.mkdir(parents=True, exist_ok=True)

            if preserve_original:
                shutil.copy2(source, destination)
                logger.info(f"Copied {source} to {destination}")
            else:
                shutil.move(str(source), str(destination))
                logger.info(f"Moved {source} to {destination}")

            result['success'] = True

        except Exception as e:
            result['error'] = str(e)
            logger.error(f"Error organizing file {source}: {e}")

        return result

    def _is_same_file(self, file1: Path, file2: Path) -> bool:
        if not file1.exists() or not file2.exists():
            return False

        if file1.stat().st_size != file2.stat().st_size:
            return False

        try:
            import hashlib

            def get_file_hash(filepath: Path) -> str:
                hasher = hashlib.md5()
                with open(filepath, 'rb') as f:
                    for chunk in iter(lambda: f.read(4096), b''):
                        hasher.update(chunk)
                return hasher.hexdigest()

            return get_file_hash(file1) == get_file_hash(file2)

        except Exception as e:
            logger.debug(f"Could not compare files: {e}")
            return False

    def create_sidecar_files(self, source_path: str, destination_path: str,
                           metadata: Dict[str, Any], dry_run: bool = False) -> bool:
        if dry_run:
            logger.info(f"[DRY RUN] Would create sidecar files for {destination_path}")
            return True

        try:
            sidecar_path = Path(destination_path).with_suffix('.xmp')

            xmp_content = self._generate_xmp_content(metadata)

            with open(sidecar_path, 'w', encoding='utf-8') as f:
                f.write(xmp_content)

            logger.info(f"Created sidecar file: {sidecar_path}")
            return True

        except Exception as e:
            logger.error(f"Error creating sidecar files: {e}")
            return False

    def _generate_xmp_content(self, metadata: Dict[str, Any]) -> str:
        xmp_template = '''<?xml version="1.0" encoding="UTF-8"?>
<x:xmpmeta xmlns:x="adobe:ns:meta/">
    <rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#">
        <rdf:Description rdf:about=""
            xmlns:dc="http://purl.org/dc/elements/1.1/"
            xmlns:exif="http://ns.adobe.com/exif/1.0/"
            xmlns:tiff="http://ns.adobe.com/tiff/1.0/"
            xmlns:xmp="http://ns.adobe.com/xap/1.0/"
            xmlns:aux="http://ns.adobe.com/exif/1.0/aux/"
            xmlns:crs="http://ns.adobe.com/camera-raw-settings/1.0/"
            xmlns:photoshop="http://ns.adobe.com/photoshop/1.0/">
            {properties}
        </rdf:Description>
    </rdf:RDF>
</x:xmpmeta>'''

        properties = []

        # === CORE CAMERA INFORMATION ===
        if metadata.get('camera_make'):
            properties.append(f'<tiff:Make>{self._escape_xml(metadata["camera_make"])}</tiff:Make>')
        if metadata.get('camera_model'):
            properties.append(f'<tiff:Model>{self._escape_xml(metadata["camera_model"])}</tiff:Model>')
        if metadata.get('software'):
            properties.append(f'<tiff:Software>{self._escape_xml(metadata["software"])}</tiff:Software>')

        # === DATETIME INFORMATION ===
        if metadata.get('datetime_original'):
            dt = metadata['datetime_original']
            if isinstance(dt, datetime):
                properties.append(f'<exif:DateTimeOriginal>{dt.isoformat()}</exif:DateTimeOriginal>')
                properties.append(f'<xmp:CreateDate>{dt.isoformat()}</xmp:CreateDate>')
        if metadata.get('datetime_digitized'):
            dt = metadata['datetime_digitized']
            if isinstance(dt, datetime):
                properties.append(f'<exif:DateTimeDigitized>{dt.isoformat()}</exif:DateTimeDigitized>')

        # === EXPOSURE SETTINGS ===
        if metadata.get('iso'):
            properties.append(f'<exif:ISOSpeedRatings>{metadata["iso"]}</exif:ISOSpeedRatings>')
        if metadata.get('f_number'):
            properties.append(f'<exif:FNumber>{metadata["f_number"]}</exif:FNumber>')
        if metadata.get('exposure_time'):
            properties.append(f'<exif:ExposureTime>{metadata["exposure_time"]}</exif:ExposureTime>')
        if metadata.get('exposure_mode') is not None:
            exposure_modes = {0: "Auto", 1: "Manual", 2: "Auto bracket"}
            mode = exposure_modes.get(metadata["exposure_mode"], str(metadata["exposure_mode"]))
            properties.append(f'<exif:ExposureMode>{mode}</exif:ExposureMode>')
        if metadata.get('exposure_program') is not None:
            program_modes = {
                0: "Not defined", 1: "Manual", 2: "Normal program", 3: "Aperture priority",
                4: "Shutter priority", 5: "Creative program", 6: "Action program",
                7: "Portrait mode", 8: "Landscape mode"
            }
            program = program_modes.get(metadata["exposure_program"], str(metadata["exposure_program"]))
            properties.append(f'<exif:ExposureProgram>{program}</exif:ExposureProgram>')

        # === LENS INFORMATION ===
        if metadata.get('lens_model'):
            properties.append(f'<exif:LensModel>{self._escape_xml(metadata["lens_model"])}</exif:LensModel>')
        if metadata.get('focal_length'):
            properties.append(f'<exif:FocalLength>{metadata["focal_length"]}</exif:FocalLength>')
        if metadata.get('focal_length_35mm'):
            properties.append(f'<exif:FocalLengthIn35mmFilm>{metadata["focal_length_35mm"]}</exif:FocalLengthIn35mmFilm>')

        # === FOCUS INFORMATION ===
        if metadata.get('focus_mode'):
            properties.append(f'<aux:FocusMode>{self._escape_xml(metadata["focus_mode"])}</aux:FocusMode>')
        if metadata.get('focus_distance'):
            properties.append(f'<aux:FocusDistance>{metadata["focus_distance"]}</aux:FocusDistance>')
        if metadata.get('af_area_mode'):
            properties.append(f'<aux:AFAreaMode>{metadata["af_area_mode"]}</aux:AFAreaMode>')

        # === FLASH INFORMATION ===
        if metadata.get('flash') is not None:
            properties.append(f'<exif:Flash>{metadata["flash"]}</exif:Flash>')
        if metadata.get('flash_fired') is not None:
            properties.append(f'<exif:FlashFired>{str(metadata["flash_fired"]).lower()}</exif:FlashFired>')
        if metadata.get('flash_mode'):
            properties.append(f'<aux:FlashMode>{self._escape_xml(metadata["flash_mode"])}</aux:FlashMode>')

        # === METERING AND WHITE BALANCE ===
        if metadata.get('metering_mode') is not None:
            metering_modes = {
                0: "Unknown", 1: "Average", 2: "Center-weighted average", 3: "Spot",
                4: "Multi-spot", 5: "Pattern", 6: "Partial", 255: "Other"
            }
            mode = metering_modes.get(metadata["metering_mode"], str(metadata["metering_mode"]))
            properties.append(f'<exif:MeteringMode>{mode}</exif:MeteringMode>')
        if metadata.get('white_balance') is not None:
            wb_modes = {0: "Auto", 1: "Manual"}
            wb = wb_modes.get(metadata["white_balance"], str(metadata["white_balance"]))
            properties.append(f'<exif:WhiteBalance>{wb}</exif:WhiteBalance>')

        # === IMAGE DIMENSIONS AND ORIENTATION ===
        if metadata.get('width'):
            properties.append(f'<tiff:ImageWidth>{metadata["width"]}</tiff:ImageWidth>')
            properties.append(f'<exif:PixelXDimension>{metadata["width"]}</exif:PixelXDimension>')
        if metadata.get('height'):
            properties.append(f'<tiff:ImageLength>{metadata["height"]}</tiff:ImageLength>')
            properties.append(f'<exif:PixelYDimension>{metadata["height"]}</exif:PixelYDimension>')
        if metadata.get('orientation') is not None:
            properties.append(f'<tiff:Orientation>{metadata["orientation"]}</tiff:Orientation>')

        # === PROFESSIONAL CAMERA SETTINGS ===
        if metadata.get('scene_mode') is not None:
            scene_modes = {
                0: "Standard", 1: "Landscape", 2: "Portrait", 3: "Night scene",
                4: "Back light", 5: "Sport", 6: "Night portrait", 7: "Party/Indoor",
                8: "Beach/Snow", 9: "Sunset", 10: "Dusk/Dawn", 11: "Pet portrait",
                12: "Candlelight", 13: "Blossom", 14: "Autumn", 15: "Food"
            }
            scene = scene_modes.get(metadata["scene_mode"], str(metadata["scene_mode"]))
            properties.append(f'<exif:SceneCaptureType>{scene}</exif:SceneCaptureType>')

        if metadata.get('shooting_mode'):
            properties.append(f'<aux:ShootingMode>{self._escape_xml(metadata["shooting_mode"])}</aux:ShootingMode>')
        if metadata.get('image_quality'):
            properties.append(f'<aux:ImageQuality>{self._escape_xml(metadata["image_quality"])}</aux:ImageQuality>')
        if metadata.get('noise_reduction'):
            properties.append(f'<aux:NoiseReduction>{self._escape_xml(metadata["noise_reduction"])}</aux:NoiseReduction>')
        if metadata.get('vignette_control'):
            properties.append(f'<aux:VignetteControl>{metadata["vignette_control"]}</aux:VignetteControl>')

        # === FILE INFORMATION ===
        if metadata.get('file_name'):
            properties.append(f'<photoshop:DocumentAncestors><rdf:Bag><rdf:li>{self._escape_xml(metadata["file_name"])}</rdf:li></rdf:Bag></photoshop:DocumentAncestors>')
        if metadata.get('file_size'):
            properties.append('<tiff:BitsPerSample>16</tiff:BitsPerSample>')  # Assuming RAW
        if metadata.get('file_extension'):
            properties.append(f'<dc:format>image/{metadata["file_extension"][1:].lower()}</dc:format>')

        # === GPS INFORMATION ===
        if metadata.get('gps'):
            gps = metadata['gps']
            if gps.get('latitude') is not None:
                lat = gps['latitude']
                lat_ref = 'N' if lat >= 0 else 'S'
                properties.append(f'<exif:GPSLatitude>{abs(lat)}</exif:GPSLatitude>')
                properties.append(f'<exif:GPSLatitudeRef>{lat_ref}</exif:GPSLatitudeRef>')
            if gps.get('longitude') is not None:
                lon = gps['longitude']
                lon_ref = 'E' if lon >= 0 else 'W'
                properties.append(f'<exif:GPSLongitude>{abs(lon)}</exif:GPSLongitude>')
                properties.append(f'<exif:GPSLongitudeRef>{lon_ref}</exif:GPSLongitudeRef>')
            if gps.get('altitude') is not None:
                properties.append(f'<exif:GPSAltitude>{gps["altitude"]}</exif:GPSAltitude>')
                properties.append('<exif:GPSAltitudeRef>0</exif:GPSAltitudeRef>')

        # === GEOLOCATION INFORMATION ===
        if metadata.get('location'):
            location = metadata['location']
            if location.get('city'):
                properties.append(f'<photoshop:City>{self._escape_xml(location["city"])}</photoshop:City>')
            if location.get('country'):
                properties.append(f'<photoshop:Country>{self._escape_xml(location["country"])}</photoshop:Country>')
            if location.get('state'):
                properties.append(f'<photoshop:State>{self._escape_xml(location["state"])}</photoshop:State>')

        # === CREATOR INFORMATION ===
        if metadata.get('artist'):
            properties.append(f'<dc:creator><rdf:Seq><rdf:li>{self._escape_xml(metadata["artist"])}</rdf:li></rdf:Seq></dc:creator>')
            properties.append(f'<photoshop:AuthorsPosition>{self._escape_xml(metadata["artist"])}</photoshop:AuthorsPosition>')
        if metadata.get('copyright'):
            properties.append(f'<dc:rights>{self._escape_xml(metadata["copyright"])}</dc:rights>')
            properties.append(f'<xmp:Rights><rdf:Alt><rdf:li xml:lang="x-default">{self._escape_xml(metadata["copyright"])}</rdf:li></rdf:Alt></xmp:Rights>')

        # === VIDEO-SPECIFIC METADATA ===
        if metadata.get('media_type') == 'video':
            # Video format and codec information
            if metadata.get('video_codec'):
                properties.append(f'<aux:VideoCodec>{self._escape_xml(metadata["video_codec"])}</aux:VideoCodec>')
            if metadata.get('video_profile'):
                properties.append(f'<aux:VideoProfile>{self._escape_xml(metadata["video_profile"])}</aux:VideoProfile>')
            if metadata.get('video_level'):
                properties.append(f'<aux:VideoLevel>{self._escape_xml(metadata["video_level"])}</aux:VideoLevel>')

            # Video quality and technical specs
            if metadata.get('video_bitrate'):
                properties.append(f'<aux:VideoBitrate>{metadata["video_bitrate"]}</aux:VideoBitrate>')
            if metadata.get('video_framerate'):
                properties.append(f'<aux:VideoFrameRate>{metadata["video_framerate"]}</aux:VideoFrameRate>')
            if metadata.get('video_frame_count'):
                properties.append(f'<aux:VideoFrameCount>{metadata["video_frame_count"]}</aux:VideoFrameCount>')
            if metadata.get('video_bit_depth'):
                properties.append(f'<aux:VideoBitDepth>{metadata["video_bit_depth"]}</aux:VideoBitDepth>')
            if metadata.get('video_color_space'):
                properties.append(f'<aux:VideoColorSpace>{self._escape_xml(metadata["video_color_space"])}</aux:VideoColorSpace>')
            if metadata.get('video_chroma_subsampling'):
                properties.append(f'<aux:VideoChromaSubsampling>{self._escape_xml(metadata["video_chroma_subsampling"])}</aux:VideoChromaSubsampling>')

            # Video display information
            if metadata.get('video_aspect_ratio'):
                properties.append(f'<aux:VideoAspectRatio>{self._escape_xml(metadata["video_aspect_ratio"])}</aux:VideoAspectRatio>')
            if metadata.get('video_pixel_aspect_ratio'):
                properties.append(f'<aux:VideoPixelAspectRatio>{metadata["video_pixel_aspect_ratio"]}</aux:VideoPixelAspectRatio>')
            if metadata.get('video_scan_type'):
                properties.append(f'<aux:VideoScanType>{self._escape_xml(metadata["video_scan_type"])}</aux:VideoScanType>')

            # Audio information
            if metadata.get('audio_codec'):
                properties.append(f'<aux:AudioCodec>{self._escape_xml(metadata["audio_codec"])}</aux:AudioCodec>')
            if metadata.get('audio_bitrate'):
                properties.append(f'<aux:AudioBitrate>{metadata["audio_bitrate"]}</aux:AudioBitrate>')
            if metadata.get('audio_sample_rate'):
                properties.append(f'<aux:AudioSampleRate>{metadata["audio_sample_rate"]}</aux:AudioSampleRate>')
            if metadata.get('audio_channels'):
                properties.append(f'<aux:AudioChannels>{metadata["audio_channels"]}</aux:AudioChannels>')
            if metadata.get('audio_bit_depth'):
                properties.append(f'<aux:AudioBitDepth>{metadata["audio_bit_depth"]}</aux:AudioBitDepth>')
            if metadata.get('audio_language'):
                properties.append(f'<aux:AudioLanguage>{self._escape_xml(metadata["audio_language"])}</aux:AudioLanguage>')

            # Video duration and timing
            if metadata.get('duration_seconds'):
                properties.append(f'<aux:Duration>{metadata["duration_seconds"]}</aux:Duration>')
            if metadata.get('duration_formatted'):
                properties.append(f'<aux:DurationFormatted>{self._escape_xml(metadata["duration_formatted"])}</aux:DurationFormatted>')

            # Video encoding information
            if metadata.get('video_encoder'):
                properties.append(f'<aux:VideoEncoder>{self._escape_xml(metadata["video_encoder"])}</aux:VideoEncoder>')
            if metadata.get('video_encoder_version'):
                properties.append(f'<aux:VideoEncoderVersion>{self._escape_xml(metadata["video_encoder_version"])}</aux:VideoEncoderVersion>')
            if metadata.get('encoding_library'):
                properties.append(f'<aux:EncodingLibrary>{self._escape_xml(metadata["encoding_library"])}</aux:EncodingLibrary>')
            if metadata.get('overall_bitrate'):
                properties.append(f'<aux:OverallBitrate>{metadata["overall_bitrate"]}</aux:OverallBitrate>')

        # === LENSLOGIC PROCESSING INFORMATION ===
        tool_name = "LensLogic - Professional Photo & Video Organizer"
        extraction_method = "PyExifTool & PyMediaInfo" if metadata.get('media_type') == 'video' else "PyExifTool"
        properties.append(f'<xmp:CreatorTool>{tool_name}</xmp:CreatorTool>')
        properties.append(f'<xmp:ModifyDate>{datetime.now().isoformat()}</xmp:ModifyDate>')
        properties.append(f'<photoshop:Instructions>Processed by LensLogic with enhanced metadata extraction using {extraction_method}</photoshop:Instructions>')

        return xmp_template.format(properties='\n            '.join(properties))

    def _escape_xml(self, text: str) -> str:
        """Escape special XML characters"""
        if not isinstance(text, str):
            text = str(text)
        return (text.replace('&', '&amp;')
                   .replace('<', '&lt;')
                   .replace('>', '&gt;')
                   .replace('"', '&quot;')
                   .replace("'", '&#39;'))

    def get_statistics(self, source_directory: str) -> Dict[str, Any]:
        source_path = Path(source_directory)

        if not source_path.exists():
            return {'error': 'Source directory does not exist'}

        stats = {
            'total_files': 0,
            'images': 0,
            'raw_files': 0,
            'videos': 0,
            'unknown': 0,
            'total_size': 0,
            'file_types': {}
        }

        for file_path in source_path.rglob('*'):
            if file_path.is_file():
                stats['total_files'] += 1
                stats['total_size'] += file_path.stat().st_size

                extension = file_path.suffix.lower()

                if extension in self.raw_extensions:
                    stats['raw_files'] += 1
                elif extension in self.image_extensions:
                    stats['images'] += 1
                elif extension in self.video_extensions:
                    stats['videos'] += 1
                else:
                    stats['unknown'] += 1

                if extension not in stats['file_types']:
                    stats['file_types'][extension] = 0
                stats['file_types'][extension] += 1

        stats['total_size_mb'] = round(stats['total_size'] / (1024 * 1024), 2)
        stats['total_size_gb'] = round(stats['total_size'] / (1024 * 1024 * 1024), 2)

        return stats