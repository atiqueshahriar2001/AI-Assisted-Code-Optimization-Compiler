from __future__ import annotations

import re
from collections import Counter

from .models import Program


IDENTIFIER_RE = re.compile(r"\b[A-Za-z_]\w*\b")
KEYWORDS = {"for", "if", "else", "while", "return"}


def analyze_program(program: Program) -> dict:
    identifiers = [
        token
        for token in IDENTIFIER_RE.findall(program.source)
        if token not in KEYWORDS
    ]
    counts = Counter(identifiers)
    loops = sum(1 for statement in program.statements if statement.kind == "for_loop")
    assignments = sum(1 for statement in program.statements if statement.kind == "assignment")

    return {
        "statement_count": len(program.statements),
        "assignment_count": assignments,
        "loop_count": loops,
        "unique_identifier_count": len(counts),
        "hot_identifiers": counts.most_common(5),
        "estimated_complexity": estimate_complexity(loops),
    }


def estimate_complexity(loop_count: int) -> str:
    if loop_count == 0:
        return "O(1) for straight-line assignments"
    if loop_count == 1:
        return "O(n) before loop optimizations"
    return f"O(n^{loop_count}) worst-case if loops are nested or dependent"

