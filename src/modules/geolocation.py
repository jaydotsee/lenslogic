import logging
import json
import time
from pathlib import Path
from typing import Dict, Any, Optional, Tuple
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError
import hashlib

logger = logging.getLogger(__name__)


class GeolocationService:
    def __init__(self, config: Dict[str, Any], cache_dir: Optional[str] = None):
        self.config = config.get('geolocation', {})
        self.enabled = self.config.get('enabled', True)
        self.reverse_geocode = self.config.get('reverse_geocode', True)
        self.add_location_to_folder = self.config.get('add_location_to_folder', False)
        self.location_folder_pattern = self.config.get('location_folder_pattern', '{country}/{city}')
        self.cache_lookups = self.config.get('cache_lookups', True)

        self.geolocator = Nominatim(user_agent="lenslogic/1.0")

        if cache_dir:
            self.cache_dir = Path(cache_dir)
        else:
            self.cache_dir = Path.home() / '.lenslogic' / 'geocache'

        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.cache_file = self.cache_dir / 'locations.json'
        self.cache = self._load_cache()

        self.last_request_time = 0
        self.min_delay = 1.0

    def _load_cache(self) -> Dict[str, Any]:
        if not self.cache_lookups or not self.cache_file.exists():
            return {}

        try:
            with open(self.cache_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.warning(f"Could not load geocache: {e}")
            return {}

    def _save_cache(self):
        if not self.cache_lookups:
            return

        try:
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(self.cache, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.warning(f"Could not save geocache: {e}")

    def get_location_info(self, latitude: float, longitude: float) -> Optional[Dict[str, str]]:
        if not self.enabled or not self.reverse_geocode:
            return None

        cache_key = self._get_cache_key(latitude, longitude)

        if self.cache_lookups and cache_key in self.cache:
            logger.debug(f"Using cached location for {latitude}, {longitude}")
            return self.cache[cache_key]

        location_info = self._reverse_geocode(latitude, longitude)

        if location_info and self.cache_lookups:
            self.cache[cache_key] = location_info
            self._save_cache()

        return location_info

    def _get_cache_key(self, latitude: float, longitude: float) -> str:
        rounded_lat = round(latitude, 4)
        rounded_lon = round(longitude, 4)

        key_string = f"{rounded_lat}:{rounded_lon}"
        return hashlib.md5(key_string.encode()).hexdigest()

    def _reverse_geocode(self, latitude: float, longitude: float) -> Optional[Dict[str, str]]:
        current_time = time.time()
        elapsed = current_time - self.last_request_time

        if elapsed < self.min_delay:
            time.sleep(self.min_delay - elapsed)

        try:
            location = self.geolocator.reverse((latitude, longitude))
            self.last_request_time = time.time()

            if not location:
                return None

            address = location.raw.get('address', {})

            location_info = {
                'full_address': location.address,
                'country': address.get('country', ''),
                'country_code': address.get('country_code', '').upper(),
                'state': address.get('state', address.get('region', '')),
                'county': address.get('county', ''),
                'city': address.get('city', address.get('town', address.get('village', ''))),
                'suburb': address.get('suburb', address.get('neighbourhood', '')),
                'postcode': address.get('postcode', ''),
                'road': address.get('road', ''),
                'house_number': address.get('house_number', ''),
            }

            for key, value in location_info.items():
                if value:
                    location_info[key] = self._sanitize_for_filename(str(value))

            location_info['display_name'] = self._create_display_name(location_info)

            location_info['raw'] = location.raw

            return location_info

        except GeocoderTimedOut:
            logger.warning(f"Geocoding timeout for {latitude}, {longitude}")
            return None
        except GeocoderServiceError as e:
            logger.warning(f"Geocoding service error: {e}")
            return None
        except Exception as e:
            logger.error(f"Error reverse geocoding {latitude}, {longitude}: {e}")
            return None

    def _sanitize_for_filename(self, text: str) -> str:
        invalid_chars = ['<', '>', ':', '"', '/', '\\', '|', '?', '*']
        for char in invalid_chars:
            text = text.replace(char, '_')

        text = ' '.join(text.split())

        return text[:50]

    def _create_display_name(self, location_info: Dict[str, str]) -> str:
        parts = []

        if location_info.get('city'):
            parts.append(location_info['city'])
        elif location_info.get('suburb'):
            parts.append(location_info['suburb'])

        if location_info.get('state'):
            parts.append(location_info['state'])

        if location_info.get('country'):
            parts.append(location_info['country'])

        return ', '.join(parts) if parts else 'Unknown Location'

    def format_location_folder(self, location_info: Dict[str, str]) -> str:
        if not location_info or not self.add_location_to_folder:
            return ''

        try:
            folder_path = self.location_folder_pattern.format(**location_info)

            folder_path = folder_path.replace('//', '/')
            folder_path = folder_path.strip('/')

            return folder_path
        except KeyError as e:
            logger.warning(f"Invalid location folder pattern variable: {e}")
            return ''
        except Exception as e:
            logger.error(f"Error formatting location folder: {e}")
            return ''

    def extract_gps_from_metadata(self, metadata: Dict[str, Any]) -> Optional[Tuple[float, float]]:
        if not metadata.get('gps'):
            return None

        gps_data = metadata['gps']

        latitude = gps_data.get('latitude')
        longitude = gps_data.get('longitude')

        if latitude is not None and longitude is not None:
            try:
                lat = float(latitude)
                lon = float(longitude)

                if -90 <= lat <= 90 and -180 <= lon <= 180:
                    return (lat, lon)
            except (ValueError, TypeError):
                pass

        return None

    def add_location_to_metadata(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        if not self.enabled:
            return metadata

        gps_coords = self.extract_gps_from_metadata(metadata)

        if gps_coords:
            latitude, longitude = gps_coords
            location_info = self.get_location_info(latitude, longitude)

            if location_info:
                metadata['location'] = location_info
                logger.info(f"Added location info: {location_info['display_name']}")

        return metadata

    def create_location_map(self, photos_with_location: list) -> Dict[str, list]:
        location_map = {}

        for photo_info in photos_with_location:
            if photo_info.get('location'):
                location = photo_info['location']
                key = location.get('display_name', 'Unknown')

                if key not in location_map:
                    location_map[key] = []

                location_map[key].append({
                    'file': photo_info['file'],
                    'latitude': photo_info['gps']['latitude'],
                    'longitude': photo_info['gps']['longitude'],
                    'datetime': photo_info.get('datetime_original')
                })

        return location_map

    def export_kml(self, photos_with_location: list, output_path: str):
        kml_template = '''<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
  <Document>
    <name>Photo Locations</name>
    <description>Locations of organized photos</description>
    {placemarks}
  </Document>
</kml>'''

        placemark_template = '''    <Placemark>
      <name>{name}</name>
      <description>{description}</description>
      <Point>
        <coordinates>{longitude},{latitude},0</coordinates>
      </Point>
    </Placemark>'''

        placemarks = []

        for photo_info in photos_with_location:
            if photo_info.get('gps'):
                gps = photo_info['gps']
                name = Path(photo_info['file']).name
                description = photo_info.get('location', {}).get('display_name', 'No location info')

                placemark = placemark_template.format(
                    name=name,
                    description=description,
                    latitude=gps['latitude'],
                    longitude=gps['longitude']
                )
                placemarks.append(placemark)

        kml_content = kml_template.format(placemarks='\n'.join(placemarks))

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(kml_content)

        logger.info(f"Exported KML file to {output_path}")

    def clear_cache(self):
        self.cache.clear()
        if self.cache_file.exists():
            self.cache_file.unlink()
        logger.info("Geocache cleared")