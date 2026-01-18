"""
CalculatorAgent - Mathematical operations with robust validation.

Day 3 - Reusing Day 1 patterns for rapid implementation.
"""

import math
from typing import Union

Number = Union[int, float]


class CalculatorAgent:
    """Calculator agent with 7 operations and comprehensive validation."""

    def __init__(self) -> None:
        """Initialize the CalculatorAgent."""
        self.version = "1.0"

    # =========================================================================
    # VALIDATION (Pattern 1, 5, 6 from CLAUDE.md)
    # =========================================================================

    def _validate_inputs(self, a, b=None) -> None:
        """Validate numeric inputs, rejecting booleans, NaN, Infinity."""
        for name, value in [("a", a), ("b", b)]:
            if value is None and name == "b":
                continue  # b is optional for single-arg operations
            if value is None:
                raise ValueError(f"{name} cannot be None")
            if type(value) is bool:
                raise ValueError(f"{name} must be a number, got bool")
            if type(value) not in (int, float):
                raise ValueError(f"{name} must be a number, got {type(value).__name__}")
            if isinstance(value, float):
                if math.isnan(value):
                    raise ValueError(f"{name} cannot be NaN")
                if math.isinf(value):
                    raise ValueError(f"{name} cannot be Infinity")

    def _check_result(self, result: float, operation: str) -> float:
        """Check result for overflow (Pattern 6)."""
        if math.isinf(result):
            raise ValueError(f"'{operation}' produced Infinity (overflow)")
        return result

    # =========================================================================
    # OPERATIONS
    # =========================================================================

    def add(self, a: Number, b: Number) -> float:
        """Add two numbers."""
        self._validate_inputs(a, b)
        result = float(a + b)
        return self._check_result(result, "add")

    def subtract(self, a: Number, b: Number) -> float:
        """Subtract b from a."""
        self._validate_inputs(a, b)
        result = float(a - b)
        return self._check_result(result, "subtract")

    def multiply(self, a: Number, b: Number) -> float:
        """Multiply two numbers."""
        self._validate_inputs(a, b)
        result = float(a * b)
        return self._check_result(result, "multiply")

    def divide(self, a: Number, b: Number) -> float:
        """Divide a by b."""
        self._validate_inputs(a, b)
        if b == 0:
            raise ValueError(f"Cannot divide {a} by zero")
        result = float(a / b)
        return self._check_result(result, "divide")

    def power(self, a: Number, b: Number) -> float:
        """Raise a to the power of b."""
        self._validate_inputs(a, b)
        if a < 0 and not float(b).is_integer():
            raise ValueError(f"Cannot raise negative number {a} to non-integer power {b}")
        result = float(a ** b)
        return self._check_result(result, "power")

    def modulo(self, a: Number, b: Number) -> float:
        """Return a modulo b."""
        self._validate_inputs(a, b)
        if b == 0:
            raise ValueError(f"Cannot calculate {a} modulo zero")
        return float(a % b)

    def sqrt(self, a: Number) -> float:
        """Return square root of a."""
        self._validate_inputs(a)
        if a < 0:
            raise ValueError(f"Cannot calculate square root of negative number {a}")
        return float(math.sqrt(a))

    # =========================================================================
    # VERIFICATION
    # =========================================================================

    def verify(self) -> dict:
        """Run self-tests."""
        tests = [
            ("add(2, 3) == 5.0", lambda: self.add(2, 3), 5.0, False),
            ("subtract(10, 4) == 6.0", lambda: self.subtract(10, 4), 6.0, False),
            ("multiply(3, 4) == 12.0", lambda: self.multiply(3, 4), 12.0, False),
            ("divide(15, 3) == 5.0", lambda: self.divide(15, 3), 5.0, False),
            ("power(2, 3) == 8.0", lambda: self.power(2, 3), 8.0, False),
            ("modulo(10, 3) == 1.0", lambda: self.modulo(10, 3), 1.0, False),
            ("sqrt(16) == 4.0", lambda: self.sqrt(16), 4.0, False),
            ("divide by zero raises", lambda: self.divide(5, 0), ValueError, True),
            ("sqrt(-1) raises", lambda: self.sqrt(-1), ValueError, True),
        ]

        details = []
        passed = 0

        for desc, op, expected, expects_error in tests:
            try:
                result = op()
                if expects_error:
                    details.append({"test": desc, "result": "FAIL", "reason": f"Expected error"})
                elif result == expected:
                    details.append({"test": desc, "result": "PASS"})
                    passed += 1
                else:
                    details.append({"test": desc, "result": "FAIL", "reason": f"Got {result}"})
            except Exception as e:
                if expects_error and isinstance(e, expected):
                    details.append({"test": desc, "result": "PASS"})
                    passed += 1
                else:
                    details.append({"test": desc, "result": "FAIL", "reason": str(e)})

        return {
            "status": "PASS" if passed == len(tests) else "FAIL",
            "tests_passed": passed,
            "tests_run": len(tests),
            "details": details
        }

    def verify_print(self) -> bool:
        """Print verification results."""
        result = self.verify()
        print("=" * 50)
        print(f"CalculatorAgent v{self.version} Self-Verification")
        print("=" * 50)
        for d in result["details"]:
            sym = "✓" if d["result"] == "PASS" else "✗"
            print(f"  {sym} {d['test']}")
        print("-" * 50)
        print(f"✓ Status: {result['status']} ({result['tests_passed']}/{result['tests_run']})")
        print("=" * 50)
        return result["status"] == "PASS"


if __name__ == "__main__":
    agent = CalculatorAgent()
    agent.verify_print()
