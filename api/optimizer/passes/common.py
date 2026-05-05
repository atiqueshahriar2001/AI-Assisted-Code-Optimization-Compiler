from __future__ import annotations

import ast


def safe_eval_arithmetic(expr: str) -> int | float | None:
    try:
        tree = ast.parse(expr, mode="eval")
        if not all(is_safe_node(node) for node in ast.walk(tree)):
            return None
        value = eval(compile(tree, "<constant-fold>", "eval"), {"__builtins__": {}}, {})
    except Exception:
        return None

    if isinstance(value, float) and value.is_integer():
        return int(value)
    if isinstance(value, (int, float)):
        return value
    return None


def is_safe_node(node: ast.AST) -> bool:
    allowed = (
        ast.Expression,
        ast.BinOp,
        ast.UnaryOp,
        ast.Constant,
        ast.Add,
        ast.Sub,
        ast.Mult,
        ast.Div,
        ast.FloorDiv,
        ast.Mod,
        ast.Pow,
        ast.USub,
        ast.UAdd,
        ast.Load,
    )
    return isinstance(node, allowed) and not isinstance(node, ast.Name)