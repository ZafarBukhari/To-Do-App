"""TaskList model with CRUD operations, filtering, and sorting."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Callable, Dict, List, Optional

from todo_cli.models.task import Task, TaskPriority, TaskStatus


@dataclass
class TaskList:
    """
    Manages a collection of tasks with CRUD operations.

    Attributes:
        tasks: List of Task objects
        next_id: Next available task ID
    """

    tasks: List[Task] = field(default_factory=list)
    next_id: int = 1

    def add(self, title: str, **kwargs) -> Task:
        """
        Add a new task to the list.

        Args:
            title: Task title
            **kwargs: Additional task attributes (priority, tags, due_date, etc.)

        Returns:
            The newly created Task object.
        """
        task = Task(
            id=self.next_id,
            title=title,
            status=TaskStatus(kwargs.get("status", "pending")),
            priority=TaskPriority(kwargs.get("priority", "medium")),
            tags=kwargs.get("tags", []),
            project=kwargs.get("project"),
            due_date=kwargs.get("due_date"),
        )
        self.tasks.append(task)
        self.next_id += 1
        return task

    def get_by_id(self, task_id: int) -> Optional[Task]:
        """
        Retrieve a task by its ID.

        Args:
            task_id: The unique task identifier.

        Returns:
            Task object if found, None otherwise.
        """
        for task in self.tasks:
            if task.id == task_id:
                return task
        return None

    def update(self, task_id: int, **kwargs) -> Optional[Task]:
        """
        Update an existing task.

        Args:
            task_id: The unique task identifier.
            **kwargs: Fields to update.

        Returns:
            Updated Task object if found, None otherwise.
        """
        task = self.get_by_id(task_id)
        if task is None:
            return None

        for key, value in kwargs.items():
            if value is not None and hasattr(task, key):
                if key == "status":
                    task.status = TaskStatus(value)
                elif key == "priority":
                    task.priority = TaskPriority(value)
                else:
                    setattr(task, key, value)
        return task

    def delete(self, task_id: int) -> Optional[Task]:
        """
        Delete a task from the list.

        Args:
            task_id: The unique task identifier.

        Returns:
            Deleted Task object if found, None otherwise.
        """
        task = self.get_by_id(task_id)
        if task is None:
            return None
        self.tasks.remove(task)
        return task

    def mark_completed(self, task_id: int) -> Optional[Task]:
        """
        Mark a task as completed.

        Args:
            task_id: The unique task identifier.

        Returns:
            Updated Task object if found, None otherwise.
        """
        return self.update(task_id, status=TaskStatus.COMPLETED)

    def mark_pending(self, task_id: int) -> Optional[Task]:
        """
        Mark a task as pending (undo completion).

        Args:
            task_id: The unique task identifier.

        Returns:
            Updated Task object if found, None otherwise.
        """
        return self.update(task_id, status=TaskStatus.PENDING)

    def filter(
        self,
        status: Optional[TaskStatus] = None,
        priority: Optional[TaskPriority] = None,
        tag: Optional[str] = None,
        project: Optional[str] = None,
        overdue_only: bool = False,
        keyword: Optional[str] = None,
    ) -> List[Task]:
        """
        Filter tasks based on criteria.

        Args:
            status: Filter by task status.
            priority: Filter by priority.
            tag: Filter by tag presence.
            project: Filter by project name.
            overdue_only: Only include overdue tasks.
            keyword: Search keyword in title.

        Returns:
            List of filtered Task objects.
        """
        filtered_tasks = self.tasks.copy()

        if status:
            filtered_tasks = [t for t in filtered_tasks if t.status == status]
        if priority:
            filtered_tasks = [t for t in filtered_tasks if t.priority == priority]
        if tag:
            filtered_tasks = [t for t in filtered_tasks if tag in t.tags]
        if project:
            filtered_tasks = [t for t in filtered_tasks if t.project == project]
        if overdue_only:
            filtered_tasks = [t for t in filtered_tasks if t.is_overdue()]
        if keyword:
            filtered_tasks = [t for t in filtered_tasks if keyword.lower() in t.title.lower()]

        return filtered_tasks

    def sort(
        self, tasks: Optional[List[Task]] = None, by: str = "priority", reverse: bool = False
    ) -> List[Task]:
        """
        Sort tasks by specified criteria.

        Args:
            tasks: List of tasks to sort (defaults to all tasks).
            by: Sort field ('priority', 'due_date', 'created_at', 'title').
            reverse: Sort in descending order.

        Returns:
            Sorted list of Task objects.
        """
        if tasks is None:
            tasks = self.tasks

        sort_key: Callable[[Task], any]
        if by == "priority":
            priority_order = {"high": 3, "medium": 2, "low": 1}
            sort_key = lambda t: priority_order[t.priority.value]
        elif by == "due_date":
            sort_key = lambda t: t.due_date or datetime.max
        elif by == "created_at":
            sort_key = lambda t: t.created_at
        elif by == "title":
            sort_key = lambda t: t.title.lower()
        else:
            sort_key = lambda t: t.id

        return sorted(tasks, key=sort_key, reverse=reverse)

    def get_all(self) -> List[Task]:
        """Return all tasks."""
        return self.tasks.copy()

    def count(self, status: Optional[TaskStatus] = None) -> int:
        """
        Count tasks optionally by status.

        Args:
            status: Optional status filter.

        Returns:
            Number of matching tasks.
        """
        if status:
            return len(self.filter(status=status))
        return len(self.tasks)

    def to_dict(self) -> Dict:
        """
        Convert TaskList to dictionary for JSON serialization.

        Returns:
            Dictionary representation of the task list.
        """
        return {
            "tasks": [task.to_dict() for task in self.tasks],
            "next_id": self.next_id,
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "TaskList":
        """
        Create TaskList from dictionary.

        Args:
            data: Dictionary containing task list data.

        Returns:
            TaskList instance.
        """
        tasks = [Task.from_dict(task_data) for task_data in data.get("tasks", [])]
        return cls(tasks=tasks, next_id=data.get("next_id", 1))
