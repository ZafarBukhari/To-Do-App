"""Unit tests for CLI commands."""

from datetime import datetime
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from todo_cli.commands.add import add_task
from todo_cli.commands.delete import delete_task
from todo_cli.commands.done import mark_done
from todo_cli.commands.edit import edit_task
from todo_cli.commands.list_cmd import list_tasks
from todo_cli.commands.search import search_tasks
from todo_cli.commands.undo import mark_undo
from todo_cli.models.task import TaskPriority, TaskStatus
from todo_cli.models.task_list import TaskList


class TestAddCommand:
    """Tests for add task command."""

    @pytest.fixture
    def temp_config(self, tmp_path: Path) -> dict:
        """Create a temporary config for testing."""
        return {
            "data_dir": tmp_path,
            "default_priority": "medium",
            "default_tags": [],
            "show_completed": True,
            "color_enabled": False,  # Disable color for tests
            "date_format": "%Y-%m-%d",
            "editor": None,
            "sort_by": "priority",
            "sort_reverse": False,
            "aliases": {},
        }

    @patch("todo_cli.commands.add.ConfigLoader")
    @patch("todo_cli.commands.add.StorageManager")
    @patch("todo_cli.commands.add.DisplayFormatter")
    def test_add_simple_task(
        self, mock_formatter, mock_storage, mock_config_loader, temp_config
    ) -> None:
        """Test adding a simple task."""
        mock_config_loader.return_value.load.return_value = temp_config
        mock_storage.return_value.load.return_value = TaskList()
        mock_storage.return_value.save.return_value = None

        add_task("New task")

        # Verify task was added
        mock_storage.return_value.add.assert_called_once_with(
            "New task",
            priority="medium",
            tags=[],
            project=None,
            due_date=None,
        )

        # Verify saved
        mock_storage.return_value.save.assert_called_once()

    @patch("todo_cli.commands.add.ConfigLoader")
    @patch("todo_cli.commands.add.StorageManager")
    @patch("todo_cli.commands.add.DisplayFormatter")
    def test_add_task_with_priority(
        self, mock_formatter, mock_storage, mock_config_loader, temp_config
    ) -> None:
        """Test adding task with priority."""
        mock_config_loader.return_value.load.return_value = temp_config
        mock_storage.return_value.load.return_value = TaskList()
        mock_storage.return_value.save.return_value = None

        add_task("Task with priority", priority="high")

        # Verify priority was set
        added_task = mock_storage.return_value.add.call_args[0]
        assert added_task[1]["priority"] == "high"

    @patch("todo_cli.commands.add.ConfigLoader")
    @patch("todo_cli.commands.add.StorageManager")
    @patch("todo_cli.commands.add.DisplayFormatter")
    def test_add_task_with_tags(
        self, mock_formatter, mock_storage, mock_config_loader, temp_config
    ) -> None:
        """Test adding task with tags."""
        mock_config_loader.return_value.load.return_value = temp_config
        mock_storage.return_value.load.return_value = TaskList()
        mock_storage.return_value.save.return_value = None

        add_task("Tagged task", tag=["urgent", "work"])

        # Verify tags were processed
        added_task = mock_storage.return_value.add.call_args[0]
        assert "urgent" in added_task[1]["tags"]
        assert "work" in added_task[1]["tags"]

    @patch("todo_cli.commands.add.ConfigLoader")
    @patch("todo_cli.commands.add.StorageManager")
    @patch("todo_cli.commands.add.DisplayFormatter")
    def test_add_task_with_due_date(
        self, mock_formatter, mock_storage, mock_config_loader, temp_config
    ) -> None:
        """Test adding task with due date."""
        mock_config_loader.return_value.load.return_value = temp_config
        mock_storage.return_value.load.return_value = TaskList()
        mock_storage.return_value.save.return_value = None

        add_task("Task with due date", due="2026-01-15")

        # Verify due date was parsed
        added_task = mock_storage.return_value.add.call_args[0]
        assert added_task[1]["due_date"] is not None


class TestListCommand:
    """Tests for list tasks command."""

    @pytest.fixture
    def task_list_with_tasks(self) -> TaskList:
        """Create task list with sample tasks."""
        task_list = TaskList()
        task_list.add("Pending high priority", priority="high", tags=["work"])
        task_list.add("Completed task", priority="low", status="completed")
        task_list.add("Pending low priority", priority="low", tags=["personal"])
        return task_list

    @pytest.fixture
    def temp_config(self, tmp_path: Path) -> dict:
        """Create a temporary config for testing."""
        return {
            "data_dir": tmp_path,
            "show_completed": True,
            "color_enabled": False,
            "date_format": "%Y-%m-%d",
        }

    @patch("todo_cli.commands.list_cmd.ConfigLoader")
    @patch("todo_cli.commands.list_cmd.StorageManager")
    @patch("todo_cli.commands.list_cmd.DisplayFormatter")
    def test_list_all_tasks(
        self, mock_formatter, mock_storage, mock_config_loader, task_list_with_tasks, temp_config
    ) -> None:
        """Test listing all tasks."""
        mock_config_loader.return_value.load.return_value = temp_config
        mock_storage.return_value.load.return_value = task_list_with_tasks

        list_tasks()

        # Verify tasks were displayed
        mock_formatter.return_value.format_task_table.assert_called_once()

    @patch("todo_cli.commands.list_cmd.ConfigLoader")
    @patch("todo_cli.commands.list_cmd.StorageManager")
    @patch("todo_cli.commands.list_cmd.DisplayFormatter")
    def test_list_pending_only(
        self, mock_formatter, mock_storage, mock_config_loader, task_list_with_tasks, temp_config
    ) -> None:
        """Test listing pending tasks only."""
        mock_config_loader.return_value.load.return_value = temp_config
        mock_storage.return_value.load.return_value = task_list_with_tasks

        list_tasks(pending=True)

        # Verify only pending tasks shown
        call_args = mock_formatter.return_value.format_task_table.call_args
        displayed_tasks = call_args[0][0]
        assert len(displayed_tasks) == 2  # Only pending tasks


class TestDoneCommand:
    """Tests for mark task as completed command."""

    @pytest.fixture
    def task_list(self) -> TaskList:
        """Create task list with pending task."""
        task_list = TaskList()
        task_list.add("Task to complete", priority="high")
        return task_list

    @pytest.fixture
    def temp_config(self, tmp_path: Path) -> dict:
        """Create a temporary config for testing."""
        return {
            "data_dir": tmp_path,
            "color_enabled": False,
        }

    @patch("todo_cli.commands.done.ConfigLoader")
    @patch("todo_cli.commands.done.StorageManager")
    @patch("todo_cli.commands.done.UndoManager")
    @patch("todo_cli.commands.done.DisplayFormatter")
    def test_mark_task_completed(
        self, mock_formatter, mock_storage, mock_undo, mock_config_loader, task_list, temp_config
    ) -> None:
        """Test marking task as completed."""
        mock_config_loader.return_value.load.return_value = temp_config
        mock_storage.return_value.load.return_value = task_list
        mock_storage.return_value.save.return_value = None
        mock_undo.return_value.record_complete.return_value = None
        task = task_list.get_by_id(1)

        mark_done(1)

        # Verify task was marked completed
        assert task.status == TaskStatus.COMPLETED
        mock_storage.return_value.save.assert_called_once()
        mock_undo.return_value.record_complete.assert_called_once_with(task)


class TestUndoCommand:
    """Tests for mark task as incomplete command."""

    @pytest.fixture
    def task_list(self) -> TaskList:
        """Create task list with completed task."""
        task_list = TaskList()
        task_list.add("Completed task", priority="high", status="completed")
        return task_list

    @pytest.fixture
    def temp_config(self, tmp_path: Path) -> dict:
        """Create a temporary config for testing."""
        return {
            "data_dir": tmp_path,
            "color_enabled": False,
        }

    @patch("todo_cli.commands.undo.ConfigLoader")
    @patch("todo_cli.commands.undo.StorageManager")
    @patch("todo_cli.commands.undo.DisplayFormatter")
    def test_mark_task_incomplete(
        self, mock_formatter, mock_storage, mock_config_loader, task_list, temp_config
    ) -> None:
        """Test marking completed task as incomplete."""
        mock_config_loader.return_value.load.return_value = temp_config
        mock_storage.return_value.load.return_value = task_list
        mock_storage.return_value.save.return_value = None
        task = task_list.get_by_id(1)

        mark_undo(1)

        # Verify task was marked pending
        assert task.status == TaskStatus.PENDING
        mock_storage.return_value.save.assert_called_once()


class TestEditCommand:
    """Tests for edit task command."""

    @pytest.fixture
    def task_list(self) -> TaskList:
        """Create task list with task to edit."""
        task_list = TaskList()
        task_list.add("Original title", priority="medium")
        return task_list

    @pytest.fixture
    def temp_config(self, tmp_path: Path) -> dict:
        """Create a temporary config for testing."""
        return {
            "data_dir": tmp_path,
            "color_enabled": False,
        }

    @patch("todo_cli.commands.edit.ConfigLoader")
    @patch("todo_cli.commands.edit.StorageManager")
    @patch("todo_cli.commands.edit.UndoManager")
    @patch("todo_cli.commands.edit.DisplayFormatter")
    def test_edit_task_title(
        self, mock_formatter, mock_storage, mock_undo, mock_config_loader, task_list, temp_config
    ) -> None:
        """Test editing task title."""
        mock_config_loader.return_value.load.return_value = temp_config
        mock_storage.return_value.load.return_value = task_list
        mock_storage.return_value.save.return_value = None
        mock_undo.return_value.record_edit.return_value = None

        edit_task(1, title="Updated title")

        # Verify task was updated
        task = task_list.get_by_id(1)
        assert task.title == "Updated title"
        mock_storage.return_value.save.assert_called_once()


class TestDeleteCommand:
    """Tests for delete task command."""

    @pytest.fixture
    def task_list(self) -> TaskList:
        """Create task list with task to delete."""
        task_list = TaskList()
        task_list.add("Task to delete", priority="high")
        return task_list

    @pytest.fixture
    def temp_config(self, tmp_path: Path) -> dict:
        """Create a temporary config for testing."""
        return {
            "data_dir": tmp_path,
            "color_enabled": False,
        }

    @patch("todo_cli.commands.delete.ConfigLoader")
    @patch("todo_cli.commands.delete.StorageManager")
    @patch("todo_cli.commands.delete.UndoManager")
    @patch("todo_cli.commands.delete.DisplayFormatter")
    @patch("typer.confirm")
    def test_delete_task(
        self, mock_confirm, mock_formatter, mock_storage, mock_undo, mock_config_loader, task_list, temp_config
    ) -> None:
        """Test deleting a task with confirmation."""
        mock_confirm.return_value = True
        mock_config_loader.return_value.load.return_value = temp_config
        mock_storage.return_value.load.return_value = task_list
        mock_storage.return_value.save.return_value = None
        mock_undo.return_value.record_delete.return_value = None

        delete_task(1)

        # Verify task was deleted
        assert len(task_list.tasks) == 0
        mock_storage.return_value.save.assert_called_once()
        mock_undo.return_value.record_delete.assert_called_once()

    @patch("todo_cli.commands.delete.ConfigLoader")
    @patch("todo_cli.commands.delete.StorageManager")
    @patch("todo_cli.commands.delete.UndoManager")
    @patch("todo_cli.commands.delete.DisplayFormatter")
    @patch("typer.confirm")
    def test_delete_task_skip_confirmation(
        self, mock_confirm, mock_formatter, mock_storage, mock_undo, mock_config_loader, task_list, temp_config
    ) -> None:
        """Test deleting a task without confirmation."""
        mock_config_loader.return_value.load.return_value = temp_config
        mock_storage.return_value.load.return_value = task_list
        mock_storage.return_value.save.return_value = None
        mock_undo.return_value.record_delete.return_value = None

        delete_task(1, confirm=True)

        # Verify confirmation was skipped
        mock_confirm.assert_not_called()
        mock_storage.return_value.save.assert_called_once()


class TestSearchCommand:
    """Tests for search tasks command."""

    @pytest.fixture
    def task_list(self) -> TaskList:
        """Create task list with various tasks."""
        task_list = TaskList()
        task_list.add("Electricity bill", tags=["finance"])
        task_list.add("Grocery shopping", tags=["shopping"])
        task_list.add("Code review", tags=["work", "urgent"])
        task_list.add("Meeting notes", tags=["meeting", "work"])
        return task_list

    @pytest.fixture
    def temp_config(self, tmp_path: Path) -> dict:
        """Create a temporary config for testing."""
        return {
            "data_dir": tmp_path,
            "color_enabled": False,
        }

    @patch("todo_cli.commands.search.ConfigLoader")
    @patch("todo_cli.commands.search.StorageManager")
    @patch("todo_cli.commands.search.DisplayFormatter")
    def test_search_by_keyword(
        self, mock_formatter, mock_storage, mock_config_loader, task_list, temp_config
    ) -> None:
        """Test searching by keyword."""
        mock_config_loader.return_value.load.return_value = temp_config
        mock_storage.return_value.load.return_value = task_list

        search_tasks("bill")

        # Verify search was performed
        call_args = mock_formatter.return_value.format_task_table.call_args
        displayed_tasks = call_args[0][0]
        assert len(displayed_tasks) == 1
        assert "Electricity" in displayed_tasks[0].title

    @patch("todo_cli.commands.search.ConfigLoader")
    @patch("todo_cli.commands.search.StorageManager")
    @patch("todo_cli.commands.search.DisplayFormatter")
    def test_search_by_tag(
        self, mock_formatter, mock_storage, mock_config_loader, task_list, temp_config
    ) -> None:
        """Test searching by tag."""
        mock_config_loader.return_value.load.return_value = temp_config
        mock_storage.return_value.load.return_value = task_list

        search_tasks(tag="work")

        # Verify search was performed
        call_args = mock_formatter.return_value.format_task_table.call_args
        displayed_tasks = call_args[0][0]
        assert len(displayed_tasks) == 2
        assert all("work" in t.tags for t in displayed_tasks)
