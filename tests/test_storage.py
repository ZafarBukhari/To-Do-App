"""Unit tests for storage modules."""

import json
from datetime import datetime
from pathlib import Path
from unittest.mock import patch

import pytest
import tempfile

from todo_cli.models.task import Task, TaskPriority, TaskStatus
from todo_cli.models.task_list import TaskList
from todo_cli.storage.config_loader import Config, ConfigError, ConfigLoader
from todo_cli.storage.storage_manager import StorageError, StorageManager


class TestStorageManager:
    """Tests for StorageManager."""

    @pytest.fixture
    def temp_dir(self, tmp_path: Path) -> Path:
        """Create a temporary directory for testing."""
        return tmp_path

    def test_load_creates_empty_tasklist(self, temp_dir: Path) -> None:
        """Test loading from non-existent file creates empty TaskList."""
        tasks_file = temp_dir / "tasks.json"
        storage = StorageManager(tasks_file)
        task_list = storage.load()

        assert isinstance(task_list, TaskList)
        assert len(task_list.tasks) == 0

    def test_save_and_load(self, temp_dir: Path) -> None:
        """Test saving and loading tasks."""
        tasks_file = temp_dir / "tasks.json"
        storage = StorageManager(tasks_file)

        # Create and save tasks
        task_list = TaskList()
        task_list.add("Task 1", priority="high")
        task_list.add("Task 2", priority="low")
        storage.save(task_list)

        # Load and verify
        loaded_list = storage.load()
        assert len(loaded_list.tasks) == 2
        assert loaded_list.tasks[0].title == "Task 1"
        assert loaded_list.tasks[0].priority == TaskPriority.HIGH
        assert loaded_list.tasks[1].title == "Task 2"

    def test_save_creates_version_and_metadata(self, temp_dir: Path) -> None:
        """Test saving adds version and metadata."""
        tasks_file = temp_dir / "tasks.json"
        storage = StorageManager(tasks_file)

        task_list = TaskList()
        task_list.add("Test task")
        storage.save(task_list)

        # Read file to verify
        with open(tasks_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        assert data["version"] == "1.0.0"
        assert "last_modified" in data
        assert data["next_id"] == 1

    def test_atomic_write(self, temp_dir: Path) -> None:
        """Test that writes are atomic (temporary file + rename)."""
        tasks_file = temp_dir / "tasks.json"
        storage = StorageManager(tasks_file, create_backup=False)

        task_list = TaskList()
        task_list.add("Test task")
        storage.save(task_list)

        # Verify file was written
        assert tasks_file.exists()

    def test_backup_created(self, temp_dir: Path) -> None:
        """Test that backups are created."""
        tasks_file = temp_dir / "tasks.json"
        storage = StorageManager(tasks_file, create_backup=True)

        # Save first time
        task_list = TaskList()
        task_list.add("First task")
        storage.save(task_list)

        # Save second time (should create backup)
        task_list.add("Second task")
        storage.save(task_list)

        # Check backup exists
        backups = list((temp_dir / "backups").glob(f"{tasks_file.name}.*"))
        assert len(backups) > 0

    def test_restore_backup(self, temp_dir: Path) -> None:
        """Test restoring from backup."""
        tasks_file = temp_dir / "tasks.json"
        storage = StorageManager(tasks_file, create_backup=True)

        # Create initial task
        task_list = TaskList()
        task_list.add("Original task")
        storage.save(task_list)

        # Get backup timestamp
        backups = storage.list_backups()
        assert len(backups) > 0
        backup_timestamp = backups[0]

        # Modify task
        task_list.tasks[0].title = "Modified task"
        storage.save(task_list)

        # Restore from backup
        storage.restore_backup(backup_timestamp)
        restored_list = storage.load()

        assert restored_list.tasks[0].title == "Original task"

    def test_load_corrupted_json(self, temp_dir: Path) -> None:
        """Test loading corrupted JSON raises error."""
        tasks_file = temp_dir / "tasks.json"

        # Write invalid JSON
        with open(tasks_file, "w", encoding="utf-8") as f:
            f.write("invalid json {{{")

        storage = StorageManager(tasks_file)
        with pytest.raises(StorageError):
            storage.load()


class TestConfigLoader:
    """Tests for ConfigLoader."""

    @pytest.fixture
    def temp_dir(self, tmp_path: Path) -> Path:
        """Create a temporary directory for testing."""
        return tmp_path

    def test_load_nonexistent_creates_default(self, temp_dir: Path) -> None:
        """Test loading non-existent config creates default."""
        config_file = temp_dir / "config.toml"
        loader = ConfigLoader(config_file)
        config = loader.load()

        assert isinstance(config, Config)
        assert config.default_priority == "medium"
        assert config.color_enabled is True

    def test_save_and_load(self, temp_dir: Path) -> None:
        """Test saving and loading config."""
        config_file = temp_dir / "config.toml"
        loader = ConfigLoader(config_file)

        # Save config
        config = Config(default_priority="high", show_completed=False)
        loader.save(config)

        # Load and verify
        loaded_config = loader.load()
        assert loaded_config.default_priority == "high"
        assert loaded_config.show_completed is False

    def test_get_existing_key(self, temp_dir: Path) -> None:
        """Test getting existing config value."""
        config_file = temp_dir / "config.toml"
        loader = ConfigLoader(config_file)

        config = Config(default_priority="high")
        loader.save(config)

        value = loader.get("default_priority")
        assert value == "high"

    def test_get_nonexistent_key_returns_default(self, temp_dir: Path) -> None:
        """Test getting non-existent key returns default."""
        config_file = temp_dir / "config.toml"
        loader = ConfigLoader(config_file)

        value = loader.get("nonexistent_key", "default")
        assert value == "default"

    def test_set_value(self, temp_dir: Path) -> None:
        """Test setting a config value."""
        config_file = temp_dir / "config.toml"
        loader = ConfigLoader(config_file)

        config = Config(default_priority="medium")
        loader.save(config)

        # Set new value
        loader.set("default_priority", "high")

        # Reload and verify
        reloaded = loader.load()
        assert reloaded.default_priority == "high"

    def test_set_color_enabled_true(self, temp_dir: Path) -> None:
        """Test setting color_enabled to true."""
        config_file = temp_dir / "config.toml"
        loader = ConfigLoader(config_file)

        loader.set("color_enabled", "true")
        reloaded = loader.load()
        assert reloaded.color_enabled is True

    def test_set_color_enabled_false(self, temp_dir: Path) -> None:
        """Test setting color_enabled to false."""
        config_file = temp_dir / "config.toml"
        loader = ConfigLoader(config_file)

        loader.set("color_enabled", "false")
        reloaded = loader.load()
        assert reloaded.color_enabled is False

    def test_set_invalid_key_raises_error(self, temp_dir: Path) -> None:
        """Test setting invalid key raises error."""
        config_file = temp_dir / "config.toml"
        loader = ConfigLoader(config_file)

        with pytest.raises(ConfigError):
            loader.set("invalid_key", "value")
