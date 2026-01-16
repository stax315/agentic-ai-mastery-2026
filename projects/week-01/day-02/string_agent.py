"""
StringAgent - A self-verifying string manipulation agent.

Day 2 of AI Mastery - Applying planning-first workflow to string operations.
"""


class StringAgent:
    """Agent for string manipulation with built-in verification."""

    def __init__(self) -> None:
        """Initialize the StringAgent."""
        self.version = "1.0"

    def _validate_input(self, text, param_name: str = "text") -> None:
        """
        Validate that input is a string.

        Rejects None, booleans, and non-string types with descriptive errors.

        Args:
            text: The value to validate
            param_name: Name of parameter for error messages

        Raises:
            ValueError: If input is not a valid string
        """
        if text is None:
            raise ValueError(f"{param_name} cannot be None")
        if type(text) is bool:  # Check BEFORE isinstance - booleans are not strings!
            raise ValueError(f"{param_name} must be a string, got bool")
        if not isinstance(text, str):
            raise ValueError(f"{param_name} must be a string, got {type(text).__name__}")

    def reverse_string(self, text: str) -> str:
        """
        Reverse the characters in a string.

        Args:
            text: The string to reverse

        Returns:
            The reversed string

        Raises:
            ValueError: If text is not a valid string
        """
        self._validate_input(text)
        return text[::-1]

    def to_uppercase(self, text: str) -> str:
        """
        Convert all characters to uppercase.

        Args:
            text: The string to convert

        Returns:
            The uppercase string

        Raises:
            ValueError: If text is not a valid string
        """
        self._validate_input(text)
        return text.upper()

    def to_lowercase(self, text: str) -> str:
        """
        Convert all characters to lowercase.

        Args:
            text: The string to convert

        Returns:
            The lowercase string

        Raises:
            ValueError: If text is not a valid string
        """
        self._validate_input(text)
        return text.lower()

    def count_words(self, text: str) -> int:
        """
        Count the number of words in a string.

        A word is defined as a maximal contiguous sequence of non-whitespace characters.
        Uses str.split() which handles all whitespace types (space, tab, newline).

        Args:
            text: The string to count words in

        Returns:
            The number of words (0 for empty or whitespace-only strings)

        Raises:
            ValueError: If text is not a valid string
        """
        self._validate_input(text)
        return len(text.split())

    def remove_spaces(self, text: str) -> str:
        """
        Remove all whitespace characters from a string.

        Removes spaces, tabs, newlines, and all other whitespace.

        Args:
            text: The string to remove whitespace from

        Returns:
            The string with all whitespace removed

        Raises:
            ValueError: If text is not a valid string
        """
        self._validate_input(text)
        return "".join(text.split())

    def verify(self) -> dict:
        """
        Run self-tests and return structured results.

        Returns:
            dict with keys: status, passed, failed, total, details
        """
        tests = [
            # (description, lambda, expected, should_raise)
            # reverse_string tests
            ("reverse 'hello'", lambda: self.reverse_string("hello"), "olleh", False),
            ("reverse empty", lambda: self.reverse_string(""), "", False),
            ("reverse palindrome", lambda: self.reverse_string("racecar"), "racecar", False),
            # to_uppercase tests
            ("uppercase 'hello'", lambda: self.to_uppercase("hello"), "HELLO", False),
            ("uppercase empty", lambda: self.to_uppercase(""), "", False),
            ("uppercase mixed", lambda: self.to_uppercase("HeLLo"), "HELLO", False),
            # to_lowercase tests
            ("lowercase 'HELLO'", lambda: self.to_lowercase("HELLO"), "hello", False),
            ("lowercase empty", lambda: self.to_lowercase(""), "", False),
            ("lowercase mixed", lambda: self.to_lowercase("HeLLo"), "hello", False),
            # count_words tests
            ("count 'a b c'", lambda: self.count_words("a b c"), 3, False),
            ("count empty", lambda: self.count_words(""), 0, False),
            ("count whitespace only", lambda: self.count_words("   "), 0, False),
            ("count contraction", lambda: self.count_words("don't"), 1, False),
            ("count hyphenated", lambda: self.count_words("well-known"), 1, False),
            # remove_spaces tests
            ("remove spaces 'a b'", lambda: self.remove_spaces("a b"), "ab", False),
            ("remove spaces empty", lambda: self.remove_spaces(""), "", False),
            ("remove tabs", lambda: self.remove_spaces("a\tb"), "ab", False),
            ("remove mixed whitespace", lambda: self.remove_spaces("a \t\n b"), "ab", False),
            # Error handling tests
            ("reject None", lambda: self.reverse_string(None), ValueError, True),
            ("reject bool", lambda: self.count_words(True), ValueError, True),
            ("reject int", lambda: self.to_uppercase(123), ValueError, True),
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
        print(f"\nStringAgent v{self.version} Verification")
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
    agent = StringAgent()
    agent.verify_print()
