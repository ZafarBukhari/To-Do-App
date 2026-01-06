"""Add task command."""

import typer

from todo_cli.display.formatter import DisplayFormatter
from todo_cli.models.config import Config
from todo_cli.models.task_list import TaskList
from todo_cli.storage.config_loader import ConfigLoader
from todo_cli.storage.storage_manager import StorageManager
from todo_cli.utils.date_utils import parse_date
from todo_cli.utils.validators import validate_priority, validate_tags

app = typer.Typer()


def add_task(
    title: str = typer.Argument(..., help="Task description"),
    priority: str = typer.Option("medium", "--priority", "-p", help="Priority level (low, medium, high)"),
    tag: list[str] = typer.Option([], "--tag", "-t", help="Task tags (comma-separated)"),
    project: str = typer.Option(None, "--project", help="Project/group name"),
    due: str = typer.Option(None, "--due", "-d", help="Due date (YYYY-MM-DD, MM-DD, today, tomorrow, +N)"),
) -> None:
    """
    Add a new task to the list.

    Examples:
        todo add "Pay electricity bill" --due 2026-01-10 --priority high --tag finance,urgent
        todo add "Buy groceries" -p low -t shopping
        todo add "Submit report" --project work --due tomorrow
    """
    # Load configuration and tasks
    config_loader = ConfigLoader()
    config = config_loader.load()

    storage = StorageManager(config.data_dir / "tasks.json")
    task_list = storage.load()

    formatter = DisplayFormatter(config)

    # Validate priority
    if not validate_priority(priority):
        formatter.print_error(f"Invalid priority: {priority}. Must be low, medium, or high.")
        raise typer.Exit(1)

    # Parse tags (handle comma-separated)
    all_tags = []
    for t in tag:
        if "," in t:
            all_tags.extend(t.split(","))
        else:
            all_tags.append(t)
    validated_tags = validate_tags(all_tags)

    # Parse due date
    due_date = None
    if due:
        due_date = parse_date(due)
        if due_date is None:
            formatter.print_warning(f"Could not parse due date: {due}. Using no due date.")

    # Add default tags from config if specified
    if config.default_tags:
        for default_tag in config.default_tags:
            if default_tag not in validated_tags:
                validated_tags.append(default_tag)

    # Add task
    task = task_list.add(
        title,
        priority=priority or config.default_priority,
        tags=validated_tags,
        project=project if project else None,
        due_date=due_date,
    )

    # Save
    storage.save(task_list)

    # Display success
    formatter.print_success(f"Added task #{task.id}: {task.title}")
    if task.due_date:
        formatter.print_info(f"Due: {task.due_date.strftime(config.date_format)}")
    if task.tags:
        formatter.print_info(f"Tags: {', '.join(task.tags)}")
    if task.project:
        formatter.print_info(f"Project: {task.project}")
