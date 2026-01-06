"""Undo manager for tracking and reverting destructive actions."""

import json
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from todo_cli.models.task import Task


@dataclass
class UndoAction:
    """
    Represents a single undoable action.

    Attributes:
        action_type: Type of action (delete, edit, complete, etc.)
        task: Task that was affected
        previous_state: Previous state of task (for edits)
        timestamp: When the action occurred
    """

    action_type: str
    task: Task
    previous_state: Optional[Dict] = None
    timestamp: datetime = field(default_factory=datetime.now)


class UndoManager:
    """Manages undo history for destructive actions."""

    def __init__(self, history_file: Path) -> None:
        """
        Initialize undo manager.

        Args:
            history_file: Path to undo history file.
        """
        self.history_file: Path = history_file
        self.history: List[UndoAction] = []
        self._load_history()

    def record_delete(self, task: Task) -> None:
        """
        Record a task deletion for undo.

        Args:
            task: The deleted task.
        """
        action = UndoAction(action_type="delete", task=task)
        self.history.append(action)
        self._save_history()

    def record_edit(self, task: Task, previous_state: Dict) -> None:
        """
        Record a task edit for undo.

        Args:
            task: The edited task.
            previous_state: Previous task state.
        """
        action = UndoAction(action_type="edit", task=task, previous_state=previous_state)
        self.history.append(action)
        self._save_history()

    def record_complete(self, task: Task) -> None:
        """
        Record a task completion for undo.

        Args:
            task: The completed task.
        """
        action = UndoAction(action_type="complete", task=task, previous_state={"status": "pending"})
        self.history.append(action)
        self._save_history()

    def can_undo(self) -> bool:
        """Check if undo is available."""
        return len(self.history) > 0

    def get_last_action(self) -> Optional[UndoAction]:
        """Get the last action for undo."""
        return self.history[-1] if self.history else None

    def undo(self) -> Optional[UndoAction]:
        """
        Perform undo operation.

        Returns:
            The undo action that was performed.
        """
        if not self.history:
            return None

        action = self.history.pop()
        self._save_history()
        return action

    def clear_history(self) -> None:
        """Clear all undo history."""
        self.history = []
        self._save_history()

    def _save_history(self) -> None:
        """Save undo history to file."""
        # Keep only last 50 actions
        self.history = self.history[-50:]

        data = [
            {
                "action_type": action.action_type,
                "task": action.task.to_dict(),
                "previous_state": action.previous_state,
                "timestamp": action.timestamp.isoformat(),
            }
            for action in self.history
        ]

        with open(self.history_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, default=str)

    def _load_history(self) -> None:
        """Load undo history from file."""
        if not self.history_file.exists():
            return

        try:
            with open(self.history_file, "r", encoding="utf-8") as f:
                data = json.load(f)

            self.history = [
                UndoAction(
                    action_type=item["action_type"],
                    task=Task.from_dict(item["task"]),
                    previous_state=item.get("previous_state"),
                    timestamp=datetime.fromisoformat(item["timestamp"]),
                )
                for item in data
            ]
        except Exception:
            self.history = []
