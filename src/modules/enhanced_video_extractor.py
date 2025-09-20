import logging
import warnings
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List

# Suppress specific warnings
warnings.filterwarnings("ignore", category=UserWarning, module="pymediainfo")

logger = logging.getLogger(__name__)

# Try to import pymediainfo
try:
    from pymediainfo import MediaInfo
    MEDIAINFO_AVAILABLE = True
    logger.info("PyMediaInfo available - using for enhanced video metadata extraction")
except ImportError:
    MEDIAINFO_AVAILABLE = False
    logger.warning("PyMediaInfo not available - video metadata extraction will be limited")


class EnhancedVideoExtractor:
    def __init__(self):
        self.cache = {}
        self.supported_formats = self._get_supported_formats()

    def _get_supported_formats(self) -> List[str]:
        """Get list of supported video formats"""
        if MEDIAINFO_AVAILABLE:
            # Professional video formats supported by MediaInfo
            return [
                'mp4', 'mov', 'avi', 'mkv', 'wmv', 'flv', 'webm', 'm4v',
                'mpg', 'mpeg', 'mpeg4', '3gp', 'asf', 'rm', 'rmvb', 'vob',
                'ts', 'mts', 'm2ts', 'mxf', 'dv', 'dvr-ms', 'wtv', 'ogv',
                'f4v', 'swf', 'qt', 'movie', 'mpe', 'm1v', 'm2v', 'mpv2',
                'mp2v', 'dat', 'prores', 'dnxhd', 'r3d', 'braw'
            ]
        else:
            # Basic formats when MediaInfo not available
            return ['mp4', 'mov', 'avi', 'mkv', 'wmv', 'flv', 'webm', 'm4v']

    def get_extraction_method(self) -> str:
        """Get the current extraction method being used"""
        if MEDIAINFO_AVAILABLE:
            return "PyMediaInfo (Professional)"
        else:
            return "Basic (Limited)"

    def get_mediainfo_version(self) -> Optional[str]:
        """Get MediaInfo library version"""
        if MEDIAINFO_AVAILABLE:
            try:
                # Try to get version from MediaInfo
                MediaInfo.parse("")  # Empty parse to check version
                return "Available"
            except Exception:
                return "Unknown"
        return None

    def get_supported_formats(self) -> List[str]:
        """Get list of supported video formats"""
        return self.supported_formats.copy()

    def extract_metadata(self, file_path: str) -> Dict[str, Any]:
        """Extract comprehensive metadata from video file"""
        file_path_obj = Path(file_path)

        # Check cache first
        cache_key = f"{file_path_obj}_{file_path_obj.stat().st_mtime}"
        if cache_key in self.cache:
            return self.cache[cache_key].copy()

        metadata = self._initialize_basic_metadata(file_path_obj)

        if MEDIAINFO_AVAILABLE:
            try:
                video_metadata = self._extract_with_mediainfo(str(file_path_obj))
                metadata.update(video_metadata)
                logger.debug(f"Extracted {len(metadata)} metadata fields with MediaInfo from {file_path_obj}")
            except Exception as e:
                logger.warning(f"MediaInfo extraction failed for {file_path_obj}: {e}")
                # Fallback to basic extraction
                metadata.update(self._extract_basic_metadata(file_path_obj))
        else:
            metadata.update(self._extract_basic_metadata(file_path_obj))

        # Cache the result
        self.cache[cache_key] = metadata.copy()
        return metadata

    def _initialize_basic_metadata(self, file_path: Path) -> Dict[str, Any]:
        """Initialize basic file metadata"""
        return {
            'file_path': str(file_path),
            'file_name': file_path.name,
            'file_size': file_path.stat().st_size if file_path.exists() else 0,
            'file_extension': file_path.suffix.lower(),
            'file_modified': datetime.fromtimestamp(file_path.stat().st_mtime) if file_path.exists() else None,
            'file_created': datetime.fromtimestamp(file_path.stat().st_ctime) if file_path.exists() else None,
        }

    def _extract_with_mediainfo(self, file_path: str) -> Dict[str, Any]:
        """Extract metadata using PyMediaInfo"""
        metadata = {}

        try:
            media_info = MediaInfo.parse(file_path)

            # Process video tracks
            for track in media_info.tracks:
                if track.track_type == 'Video':
                    metadata.update(self._process_video_track(track))
                elif track.track_type == 'Audio':
                    metadata.update(self._process_audio_track(track))
                elif track.track_type == 'General':
                    metadata.update(self._process_general_track(track))

        except Exception as e:
            logger.error(f"Error extracting metadata with MediaInfo: {e}")

        return metadata

    def _process_general_track(self, track) -> Dict[str, Any]:
        """Process general track information"""
        metadata = {}

        # Basic file information
        if hasattr(track, 'format'):
            metadata['container_format'] = track.format
        if hasattr(track, 'file_size'):
            metadata['file_size_mediainfo'] = track.file_size
        if hasattr(track, 'duration'):
            if track.duration:
                metadata['duration_ms'] = track.duration
                metadata['duration_seconds'] = track.duration / 1000.0
                metadata['duration_formatted'] = self._format_duration(track.duration)

        # Creation time
        if hasattr(track, 'encoded_date'):
            metadata['encoded_date'] = self._parse_mediainfo_datetime(track.encoded_date)
        if hasattr(track, 'tagged_date'):
            metadata['tagged_date'] = self._parse_mediainfo_datetime(track.tagged_date)
        if hasattr(track, 'file_last_modification_date'):
            metadata['modification_date'] = self._parse_mediainfo_datetime(track.file_last_modification_date)

        # Use the best available datetime as primary
        for date_field in ['encoded_date', 'tagged_date', 'modification_date']:
            if metadata.get(date_field):
                metadata['datetime_original'] = metadata[date_field]
                break

        # Metadata
        if hasattr(track, 'title'):
            metadata['title'] = track.title
        if hasattr(track, 'album'):
            metadata['album'] = track.album
        if hasattr(track, 'performer'):
            metadata['artist'] = track.performer
        if hasattr(track, 'copyright'):
            metadata['copyright'] = track.copyright
        if hasattr(track, 'comment'):
            metadata['comment'] = track.comment

        # Technical information
        if hasattr(track, 'overall_bit_rate'):
            metadata['overall_bitrate'] = track.overall_bit_rate
        if hasattr(track, 'writing_application'):
            metadata['software'] = track.writing_application
        if hasattr(track, 'writing_library'):
            metadata['encoding_library'] = track.writing_library

        return metadata

    def _process_video_track(self, track) -> Dict[str, Any]:
        """Process video track information"""
        metadata = {}

        # Resolution and format
        if hasattr(track, 'width'):
            metadata['video_width'] = track.width
        if hasattr(track, 'height'):
            metadata['video_height'] = track.height
        if hasattr(track, 'format'):
            metadata['video_codec'] = track.format
        if hasattr(track, 'format_profile'):
            metadata['video_profile'] = track.format_profile
        if hasattr(track, 'format_level'):
            metadata['video_level'] = track.format_level

        # Frame rate and timing
        if hasattr(track, 'frame_rate'):
            metadata['video_framerate'] = float(track.frame_rate) if track.frame_rate else None
        if hasattr(track, 'frame_count'):
            metadata['video_frame_count'] = track.frame_count

        # Quality and compression
        if hasattr(track, 'bit_rate'):
            metadata['video_bitrate'] = track.bit_rate
        if hasattr(track, 'bit_depth'):
            metadata['video_bit_depth'] = track.bit_depth
        if hasattr(track, 'color_space'):
            metadata['video_color_space'] = track.color_space
        if hasattr(track, 'chroma_subsampling'):
            metadata['video_chroma_subsampling'] = track.chroma_subsampling

        # Professional video information
        if hasattr(track, 'scan_type'):
            metadata['video_scan_type'] = track.scan_type  # Progressive/Interlaced
        if hasattr(track, 'display_aspect_ratio'):
            metadata['video_aspect_ratio'] = track.display_aspect_ratio
        if hasattr(track, 'pixel_aspect_ratio'):
            metadata['video_pixel_aspect_ratio'] = track.pixel_aspect_ratio

        # Camera and recording information
        if hasattr(track, 'encoded_library_name'):
            metadata['video_encoder'] = track.encoded_library_name
        if hasattr(track, 'encoded_library_version'):
            metadata['video_encoder_version'] = track.encoded_library_version

        return metadata

    def _process_audio_track(self, track) -> Dict[str, Any]:
        """Process audio track information"""
        metadata = {}

        # Audio format and quality
        if hasattr(track, 'format'):
            metadata['audio_codec'] = track.format
        if hasattr(track, 'format_profile'):
            metadata['audio_profile'] = track.format_profile
        if hasattr(track, 'bit_rate'):
            metadata['audio_bitrate'] = track.bit_rate
        if hasattr(track, 'sampling_rate'):
            metadata['audio_sample_rate'] = track.sampling_rate
        if hasattr(track, 'bit_depth'):
            metadata['audio_bit_depth'] = track.bit_depth
        if hasattr(track, 'channel_s'):
            metadata['audio_channels'] = track.channel_s

        # Audio language and metadata
        if hasattr(track, 'language'):
            metadata['audio_language'] = track.language
        if hasattr(track, 'title'):
            metadata['audio_title'] = track.title

        return metadata

    def _extract_basic_metadata(self, file_path: Path) -> Dict[str, Any]:
        """Extract basic metadata when MediaInfo is not available"""
        metadata = {}

        # Try to extract some basic information from file properties
        metadata.update({
            'duration_seconds': None,  # Cannot determine without MediaInfo
            'video_width': None,
            'video_height': None,
            'video_codec': None,
            'audio_codec': None,
            'container_format': file_path.suffix[1:].upper() if file_path.suffix else 'Unknown'
        })

        return metadata

    def _parse_mediainfo_datetime(self, date_str: str) -> Optional[datetime]:
        """Parse datetime from MediaInfo output"""
        if not date_str:
            return None

        try:
            # MediaInfo datetime formats
            datetime_formats = [
                '%Y-%m-%d %H:%M:%S',
                '%Y-%m-%d %H:%M:%S UTC',
                '%Y-%m-%dT%H:%M:%S',
                '%Y-%m-%dT%H:%M:%SZ',
                '%Y-%m-%d',
            ]

            # Clean the datetime string - ensure it's not None
            date_str = str(date_str).strip() if date_str is not None else ''
            if not date_str:
                return None

            for fmt in datetime_formats:
                try:
                    return datetime.strptime(date_str, fmt)
                except ValueError:
                    continue

            # Try to parse timezone-aware formats
            if 'UTC' in date_str:
                clean_dt = date_str.replace(' UTC', '')
                return datetime.strptime(clean_dt, '%Y-%m-%d %H:%M:%S')

        except Exception as e:
            logger.debug(f"Could not parse datetime: {date_str} - {e}")

        return None

    def _format_duration(self, duration_ms: int) -> str:
        """Format duration from milliseconds to human readable format"""
        try:
            total_seconds = int(duration_ms / 1000)
            hours = total_seconds // 3600
            minutes = (total_seconds % 3600) // 60
            seconds = total_seconds % 60

            if hours > 0:
                return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
            else:
                return f"{minutes:02d}:{seconds:02d}"
        except (ValueError, TypeError):
            return "Unknown"

    def get_capture_datetime(self, metadata: Dict[str, Any]) -> Optional[datetime]:
        """Get the best available capture datetime for video"""
        date_sources = [
            'datetime_original',
            'encoded_date',
            'tagged_date',
            'modification_date',
            'file_modified',
            'file_created'
        ]

        for source in date_sources:
            if source in metadata and metadata[source]:
                if isinstance(metadata[source], datetime):
                    return metadata[source]

        return None