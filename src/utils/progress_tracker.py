import logging
import time
from pathlib import Path
from typing import Any

from rich.console import Console
from rich.panel import Panel
from rich.progress import (
    BarColumn,
    Progress,
    SpinnerColumn,
    TaskProgressColumn,
    TextColumn,
    TimeRemainingColumn,
)
from rich.table import Table

logger = logging.getLogger(__name__)


class ProgressTracker:
    def __init__(self, verbose: bool = True):
        self.console = Console()
        self.verbose = verbose
        self.start_time = None
        self.stats = {
            "total_files": 0,
            "processed_files": 0,
            "skipped_files": 0,
            "failed_files": 0,
            "copied_files": 0,
            "moved_files": 0,
            "renamed_files": 0,
            "duplicates_found": 0,
            "total_size": 0,
            "processed_size": 0,
        }
        self.current_file = None
        self.progress = None
        self.task_id = None

    def start_processing(self, total_files: int, operation: str = "Processing"):
        self.start_time = time.time()
        self.stats["total_files"] = total_files

        if self.verbose:
            self.progress = Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TaskProgressColumn(),
                TimeRemainingColumn(),
                console=self.console,
            )
            self.task_id = self.progress.add_task(f"[cyan]{operation} files...", total=total_files)
            self.progress.start()

    def update_file(self, file_path: str, status: str = "processing"):
        self.current_file = file_path

        if self.verbose and self.progress:
            self.progress.update(self.task_id, description=f"[cyan]{status}: {Path(file_path).name}")

    def file_processed(
        self,
        success: bool = True,
        action: str = None,
        size: int = 0,
        skipped: bool = False,
    ):
        self.stats["processed_files"] += 1
        self.stats["processed_size"] += size

        if skipped:
            self.stats["skipped_files"] += 1
        elif not success:
            self.stats["failed_files"] += 1
        elif action == "copy":
            self.stats["copied_files"] += 1
        elif action == "move":
            self.stats["moved_files"] += 1
        elif action == "rename":
            self.stats["renamed_files"] += 1

        if self.verbose and self.progress:
            self.progress.advance(self.task_id)

    def duplicate_found(self):
        self.stats["duplicates_found"] += 1

    def stop_processing(self):
        if self.progress:
            self.progress.stop()

        if self.start_time:
            elapsed_time = time.time() - self.start_time
            self.stats["elapsed_time"] = elapsed_time

    def print_summary(self):
        self.console.print("\n[bold cyan]═══ Processing Summary ═══[/bold cyan]\n")

        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", justify="right", style="green")

        table.add_row("Total Files", str(self.stats["total_files"]))
        table.add_row("Processed", str(self.stats["processed_files"]))
        table.add_row("Copied", str(self.stats["copied_files"]))
        table.add_row("Moved", str(self.stats["moved_files"]))
        table.add_row("Renamed", str(self.stats["renamed_files"]))
        table.add_row("Skipped", str(self.stats["skipped_files"]))
        table.add_row("Failed", str(self.stats["failed_files"]))
        table.add_row("Duplicates", str(self.stats["duplicates_found"]))

        if self.stats["processed_size"] > 0:
            size_mb = self.stats["processed_size"] / (1024 * 1024)
            table.add_row("Processed Size", f"{size_mb:.2f} MB")

        if "elapsed_time" in self.stats:
            elapsed = self.stats["elapsed_time"]
            minutes = int(elapsed // 60)
            seconds = int(elapsed % 60)
            table.add_row("Time Elapsed", f"{minutes}m {seconds}s")

            if self.stats["processed_files"] > 0:
                rate = self.stats["processed_files"] / elapsed
                table.add_row("Processing Rate", f"{rate:.1f} files/sec")

        self.console.print(table)

        success_rate = 0
        if self.stats["processed_files"] > 0:
            success_rate = (
                (self.stats["processed_files"] - self.stats["failed_files"]) / self.stats["processed_files"] * 100
            )

        if success_rate >= 95:
            status_color = "green"
            status_emoji = "✅"
        elif success_rate >= 80:
            status_color = "yellow"
            status_emoji = "⚠️"
        else:
            status_color = "red"
            status_emoji = "❌"

        self.console.print(f"\n[{status_color}]{status_emoji} Success Rate: {success_rate:.1f}%[/{status_color}]")

    def print_error(self, message: str):
        self.console.print(f"[red]✗ Error:[/red] {message}")

    def print_warning(self, message: str):
        self.console.print(f"[yellow]⚠ Warning:[/yellow] {message}")

    def print_info(self, message: str):
        if self.verbose:
            self.console.print(f"[blue]ℹ Info:[/blue] {message}")

    def print_success(self, message: str):
        self.console.print(f"[green]✓ Success:[/green] {message}")

    def print_dry_run(self, message: str):
        self.console.print(f"[cyan][DRY RUN][/cyan] {message}")

    def display_file_preview(self, original: str, new_name: str, destination: str, metadata: dict[str, Any]):
        panel_content = f"""
[bold]Original:[/bold] {Path(original).name}
[bold]New Name:[/bold] {new_name}
[bold]Destination:[/bold] {destination}

[bold cyan]Metadata:[/bold cyan]
• Date: {metadata.get('datetime_original', 'Unknown')}
• Camera: {metadata.get('camera_model', 'Unknown')}
• Dimensions: {metadata.get('width', '?')}x{metadata.get('height', '?')}
• ISO: {metadata.get('iso', 'N/A')}
• F-Stop: {metadata.get('f_number', 'N/A')}
"""

        if metadata.get("location"):
            panel_content += f"• Location: {metadata['location']['display_name']}\n"

        panel = Panel(
            panel_content.strip(),
            title="[bold blue]File Preview[/bold blue]",
            border_style="blue",
        )

        self.console.print(panel)

    def create_statistics_table(self, stats: dict[str, Any]) -> Table:
        table = Table(title="Library Statistics", show_header=True, header_style="bold magenta")

        table.add_column("File Type", style="cyan")
        table.add_column("Count", justify="right", style="green")
        table.add_column("Size (MB)", justify="right", style="yellow")

        if stats.get("images"):
            table.add_row("Images", str(stats["images"]), "-")
        if stats.get("raw_files"):
            table.add_row("RAW Files", str(stats["raw_files"]), "-")
        if stats.get("videos"):
            table.add_row("Videos", str(stats["videos"]), "-")
        if stats.get("unknown"):
            table.add_row("Unknown", str(stats["unknown"]), "-")

        table.add_row("", "", "")
        table.add_row(
            "[bold]Total[/bold]",
            f"[bold]{stats.get('total_files', 0)}[/bold]",
            f"[bold]{stats.get('total_size_mb', 0):.2f}[/bold]",
        )

        return table
