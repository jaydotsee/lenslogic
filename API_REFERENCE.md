# LensLogic API Reference

## Table of Contents
1. [Core Classes](#core-classes)
2. [Metadata Extractors](#metadata-extractors)
3. [File Processors](#file-processors)
4. [Utilities](#utilities)
5. [Configuration API](#configuration-api)
6. [Plugin System](#plugin-system)
7. [Error Handling](#error-handling)
8. [Examples](#examples)

## Core Classes

### LensLogic (`main.py`)

The main orchestrator class that coordinates all photo organization operations.

```python
class LensLogic:
    """Main LensLogic application class"""

    def __init__(self, config_path: Optional[str] = None,
                 args: Optional[Dict[str, Any]] = None):
        """
        Initialize LensLogic with configuration.

        Args:
            config_path: Path to configuration file
            args: Dictionary of configuration overrides
        """

    def organize_photos(self, source_dir: str, destination_dir: Optional[str] = None,
                       dry_run: bool = False) -> Dict[str, Any]:
        """
        Organize photos from source to destination directory.

        Args:
            source_dir: Source directory containing photos
            destination_dir: Destination directory for organized photos
            dry_run: If True, preview changes without executing

        Returns:
            Dict containing organization results:
            {
                'total_processed': int,
                'successful': int,
                'failed': int,
                'skipped': int,
                'errors': List[str],
                'statistics': Dict[str, Any]
            }
        """

    def analyze_xmp_library(self, library_path: Optional[str] = None,
                           output_dir: Optional[str] = None) -> Dict[str, Any]:
        """
        Analyze XMP sidecar files in a directory.

        Args:
            library_path: Path to library containing XMP files
            output_dir: Directory for analysis output

        Returns:
            Dict containing analysis results
        """

    def generate_statistics(self, source_dir: str) -> Dict[str, Any]:
        """
        Generate comprehensive statistics for a photo library.

        Args:
            source_dir: Directory containing organized photos

        Returns:
            Dict containing detailed statistics
        """
```

### ConfigManager (`utils/config_manager.py`)

Manages configuration loading, validation, and updates.

```python
class ConfigManager:
    """Configuration management with hierarchical loading"""

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize configuration manager.

        Args:
            config_path: Path to custom configuration file
        """

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value using dot notation.

        Args:
            key: Configuration key (e.g., 'general.source_directory')
            default: Default value if key not found

        Returns:
            Configuration value or default
        """

    def update(self, updates: Dict[str, Any]) -> None:
        """
        Update configuration with new values.

        Args:
            updates: Dictionary of configuration updates
        """

    def validate(self) -> List[str]:
        """
        Validate configuration and return list of errors.

        Returns:
            List of validation error messages
        """

    def save_user_config(self) -> bool:
        """
        Save current configuration to user config file.

        Returns:
            True if saved successfully, False otherwise
        """
```

## Metadata Extractors

### EnhancedExifExtractor (`modules/enhanced_exif_extractor.py`)

Professional metadata extraction with multiple engine support.

```python
class EnhancedExifExtractor:
    """Enhanced EXIF extraction with professional features"""

    def __init__(self):
        """Initialize extractor with available engines"""

    def extract_metadata(self, file_path: str) -> Dict[str, Any]:
        """
        Extract comprehensive metadata from image or video file.

        Args:
            file_path: Path to media file

        Returns:
            Dictionary containing extracted metadata:
            {
                'file_path': str,
                'file_name': str,
                'file_size': int,
                'file_extension': str,
                'file_modified': datetime,
                'file_created': datetime,
                'width': int,
                'height': int,
                'camera_make': str,
                'camera_model': str,
                'lens_model': str,
                'datetime_original': datetime,
                'iso': int,
                'f_number': float,
                'exposure_time': float,
                'focal_length': float,
                'gps': {
                    'latitude': float,
                    'longitude': float,
                    'altitude': float
                },
                'software': str,
                'artist': str,
                'copyright': str
            }
        """

    def get_capture_datetime(self, metadata: Dict[str, Any]) -> Optional[datetime]:
        """
        Get the best available capture datetime from metadata.

        Args:
            metadata: Metadata dictionary from extract_metadata()

        Returns:
            Datetime object or None if no valid datetime found
        """

    def clear_cache(self) -> None:
        """Clear the metadata cache"""

    def get_supported_formats(self) -> List[str]:
        """
        Get list of supported file formats.

        Returns:
            List of supported file extensions (without dots)
        """

    def get_extraction_method(self) -> str:
        """
        Get current extraction method being used.

        Returns:
            String describing extraction method
        """
```

### EnhancedVideoExtractor (`modules/enhanced_video_extractor.py`)

Specialized video metadata extraction using MediaInfo.

```python
class EnhancedVideoExtractor:
    """Enhanced video metadata extraction"""

    def __init__(self):
        """Initialize video extractor"""

    def extract_metadata(self, file_path: str) -> Dict[str, Any]:
        """
        Extract metadata from video file.

        Args:
            file_path: Path to video file

        Returns:
            Dictionary containing video metadata:
            {
                'file_path': str,
                'file_name': str,
                'file_size': int,
                'duration_ms': int,
                'duration_seconds': float,
                'duration_formatted': str,
                'video_width': int,
                'video_height': int,
                'video_codec': str,
                'video_bitrate': int,
                'video_framerate': float,
                'audio_codec': str,
                'audio_bitrate': int,
                'audio_channels': int,
                'container_format': str,
                'datetime_original': datetime
            }
        """

    def get_supported_formats(self) -> List[str]:
        """Get list of supported video formats"""

    def get_extraction_method(self) -> str:
        """Get current extraction method"""
```

## File Processors

### FileRenamer (`modules/file_renamer.py`)

Intelligent file renaming with metadata-driven templates.

```python
class FileRenamer:
    """File renaming with template system"""

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize file renamer with configuration.

        Args:
            config: Configuration dictionary
        """

    def generate_new_name(self, file_path: str, metadata: Dict[str, Any],
                         destination_folder: Optional[str] = None) -> str:
        """
        Generate new filename based on metadata and templates.

        Args:
            file_path: Original file path
            metadata: Metadata dictionary
            destination_folder: Target destination folder

        Returns:
            New filename with extension
        """

    def preview_rename(self, file_path: str, metadata: Dict[str, Any]) -> Dict[str, str]:
        """
        Preview rename operation without executing.

        Args:
            file_path: Original file path
            metadata: Metadata dictionary

        Returns:
            Dictionary with rename preview:
            {
                'original': str,
                'new_name': str,
                'original_name': str,
                'would_change': bool
            }
        """

    def reset_counters(self) -> None:
        """Reset sequence number counters"""
```

### FolderOrganizer (`modules/folder_organizer.py`)

Dynamic folder structure creation based on metadata.

```python
class FolderOrganizer:
    """Folder organization with configurable structures"""

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize folder organizer.

        Args:
            config: Configuration dictionary
        """

    def determine_destination_path(self, file_path: str, metadata: Dict[str, Any],
                                  base_destination: str,
                                  location_info: Optional[Dict[str, str]] = None) -> Path:
        """
        Determine destination path for file based on metadata.

        Args:
            file_path: Source file path
            metadata: File metadata
            base_destination: Base destination directory
            location_info: Optional location information

        Returns:
            Path object for destination directory
        """

    def create_folder_structure(self, base_path: str,
                               structure_info: Dict[str, Any]) -> Path:
        """
        Create folder structure based on template.

        Args:
            base_path: Base directory path
            structure_info: Dictionary with folder structure variables

        Returns:
            Created directory path
        """
```

### GeolocationService (`modules/geolocation.py`)

GPS coordinate extraction and reverse geocoding.

```python
class GeolocationService:
    """GPS and geolocation services"""

    def __init__(self, config: Dict[str, Any], cache_dir: Optional[str] = None):
        """
        Initialize geolocation service.

        Args:
            config: Configuration dictionary
            cache_dir: Directory for location cache
        """

    def extract_gps_from_metadata(self, metadata: Dict[str, Any]) -> Optional[Tuple[float, float]]:
        """
        Extract GPS coordinates from metadata.

        Args:
            metadata: Metadata dictionary

        Returns:
            Tuple of (latitude, longitude) or None
        """

    def get_location_info(self, latitude: float, longitude: float) -> Optional[Dict[str, str]]:
        """
        Get location information from coordinates.

        Args:
            latitude: GPS latitude
            longitude: GPS longitude

        Returns:
            Dictionary with location information:
            {
                'city': str,
                'country': str,
                'state': str,
                'address': str
            }
        """

    def export_locations_to_kml(self, locations: List[Dict[str, Any]],
                               output_file: str) -> bool:
        """
        Export locations to KML file.

        Args:
            locations: List of location dictionaries
            output_file: Output KML file path

        Returns:
            True if exported successfully
        """
```

## Utilities

### ProgressTracker (`utils/progress_tracker.py`)

Progress tracking with rich console output.

```python
class ProgressTracker:
    """Progress tracking with rich console display"""

    def __init__(self, console: Optional[Console] = None):
        """
        Initialize progress tracker.

        Args:
            console: Rich console instance
        """

    def start_task(self, description: str, total: Optional[int] = None) -> str:
        """
        Start a new progress task.

        Args:
            description: Task description
            total: Total number of items (None for indeterminate)

        Returns:
            Task ID for updates
        """

    def update_task(self, task_id: str, advance: int = 1,
                   description: Optional[str] = None) -> None:
        """
        Update task progress.

        Args:
            task_id: Task ID from start_task()
            advance: Number of items to advance
            description: Updated description
        """

    def finish_task(self, task_id: str) -> None:
        """
        Mark task as completed.

        Args:
            task_id: Task ID to finish
        """

    def display_summary(self, results: Dict[str, Any]) -> None:
        """
        Display operation summary.

        Args:
            results: Results dictionary to display
        """
```

### CameraSlugger (`utils/camera_slugger.py`)

Camera name simplification and slugging.

```python
class CameraSlugger:
    """Camera name simplification"""

    def __init__(self, custom_mappings: Optional[Dict[str, str]] = None):
        """
        Initialize camera slugger.

        Args:
            custom_mappings: Custom camera name mappings
        """

    def create_slug(self, camera_make: str, camera_model: str) -> str:
        """
        Create simplified camera slug.

        Args:
            camera_make: Camera manufacturer
            camera_model: Camera model

        Returns:
            Simplified camera slug
        """

    def get_examples(self) -> Dict[str, str]:
        """
        Get examples of camera name mappings.

        Returns:
            Dictionary of example mappings
        """

def get_camera_slug(camera_make: str = '', camera_model: str = '',
                   custom_mappings: Optional[Dict[str, str]] = None) -> str:
    """
    Convenience function to get camera slug.

    Args:
        camera_make: Camera manufacturer
        camera_model: Camera model
        custom_mappings: Custom mappings

    Returns:
        Camera slug string
    """
```

## Configuration API

### Configuration Schema

The configuration system uses a hierarchical YAML structure:

```yaml
general:
  source_directory: str
  destination_directory: str
  verbosity: str  # DEBUG, INFO, WARNING, ERROR
  log_file: Optional[str]
  dry_run: bool

organization:
  folder_structure: str  # Template string
  folder_structure_with_location: str
  folder_structure_templates: Dict[str, str]
  separate_raw: bool
  raw_folder: str
  jpg_folder: str
  video_folder: str
  unknown_folder: str
  date_sources: List[str]

naming:
  pattern: str  # Template string
  include_sequence: bool
  sequence_padding: int
  lowercase_extension: bool
  replacements: Dict[str, str]
  camera_names: Dict[str, str]

file_types:
  images: List[str]
  raw: List[str]
  videos: List[str]

features:
  extract_gps: bool
  detect_duplicates: bool
  detect_sessions: bool
  generate_sidecars: bool
  backup_enabled: bool

geolocation:
  enabled: bool
  reverse_geocode: bool
  add_location_to_folder: bool
  location_components: str  # city, country, city_country
  cache_locations: bool
  rate_limit_delay: float
  export_kml: bool

duplicate_detection:
  method: str  # hash, pixel, perceptual
  action: str  # skip, rename, move, interactive
  similarity_threshold: float
  move_to_folder: str

session_detection:
  time_threshold_hours: int
  location_threshold_km: float
  create_session_folders: bool
  session_naming: str  # auto, date, location

backup:
  destinations: List[str]
  enable_verification: bool
  incremental_mode: bool
  use_trash: bool
  checksum_cache: str

statistics:
  enable_charts: bool
  chart_output_dir: str

image_processing:
  auto_rotate: bool
  auto_enhance: bool
  generate_thumbnails: bool
  thumbnail_sizes: List[int]
```

### Configuration Access

```python
# Direct access
config = ConfigManager()
source_dir = config.get('general.source_directory')

# With default
verbosity = config.get('general.verbosity', 'INFO')

# Nested access
folder_structure = config.get('organization.folder_structure')

# Update configuration
config.update({
    'general.verbosity': 'DEBUG',
    'features.extract_gps': True
})

# Validate configuration
errors = config.validate()
if errors:
    for error in errors:
        print(f"Configuration error: {error}")
```

### Template Variables

#### File Naming Templates

Available variables for `naming.pattern`:

| Variable | Type | Description | Example |
|----------|------|-------------|---------|
| `{year}` | int | Photo year | `2024` |
| `{month}` | int | Month (1-12) | `3` |
| `{month:02d}` | str | Zero-padded month | `03` |
| `{day}` | int | Day of month | `15` |
| `{hour}` | int | Hour (0-23) | `14` |
| `{minute}` | int | Minute (0-59) | `30` |
| `{second}` | int | Second (0-59) | `22` |
| `{date}` | str | YYYYMMDD format | `20240315` |
| `{time}` | str | HHMMSS format | `143022` |
| `{timestamp}` | int | Unix timestamp | `1710507022` |
| `{camera}` | str | Camera slug | `iphone15pro` |
| `{camera_make}` | str | Camera make | `Apple` |
| `{camera_model}` | str | Camera model | `iPhone 15 Pro` |
| `{lens}` | str | Lens model | `85mm f/1.4` |
| `{iso}` | int | ISO setting | `400` |
| `{f_number}` | float | Aperture | `2.8` |
| `{exposure}` | float | Shutter speed | `0.004` |
| `{focal_length}` | float | Focal length | `85.0` |
| `{original_name}` | str | Original filename | `IMG_1234` |
| `{original_sequence}` | str | Sequence from original filename | `8151` (from ZF0_8151.JPG) |
| `{width}` | int | Image width | `4032` |
| `{height}` | int | Image height | `3024` |
| `{has_gps}` | str | GPS indicator | `GPS` or `` |
| `{latitude}` | float | GPS latitude | `37.7749` |
| `{longitude}` | float | GPS longitude | `-122.4194` |
| `{artist}` | str | Artist/photographer | `John Doe` |
| `{software}` | str | Software used | `Adobe Lightroom` |

#### Folder Structure Templates

Available variables for `organization.folder_structure`:

| Variable | Type | Description | Example |
|----------|------|-------------|---------|
| `{year}` | int | Photo year | `2024` |
| `{month}` | int | Month | `3` |
| `{month:02d}` | str | Zero-padded month | `03` |
| `{day}` | int | Day | `15` |
| `{hour}` | int | Hour | `14` |
| `{date}` | str | YYYYMMDD | `20240315` |
| `{year_month}` | str | YYYY-MM | `2024-03` |
| `{month_name}` | str | Full month name | `March` |
| `{month_short}` | str | Short month name | `Mar` |
| `{weekday}` | str | Full weekday name | `Friday` |
| `{week}` | str | Week number | `11` |
| `{camera}` | str | Camera slug | `iphone15pro` |
| `{city}` | str | City name | `San Francisco` |
| `{country}` | str | Country name | `United States` |
| `{location}` | str | Primary location | `San Francisco` |

## Plugin System

### Plugin Interface

```python
class LensLogicPlugin:
    """Base plugin interface"""

    # Plugin metadata
    NAME: str = ""
    VERSION: str = "1.0.0"
    DESCRIPTION: str = ""
    AUTHOR: str = ""

    # Hook registration
    HOOKS: List[str] = []

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize plugin with configuration.

        Args:
            config: Plugin configuration
        """
        self.config = config

    def initialize(self) -> bool:
        """
        Initialize plugin resources.

        Returns:
            True if initialization successful
        """
        return True

    def cleanup(self) -> None:
        """Cleanup plugin resources"""
        pass
```

### Available Hooks

```python
# Pre-processing hooks
def pre_metadata_extraction(self, file_path: str) -> Optional[Dict[str, Any]]:
    """Called before metadata extraction"""

def post_metadata_extraction(self, file_path: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
    """Called after metadata extraction"""

# Processing hooks
def pre_file_processing(self, file_path: str, metadata: Dict[str, Any]) -> bool:
    """Called before file processing. Return False to skip file."""

def post_file_processing(self, file_path: str, destination_path: str,
                        metadata: Dict[str, Any]) -> None:
    """Called after file processing"""

# Organization hooks
def custom_folder_structure(self, metadata: Dict[str, Any]) -> Optional[str]:
    """Provide custom folder structure"""

def custom_filename(self, file_path: str, metadata: Dict[str, Any]) -> Optional[str]:
    """Provide custom filename"""

# Analysis hooks
def custom_statistics(self, metadata_list: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Provide custom statistics"""
```

### Plugin Registration

```python
from modules.plugin_manager import PluginManager

# Register plugin
plugin_manager = PluginManager()
plugin_manager.register_plugin('watermark', WatermarkPlugin)

# Execute hooks
results = plugin_manager.execute_hook('post_file_processing',
                                     file_path, destination_path, metadata)
```

### Example Plugin

```python
class WatermarkPlugin(LensLogicPlugin):
    """Add watermarks to processed images"""

    NAME = "Watermark Plugin"
    VERSION = "1.0.0"
    DESCRIPTION = "Adds watermarks to processed images"
    AUTHOR = "LensLogic Team"
    HOOKS = ['post_file_processing']

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.watermark_text = config.get('watermark_text', '© LensLogic')
        self.watermark_position = config.get('position', 'bottom-right')

    def post_file_processing(self, file_path: str, destination_path: str,
                           metadata: Dict[str, Any]) -> None:
        """Add watermark after file processing"""

        if not destination_path.lower().endswith(('.jpg', '.jpeg', '.png')):
            return

        try:
            from PIL import Image, ImageDraw, ImageFont

            # Open processed image
            with Image.open(destination_path) as img:
                # Create watermark
                draw = ImageDraw.Draw(img)

                # Calculate position
                x, y = self._calculate_position(img.size)

                # Add watermark
                draw.text((x, y), self.watermark_text, fill=(255, 255, 255, 128))

                # Save with watermark
                img.save(destination_path)

        except Exception as e:
            logger.warning(f"Failed to add watermark to {destination_path}: {e}")
```

## Error Handling

### Exception Classes

```python
class LensLogicError(Exception):
    """Base exception for LensLogic"""
    pass

class ConfigurationError(LensLogicError):
    """Configuration-related errors"""
    pass

class MetadataExtractionError(LensLogicError):
    """Metadata extraction errors"""
    pass

class FileProcessingError(LensLogicError):
    """File processing errors"""
    pass

class GeolocationError(LensLogicError):
    """Geolocation service errors"""
    pass
```

### Error Handling Patterns

```python
# Graceful degradation
try:
    metadata = extractor.extract_metadata(file_path)
except MetadataExtractionError as e:
    logger.warning(f"Metadata extraction failed for {file_path}: {e}")
    metadata = {'file_path': file_path, 'error': str(e)}

# Retry with backoff
import time
from functools import wraps

def retry_with_backoff(max_retries: int = 3, delay: float = 1.0):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_retries - 1:
                        raise
                    time.sleep(delay * (2 ** attempt))
            return None
        return wrapper
    return decorator

@retry_with_backoff(max_retries=3)
def get_location_info(self, lat: float, lon: float):
    """Get location with retry"""
    return self.geolocator.reverse(f"{lat}, {lon}")
```

## Examples

### Basic Usage

```python
from main import LensLogic

# Initialize with default configuration
lens_logic = LensLogic()

# Organize photos
result = lens_logic.organize_photos(
    source_dir='/Users/photographer/Unsorted',
    destination_dir='/Users/photographer/Organized'
)

print(f"Processed {result['total_processed']} files")
print(f"Successful: {result['successful']}")
print(f"Failed: {result['failed']}")
```

### Custom Configuration

```python
from utils.config_manager import ConfigManager
from main import LensLogic

# Load custom configuration
config = ConfigManager('my_config.yaml')

# Override specific settings
config.update({
    'naming.pattern': '{year}{month:02d}{day:02d}_{camera}_{original_name}',
    'organization.folder_structure': '{year}/{month:02d}/{camera}',
    'features.extract_gps': True,
    'features.detect_duplicates': True
})

# Initialize LensLogic
lens_logic = LensLogic(config=config)

# Process with custom settings
result = lens_logic.organize_photos(
    source_dir='/path/to/photos',
    dry_run=True  # Preview changes first
)
```

### Metadata Extraction

```python
from modules.enhanced_exif_extractor import EnhancedExifExtractor

# Initialize extractor
extractor = EnhancedExifExtractor()

# Extract metadata
metadata = extractor.extract_metadata('/path/to/photo.jpg')

# Access metadata
print(f"Camera: {metadata.get('camera_make')} {metadata.get('camera_model')}")
print(f"Date: {metadata.get('datetime_original')}")

if 'gps' in metadata:
    gps = metadata['gps']
    print(f"Location: {gps['latitude']}, {gps['longitude']}")
```

### File Renaming

```python
from modules.file_renamer import FileRenamer

# Configuration for renaming
config = {
    'naming': {
        'pattern': '{year}{month:02d}{day:02d}_{time}_{camera}',
        'include_sequence': True,
        'lowercase_extension': True
    }
}

# Initialize renamer
renamer = FileRenamer(config)

# Generate new name
new_name = renamer.generate_new_name(
    file_path='/path/to/IMG_1234.jpg',
    metadata={
        'datetime_original': datetime(2024, 3, 15, 14, 30, 22),
        'camera': 'iphone15pro'
    }
)

print(f"New name: {new_name}")  # 20240315_143022_iphone15pro.jpg
```

### Folder Organization

```python
from modules.folder_organizer import FolderOrganizer

# Configuration
config = {
    'organization': {
        'folder_structure': '{year}/{month:02d}/{day:02d}',
        'folder_structure_with_location': '{year}/{month:02d}/{city}',
        'separate_raw': True,
        'raw_folder': 'RAW'
    },
    'geolocation': {
        'add_location_to_folder': True
    }
}

# Initialize organizer
organizer = FolderOrganizer(config)

# Determine destination
destination = organizer.determine_destination_path(
    file_path='/path/to/photo.cr3',
    metadata={
        'datetime_original': datetime(2024, 3, 15),
        'file_extension': '.cr3'
    },
    base_destination='/organized',
    location_info={'city': 'Paris'}
)

print(f"Destination: {destination}")  # /organized/RAW/2024/03/Paris
```

### Geolocation Services

```python
from modules.geolocation import GeolocationService

# Initialize service
geo_service = GeolocationService({
    'geolocation': {
        'enabled': True,
        'reverse_geocode': True,
        'cache_locations': True
    }
})

# Extract GPS from metadata
coords = geo_service.extract_gps_from_metadata({
    'gps': {
        'latitude': 37.7749,
        'longitude': -122.4194
    }
})

if coords:
    lat, lon = coords

    # Get location information
    location = geo_service.get_location_info(lat, lon)

    if location:
        print(f"Location: {location['city']}, {location['country']}")
```

### Statistics Generation

```python
from modules.statistics_generator import StatisticsGenerator

# Initialize generator
stats_gen = StatisticsGenerator({
    'statistics': {
        'enable_charts': True,
        'chart_output_dir': '/output/charts'
    }
})

# Generate statistics
photos_metadata = [
    # List of metadata dictionaries
]

stats = stats_gen.generate_library_statistics(photos_metadata)

# Access statistics
print(f"Total photos: {stats['total_photos']}")
print(f"Date range: {stats['date_range']}")
print(f"Top camera: {list(stats['cameras'].keys())[0]}")
```

This API reference provides comprehensive documentation for all public interfaces in LensLogic, making it easy for developers to integrate, extend, and use the system programmatically.