"""
XMP Library Analyzer - Generate comprehensive reports from XMP sidecar files
"""

import json
import re
import xml.etree.ElementTree as ET
from collections import Counter
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from rich.console import Console
from rich.progress import Progress
from rich.table import Table


@dataclass
class PhotoMetadata:
    """Structured photo metadata from XMP"""

    file_path: str
    camera_make: str = ""
    camera_model: str = ""
    lens_model: str = ""
    focal_length: str = ""
    f_number: str = ""
    iso: str = ""
    exposure_time: str = ""
    datetime_original: str = ""
    gps_latitude: str = ""
    gps_longitude: str = ""
    location_city: str = ""
    location_country: str = ""
    software: str = ""
    artist: str = ""
    copyright: str = ""
    keywords: Optional[List[str]] = None
    rating: str = ""
    color_space: str = ""
    bit_depth: str = ""
    width: str = ""
    height: str = ""
    file_size: int = 0
    video_codec: str = ""
    video_framerate: str = ""
    video_duration: str = ""
    audio_codec: str = ""

    def __post_init__(self):
        if self.keywords is None:
            self.keywords = []


class XMPAnalyzer:
    """Analyzes photo libraries using XMP sidecar files"""

    def __init__(self, console: Optional[Console] = None):
        self.console = console or Console()
        self.photos: List[PhotoMetadata] = []
        self.total_files_processed = 0
        self.xmp_files_found = 0
        self.errors: List[Tuple[str, str]] = []

        # XMP namespace mappings
        self.namespaces = {
            "x": "adobe:ns:meta/",
            "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
            "dc": "http://purl.org/dc/elements/1.1/",
            "exif": "http://ns.adobe.com/exif/1.0/",
            "tiff": "http://ns.adobe.com/tiff/1.0/",
            "xmp": "http://ns.adobe.com/xap/1.0/",
            "aux": "http://ns.adobe.com/exif/1.0/aux/",
            "crs": "http://ns.adobe.com/camera-raw-settings/1.0/",
            "photoshop": "http://ns.adobe.com/photoshop/1.0/",
            "lr": "http://ns.adobe.com/lightroom/1.0/",
            "xmpMM": "http://ns.adobe.com/xap/1.0/mm/",
        }

    def analyze_library(self, root_directory: str, output_dir: Optional[str] = None) -> Dict[str, Any]:
        """
        Analyze a photo library by scanning XMP files

        Args:
            root_directory: Root directory to scan for XMP files
            output_dir: Optional directory to save detailed reports

        Returns:
            Comprehensive analysis results
        """
        root_path = Path(root_directory)
        if not root_path.exists():
            raise ValueError(f"Directory does not exist: {root_directory}")

        self.console.print(f"[bold cyan]📊 Analyzing photo library at: {root_directory}[/bold cyan]")

        # Scan for XMP files
        xmp_files = self._find_xmp_files(root_path)

        if not xmp_files:
            self.console.print("[yellow]⚠️  No XMP files found in the directory[/yellow]")
            return self._create_empty_report()

        self.console.print(f"[green]Found {len(xmp_files)} XMP files[/green]")

        # Process XMP files with progress bar
        with Progress() as progress:
            task = progress.add_task("[cyan]Processing XMP files...", total=len(xmp_files))

            for xmp_file in xmp_files:
                try:
                    metadata = self._parse_xmp_file(xmp_file)
                    if metadata:
                        self.photos.append(metadata)
                    self.total_files_processed += 1
                except Exception as e:
                    self.errors.append((str(xmp_file), str(e)))
                    # Debug: print errors to console for troubleshooting
                    if self.console:
                        self.console.print(f"[yellow]Error parsing {xmp_file.name}: {e}[/yellow]")

                progress.update(task, advance=1)

        self.xmp_files_found = len(xmp_files)

        # Generate comprehensive analysis
        analysis = self._generate_analysis()

        # Save detailed reports if output directory specified
        if output_dir:
            self._save_detailed_reports(analysis, output_dir)

        return analysis

    def _find_xmp_files(self, root_path: Path) -> List[Path]:
        """Find all XMP files in the directory tree"""
        xmp_files = []
        for path in root_path.rglob("*.xmp"):
            xmp_files.append(path)
        return sorted(xmp_files)

    def _parse_xmp_file(self, xmp_path: Path) -> Optional[PhotoMetadata]:
        """Parse an XMP file and extract metadata"""
        try:
            # Get associated media file info
            media_file = self._find_associated_media_file(xmp_path)
            file_size = media_file.stat().st_size if media_file and media_file.exists() else 0

            # Read and fix common XML issues in XMP content
            with open(xmp_path, encoding="utf-8") as f:
                content = f.read()

            # Fix unescaped ampersands (common in tool names)
            content = content.replace(" & ", " &amp; ")

            # Parse XMP content
            root = ET.fromstring(content)

            # Register namespaces
            for prefix, uri in self.namespaces.items():
                ET.register_namespace(prefix, uri)

            metadata = PhotoMetadata(
                file_path=str(media_file) if media_file else str(xmp_path),
                file_size=file_size,
            )

            # Extract metadata from XMP
            self._extract_camera_info(root, metadata)
            self._extract_lens_info(root, metadata)
            self._extract_exposure_info(root, metadata)
            self._extract_datetime_info(root, metadata)
            self._extract_gps_info(root, metadata)
            self._extract_location_info(root, metadata)
            self._extract_image_info(root, metadata)
            self._extract_video_info(root, metadata)
            self._extract_creator_info(root, metadata)
            self._extract_keywords(root, metadata)

            return metadata

        except Exception as e:
            raise Exception(f"Failed to parse XMP file: {e}") from e

    def _find_associated_media_file(self, xmp_path: Path) -> Optional[Path]:
        """Find the media file associated with an XMP sidecar"""
        base_name = xmp_path.stem
        parent_dir = xmp_path.parent

        # Common media file extensions
        media_extensions = [
            ".jpg",
            ".jpeg",
            ".tiff",
            ".tif",
            ".png",
            ".heic",
            ".heif",
            ".nef",
            ".cr2",
            ".cr3",
            ".arw",
            ".orf",
            ".dng",
            ".raf",
            ".rw2",
            ".mp4",
            ".mov",
            ".avi",
            ".mkv",
            ".webm",
            ".mxf",
            ".r3d",
            ".braw",
        ]

        for ext in media_extensions:
            media_file = parent_dir / f"{base_name}{ext}"
            if media_file.exists():
                return media_file

        return None

    def _extract_camera_info(self, root: ET.Element, metadata: PhotoMetadata):
        """Extract camera information"""
        # Try multiple XMP paths for camera info
        camera_paths = [".//tiff:Make", ".//exif:Make", ".//aux:Make"]

        model_paths = [".//tiff:Model", ".//exif:Model", ".//aux:Model"]

        for path in camera_paths:
            elem = root.find(path, self.namespaces)
            if elem is not None and elem.text:
                metadata.camera_make = elem.text.strip()
                break

        for path in model_paths:
            elem = root.find(path, self.namespaces)
            if elem is not None and elem.text:
                metadata.camera_model = elem.text.strip()
                break

    def _extract_lens_info(self, root: ET.Element, metadata: PhotoMetadata):
        """Extract lens information"""
        lens_paths = [
            ".//aux:LensModel",
            ".//exif:LensModel",
            ".//aux:Lens",
            ".//exif:LensInfo",
        ]

        for path in lens_paths:
            elem = root.find(path, self.namespaces)
            if elem is not None and elem.text:
                metadata.lens_model = elem.text.strip()
                break

    def _extract_exposure_info(self, root: ET.Element, metadata: PhotoMetadata):
        """Extract exposure settings"""
        # Focal length
        focal_elem = root.find(".//exif:FocalLength", self.namespaces)
        if focal_elem is not None and focal_elem.text:
            metadata.focal_length = focal_elem.text.strip()

        # F-number
        f_elem = root.find(".//exif:FNumber", self.namespaces)
        if f_elem is not None and f_elem.text:
            metadata.f_number = f_elem.text.strip()

        # ISO - try multiple field names
        iso_paths = [".//exif:ISOSpeedRatings", ".//exif:ISO", ".//aux:ISO"]
        for path in iso_paths:
            iso_elem = root.find(path, self.namespaces)
            if iso_elem is not None and iso_elem.text:
                metadata.iso = iso_elem.text.strip()
                break

        # Exposure time
        exposure_elem = root.find(".//exif:ExposureTime", self.namespaces)
        if exposure_elem is not None and exposure_elem.text:
            metadata.exposure_time = exposure_elem.text.strip()

    def _extract_datetime_info(self, root: ET.Element, metadata: PhotoMetadata):
        """Extract datetime information"""
        datetime_paths = [
            ".//exif:DateTimeOriginal",
            ".//xmp:CreateDate",
            ".//xmp:ModifyDate",
        ]

        for path in datetime_paths:
            elem = root.find(path, self.namespaces)
            if elem is not None and elem.text:
                metadata.datetime_original = elem.text.strip()
                break

    def _extract_gps_info(self, root: ET.Element, metadata: PhotoMetadata):
        """Extract GPS coordinates"""
        # Try multiple GPS field formats
        gps_lat_paths = [".//exif:GPSLatitude", ".//aux:GPSLatitude"]
        gps_lon_paths = [".//exif:GPSLongitude", ".//aux:GPSLongitude"]

        for path in gps_lat_paths:
            lat_elem = root.find(path, self.namespaces)
            if lat_elem is not None and lat_elem.text:
                metadata.gps_latitude = lat_elem.text.strip()
                break

        for path in gps_lon_paths:
            lon_elem = root.find(path, self.namespaces)
            if lon_elem is not None and lon_elem.text:
                metadata.gps_longitude = lon_elem.text.strip()
                break

    def _extract_location_info(self, root: ET.Element, metadata: PhotoMetadata):
        """Extract location information"""
        city_elem = root.find(".//photoshop:City", self.namespaces)
        if city_elem is not None and city_elem.text:
            metadata.location_city = city_elem.text.strip()

        country_elem = root.find(".//photoshop:Country", self.namespaces)
        if country_elem is not None and country_elem.text:
            metadata.location_country = country_elem.text.strip()

    def _extract_image_info(self, root: ET.Element, metadata: PhotoMetadata):
        """Extract image technical information"""
        width_elem = root.find(".//tiff:ImageWidth", self.namespaces)
        if width_elem is not None and width_elem.text:
            metadata.width = width_elem.text.strip()

        height_elem = root.find(".//tiff:ImageLength", self.namespaces)
        if height_elem is not None and height_elem.text:
            metadata.height = height_elem.text.strip()

        bits_elem = root.find(".//tiff:BitsPerSample", self.namespaces)
        if bits_elem is not None and bits_elem.text:
            metadata.bit_depth = bits_elem.text.strip()

        colorspace_elem = root.find(".//exif:ColorSpace", self.namespaces)
        if colorspace_elem is not None and colorspace_elem.text:
            metadata.color_space = colorspace_elem.text.strip()

    def _extract_video_info(self, root: ET.Element, metadata: PhotoMetadata):
        """Extract video-specific information"""
        codec_elem = root.find(".//aux:VideoCodec", self.namespaces)
        if codec_elem is not None and codec_elem.text:
            metadata.video_codec = codec_elem.text.strip()

        framerate_elem = root.find(".//aux:VideoFrameRate", self.namespaces)
        if framerate_elem is not None and framerate_elem.text:
            metadata.video_framerate = framerate_elem.text.strip()

        duration_elem = root.find(".//aux:Duration", self.namespaces)
        if duration_elem is not None and duration_elem.text:
            metadata.video_duration = duration_elem.text.strip()

        audio_elem = root.find(".//aux:AudioCodec", self.namespaces)
        if audio_elem is not None and audio_elem.text:
            metadata.audio_codec = audio_elem.text.strip()

    def _extract_creator_info(self, root: ET.Element, metadata: PhotoMetadata):
        """Extract creator and software information"""
        software_elem = root.find(".//tiff:Software", self.namespaces)
        if software_elem is not None and software_elem.text:
            metadata.software = software_elem.text.strip()

        # Try multiple paths for creator/artist
        creator_paths = [
            ".//dc:creator/rdf:Seq/rdf:li",
            ".//photoshop:AuthorsPosition",
            ".//tiff:Artist",
        ]

        for path in creator_paths:
            elem = root.find(path, self.namespaces)
            if elem is not None and elem.text:
                metadata.artist = elem.text.strip()
                break

        copyright_elem = root.find(".//dc:rights/rdf:Alt/rdf:li", self.namespaces)
        if copyright_elem is not None and copyright_elem.text:
            metadata.copyright = copyright_elem.text.strip()

    def _extract_keywords(self, root: ET.Element, metadata: PhotoMetadata):
        """Extract keywords/tags"""
        keywords_elem = root.find(".//dc:subject/rdf:Bag", self.namespaces)
        if keywords_elem is not None:
            keywords = []
            for li in keywords_elem.findall(".//rdf:li", self.namespaces):
                if li.text:
                    keywords.append(li.text.strip())
            metadata.keywords = keywords

    def _generate_analysis(self) -> Dict[str, Any]:
        """Generate comprehensive analysis from collected metadata"""
        if not self.photos:
            return self._create_empty_report()

        analysis = {
            "summary": self._analyze_summary(),
            "cameras": self._analyze_cameras(),
            "lenses": self._analyze_lenses(),
            "locations": self._analyze_locations(),
            "exposure_settings": self._analyze_exposure_settings(),
            "temporal_analysis": self._analyze_temporal_patterns(),
            "technical_specs": self._analyze_technical_specs(),
            "video_analysis": self._analyze_video_content(),
            "creator_analysis": self._analyze_creators(),
            "keywords_analysis": self._analyze_keywords(),
            "file_analysis": self._analyze_files(),
        }

        return analysis

    def _analyze_summary(self) -> Dict[str, Any]:
        """Generate summary statistics"""
        total_photos = len(self.photos)
        photos_with_gps = len([p for p in self.photos if p.gps_latitude and p.gps_longitude])
        photos_with_location = len([p for p in self.photos if p.location_city or p.location_country])
        video_files = len([p for p in self.photos if p.video_codec])

        return {
            "total_files": total_photos,
            "xmp_files_found": self.xmp_files_found,
            "files_processed": self.total_files_processed,
            "photos_with_gps": photos_with_gps,
            "photos_with_location_info": photos_with_location,
            "video_files": video_files,
            "image_files": total_photos - video_files,
            "errors_encountered": len(self.errors),
            "gps_coverage_percentage": ((photos_with_gps / total_photos * 100) if total_photos > 0 else 0),
            "location_coverage_percentage": ((photos_with_location / total_photos * 100) if total_photos > 0 else 0),
        }

    def _analyze_cameras(self) -> Dict[str, Any]:
        """Analyze camera usage patterns"""
        camera_counts = Counter()
        make_counts = Counter()
        model_counts = Counter()

        for photo in self.photos:
            make = photo.camera_make or "Unknown"
            model = photo.camera_model or "Unknown"

            make_counts[make] += 1
            model_counts[model] += 1

            if make != "Unknown" and model != "Unknown":
                full_name = f"{make} {model}"
                camera_counts[full_name] += 1

        return {
            "total_unique_cameras": len(camera_counts),
            "camera_distribution": dict(camera_counts.most_common()),
            "make_distribution": dict(make_counts.most_common()),
            "model_distribution": dict(model_counts.most_common()),
            "most_used_camera": (camera_counts.most_common(1)[0] if camera_counts else None),
            "most_used_make": make_counts.most_common(1)[0] if make_counts else None,
        }

    def _analyze_lenses(self) -> Dict[str, Any]:
        """Analyze lens usage patterns"""
        lens_counts = Counter()
        focal_length_counts = Counter()

        for photo in self.photos:
            if photo.lens_model:
                lens_counts[photo.lens_model] += 1

            if photo.focal_length:
                # Extract numeric focal length
                focal_match = re.search(r"(\d+(?:\.\d+)?)", photo.focal_length)
                if focal_match:
                    focal_mm = float(focal_match.group(1))
                    # Group into ranges
                    if focal_mm < 20:
                        focal_range = "Ultra-wide (< 20mm)"
                    elif focal_mm < 35:
                        focal_range = "Wide (20-35mm)"
                    elif focal_mm < 85:
                        focal_range = "Standard (35-85mm)"
                    elif focal_mm < 200:
                        focal_range = "Telephoto (85-200mm)"
                    else:
                        focal_range = "Super-telephoto (> 200mm)"

                    focal_length_counts[focal_range] += 1

        return {
            "total_unique_lenses": len(lens_counts),
            "lens_distribution": dict(lens_counts.most_common()),
            "focal_length_ranges": dict(focal_length_counts.most_common()),
            "most_used_lens": lens_counts.most_common(1)[0] if lens_counts else None,
        }

    def _analyze_locations(self) -> Dict[str, Any]:
        """Analyze location patterns"""
        city_counts = Counter()
        country_counts = Counter()
        gps_coordinates = []

        for photo in self.photos:
            if photo.location_city:
                city_counts[photo.location_city] += 1
            if photo.location_country:
                country_counts[photo.location_country] += 1
            if photo.gps_latitude and photo.gps_longitude:
                try:
                    lat = float(photo.gps_latitude)
                    lon = float(photo.gps_longitude)
                    gps_coordinates.append((lat, lon))
                except ValueError:
                    pass

        return {
            "total_unique_cities": len(city_counts),
            "total_unique_countries": len(country_counts),
            "city_distribution": dict(city_counts.most_common()),
            "country_distribution": dict(country_counts.most_common()),
            "gps_coordinates_available": len(gps_coordinates),
            "most_photographed_city": (city_counts.most_common(1)[0] if city_counts else None),
            "most_photographed_country": (country_counts.most_common(1)[0] if country_counts else None),
        }

    def _analyze_exposure_settings(self) -> Dict[str, Any]:
        """Analyze exposure settings patterns"""
        f_number_counts = Counter()
        iso_counts = Counter()
        exposure_counts = Counter()

        for photo in self.photos:
            if photo.f_number:
                f_number_counts[photo.f_number] += 1
            if photo.iso:
                iso_counts[photo.iso] += 1
            if photo.exposure_time:
                exposure_counts[photo.exposure_time] += 1

        return {
            "f_number_distribution": dict(f_number_counts.most_common()),
            "iso_distribution": dict(iso_counts.most_common()),
            "exposure_time_distribution": dict(exposure_counts.most_common()),
            "most_used_aperture": (f_number_counts.most_common(1)[0] if f_number_counts else None),
            "most_used_iso": iso_counts.most_common(1)[0] if iso_counts else None,
        }

    def _analyze_temporal_patterns(self) -> Dict[str, Any]:
        """Analyze temporal shooting patterns"""
        years = Counter()
        months = Counter()
        days_of_week = Counter()
        hours = Counter()

        for photo in self.photos:
            if photo.datetime_original:
                try:
                    # Parse various datetime formats
                    dt_str = photo.datetime_original
                    # Handle ISO format with timezone
                    if "T" in dt_str:
                        dt_str = (
                            dt_str.split("T")[0] + " " + dt_str.split("T")[1].split("+")[0].split("-")[0].split("Z")[0]
                        )

                    dt = datetime.fromisoformat(dt_str.replace("Z", ""))

                    years[dt.year] += 1
                    months[dt.strftime("%B")] += 1
                    days_of_week[dt.strftime("%A")] += 1
                    hours[dt.hour] += 1
                except Exception:
                    continue

        return {
            "year_distribution": dict(years.most_common()),
            "month_distribution": dict(months.most_common()),
            "day_of_week_distribution": dict(days_of_week.most_common()),
            "hour_distribution": dict(hours.most_common()),
            "most_active_year": years.most_common(1)[0] if years else None,
            "most_active_month": months.most_common(1)[0] if months else None,
            "most_active_day": days_of_week.most_common(1)[0] if days_of_week else None,
        }

    def _analyze_technical_specs(self) -> Dict[str, Any]:
        """Analyze technical specifications"""
        resolutions = Counter()
        bit_depths = Counter()
        color_spaces = Counter()
        file_sizes = []

        for photo in self.photos:
            if photo.width and photo.height:
                resolution = f"{photo.width}x{photo.height}"
                resolutions[resolution] += 1

            if photo.bit_depth:
                bit_depths[photo.bit_depth] += 1

            if photo.color_space:
                color_spaces[photo.color_space] += 1

            if photo.file_size > 0:
                file_sizes.append(photo.file_size)

        avg_file_size = sum(file_sizes) / len(file_sizes) if file_sizes else 0
        total_file_size = sum(file_sizes)

        return {
            "resolution_distribution": dict(resolutions.most_common()),
            "bit_depth_distribution": dict(bit_depths.most_common()),
            "color_space_distribution": dict(color_spaces.most_common()),
            "average_file_size_mb": avg_file_size / (1024 * 1024),
            "total_library_size_gb": total_file_size / (1024 * 1024 * 1024),
            "largest_file_size_mb": (max(file_sizes) / (1024 * 1024) if file_sizes else 0),
        }

    def _analyze_video_content(self) -> Dict[str, Any]:
        """Analyze video-specific content"""
        video_codecs = Counter()
        framerates = Counter()
        audio_codecs = Counter()
        durations = []

        for photo in self.photos:
            if photo.video_codec:
                video_codecs[photo.video_codec] += 1

            if photo.video_framerate:
                framerates[photo.video_framerate] += 1

            if photo.audio_codec:
                audio_codecs[photo.audio_codec] += 1

            if photo.video_duration:
                try:
                    duration = float(photo.video_duration)
                    durations.append(duration)
                except ValueError:
                    pass

        total_video_duration = sum(durations)

        return {
            "video_codec_distribution": dict(video_codecs.most_common()),
            "framerate_distribution": dict(framerates.most_common()),
            "audio_codec_distribution": dict(audio_codecs.most_common()),
            "total_video_duration_hours": total_video_duration / 3600,
            "average_video_length_seconds": (sum(durations) / len(durations) if durations else 0),
        }

    def _analyze_creators(self) -> Dict[str, Any]:
        """Analyze creator and software information"""
        software_counts = Counter()
        creator_counts = Counter()

        for photo in self.photos:
            if photo.software:
                software_counts[photo.software] += 1
            if photo.artist:
                creator_counts[photo.artist] += 1

        return {
            "software_distribution": dict(software_counts.most_common()),
            "creator_distribution": dict(creator_counts.most_common()),
            "most_used_software": (software_counts.most_common(1)[0] if software_counts else None),
        }

    def _analyze_keywords(self) -> Dict[str, Any]:
        """Analyze keywords and tags"""
        all_keywords = []
        for photo in self.photos:
            if photo.keywords:
                all_keywords.extend(photo.keywords)

        keyword_counts = Counter(all_keywords)

        return {
            "total_unique_keywords": len(keyword_counts),
            "total_keyword_instances": len(all_keywords),
            "keyword_distribution": dict(keyword_counts.most_common(50)),  # Top 50
            "most_used_keyword": (keyword_counts.most_common(1)[0] if keyword_counts else None),
        }

    def _analyze_files(self) -> Dict[str, Any]:
        """Analyze file organization patterns"""
        folder_counts = Counter()
        file_extensions = Counter()

        for photo in self.photos:
            folder = str(Path(photo.file_path).parent)
            folder_counts[folder] += 1

            extension = Path(photo.file_path).suffix.lower()
            if extension:
                file_extensions[extension] += 1

        return {
            "folder_distribution": dict(folder_counts.most_common(20)),  # Top 20 folders
            "file_extension_distribution": dict(file_extensions.most_common()),
            "most_populated_folder": (folder_counts.most_common(1)[0] if folder_counts else None),
        }

    def _create_empty_report(self) -> Dict[str, Any]:
        """Create an empty report structure"""
        return {
            "summary": {"total_files": 0, "xmp_files_found": 0},
            "cameras": {},
            "lenses": {},
            "locations": {},
            "exposure_settings": {},
            "temporal_analysis": {},
            "technical_specs": {},
            "video_analysis": {},
            "creator_analysis": {},
            "keywords_analysis": {},
            "file_analysis": {},
        }

    def _save_detailed_reports(self, analysis: Dict[str, Any], output_dir: str):
        """Save detailed analysis reports"""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        # Save JSON report
        json_path = output_path / "library_analysis.json"
        with open(json_path, "w") as f:
            json.dump(analysis, f, indent=2, default=str)

        # Save detailed CSV exports
        self._save_csv_reports(output_path)

        self.console.print(f"[green]📄 Detailed reports saved to: {output_path}[/green]")

    def _save_csv_reports(self, output_path: Path):
        """Save CSV reports for detailed analysis"""
        import csv

        # Photos metadata CSV
        csv_path = output_path / "photos_metadata.csv"
        with open(csv_path, "w", newline="", encoding="utf-8") as f:
            if self.photos:
                writer = csv.DictWriter(f, fieldnames=asdict(self.photos[0]).keys())
                writer.writeheader()
                for photo in self.photos:
                    row = asdict(photo)
                    row["keywords"] = "; ".join(row["keywords"]) if row["keywords"] else ""
                    writer.writerow(row)

    def display_analysis(self, analysis: Dict[str, Any]):
        """Display analysis results in a formatted way"""
        self._display_summary(analysis["summary"])
        self._display_cameras(analysis["cameras"])
        self._display_lenses(analysis["lenses"])
        self._display_locations(analysis["locations"])
        self._display_exposure_settings(analysis["exposure_settings"])
        self._display_temporal_analysis(analysis["temporal_analysis"])
        self._display_technical_specs(analysis["technical_specs"])

        if analysis["video_analysis"].get("video_codec_distribution"):
            self._display_video_analysis(analysis["video_analysis"])

    def _display_summary(self, summary: Dict[str, Any]):
        """Display summary statistics"""
        table = Table(title="📊 Library Summary", show_header=True, header_style="bold cyan")
        table.add_column("Metric", style="bold")
        table.add_column("Value", justify="right", style="green")

        table.add_row("Total Files", str(summary.get("total_files", 0)))
        table.add_row("XMP Files Found", str(summary.get("xmp_files_found", 0)))
        table.add_row("Image Files", str(summary.get("image_files", 0)))
        table.add_row("Video Files", str(summary.get("video_files", 0)))
        table.add_row("Files with GPS", str(summary.get("photos_with_gps", 0)))
        table.add_row("GPS Coverage", f"{summary.get('gps_coverage_percentage', 0):.1f}%")
        table.add_row(
            "Location Coverage",
            f"{summary.get('location_coverage_percentage', 0):.1f}%",
        )

        self.console.print(table)
        self.console.print()

    def _display_cameras(self, cameras: Dict[str, Any]):
        """Display camera statistics"""
        if not cameras.get("camera_distribution"):
            return

        table = Table(title="📸 Camera Usage", show_header=True, header_style="bold magenta")
        table.add_column("Camera", style="cyan")
        table.add_column("Photos", justify="right", style="green")
        table.add_column("Percentage", justify="right", style="yellow")

        total_photos = sum(cameras["camera_distribution"].values())

        for camera, count in list(cameras["camera_distribution"].items())[:10]:
            percentage = (count / total_photos * 100) if total_photos > 0 else 0
            table.add_row(camera, str(count), f"{percentage:.1f}%")

        self.console.print(table)
        self.console.print()

    def _display_lenses(self, lenses: Dict[str, Any]):
        """Display lens statistics"""
        if not lenses.get("lens_distribution"):
            return

        table = Table(title="🔍 Lens Usage", show_header=True, header_style="bold blue")
        table.add_column("Lens", style="cyan")
        table.add_column("Photos", justify="right", style="green")

        for lens, count in list(lenses["lens_distribution"].items())[:10]:
            table.add_row(lens, str(count))

        self.console.print(table)
        self.console.print()

        # Focal length ranges
        if lenses.get("focal_length_ranges"):
            focal_table = Table(
                title="📏 Focal Length Distribution",
                show_header=True,
                header_style="bold blue",
            )
            focal_table.add_column("Range", style="cyan")
            focal_table.add_column("Photos", justify="right", style="green")

            for range_name, count in lenses["focal_length_ranges"].items():
                focal_table.add_row(range_name, str(count))

            self.console.print(focal_table)
            self.console.print()

    def _display_locations(self, locations: Dict[str, Any]):
        """Display location statistics"""
        if locations.get("country_distribution"):
            table = Table(
                title="🗺️  Location Distribution",
                show_header=True,
                header_style="bold green",
            )
            table.add_column("Country", style="cyan")
            table.add_column("Photos", justify="right", style="green")

            for country, count in list(locations["country_distribution"].items())[:10]:
                table.add_row(country, str(count))

            self.console.print(table)
            self.console.print()

    def _display_exposure_settings(self, exposure: Dict[str, Any]):
        """Display exposure settings statistics"""
        if exposure.get("most_used_aperture"):
            table = Table(
                title="📷 Exposure Settings",
                show_header=True,
                header_style="bold yellow",
            )
            table.add_column("Setting", style="bold")
            table.add_column("Most Used Value", style="cyan")
            table.add_column("Count", justify="right", style="green")

            if exposure.get("most_used_aperture"):
                aperture, count = exposure["most_used_aperture"]
                table.add_row("Aperture", aperture, str(count))

            if exposure.get("most_used_iso"):
                iso, count = exposure["most_used_iso"]
                table.add_row("ISO", iso, str(count))

            self.console.print(table)
            self.console.print()

    def _display_temporal_analysis(self, temporal: Dict[str, Any]):
        """Display temporal analysis"""
        if temporal.get("most_active_year"):
            table = Table(
                title="📅 Temporal Patterns",
                show_header=True,
                header_style="bold purple",
            )
            table.add_column("Period", style="bold")
            table.add_column("Most Active", style="cyan")
            table.add_column("Count", justify="right", style="green")

            if temporal.get("most_active_year"):
                year, count = temporal["most_active_year"]
                table.add_row("Year", str(year), str(count))

            if temporal.get("most_active_month"):
                month, count = temporal["most_active_month"]
                table.add_row("Month", month, str(count))

            if temporal.get("most_active_day"):
                day, count = temporal["most_active_day"]
                table.add_row("Day of Week", day, str(count))

            self.console.print(table)
            self.console.print()

    def _display_technical_specs(self, technical: Dict[str, Any]):
        """Display technical specifications"""
        table = Table(
            title="⚙️  Technical Specifications",
            show_header=True,
            header_style="bold red",
        )
        table.add_column("Metric", style="bold")
        table.add_column("Value", style="cyan")

        table.add_row("Average File Size", f"{technical.get('average_file_size_mb', 0):.1f} MB")
        table.add_row("Total Library Size", f"{technical.get('total_library_size_gb', 0):.1f} GB")
        table.add_row("Largest File", f"{technical.get('largest_file_size_mb', 0):.1f} MB")

        self.console.print(table)
        self.console.print()

    def _display_video_analysis(self, video: Dict[str, Any]):
        """Display video analysis"""
        table = Table(title="🎬 Video Content", show_header=True, header_style="bold cyan")
        table.add_column("Metric", style="bold")
        table.add_column("Value", style="cyan")

        table.add_row(
            "Total Video Duration",
            f"{video.get('total_video_duration_hours', 0):.1f} hours",
        )
        table.add_row(
            "Average Video Length",
            f"{video.get('average_video_length_seconds', 0):.1f} seconds",
        )

        if video.get("video_codec_distribution"):
            codecs = list(video["video_codec_distribution"].keys())[:3]
            table.add_row("Common Codecs", ", ".join(codecs))

        self.console.print(table)
        self.console.print()
