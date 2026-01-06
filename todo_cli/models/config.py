"""Config model for user configuration."""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional


@dataclass
class Config:
    """
    User configuration for the todo application.

    Attributes:
        data_dir: Directory for storing tasks and config
        default_priority: Default priority for new tasks
        default_tags: Default tags to apply to new tasks
        show_completed: Whether to show completed tasks by default
        color_enabled: Whether color output is enabled
        date_format: Format string for displaying dates
        editor: Default text editor command
        sort_by: Default sort field
        sort_reverse: Default sort direction
        aliases: Custom command aliases
    """

    data_dir: Path = field(default_factory=lambda: Path.home() / ".todo")
    default_priority: str = "medium"
    default_tags: List[str] = field(default_factory=list)
    show_completed: bool = True
    color_enabled: bool = True
    date_format: str = "%Y-%m-%d"
    editor: Optional[str] = None
    sort_by: str = "priority"
    sort_reverse: bool = False
    aliases: Dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> Dict:
        """Convert config to dictionary for TOML serialization."""
        return {
            "data_dir": str(self.data_dir),
            "default_priority": self.default_priority,
            "default_tags": self.default_tags,
            "show_completed": self.show_completed,
            "color_enabled": self.color_enabled,
            "date_format": self.date_format,
            "editor": self.editor,
            "sort_by": self.sort_by,
            "sort_reverse": self.sort_reverse,
            "aliases": self.aliases,
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "Config":
        """Create Config from dictionary."""
        return cls(
            data_dir=Path(data.get("data_dir", Path.home() / ".todo")),
            default_priority=data.get("default_priority", "medium"),
            default_tags=data.get("default_tags", []),
            show_completed=data.get("show_completed", True),
            color_enabled=data.get("color_enabled", True),
            date_format=data.get("date_format", "%Y-%m-%d"),
            editor=data.get("editor"),
            sort_by=data.get("sort_by", "priority"),
            sort_reverse=data.get("sort_reverse", False),
            aliases=data.get("aliases", {}),
        )
