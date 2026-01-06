"""Search tasks command."""

import typer

from todo_cli.display.formatter import DisplayFormatter
from todo_cli.models.config import Config
from todo_cli.models.task_list import TaskList
from todo_cli.storage.config_loader import ConfigLoader
from todo_cli.storage.storage_manager import StorageManager


def search_tasks(
    keyword: str = typer.Argument(None, help="Search keyword"),
    tag: str = typer.Option(None, "--tag", help="Filter by tag"),
    project: str = typer.Option(None, "--project", help="Filter by project"),
) -> None:
    """
    Search for tasks by keyword or filter criteria.

    Examples:
        todo search "electricity"
        todo find --tag finance
        todo search --project work "report"
    """
    # Load configuration and tasks
    config_loader = ConfigLoader()
    config = config_loader.load()

    storage = StorageManager(config.data_dir / "tasks.json")
    task_list = storage.load()

    formatter = DisplayFormatter(config)

    # Search/filter tasks
    filtered_tasks = task_list.filter(
        keyword=keyword,
        tag=tag,
        project=project,
    )

    if not filtered_tasks:
        formatter.print_info("No matching tasks found.")
        raise typer.Exit(0)

    # Display results
    title = "Search Results"
    if keyword:
        title += f' (keyword: "{keyword}")'
    if tag:
        title += f" (tag: {tag})"
    if project:
        title += f" (project: {project})"

    formatter.format_task_table(filtered_tasks, title=title)
    formatter.print_info(f"Found {len(filtered_tasks)} task(s).")
