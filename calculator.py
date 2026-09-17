"""Small public API for evaluating expressions."""

from formatter import format_result
from expression_parser import parse_expression


def evaluate(expression):
    """Evaluate one expression and return formatted result data."""
    return format_result(parse_expression(expression))
