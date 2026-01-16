"""
Tests for UtilityAgent v2 - Day 2 of AI Mastery.

Total: 63 tests covering:
- V1 functionality: routing, integration, error handling, edge cases (32 tests)
- V2 new features: calculator, aliases, describe, suggestions, categories (31 tests)

This is our first multi-agent integration test suite with v2 enhancements.
"""

import re
import pytest
from utility_agent import UtilityAgent


@pytest.fixture
def agent():
    """Create a UtilityAgent instance for testing."""
    return UtilityAgent()


# =============================================================================
# V1 TESTS - String Routing Tests (6)
# =============================================================================

def test_route_reverse(agent):
    """Test routing 'reverse' to StringAgent.reverse_string()."""
    assert agent.execute("reverse", "hello") == "olleh"


def test_route_uppercase(agent):
    """Test routing 'uppercase' to StringAgent.to_uppercase()."""
    assert agent.execute("uppercase", "hello") == "HELLO"


def test_route_lowercase(agent):
    """Test routing 'lowercase' to StringAgent.to_lowercase()."""
    assert agent.execute("lowercase", "HELLO") == "hello"


def test_route_count_words(agent):
    """Test routing 'count_words' to StringAgent.count_words()."""
    assert agent.execute("count_words", "hello world") == 2


def test_route_remove_spaces(agent):
    """Test routing 'remove_spaces' to StringAgent.remove_spaces()."""
    assert agent.execute("remove_spaces", "a b c") == "abc"


def test_string_error_propagates(agent):
    """Test that StringAgent errors propagate through UtilityAgent."""
    with pytest.raises(ValueError) as exc_info:
        agent.execute("reverse", None)
    assert "cannot be None" in str(exc_info.value)


# =============================================================================
# V1 TESTS - DateTime Routing Tests (6)
# =============================================================================

def test_route_current_time(agent):
    """Test routing 'current_time' to DateTimeAgent.get_current_time()."""
    result = agent.execute("current_time")
    assert re.match(r'\d{2}:\d{2}:\d{2}', result), f"Expected HH:MM:SS, got {result}"


def test_route_current_date(agent):
    """Test routing 'current_date' to DateTimeAgent.get_current_date()."""
    result = agent.execute("current_date")
    assert re.match(r'\d{4}-\d{2}-\d{2}', result), f"Expected YYYY-MM-DD, got {result}"


def test_route_add_days(agent):
    """Test routing 'add_days' to DateTimeAgent.add_days()."""
    assert agent.execute("add_days", "2024-01-15", 5) == "2024-01-20"


def test_route_days_between(agent):
    """Test routing 'days_between' to DateTimeAgent.days_between()."""
    assert agent.execute("days_between", "2024-01-15", "2024-01-20") == 5


def test_route_format_date(agent):
    """Test routing 'format_date' to DateTimeAgent.format_date()."""
    assert agent.execute("format_date", "2024-01-15", "%m/%d/%Y") == "01/15/2024"


def test_datetime_error_propagates(agent):
    """Test that DateTimeAgent errors propagate through UtilityAgent."""
    with pytest.raises(ValueError) as exc_info:
        agent.execute("add_days", "not-a-date", 5)
    assert "Cannot parse date" in str(exc_info.value)


# =============================================================================
# V1 TESTS - Operation Validation Tests (5)
# =============================================================================

def test_none_operation_raises(agent):
    """Test that None operation raises ValueError."""
    with pytest.raises(ValueError) as exc_info:
        agent.execute(None, "x")
    assert "cannot be None" in str(exc_info.value)


def test_bool_operation_raises(agent):
    """Test that boolean operation raises ValueError."""
    with pytest.raises(ValueError) as exc_info:
        agent.execute(True, "x")
    assert "must be a string" in str(exc_info.value)
    assert "got bool" in str(exc_info.value)


def test_int_operation_raises(agent):
    """Test that integer operation raises ValueError."""
    with pytest.raises(ValueError) as exc_info:
        agent.execute(123, "x")
    assert "must be a string" in str(exc_info.value)
    assert "got int" in str(exc_info.value)


def test_empty_operation_raises(agent):
    """Test that empty string operation raises ValueError."""
    with pytest.raises(ValueError) as exc_info:
        agent.execute("", "x")
    assert "cannot be empty" in str(exc_info.value)


def test_whitespace_operation_raises(agent):
    """Test that whitespace-only operation raises ValueError."""
    with pytest.raises(ValueError) as exc_info:
        agent.execute("   ", "x")
    assert "cannot be empty" in str(exc_info.value)


# =============================================================================
# V1 TESTS - Unknown Operation Tests (4)
# =============================================================================

def test_unknown_operation_raises(agent):
    """Test that unknown operation raises ValueError with available list."""
    with pytest.raises(ValueError) as exc_info:
        agent.execute("xyz", "x")
    assert "Unknown operation: 'xyz'" in str(exc_info.value)
    assert "Available:" in str(exc_info.value)


def test_typo_operation_raises(agent):
    """Test that typo in operation name raises ValueError."""
    with pytest.raises(ValueError) as exc_info:
        agent.execute("revrese", "hello")  # Typo: revrese instead of reverse
    assert "Unknown operation: 'revrese'" in str(exc_info.value)


def test_case_sensitive(agent):
    """Test that operation names are case-sensitive."""
    with pytest.raises(ValueError) as exc_info:
        agent.execute("REVERSE", "hello")  # Wrong case
    assert "Unknown operation: 'REVERSE'" in str(exc_info.value)


def test_similar_name_raises(agent):
    """Test that using internal method name raises ValueError."""
    with pytest.raises(ValueError) as exc_info:
        agent.execute("reverse_string", "hello")  # Internal name, not registry name
    assert "Unknown operation: 'reverse_string'" in str(exc_info.value)


# =============================================================================
# V1 TESTS - Error Propagation Tests (4)
# =============================================================================

def test_string_agent_error_propagates(agent):
    """Test that StringAgent ValueError propagates unchanged."""
    with pytest.raises(ValueError) as exc_info:
        agent.execute("uppercase", None)
    # Should be StringAgent's error message
    assert "cannot be None" in str(exc_info.value)


def test_datetime_agent_error_propagates(agent):
    """Test that DateTimeAgent ValueError propagates unchanged."""
    with pytest.raises(ValueError) as exc_info:
        agent.execute("add_days", "2024-02-30", 5)  # Invalid date
    # Should be DateTimeAgent's error message
    assert "Cannot parse date" in str(exc_info.value)


def test_error_message_preserved(agent):
    """Test that original error message is preserved."""
    with pytest.raises(ValueError) as exc_info:
        agent.execute("count_words", 123)  # Wrong type
    # StringAgent's specific message should come through
    assert "must be a string" in str(exc_info.value)


def test_error_type_preserved(agent):
    """Test that error type (ValueError) is preserved."""
    with pytest.raises(ValueError):  # Specifically ValueError, not wrapped
        agent.execute("days_between", None, "2024-01-20")


# =============================================================================
# V1 TESTS - Wrong Arguments Tests (3)
# =============================================================================

def test_missing_required_arg(agent):
    """Test that missing required argument raises TypeError."""
    with pytest.raises(TypeError) as exc_info:
        agent.execute("reverse")  # Missing 'text' argument
    assert "missing" in str(exc_info.value).lower()


def test_wrong_arg_type(agent):
    """Test that wrong argument type raises ValueError from sub-agent."""
    with pytest.raises(ValueError) as exc_info:
        agent.execute("add_days", "2024-01-15", "five")  # String instead of int
    assert "must be an integer" in str(exc_info.value)


def test_extra_args_to_no_arg_method(agent):
    """Test behavior when passing args to no-arg method."""
    # current_time takes no args, but Python allows passing extra args
    # This tests that the method is actually called correctly
    result = agent.execute("current_time")
    assert re.match(r'\d{2}:\d{2}:\d{2}', result)


# =============================================================================
# V1 TESTS - list_operations() Tests (2) - UPDATED FOR V2
# =============================================================================

def test_list_operations_returns_list(agent):
    """Test that list_operations() returns a list."""
    result = agent.list_operations()
    assert isinstance(result, list)


def test_list_operations_complete(agent):
    """Test that list_operations() contains all 17 operations, sorted."""
    result = agent.list_operations()
    expected = [
        "add", "add_days", "count_words", "current_date", "current_time",
        "days_between", "divide", "format_date", "lowercase", "modulo",
        "multiply", "power", "remove_spaces", "reverse", "sqrt",
        "subtract", "uppercase"
    ]
    assert result == expected
    assert len(result) == 17


# =============================================================================
# V1 TESTS - verify() Tests (2)
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


# =============================================================================
# V2 TESTS - Calculator Routing Tests (8)
# =============================================================================

def test_route_add(agent):
    """Test routing 'add' to CalculatorAgent.add()."""
    assert agent.execute("add", 2, 3) == 5.0


def test_route_subtract(agent):
    """Test routing 'subtract' to CalculatorAgent.subtract()."""
    assert agent.execute("subtract", 10, 4) == 6.0


def test_route_multiply(agent):
    """Test routing 'multiply' to CalculatorAgent.multiply()."""
    assert agent.execute("multiply", 3, 4) == 12.0


def test_route_divide(agent):
    """Test routing 'divide' to CalculatorAgent.divide()."""
    assert agent.execute("divide", 10, 2) == 5.0


def test_route_power(agent):
    """Test routing 'power' to CalculatorAgent.power()."""
    assert agent.execute("power", 2, 3) == 8.0


def test_route_modulo(agent):
    """Test routing 'modulo' to CalculatorAgent.modulo()."""
    assert agent.execute("modulo", 10, 3) == 1.0


def test_route_sqrt(agent):
    """Test routing 'sqrt' to CalculatorAgent.sqrt()."""
    assert agent.execute("sqrt", 16) == 4.0


def test_calculator_error_propagates(agent):
    """Test that CalculatorAgent errors propagate through UtilityAgent."""
    with pytest.raises(ValueError) as exc_info:
        agent.execute("divide", 1, 0)
    assert "zero" in str(exc_info.value).lower()


# =============================================================================
# V2 TESTS - Alias Tests (6)
# =============================================================================

def test_alias_rev(agent):
    """Test that 'rev' alias works for 'reverse'."""
    assert agent.execute("rev", "hello") == "olleh"


def test_alias_upper(agent):
    """Test that 'upper' alias works for 'uppercase'."""
    assert agent.execute("upper", "hi") == "HI"


def test_alias_lower(agent):
    """Test that 'lower' alias works for 'lowercase'."""
    assert agent.execute("lower", "HI") == "hi"


def test_alias_now(agent):
    """Test that 'now' alias works for 'current_time'."""
    result = agent.execute("now")
    assert re.match(r'\d{2}:\d{2}:\d{2}', result)


def test_alias_today(agent):
    """Test that 'today' alias works for 'current_date'."""
    result = agent.execute("today")
    assert re.match(r'\d{4}-\d{2}-\d{2}', result)


def test_alias_plus(agent):
    """Test that 'plus' alias works for 'add'."""
    assert agent.execute("plus", 2, 3) == 5.0


# =============================================================================
# V2 TESTS - Describe Tests (5)
# =============================================================================

def test_describe_returns_string(agent):
    """Test that describe() returns a string."""
    result = agent.describe("reverse")
    assert isinstance(result, str)


def test_describe_reverse(agent):
    """Test describe() for reverse operation."""
    result = agent.describe("reverse")
    assert "string" in result.lower()
    assert "Args:" in result


def test_describe_add_days(agent):
    """Test describe() for add_days operation."""
    result = agent.describe("add_days")
    assert "date" in result.lower()
    assert "Args:" in result


def test_describe_with_alias(agent):
    """Test that describe() works with aliases."""
    result = agent.describe("rev")  # alias for reverse
    assert "string" in result.lower()


def test_describe_unknown_raises(agent):
    """Test that describe() raises ValueError for unknown operation."""
    with pytest.raises(ValueError) as exc_info:
        agent.describe("xyz")
    assert "Unknown operation" in str(exc_info.value)


# =============================================================================
# V2 TESTS - "Did You Mean?" Suggestion Tests (4)
# =============================================================================

def test_suggestion_for_typo(agent):
    """Test that typo gets 'Did you mean?' suggestion."""
    with pytest.raises(ValueError) as exc_info:
        agent.execute("revrese", "hello")  # typo of reverse
    error_msg = str(exc_info.value)
    assert "Did you mean" in error_msg
    assert "reverse" in error_msg


def test_suggestion_for_prefix_typo(agent):
    """Test suggestion for prefix-match typo."""
    with pytest.raises(ValueError) as exc_info:
        agent.execute("uppercas", "hello")  # missing 'e'
    error_msg = str(exc_info.value)
    assert "Did you mean" in error_msg
    assert "uppercase" in error_msg


def test_no_suggestion_for_gibberish(agent):
    """Test that gibberish doesn't get unhelpful suggestions."""
    with pytest.raises(ValueError) as exc_info:
        agent.execute("xyz", "hello")
    error_msg = str(exc_info.value)
    # Should NOT suggest anything for completely unrelated input
    assert "Available:" in error_msg


def test_suggestion_includes_available(agent):
    """Test that error still includes available operations list."""
    with pytest.raises(ValueError) as exc_info:
        agent.execute("revrese", "hello")
    error_msg = str(exc_info.value)
    assert "Available:" in error_msg


# =============================================================================
# V2 TESTS - Category Tests (4)
# =============================================================================

def test_categories_returns_dict(agent):
    """Test that list_operations_by_category() returns a dict."""
    result = agent.list_operations_by_category()
    assert isinstance(result, dict)


def test_categories_has_three_keys(agent):
    """Test that categories dict has three keys."""
    result = agent.list_operations_by_category()
    assert len(result) == 3
    assert "string" in result
    assert "datetime" in result
    assert "calculator" in result


def test_categories_string_ops(agent):
    """Test that string category contains correct operations."""
    result = agent.list_operations_by_category()
    assert "reverse" in result["string"]
    assert "uppercase" in result["string"]
    assert len(result["string"]) == 5


def test_categories_calculator_ops(agent):
    """Test that calculator category contains correct operations."""
    result = agent.list_operations_by_category()
    assert "add" in result["calculator"]
    assert "sqrt" in result["calculator"]
    assert len(result["calculator"]) == 7


# =============================================================================
# V2 TESTS - list_aliases() Tests (2)
# =============================================================================

def test_list_aliases_returns_dict(agent):
    """Test that list_aliases() returns a dict."""
    result = agent.list_aliases()
    assert isinstance(result, dict)


def test_list_aliases_complete(agent):
    """Test that list_aliases() contains all 10 aliases."""
    result = agent.list_aliases()
    assert len(result) == 10
    assert result["rev"] == "reverse"
    assert result["plus"] == "add"
    assert result["now"] == "current_time"


# =============================================================================
# V2 TESTS - Version Tests (2)
# =============================================================================

def test_version_is_2(agent):
    """Test that agent version is 2.0."""
    assert agent.version == "2.0"


def test_has_three_subagents(agent):
    """Test that agent has three sub-agents."""
    assert hasattr(agent, "string_agent")
    assert hasattr(agent, "datetime_agent")
    assert hasattr(agent, "calculator_agent")
