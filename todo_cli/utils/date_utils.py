"""Date utilities for parsing and formatting dates."""

from datetime import datetime, timedelta
from typing import Optional


def parse_date(date_str: str) -> Optional[datetime]:
    """
    Parse date string into datetime object.

    Supported formats:
    - YYYY-MM-DD
    - MM-DD
    - today
    - tomorrow
    - +N (N days from now)

    Args:
        date_str: Date string to parse.

    Returns:
        Datetime object or None if parsing fails.
    """
    date_str = date_str.lower().strip()
    now = datetime.now()
    today = now.date()

    # Natural language dates
    if date_str == "today":
        return datetime.combine(today, datetime.min.time())
    elif date_str == "tomorrow":
        tomorrow = today + timedelta(days=1)
        return datetime.combine(tomorrow, datetime.min.time())

    # Relative dates (+N)
    if date_str.startswith("+"):
        try:
            days = int(date_str[1:])
            target_date = today + timedelta(days=days)
            return datetime.combine(target_date, datetime.min.time())
        except ValueError:
            return None

    # YYYY-MM-DD format
    try:
        return datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        pass

    # MM-DD format (current year)
    try:
        date_without_year = datetime.strptime(date_str, "%m-%d")
        target_date = date_without_year.replace(year=now.year)

        # If date has passed this year, use next year
        if target_date.date() < today:
            target_date = target_date.replace(year=now.year + 1)

        return target_date
    except ValueError:
        pass

    return None


def format_date(dt: datetime, format_str: str = "%Y-%m-%d") -> str:
    """
    Format datetime object as string.

    Args:
        dt: Datetime object.
        format_str: Format string.

    Returns:
        Formatted date string.
    """
    return dt.strftime(format_str)


def is_overdue(due_date: Optional[datetime]) -> bool:
    """
    Check if a due date is overdue.

    Args:
        due_date: Due date to check.

    Returns:
        True if overdue, False otherwise.
    """
    if due_date is None:
        return False
    return datetime.now() > due_date


def get_days_until(due_date: Optional[datetime]) -> Optional[int]:
    """
    Get number of days until due date.

    Args:
        due_date: Due date.

    Returns:
        Number of days until due, None if no due date.
    """
    if due_date is None:
        return None

    delta = (due_date - datetime.now()).days
    return delta
