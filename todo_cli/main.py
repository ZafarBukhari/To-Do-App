"""Main CLI entry point for the To-Do application."""

from pathlib import Path

import typer

from todo_cli.commands.add import add_task
from todo_cli.commands.delete import delete_task
from todo_cli.commands.done import mark_done
from todo_cli.commands.edit import edit_task
from todo_cli.commands.list_cmd import list_tasks
from todo_cli.commands.search import search_tasks
from todo_cli.commands.undo import mark_undo
from todo_cli.display.formatter import DisplayFormatter
from todo_cli.models.config import Config
from todo_cli.models.task_list import TaskList
from todo_cli.storage.config_loader import ConfigLoader
from todo_cli.storage.storage_manager import StorageManager
from todo_cli.utils.undo_manager import UndoManager

# Create main Typer app
app = typer.Typer(
    name="todo",
    help="A production-ready To-Do CLI application",
    no_args_is_help=True,
    add_completion=False,
)


# Register commands with aliases
app.command(name="add")(add_task)
app.command(name="new")(add_task)  # Alias
app.command(name="create")(add_task)  # Alias

app.command(name="list")(list_tasks)
app.command(name="ls")(list_tasks)  # Alias

app.command(name="edit")(edit_task)
app.command(name="modify")(edit_task)  # Alias
app.command(name="update")(edit_task)  # Alias

app.command(name="done")(mark_done)
app.command(name="complete")(mark_done)  # Alias
app.command(name="finish")(mark_done)  # Alias
app.command(name="check")(mark_done)  # Alias

app.command(name="undo")(mark_undo)
app.command(name="reopen")(mark_undo)  # Alias
app.command(name="uncomplete")(mark_undo)  # Alias

app.command(name="delete")(delete_task)
app.command(name="rm")(delete_task)  # Alias
app.command(name="remove")(delete_task)  # Alias

app.command(name="search")(search_tasks)
app.command(name="find")(search_tasks)  # Alias


@app.command()
def init() -> None:
    """Initialize the todo application (create data directory)."""
    config_loader = ConfigLoader()
    config = config_loader.load()

    # Create data directory
    config.data_dir.mkdir(parents=True, exist_ok=True)

    # Create empty tasks file if it doesn't exist
    tasks_file = config.data_dir / "tasks.json"
    if not tasks_file.exists():
        storage = StorageManager(tasks_file)
        storage.save(TaskList())

    # Create config file if it doesn't exist
    config_file = config.data_dir / "config.toml"
    if not config_file.exists():
        config_loader.save(config)

    formatter = DisplayFormatter(config)
    formatter.print_success(f"Initialized todo data directory: {config.data_dir}")
    formatter.print_info(f"Config file: {config_file}")
    formatter.print_info(f"Tasks file: {tasks_file}")


@app.command()
def undo_last() -> None:
    """
    Undo the last destructive action.

    Supports undoing: delete, edit, complete
    """
    config_loader = ConfigLoader()
    config = config_loader.load()

    storage = StorageManager(config.data_dir / "tasks.json")
    task_list = storage.load()

    undo_manager = UndoManager(config.data_dir / "undo_history.json")
    formatter = DisplayFormatter(config)

    if not undo_manager.can_undo():
        formatter.print_info("No actions to undo.")
        raise typer.Exit(0)

    # Get last action
    action = undo_manager.get_last_action()
    if action is None:
        formatter.print_info("No actions to undo.")
        raise typer.Exit(0)

    # Undo based on action type
    if action.action_type == "delete":
        # Restore deleted task
        task_list.add(
            action.task.title,
            priority=action.task.priority.value,
            tags=action.task.tags,
            project=action.task.project,
            due_date=action.task.due_date,
        )
        formatter.print_success(f"Restored deleted task: {action.task.title}")

    elif action.action_type == "edit":
        # Revert edit
        task = task_list.update(action.task.id, **action.previous_state)
        if task:
            formatter.print_success(f"Reverted edit for task #{task.id}")

    elif action.action_type == "complete":
        # Mark as pending
        task = task_list.mark_pending(action.task.id)
        if task:
            formatter.print_success(f"Marked task #{task.id} as pending: {task.title}")

    # Pop the action from history and save
    undo_manager.undo()
    storage.save(task_list)


@app.command()
def config_set(key: str = typer.Argument(..., help="Configuration key"), value: str = typer.Argument(..., help="Configuration value")) -> None:
    """
    Set a configuration value.

    Examples:
        todo config set default_priority high
        todo config set color_enabled false
        todo config set editor vim
    """
    config_loader = ConfigLoader()
    formatter = DisplayFormatter(config_loader.load())

    try:
        config_loader.set(key, value)
        formatter.print_success(f"Set {key} = {value}")
    except Exception as e:
        formatter.print_error(f"Failed to set {key}: {e}")
        raise typer.Exit(1)


@app.command(name="config")
def config_show() -> None:
    """Display current configuration."""
    config_loader = ConfigLoader()
    config = config_loader.load()
    formatter = DisplayFormatter(config)

    formatter.print_info("Current Configuration:")
    print(f"  Data Directory: {config.data_dir}")
    print(f"  Default Priority: {config.default_priority}")
    print(f"  Default Tags: {', '.join(config.default_tags) if config.default_tags else 'None'}")
    print(f"  Show Completed: {config.show_completed}")
    print(f"  Color Enabled: {config.color_enabled}")
    print(f"  Date Format: {config.date_format}")
    print(f"  Editor: {config.editor or '$EDITOR'}")
    print(f"  Sort By: {config.sort_by}")
    print(f"  Sort Reverse: {config.sort_reverse}")
    if config.aliases:
        print(f"  Aliases: {config.aliases}")


def main() -> None:
    """Main entry point."""
    app()


if __name__ == "__main__":
    main()
