import logging
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, Union
from pathvalidate import sanitize_filename

logger = logging.getLogger(__name__)


class FileRenamer:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.naming_config = config.get('naming', {})
        self.pattern = self.naming_config.get('pattern', '{year}{month:02d}{day:02d}_{original_name}')
        self.include_sequence = self.naming_config.get('include_sequence', True)
        self.sequence_padding = self.naming_config.get('sequence_padding', 3)
        self.lowercase_extension = self.naming_config.get('lowercase_extension', True)
        self.replacements = self.naming_config.get('replacements', {' ': '_', '-': '_'})
        self.camera_names = self.naming_config.get('camera_names', {})
        self.counters = {}

    def generate_new_name(self, file_path: str, metadata: Dict[str, Any],
                         destination_folder: Optional[str] = None) -> str:
        file_path_obj = Path(file_path)
        original_name = file_path_obj.stem
        extension = file_path_obj.suffix

        if self.lowercase_extension:
            extension = extension.lower()

        capture_datetime = self._get_datetime_from_metadata(metadata)

        if not capture_datetime:
            capture_datetime = datetime.now()
            logger.warning(f"No datetime found for {file_path_obj}, using current time")

        template_vars = self._create_template_variables(
            file_path_obj, metadata, capture_datetime, original_name
        )

        new_name = self._format_pattern(self.pattern, template_vars)

        new_name = self._apply_replacements(new_name)

        new_name = sanitize_filename(new_name)

        if self.include_sequence and destination_folder:
            new_name = self._add_sequence_number(new_name, destination_folder, extension)

        final_name = f"{new_name}{extension}"

        return final_name

    def _get_datetime_from_metadata(self, metadata: Dict[str, Any]) -> Optional[datetime]:
        date_sources = self.config.get('organization', {}).get('date_sources', [
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

    def _create_template_variables(self, file_path: Path, metadata: Dict[str, Any],
                                  capture_datetime: datetime, original_name: str) -> Dict[str, Any]:
        variables = {
            'original_name': original_name,
            'year': capture_datetime.year,
            'month': capture_datetime.month,
            'day': capture_datetime.day,
            'hour': capture_datetime.hour,
            'minute': capture_datetime.minute,
            'second': capture_datetime.second,
            'date': capture_datetime.strftime('%Y%m%d'),
            'time': capture_datetime.strftime('%H%M%S'),
            'timestamp': int(capture_datetime.timestamp()),
        }

        camera_make = (metadata.get('camera_make') or '').strip()
        camera_model = (metadata.get('camera_model') or '').strip()

        if camera_model or camera_make:
            camera = self._simplify_camera_name_enhanced(camera_make, camera_model)
        else:
            camera = 'unknown'

        variables['camera'] = camera
        variables['camera_make'] = camera_make
        variables['camera_model'] = camera_model

        variables['lens'] = (metadata.get('lens_model') or '').strip()
        variables['iso'] = metadata.get('iso', '')
        variables['f_number'] = metadata.get('f_number', '')
        variables['exposure'] = metadata.get('exposure_time', '')
        variables['focal_length'] = metadata.get('focal_length', '')

        variables['width'] = metadata.get('width', '')
        variables['height'] = metadata.get('height', '')

        if metadata.get('gps'):
            variables['has_gps'] = 'GPS'
            variables['latitude'] = metadata['gps'].get('latitude', '')
            variables['longitude'] = metadata['gps'].get('longitude', '')
        else:
            variables['has_gps'] = ''
            variables['latitude'] = ''
            variables['longitude'] = ''

        # Handle potentially None values safely
        artist_value = metadata.get('artist', '') or ''
        software_value = metadata.get('software', '') or ''
        variables['artist'] = artist_value.strip() if artist_value else ''
        variables['software'] = software_value.strip() if software_value else ''

        return variables

    def _simplify_camera_name(self, camera_name: str) -> str:
        from utils.camera_slugger import get_camera_slug

        # Use the new slugger with enhanced pattern matching
        return get_camera_slug('', camera_name, self.camera_names)

    def _simplify_camera_name_enhanced(self, camera_make: str, camera_model: str) -> str:
        from utils.camera_slugger import get_camera_slug

        # Use the new slugger with both make and model for better pattern matching
        return get_camera_slug(camera_make, camera_model, self.camera_names)

    def _format_pattern(self, pattern: str, variables: Dict[str, Any]) -> str:
        try:
            formatted = pattern.format(**variables)

            formatted = re.sub(r'_{2,}', '_', formatted)
            formatted = re.sub(r'-{2,}', '-', formatted)

            formatted = formatted.strip('_-')

            return formatted
        except KeyError as e:
            logger.error(f"Invalid pattern variable: {e}")
            return f"{variables['date']}_{variables['original_name']}"
        except Exception as e:
            logger.error(f"Error formatting pattern: {e}")
            return f"{variables['date']}_{variables['original_name']}"

    def _apply_replacements(self, name: str) -> str:
        for old, new in self.replacements.items():
            name = name.replace(old, new)

        return name

    def _add_sequence_number(self, base_name: str, destination_folder: str,
                            extension: str) -> str:
        if not destination_folder:
            return base_name

        destination_path = Path(destination_folder)

        counter_key = f"{destination_folder}:{base_name}"

        if counter_key not in self.counters:
            existing_files = list(destination_path.glob(f"{base_name}*{extension}"))

            if not existing_files:
                return base_name

            max_sequence = 0
            pattern = re.compile(rf"{re.escape(base_name)}_(\d+){re.escape(extension)}$")

            for file in existing_files:
                match = pattern.match(file.name)
                if match:
                    seq_num = int(match.group(1))
                    max_sequence = max(max_sequence, seq_num)

            if destination_path.joinpath(f"{base_name}{extension}").exists():
                max_sequence = max(max_sequence, 0)

            self.counters[counter_key] = max_sequence

        self.counters[counter_key] += 1
        sequence = str(self.counters[counter_key]).zfill(self.sequence_padding)

        return f"{base_name}_{sequence}"

    def reset_counters(self):
        self.counters.clear()

    def preview_rename(self, file_path: str, metadata: Dict[str, Any]) -> Dict[str, Union[str, bool]]:
        original_path = Path(file_path)
        new_name = self.generate_new_name(file_path, metadata)

        return {
            'original': str(original_path),
            'new_name': new_name,
            'original_name': original_path.name,
            'would_change': original_path.name != new_name
        }