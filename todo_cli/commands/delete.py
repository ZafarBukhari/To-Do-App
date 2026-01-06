"""Delete task command."""

import typer

from todo_cli.display.formatter import DisplayFormatter
from todo_cli.models.config import Config
from todo_cli.models.task_list import TaskList
from todo_cli.storage.config_loader import ConfigLoader
from todo_cli.storage.storage_manager import StorageManager
from todo_cli.utils.undo_manager import UndoManager


def delete_task(
    task_id: int = typer.Argument(..., help="Task ID to delete"),
    confirm: bool = typer.Option(False, "--yes", "-y", help="Skip confirmation"),
) -> None:
    """
    Delete a task from the list.

    Examples:
        todo delete 5
        todo rm 3 --yes
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

    # Show task details
    print(formatter.format_task(task, show_tags=True))

    # Confirm deletion
    if not confirm:
        typer.confirm(f"Are you sure you want to delete task #{task_id}?", abort=True)

    # Delete task
    deleted_task = task_list.delete(task_id)

    if deleted_task:
        # Record for undo
        undo_manager.record_delete(task)

        # Save
        storage.save(task_list)

        formatter.print_success(f"Deleted task #{task_id}: {deleted_task.title}")
    else:
        formatter.print_error(f"Failed to delete task #{task_id}")
        raise typer.Exit(1)
