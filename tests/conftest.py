"""
Pytest configuration and fixtures for LensLogic tests
"""

import pytest
from pathlib import Path
from unittest.mock import MagicMock
from datetime import datetime


@pytest.fixture
def sample_exif_metadata():
    """Sample EXIF metadata for testing"""
    return {
        'EXIF:Make': 'Apple',
        'EXIF:Model': 'iPhone 15 Pro Max',
        'EXIF:DateTime': '2025:09:19 14:30:25',
        'EXIF:DateTimeOriginal': '2025:09:19 14:30:25',
        'EXIF:ISO': 64,
        'EXIF:FNumber': 1.78,
        'EXIF:ExposureTime': '1/60',
        'EXIF:FocalLength': '24.0 mm',
        'EXIF:ExifImageWidth': 4032,
        'EXIF:ExifImageHeight': 3024,
        'GPS:GPSLatitude': 37.7749,
        'GPS:GPSLongitude': -122.4194,
        'GPS:GPSAltitude': 15.5
    }


@pytest.fixture
def sample_video_metadata():
    """Sample video metadata for testing"""
    return {
        'file_path': '/test/video.mp4',
        'file_name': 'video.mp4',
        'file_extension': '.mp4',
        'file_size': 150000000,
        'datetime_original': datetime(2025, 9, 19, 17, 32, 22),
        'camera_make': 'Apple',
        'camera_model': 'iPhone 15 Pro Max',
        'video_codec': 'H.264',
        'video_width': '1920',
        'video_height': '1080',
        'video_framerate': '60',
        'duration_seconds': 45.2,
        'audio_codec': 'AAC'
    }


@pytest.fixture
def temp_config():
    """Basic configuration for testing"""
    return {
        'general': {
            'source_directory': './test_source',
            'destination_directory': './test_destination',
            'dry_run': False,
            'preserve_originals': True
        },
        'organization': {
            'folder_structure': '{year}/{month:02d}/{day:02d}',
            'separate_raw': True,
            'raw_folder': 'RAW',
            'jpg_folder': 'JPG'
        },
        'naming': {
            'pattern': '{year}{month:02d}{day:02d}_{hour:02d}{minute:02d}{second:02d}_{camera}_{original_name}',
            'camera_names': {
                'Apple iPhone 15 Pro Max': 'iphone15promax'
            }
        },
        'file_types': {
            'raw': ['cr2', 'nef', 'arw'],
            'images': ['jpg', 'jpeg', 'png'],
            'videos': ['mp4', 'mov', 'avi']
        }
    }


@pytest.fixture
def mock_exiftool_session():
    """Mock ExifTool session for testing"""
    session = MagicMock()
    session.get_metadata.return_value = [{}]
    return session