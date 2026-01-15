"""
Tests for Calculator Agent v2
Day 1 - Production-ready tests including edge cases

Run with: python3 -m pytest test_calculator_agent_v2.py -v
"""

import math
import pytest
from calculator_agent_v2 import CalculatorAgent


# =============================================================================
# VALIDATION TESTS
# =============================================================================

class TestValidation:
    """Tests for input validation."""

    def test_rejects_string(self):
        """Strings should be rejected."""
        calc = CalculatorAgent()
        with pytest.raises(ValueError, match="must be a number"):
            calc.add("5", 3)

    def test_rejects_none(self):
        """None should be rejected."""
        calc = CalculatorAgent()
        with pytest.raises(ValueError, match="must be a number"):
            calc.add(None, 3)

    def test_rejects_boolean(self):
        """Booleans should be rejected."""
        calc = CalculatorAgent()
        with pytest.raises(ValueError, match="must be a number"):
            calc.add(True, 3)

    def test_rejects_list(self):
        """Lists should be rejected."""
        calc = CalculatorAgent()
        with pytest.raises(ValueError, match="must be a number"):
            calc.add([1, 2], 3)

    def test_rejects_nan(self):
        """NaN should be rejected (v2 improvement)."""
        calc = CalculatorAgent()
        with pytest.raises(ValueError, match="cannot be NaN"):
            calc.add(float('nan'), 1)

    def test_rejects_infinity(self):
        """Infinity should be rejected (v2 improvement)."""
        calc = CalculatorAgent()
        with pytest.raises(ValueError, match="cannot be Infinity"):
            calc.add(float('inf'), 1)

    def test_rejects_negative_infinity(self):
        """Negative infinity should be rejected."""
        calc = CalculatorAgent()
        with pytest.raises(ValueError, match="cannot be Infinity"):
            calc.add(float('-inf'), 1)

    def test_accepts_integers(self):
        """Valid integers should be accepted."""
        calc = CalculatorAgent()
        result = calc.add(5, 3)
        assert result == 8.0

    def test_accepts_floats(self):
        """Valid floats should be accepted."""
        calc = CalculatorAgent()
        result = calc.add(5.5, 3.3)
        assert result == 8.8


# =============================================================================
# ADD TESTS
# =============================================================================

class TestAdd:
    """Tests for add operation."""

    def test_positive_numbers(self):
        calc = CalculatorAgent()
        assert calc.add(2, 3) == 5.0

    def test_negative_numbers(self):
        calc = CalculatorAgent()
        assert calc.add(-1, -2) == -3.0

    def test_mixed_signs(self):
        calc = CalculatorAgent()
        assert calc.add(-1, 1) == 0.0

    def test_floats(self):
        calc = CalculatorAgent()
        assert calc.add(1.5, 2.5) == 4.0

    def test_returns_float(self):
        calc = CalculatorAgent()
        result = calc.add(2, 3)
        assert isinstance(result, float)


# =============================================================================
# SUBTRACT TESTS
# =============================================================================

class TestSubtract:
    """Tests for subtract operation."""

    def test_basic(self):
        calc = CalculatorAgent()
        assert calc.subtract(10, 4) == 6.0

    def test_negative_result(self):
        calc = CalculatorAgent()
        assert calc.subtract(5, 10) == -5.0

    def test_same_numbers(self):
        calc = CalculatorAgent()
        assert calc.subtract(5, 5) == 0.0


# =============================================================================
# MULTIPLY TESTS
# =============================================================================

class TestMultiply:
    """Tests for multiply operation."""

    def test_basic(self):
        calc = CalculatorAgent()
        assert calc.multiply(3, 4) == 12.0

    def test_by_zero(self):
        calc = CalculatorAgent()
        assert calc.multiply(5, 0) == 0.0

    def test_negatives(self):
        calc = CalculatorAgent()
        assert calc.multiply(-2, -3) == 6.0

    def test_mixed_signs(self):
        calc = CalculatorAgent()
        assert calc.multiply(-2, 3) == -6.0


# =============================================================================
# DIVIDE TESTS
# =============================================================================

class TestDivide:
    """Tests for divide operation."""

    def test_basic(self):
        calc = CalculatorAgent()
        assert calc.divide(10, 2) == 5.0

    def test_float_result(self):
        calc = CalculatorAgent()
        assert calc.divide(7, 2) == 3.5

    def test_by_zero_raises_error(self):
        calc = CalculatorAgent()
        with pytest.raises(ValueError, match="Cannot divide"):
            calc.divide(10, 0)

    def test_error_message_includes_value(self):
        """v2: Error message should include the value being divided."""
        calc = CalculatorAgent()
        with pytest.raises(ValueError, match="Cannot divide 10 by zero"):
            calc.divide(10, 0)


# =============================================================================
# POWER TESTS (v2 new)
# =============================================================================

class TestPower:
    """Tests for power operation (v2)."""

    def test_basic(self):
        calc = CalculatorAgent()
        assert calc.power(2, 3) == 8.0

    def test_negative_exponent(self):
        calc = CalculatorAgent()
        assert calc.power(2, -1) == 0.5

    def test_zero_exponent(self):
        calc = CalculatorAgent()
        assert calc.power(5, 0) == 1.0

    def test_zero_base(self):
        calc = CalculatorAgent()
        assert calc.power(0, 5) == 0.0

    def test_negative_base_integer_exponent(self):
        calc = CalculatorAgent()
        assert calc.power(-2, 3) == -8.0

    def test_negative_base_non_integer_exponent_raises(self):
        """Cannot raise negative to fractional power (complex result)."""
        calc = CalculatorAgent()
        with pytest.raises(ValueError, match="non-integer power"):
            calc.power(-2, 0.5)


# =============================================================================
# MODULO TESTS (v2 new)
# =============================================================================

class TestModulo:
    """Tests for modulo operation (v2)."""

    def test_basic(self):
        calc = CalculatorAgent()
        assert calc.modulo(10, 3) == 1.0

    def test_no_remainder(self):
        calc = CalculatorAgent()
        assert calc.modulo(10, 5) == 0.0

    def test_negative_dividend(self):
        calc = CalculatorAgent()
        # Python modulo: -10 % 3 = 2 (not -1)
        assert calc.modulo(-10, 3) == 2.0

    def test_by_zero_raises_error(self):
        calc = CalculatorAgent()
        with pytest.raises(ValueError, match="modulo zero"):
            calc.modulo(10, 0)


# =============================================================================
# SQRT TESTS (v2 new)
# =============================================================================

class TestSqrt:
    """Tests for sqrt operation (v2)."""

    def test_perfect_square(self):
        calc = CalculatorAgent()
        assert calc.sqrt(16) == 4.0

    def test_non_perfect_square(self):
        calc = CalculatorAgent()
        assert round(calc.sqrt(2), 10) == round(math.sqrt(2), 10)

    def test_zero(self):
        calc = CalculatorAgent()
        assert calc.sqrt(0) == 0.0

    def test_one(self):
        calc = CalculatorAgent()
        assert calc.sqrt(1) == 1.0

    def test_negative_raises_error(self):
        calc = CalculatorAgent()
        with pytest.raises(ValueError, match="negative number"):
            calc.sqrt(-1)

    def test_error_includes_value(self):
        calc = CalculatorAgent()
        with pytest.raises(ValueError, match="-4"):
            calc.sqrt(-4)


# =============================================================================
# VERIFY TESTS
# =============================================================================

class TestVerify:
    """Tests for self-verification."""

    def test_returns_dict(self):
        calc = CalculatorAgent()
        result = calc.verify()
        assert isinstance(result, dict)

    def test_has_required_keys(self):
        calc = CalculatorAgent()
        result = calc.verify()
        assert "status" in result
        assert "tests_run" in result
        assert "tests_passed" in result
        assert "tests_failed" in result
        assert "details" in result

    def test_all_tests_pass(self):
        calc = CalculatorAgent()
        result = calc.verify()
        assert result["status"] == "PASS"
        assert result["tests_failed"] == 0

    def test_runs_21_tests(self):
        """v2 should run 21 internal tests."""
        calc = CalculatorAgent()
        result = calc.verify()
        assert result["tests_run"] == 21


class TestVerifyPrint:
    """Tests for verify_print method (v2 new)."""

    def test_returns_boolean(self):
        calc = CalculatorAgent()
        result = calc.verify_print()
        assert isinstance(result, bool)

    def test_returns_true_when_passing(self):
        calc = CalculatorAgent()
        result = calc.verify_print()
        assert result is True
