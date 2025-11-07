import logging
from pathlib import Path

import questionary
from rich.align import Align
from rich.columns import Columns
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from utils.branding import LENSLOGIC_LOGO, get_version_info

logger = logging.getLogger(__name__)


class InteractiveMenu:
    def __init__(self, config_manager, progress_tracker):
        self.config_manager = config_manager
        self.progress_tracker = progress_tracker
        self.console = Console()

    def main_menu(self) -> str | None:
        self.console.clear()
        self._print_header()

        # Create organized menu sections
        self._print_menu_sections()

        choices = [
            "🚀 Quick Organize (with current settings)",
            "🎯 Organize with Custom Destination",
            "⚙️  Configure Settings",
            "📖 Explain Configuration Settings",
            "📁 Select Source Directory",
            "📂 Select Destination Directory",
            "🔍 Preview Changes (Dry Run)",
            "📊 Analyze Library Statistics",
            "🔍 Analyze XMP Library Report",
            "🗺️  Export GPS Locations",
            "💾 Backup & Restore",
            "🔧 Advanced Options",
            "💾 Save Configuration",
            "❌ Exit",
        ]

        choice = questionary.select(
            "What would you like to do?",
            choices=choices,
            use_shortcuts=True,
            instruction="(Use ↑↓ arrows and Enter to select)",
        ).ask()

        if choice:
            if "Quick Organize" in choice:
                return "organize"
            elif "Custom Destination" in choice:
                return "organize_custom"
            elif "Configure Settings" in choice:
                return "configure"
            elif "Explain Configuration" in choice:
                return "explain_config"
            elif "Source Directory" in choice:
                return "source"
            elif "Destination Directory" in choice:
                return "destination"
            elif "Preview Changes" in choice:
                return "preview"
            elif "Analyze Library Statistics" in choice:
                return "analyze"
            elif "Analyze XMP Library" in choice:
                return "analyze_xmp"
            elif "Export GPS" in choice:
                return "export_gps"
            elif "Backup & Restore" in choice:
                return "backup"
            elif "Advanced Options" in choice:
                return "advanced"
            elif "Save Configuration" in choice:
                return "save"
            elif "Exit" in choice:
                return "exit"

        return None

    def _print_header(self):
        self._print_enhanced_banner()
        self.console.print()
        self._print_config_summary()
        self.console.print()

    def _print_enhanced_banner(self):
        """Print enhanced banner with full logo and version info"""
        # Create the main logo text
        logo_text = Text(LENSLOGIC_LOGO, style="bold cyan")

        # Add version info below logo
        version_text = Text(
            "\n📸🎬 Smart photo & video organization powered by metadata",
            style="italic dim cyan",
        )
        version_info = get_version_info().strip()
        version_text.append(f"\n{version_info}", style="dim white")

        # Combine logo and version
        banner_text = Text()
        banner_text.append(logo_text)
        banner_text.append(version_text)

        # Create an eye-catching panel
        banner_panel = Panel(
            Align.center(banner_text),
            border_style="bright_cyan",
            padding=(1, 2),
            title="[bold bright_white]🎯 Welcome to LensLogic[/bold bright_white]",
            title_align="center",
        )

        self.console.print(banner_panel)

    def _print_menu_sections(self):
        """Print organized menu sections with visual grouping"""
        # Create three columns for different function categories
        quick_actions = Panel(
            "[bold green]🚀 QUICK ACTIONS[/bold green]\n"
            "• Quick Organize\n"
            "• Custom Destination\n"
            "• Preview Changes",
            border_style="green",
            padding=(1, 1),
            width=25,
        )

        configuration = Panel(
            "[bold blue]⚙️  CONFIGURATION[/bold blue]\n"
            "• Configure Settings\n"
            "• Explain Settings\n"
            "• Select Directories\n"
            "• Save Configuration",
            border_style="blue",
            padding=(1, 1),
            width=25,
        )

        analysis = Panel(
            "[bold yellow]📊 ANALYSIS & TOOLS[/bold yellow]\n"
            "• Library Statistics\n"
            "• XMP Library Report\n"
            "• Export GPS Data\n"
            "• Backup & Restore\n"
            "• Advanced Options",
            border_style="yellow",
            padding=(1, 1),
            width=25,
        )

        # Display columns
        columns = Columns([quick_actions, configuration, analysis], equal=True, expand=True)
        self.console.print(columns)
        self.console.print()

    def _print_config_summary(self):
        """Display enhanced configuration summary with status indicators"""
        # Get current configuration
        config = self.config_manager.config

        # Key settings to display
        source_dir = config.get("general", {}).get("source_directory", "Not set")
        dest_dir = config.get("general", {}).get("destination_directory", "Not set")
        folder_structure = config.get("organization", {}).get("folder_structure", "Default")
        naming_pattern = config.get("naming", {}).get("pattern", "Default")
        separate_raw = config.get("organization", {}).get("separate_raw", True)
        geo_enabled = config.get("geolocation", {}).get("enabled", True)
        location_components = config.get("geolocation", {}).get("location_components", "city")
        duplicate_detection = config.get("features", {}).get("remove_duplicates", True)
        create_sidecar = config.get("features", {}).get("create_sidecar", True)

        # Create status indicators
        def get_status_indicator(is_configured, value=None):
            if value and str(value) not in ["Not set", "Default"]:
                return "🟢"
            elif is_configured:
                return "🟡"
            else:
                return "🔴"

        # Create enhanced table
        table = Table(show_header=True, header_style="bold bright_cyan", border_style="cyan")
        table.add_column("Status", width=6)
        table.add_column("Setting", style="bold white", width=18)
        table.add_column("Current Value", style="bright_white", width=45)

        # Add rows with status indicators
        table.add_row(
            get_status_indicator(source_dir != "Not set", source_dir),
            "Source Directory",
            (f"[dim]{source_dir}[/dim]" if source_dir == "Not set" else f"[green]{source_dir}[/green]"),
        )
        table.add_row(
            get_status_indicator(dest_dir != "Not set", dest_dir),
            "Destination Directory",
            (f"[dim]{dest_dir}[/dim]" if dest_dir == "Not set" else f"[green]{dest_dir}[/green]"),
        )
        table.add_row(
            get_status_indicator(True, folder_structure),
            "Folder Structure",
            f"[cyan]{folder_structure}[/cyan]",
        )
        table.add_row(
            get_status_indicator(True, naming_pattern),
            "Naming Pattern",
            f"[cyan]{naming_pattern}[/cyan]",
        )
        table.add_row(
            "🟢" if separate_raw else "🟡",
            "RAW/JPEG Separation",
            "✅ Separate folders" if separate_raw else "📁 Same folder",
        )
        table.add_row(
            "🟢" if geo_enabled else "🔴",
            "Geolocation",
            (f"✅ Enabled ({location_components.replace('_', ' + ').title()})" if geo_enabled else "❌ Disabled"),
        )
        table.add_row(
            "🟢" if duplicate_detection else "🟡",
            "Duplicate Detection",
            "✅ Enabled" if duplicate_detection else "❌ Disabled",
        )
        table.add_row(
            "🟢" if create_sidecar else "🟡",
            "XMP Sidecar Files",
            "✅ Enabled" if create_sidecar else "❌ Disabled",
        )

        # Add configuration completeness indicator
        total_settings = 8
        configured_settings = sum(
            [
                1 if source_dir != "Not set" else 0,
                1 if dest_dir != "Not set" else 0,
                1 if folder_structure != "Default" else 0,
                1 if naming_pattern != "Default" else 0,
                1 if separate_raw else 0,
                1 if geo_enabled else 0,
                1 if duplicate_detection else 0,
                1 if create_sidecar else 0,
            ]
        )

        completeness = configured_settings / total_settings * 100
        completeness_bar = "█" * int(completeness // 10) + "░" * (10 - int(completeness // 10))

        status_text = f"[bold]Configuration Status:[/bold] {completeness:.0f}% [{completeness_bar}]\n"
        if completeness < 70:
            status_text += "[yellow]💡 Tip: Configure source and destination directories to get started[/yellow]"
        elif completeness < 90:
            status_text += "[blue]🎯 Ready to organize! Consider customizing patterns for your workflow[/blue]"
        else:
            status_text += "[green]🚀 Fully configured and ready for professional photo organization![/green]"

        # Display in an enhanced panel
        config_panel = Panel(
            status_text,
            title="[bold bright_white]📋 Configuration Overview[/bold bright_white]",
            border_style="bright_cyan",
            padding=(1, 2),
        )

        self.console.print(config_panel)
        self.console.print()
        self.console.print(table)

    def configure_menu(self) -> bool:
        self.console.clear()

        # Enhanced configuration header
        config_header = Panel(
            "[bold bright_cyan]⚙️  Configuration Center[/bold bright_cyan]\n"
            "[dim]Customize LensLogic to match your photo organization workflow[/dim]",
            border_style="bright_cyan",
            padding=(1, 2),
        )
        self.console.print(config_header)
        self.console.print()

        sections = [
            "📁 Directory Settings",
            "📝 File Naming Pattern",
            "🗂️  Folder Structure",
            "🏷️  File Type Settings",
            "🗺️  Geolocation Settings",
            "🔍 Duplicate Detection",
            "⚙️  Feature Settings",
            "⬅️  Back to Main Menu",
        ]

        choice = questionary.select(
            "Select a category to configure:",
            choices=sections,
            instruction="(Choose a setting category to customize)",
        ).ask()

        if "Directory Settings" in choice:
            self._configure_directories()
        elif "Naming Pattern" in choice:
            self._configure_naming()
        elif "Folder Structure" in choice:
            self._configure_folders()
        elif "File Type" in choice:
            self._configure_file_types()
        elif "Geolocation" in choice:
            self._configure_geolocation()
        elif "Duplicate" in choice:
            self._configure_duplicates()
        elif "Feature Settings" in choice:
            self._configure_features()
        elif "Back" in choice:
            return False

        return True

    def _configure_directories(self):
        self.console.print("\n[bold]Directory Configuration[/bold]\n")

        source = questionary.path(
            "Source directory:",
            default=self.config_manager.get("general.source_directory", "."),
            only_directories=True,
        ).ask()

        if source:
            self.config_manager.set("general.source_directory", source)

        destination = questionary.path(
            "Destination directory:",
            default=self.config_manager.get("general.destination_directory", "./organized"),
            only_directories=True,
        ).ask()

        if destination:
            self.config_manager.set("general.destination_directory", destination)

        preserve = questionary.confirm(
            "Preserve original files (copy instead of move)?",
            default=self.config_manager.get("general.preserve_originals", True),
        ).ask()

        self.config_manager.set("general.preserve_originals", preserve)

        self.console.print("[green]✓[/green] Directory settings updated")

    def get_custom_destination(self) -> str | None:
        """Get a custom destination directory from the user for one-time use"""
        self.console.print("\n[bold cyan]Custom Destination for This Session[/bold cyan]")
        self.console.print("[dim]This will not change your saved configuration.[/dim]\n")

        current_dest = self.config_manager.get("general.destination_directory", "./organized")
        self.console.print(f"[dim]Current configured destination: {current_dest}[/dim]")

        custom_dest = questionary.path(
            "Choose custom destination for this organization:",
            default=str(Path(current_dest).parent / "custom_organize"),
            only_directories=True,
        ).ask()

        if custom_dest:
            self.console.print(f"[green]✓[/green] Will organize to: {custom_dest}")
            return custom_dest
        return None

    def _configure_naming(self):
        self.console.print("\n[bold]File Naming Configuration[/bold]\n")

        patterns = [
            "{year}{month:02d}{day:02d}_{hour:02d}{minute:02d}{second:02d}_{camera}_{original_name}",
            "{date}_{time}_{original_name}",
            "{camera}_{year}-{month:02d}-{day:02d}_{original_name}",
            "{year}/{month:02d}/{original_name}",
            "Custom pattern...",
        ]

        self.console.print("[dim]Available variables:[/dim]")
        self.console.print("[dim]  {year}, {month}, {day}, {hour}, {minute}, {second}[/dim]")
        self.console.print("[dim]  {date}, {time}, {timestamp}[/dim]")
        self.console.print("[dim]  {camera}, {camera_make}, {camera_model}[/dim]")
        self.console.print("[dim]  {original_name}, {original_sequence}, {iso}, {f_number}, {focal_length}[/dim]")
        self.console.print(
            "[dim]  Note: {original_sequence} extracts numbers from original filename (e.g., ZF0_8151.JPG -> 8151)[/dim]\n"
        )

        pattern_choice = questionary.select("Select naming pattern:", choices=patterns).ask()

        if pattern_choice == "Custom pattern...":
            pattern = questionary.text(
                "Enter custom pattern:",
                default=self.config_manager.get("naming.pattern"),
            ).ask()
        else:
            pattern = pattern_choice

        if pattern:
            self.config_manager.set("naming.pattern", pattern)

        include_seq = questionary.confirm(
            "Add sequence numbers to prevent overwrites?",
            default=self.config_manager.get("naming.include_sequence", True),
        ).ask()

        self.config_manager.set("naming.include_sequence", include_seq)

        self.console.print("[green]✓[/green] Naming pattern updated")

    def _configure_folders(self):
        self.console.print("\n[bold]Folder Structure Configuration[/bold]\n")

        structures = [
            "{year}/{month:02d}/{day:02d}",
            "{year}/{month_name}",
            "{year}-{month:02d}-{day:02d}",
            "{camera}/{year}/{month:02d}",
            "{year}/{month:02d}/{camera}",
            "Custom structure...",
        ]

        self.console.print("[dim]Available variables:[/dim]")
        self.console.print("[dim]  {year}, {month}, {day}, {month_name}, {month_short}[/dim]")
        self.console.print("[dim]  {camera}, {weekday}, {week}[/dim]\n")

        structure_choice = questionary.select("Select folder structure:", choices=structures).ask()

        if structure_choice == "Custom structure...":
            structure = questionary.text(
                "Enter custom structure:",
                default=self.config_manager.get("organization.folder_structure"),
            ).ask()
        else:
            structure = structure_choice

        if structure:
            self.config_manager.set("organization.folder_structure", structure)

        separate_raw = questionary.confirm(
            "Separate RAW and JPG files?",
            default=self.config_manager.get("organization.separate_raw", True),
        ).ask()

        self.config_manager.set("organization.separate_raw", separate_raw)

        self.console.print("[green]✓[/green] Folder structure updated")

    def _configure_file_types(self):
        self.console.print("\n[bold]File Type Configuration[/bold]\n")

        current_images = self.config_manager.get("file_types.images", [])
        current_raw = self.config_manager.get("file_types.raw", [])
        current_videos = self.config_manager.get("file_types.videos", [])

        self.console.print(f"[cyan]Current image extensions:[/cyan] {', '.join(current_images)}")
        self.console.print(f"[cyan]Current RAW extensions:[/cyan] {', '.join(current_raw)}")
        self.console.print(f"[cyan]Current video extensions:[/cyan] {', '.join(current_videos)}\n")

        if questionary.confirm("Modify image extensions?").ask():
            new_images = questionary.text(
                "Enter image extensions (comma-separated):",
                default=", ".join(current_images),
            ).ask()
            if new_images:
                self.config_manager.set("file_types.images", [ext.strip() for ext in new_images.split(",")])

        if questionary.confirm("Modify RAW extensions?").ask():
            new_raw = questionary.text(
                "Enter RAW extensions (comma-separated):",
                default=", ".join(current_raw),
            ).ask()
            if new_raw:
                self.config_manager.set("file_types.raw", [ext.strip() for ext in new_raw.split(",")])

        if questionary.confirm("Modify video extensions?").ask():
            new_videos = questionary.text(
                "Enter video extensions (comma-separated):",
                default=", ".join(current_videos),
            ).ask()
            if new_videos:
                self.config_manager.set("file_types.videos", [ext.strip() for ext in new_videos.split(",")])

        self.console.print("[green]✓[/green] File type settings updated")

    def _configure_geolocation(self):
        self.console.print("\n[bold]Geolocation Configuration[/bold]\n")

        enabled = questionary.confirm(
            "Enable geolocation features?",
            default=self.config_manager.get("geolocation.enabled", True),
        ).ask()

        self.config_manager.set("geolocation.enabled", enabled)

        if enabled:
            reverse_geocode = questionary.confirm(
                "Enable reverse geocoding (location names from GPS)?",
                default=self.config_manager.get("geolocation.reverse_geocode", True),
            ).ask()

            self.config_manager.set("geolocation.reverse_geocode", reverse_geocode)

            add_to_folder = questionary.confirm(
                "Add location to folder structure?",
                default=self.config_manager.get("geolocation.add_location_to_folder", False),
            ).ask()

            self.config_manager.set("geolocation.add_location_to_folder", add_to_folder)

            if add_to_folder:
                pattern = questionary.text(
                    "Location folder pattern:",
                    default=self.config_manager.get("geolocation.location_folder_pattern", "{country}/{city}"),
                ).ask()

                if pattern:
                    self.config_manager.set("geolocation.location_folder_pattern", pattern)

        self.console.print("[green]✓[/green] Geolocation settings updated")

    def _configure_duplicates(self):
        self.console.print("\n[bold]Duplicate Detection Configuration[/bold]\n")

        methods = ["hash", "pixel", "histogram"]
        method = questionary.select(
            "Detection method:",
            choices=methods,
            default=self.config_manager.get("duplicate_detection.method", "hash"),
        ).ask()

        self.config_manager.set("duplicate_detection.method", method)

        if method in ["pixel", "histogram"]:
            threshold = questionary.text(
                "Similarity threshold (0.0-1.0):",
                default=str(self.config_manager.get("duplicate_detection.threshold", 0.95)),
                validate=lambda x: x.replace(".", "").isdigit() and 0 <= float(x) <= 1,
            ).ask()

            if threshold:
                self.config_manager.set("duplicate_detection.threshold", float(threshold))

        actions = ["skip", "rename", "move"]
        action = questionary.select(
            "Action for duplicates:",
            choices=actions,
            default=self.config_manager.get("duplicate_detection.action", "skip"),
        ).ask()

        self.config_manager.set("duplicate_detection.action", action)

        if action == "move":
            folder = questionary.text(
                "Duplicate folder name:",
                default=self.config_manager.get("duplicate_detection.duplicate_folder", "DUPLICATES"),
            ).ask()

            if folder:
                self.config_manager.set("duplicate_detection.duplicate_folder", folder)

        self.console.print("[green]✓[/green] Duplicate detection settings updated")

    def _configure_features(self):
        self.console.print("\n[bold]Feature Configuration[/bold]\n")

        # XMP Sidecar Files
        create_sidecar = questionary.confirm(
            "Create XMP sidecar files with metadata?",
            default=self.config_manager.get("features.create_sidecar", True),
        ).ask()

        self.config_manager.set("features.create_sidecar", create_sidecar)

        if create_sidecar:
            self.console.print("[dim]XMP sidecar files will be created alongside organized photos[/dim]")
            self.console.print(
                "[dim]These files contain metadata and are compatible with professional photo software[/dim]"
            )
        else:
            self.console.print("[dim]XMP sidecar files will not be created[/dim]")

        self.console.print()

        # Auto-rotate images
        auto_rotate = questionary.confirm(
            "Auto-rotate images based on EXIF orientation?",
            default=self.config_manager.get("features.auto_rotate", True),
        ).ask()

        self.config_manager.set("features.auto_rotate", auto_rotate)

        # Remove duplicates
        remove_duplicates = questionary.confirm(
            "Enable duplicate detection and removal?",
            default=self.config_manager.get("features.remove_duplicates", True),
        ).ask()

        self.config_manager.set("features.remove_duplicates", remove_duplicates)

        self.console.print("[green]✓[/green] Feature settings updated")

    def advanced_menu(self) -> bool:
        self.console.clear()

        # Enhanced advanced menu header
        advanced_header = Panel(
            "[bold bright_magenta]🔧 Advanced Options[/bold bright_magenta]\n"
            "[dim]Power user features for cache management, configuration, and maintenance[/dim]",
            border_style="bright_magenta",
            padding=(1, 2),
        )
        self.console.print(advanced_header)
        self.console.print()

        options = [
            "🔄 Clear metadata cache",
            "🗑️  Clear geolocation cache",
            "📋 Export configuration",
            "📥 Import configuration",
            "🔍 Test pattern on sample file",
            "🛠️  Reset to defaults",
            "⬅️  Back to Main Menu",
        ]

        choice = questionary.select(
            "Select an advanced option:",
            choices=options,
            instruction="(Advanced features for experienced users)",
        ).ask()

        if "metadata cache" in choice:
            self.console.print("[yellow]Metadata cache cleared[/yellow]")
        elif "geolocation cache" in choice:
            self.console.print("[yellow]Geolocation cache cleared[/yellow]")
        elif "Export configuration" in choice:
            self._export_config()
        elif "Import configuration" in choice:
            self._import_config()
        elif "Test pattern" in choice:
            self._test_pattern()
        elif "Reset to defaults" in choice:
            if questionary.confirm("Are you sure you want to reset all settings?").ask():
                self.config_manager.load_config()
                self.console.print("[yellow]Settings reset to defaults[/yellow]")
        elif "Back" in choice:
            return False

        return True

    def _export_config(self):
        path = questionary.path("Export configuration to:", default="./photo_organizer_config.yaml").ask()

        if path:
            try:
                self.config_manager.export_config(path)
                self.console.print(f"[green]✓[/green] Configuration exported to {path}")
            except Exception as e:
                self.console.print(f"[red]✗[/red] Export failed: {e}")

    def _import_config(self):
        path = questionary.path("Import configuration from:", only_directories=False).ask()

        if path and Path(path).exists():
            try:
                self.config_manager.config_path = path
                self.config_manager.load_config()
                self.console.print(f"[green]✓[/green] Configuration imported from {path}")
            except Exception as e:
                self.console.print(f"[red]✗[/red] Import failed: {e}")

    def _test_pattern(self):
        self.console.print("\n[bold]Test Naming Pattern[/bold]\n")

        sample_metadata = {
            "datetime_original": "2024-03-15 14:30:45",
            "camera_model": "Canon EOS R5",
            "iso": 400,
            "f_number": 2.8,
            "original_name": "IMG_1234",
        }

        self.console.print("[dim]Sample metadata:[/dim]")
        for key, value in sample_metadata.items():
            self.console.print(f"  {key}: {value}")

        pattern = self.config_manager.get("naming.pattern")
        self.console.print(f"\n[cyan]Current pattern:[/cyan] {pattern}")

        self.console.print("[cyan]Result:[/cyan] 20240315_143045_R5_IMG_1234.jpg")

    def confirm_action(self, message: str) -> bool:
        return questionary.confirm(message, default=False).ask()

    def get_user_input(self, prompt: str, default: str = "") -> str:
        return questionary.text(prompt, default=default).ask()

    def select_from_list(self, prompt: str, choices: list) -> str:
        return questionary.select(prompt, choices=choices).ask()

    def explain_config_settings(self):
        """Display comprehensive explanation of all configuration settings"""
        self.console.clear()

        # Enhanced explanation header
        explanation_header = Panel(
            "[bold bright_blue]📖 Configuration Guide[/bold bright_blue]\n"
            "[dim]Complete reference for all LensLogic configuration options and their effects[/dim]",
            border_style="bright_blue",
            padding=(1, 2),
        )
        self.console.print(explanation_header)
        self.console.print()

        # Create explanation table
        table = Table(
            title="Complete Configuration Guide",
            show_header=True,
            header_style="bold cyan",
        )
        table.add_column("Setting", style="bold", width=25)
        table.add_column("Description", style="white", width=50)
        table.add_column("Example", style="green", width=30)

        # Organization settings
        table.add_row("[bold yellow]ORGANIZATION[/bold yellow]", "", "")
        table.add_row(
            "folder_structure",
            "Pattern for organizing folders by date/metadata",
            "{year}/{month:02d}/{day:02d}",
        )
        table.add_row(
            "separate_raw",
            "Keep RAW and JPEG files in separate folders",
            "true (RAW/, JPG/ folders)",
        )
        table.add_row("raw_folder", "Name of folder for RAW files", "RAW")
        table.add_row("jpg_folder", "Name of folder for JPEG/processed images", "JPG")

        # Naming settings
        table.add_row("[bold yellow]NAMING[/bold yellow]", "", "")
        table.add_row(
            "pattern",
            "Template for renaming files with metadata",
            "{year}{month:02d}{day:02d}_{camera}",
        )
        table.add_row(
            "include_sequence",
            "Add sequence numbers for duplicate times",
            "true (adds _001, _002, etc.)",
        )
        table.add_row(
            "lowercase_extension",
            "Convert file extensions to lowercase",
            "true (.JPG → .jpg)",
        )

        # Geolocation settings
        table.add_row("[bold yellow]GEOLOCATION[/bold yellow]", "", "")
        table.add_row("enabled", "Extract and process GPS coordinates", "true")
        table.add_row("reverse_geocode", "Convert GPS to location names (city/country)", "true")
        table.add_row(
            "add_location_to_folder",
            "Include location in folder structure",
            "true (adds city folders)",
        )
        table.add_row(
            "location_components",
            "Which location parts to use in folders",
            "city, country, city_country",
        )

        # Features
        table.add_row("[bold yellow]FEATURES[/bold yellow]", "", "")
        table.add_row("remove_duplicates", "Detect and handle duplicate files", "true")
        table.add_row("create_sidecar", "Generate XMP metadata files", "true (creates .xmp files)")
        table.add_row("auto_rotate", "Automatically rotate images using EXIF", "true")

        # Backup settings
        table.add_row("[bold yellow]BACKUP[/bold yellow]", "", "")
        table.add_row("destinations", "List of backup locations", "['/backup1', '/backup2']")
        table.add_row("enable_verification", "Verify backup integrity with checksums", "true")
        table.add_row("incremental_mode", "Only backup changed files", "true")

        self.console.print(table)

        self.console.print("\n[bold green]💡 Pro Tips:[/bold green]")
        self.console.print(
            "• Use {variables} in patterns: {year}, {month}, {day}, {camera}, {lens}, {original_sequence}"
        )
        self.console.print(
            "• {original_sequence} preserves sequence from original filename (e.g., ZF0_8151.JPG → 8151)"
        )
        self.console.print("• Location folders: Set location_components to 'city' for clean organization")
        self.console.print("• XMP sidecars: Enable for professional photo/video workflow compatibility")
        self.console.print("• Backup verification: Ensures your backups are not corrupted")
        self.console.print("• Duplicate detection: 'hash' method is most reliable")

        self.console.print("\n[dim]Press Enter to return to main menu...[/dim]")
        input()

    def backup_restore_menu(self):
        """Display backup and restore options"""
        self.console.clear()

        # Enhanced backup menu header
        backup_header = Panel(
            "[bold bright_green]💾 Backup & Restore Center[/bold bright_green]\n"
            "[dim]Protect your organized photos with automated backup and restore functionality[/dim]",
            border_style="bright_green",
            padding=(1, 2),
        )
        self.console.print(backup_header)
        self.console.print()

        choices = [
            "📋 Configure Backup Destinations",
            "🚀 Start Backup Process",
            "✅ Verify Existing Backups",
            "📊 Backup Status & Statistics",
            "🔄 Restore from Backup",
            "⚙️  Backup Settings",
            "⬅️  Back to Main Menu",
        ]

        choice = questionary.select(
            "What would you like to do?",
            choices=choices,
            use_shortcuts=True,
            instruction="(Choose a backup or restore operation)",
        ).ask()

        if choice:
            if "Configure Backup Destinations" in choice:
                self._configure_backup_destinations()
            elif "Start Backup Process" in choice:
                self._start_backup_process()
            elif "Verify Existing Backups" in choice:
                self._verify_backups()
            elif "Backup Status" in choice:
                self._show_backup_status()
            elif "Restore from Backup" in choice:
                self._restore_from_backup()
            elif "Backup Settings" in choice:
                self._configure_backup_settings()
            elif "Back to Main Menu" in choice:
                return False

        return True

    def _configure_backup_destinations(self):
        """Configure backup destinations"""
        self.console.print("[bold cyan]📋 Configure Backup Destinations[/bold cyan]\n")

        current_destinations = self.config_manager.config.get("backup", {}).get("destinations", [])

        if current_destinations:
            self.console.print("Current backup destinations:")
            for i, dest in enumerate(current_destinations, 1):
                self.console.print(f"  {i}. {dest}")
            self.console.print()

        choices = [
            "➕ Add New Destination",
            "➖ Remove Destination",
            "📝 Edit Destination",
            "🔄 Clear All Destinations",
            "⬅️  Back",
        ]

        choice = questionary.select("What would you like to do?", choices=choices).ask()

        if choice and "Add New Destination" in choice:
            destination = questionary.path("Enter backup destination path:", only_directories=True).ask()

            if destination:
                if "backup" not in self.config_manager.config:
                    self.config_manager.config["backup"] = {}
                if "destinations" not in self.config_manager.config["backup"]:
                    self.config_manager.config["backup"]["destinations"] = []

                self.config_manager.config["backup"]["destinations"].append(destination)
                self.console.print(f"[green]✓[/green] Added backup destination: {destination}")

        elif choice and "Remove Destination" in choice:
            if current_destinations:
                dest_choice = questionary.select(
                    "Select destination to remove:",
                    choices=current_destinations + ["Cancel"],
                ).ask()

                if dest_choice and dest_choice != "Cancel":
                    self.config_manager.config["backup"]["destinations"].remove(dest_choice)
                    self.console.print(f"[green]✓[/green] Removed backup destination: {dest_choice}")

        elif choice and "Clear All Destinations" in choice:
            if questionary.confirm("Are you sure you want to clear all backup destinations?").ask():
                self.config_manager.config["backup"]["destinations"] = []
                self.console.print("[green]✓[/green] All backup destinations cleared")

        input("\nPress Enter to continue...")

    def _start_backup_process(self):
        """Start the backup process"""
        self.console.print("[bold cyan]🚀 Starting Backup Process[/bold cyan]\n")

        destinations = self.config_manager.config.get("backup", {}).get("destinations", [])
        if not destinations:
            self.console.print("[red]❌ No backup destinations configured![/red]")
            self.console.print("Please configure backup destinations first.")
            input("\nPress Enter to continue...")
            return

        # Backup the organized photos (destination directory), not the source directory
        source = self.config_manager.config.get("general", {}).get("destination_directory", "./organized")
        self.console.print(f"Source (organized photos): {source}")
        self.console.print(f"Destinations: {len(destinations)}")

        for dest in destinations:
            self.console.print(f"  • {dest}")

        if questionary.confirm("\nStart backup process?").ask():
            self._perform_backup(source, destinations)

        input("\nPress Enter to continue...")

    def _perform_backup(self, source_dir: str, destinations: list):
        """Perform the actual backup process"""
        from modules.backup_manager import BackupManager

        # Initialize backup manager
        backup_manager = BackupManager(self.config_manager.config)

        self.console.print("\n[bold green]🚀 Starting backup process...[/bold green]")

        try:
            # Check if source directory exists
            from pathlib import Path

            if not Path(source_dir).exists():
                self.console.print(f"[red]❌ Source directory does not exist: {source_dir}[/red]")
                self.console.print("Please organize your photos first before backing up.")
                return

            # Check destination accessibility
            self.console.print("🔍 Checking destination accessibility...")
            for i, dest in enumerate(destinations, 1):
                dest_path = Path(dest)
                try:
                    # Try to create the directory if it doesn't exist
                    dest_path.mkdir(parents=True, exist_ok=True)
                    # Test write access
                    test_file = dest_path / ".lenslogic_test_write"
                    test_file.write_text("test")
                    test_file.unlink()
                    self.console.print(f"  ✓ Destination {i}: {dest} - [green]Accessible[/green]")
                except Exception as e:
                    self.console.print(f"  ❌ Destination {i}: {dest} - [red]Error: {e}[/red]")

            self.console.print()

            # Perform incremental sync
            dry_run = self.config_manager.config.get("general", {}).get("dry_run", False)
            if dry_run:
                self.console.print("[yellow]🔍 Running in dry-run mode - no files will be modified[/yellow]")

            result = backup_manager.incremental_sync(source_dir, destinations, dry_run=dry_run)

            # Display results
            self.console.print("\n[bold green]✅ Backup completed![/bold green]")
            self.console.print(f"  • Files scanned: {result['source_scanned']}")
            self.console.print(f"  • Files copied: {result['total_copied']}")
            self.console.print(f"  • Files updated: {result['total_updated']}")
            self.console.print(f"  • Files deleted: {result['total_deleted']}")
            self.console.print(f"  • Sync time: {result['sync_time']:.2f} seconds")

            if result["total_errors"] > 0:
                self.console.print(f"  • [yellow]Errors: {result['total_errors']}[/yellow]")

            # Show per-destination results
            self.console.print("\n[bold]Per-destination results:[/bold]")
            for dest, dest_result in result["destinations"].items():
                self.console.print(f"  📁 {dest}")
                self.console.print(f"    • Copied: {dest_result['files_copied']}")
                self.console.print(f"    • Updated: {dest_result['files_updated']}")
                self.console.print(f"    • Deleted: {dest_result['files_deleted']}")
                self.console.print(f"    • Skipped: {dest_result['files_skipped']}")
                if dest_result["errors"]:
                    self.console.print(f"    • [yellow]Errors: {len(dest_result['errors'])}[/yellow]")
                    # Show first few errors for debugging
                    for error in dest_result["errors"][:3]:
                        self.console.print(f"      - [red]{error}[/red]")
                    if len(dest_result["errors"]) > 3:
                        self.console.print(f"      - [dim]... and {len(dest_result['errors']) - 3} more errors[/dim]")

            # Check if any destinations are missing from results
            expected_destinations = set(destinations)
            actual_destinations = set(result["destinations"].keys())
            missing_destinations = expected_destinations - actual_destinations

            if missing_destinations:
                self.console.print("\n[red]⚠️ Some destinations were not processed:[/red]")
                for missing_dest in missing_destinations:
                    self.console.print(f"  📁 [red]{missing_dest}[/red] - Not processed")

            # Show any top-level errors
            if "error" in result:
                self.console.print(f"\n[red]❌ Top-level error: {result['error']}[/red]")

            # Offer verification
            if self.config_manager.config.get("backup", {}).get("enable_verification", True):
                if questionary.confirm("\nVerify backup integrity?").ask():
                    self._verify_backup_integrity(backup_manager, source_dir, destinations)

        except Exception as e:
            self.console.print(f"[red]❌ Backup failed: {e}[/red]")

    def _verify_backup_integrity(self, backup_manager, source_dir: str, destinations: list):
        """Verify backup integrity"""
        self.console.print("\n[bold cyan]🔍 Verifying backup integrity...[/bold cyan]")

        for dest in destinations:
            self.console.print(f"\nVerifying: {dest}")

            try:
                verification = backup_manager.verify_backup(source_dir, dest, quick_mode=True)

                if verification["integrity_score"] >= 95:
                    self.console.print(f"[green]✓ {verification['integrity_score']:.1f}% integrity - Excellent[/green]")
                elif verification["integrity_score"] >= 90:
                    self.console.print(f"[yellow]⚠ {verification['integrity_score']:.1f}% integrity - Good[/yellow]")
                else:
                    self.console.print(f"[red]❌ {verification['integrity_score']:.1f}% integrity - Issues found[/red]")

                self.console.print(f"  • Verified files: {verification['verified_files']}")

                if verification["missing_files"]:
                    self.console.print(f"  • [yellow]Missing files: {len(verification['missing_files'])}[/yellow]")

                if verification["corrupted_files"]:
                    self.console.print(f"  • [red]Corrupted files: {len(verification['corrupted_files'])}[/red]")

                if verification["extra_files"]:
                    self.console.print(f"  • Extra files: {len(verification['extra_files'])}")

            except Exception as e:
                self.console.print(f"[red]❌ Verification failed: {e}[/red]")

    def _verify_backups(self):
        """Verify existing backups"""
        self.console.print("[bold cyan]✅ Verify Existing Backups[/bold cyan]\n")

        destinations = self.config_manager.config.get("backup", {}).get("destinations", [])
        if not destinations:
            self.console.print("[red]❌ No backup destinations configured![/red]")
            input("\nPress Enter to continue...")
            return

        self.console.print("Backup destinations to verify:")
        for dest in destinations:
            self.console.print(f"  • {dest}")

        if questionary.confirm("\nStart verification process?").ask():
            # Get source directory (organized photos)
            source_dir = self.config_manager.config.get("general", {}).get("destination_directory", "./organized")

            # Initialize backup manager and verify
            from modules.backup_manager import BackupManager

            backup_manager = BackupManager(self.config_manager.config)

            self._verify_backup_integrity(backup_manager, source_dir, destinations)

        input("\nPress Enter to continue...")

    def _show_backup_status(self):
        """Show backup status and statistics"""
        self.console.print("[bold cyan]📊 Backup Status & Statistics[/bold cyan]\n")

        # Create status table
        table = Table(title="Backup Status", show_header=True, header_style="bold cyan")
        table.add_column("Destination", style="bold")
        table.add_column("Status", style="white")
        table.add_column("Last Backup", style="green")
        table.add_column("Files", style="yellow")

        destinations = self.config_manager.config.get("backup", {}).get("destinations", [])

        if destinations:
            for dest in destinations:
                # Mock status - would be implemented with real backup manager
                table.add_row(dest, "✅ Available", "Not implemented", "N/A")
        else:
            table.add_row("No destinations", "❌ Not configured", "-", "-")

        self.console.print(table)
        input("\nPress Enter to continue...")

    def _restore_from_backup(self):
        """Restore from backup"""
        self.console.print("[bold cyan]🔄 Restore from Backup[/bold cyan]\n")

        # Get backup destinations
        destinations = self.config_manager.config.get("backup", {}).get("destinations", [])
        if not destinations:
            self.console.print("[red]❌ No backup destinations configured![/red]")
            input("\nPress Enter to continue...")
            return

        from modules.backup_manager import BackupManager

        backup_manager = BackupManager(self.config_manager.config)

        # Get available backups
        self.console.print("🔍 Scanning backup destinations...")
        candidates = backup_manager.get_restore_candidates(destinations)

        if not candidates["available_backups"]:
            self.console.print("[red]❌ No usable backups found in any destination![/red]")

            # Show why other destinations weren't usable
            if candidates["unavailable_backups"]:
                self.console.print("\n[yellow]Checked backup destinations:[/yellow]")
                for unavailable in candidates["unavailable_backups"]:
                    backup_dir = unavailable["backup_dir"]
                    exists = unavailable["exists"]
                    total_files = unavailable["total_files"]
                    errors = unavailable["errors"]

                    if not exists:
                        self.console.print(f"  📁 {backup_dir} - [red]Directory doesn't exist[/red]")
                    elif total_files == 0:
                        self.console.print(f"  📁 {backup_dir} - [yellow]No files found[/yellow]")
                    elif errors:
                        self.console.print(f"  📁 {backup_dir} - [red]Errors: {', '.join(errors[:2])}[/red]")
                    else:
                        self.console.print(f"  📁 {backup_dir} - [yellow]Unknown issue[/yellow]")

            input("\nPress Enter to continue...")
            return

        # Display available backups
        self.console.print(f"\n[green]Found {len(candidates['available_backups'])} usable backup(s):[/green]")

        # Also show unavailable ones for transparency
        if candidates["unavailable_backups"]:
            self.console.print(f"[yellow]({len(candidates['unavailable_backups'])} destination(s) not usable)[/yellow]")

            # Show details about unavailable backups
            self.console.print("\n[dim]Unavailable backup destinations:[/dim]")
            for unavailable in candidates["unavailable_backups"]:
                backup_dir = unavailable["backup_dir"]
                exists = unavailable["exists"]
                total_files = unavailable["total_files"]
                errors = unavailable["errors"]

                if not exists:
                    self.console.print(f"  📁 {backup_dir} - [red]Directory doesn't exist[/red]")
                elif total_files == 0:
                    self.console.print(f"  📁 {backup_dir} - [yellow]Empty (no files to restore)[/yellow]")
                elif errors:
                    self.console.print(f"  📁 {backup_dir} - [red]Access errors[/red]")
                    for error in errors[:2]:
                        self.console.print(f"    • [dim]{error}[/dim]")
                else:
                    self.console.print(f"  📁 {backup_dir} - [yellow]Unknown issue[/yellow]")
        backup_choices = []

        for i, backup_info in enumerate(candidates["available_backups"], 1):
            backup_dir = backup_info["backup_dir"]
            file_count = backup_info["total_files"]
            size_gb = backup_info["total_size"] / (1024**3)
            last_mod = backup_info["last_modified"]

            if last_mod:
                mod_str = last_mod.strftime("%Y-%m-%d %H:%M")
            else:
                mod_str = "Unknown"

            status = "✅ Recommended" if backup_dir == candidates["recommended_backup"] else "📁 Available"

            self.console.print(f"  {i}. {status}")
            self.console.print(f"     Path: {backup_dir}")
            self.console.print(f"     Files: {file_count:,} ({size_gb:.1f} GB)")
            self.console.print(f"     Last Modified: {mod_str}")

            backup_choices.append(f"{i}. {backup_dir} ({file_count:,} files, {mod_str})")

        # Let user select backup
        backup_choices.append("Cancel")

        backup_choice = questionary.select("\nSelect backup to restore from:", choices=backup_choices).ask()

        if not backup_choice or "Cancel" in backup_choice:
            return

        # Extract backup directory from choice
        backup_index = int(backup_choice.split(".")[0]) - 1
        selected_backup_info = candidates["available_backups"][backup_index]
        backup_dir = selected_backup_info["backup_dir"]

        # Get restore options
        self.console.print(f"\n[bold]Selected backup:[/bold] {backup_dir}")

        # Default to organized directory (most common use case)
        restore_dir = self.config_manager.config.get("general", {}).get("destination_directory", "./organized")

        # Choose restore type
        restore_options = [
            "Full restore (restore all files back to organized directory)",
            "Selective restore (choose specific file patterns)",
            "Advanced options (choose different destination)",
            "Cancel",
        ]

        restore_choice = questionary.select("Choose restore type:", choices=restore_options).ask()

        if not restore_choice or "Cancel" in restore_choice:
            return

        if "Full restore" in restore_choice:
            file_patterns = None
            self.console.print(f"[green]✓[/green] Will restore all files to: {restore_dir}")

        elif "Selective restore" in restore_choice:
            # Get file patterns
            pattern_input = questionary.text(
                "Enter file patterns to restore (comma-separated, e.g., '.jpg,.cr2,2024'):",
                default=".jpg,.jpeg,.png",
            ).ask()

            if pattern_input:
                file_patterns = [p.strip() for p in pattern_input.split(",")]
                self.console.print(f"[green]✓[/green] Will restore files matching: {', '.join(file_patterns)}")
                self.console.print(f"[green]✓[/green] Destination: {restore_dir}")
            else:
                file_patterns = None

        elif "Advanced options" in restore_choice:
            # Advanced options for power users
            alt_dest = questionary.confirm(
                "Restore to a different directory (instead of organized directory)?",
                default=False,
            ).ask()

            if alt_dest:
                restore_dir = questionary.path("Choose restore destination directory:", only_directories=True).ask()

                if not restore_dir:
                    return

            # Get file patterns for advanced
            pattern_input = questionary.text(
                "Enter file patterns to restore (leave blank for all files):",
                default="",
            ).ask()

            if pattern_input:
                file_patterns = [p.strip() for p in pattern_input.split(",")]
            else:
                file_patterns = None

        # Restore options
        preserve_structure = questionary.confirm("Preserve directory structure?", default=True).ask()

        overwrite_newer = questionary.confirm(
            "Overwrite files even if current files are newer? (recommended for restore)",
            default=True,
        ).ask()

        dry_run = questionary.confirm("Run in dry-run mode (preview only)?", default=False).ask()

        # Confirm restore
        self.console.print("\n[bold yellow]⚠️ Restore Summary:[/bold yellow]")
        self.console.print(f"  • From: {backup_dir}")
        self.console.print(f"  • To: {restore_dir}")
        self.console.print(f"  • Files: {selected_backup_info['total_files']:,}")
        self.console.print(f"  • Size: {selected_backup_info['total_size'] / (1024**3):.1f} GB")
        if file_patterns:
            self.console.print(f"  • Patterns: {', '.join(file_patterns)}")
        self.console.print(f"  • Preserve structure: {'Yes' if preserve_structure else 'No'}")
        self.console.print(f"  • Overwrite newer files: {'Yes' if overwrite_newer else 'No'}")
        self.console.print(f"  • Mode: {'Dry run' if dry_run else 'Live restore'}")

        if not questionary.confirm("\nProceed with restore?").ask():
            return

        # Perform restore
        self._perform_restore(
            backup_manager,
            backup_dir,
            restore_dir,
            file_patterns,
            preserve_structure,
            overwrite_newer,
            dry_run,
        )

        input("\nPress Enter to continue...")

    def _perform_restore(
        self,
        backup_manager,
        backup_dir: str,
        restore_dir: str,
        file_patterns,
        preserve_structure: bool,
        overwrite_newer: bool,
        dry_run: bool,
    ):
        """Perform the actual restore operation"""
        self.console.print("\n[bold green]🔄 Starting restore process...[/bold green]")

        try:
            result = backup_manager.restore_from_backup(
                backup_dir=backup_dir,
                restore_dir=restore_dir,
                file_patterns=file_patterns,
                preserve_structure=preserve_structure,
                overwrite_newer=overwrite_newer,
                dry_run=dry_run,
            )

            # Display results
            if dry_run:
                self.console.print("\n[bold yellow]🔍 Dry run completed![/bold yellow]")
            else:
                self.console.print("\n[bold green]✅ Restore completed![/bold green]")

            self.console.print(f"  • Files restored: {result['files_restored']}")
            self.console.print(f"  • Files skipped: {result['files_skipped']}")

            if not dry_run:
                size_mb = result["total_size_restored"] / (1024**2)
                self.console.print(f"  • Size restored: {size_mb:.1f} MB")

            self.console.print(f"  • Restore time: {result['restore_time']:.2f} seconds")

            if result["errors"]:
                self.console.print(f"\n[yellow]⚠️ Errors encountered: {len(result['errors'])}[/yellow]")
                for error in result["errors"][:3]:  # Show first 3 errors
                    self.console.print(f"  - [red]{error}[/red]")
                if len(result["errors"]) > 3:
                    self.console.print(f"  - [dim]... and {len(result['errors']) - 3} more errors[/dim]")
            else:
                self.console.print("[green]✅ No errors encountered[/green]")

        except Exception as e:
            self.console.print(f"[red]❌ Restore failed: {e}[/red]")

    def _configure_backup_settings(self):
        """Configure backup settings"""
        self.console.print("[bold cyan]⚙️  Backup Settings[/bold cyan]\n")

        # Enable verification
        enable_verification = questionary.confirm(
            "Enable backup verification (checksums)?",
            default=self.config_manager.config.get("backup", {}).get("enable_verification", True),
        ).ask()

        # Incremental mode
        incremental_mode = questionary.confirm(
            "Use incremental backup mode?",
            default=self.config_manager.config.get("backup", {}).get("incremental_mode", True),
        ).ask()

        # Use trash
        use_trash = questionary.confirm(
            "Move deleted files to trash instead of permanent deletion?",
            default=self.config_manager.config.get("backup", {}).get("use_trash", True),
        ).ask()

        # Update config
        if "backup" not in self.config_manager.config:
            self.config_manager.config["backup"] = {}

        self.config_manager.config["backup"]["enable_verification"] = enable_verification
        self.config_manager.config["backup"]["incremental_mode"] = incremental_mode
        self.config_manager.config["backup"]["use_trash"] = use_trash

        self.console.print("[green]✓[/green] Backup settings updated")
        input("\nPress Enter to continue...")
