"""Task model with all required attributes and methods."""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional


class TaskStatus(str, Enum):
    """Task status enumeration."""

    PENDING = "pending"
    COMPLETED = "completed"


class TaskPriority(str, Enum):
    """Task priority levels."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


@dataclass
class Task:
    """
    Represents a single task in the to-do list.

    Attributes:
        id: Unique numeric identifier
        title: Task description/title
        status: Current task status
        priority: Task priority level
        tags: List of associated tags
        project: Optional project/group name
        created_at: Timestamp when task was created
        due_date: Optional due date for the task
    """

    id: int
    title: str
    status: TaskStatus = TaskStatus.PENDING
    priority: TaskPriority = TaskPriority.MEDIUM
    tags: List[str] = field(default_factory=list)
    project: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    due_date: Optional[datetime] = None

    def is_overdue(self) -> bool:
        """
        Check if the task is overdue.

        Returns:
            True if task has a due date and it's in the past, False otherwise.
        """
        if self.due_date is None:
            return False
        return datetime.now() > self.due_date

    def to_dict(self) -> Dict:
        """
        Convert task to dictionary for JSON serialization.

        Returns:
            Dictionary representation of the task.
        """
        return {
            "id": self.id,
            "title": self.title,
            "status": self.status.value,
            "priority": self.priority.value,
            "tags": self.tags,
            "project": self.project,
            "created_at": self.created_at.isoformat(),
            "due_date": self.due_date.isoformat() if self.due_date else None,
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "Task":
        """
        Create Task instance from dictionary.

        Args:
            data: Dictionary containing task data.

        Returns:
            Task instance.
        """
        return cls(
            id=data["id"],
            title=data["title"],
            status=TaskStatus(data["status"]),
            priority=TaskPriority(data["priority"]),
            tags=data.get("tags", []),
            project=data.get("project"),
            created_at=datetime.fromisoformat(data["created_at"]),
            due_date=datetime.fromisoformat(data["due_date"]) if data.get("due_date") else None,
        )

    def __str__(self) -> str:
        """String representation of task."""
        status_icon = "✓" if self.status == TaskStatus.COMPLETED else "○"
        priority_emoji = {"low": "↓", "medium": "→", "high": "↑"}[self.priority.value]
        return f"{self.id}. [{status_icon}] {self.title} {priority_emoji}"
