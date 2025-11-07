import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional
from collections import defaultdict, Counter
import matplotlib.pyplot as plt
from rich.console import Console
from rich.table import Table
import numpy as np

logger = logging.getLogger(__name__)


class StatisticsGenerator:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.stats_config = config.get("statistics", {})
        self.console = Console()
        self.enable_charts = self.stats_config.get("enable_charts", True)
        self.chart_output_dir = self.stats_config.get("chart_output_dir", "charts")

    def generate_library_statistics(
        self, photos_metadata: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Generate comprehensive statistics for the photo library"""
        if not photos_metadata:
            return {"error": "No photos provided for analysis"}

        stats = {
            "total_photos": len(photos_metadata),
            "date_range": self._calculate_date_range(photos_metadata),
            "cameras": self._analyze_cameras(photos_metadata),
            "lenses": self._analyze_lenses(photos_metadata),
            "technical_settings": self._analyze_technical_settings(photos_metadata),
            "file_info": self._analyze_file_info(photos_metadata),
            "location_info": self._analyze_locations(photos_metadata),
            "shooting_patterns": self._analyze_shooting_patterns(photos_metadata),
            "quality_metrics": self._analyze_quality_metrics(photos_metadata),
        }

        return stats

    def _calculate_date_range(
        self, photos_metadata: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Calculate date range of photos"""
        dates = []
        for photo in photos_metadata:
            date = self._get_photo_date(photo)
            if date:
                dates.append(date)

        if not dates:
            return {"error": "No valid dates found"}

        dates.sort()
        span = dates[-1] - dates[0]

        return {
            "earliest": dates[0],
            "latest": dates[-1],
            "span_days": span.days,
            "span_years": round(span.days / 365.25, 1),
            "total_photos_with_dates": len(dates),
        }

    def _analyze_cameras(self, photos_metadata: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze camera usage statistics"""
        camera_counts = Counter()
        camera_models = Counter()
        camera_makes = Counter()

        for photo in photos_metadata:
            make = photo.get("camera_make", "Unknown")
            model = photo.get("camera_model", "Unknown")

            camera_makes[make] += 1
            camera_models[model] += 1

            if make != "Unknown" and model != "Unknown":
                full_name = f"{make} {model}"
                camera_counts[full_name] += 1

        return {
            "total_cameras": len(camera_counts),
            "most_used_camera": (
                camera_counts.most_common(1)[0] if camera_counts else None
            ),
            "camera_distribution": dict(camera_counts.most_common()),
            "make_distribution": dict(camera_makes.most_common()),
            "model_distribution": dict(camera_models.most_common()),
        }

    def _analyze_lenses(self, photos_metadata: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze lens usage statistics"""
        lens_counts = Counter()
        focal_lengths = []

        for photo in photos_metadata:
            lens = photo.get("lens_model")
            if lens and lens != "Unknown":
                lens_counts[lens] += 1

            focal_length = photo.get("focal_length")
            if focal_length and isinstance(focal_length, (int, float)):
                focal_lengths.append(focal_length)

        focal_length_stats = {}
        if focal_lengths:
            focal_length_stats = {
                "min": min(focal_lengths),
                "max": max(focal_lengths),
                "avg": round(np.mean(focal_lengths), 1),
                "median": round(np.median(focal_lengths), 1),
                "most_common": Counter([int(fl) for fl in focal_lengths]).most_common(
                    5
                ),
            }

        return {
            "total_lenses": len(lens_counts),
            "most_used_lens": lens_counts.most_common(1)[0] if lens_counts else None,
            "lens_distribution": dict(lens_counts.most_common()),
            "focal_length_stats": focal_length_stats,
        }

    def _analyze_technical_settings(
        self, photos_metadata: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Analyze camera technical settings"""
        iso_values = []
        aperture_values = []
        shutter_speeds = []

        for photo in photos_metadata:
            iso = photo.get("iso")
            if iso and isinstance(iso, (int, float)):
                iso_values.append(iso)

            f_number = photo.get("f_number")
            if f_number and isinstance(f_number, (int, float)):
                aperture_values.append(f_number)

            exposure = photo.get("exposure_time")
            if exposure and isinstance(exposure, (int, float)):
                shutter_speeds.append(exposure)

        stats = {}

        if iso_values:
            stats["iso"] = {
                "min": min(iso_values),
                "max": max(iso_values),
                "avg": round(np.mean(iso_values), 0),
                "median": round(np.median(iso_values), 0),
                "distribution": dict(Counter(iso_values).most_common(10)),
            }

        if aperture_values:
            stats["aperture"] = {
                "min": min(aperture_values),
                "max": max(aperture_values),
                "avg": round(np.mean(aperture_values), 1),
                "median": round(np.median(aperture_values), 1),
                "distribution": dict(
                    Counter([round(f, 1) for f in aperture_values]).most_common(10)
                ),
            }

        if shutter_speeds:
            stats["shutter_speed"] = {
                "fastest": min(shutter_speeds),
                "slowest": max(shutter_speeds),
                "avg": round(np.mean(shutter_speeds), 4),
                "median": round(np.median(shutter_speeds), 4),
            }

        return stats

    def _analyze_file_info(
        self, photos_metadata: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Analyze file information"""
        file_sizes = []
        extensions = Counter()
        dimensions = []

        for photo in photos_metadata:
            size = photo.get("file_size")
            if size and isinstance(size, (int, float)):
                file_sizes.append(size)

            ext = photo.get("file_extension", "").lower()
            if ext:
                extensions[ext] += 1

            width = photo.get("width")
            height = photo.get("height")
            if width and height:
                dimensions.append((width, height))

        stats = {}

        if file_sizes:
            total_size = sum(file_sizes)
            stats["file_sizes"] = {
                "total_mb": round(total_size / (1024 * 1024), 2),
                "total_gb": round(total_size / (1024 * 1024 * 1024), 2),
                "avg_mb": round(np.mean(file_sizes) / (1024 * 1024), 2),
                "median_mb": round(np.median(file_sizes) / (1024 * 1024), 2),
                "largest_mb": round(max(file_sizes) / (1024 * 1024), 2),
                "smallest_mb": round(min(file_sizes) / (1024 * 1024), 2),
            }

        stats["file_types"] = dict(extensions.most_common())

        if dimensions:
            stats["dimensions"] = {
                "most_common": Counter(dimensions).most_common(5),
                "unique_resolutions": len(set(dimensions)),
            }

        return stats

    def _analyze_locations(
        self, photos_metadata: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Analyze location information"""
        locations = Counter()
        countries = Counter()
        cities = Counter()
        gps_photos = 0

        for photo in photos_metadata:
            if photo.get("gps"):
                gps_photos += 1

            location = photo.get("location")
            if location:
                display_name = location.get("display_name")
                if display_name:
                    locations[display_name] += 1

                country = location.get("country")
                if country:
                    countries[country] += 1

                city = location.get("city")
                if city:
                    cities[city] += 1

        return {
            "photos_with_gps": gps_photos,
            "photos_with_location_names": len(locations),
            "unique_locations": len(locations),
            "unique_countries": len(countries),
            "unique_cities": len(cities),
            "most_photographed_locations": dict(locations.most_common(10)),
            "countries_visited": dict(countries.most_common()),
            "cities_visited": dict(cities.most_common(10)),
        }

    def _analyze_shooting_patterns(
        self, photos_metadata: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Analyze shooting patterns over time"""
        photos_by_month = defaultdict(int)
        photos_by_hour = defaultdict(int)
        photos_by_weekday = defaultdict(int)

        for photo in photos_metadata:
            date = self._get_photo_date(photo)
            if date:
                month_key = date.strftime("%Y-%m")
                photos_by_month[month_key] += 1
                photos_by_hour[date.hour] += 1
                photos_by_weekday[date.strftime("%A")] += 1

        return {
            "photos_by_month": dict(sorted(photos_by_month.items())),
            "photos_by_hour": dict(sorted(photos_by_hour.items())),
            "photos_by_weekday": dict(photos_by_weekday),
            "most_active_month": (
                max(photos_by_month.items(), key=lambda x: x[1])
                if photos_by_month
                else None
            ),
            "most_active_hour": (
                max(photos_by_hour.items(), key=lambda x: x[1])
                if photos_by_hour
                else None
            ),
            "most_active_weekday": (
                max(photos_by_weekday.items(), key=lambda x: x[1])
                if photos_by_weekday
                else None
            ),
        }

    def _analyze_quality_metrics(
        self, photos_metadata: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Analyze image quality metrics"""
        # This is a placeholder for quality analysis
        # In a real implementation, you might analyze:
        # - Blur detection scores
        # - Exposure quality
        # - Composition analysis
        # - etc.

        return {
            "note": "Quality metrics analysis not yet implemented",
            "available_metrics": [],
        }

    def _get_photo_date(self, photo: Dict[str, Any]) -> Optional[datetime]:
        """Extract photo date from metadata"""
        date_fields = [
            "datetime_original",
            "datetime_digitized",
            "datetime",
            "file_modified",
        ]

        for field in date_fields:
            if field in photo and photo[field]:
                if isinstance(photo[field], datetime):
                    return photo[field]
                elif isinstance(photo[field], str):
                    try:
                        return datetime.fromisoformat(photo[field])
                    except ValueError:
                        continue

        return None

    def display_statistics(self, stats: Dict[str, Any]) -> None:
        """Display statistics in a formatted console output"""
        self.console.print("\n[bold cyan]📊 LensLogic Library Statistics[/bold cyan]\n")

        # Overview
        overview_table = Table(
            title="Library Overview", show_header=True, header_style="bold magenta"
        )
        overview_table.add_column("Metric", style="cyan")
        overview_table.add_column("Value", justify="right", style="green")

        overview_table.add_row("Total Photos", str(stats["total_photos"]))

        if "date_range" in stats and "earliest" in stats["date_range"]:
            date_range = stats["date_range"]
            overview_table.add_row(
                "Date Range",
                f"{date_range['earliest'].strftime('%Y-%m-%d')} to {date_range['latest'].strftime('%Y-%m-%d')}",
            )
            overview_table.add_row(
                "Span",
                f"{date_range['span_years']} years ({date_range['span_days']} days)",
            )

        if "file_info" in stats and "file_sizes" in stats["file_info"]:
            file_info = stats["file_info"]["file_sizes"]
            overview_table.add_row("Total Size", f"{file_info['total_gb']:.2f} GB")
            overview_table.add_row("Average File Size", f"{file_info['avg_mb']:.2f} MB")

        self.console.print(overview_table)

        # Camera Statistics
        if "cameras" in stats:
            camera_stats = stats["cameras"]
            camera_table = Table(
                title="Camera Usage", show_header=True, header_style="bold magenta"
            )
            camera_table.add_column("Camera", style="cyan")
            camera_table.add_column("Photos", justify="right", style="green")
            camera_table.add_column("Percentage", justify="right", style="yellow")

            for camera, count in list(camera_stats["camera_distribution"].items())[:5]:
                percentage = (count / stats["total_photos"]) * 100
                camera_table.add_row(camera, str(count), f"{percentage:.1f}%")

            self.console.print(camera_table)

        # Technical Settings
        if "technical_settings" in stats:
            tech_stats = stats["technical_settings"]
            tech_table = Table(
                title="Technical Settings",
                show_header=True,
                header_style="bold magenta",
            )
            tech_table.add_column("Setting", style="cyan")
            tech_table.add_column("Min", justify="right", style="green")
            tech_table.add_column("Max", justify="right", style="green")
            tech_table.add_column("Average", justify="right", style="yellow")

            if "iso" in tech_stats:
                iso = tech_stats["iso"]
                tech_table.add_row(
                    "ISO",
                    str(int(iso["min"])),
                    str(int(iso["max"])),
                    str(int(iso["avg"])),
                )

            if "aperture" in tech_stats:
                aperture = tech_stats["aperture"]
                tech_table.add_row(
                    "Aperture",
                    f"f/{aperture['min']}",
                    f"f/{aperture['max']}",
                    f"f/{aperture['avg']}",
                )

            if "shutter_speed" in tech_stats:
                shutter = tech_stats["shutter_speed"]
                tech_table.add_row(
                    "Shutter Speed",
                    f"1/{int(1/shutter['fastest'])}",
                    f"{shutter['slowest']:.3f}s",
                    f"{shutter['avg']:.3f}s",
                )

            if len(tech_table.rows) > 0:
                self.console.print(tech_table)

        # Location Statistics
        if "location_info" in stats:
            location_stats = stats["location_info"]
            if location_stats["photos_with_gps"] > 0:
                location_table = Table(
                    title="Location Statistics",
                    show_header=True,
                    header_style="bold magenta",
                )
                location_table.add_column("Metric", style="cyan")
                location_table.add_column("Value", justify="right", style="green")

                location_table.add_row(
                    "Photos with GPS", str(location_stats["photos_with_gps"])
                )
                location_table.add_row(
                    "Unique Countries", str(location_stats["unique_countries"])
                )
                location_table.add_row(
                    "Unique Cities", str(location_stats["unique_cities"])
                )

                self.console.print(location_table)

    def generate_charts(
        self, stats: Dict[str, Any], output_dir: str = None
    ) -> List[str]:
        """Generate statistical charts"""
        if not self.enable_charts:
            return []

        if not output_dir:
            output_dir = self.chart_output_dir

        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        charts_created = []

        try:
            # Shooting patterns chart
            if "shooting_patterns" in stats:
                chart_path = self._create_shooting_patterns_chart(
                    stats["shooting_patterns"], output_path
                )
                if chart_path:
                    charts_created.append(chart_path)

            # Camera usage chart
            if "cameras" in stats:
                chart_path = self._create_camera_usage_chart(
                    stats["cameras"], output_path
                )
                if chart_path:
                    charts_created.append(chart_path)

            # Technical settings chart
            if "technical_settings" in stats:
                chart_path = self._create_technical_settings_chart(
                    stats["technical_settings"], output_path
                )
                if chart_path:
                    charts_created.append(chart_path)

        except Exception as e:
            logger.error(f"Error generating charts: {e}")

        return charts_created

    def _create_shooting_patterns_chart(
        self, patterns: Dict[str, Any], output_path: Path
    ) -> Optional[str]:
        """Create shooting patterns chart"""
        try:
            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))

            # Photos by hour
            if "photos_by_hour" in patterns:
                hours = list(patterns["photos_by_hour"].keys())
                counts = list(patterns["photos_by_hour"].values())

                ax1.bar(hours, counts, color="skyblue", alpha=0.7)
                ax1.set_title("Photos by Hour of Day")
                ax1.set_xlabel("Hour")
                ax1.set_ylabel("Number of Photos")
                ax1.set_xticks(range(0, 24, 2))

            # Photos by month
            if "photos_by_month" in patterns:
                months = list(patterns["photos_by_month"].keys())
                counts = list(patterns["photos_by_month"].values())

                ax2.plot(months, counts, marker="o", color="orange")
                ax2.set_title("Photos by Month")
                ax2.set_xlabel("Month")
                ax2.set_ylabel("Number of Photos")
                ax2.tick_params(axis="x", rotation=45)

            plt.tight_layout()
            chart_path = output_path / "shooting_patterns.png"
            plt.savefig(chart_path, dpi=300, bbox_inches="tight")
            plt.close()

            return str(chart_path)

        except Exception as e:
            logger.error(f"Error creating shooting patterns chart: {e}")
            return None

    def _create_camera_usage_chart(
        self, camera_stats: Dict[str, Any], output_path: Path
    ) -> Optional[str]:
        """Create camera usage pie chart"""
        try:
            if not camera_stats.get("camera_distribution"):
                return None

            cameras = list(camera_stats["camera_distribution"].keys())[:5]  # Top 5
            counts = list(camera_stats["camera_distribution"].values())[:5]

            plt.figure(figsize=(10, 8))
            plt.pie(counts, labels=cameras, autopct="%1.1f%%", startangle=90)
            plt.title("Camera Usage Distribution")
            plt.axis("equal")

            chart_path = output_path / "camera_usage.png"
            plt.savefig(chart_path, dpi=300, bbox_inches="tight")
            plt.close()

            return str(chart_path)

        except Exception as e:
            logger.error(f"Error creating camera usage chart: {e}")
            return None

    def _create_technical_settings_chart(
        self, tech_stats: Dict[str, Any], output_path: Path
    ) -> Optional[str]:
        """Create technical settings distribution chart"""
        try:
            fig, axes = plt.subplots(1, 3, figsize=(18, 6))

            # ISO distribution
            if "iso" in tech_stats and "distribution" in tech_stats["iso"]:
                iso_data = tech_stats["iso"]["distribution"]
                isos = list(iso_data.keys())[:10]
                counts = list(iso_data.values())[:10]

                axes[0].bar(range(len(isos)), counts, color="lightcoral")
                axes[0].set_title("ISO Distribution")
                axes[0].set_xlabel("ISO")
                axes[0].set_ylabel("Count")
                axes[0].set_xticks(range(len(isos)))
                axes[0].set_xticklabels(isos, rotation=45)

            # Aperture distribution
            if "aperture" in tech_stats and "distribution" in tech_stats["aperture"]:
                aperture_data = tech_stats["aperture"]["distribution"]
                apertures = list(aperture_data.keys())[:10]
                counts = list(aperture_data.values())[:10]

                axes[1].bar(range(len(apertures)), counts, color="lightgreen")
                axes[1].set_title("Aperture Distribution")
                axes[1].set_xlabel("f-stop")
                axes[1].set_ylabel("Count")
                axes[1].set_xticks(range(len(apertures)))
                axes[1].set_xticklabels([f"f/{a}" for a in apertures], rotation=45)

            # Placeholder for third chart
            axes[2].text(
                0.5, 0.5, "Additional\nMetrics", ha="center", va="center", fontsize=16
            )
            axes[2].set_title("Future Metrics")

            plt.tight_layout()
            chart_path = output_path / "technical_settings.png"
            plt.savefig(chart_path, dpi=300, bbox_inches="tight")
            plt.close()

            return str(chart_path)

        except Exception as e:
            logger.error(f"Error creating technical settings chart: {e}")
            return None
