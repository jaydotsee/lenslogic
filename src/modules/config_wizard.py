import logging
import questionary
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from utils.branding import print_logo

logger = logging.getLogger(__name__)


class ConfigurationWizard:
    def __init__(self, config_manager):
        self.config_manager = config_manager
        self.console = Console()

    def run_wizard(self) -> bool:
        """Run the complete configuration wizard"""
        self.console.clear()
        print_logo("compact")

        self.console.print("\n[bold cyan]🔧 LensLogic Configuration Wizard[/bold cyan]")
        self.console.print(
            "[dim]Let's set up LensLogic for your photo organization needs[/dim]\n"
        )

        try:
            # Welcome and overview
            if not self._welcome_screen():
                return False

            # Step-by-step configuration
            self._configure_basic_settings()
            self._configure_organization_settings()
            self._configure_naming_patterns()
            self._configure_advanced_features()
            self._configure_backup_settings()

            # Summary and save
            self._show_configuration_summary()

            if questionary.confirm("Save this configuration?", default=True).ask():
                self.config_manager.save_user_config()
                self.console.print(
                    "\n[green]✅ Configuration saved successfully![/green]"
                )
                self.console.print(
                    f"[dim]Configuration saved to: {self.config_manager.user_config_path}[/dim]"
                )
                return True
            else:
                self.console.print("\n[yellow]Configuration not saved[/yellow]")
                return False

        except KeyboardInterrupt:
            self.console.print("\n[yellow]Configuration wizard cancelled[/yellow]")
            return False
        except Exception as e:
            self.console.print(f"\n[red]Error in configuration wizard: {e}[/red]")
            return False

    def _welcome_screen(self) -> bool:
        """Show welcome screen and get user consent"""
        welcome_text = """
Welcome to the LensLogic Configuration Wizard!

This wizard will guide you through setting up LensLogic for your specific
photo organization needs. We'll configure:

• Basic directories and file handling
• Folder organization patterns
• File naming conventions
• Advanced features (geolocation, duplicates, etc.)
• Backup and sync settings

The wizard takes about 5-10 minutes to complete.
        """

        panel = Panel(
            welcome_text.strip(),
            title="[bold blue]Welcome[/bold blue]",
            border_style="blue",
        )
        self.console.print(panel)

        return questionary.confirm(
            "Would you like to continue with the configuration wizard?", default=True
        ).ask()

    def _configure_basic_settings(self):
        """Configure basic directory and file settings"""
        self.console.print("\n[bold cyan]📁 Basic Settings[/bold cyan]")

        # Source directory
        current_source = self.config_manager.get("general.source_directory", ".")
        source = questionary.path(
            "Where are your photos located? (source directory)",
            default=current_source,
            only_directories=True,
        ).ask()

        if source:
            self.config_manager.set("general.source_directory", source)

        # Destination directory
        current_dest = self.config_manager.get(
            "general.destination_directory", "./organized"
        )
        destination = questionary.path(
            "Where should organized photos be saved? (destination directory)",
            default=current_dest,
            only_directories=True,
        ).ask()

        if destination:
            self.config_manager.set("general.destination_directory", destination)

        # File handling
        preserve = questionary.confirm(
            "Preserve original files? (copy instead of move)",
            default=self.config_manager.get("general.preserve_originals", True),
        ).ask()
        self.config_manager.set("general.preserve_originals", preserve)

        verbose = questionary.confirm(
            "Enable verbose output and logging?",
            default=self.config_manager.get("general.verbose", True),
        ).ask()
        self.config_manager.set("general.verbose", verbose)

        self.console.print("[green]✓[/green] Basic settings configured")

    def _configure_organization_settings(self):
        """Configure folder organization settings"""
        self.console.print("\n[bold cyan]🗂️ Folder Organization[/bold cyan]")

        # Folder structure patterns
        patterns = [
            "{year}/{month:02d}/{day:02d}",
            "{year}/{month_name}",
            "{year}-{month:02d}-{day:02d}",
            "{camera}/{year}/{month:02d}",
            "{year}/{month:02d}/{camera}",
            "Custom pattern...",
        ]

        self.console.print(
            "\n[dim]Available variables: {year}, {month}, {day}, {month_name}, {camera}[/dim]"
        )

        pattern = questionary.select(
            "How should folders be organized?",
            choices=patterns,
            default=self.config_manager.get(
                "organization.folder_structure", patterns[0]
            ),
        ).ask()

        if pattern == "Custom pattern...":
            pattern = questionary.text(
                "Enter your custom folder pattern:",
                default=self.config_manager.get("organization.folder_structure"),
            ).ask()

        if pattern:
            self.config_manager.set("organization.folder_structure", pattern)

        # RAW/JPEG separation
        separate_raw = questionary.confirm(
            "Separate RAW and JPEG files into different folders?",
            default=self.config_manager.get("organization.separate_raw", True),
        ).ask()
        self.config_manager.set("organization.separate_raw", separate_raw)

        if separate_raw:
            raw_folder = questionary.text(
                "Name for RAW files folder:",
                default=self.config_manager.get("organization.raw_folder", "RAW"),
            ).ask()
            self.config_manager.set("organization.raw_folder", raw_folder)

            jpg_folder = questionary.text(
                "Name for JPEG files folder:",
                default=self.config_manager.get("organization.jpg_folder", "JPG"),
            ).ask()
            self.config_manager.set("organization.jpg_folder", jpg_folder)

        self.console.print("[green]✓[/green] Folder organization configured")

    def _configure_naming_patterns(self):
        """Configure file naming patterns"""
        self.console.print("\n[bold cyan]📝 File Naming[/bold cyan]")

        # Naming patterns
        patterns = [
            "{year}{month:02d}{day:02d}_{hour:02d}{minute:02d}{second:02d}_{camera}_{original_name}",
            "{date}_{time}_{original_name}",
            "{camera}_{year}-{month:02d}-{day:02d}_{original_name}",
            "{original_name}_{date}_{time}",
            "Custom pattern...",
        ]

        self.console.print(
            "\n[dim]Available variables: {year}, {month}, {day}, {hour}, {minute}, {second}[/dim]"
        )
        self.console.print(
            "[dim]                    {date}, {time}, {camera}, {original_name}, {iso}, {f_number}[/dim]"
        )

        pattern = questionary.select(
            "How should files be named?",
            choices=patterns,
            default=self.config_manager.get("naming.pattern", patterns[0]),
        ).ask()

        if pattern == "Custom pattern...":
            pattern = questionary.text(
                "Enter your custom naming pattern:",
                default=self.config_manager.get("naming.pattern"),
            ).ask()

        if pattern:
            self.config_manager.set("naming.pattern", pattern)

        # Sequence numbers
        include_seq = questionary.confirm(
            "Add sequence numbers to prevent filename conflicts?",
            default=self.config_manager.get("naming.include_sequence", True),
        ).ask()
        self.config_manager.set("naming.include_sequence", include_seq)

        # Extension case
        lowercase_ext = questionary.confirm(
            "Convert file extensions to lowercase?",
            default=self.config_manager.get("naming.lowercase_extension", True),
        ).ask()
        self.config_manager.set("naming.lowercase_extension", lowercase_ext)

        self.console.print("[green]✓[/green] File naming configured")

    def _configure_advanced_features(self):
        """Configure advanced features"""
        self.console.print("\n[bold cyan]🚀 Advanced Features[/bold cyan]")

        # Geolocation
        geo_enabled = questionary.confirm(
            "Enable geolocation features? (GPS extraction, reverse geocoding)",
            default=self.config_manager.get("geolocation.enabled", True),
        ).ask()
        self.config_manager.set("geolocation.enabled", geo_enabled)

        if geo_enabled:
            reverse_geo = questionary.confirm(
                "Enable reverse geocoding? (convert GPS to location names)",
                default=self.config_manager.get("geolocation.reverse_geocode", True),
            ).ask()
            self.config_manager.set("geolocation.reverse_geocode", reverse_geo)

            location_folders = questionary.confirm(
                "Include location in folder structure?",
                default=self.config_manager.get(
                    "geolocation.add_location_to_folder", False
                ),
            ).ask()
            self.config_manager.set(
                "geolocation.add_location_to_folder", location_folders
            )

        # Duplicate detection
        enable_duplicates = questionary.confirm(
            "Enable duplicate detection?",
            default=self.config_manager.get("features.remove_duplicates", True),
        ).ask()
        self.config_manager.set("features.remove_duplicates", enable_duplicates)

        if enable_duplicates:
            dup_methods = ["hash", "pixel", "histogram"]
            dup_method = questionary.select(
                "Duplicate detection method:",
                choices=dup_methods,
                default=self.config_manager.get("duplicate_detection.method", "hash"),
            ).ask()
            self.config_manager.set("duplicate_detection.method", dup_method)

            dup_actions = ["skip", "rename", "move"]
            dup_action = questionary.select(
                "What to do with duplicates:",
                choices=dup_actions,
                default=self.config_manager.get("duplicate_detection.action", "skip"),
            ).ask()
            self.config_manager.set("duplicate_detection.action", dup_action)

        # Image processing
        auto_rotate = questionary.confirm(
            "Auto-rotate images based on EXIF orientation?", default=True
        ).ask()
        self.config_manager.set("image_processing.auto_rotate", auto_rotate)

        # Session detection
        session_detection = questionary.confirm(
            "Enable shooting session detection?", default=True
        ).ask()
        if session_detection:
            time_gap = questionary.text(
                "Time gap between sessions (minutes):",
                default="30",
                validate=lambda x: x.isdigit() and int(x) > 0,
            ).ask()
            self.config_manager.set("session_detection.time_gap_minutes", int(time_gap))

        # Sidecar files
        sidecar = questionary.confirm(
            "Create XMP sidecar files with metadata?",
            default=self.config_manager.get("features.create_sidecar", True),
        ).ask()
        self.config_manager.set("features.create_sidecar", sidecar)

        self.console.print("[green]✓[/green] Advanced features configured")

    def _configure_backup_settings(self):
        """Configure backup and sync settings"""
        self.console.print("\n[bold cyan]💾 Backup & Sync[/bold cyan]")

        enable_backup = questionary.confirm(
            "Configure backup settings?", default=False
        ).ask()

        if enable_backup:
            # Backup verification
            verify_backups = questionary.confirm(
                "Enable backup verification (checksum validation)?", default=True
            ).ask()
            self.config_manager.set("backup.enable_verification", verify_backups)

            # Incremental sync
            incremental = questionary.confirm(
                "Use incremental sync (only copy changed files)?", default=True
            ).ask()
            self.config_manager.set("backup.incremental_mode", incremental)

            # Backup destinations
            destinations = []
            while True:
                dest = questionary.path(
                    f"Backup destination #{len(destinations) + 1} (leave empty to finish):",
                    only_directories=True,
                ).ask()

                if not dest:
                    break

                destinations.append(dest)

                if len(destinations) >= 5:  # Reasonable limit
                    break

            if destinations:
                self.config_manager.set("backup.destinations", destinations)

            # Trash vs permanent delete
            use_trash = questionary.confirm(
                "Send deleted files to trash instead of permanent deletion?",
                default=True,
            ).ask()
            self.config_manager.set("backup.use_trash", use_trash)

        self.console.print("[green]✓[/green] Backup settings configured")

    def _show_configuration_summary(self):
        """Show summary of configuration"""
        self.console.print("\n[bold cyan]📋 Configuration Summary[/bold cyan]")

        # Create summary table
        table = Table(
            title="Your LensLogic Configuration",
            show_header=True,
            header_style="bold magenta",
        )
        table.add_column("Setting", style="cyan", width=30)
        table.add_column("Value", style="green")

        # Basic settings
        table.add_row(
            "Source Directory",
            self.config_manager.get("general.source_directory", "Not set"),
        )
        table.add_row(
            "Destination Directory",
            self.config_manager.get("general.destination_directory", "Not set"),
        )
        table.add_row(
            "Preserve Originals",
            str(self.config_manager.get("general.preserve_originals", True)),
        )

        # Organization
        table.add_row(
            "Folder Structure",
            self.config_manager.get("organization.folder_structure", "Default"),
        )
        table.add_row(
            "Separate RAW/JPEG",
            str(self.config_manager.get("organization.separate_raw", True)),
        )
        table.add_row(
            "Naming Pattern", self.config_manager.get("naming.pattern", "Default")
        )

        # Features
        table.add_row(
            "Geolocation Enabled",
            str(self.config_manager.get("geolocation.enabled", True)),
        )
        table.add_row(
            "Duplicate Detection",
            str(self.config_manager.get("features.remove_duplicates", True)),
        )
        table.add_row(
            "Auto-rotate Images",
            str(self.config_manager.get("image_processing.auto_rotate", True)),
        )

        # Backup
        backup_destinations = self.config_manager.get("backup.destinations", [])
        table.add_row(
            "Backup Destinations",
            f"{len(backup_destinations)} configured" if backup_destinations else "None",
        )

        self.console.print(table)

    def quick_setup(self) -> bool:
        """Quick setup for users who want minimal configuration"""
        self.console.clear()
        print_logo("simple")

        self.console.print("\n[bold cyan]⚡ Quick Setup[/bold cyan]")
        self.console.print("[dim]Let's get you started with sensible defaults[/dim]\n")

        try:
            # Just get the essential paths
            source = questionary.path(
                "Where are your photos?", default=".", only_directories=True
            ).ask()

            if not source:
                return False

            destination = questionary.path(
                "Where should organized photos go?",
                default="./organized",
                only_directories=True,
            ).ask()

            if not destination:
                return False

            # Set basic configuration
            self.config_manager.set("general.source_directory", source)
            self.config_manager.set("general.destination_directory", destination)

            # Use smart defaults
            self.config_manager.set("general.preserve_originals", True)
            self.config_manager.set(
                "organization.folder_structure", "{year}/{month:02d}/{day:02d}"
            )
            self.config_manager.set("organization.separate_raw", True)
            self.config_manager.set(
                "naming.pattern",
                "{year}{month:02d}{day:02d}_{hour:02d}{minute:02d}{second:02d}_{camera}_{original_name}",
            )
            self.config_manager.set("geolocation.enabled", True)
            self.config_manager.set("features.remove_duplicates", True)

            self.console.print("\n[green]✅ Quick setup complete![/green]")
            self.console.print(
                "[dim]You can always run the full configuration wizard later[/dim]"
            )

            if questionary.confirm("Save configuration?", default=True).ask():
                self.config_manager.save_user_config()
                return True

        except KeyboardInterrupt:
            self.console.print("\n[yellow]Quick setup cancelled[/yellow]")

        return False

    def reset_configuration(self) -> bool:
        """Reset configuration to defaults"""
        self.console.print("\n[bold red]⚠️ Reset Configuration[/bold red]")

        if questionary.confirm(
            "This will reset ALL settings to defaults. Are you sure?", default=False
        ).ask():

            # Clear user config
            self.config_manager.config = self.config_manager._get_hardcoded_defaults()

            if questionary.confirm("Save reset configuration?", default=True).ask():
                self.config_manager.save_user_config()
                self.console.print("[green]✅ Configuration reset to defaults[/green]")
                return True

        return False
