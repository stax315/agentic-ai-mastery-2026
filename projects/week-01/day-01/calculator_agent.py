"""
Calculator Agent - A self-verifying calculator
Day 1 - Learning to build agents with verification

This agent can perform math operations AND verify its own correctness.
"""


class CalculatorAgent:
    """
    A calculator that can test itself.

    Methods:
        add(a, b): Add two numbers
        subtract(a, b): Subtract b from a
        multiply(a, b): Multiply two numbers
        divide(a, b): Divide a by b
        verify(): Run self-tests and report results
    """

    def __init__(self) -> None:
        """Initialize the calculator agent."""
        pass  # No setup needed for now

    def _validate_inputs(self, a, b) -> None:
        """
        Validate that both inputs are numbers (int or float, NOT bool).

        Args:
            a: First input to validate
            b: Second input to validate

        Raises:
            ValueError: If either input is not a number
        """
        # Check type exactly - this excludes booleans!
        # (isinstance(True, int) is True, but type(True) is bool)
        if type(a) not in (int, float):
            raise ValueError(f"First argument must be a number, got {type(a).__name__}")
        if type(b) not in (int, float):
            raise ValueError(f"Second argument must be a number, got {type(b).__name__}")

    def add(self, a: float, b: float) -> float:
        """
        Add two numbers.

        Args:
            a: First number
            b: Second number

        Returns:
            Sum of a and b as a float

        Raises:
            ValueError: If inputs are not numbers
        """
        self._validate_inputs(a, b)
        return float(a + b)

    def subtract(self, a: float, b: float) -> float:
        """
        Subtract b from a.

        Args:
            a: Number to subtract from
            b: Number to subtract

        Returns:
            Difference (a - b) as a float

        Raises:
            ValueError: If inputs are not numbers
        """
        self._validate_inputs(a, b)
        return float(a - b)

    def multiply(self, a: float, b: float) -> float:
        """
        Multiply two numbers.

        Args:
            a: First number
            b: Second number

        Returns:
            Product of a and b as a float

        Raises:
            ValueError: If inputs are not numbers
        """
        self._validate_inputs(a, b)
        return float(a * b)

    def divide(self, a: float, b: float) -> float:
        """
        Divide a by b.

        Args:
            a: Dividend (number to be divided)
            b: Divisor (number to divide by)

        Returns:
            Quotient (a / b) as a float

        Raises:
            ValueError: If inputs are not numbers OR if b is zero
        """
        self._validate_inputs(a, b)
        if b == 0:
            raise ValueError("Cannot divide by zero")
        return float(a / b)

    def verify(self) -> dict:
        """
        Run self-tests and report results.

        This is what makes this a self-verifying agent - it can test
        its own correctness and report the results.

        Returns:
            A dictionary with:
            - status: "PASS" if all tests pass, "FAIL" otherwise
            - tests_run: Number of tests executed
            - tests_passed: Number of tests that passed
            - tests_failed: Number of tests that failed
            - details: List of individual test results
        """
        # Define all the tests to run
        tests = [
            # (description, operation, expected_result, expects_error)
            ("add(2, 3) == 5.0", lambda: self.add(2, 3), 5.0, False),
            ("add(-1, 1) == 0.0", lambda: self.add(-1, 1), 0.0, False),
            ("add(1.5, 2.5) == 4.0", lambda: self.add(1.5, 2.5), 4.0, False),
            ("subtract(10, 4) == 6.0", lambda: self.subtract(10, 4), 6.0, False),
            ("subtract(5, 10) == -5.0", lambda: self.subtract(5, 10), -5.0, False),
            ("multiply(3, 4) == 12.0", lambda: self.multiply(3, 4), 12.0, False),
            ("multiply(-2, 3) == -6.0", lambda: self.multiply(-2, 3), -6.0, False),
            ("multiply(5, 0) == 0.0", lambda: self.multiply(5, 0), 0.0, False),
            ("divide(10, 2) == 5.0", lambda: self.divide(10, 2), 5.0, False),
            ("divide(7, 2) == 3.5", lambda: self.divide(7, 2), 3.5, False),
            ("divide(10, 0) raises ValueError", lambda: self.divide(10, 0), None, True),
            ("add('5', 3) raises ValueError", lambda: self.add("5", 3), None, True),
        ]

        details = []
        tests_passed = 0
        tests_failed = 0

        for description, operation, expected, expects_error in tests:
            try:
                result = operation()

                if expects_error:
                    # We expected an error but didn't get one
                    details.append({"test": description, "result": "FAIL", "reason": "Expected error, got result"})
                    tests_failed += 1
                elif result == expected:
                    details.append({"test": description, "result": "PASS"})
                    tests_passed += 1
                else:
                    details.append({"test": description, "result": "FAIL", "reason": f"Expected {expected}, got {result}"})
                    tests_failed += 1

            except ValueError:
                if expects_error:
                    details.append({"test": description, "result": "PASS"})
                    tests_passed += 1
                else:
                    details.append({"test": description, "result": "FAIL", "reason": "Unexpected error"})
                    tests_failed += 1

            except Exception as e:
                details.append({"test": description, "result": "FAIL", "reason": str(e)})
                tests_failed += 1

        return {
            "status": "PASS" if tests_failed == 0 else "FAIL",
            "tests_run": len(tests),
            "tests_passed": tests_passed,
            "tests_failed": tests_failed,
            "details": details
        }
