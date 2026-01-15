"""
Simple Calculator Module
Day 1 - Learning functions, loops, and testing

This module contains utility functions for number calculations.
"""


def sum_even_numbers(numbers: list) -> int:
    """
    Sum only the even numbers from a list.

    Args:
        numbers: A list of integers

    Returns:
        The sum of all even numbers in the list

    Examples:
        >>> sum_even_numbers([1, 2, 3, 4, 5, 6])
        12
        >>> sum_even_numbers([])
        0
    """
    total = 0

    for number in numbers:
        if number % 2 == 0:
            total = total + number

    return total
