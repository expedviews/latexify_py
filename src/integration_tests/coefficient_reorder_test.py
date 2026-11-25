"""Integration tests for the reorder_coefficients option."""

from __future__ import annotations

import math

from integration_tests import integration_utils


def test_issue_114_quadratic_formula() -> None:
    def solve(a, b, c):
        return (-b + math.sqrt(b**2 - 4 * a * c)) / (a * 2)

    latex = (
        r"\mathrm{solve}(a, b, c) = "
        r"\frac{-b + \sqrt{ b^{2} - 4 a c }}{2 a}"
    )
    integration_utils.check_function(solve, latex, reorder_coefficients=True)


def test_constants_bubble_to_front() -> None:
    def f(x):
        return 2 * x * 4

    latex = r"f(x) = 2 \cdot 4 x"
    integration_utils.check_function(f, latex, reorder_coefficients=True)


def test_trailing_constant_moved_to_front() -> None:
    def g(x):
        return x * 2

    latex = r"g(x) = 2 x"
    integration_utils.check_function(g, latex, reorder_coefficients=True)


def test_default_behavior_unchanged() -> None:
    def g(x):
        return x * 2

    latex = r"g(x) = x \cdot 2"
    integration_utils.check_function(g, latex)
