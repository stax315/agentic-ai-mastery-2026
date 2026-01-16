"""
Tests for Calculator Agent
Day 1 - Test-as-you-go approach

Run with: python3 -m pytest test_calculator_agent.py -v
"""

import pytest
from calculator_agent import CalculatorAgent


# =============================================================================
# VALIDATION TESTS
# =============================================================================

def test_validate_rejects_string():
    """Validation should reject string inputs."""
    calc = CalculatorAgent()
    with pytest.raises(ValueError) as exc_info:
        calc._validate_inputs("5", 3)
    assert "First argument must be a number" in str(exc_info.value)


def test_validate_rejects_none():
    """Validation should reject None inputs."""
    calc = CalculatorAgent()
    with pytest.raises(ValueError) as exc_info:
        calc._validate_inputs(None, 3)
    assert "First argument must be a number" in str(exc_info.value)


def test_validate_rejects_boolean():
    """Validation should reject boolean inputs (True/False)."""
    calc = CalculatorAgent()
    with pytest.raises(ValueError) as exc_info:
        calc._validate_inputs(True, 3)
    assert "First argument must be a number" in str(exc_info.value)


def test_validate_rejects_list():
    """Validation should reject list inputs."""
    calc = CalculatorAgent()
    with pytest.raises(ValueError) as exc_info:
        calc._validate_inputs([1, 2], 3)
    assert "First argument must be a number" in str(exc_info.value)


def test_validate_rejects_second_arg_string():
    """Validation should reject string as second argument."""
    calc = CalculatorAgent()
    with pytest.raises(ValueError) as exc_info:
        calc._validate_inputs(3, "5")
    assert "Second argument must be a number" in str(exc_info.value)


def test_validate_accepts_integers():
    """Validation should accept integer inputs."""
    calc = CalculatorAgent()
    # Should not raise any exception
    calc._validate_inputs(5, 3)


def test_validate_accepts_floats():
    """Validation should accept float inputs."""
    calc = CalculatorAgent()
    # Should not raise any exception
    calc._validate_inputs(5.5, 3.3)


# =============================================================================
# ADD TESTS
# =============================================================================

def test_add_positive_numbers():
    """Add two positive numbers."""
    calc = CalculatorAgent()
    result = calc.add(2, 3)
    assert result == 5.0
    assert isinstance(result, float)


def test_add_negative_numbers():
    """Add two negative numbers."""
    calc = CalculatorAgent()
    result = calc.add(-1, -2)
    assert result == -3.0


def test_add_mixed_signs():
    """Add positive and negative numbers."""
    calc = CalculatorAgent()
    result = calc.add(-1, 1)
    assert result == 0.0


def test_add_floats():
    """Add two float numbers."""
    calc = CalculatorAgent()
    result = calc.add(1.5, 2.5)
    assert result == 4.0


def test_add_with_zero():
    """Add with zero (identity property)."""
    calc = CalculatorAgent()
    result = calc.add(5, 0)
    assert result == 5.0


def test_add_rejects_invalid_input():
    """Add should reject invalid inputs via validation."""
    calc = CalculatorAgent()
    with pytest.raises(ValueError):
        calc.add("5", 3)


# =============================================================================
# SUBTRACT TESTS
# =============================================================================

def test_subtract_basic():
    """Subtract two numbers."""
    calc = CalculatorAgent()
    result = calc.subtract(10, 4)
    assert result == 6.0
    assert isinstance(result, float)


def test_subtract_negative_result():
    """Subtract to get a negative result."""
    calc = CalculatorAgent()
    result = calc.subtract(5, 10)
    assert result == -5.0


def test_subtract_same_numbers():
    """Subtract same numbers equals zero."""
    calc = CalculatorAgent()
    result = calc.subtract(5, 5)
    assert result == 0.0


# =============================================================================
# MULTIPLY TESTS
# =============================================================================

def test_multiply_basic():
    """Multiply two numbers."""
    calc = CalculatorAgent()
    result = calc.multiply(3, 4)
    assert result == 12.0
    assert isinstance(result, float)


def test_multiply_by_zero():
    """Multiply by zero equals zero."""
    calc = CalculatorAgent()
    result = calc.multiply(5, 0)
    assert result == 0.0


def test_multiply_negatives():
    """Multiply two negatives equals positive."""
    calc = CalculatorAgent()
    result = calc.multiply(-2, -3)
    assert result == 6.0


def test_multiply_mixed_signs():
    """Multiply positive by negative equals negative."""
    calc = CalculatorAgent()
    result = calc.multiply(-2, 3)
    assert result == -6.0


# =============================================================================
# DIVIDE TESTS
# =============================================================================

def test_divide_basic():
    """Divide two numbers."""
    calc = CalculatorAgent()
    result = calc.divide(10, 2)
    assert result == 5.0
    assert isinstance(result, float)


def test_divide_float_result():
    """Divide to get a float result."""
    calc = CalculatorAgent()
    result = calc.divide(7, 2)
    assert result == 3.5


def test_divide_by_zero_raises_error():
    """Division by zero should raise ValueError."""
    calc = CalculatorAgent()
    with pytest.raises(ValueError) as exc_info:
        calc.divide(10, 0)
    assert "Cannot divide by zero" in str(exc_info.value)


def test_divide_negative():
    """Divide with negative numbers."""
    calc = CalculatorAgent()
    result = calc.divide(-10, 2)
    assert result == -5.0


# =============================================================================
# VERIFY TESTS (Self-Testing Agent)
# =============================================================================

def test_verify_returns_dict():
    """verify() should return a dictionary."""
    calc = CalculatorAgent()
    result = calc.verify()
    assert isinstance(result, dict)


def test_verify_has_required_keys():
    """verify() result should have all required keys."""
    calc = CalculatorAgent()
    result = calc.verify()
    assert "status" in result
    assert "tests_run" in result
    assert "tests_passed" in result
    assert "tests_failed" in result
    assert "details" in result


def test_verify_all_tests_pass():
    """verify() should report all tests passing."""
    calc = CalculatorAgent()
    result = calc.verify()
    assert result["status"] == "PASS"
    assert result["tests_failed"] == 0
    assert result["tests_passed"] == result["tests_run"]


def test_verify_runs_expected_number_of_tests():
    """verify() should run 12 internal tests."""
    calc = CalculatorAgent()
    result = calc.verify()
    assert result["tests_run"] == 12


def test_verify_details_is_list():
    """verify() details should be a list of test results."""
    calc = CalculatorAgent()
    result = calc.verify()
    assert isinstance(result["details"], list)
    assert len(result["details"]) == result["tests_run"]
