from __future__ import annotations

import re

from ..models import OptimizationContext, Suggestion
from .base import OptimizationPass


class SyntaxSimplificationPass(OptimizationPass):
    name = "syntax_simplification"
    description = "Normalizes verbose assignments into clearer equivalent forms."

    def apply(self, context: OptimizationContext) -> None:
        program = self.program(context)

        for statement in program.statements:
            if statement.kind != "assignment" or not statement.expression or not statement.target:
                continue

            pattern = re.compile(rf"^{re.escape(statement.target)}\s*\+\s*(?P<expr>[A-Za-z_]\w*)$")
            match = pattern.match(statement.expression)
            if not match:
                continue

            after = f"{statement.target} += {match.group('expr')};"
            context.optimized = context.optimized.replace(statement.text, after, 1)
            context.suggestions.append(
                Suggestion(
                    title="Prefer compound assignment",
                    explanation="Compound assignment communicates intent clearly and can simplify generated intermediate code.",
                    before=statement.text,
                    after=after,
                    confidence=0.72,
                    strategy="syntax_simplification",
                    pass_name=self.name,
                    line=statement.line,
                    impact="low",
                )
            )