"""
Calculator Agent v2 - Production-Ready Self-Verifying Calculator
Day 1 - Improved version based on code review

Changes from v1:
- Rejects NaN and Infinity (prevents silent bug propagation)
- Better error messages for edge cases
- Added verify_print() for readable output
- Added power(), modulo(), sqrt() operations
- More comprehensive self-tests
"""

import math


class CalculatorAgent:
    """
    A production-ready calculator that can test itself.

    v2 Improvements:
    - Rejects special floats (NaN, Infinity) to prevent silent bugs
    - Better error messages with context
    - Pretty-printed verification output
    - Additional operations: power, modulo, sqrt

    Methods:
        add(a, b): Add two numbers
        subtract(a, b): Subtract b from a
        multiply(a, b): Multiply two numbers
        divide(a, b): Divide a by b
        power(base, exp): Raise base to exponent
        modulo(a, b): Remainder of a divided by b
        sqrt(a): Square root of a
        verify(): Run self-tests and return results dict
        verify_print(): Run self-tests and print readable output
    """

    # Maximum safe float value
    MAX_FLOAT = 1.7976931348623157e+308

    def __init__(self) -> None:
        """Initialize the calculator agent."""
        self.version = "2.0"

    def _validate_inputs(self, a, b=None) -> None:
        """
        Validate that inputs are valid numbers.

        Rejects:
        - Non-numeric types (strings, None, lists, booleans)
        - Special floats (NaN, Infinity, -Infinity)
        - Numbers that exceed float limits

        Args:
            a: First input to validate
            b: Second input to validate (optional for single-arg methods)

        Raises:
            ValueError: If any input is invalid
        """
        inputs = [("First", a)]
        if b is not None:
            inputs.append(("Second", b))

        for position, value in inputs:
            # Check type - excludes booleans
            if type(value) not in (int, float):
                raise ValueError(
                    f"{position} argument must be a number, got {type(value).__name__}"
                )

            # Check for NaN
            if isinstance(value, float) and math.isnan(value):
                raise ValueError(
                    f"{position} argument cannot be NaN (Not a Number)"
                )

            # Check for Infinity
            if isinstance(value, float) and math.isinf(value):
                raise ValueError(
                    f"{position} argument cannot be Infinity"
                )

            # Check for overflow risk (very large integers)
            if isinstance(value, int) and abs(value) > self.MAX_FLOAT:
                raise ValueError(
                    f"{position} argument too large: {value} exceeds maximum float value"
                )

    def _check_result(self, result: float, operation: str) -> float:
        """
        Validate the result of an operation.

        Catches overflow and invalid results that Python allows.

        Args:
            result: The computed result
            operation: Description of operation for error message

        Returns:
            The result if valid

        Raises:
            ValueError: If result is NaN or Infinity
        """
        if math.isnan(result):
            raise ValueError(
                f"Operation '{operation}' produced NaN (undefined result)"
            )
        if math.isinf(result):
            raise ValueError(
                f"Operation '{operation}' produced Infinity (overflow)"
            )
        return result

    def add(self, a: float, b: float) -> float:
        """
        Add two numbers.

        Args:
            a: First number
            b: Second number

        Returns:
            Sum of a and b as a float

        Raises:
            ValueError: If inputs invalid or result overflows
        """
        self._validate_inputs(a, b)
        result = float(a + b)
        return self._check_result(result, f"{a} + {b}")

    def subtract(self, a: float, b: float) -> float:
        """
        Subtract b from a.

        Args:
            a: Number to subtract from
            b: Number to subtract

        Returns:
            Difference (a - b) as a float

        Raises:
            ValueError: If inputs invalid or result overflows
        """
        self._validate_inputs(a, b)
        result = float(a - b)
        return self._check_result(result, f"{a} - {b}")

    def multiply(self, a: float, b: float) -> float:
        """
        Multiply two numbers.

        Args:
            a: First number
            b: Second number

        Returns:
            Product of a and b as a float

        Raises:
            ValueError: If inputs invalid or result overflows
        """
        self._validate_inputs(a, b)
        result = float(a * b)
        return self._check_result(result, f"{a} * {b}")

    def divide(self, a: float, b: float) -> float:
        """
        Divide a by b.

        Args:
            a: Dividend (number to be divided)
            b: Divisor (number to divide by)

        Returns:
            Quotient (a / b) as a float

        Raises:
            ValueError: If inputs invalid, b is zero, or result overflows
        """
        self._validate_inputs(a, b)
        if b == 0:
            raise ValueError(f"Cannot divide {a} by zero")
        result = float(a / b)
        return self._check_result(result, f"{a} / {b}")

    def power(self, base: float, exponent: float) -> float:
        """
        Raise base to the power of exponent.

        Args:
            base: The base number
            exponent: The exponent

        Returns:
            base raised to exponent as a float

        Raises:
            ValueError: If inputs invalid or result overflows
        """
        self._validate_inputs(base, exponent)

        # Special case: negative base with non-integer exponent
        if base < 0 and exponent != int(exponent):
            raise ValueError(
                f"Cannot raise negative number {base} to non-integer power {exponent}"
            )

        try:
            result = float(base ** exponent)
        except OverflowError:
            raise ValueError(
                f"Result of {base} ** {exponent} is too large"
            )

        return self._check_result(result, f"{base} ** {exponent}")

    def modulo(self, a: float, b: float) -> float:
        """
        Return remainder of a divided by b.

        Args:
            a: Dividend
            b: Divisor

        Returns:
            Remainder of a / b as a float

        Raises:
            ValueError: If inputs invalid or b is zero
        """
        self._validate_inputs(a, b)
        if b == 0:
            raise ValueError(f"Cannot compute {a} modulo zero")
        result = float(a % b)
        return self._check_result(result, f"{a} % {b}")

    def sqrt(self, a: float) -> float:
        """
        Return square root of a.

        Args:
            a: Number to take square root of (must be non-negative)

        Returns:
            Square root of a as a float

        Raises:
            ValueError: If a is negative or invalid
        """
        self._validate_inputs(a)
        if a < 0:
            raise ValueError(
                f"Cannot compute square root of negative number: {a}"
            )
        result = float(math.sqrt(a))
        return self._check_result(result, f"sqrt({a})")

    def verify(self) -> dict:
        """
        Run self-tests and return results as a dictionary.

        Returns:
            A dictionary with:
            - status: "PASS" if all tests pass, "FAIL" otherwise
            - tests_run: Number of tests executed
            - tests_passed: Number of tests that passed
            - tests_failed: Number of tests that failed
            - details: List of individual test results
        """
        tests = [
            # Basic operations
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

            # New operations (v2)
            ("power(2, 3) == 8.0", lambda: self.power(2, 3), 8.0, False),
            ("power(2, -1) == 0.5", lambda: self.power(2, -1), 0.5, False),
            ("modulo(10, 3) == 1.0", lambda: self.modulo(10, 3), 1.0, False),
            ("sqrt(16) == 4.0", lambda: self.sqrt(16), 4.0, False),
            ("sqrt(2) ~= 1.414", lambda: round(self.sqrt(2), 3), 1.414, False),

            # Error cases
            ("divide(10, 0) raises ValueError", lambda: self.divide(10, 0), None, True),
            ("add('5', 3) raises ValueError", lambda: self.add("5", 3), None, True),
            ("sqrt(-1) raises ValueError", lambda: self.sqrt(-1), None, True),

            # v2: Special float rejection
            ("add(nan, 1) raises ValueError", lambda: self.add(float('nan'), 1), None, True),
            ("add(inf, 1) raises ValueError", lambda: self.add(float('inf'), 1), None, True),
            ("add(True, 1) raises ValueError", lambda: self.add(True, 1), None, True),
        ]

        details = []
        tests_passed = 0
        tests_failed = 0

        for description, operation, expected, expects_error in tests:
            try:
                result = operation()

                if expects_error:
                    details.append({
                        "test": description,
                        "result": "FAIL",
                        "reason": "Expected error, got result"
                    })
                    tests_failed += 1
                elif result == expected:
                    details.append({"test": description, "result": "PASS"})
                    tests_passed += 1
                else:
                    details.append({
                        "test": description,
                        "result": "FAIL",
                        "reason": f"Expected {expected}, got {result}"
                    })
                    tests_failed += 1

            except ValueError:
                if expects_error:
                    details.append({"test": description, "result": "PASS"})
                    tests_passed += 1
                else:
                    details.append({
                        "test": description,
                        "result": "FAIL",
                        "reason": "Unexpected ValueError"
                    })
                    tests_failed += 1

            except Exception as e:
                details.append({
                    "test": description,
                    "result": "FAIL",
                    "reason": str(e)
                })
                tests_failed += 1

        return {
            "status": "PASS" if tests_failed == 0 else "FAIL",
            "tests_run": len(tests),
            "tests_passed": tests_passed,
            "tests_failed": tests_failed,
            "details": details
        }

    def verify_print(self) -> bool:
        """
        Run self-tests and print readable output.

        Returns:
            True if all tests pass, False otherwise
        """
        result = self.verify()

        print("=" * 50)
        print(f"CalculatorAgent v{self.version} Self-Verification")
        print("=" * 50)
        print()

        for detail in result["details"]:
            symbol = "✓" if detail["result"] == "PASS" else "✗"
            print(f"  {symbol} {detail['test']}")
            if detail["result"] == "FAIL" and "reason" in detail:
                print(f"      Reason: {detail['reason']}")

        print()
        print("-" * 50)
        status_symbol = "✓" if result["status"] == "PASS" else "✗"
        print(f"{status_symbol} Status: {result['status']}")
        print(f"  Tests: {result['tests_passed']}/{result['tests_run']} passed")

        if result["tests_failed"] > 0:
            print(f"  Failed: {result['tests_failed']}")

        print("=" * 50)

        return result["status"] == "PASS"
