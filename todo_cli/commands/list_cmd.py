"""List tasks command."""

from typing import List

import typer

from todo_cli.display.formatter import DisplayFormatter
from todo_cli.models.config import Config
from todo_cli.models.task import TaskPriority, TaskStatus
from todo_cli.models.task_list import TaskList
from todo_cli.storage.config_loader import ConfigLoader
from todo_cli.storage.storage_manager import StorageManager
from todo_cli.utils.validators import validate_priority


def list_tasks(
    all: bool = typer.Option(False, "--all", "-a", help="Show all tasks"),
    pending: bool = typer.Option(False, "--pending", "-p", help="Show pending tasks"),
    completed: bool = typer.Option(False, "--completed", "-c", help="Show completed tasks"),
    tag: str = typer.Option(None, "--tag", help="Filter by tag"),
    project: str = typer.Option(None, "--project", help="Filter by project"),
    overdue: bool = typer.Option(False, "--overdue", help="Show only overdue tasks"),
    sort: str = typer.Option("priority", "--sort", help="Sort by: priority, due_date, created_at, title"),
    reverse: bool = typer.Option(False, "--reverse", "-r", help="Reverse sort order"),
) -> None:
    """
    List tasks with optional filtering and sorting.

    Examples:
        todo list --pending
        todo ls --tag finance
        todo list --overdue --sort due_date
        todo list --project work --reverse
    """
    # Load configuration and tasks
    config_loader = ConfigLoader()
    config = config_loader.load()

    storage = StorageManager(config.data_dir / "tasks.json")
    task_list = storage.load()

    formatter = DisplayFormatter(config)

    # Determine filter criteria
    status_filter: TaskStatus | None = None

    if pending:
        status_filter = TaskStatus.PENDING
    elif completed:
        status_filter = TaskStatus.COMPLETED
    elif not all and not config.show_completed:
        status_filter = TaskStatus.PENDING

    # Filter tasks
    filtered_tasks = task_list.filter(
        status=status_filter,
        tag=tag,
        project=project,
        overdue_only=overdue,
    )

    # Sort tasks
    sorted_tasks = task_list.sort(tasks=filtered_tasks, by=sort, reverse=reverse)

    # Display
    title = "All Tasks"
    if status_filter == TaskStatus.PENDING:
        title = "Pending Tasks"
    elif status_filter == TaskStatus.COMPLETED:
        title = "Completed Tasks"
    if tag:
        title += f" (tag: {tag})"
    if project:
        title += f" (project: {project})"
    if overdue:
        title += " (overdue)"

    formatter.format_task_table(sorted_tasks, title=title)

    # Print summary
    total_count = len(task_list.get_all())
    completed_count = task_list.count(TaskStatus.COMPLETED)
    pending_count = task_list.count(TaskStatus.PENDING)
    overdue_count = len(task_list.filter(overdue_only=True))

    formatter.print_summary(total_count, completed_count, pending_count, overdue_count)
