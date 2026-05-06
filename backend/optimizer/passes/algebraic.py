from __future__ import annotations

import re

from ..models import OptimizationContext, Suggestion
from .base import OptimizationPass


class AlgebraicSimplificationPass(OptimizationPass):
    name = "algebraic_simplification"
    description = "Applies algebraic identities to simplify expressions."

    def apply(self, context: OptimizationContext) -> None:
        patterns = [
            (re.compile(r"(?P<expr>\b[A-Za-z_]\w*\b)\s*\*\s*1"), lambda m: m.group("expr"), "Multiplication by 1 identity"),
            (re.compile(r"(?P<expr>\b[A-Za-z_]\w*\b)\s*\*\s*0"), lambda m: "0", "Multiplication by 0 identity"),
            (re.compile(r"(?P<expr>\b[A-Za-z_]\w*\b)\s*\+\s*0"), lambda m: m.group("expr"), "Addition of 0 identity"),
            (re.compile(r"(?P<expr>\b[A-Za-z_]\w*\b)\s*-\s*0"), lambda m: m.group("expr"), "Subtraction of 0 identity"),
            (re.compile(r"(?P<expr>\b[A-Za-z_]\w*\b)\s*/\s*1"), lambda m: m.group("expr"), "Division by 1 identity"),
            (re.compile(r"(?P<expr>\b[A-Za-z_]\w*\b)\s*\+\s*(?P=expr)"), lambda m: f"{m.group('expr')} * 2", "Addition of variable to itself"),
            (re.compile(r"(?P<expr>\b[A-Za-z_]\w*\b)\s*-\s*(?P=expr)"), lambda m: "0", "Subtraction of variable from itself"),
        ]

        for pattern, replacement, explanation in patterns:
            def replacer(match: re.Match[str]) -> str:
                before = match.group(0)
                after = replacement(match) if callable(replacement) else replacement
                if before == after:
                    return before

                line = context.optimized[: match.start()].count("\n") + 1
                context.suggestions.append(
                    Suggestion(
                        title="Algebraic simplification",
                        explanation=explanation,
                        before=before,
                        after=after,
                        confidence=0.90,
                        strategy="algebraic_simplification",
                        pass_name=self.name,
                        line=line,
                        impact="low",
                    )
                )
                return after

            context.optimized = pattern.sub(replacer, context.optimized)
