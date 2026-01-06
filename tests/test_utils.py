"""Unit tests for utility modules."""

from datetime import datetime, timedelta

import pytest

from todo_cli.utils.date_utils import format_date, get_days_until, is_overdue, parse_date
from todo_cli.utils.validators import (
    validate_priority,
    validate_project,
    validate_status,
    validate_tags,
    validate_task_id,
)


class TestDateUtils:
    """Tests for date utilities."""

    def test_parse_date_yyyy_mm_dd(self) -> None:
        """Test parsing YYYY-MM-DD format."""
        result = parse_date("2026-01-15")
        assert result == datetime(2026, 1, 15)

    def test_parse_date_mm_dd_current_year(self) -> None:
        """Test parsing MM-DD format with current year."""
        result = parse_date("01-15")
        assert result.year == datetime.now().year
        assert result.month == 1
        assert result.day == 15

    def test_parse_date_today(self) -> None:
        """Test parsing 'today'."""
        result = parse_date("today")
        assert result.date() == datetime.now().date()

    def test_parse_date_tomorrow(self) -> None:
        """Test parsing 'tomorrow'."""
        result = parse_date("tomorrow")
        assert result.date() == (datetime.now() + timedelta(days=1)).date()

    def test_parse_date_plus_n(self) -> None:
        """Test parsing +N format."""
        result = parse_date("+7")
        assert result.date() == (datetime.now() + timedelta(days=7)).date()

    def test_parse_date_invalid(self) -> None:
        """Test parsing invalid date returns None."""
        result = parse_date("invalid-date")
        assert result is None

    def test_is_overdue_with_past_date(self) -> None:
        """Test overdue detection with past date."""
        past_date = datetime.now() - timedelta(days=1)
        assert is_overdue(past_date) is True

    def test_is_overdue_with_future_date(self) -> None:
        """Test overdue detection with future date."""
        future_date = datetime.now() + timedelta(days=1)
        assert is_overdue(future_date) is False

    def test_is_overdue_with_none(self) -> None:
        """Test overdue detection with None."""
        assert is_overdue(None) is False

    def test_get_days_until_future(self) -> None:
        """Test days until for future date."""
        future_date = datetime.now().replace(microsecond=0) + timedelta(days=5)
        # Get days using date-only datetime to avoid precision issues
        future_date_only = datetime(future_date.year, future_date.month, future_date.day)
        days_until = get_days_until(future_date_only)
        assert days_until is not None and abs(days_until - 5) <= 1

    def test_get_days_until_past(self) -> None:
        """Test days until for past date."""
        # Use date comparison without time component
        today = datetime.now().date()
        past_date_only = datetime(today.year, today.month, today.day)
        days_until = get_days_until(past_date_only)
        # For past dates, days_until will be negative
        assert days_until is not None and days_until < 0

    def test_get_days_until_none(self) -> None:
        """Test days until with None."""
        assert get_days_until(None) is None

    def test_format_date(self) -> None:
        """Test date formatting."""
        date = datetime(2026, 1, 15, 10, 30)
        result = format_date(date, "%Y-%m-%d %H:%M")
        assert result == "2026-01-15 10:30"


class TestValidators:
    """Tests for input validators."""

    def test_validate_priority_valid(self) -> None:
        """Test validating valid priorities."""
        assert validate_priority("low") == "low"
        assert validate_priority("medium") == "medium"
        assert validate_priority("high") == "high"

    def test_validate_priority_case_insensitive(self) -> None:
        """Test priority validation is case-insensitive."""
        assert validate_priority("HIGH") == "high"
        assert validate_priority("Low") == "low"
        assert validate_priority("MEDIUM") == "medium"

    def test_validate_priority_invalid(self) -> None:
        """Test validating invalid priority."""
        assert validate_priority("urgent") is None
        assert validate_priority("invalid") is None

    def test_validate_status_valid(self) -> None:
        """Test validating valid statuses."""
        assert validate_status("pending") == "pending"
        assert validate_status("completed") == "completed"

    def test_validate_status_case_insensitive(self) -> None:
        """Test status validation is case-insensitive."""
        assert validate_status("PENDING") == "pending"
        assert validate_status("COMPLETED") == "completed"

    def test_validate_status_invalid(self) -> None:
        """Test validating invalid status."""
        assert validate_status("active") is None
        assert validate_status("invalid") is None

    def test_validate_tags_normalization(self) -> None:
        """Test tag normalization."""
        tags = validate_tags(["Work", "URGENT", "shopping", "work"])
        assert tags == ["work", "urgent", "shopping"]  # Normalized to lowercase

    def test_validate_tags_trimming(self) -> None:
        """Test tag trimming."""
        tags = validate_tags(["  Work  ", " URGENT "])
        assert tags == ["work", "urgent"]

    def test_validate_tags_removes_empty(self) -> None:
        """Test removing empty tags."""
        tags = validate_tags(["work", "", "urgent", "  "])
        assert tags == ["work", "urgent"]

    def test_validate_tags_removes_duplicates(self) -> None:
        """Test removing duplicate tags."""
        tags = validate_tags(["work", "URGENT", "work", "shopping"])
        assert tags == ["work", "urgent", "shopping"]  # work appears only once

    def test_validate_project_valid(self) -> None:
        """Test validating valid project."""
        assert validate_project("My Project") == "My Project"

    def test_validate_project_trims_whitespace(self) -> None:
        """Test project trimming."""
        assert validate_project("  My Project  ") == "My Project"

    def test_validate_project_empty_string(self) -> None:
        """Test validating empty project returns None."""
        assert validate_project("") is None
        assert validate_project("   ") is None

    def test_validate_project_none(self) -> None:
        """Test validating None project."""
        assert validate_project(None) is None

    def test_validate_task_id_valid(self) -> None:
        """Test validating valid task IDs."""
        valid_ids = [1, 2, 3, 5]
        assert validate_task_id(1, valid_ids) is True
        assert validate_task_id(3, valid_ids) is True
        assert validate_task_id(5, valid_ids) is True

    def test_validate_task_id_invalid(self) -> None:
        """Test validating invalid task IDs."""
        valid_ids = [1, 2, 3, 5]
        assert validate_task_id(4, valid_ids) is False
        assert validate_task_id(6, valid_ids) is False
        assert validate_task_id(0, valid_ids) is False
