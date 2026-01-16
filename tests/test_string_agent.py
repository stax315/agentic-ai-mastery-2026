"""
Tests for StringAgent - Day 2 of AI Mastery.

Total: 45 tests covering all operations, edge cases, and error handling.
"""

import pytest
from string_agent import StringAgent


@pytest.fixture
def agent():
    """Create a StringAgent instance for testing."""
    return StringAgent()


# =============================================================================
# reverse_string() Tests (6)
# =============================================================================

def test_reverse_normal(agent):
    """Test reversing a normal string."""
    assert agent.reverse_string("hello") == "olleh"


def test_reverse_palindrome(agent):
    """Test reversing a palindrome stays the same."""
    assert agent.reverse_string("racecar") == "racecar"


def test_reverse_empty(agent):
    """Test reversing an empty string returns empty."""
    assert agent.reverse_string("") == ""


def test_reverse_whitespace(agent):
    """Test reversing whitespace preserves it."""
    assert agent.reverse_string("   ") == "   "


def test_reverse_unicode(agent):
    """Test reversing a string with unicode/emoji."""
    assert agent.reverse_string("hi 👋") == "👋 ih"


def test_reverse_none_raises(agent):
    """Test that None raises ValueError."""
    with pytest.raises(ValueError) as exc_info:
        agent.reverse_string(None)
    assert "cannot be None" in str(exc_info.value)


# =============================================================================
# to_uppercase() Tests (6)
# =============================================================================

def test_uppercase_normal(agent):
    """Test converting lowercase to uppercase."""
    assert agent.to_uppercase("hello") == "HELLO"


def test_uppercase_mixed(agent):
    """Test converting mixed case to uppercase."""
    assert agent.to_uppercase("HeLLo") == "HELLO"


def test_uppercase_already(agent):
    """Test that already uppercase stays uppercase."""
    assert agent.to_uppercase("HELLO") == "HELLO"


def test_uppercase_empty(agent):
    """Test uppercase of empty string is empty."""
    assert agent.to_uppercase("") == ""


def test_uppercase_with_numbers(agent):
    """Test that numbers in string are unchanged."""
    assert agent.to_uppercase("abc123") == "ABC123"


def test_uppercase_none_raises(agent):
    """Test that None raises ValueError."""
    with pytest.raises(ValueError) as exc_info:
        agent.to_uppercase(None)
    assert "cannot be None" in str(exc_info.value)


# =============================================================================
# to_lowercase() Tests (6)
# =============================================================================

def test_lowercase_normal(agent):
    """Test converting uppercase to lowercase."""
    assert agent.to_lowercase("HELLO") == "hello"


def test_lowercase_mixed(agent):
    """Test converting mixed case to lowercase."""
    assert agent.to_lowercase("HeLLo") == "hello"


def test_lowercase_already(agent):
    """Test that already lowercase stays lowercase."""
    assert agent.to_lowercase("hello") == "hello"


def test_lowercase_empty(agent):
    """Test lowercase of empty string is empty."""
    assert agent.to_lowercase("") == ""


def test_lowercase_special_chars(agent):
    """Test that special characters are unchanged."""
    assert agent.to_lowercase("HELLO!") == "hello!"


def test_lowercase_int_raises(agent):
    """Test that integer raises ValueError."""
    with pytest.raises(ValueError) as exc_info:
        agent.to_lowercase(123)
    assert "must be a string" in str(exc_info.value)
    assert "got int" in str(exc_info.value)


# =============================================================================
# count_words() Tests (13)
# =============================================================================

def test_count_normal(agent):
    """Test counting words in normal string."""
    assert agent.count_words("Hello World") == 2


def test_count_single(agent):
    """Test counting a single word."""
    assert agent.count_words("Hello") == 1


def test_count_empty(agent):
    """Test counting words in empty string."""
    assert agent.count_words("") == 0


def test_count_whitespace_only(agent):
    """Test counting words in whitespace-only string."""
    assert agent.count_words("   ") == 0


def test_count_multiple_spaces(agent):
    """Test counting words with multiple spaces between."""
    assert agent.count_words("a  b  c") == 3


def test_count_leading_trailing(agent):
    """Test counting words with leading/trailing spaces."""
    assert agent.count_words("  Hello World  ") == 2


def test_count_newlines(agent):
    """Test counting words separated by newlines."""
    assert agent.count_words("Hello\nWorld") == 2


def test_count_tabs(agent):
    """Test counting words separated by tabs."""
    assert agent.count_words("Hello\tWorld") == 2


def test_count_contraction(agent):
    """Test that contraction counts as one word."""
    assert agent.count_words("don't") == 1


def test_count_contraction_sentence(agent):
    """Test contraction in a sentence."""
    assert agent.count_words("don't stop") == 2


def test_count_hyphenated(agent):
    """Test that hyphenated word counts as one word."""
    assert agent.count_words("well-known") == 1


def test_count_number_string(agent):
    """Test that number string counts as one word."""
    assert agent.count_words("123") == 1


def test_count_bool_raises(agent):
    """Test that boolean raises ValueError."""
    with pytest.raises(ValueError) as exc_info:
        agent.count_words(True)
    assert "must be a string" in str(exc_info.value)
    assert "got bool" in str(exc_info.value)


# =============================================================================
# remove_spaces() Tests (8)
# =============================================================================

def test_remove_normal(agent):
    """Test removing spaces from normal string."""
    assert agent.remove_spaces("Hello World") == "HelloWorld"


def test_remove_multiple(agent):
    """Test removing multiple spaces."""
    assert agent.remove_spaces("a  b  c") == "abc"


def test_remove_all_spaces(agent):
    """Test removing all spaces from whitespace-only string."""
    assert agent.remove_spaces("   ") == ""


def test_remove_empty(agent):
    """Test removing spaces from empty string."""
    assert agent.remove_spaces("") == ""


def test_remove_tabs(agent):
    """Test removing tabs."""
    assert agent.remove_spaces("a\tb") == "ab"


def test_remove_newlines(agent):
    """Test removing newlines."""
    assert agent.remove_spaces("a\nb") == "ab"


def test_remove_mixed_whitespace(agent):
    """Test removing mixed whitespace types."""
    assert agent.remove_spaces("a \t\n b") == "ab"


def test_remove_list_raises(agent):
    """Test that list raises ValueError."""
    with pytest.raises(ValueError) as exc_info:
        agent.remove_spaces(["a"])
    assert "must be a string" in str(exc_info.value)
    assert "got list" in str(exc_info.value)


# =============================================================================
# Validation Tests (4)
# =============================================================================

def test_validate_none(agent):
    """Test that None is rejected with clear message."""
    with pytest.raises(ValueError) as exc_info:
        agent.reverse_string(None)
    assert "cannot be None" in str(exc_info.value)


def test_validate_bool(agent):
    """Test that boolean is rejected with clear message."""
    with pytest.raises(ValueError) as exc_info:
        agent.to_uppercase(True)
    assert "must be a string" in str(exc_info.value)
    assert "got bool" in str(exc_info.value)


def test_validate_int(agent):
    """Test that integer is rejected with clear message."""
    with pytest.raises(ValueError) as exc_info:
        agent.count_words(123)
    assert "must be a string" in str(exc_info.value)
    assert "got int" in str(exc_info.value)


def test_validate_dict(agent):
    """Test that dict is rejected with clear message."""
    with pytest.raises(ValueError) as exc_info:
        agent.remove_spaces({})
    assert "must be a string" in str(exc_info.value)
    assert "got dict" in str(exc_info.value)


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
