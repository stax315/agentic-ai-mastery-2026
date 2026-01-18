"""Tests for CalculatorAgent - Day 3 rapid implementation."""

import pytest
import math
from calculator_agent import CalculatorAgent


@pytest.fixture
def agent():
    return CalculatorAgent()


# =============================================================================
# BASIC OPERATIONS
# =============================================================================

class TestAdd:
    def test_add_positive(self, agent):
        assert agent.add(2, 3) == 5.0

    def test_add_negative(self, agent):
        assert agent.add(-2, -3) == -5.0

    def test_add_floats(self, agent):
        assert agent.add(1.5, 2.5) == 4.0


class TestSubtract:
    def test_subtract_positive(self, agent):
        assert agent.subtract(10, 4) == 6.0

    def test_subtract_negative_result(self, agent):
        assert agent.subtract(4, 10) == -6.0


class TestMultiply:
    def test_multiply_positive(self, agent):
        assert agent.multiply(3, 4) == 12.0

    def test_multiply_by_zero(self, agent):
        assert agent.multiply(5, 0) == 0.0


class TestDivide:
    def test_divide_exact(self, agent):
        assert agent.divide(15, 3) == 5.0

    def test_divide_float_result(self, agent):
        assert agent.divide(10, 4) == 2.5

    def test_divide_by_zero_raises(self, agent):
        with pytest.raises(ValueError, match="Cannot divide 5 by zero"):
            agent.divide(5, 0)


class TestPower:
    def test_power_positive(self, agent):
        assert agent.power(2, 3) == 8.0

    def test_power_zero_exponent(self, agent):
        assert agent.power(5, 0) == 1.0

    def test_power_negative_base_non_integer_raises(self, agent):
        with pytest.raises(ValueError, match="Cannot raise negative"):
            agent.power(-2, 0.5)


class TestModulo:
    def test_modulo_positive(self, agent):
        assert agent.modulo(10, 3) == 1.0

    def test_modulo_by_zero_raises(self, agent):
        with pytest.raises(ValueError, match="modulo zero"):
            agent.modulo(10, 0)


class TestSqrt:
    def test_sqrt_perfect(self, agent):
        assert agent.sqrt(16) == 4.0

    def test_sqrt_non_perfect(self, agent):
        assert abs(agent.sqrt(2) - 1.41421356) < 0.0001

    def test_sqrt_negative_raises(self, agent):
        with pytest.raises(ValueError, match="negative number"):
            agent.sqrt(-1)


# =============================================================================
# VALIDATION
# =============================================================================

class TestValidation:
    def test_none_raises(self, agent):
        with pytest.raises(ValueError, match="cannot be None"):
            agent.add(None, 5)

    def test_bool_raises(self, agent):
        with pytest.raises(ValueError, match="got bool"):
            agent.add(True, 5)

    def test_string_raises(self, agent):
        with pytest.raises(ValueError, match="got str"):
            agent.add("5", 5)

    def test_nan_raises(self, agent):
        with pytest.raises(ValueError, match="cannot be NaN"):
            agent.add(float('nan'), 5)

    def test_infinity_raises(self, agent):
        with pytest.raises(ValueError, match="cannot be Infinity"):
            agent.add(float('inf'), 5)


# =============================================================================
# VERIFY
# =============================================================================

class TestVerify:
    def test_verify_returns_dict(self, agent):
        result = agent.verify()
        assert isinstance(result, dict)
        assert result["status"] == "PASS"

    def test_verify_print_returns_bool(self, agent, capsys):
        result = agent.verify_print()
        assert result is True
