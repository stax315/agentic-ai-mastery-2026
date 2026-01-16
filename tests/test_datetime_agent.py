"""
Tests for DateTimeAgent - Day 2 of AI Mastery.

Total: 51 tests covering all operations, date formats, edge cases, and error handling.
"""

import re
import pytest
from datetime import date
from datetime_agent import DateTimeAgent


@pytest.fixture
def agent():
    """Create a DateTimeAgent instance for testing."""
    return DateTimeAgent()


# =============================================================================
# get_current_time() Tests (3)
# =============================================================================

def test_current_time_format(agent):
    """Test that current time matches HH:MM:SS pattern."""
    result = agent.get_current_time()
    assert re.match(r'\d{2}:\d{2}:\d{2}', result), f"Expected HH:MM:SS, got {result}"


def test_current_time_is_string(agent):
    """Test that current time returns a string."""
    result = agent.get_current_time()
    assert isinstance(result, str)


def test_current_time_reasonable(agent):
    """Test that time values are in valid ranges."""
    result = agent.get_current_time()
    hours, minutes, seconds = map(int, result.split(':'))
    assert 0 <= hours <= 23, f"Hours out of range: {hours}"
    assert 0 <= minutes <= 59, f"Minutes out of range: {minutes}"
    assert 0 <= seconds <= 59, f"Seconds out of range: {seconds}"


# =============================================================================
# get_current_date() Tests (3)
# =============================================================================

def test_current_date_format(agent):
    """Test that current date matches YYYY-MM-DD pattern."""
    result = agent.get_current_date()
    assert re.match(r'\d{4}-\d{2}-\d{2}', result), f"Expected YYYY-MM-DD, got {result}"


def test_current_date_is_string(agent):
    """Test that current date returns a string."""
    result = agent.get_current_date()
    assert isinstance(result, str)


def test_current_date_reasonable(agent):
    """Test that date values are valid."""
    result = agent.get_current_date()
    year, month, day = map(int, result.split('-'))
    assert 2020 <= year <= 2100, f"Year out of expected range: {year}"
    assert 1 <= month <= 12, f"Month out of range: {month}"
    assert 1 <= day <= 31, f"Day out of range: {day}"


# =============================================================================
# add_days() Tests (15)
# =============================================================================

def test_add_days_positive(agent):
    """Test adding positive days."""
    assert agent.add_days("2024-01-15", 5) == "2024-01-20"


def test_add_days_negative(agent):
    """Test subtracting days (negative)."""
    assert agent.add_days("2024-01-15", -5) == "2024-01-10"


def test_add_days_zero(agent):
    """Test adding zero days returns same date."""
    assert agent.add_days("2024-01-15", 0) == "2024-01-15"


def test_add_days_month_boundary(agent):
    """Test adding days across month boundary."""
    assert agent.add_days("2024-01-29", 5) == "2024-02-03"


def test_add_days_year_boundary(agent):
    """Test adding days across year boundary."""
    assert agent.add_days("2024-12-30", 5) == "2025-01-04"


def test_add_days_leap_year(agent):
    """Test adding to Feb 28 in leap year goes to Feb 29."""
    assert agent.add_days("2024-02-28", 1) == "2024-02-29"


def test_add_days_non_leap_year(agent):
    """Test adding to Feb 28 in non-leap year goes to Mar 1."""
    assert agent.add_days("2023-02-28", 1) == "2023-03-01"


def test_add_days_us_format(agent):
    """Test adding days with US format input."""
    assert agent.add_days("01/15/2024", 5) == "2024-01-20"


def test_add_days_written_format(agent):
    """Test adding days with written format input."""
    assert agent.add_days("Jan 15, 2024", 5) == "2024-01-20"


def test_add_days_large_positive(agent):
    """Test adding a large number of days (1000+)."""
    assert agent.add_days("2024-01-01", 1000) == "2026-09-27"


def test_add_days_large_negative(agent):
    """Test subtracting a large number of days (1000+)."""
    # 2024-01-01 - 1000 days = 2021-04-06
    # (accounts for leap year 2024 and non-leap 2023, 2022, 2021)
    assert agent.add_days("2024-01-01", -1000) == "2021-04-06"


def test_add_days_none_date_raises(agent):
    """Test that None date raises ValueError."""
    with pytest.raises(ValueError) as exc_info:
        agent.add_days(None, 5)
    assert "cannot be None" in str(exc_info.value)


def test_add_days_none_days_raises(agent):
    """Test that None days raises ValueError."""
    with pytest.raises(ValueError) as exc_info:
        agent.add_days("2024-01-15", None)
    assert "cannot be None" in str(exc_info.value)


def test_add_days_invalid_date_raises(agent):
    """Test that unparseable date raises ValueError."""
    with pytest.raises(ValueError) as exc_info:
        agent.add_days("not a date", 5)
    assert "Cannot parse date" in str(exc_info.value)


def test_add_days_float_days_raises(agent):
    """Test that float days raises ValueError."""
    with pytest.raises(ValueError) as exc_info:
        agent.add_days("2024-01-15", 5.5)
    assert "must be an integer" in str(exc_info.value)
    assert "got float" in str(exc_info.value)


# =============================================================================
# days_between() Tests (12)
# =============================================================================

def test_days_between_positive(agent):
    """Test days between when date2 > date1 (positive result)."""
    assert agent.days_between("2024-01-15", "2024-01-20") == 5


def test_days_between_negative(agent):
    """Test days between when date2 < date1 (negative result)."""
    assert agent.days_between("2024-01-20", "2024-01-15") == -5


def test_days_between_same_date(agent):
    """Test days between same date is zero."""
    assert agent.days_between("2024-01-15", "2024-01-15") == 0


def test_days_between_year_boundary(agent):
    """Test days between spanning year boundary."""
    assert agent.days_between("2023-12-25", "2024-01-05") == 11


def test_days_between_leap_year(agent):
    """Test days in a leap year (366 days)."""
    assert agent.days_between("2024-01-01", "2024-12-31") == 365  # Dec 31 - Jan 1


def test_days_between_large(agent):
    """Test days between over 1000 days apart."""
    assert agent.days_between("2020-01-01", "2024-01-01") == 1461  # 4 years with leap


def test_days_between_mixed_formats(agent):
    """Test days between with different input formats."""
    assert agent.days_between("2024-01-15", "01/20/2024") == 5


def test_days_between_written_format(agent):
    """Test days between with written format."""
    assert agent.days_between("Jan 15, 2024", "Jan 20, 2024") == 5


def test_days_between_none_raises(agent):
    """Test that None date raises ValueError."""
    with pytest.raises(ValueError) as exc_info:
        agent.days_between(None, "2024-01-20")
    assert "cannot be None" in str(exc_info.value)


def test_days_between_invalid_raises(agent):
    """Test that invalid date raises ValueError."""
    with pytest.raises(ValueError) as exc_info:
        agent.days_between("2024-02-30", "2024-03-01")
    assert "Cannot parse date" in str(exc_info.value)


def test_days_between_empty_raises(agent):
    """Test that empty string raises ValueError."""
    with pytest.raises(ValueError) as exc_info:
        agent.days_between("", "2024-01-20")
    assert "cannot be empty" in str(exc_info.value)


def test_days_between_bool_raises(agent):
    """Test that boolean raises ValueError."""
    with pytest.raises(ValueError) as exc_info:
        agent.days_between(True, "2024-01-20")
    assert "must be a string" in str(exc_info.value)
    assert "got bool" in str(exc_info.value)


# =============================================================================
# format_date() Tests (8)
# =============================================================================

def test_format_date_to_us(agent):
    """Test formatting to US format."""
    assert agent.format_date("2024-01-15", "%m/%d/%Y") == "01/15/2024"


def test_format_date_to_written(agent):
    """Test formatting to full written format."""
    assert agent.format_date("2024-01-15", "%B %d, %Y") == "January 15, 2024"


def test_format_date_to_short(agent):
    """Test formatting to short written format."""
    assert agent.format_date("2024-01-15", "%b %d, %Y") == "Jan 15, 2024"


def test_format_date_weekday(agent):
    """Test formatting to weekday name."""
    assert agent.format_date("2024-01-15", "%A") == "Monday"


def test_format_date_from_us(agent):
    """Test formatting from US format input."""
    assert agent.format_date("01/15/2024", "%Y-%m-%d") == "2024-01-15"


def test_format_date_none_date_raises(agent):
    """Test that None date raises ValueError."""
    with pytest.raises(ValueError) as exc_info:
        agent.format_date(None, "%Y-%m-%d")
    assert "cannot be None" in str(exc_info.value)


def test_format_date_none_format_raises(agent):
    """Test that None format raises ValueError."""
    with pytest.raises(ValueError) as exc_info:
        agent.format_date("2024-01-15", None)
    assert "cannot be None" in str(exc_info.value)


def test_format_date_empty_format_raises(agent):
    """Test that empty format raises ValueError."""
    with pytest.raises(ValueError) as exc_info:
        agent.format_date("2024-01-15", "")
    assert "cannot be empty" in str(exc_info.value)


# =============================================================================
# Validation Tests (8)
# =============================================================================

def test_validate_none(agent):
    """Test that None is rejected with clear message."""
    with pytest.raises(ValueError) as exc_info:
        agent.add_days(None, 5)
    assert "cannot be None" in str(exc_info.value)


def test_validate_bool(agent):
    """Test that boolean is rejected with clear message."""
    with pytest.raises(ValueError) as exc_info:
        agent.add_days(True, 5)
    assert "must be a string" in str(exc_info.value)
    assert "got bool" in str(exc_info.value)


def test_validate_int(agent):
    """Test that integer is rejected with clear message."""
    with pytest.raises(ValueError) as exc_info:
        agent.add_days(123, 5)
    assert "must be a string" in str(exc_info.value)
    assert "got int" in str(exc_info.value)


def test_validate_empty(agent):
    """Test that empty string is rejected."""
    with pytest.raises(ValueError) as exc_info:
        agent.add_days("", 5)
    assert "cannot be empty" in str(exc_info.value)


def test_validate_whitespace(agent):
    """Test that whitespace-only string is rejected."""
    with pytest.raises(ValueError) as exc_info:
        agent.add_days("   ", 5)
    assert "cannot be empty" in str(exc_info.value)


def test_validate_invalid_date(agent):
    """Test that invalid date (Feb 30) is rejected."""
    with pytest.raises(ValueError) as exc_info:
        agent.add_days("2024-02-30", 5)
    assert "Cannot parse date" in str(exc_info.value)


def test_validate_non_leap_feb29(agent):
    """Test that Feb 29 in non-leap year is rejected."""
    with pytest.raises(ValueError) as exc_info:
        agent.add_days("2023-02-29", 5)
    assert "Cannot parse date" in str(exc_info.value)


def test_validate_invalid_month(agent):
    """Test that invalid month (13) is rejected."""
    with pytest.raises(ValueError) as exc_info:
        agent.add_days("2024-13-01", 5)
    assert "Cannot parse date" in str(exc_info.value)


# =============================================================================
# verify() Tests (2)
# =============================================================================

def test_verify_returns_dict(agent):
    """Test that verify() returns a dict with required keys."""
    result = agent.verify()
    assert isinstance(result, dict)
    assert "status" in result
    assert "passed" in result
    assert "failed" in result
    assert "total" in result
    assert "details" in result


def test_verify_all_pass(agent):
    """Test that verify() reports all tests passing."""
    result = agent.verify()
    assert result["status"] == "PASS"
    assert result["failed"] == 0
    assert result["passed"] == result["total"]
