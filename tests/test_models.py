"""Unit tests for data models."""

import pytest
from datetime import datetime

from todo_cli.models.task import Task, TaskPriority, TaskStatus
from todo_cli.models.task_list import TaskList
from todo_cli.models.config import Config


class TestTask:
    """Tests for Task model."""

    def test_task_creation(self) -> None:
        """Test basic task creation."""
        task = Task(id=1, title="Test task")
        assert task.id == 1
        assert task.title == "Test task"
        assert task.status == TaskStatus.PENDING
        assert task.priority == TaskPriority.MEDIUM

    def test_task_with_all_attributes(self) -> None:
        """Test task creation with all attributes."""
        task = Task(
            id=1,
            title="Complete project",
            status=TaskStatus.PENDING,
            priority=TaskPriority.HIGH,
            tags=["urgent", "work"],
            project="My Project",
            due_date=datetime(2026, 1, 15),
        )
        assert task.id == 1
        assert task.title == "Complete project"
        assert task.status == TaskStatus.PENDING
        assert task.priority == TaskPriority.HIGH
        assert task.tags == ["urgent", "work"]
        assert task.project == "My Project"
        assert task.due_date == datetime(2026, 1, 15)

    def test_is_overdue_with_past_date(self) -> None:
        """Test overdue detection with past date."""
        past_date = datetime(2020, 1, 1)
        task = Task(id=1, title="Overdue task", due_date=past_date)
        assert task.is_overdue() is True

    def test_is_overdue_with_future_date(self) -> None:
        """Test overdue detection with future date."""
        future_date = datetime(2030, 1, 1)
        task = Task(id=1, title="Future task", due_date=future_date)
        assert task.is_overdue() is False

    def test_is_overdue_without_due_date(self) -> None:
        """Test overdue detection without due date."""
        task = Task(id=1, title="No date task")
        assert task.is_overdue() is False

    def test_serialization(self) -> None:
        """Test task serialization to dictionary."""
        task = Task(
            id=1,
            title="Test",
            status=TaskStatus.COMPLETED,
            priority=TaskPriority.HIGH,
            tags=["urgent", "work"],
            project="Test Project",
            due_date=datetime(2026, 1, 15),
        )
        data = task.to_dict()
        assert data["id"] == 1
        assert data["title"] == "Test"
        assert data["status"] == "completed"
        assert data["priority"] == "high"
        assert data["tags"] == ["urgent", "work"]
        assert data["project"] == "Test Project"
        assert "created_at" in data
        assert "due_date" in data

    def test_deserialization(self) -> None:
        """Test task deserialization from dictionary."""
        data = {
            "id": 1,
            "title": "Test",
            "status": "completed",
            "priority": "high",
            "tags": ["urgent", "work"],
            "project": "Test Project",
            "created_at": "2026-01-01T10:00:00",
            "due_date": "2026-01-15T00:00:00",
        }
        task = Task.from_dict(data)
        assert task.id == 1
        assert task.title == "Test"
        assert task.status == TaskStatus.COMPLETED
        assert task.priority == TaskPriority.HIGH
        assert task.tags == ["urgent", "work"]
        assert task.project == "Test Project"

    def test_string_representation(self) -> None:
        """Test task string representation."""
        task = Task(id=1, title="Test task", status=TaskStatus.PENDING, priority=TaskPriority.MEDIUM)
        result = str(task)
        assert "1." in result
        assert "[ ]" in result or "○" in result  # Depending on platform
        assert "→" in result or "medium" in result
        assert "Test task" in result


class TestTaskList:
    """Tests for TaskList model."""

    def test_add_task(self) -> None:
        """Test adding a task."""
        task_list = TaskList()
        task = task_list.add("New task")
        assert task.id == 1
        assert task.title == "New task"
        assert len(task_list.tasks) == 1
        assert task_list.next_id == 2

    def test_get_by_id(self) -> None:
        """Test retrieving task by ID."""
        task_list = TaskList()
        added_task = task_list.add("Find me")
        found_task = task_list.get_by_id(1)
        assert found_task is added_task
        assert found_task.id == 1

    def test_get_by_id_not_found(self) -> None:
        """Test retrieving non-existent task."""
        task_list = TaskList()
        task_list.add("Task 1")
        not_found = task_list.get_by_id(999)
        assert not_found is None

    def test_delete_task(self) -> None:
        """Test deleting a task."""
        task_list = TaskList()
        task = task_list.add("To delete")
        deleted_task = task_list.delete(1)
        assert deleted_task.id == 1
        assert deleted_task.title == "To delete"
        assert len(task_list.tasks) == 0

    def test_mark_completed(self) -> None:
        """Test marking task as completed."""
        task_list = TaskList()
        task = task_list.add("Complete me")
        completed_task = task_list.mark_completed(1)
        assert completed_task.status == TaskStatus.COMPLETED

    def test_mark_pending(self) -> None:
        """Test marking task as pending."""
        task_list = TaskList()
        task = task_list.add("Pending task", priority=TaskPriority.HIGH)
        pending_task = task_list.mark_pending(1)
        assert pending_task.status == TaskStatus.PENDING

    def test_filter_by_status(self) -> None:
        """Test filtering tasks by status."""
        task_list = TaskList()
        task_list.add("Pending task", priority=TaskPriority.HIGH)
        task_list.add("Completed task", priority=TaskPriority.LOW, status=TaskStatus.COMPLETED)
        task_list.add("Another pending", priority=TaskPriority.MEDIUM)

        pending_tasks = task_list.filter(status=TaskStatus.PENDING)
        assert len(pending_tasks) == 2

        completed_tasks = task_list.filter(status=TaskStatus.COMPLETED)
        assert len(completed_tasks) == 1

    def test_filter_by_priority(self) -> None:
        """Test filtering tasks by priority."""
        task_list = TaskList()
        task_list.add("High priority", priority=TaskPriority.HIGH)
        task_list.add("Low priority", priority=TaskPriority.LOW)
        task_list.add("Medium priority", priority=TaskPriority.MEDIUM)

        high_priority = task_list.filter(priority=TaskPriority.HIGH)
        assert len(high_priority) == 1
        assert high_priority[0].title == "High priority"

    def test_filter_by_tag(self) -> None:
        """Test filtering tasks by tag."""
        task_list = TaskList()
        task_list.add("Work task", tags=["work", "urgent"])
        task_list.add("Personal task", tags=["personal"])
        task_list.add("Another work task", tags=["work"])

        work_tasks = task_list.filter(tag="work")
        assert len(work_tasks) == 2

    def test_filter_by_project(self) -> None:
        """Test filtering tasks by project."""
        task_list = TaskList()
        task_list.add("Project A task", project="Project A")
        task_list.add("Project B task", project="Project B")
        task_list.add("No project task")

        project_a_tasks = task_list.filter(project="Project A")
        assert len(project_a_tasks) == 1
        assert project_a_tasks[0].project == "Project A"

    def test_filter_overdue(self) -> None:
        """Test filtering overdue tasks."""
        task_list = TaskList()
        task_list.add("Overdue task", due_date=datetime(2020, 1, 1))
        task_list.add("Future task", due_date=datetime(2030, 1, 1))
        task_list.add("No date task")

        overdue_tasks = task_list.filter(overdue_only=True)
        assert len(overdue_tasks) == 1
        assert overdue_tasks[0].title == "Overdue task"

    def test_filter_by_keyword(self) -> None:
        """Test filtering tasks by keyword."""
        task_list = TaskList()
        task_list.add("Electricity bill")
        task_list.add("Water bill")
        task_list.add("Buy groceries")

        matching_tasks = task_list.filter(keyword="bill")
        assert len(matching_tasks) == 2

    def test_sort_by_priority(self) -> None:
        """Test sorting tasks by priority."""
        task_list = TaskList()
        task_list.add("Low priority", priority=TaskPriority.LOW)
        task_list.add("High priority", priority=TaskPriority.HIGH)
        task_list.add("Medium priority", priority=TaskPriority.MEDIUM)

        sorted_tasks = task_list.sort(by="priority", reverse=True)
        assert sorted_tasks[0].priority == TaskPriority.HIGH
        assert sorted_tasks[1].priority == TaskPriority.MEDIUM
        assert sorted_tasks[2].priority == TaskPriority.LOW

    def test_sort_by_due_date(self) -> None:
        """Test sorting tasks by due date."""
        task_list = TaskList()
        task_list.add("Task A", due_date=datetime(2026, 1, 15))
        task_list.add("Task B", due_date=datetime(2026, 1, 20))
        task_list.add("Task C", due_date=datetime(2026, 1, 10))

        sorted_tasks = task_list.sort(by="due_date")
        assert sorted_tasks[0].title == "Task C"
        assert sorted_tasks[1].title == "Task A"
        assert sorted_tasks[2].title == "Task B"

    def test_count_by_status(self) -> None:
        """Test counting tasks by status."""
        task_list = TaskList()
        task_list.add("Pending task", priority=TaskPriority.HIGH)
        task_list.add("Completed task", priority=TaskPriority.LOW, status=TaskStatus.COMPLETED)
        task_list.add("Another pending", priority=TaskPriority.MEDIUM)

        assert task_list.count() == 3
        assert task_list.count(status=TaskStatus.PENDING) == 2
        assert task_list.count(status=TaskStatus.COMPLETED) == 1

    def test_serialization(self) -> None:
        """Test TaskList serialization."""
        task_list = TaskList()
        task_list.add("Task 1", priority=TaskPriority.HIGH)
        task_list.add("Task 2", priority=TaskPriority.LOW)

        data = task_list.to_dict()
        assert data["next_id"] == 3
        assert len(data["tasks"]) == 2

    def test_deserialization(self) -> None:
        """Test TaskList deserialization."""
        data = {
            "tasks": [
                {
                    "id": 1,
                    "title": "Task 1",
                    "status": "pending",
                    "priority": "high",
                    "created_at": "2026-01-01T10:00:00",
                },
                {
                    "id": 2,
                    "title": "Task 2",
                    "status": "pending",
                    "priority": "low",
                    "created_at": "2026-01-01T11:00:00",
                },
            ],
            "next_id": 3,
        }
        task_list = TaskList.from_dict(data)
        assert len(task_list.tasks) == 2
        assert task_list.next_id == 3


class TestConfig:
    """Tests for Config model."""

    def test_default_config(self) -> None:
        """Test default configuration values."""
        config = Config()
        assert config.default_priority == "medium"
        assert config.default_tags == []
        assert config.show_completed is True
        assert config.color_enabled is True
        assert config.date_format == "%Y-%m-%d"
        assert config.editor is None
        assert config.sort_by == "priority"
        assert config.sort_reverse is False

    def test_config_serialization(self) -> None:
        """Test Config serialization."""
        config = Config(
            default_priority="high",
            default_tags=["urgent"],
            show_completed=False,
            color_enabled=False,
        )
        data = config.to_dict()
        assert data["default_priority"] == "high"
        assert data["default_tags"] == ["urgent"]
        assert data["show_completed"] is False
        assert data["color_enabled"] is False

    def test_config_deserialization(self) -> None:
        """Test Config deserialization."""
        data = {
            "data_dir": "~/.todo",
            "default_priority": "high",
            "default_tags": ["urgent"],
            "show_completed": False,
            "color_enabled": False,
        }
        config = Config.from_dict(data)
        assert config.default_priority == "high"
        assert config.default_tags == ["urgent"]
        assert config.show_completed is False
        assert config.color_enabled is False
