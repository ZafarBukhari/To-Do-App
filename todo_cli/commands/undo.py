"""Mark task as incomplete command."""

import typer

from todo_cli.display.formatter import DisplayFormatter
from todo_cli.models.config import Config
from todo_cli.models.task_list import TaskList
from todo_cli.storage.config_loader import ConfigLoader
from todo_cli.storage.storage_manager import StorageManager


def mark_undo(
    task_id: int = typer.Argument(..., help="Task ID to mark as incomplete"),
) -> None:
    """
    Mark a task as incomplete (undo completion).

    Examples:
        todo undo 3
        todo reopen 5
    """
    # Load configuration and tasks
    config_loader = ConfigLoader()
    config = config_loader.load()

    storage = StorageManager(config.data_dir / "tasks.json")
    task_list = storage.load()

    formatter = DisplayFormatter(config)

    # Get task
    task = task_list.get_by_id(task_id)
    if task is None:
        formatter.print_error(f"Task #{task_id} not found.")
        raise typer.Exit(1)

    if task.status.value == "pending":
        formatter.print_info(f"Task #{task_id} is already pending.")
        raise typer.Exit(0)

    # Mark as pending
    pending_task = task_list.mark_pending(task_id)

    if pending_task:
        # Save
        storage.save(task_list)

        formatter.print_success(f"Marked task #{task_id} as pending: {pending_task.title}")
    else:
        formatter.print_error(f"Failed to mark task #{task_id} as pending.")
        raise typer.Exit(1)
