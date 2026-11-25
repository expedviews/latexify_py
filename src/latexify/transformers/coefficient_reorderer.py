"""Reorder numeric coefficients to the front of products."""

from __future__ import annotations

import ast
from typing import Any


class CoefficientReorderer(ast.NodeTransformer):
    """NodeTransformer to move numeric constants to the front of products.

    Example:
        def f(x):
            return x * 2

        CoefficientReorderer() modifies the AST of the function above to below:

        def f(x):
            return 2 * x

    Only bare numeric constants (int and float, excluding bool) are moved.
    Other factors keep their relative order. Note that the AST does not
    preserve parentheses, so a product written with brackets such as
    (3 * a) * (2 * b) is treated as the flat chain 3 * a * 2 * b.
    """

    def visit_BinOp(self, node: ast.BinOp) -> Any:
        """Visit a BinOp node."""
        self.generic_visit(node)
        if not isinstance(node.op, ast.Mult):
            return node

        factors: list[ast.expr] = []
        _flatten_product(node, factors)
        if len(factors) < 2:
            return node

        reordered = [f for f in factors if _is_number(f)] + [
            f for f in factors if not _is_number(f)
        ]
        if all(a is b for a, b in zip(factors, reordered)):
            return node

        result = reordered[0]
        for factor in reordered[1:]:
            result = ast.BinOp(left=result, op=ast.Mult(), right=factor)
        return result


def _flatten_product(node: ast.expr, factors: list[ast.expr]) -> None:
    """Collects the factors of a multiplication chain in order."""
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Mult):
        _flatten_product(node.left, factors)
        _flatten_product(node.right, factors)
    else:
        factors.append(node)


def _is_number(node: ast.expr) -> bool:
    """Checks whether the node is a bare int or float constant."""
    return (
        isinstance(node, ast.Constant)
        and isinstance(node.value, (int, float))
        and not isinstance(node.value, bool)
    )
