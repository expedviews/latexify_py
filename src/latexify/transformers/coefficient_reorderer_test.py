"""Tests for latexify.transformers.coefficient_reorderer."""

from __future__ import annotations

import ast

from latexify import ast_utils, test_utils
from latexify.transformers.coefficient_reorderer import CoefficientReorderer


def _mult(left: ast.expr, right: ast.expr) -> ast.BinOp:
    return ast.BinOp(left=left, op=ast.Mult(), right=right)


def test_trailing_constant_moved_to_front() -> None:
    tree = _mult(ast_utils.make_name("x"), ast_utils.make_constant(2))
    expected = _mult(ast_utils.make_constant(2), ast_utils.make_name("x"))
    transformed = CoefficientReorderer().visit(tree)
    test_utils.assert_ast_equal(transformed, expected)


def test_leading_constant_unchanged() -> None:
    tree = _mult(ast_utils.make_constant(2), ast_utils.make_name("x"))
    expected = _mult(ast_utils.make_constant(2), ast_utils.make_name("x"))
    transformed = CoefficientReorderer().visit(tree)
    test_utils.assert_ast_equal(transformed, expected)


def test_constants_bubble_in_chain() -> None:
    # (2 * x) * 4 -> (2 * 4) * x
    tree = _mult(
        _mult(ast_utils.make_constant(2), ast_utils.make_name("x")),
        ast_utils.make_constant(4),
    )
    expected = _mult(
        _mult(ast_utils.make_constant(2), ast_utils.make_constant(4)),
        ast_utils.make_name("x"),
    )
    transformed = CoefficientReorderer().visit(tree)
    test_utils.assert_ast_equal(transformed, expected)


def test_no_constants_unchanged() -> None:
    tree = _mult(ast_utils.make_name("a"), ast_utils.make_name("b"))
    expected = _mult(ast_utils.make_name("a"), ast_utils.make_name("b"))
    transformed = CoefficientReorderer().visit(tree)
    test_utils.assert_ast_equal(transformed, expected)


def test_string_constant_not_moved() -> None:
    tree = _mult(ast_utils.make_name("x"), ast_utils.make_constant("a"))
    expected = _mult(ast_utils.make_name("x"), ast_utils.make_constant("a"))
    transformed = CoefficientReorderer().visit(tree)
    test_utils.assert_ast_equal(transformed, expected)


def test_bool_constant_not_moved() -> None:
    tree = _mult(ast_utils.make_name("x"), ast_utils.make_constant(True))
    expected = _mult(ast_utils.make_name("x"), ast_utils.make_constant(True))
    transformed = CoefficientReorderer().visit(tree)
    test_utils.assert_ast_equal(transformed, expected)


def test_matmul_untouched() -> None:
    tree = ast.BinOp(
        left=ast_utils.make_name("x"), op=ast.MatMult(), right=ast_utils.make_constant(2)
    )
    expected = ast.BinOp(
        left=ast_utils.make_name("x"), op=ast.MatMult(), right=ast_utils.make_constant(2)
    )
    transformed = CoefficientReorderer().visit(tree)
    test_utils.assert_ast_equal(transformed, expected)


def test_nested_inside_addition() -> None:
    # x + a * 2 -> x + 2 * a
    tree = ast.BinOp(
        left=ast_utils.make_name("x"),
        op=ast.Add(),
        right=_mult(ast_utils.make_name("a"), ast_utils.make_constant(2)),
    )
    expected = ast.BinOp(
        left=ast_utils.make_name("x"),
        op=ast.Add(),
        right=_mult(ast_utils.make_constant(2), ast_utils.make_name("a")),
    )
    transformed = CoefficientReorderer().visit(tree)
    test_utils.assert_ast_equal(transformed, expected)


def test_flat_chain_across_factors() -> None:
    # (a * 2) * (b * 3) -> (2 * 3) * (a * b) as a left-leaning chain
    tree = _mult(
        _mult(ast_utils.make_name("a"), ast_utils.make_constant(2)),
        _mult(ast_utils.make_name("b"), ast_utils.make_constant(3)),
    )
    expected = _mult(
        _mult(
            _mult(ast_utils.make_constant(2), ast_utils.make_constant(3)),
            ast_utils.make_name("a"),
        ),
        ast_utils.make_name("b"),
    )
    transformed = CoefficientReorderer().visit(tree)
    test_utils.assert_ast_equal(transformed, expected)
