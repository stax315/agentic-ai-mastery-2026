"""
DateTimeAgent - A self-verifying datetime manipulation agent.

Day 2 of AI Mastery - Applying planning-first workflow to datetime operations.

Timezone Strategy: Naive datetimes (no timezone) - uses local system time.
Output Format: ISO 8601 (YYYY-MM-DD) for all date outputs.
"""

import re
from datetime import datetime, date, timedelta


class DateTimeAgent:
    """Agent for datetime manipulation with built-in verification."""

    def __init__(self) -> None:
        """Initialize the DateTimeAgent."""
        self.version = "1.0"
        # Supported date formats in priority order
        self._date_formats = [
            "%Y-%m-%d",      # ISO: 2024-01-15 (PRIORITY 1 - unambiguous)
            "%m/%d/%Y",      # US: 01/15/2024 (PRIORITY 2 - US assumption)
            "%B %d, %Y",     # Full: January 15, 2024
            "%b %d, %Y",     # Short: Jan 15, 2024
        ]

    def _validate_date_string(self, date_str, param_name: str = "date") -> None:
        """
        Validate that input is a non-empty string.

        Args:
            date_str: The value to validate
            param_name: Name of parameter for error messages

        Raises:
            ValueError: If input is not a valid non-empty string
        """
        if date_str is None:
            raise ValueError(f"{param_name} cannot be None")
        if type(date_str) is bool:
            raise ValueError(f"{param_name} must be a string, got bool")
        if not isinstance(date_str, str):
            raise ValueError(f"{param_name} must be a string, got {type(date_str).__name__}")
        if date_str.strip() == "":
            raise ValueError(f"{param_name} cannot be empty")

    def _validate_days(self, days) -> None:
        """
        Validate that days is an integer.

        Args:
            days: The value to validate

        Raises:
            ValueError: If days is not a valid integer
        """
        if days is None:
            raise ValueError("days cannot be None")
        if type(days) is bool:
            raise ValueError("days must be an integer, got bool")
        if not isinstance(days, int):
            raise ValueError(f"days must be an integer, got {type(days).__name__}")

    def _validate_format_string(self, format_string) -> None:
        """
        Validate that format_string is a non-empty string.

        Args:
            format_string: The value to validate

        Raises:
            ValueError: If format_string is not a valid non-empty string
        """
        if format_string is None:
            raise ValueError("format_string cannot be None")
        if type(format_string) is bool:
            raise ValueError("format_string must be a string, got bool")
        if not isinstance(format_string, str):
            raise ValueError(f"format_string must be a string, got {type(format_string).__name__}")
        if format_string.strip() == "":
            raise ValueError("format_string cannot be empty")

    def _parse_date(self, date_str: str) -> date:
        """
        Parse a date string using multiple formats.

        Tries formats in priority order:
        1. ISO 8601 (YYYY-MM-DD) - unambiguous, recommended
        2. US format (MM/DD/YYYY)
        3. Full written (January 15, 2024)
        4. Short written (Jan 15, 2024)

        Args:
            date_str: The date string to parse

        Returns:
            A date object

        Raises:
            ValueError: If the date cannot be parsed in any supported format
        """
        for fmt in self._date_formats:
            try:
                return datetime.strptime(date_str, fmt).date()
            except ValueError:
                continue
        raise ValueError(
            f"Cannot parse date: '{date_str}'. "
            f"Expected formats: YYYY-MM-DD, MM/DD/YYYY, 'Month DD, YYYY', or 'Mon DD, YYYY'"
        )

    def get_current_time(self) -> str:
        """
        Return the current local time as HH:MM:SS string.

        Returns:
            Current time in 24-hour format (e.g., "14:30:45")

        Note:
            Uses local system time (naive datetime, no timezone).
        """
        return datetime.now().strftime("%H:%M:%S")

    def get_current_date(self) -> str:
        """
        Return the current local date as YYYY-MM-DD string.

        Returns:
            Current date in ISO 8601 format (e.g., "2024-01-15")

        Note:
            Uses local system date (naive datetime, no timezone).
        """
        return date.today().isoformat()

    def add_days(self, date_str: str, days: int) -> str:
        """
        Add (or subtract if negative) days to a date.

        Args:
            date_str: The date to add days to (multiple formats supported)
            days: Number of days to add (negative for subtraction)

        Returns:
            The resulting date in ISO 8601 format (YYYY-MM-DD)

        Raises:
            ValueError: If date_str is invalid or days is not an integer

        Examples:
            add_days("2024-01-15", 5)   -> "2024-01-20"
            add_days("2024-01-15", -5)  -> "2024-01-10"
            add_days("01/15/2024", 5)   -> "2024-01-20"
        """
        self._validate_date_string(date_str, "date_str")
        self._validate_days(days)
        parsed_date = self._parse_date(date_str)
        result_date = parsed_date + timedelta(days=days)
        return result_date.isoformat()

    def days_between(self, date1: str, date2: str) -> int:
        """
        Calculate the number of days between two dates (date2 - date1).

        Args:
            date1: The first date (start date)
            date2: The second date (end date)

        Returns:
            Number of days between dates (positive if date2 > date1, negative otherwise)

        Raises:
            ValueError: If either date is invalid

        Examples:
            days_between("2024-01-15", "2024-01-20")  -> 5
            days_between("2024-01-20", "2024-01-15")  -> -5
            days_between("2024-01-15", "2024-01-15")  -> 0
        """
        self._validate_date_string(date1, "date1")
        self._validate_date_string(date2, "date2")
        d1 = self._parse_date(date1)
        d2 = self._parse_date(date2)
        return (d2 - d1).days

    def format_date(self, date_str: str, format_string: str) -> str:
        """
        Format a date string according to the given format.

        Args:
            date_str: The date to format (multiple input formats supported)
            format_string: Python strftime format string

        Returns:
            The formatted date string

        Raises:
            ValueError: If date_str or format_string is invalid

        Examples:
            format_date("2024-01-15", "%m/%d/%Y")      -> "01/15/2024"
            format_date("2024-01-15", "%B %d, %Y")     -> "January 15, 2024"
            format_date("2024-01-15", "%A")            -> "Monday"
        """
        self._validate_date_string(date_str, "date_str")
        self._validate_format_string(format_string)
        parsed_date = self._parse_date(date_str)
        return parsed_date.strftime(format_string)

    def verify(self) -> dict:
        """
        Run self-tests and return structured results.

        Returns:
            dict with keys: status, passed, failed, total, details
        """
        tests = [
            # get_current_time/date format tests
            ("current_time format",
             lambda: bool(re.match(r'\d{2}:\d{2}:\d{2}', self.get_current_time())),
             True, False),
            ("current_date format",
             lambda: bool(re.match(r'\d{4}-\d{2}-\d{2}', self.get_current_date())),
             True, False),

            # add_days tests
            ("add 5 days",
             lambda: self.add_days("2024-01-15", 5),
             "2024-01-20", False),
            ("subtract 5 days",
             lambda: self.add_days("2024-01-15", -5),
             "2024-01-10", False),
            ("add zero days",
             lambda: self.add_days("2024-01-15", 0),
             "2024-01-15", False),
            ("add across month",
             lambda: self.add_days("2024-01-29", 5),
             "2024-02-03", False),
            ("add across year",
             lambda: self.add_days("2024-12-30", 5),
             "2025-01-04", False),
            ("leap year feb 29",
             lambda: self.add_days("2024-02-28", 1),
             "2024-02-29", False),
            ("non-leap year feb 28",
             lambda: self.add_days("2023-02-28", 1),
             "2023-03-01", False),
            ("US format input",
             lambda: self.add_days("01/15/2024", 5),
             "2024-01-20", False),
            ("written format input",
             lambda: self.add_days("Jan 15, 2024", 5),
             "2024-01-20", False),

            # days_between tests
            ("days between positive",
             lambda: self.days_between("2024-01-15", "2024-01-20"),
             5, False),
            ("days between negative",
             lambda: self.days_between("2024-01-20", "2024-01-15"),
             -5, False),
            ("days between same",
             lambda: self.days_between("2024-01-15", "2024-01-15"),
             0, False),
            ("days between leap year",
             lambda: self.days_between("2024-01-01", "2024-12-31"),
             365, False),

            # format_date tests
            ("format to US",
             lambda: self.format_date("2024-01-15", "%m/%d/%Y"),
             "01/15/2024", False),
            ("format to written",
             lambda: self.format_date("2024-01-15", "%B %d, %Y"),
             "January 15, 2024", False),
            ("format to weekday",
             lambda: self.format_date("2024-01-15", "%A"),
             "Monday", False),

            # Error handling tests
            ("reject None date",
             lambda: self.add_days(None, 5),
             ValueError, True),
            ("reject invalid date",
             lambda: self.add_days("2024-02-30", 5),
             ValueError, True),
            ("reject non-leap feb29",
             lambda: self.days_between("2023-02-29", "2024-01-01"),
             ValueError, True),
            ("reject None days",
             lambda: self.add_days("2024-01-15", None),
             ValueError, True),
            ("reject float days",
             lambda: self.add_days("2024-01-15", 5.5),
             ValueError, True),
            ("reject empty string",
             lambda: self.add_days("", 5),
             ValueError, True),
        ]

        results = []
        passed = 0
        failed = 0

        for desc, func, expected, should_raise in tests:
            try:
                result = func()
                if should_raise:
                    results.append({
                        "test": desc,
                        "status": "FAIL",
                        "reason": "Expected error, got result"
                    })
                    failed += 1
                elif result == expected:
                    results.append({"test": desc, "status": "PASS"})
                    passed += 1
                else:
                    results.append({
                        "test": desc,
                        "status": "FAIL",
                        "expected": expected,
                        "got": result
                    })
                    failed += 1
            except Exception as e:
                if should_raise and isinstance(e, expected):
                    results.append({"test": desc, "status": "PASS"})
                    passed += 1
                else:
                    results.append({
                        "test": desc,
                        "status": "FAIL",
                        "error": str(e)
                    })
                    failed += 1

        return {
            "status": "PASS" if failed == 0 else "FAIL",
            "passed": passed,
            "failed": failed,
            "total": len(tests),
            "details": results
        }

    def verify_print(self) -> bool:
        """
        Run verification and print human-readable output.

        Returns:
            True if all tests pass, False otherwise
        """
        result = self.verify()
        print(f"\nDateTimeAgent v{self.version} Verification")
        print("=" * 50)
        for detail in result["details"]:
            status = "PASS" if detail["status"] == "PASS" else "FAIL"
            print(f"[{status}] {detail['test']}")
            if detail["status"] == "FAIL":
                if "expected" in detail:
                    print(f"        Expected: {detail['expected']}, Got: {detail['got']}")
                elif "error" in detail:
                    print(f"        Error: {detail['error']}")
                elif "reason" in detail:
                    print(f"        Reason: {detail['reason']}")
        print("=" * 50)
        print(f"Result: {result['passed']}/{result['total']} tests passed")
        print(f"Status: {result['status']}")
        return result["status"] == "PASS"


if __name__ == "__main__":
    agent = DateTimeAgent()
    agent.verify_print()
