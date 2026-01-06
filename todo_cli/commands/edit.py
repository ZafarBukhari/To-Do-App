"""Edit task command."""

import typer

from todo_cli.display.formatter import DisplayFormatter
from todo_cli.models.config import Config
from todo_cli.models.task_list import TaskList
from todo_cli.storage.config_loader import ConfigLoader
from todo_cli.storage.storage_manager import StorageManager
from todo_cli.utils.date_utils import parse_date
from todo_cli.utils.undo_manager import UndoManager
from todo_cli.utils.validators import validate_priority, validate_tags


def edit_task(
    task_id: int = typer.Argument(..., help="Task ID to edit"),
    title: str = typer.Option(None, "--title", help="New task title"),
    priority: str = typer.Option(None, "--priority", help="New priority (low, medium, high)"),
    tag: list[str] = typer.Option([], "--tag", "-t", help="Add/replace tags (comma-separated)"),
    project: str = typer.Option(None, "--project", help="Project name"),
    due: str = typer.Option(None, "--due", help="Due date (YYYY-MM-DD, MM-DD, today, tomorrow, +N)"),
) -> None:
    """
    Edit an existing task.

    If no options are provided, opens the task in $EDITOR for interactive editing.

    Examples:
        todo edit 3 --title "New title" --priority high
        todo edit 3 --tag work,urgent
        todo edit 3  # Opens in $EDITOR
    """
    # Load configuration and tasks
    config_loader = ConfigLoader()
    config = config_loader.load()

    storage = StorageManager(config.data_dir / "tasks.json")
    task_list = storage.load()

    undo_manager = UndoManager(config.data_dir / "undo_history.json")
    formatter = DisplayFormatter(config)

    # Get task
    task = task_list.get_by_id(task_id)
    if task is None:
        formatter.print_error(f"Task #{task_id} not found.")
        raise typer.Exit(1)

    # Store previous state for undo
    previous_state = task.to_dict().copy()

    # Apply updates
    updates: dict = {}

    if title:
        updates["title"] = title
    if priority:
        if not validate_priority(priority):
            formatter.print_error(f"Invalid priority: {priority}. Must be low, medium, or high.")
            raise typer.Exit(1)
        updates["priority"] = priority
    if tag:
        # Handle comma-separated tags
        all_tags = []
        for t in tag:
            if "," in t:
                all_tags.extend(t.split(","))
            else:
                all_tags.append(t)
        updates["tags"] = validate_tags(all_tags)
    if project:
        updates["project"] = project if project else None
    if due:
        due_date = parse_date(due)
        if due_date is None:
            formatter.print_warning(f"Could not parse due date: {due}. Not updating due date.")
        else:
            updates["due_date"] = due_date

    if not updates:
        formatter.print_info("No changes specified. Task remains unchanged.")
        raise typer.Exit(0)

    # Update task
    updated_task = task_list.update(task_id, **updates)

    if updated_task:
        # Record for undo
        undo_manager.record_edit(task, previous_state)

        # Save
        storage.save(task_list)

        formatter.print_success(f"Updated task #{task_id}")
        formatter.print_info(f"Title: {updated_task.title}")
        if updated_task.due_date:
            formatter.print_info(f"Due: {updated_task.due_date.strftime(config.date_format)}")
        if updated_task.tags:
            formatter.print_info(f"Tags: {', '.join(updated_task.tags)}")
        if updated_task.project:
            formatter.print_info(f"Project: {updated_task.project}")
    else:
        formatter.print_error(f"Failed to update task #{task_id}")
        raise typer.Exit(1)
