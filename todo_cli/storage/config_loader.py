"""Config loader for TOML configuration files."""

from pathlib import Path
from typing import Optional

import tomli
import tomli_w

from todo_cli.models.config import Config


class ConfigError(Exception):
    """Configuration-related errors."""

    pass


class ConfigLoader:
    """Manages configuration loading and saving."""

    DEFAULT_CONFIG: Config = Config()

    def __init__(self, config_path: Optional[Path] = None) -> None:
        """
        Initialize config loader.

        Args:
            config_path: Path to config file. Defaults to ~/.todo/config.toml
        """
        self.config_path: Path = config_path or Path.home() / ".todo" / "config.toml"
        self._config: Optional[Config] = None

    def load(self) -> Config:
        """
        Load configuration from file.

        Returns:
            Config object with loaded settings.
        """
        if self._config is not None:
            return self._config

        if not self.config_path.exists():
            self._config = self.DEFAULT_CONFIG
            return self._config

        try:
            with open(self.config_path, "rb") as f:
                data = tomli.load(f)
            self._config = Config.from_dict(data)
        except Exception as e:
            raise ConfigError(f"Failed to load config: {e}")

        return self._config

    def save(self, config: Config) -> None:
        """
        Save configuration to file.

        Args:
            config: Config object to save.
        """
        try:
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_path, "wb") as f:
                tomli_w.dump(config.to_dict(), f)
            self._config = config
        except Exception as e:
            raise ConfigError(f"Failed to save config: {e}")

    def get(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """
        Get a configuration value by key.

        Args:
            key: Configuration key.
            default: Default value if key not found.

        Returns:
            Configuration value or default.
        """
        config = self.load()
        value: Optional[str] = None

        if key == "default_priority":
            value = config.default_priority
        elif key == "editor":
            value = config.editor
        elif key == "date_format":
            value = config.date_format
        elif key == "sort_by":
            value = config.sort_by
        elif key == "color_enabled":
            value = "true" if config.color_enabled else "false"

        return value or default

    def set(self, key: str, value: str) -> None:
        """
        Set a configuration value.

        Args:
            key: Configuration key.
            value: Configuration value.
        """
        config = self.load()

        if key == "default_priority":
            config.default_priority = value
        elif key == "editor":
            config.editor = value if value else None
        elif key == "date_format":
            config.date_format = value
        elif key == "sort_by":
            config.sort_by = value
        elif key == "color_enabled":
            config.color_enabled = value.lower() in ("true", "1", "yes")
        else:
            raise ConfigError(f"Unknown configuration key: {key}")

        self.save(config)
