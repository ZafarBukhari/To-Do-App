"""Storage manager with atomic writes and backup support."""

import json
import shutil
from datetime import datetime
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Optional

from todo_cli.models.task_list import TaskList


class StorageError(Exception):
    """Storage-related errors."""

    pass


class StorageManager:
    """
    Manages task storage with atomic writes and backup support.

    Ensures data integrity through atomic file operations and backup management.
    """

    def __init__(self, file_path: Path, create_backup: bool = True) -> None:
        """
        Initialize storage manager.

        Args:
            file_path: Path to the tasks JSON file.
            create_backup: Whether to create backups on write.
        """
        self.file_path: Path = file_path
        self.create_backup: bool = create_backup
        self.backup_dir: Path = file_path.parent / "backups"

        # Ensure parent directory exists
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        if create_backup:
            self.backup_dir.mkdir(exist_ok=True)

    def load(self) -> TaskList:
        """
        Load tasks from JSON file.

        Returns:
            TaskList with loaded tasks.
        """
        if not self.file_path.exists():
            return TaskList()

        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return TaskList.from_dict(data)
        except (json.JSONDecodeError, KeyError) as e:
            raise StorageError(f"Failed to load tasks: {e}")

    def save(self, task_list: TaskList) -> None:
        """
        Save tasks to JSON file with atomic write.

        Args:
            task_list: TaskList to save.
        """
        # Create backup if enabled
        if self.create_backup and self.file_path.exists():
            self._create_backup()

        # Atomic write using temporary file
        data = task_list.to_dict()
        data["version"] = "1.0.0"
        data["last_modified"] = datetime.now().isoformat()

        try:
            with NamedTemporaryFile(
                mode="w",
                encoding="utf-8",
                dir=self.file_path.parent,
                delete=False,
                prefix=f"{self.file_path.name}.",
                suffix=".tmp",
            ) as tmp_file:
                json.dump(data, tmp_file, indent=2, ensure_ascii=False)
                tmp_path = Path(tmp_file.name)

            # Atomic replace
            tmp_path.replace(self.file_path)
        except (IOError, OSError) as e:
            raise StorageError(f"Failed to save tasks: {e}")

    def _create_backup(self) -> None:
        """Create timestamped backup of current file."""
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        backup_path = self.backup_dir / f"{self.file_path.name}.{timestamp}"

        # Keep only last 10 backups
        backups = sorted(self.backup_dir.glob(f"{self.file_path.name}.*"))
        while len(backups) > 10:
            backups[0].unlink()
            backups.pop(0)

        shutil.copy2(self.file_path, backup_path)

    def restore_backup(self, backup_timestamp: str) -> None:
        """
        Restore from backup.

        Args:
            backup_timestamp: Timestamp of backup to restore.
        """
        backup_path = self.backup_dir / f"{self.file_path.name}.{backup_timestamp}"
        if not backup_path.exists():
            raise StorageError(f"Backup not found: {backup_timestamp}")

        shutil.copy2(backup_path, self.file_path)

    def list_backups(self) -> list[str]:
        """
        List available backups.

        Returns:
            List of backup timestamps.
        """
        backups = sorted(self.backup_dir.glob(f"{self.file_path.name}.*"))
        return [b.name.split(".", 2)[2] for b in backups]
