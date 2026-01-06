"""Mark task as completed command."""

import typer

from todo_cli.display.formatter import DisplayFormatter
from todo_cli.models.config import Config
from todo_cli.models.task_list import TaskList
from todo_cli.storage.config_loader import ConfigLoader
from todo_cli.storage.storage_manager import StorageManager
from todo_cli.utils.undo_manager import UndoManager


def mark_done(
    task_id: int = typer.Argument(..., help="Task ID to mark as completed"),
) -> None:
    """
    Mark a task as completed.

    Examples:
        todo done 3
        todo complete 5
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

    if task.status.value == "completed":
        formatter.print_info(f"Task #{task_id} is already completed.")
        raise typer.Exit(0)

    # Mark as completed
    completed_task = task_list.mark_completed(task_id)

    if completed_task:
        # Record for undo
        undo_manager.record_complete(task)

        # Save
        storage.save(task_list)

        formatter.print_success(f"Marked task #{task_id} as completed: {completed_task.title}")
    else:
        formatter.print_error(f"Failed to mark task #{task_id} as completed.")
        raise typer.Exit(1)
