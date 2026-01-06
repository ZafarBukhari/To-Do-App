"""Input validation utilities."""

from typing import List, Optional

from todo_cli.models.task import TaskPriority, TaskStatus


def validate_priority(priority: str) -> Optional[str]:
    """
    Validate priority value.

    Args:
        priority: Priority string to validate.

    Returns:
        Validated priority or None if invalid.
    """
    try:
        return TaskPriority(priority.lower()).value
    except ValueError:
        return None


def validate_status(status: str) -> Optional[str]:
    """
    Validate status value.

    Args:
        status: Status string to validate.

    Returns:
        Validated status or None if invalid.
    """
    try:
        return TaskStatus(status.lower()).value
    except ValueError:
        return None


def validate_tags(tags: List[str]) -> List[str]:
    """
    Validate and normalize tag list.

    Args:
        tags: List of tag strings.

    Returns:
        Normalized list of tags (lowercase, trimmed, no duplicates).
    """
    # Normalize: lowercase, trim, remove empty, remove duplicates
    normalized = []
    seen = set()

    for tag in tags:
        tag = tag.strip().lower()
        if tag and tag not in seen:
            normalized.append(tag)
            seen.add(tag)

    return normalized


def validate_project(project: Optional[str]) -> Optional[str]:
    """
    Validate project name.

    Args:
        project: Project name to validate.

    Returns:
        Validated project name or None if invalid/empty.
    """
    if project is None:
        return None

    project = project.strip()
    return project if project else None


def validate_task_id(task_id: int, valid_ids: List[int]) -> bool:
    """
    Validate that task ID exists.

    Args:
        task_id: Task ID to validate.
        valid_ids: List of valid task IDs.

    Returns:
        True if valid, False otherwise.
    """
    return task_id in valid_ids
