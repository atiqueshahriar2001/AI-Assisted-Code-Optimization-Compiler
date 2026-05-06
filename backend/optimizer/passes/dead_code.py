from __future__ import annotations

import re

from ..models import OptimizationContext, Suggestion
from .base import OptimizationPass


IDENTIFIER_RE = re.compile(r"\b[A-Za-z_]\w*\b")
KEYWORDS = {"for", "if", "else", "while", "return"}


class DeadAssignmentPass(OptimizationPass):
    name = "dead_assignment_detection"
    description = "Finds assignments overwritten before the value is used."

    def apply(self, context: OptimizationContext) -> None:
        program = self.program(context)
        last_assignment: dict[str, tuple[str, int, bool]] = {}
        dead_statements: list[str] = []

        for statement in program.statements:
            if statement.kind != "assignment" or not statement.target:
                self.mark_used_identifiers(statement.text, last_assignment)
                continue

            if statement.expression:
                self.mark_used_identifiers(statement.expression, last_assignment)

            if statement.target in last_assignment:
                before, line, was_used = last_assignment[statement.target]
                if not was_used:
                    context.suggestions.append(
                        Suggestion(
                            title="Remove overwritten assignment",
                            explanation="This value is assigned again before it is read, so the earlier assignment is probably dead code.",
                            before=before,
                            after="// removed dead assignment",
                            confidence=0.63,
                            strategy="dead_code_elimination",
                            pass_name=self.name,
                            line=line,
                            impact="medium",
                        )
                    )
                    dead_statements.append(before)

            last_assignment[statement.target] = (statement.text, statement.line, False)

        for statement_text in dead_statements:
            context.optimized = remove_statement_once(context.optimized, statement_text)

    def mark_used_identifiers(
        self,
        text: str,
        last_assignment: dict[str, tuple[str, int, bool]],
    ) -> None:
        for token in IDENTIFIER_RE.findall(text):
            if token in KEYWORDS or token not in last_assignment:
                continue
            before, line, _ = last_assignment[token]
            last_assignment[token] = (before, line, True)


def remove_statement_once(source: str, statement_text: str) -> str:
    start = source.find(statement_text)
    if start == -1:
        return source

    end = start + len(statement_text)
    while end < len(source) and source[end] in " \t":
        end += 1
    if end < len(source) and source[end] == "\n":
        end += 1
        return source[:start] + source[end:]

    before = source[:start].rstrip(" \t")
    after = source[end:].lstrip(" \t")
    if before and after and not before.endswith(("\n", " ", "\t")):
        return before + " " + after
    return before + after
