"""Display formatter with Rich library for colorized output."""

import os
import sys
from datetime import datetime
from typing import List, Optional

from rich.console import Console
from rich.table import Table

from todo_cli.models.config import Config
from todo_cli.models.task import Task, TaskStatus


class DisplayFormatter:
    """
    Formats task output using Rich library.

    Provides colorized, aligned, human-readable task displays.
    """

    PRIORITY_COLORS = {
        "high": "red",
        "medium": "yellow",
        "low": "green",
    }

    # Use ASCII-safe characters on Windows to avoid encoding issues
    if sys.platform == "win32":
        STATUS_ICONS = {
            TaskStatus.COMPLETED: "[+]",
            TaskStatus.PENDING: "[ ]",
        }
        PRIORITY_ARROWS = {"high": "^", "medium": "->", "low": "v"}
        SUCCESS_ICON = "[OK]"
        ERROR_ICON = "[X]"
        WARNING_ICON = "[!]"
        INFO_ICON = "[i]"
    else:
        STATUS_ICONS = {
            TaskStatus.COMPLETED: "✓",
            TaskStatus.PENDING: "○",
        }
        PRIORITY_ARROWS = {"high": "↑", "medium": "→", "low": "↓"}
        SUCCESS_ICON = "✓"
        ERROR_ICON = "✗"
        WARNING_ICON = "⚠"
        INFO_ICON = "ℹ"

    def __init__(self, config: Config) -> None:
        """
        Initialize formatter.

        Args:
            config: Configuration object.
        """
        self.config = config
        self.console = Console() if config.color_enabled else Console(no_color=True)

    def format_task(
        self,
        task: Task,
        show_id: bool = True,
        show_tags: bool = True,
    ) -> str:
        """
        Format a single task for display.

        Args:
            task: Task to format.
            show_id: Whether to show task ID.
            show_tags: Whether to show tags.

        Returns:
            Formatted task string.
        """
        status_icon = self.STATUS_ICONS[task.status]

        # Determine color based on status and overdue
        if task.status == TaskStatus.COMPLETED:
            color = "green"
        elif task.is_overdue():
            color = "red"
        else:
            color = "yellow"

        # Build output parts
        parts: List[str] = []

        if show_id:
            parts.append(f"{task.id}.")

        # Title with status
        title = f"[{color} bold]{task.title}[/{color} bold]"
        parts.append(f"[{status_icon}] {title}")

        # Priority indicator
        priority_emoji = self.PRIORITY_ARROWS[task.priority.value]
        parts.append(f"[{priority_emoji}]")

        # Due date if present
        if task.due_date:
            due_str = task.due_date.strftime(self.config.date_format)
            due_color = "red" if task.is_overdue() else "blue"
            parts.append(f"Due: [{due_color}]{due_str}[/{due_color}]")

        # Project if present
        if task.project:
            parts.append(f"[dim]({task.project})[/dim]")

        # Tags
        if show_tags and task.tags:
            tag_str = ", ".join(f"#{tag}" for tag in task.tags)
            parts.append(f"[cyan italic]{tag_str}[/cyan italic]")

        return " ".join(parts)

    def format_task_table(
        self,
        tasks: List[Task],
        title: str = "Tasks",
        show_id: bool = True,
        show_tags: bool = True,
    ) -> None:
        """
        Display tasks in a formatted table.

        Args:
            tasks: List of tasks to display.
            title: Table title.
            show_id: Whether to show task IDs.
            show_tags: Whether to show tags.
        """
        if not tasks:
            self.print_info("No tasks found.")
            return

        table = Table(title=title, show_header=True, header_style="bold magenta")

        if show_id:
            table.add_column("ID", style="cyan", width=4)
        table.add_column("Status", width=4)
        table.add_column("Title", style="bold white")
        table.add_column("Priority", width=8)
        table.add_column("Due", width=12)
        table.add_column("Project", width=15)
        if show_tags:
            table.add_column("Tags", width=20)

        for task in tasks:
            status_icon = self.STATUS_ICONS[task.status]

            # Determine row color
            if task.status == TaskStatus.COMPLETED:
                row_style = "green"
            elif task.is_overdue():
                row_style = "red"
            else:
                row_style = "yellow"

            # Due date
            due_str = task.due_date.strftime(self.config.date_format) if task.due_date else ""

            # Tags
            tags_str = ", ".join(task.tags) if task.tags else ""

            row: List[str] = []
            if show_id:
                row.append(str(task.id))
            row.append(status_icon)
            row.append(task.title)
            row.append(task.priority.value)
            row.append(due_str)
            row.append(task.project or "")
            if show_tags:
                row.append(tags_str)

            table.add_row(*row, style=row_style)

        self.console.print(table)

    def print_summary(self, total: int, completed: int, pending: int, overdue: int) -> None:
        """
        Print task summary statistics.

        Args:
            total: Total number of tasks.
            completed: Number of completed tasks.
            pending: Number of pending tasks.
            overdue: Number of overdue tasks.
        """
        self.console.print(
            f"\n[bold]Summary:[/bold] "
            f"{total} total | "
            f"[green]{completed} completed[/green] | "
            f"[yellow]{pending} pending[/yellow] | "
            f"[red]{overdue} overdue[/red]"
        )

    def print_success(self, message: str) -> None:
        """Print success message in green."""
        self.console.print(f"[bold green]{self.SUCCESS_ICON} {message}[/bold green]")

    def print_error(self, message: str) -> None:
        """Print error message in red."""
        self.console.print(f"[bold red]{self.ERROR_ICON} {message}[/bold red]")

    def print_warning(self, message: str) -> None:
        """Print warning message in yellow."""
        self.console.print(f"[bold yellow]{self.WARNING_ICON} {message}[/bold yellow]")

    def print_info(self, message: str) -> None:
        """Print info message in blue."""
        self.console.print(f"[bold blue]{self.INFO_ICON} {message}[/bold blue]")
