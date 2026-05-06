from __future__ import annotations

import re
from collections import Counter

from .models import Program


IDENTIFIER_RE = re.compile(r"\b[A-Za-z_]\w*\b")
KEYWORDS = {"for", "if", "else", "while", "return", "int", "void", "float", "double", "char", "long", "short"}
C_TYPES = {"int", "void", "float", "double", "char", "long", "short", "unsigned", "signed", "static", "const", "struct"}


def analyze_program(program: Program) -> dict:
    identifiers = [
        token
        for token in IDENTIFIER_RE.findall(program.source)
        if token not in KEYWORDS and token not in C_TYPES
    ]
    counts = Counter(identifiers)
    loops = sum(1 for statement in program.statements if statement.kind in ('for_loop', 'while_loop'))
    assignments = sum(1 for statement in program.statements if statement.kind in ("assignment", "declaration"))
    function_calls = sum(1 for statement in program.statements if statement.kind == "function_call")
    function_defs = sum(1 for statement in program.statements if statement.kind == "function_definition")

    return {
        "statement_count": len(program.statements),
        "assignment_count": assignments,
        "loop_count": loops,
        "function_call_count": function_calls,
        "function_definition_count": function_defs,
        "unique_identifier_count": len(counts),
        "hot_identifiers": counts.most_common(5),
        "estimated_complexity": estimate_complexity(loops, assignments),
    }


def estimate_complexity(loop_count: int, assignment_count: int) -> str:
    if loop_count == 0:
        return "O(1) for straight-line code"
    if loop_count == 1:
        if assignment_count < 10:
            return "O(n) with low constant factor"
        return "O(n) before loop optimizations"
    return f"O(n^{loop_count}) worst-case if loops are nested or dependent"

