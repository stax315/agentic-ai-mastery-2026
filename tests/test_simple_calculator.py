"""
Tests for Simple Calculator Module
Day 1 - Learning to write tests with pytest

Run with: python -m pytest test_simple_calculator.py -v
"""

from simple_calculator import sum_even_numbers


def test_basic_mixed_list():
    """Test with a mix of even and odd numbers."""
    result = sum_even_numbers([1, 2, 3, 4, 5, 6])
    assert result == 12  # 2 + 4 + 6 = 12


def test_empty_list():
    """Test with an empty list - should return 0."""
    result = sum_even_numbers([])
    assert result == 0


def test_all_even_numbers():
    """Test when all numbers are even."""
    result = sum_even_numbers([2, 4, 6])
    assert result == 12  # 2 + 4 + 6 = 12


def test_all_odd_numbers():
    """Test when all numbers are odd - should return 0."""
    result = sum_even_numbers([1, 3, 5])
    assert result == 0


def test_single_even_number():
    """Test with just one even number."""
    result = sum_even_numbers([4])
    assert result == 4


def test_single_odd_number():
    """Test with just one odd number - should return 0."""
    result = sum_even_numbers([3])
    assert result == 0


def test_with_zero():
    """Test that zero is treated as even."""
    result = sum_even_numbers([0, 1, 2])
    assert result == 2  # 0 + 2 = 2


def test_negative_even_numbers():
    """Test that negative even numbers work correctly."""
    result = sum_even_numbers([-2, -4, 3])
    assert result == -6  # -2 + -4 = -6


def test_large_numbers():
    """Test with large numbers."""
    result = sum_even_numbers([1000000, 1])
    assert result == 1000000
