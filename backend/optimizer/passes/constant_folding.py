from __future__ import annotations

import re

from ..models import OptimizationContext, Suggestion
from .base import OptimizationPass
from .common import safe_eval_arithmetic


DECL_RE = re.compile(r'^(?:int|void|float|double|char|long|short)\s+([A-Za-z_]\w*)\s*=\s*(.+)$')


class ConstantFoldingPass(OptimizationPass):
    name = "constant_folding"
    description = "Evaluates arithmetic expressions made only from constants."

    def apply(self, context: OptimizationContext) -> None:
        program = self.program(context)

        for statement in program.statements:
            if statement.kind != "assignment" or not statement.expression or not statement.target:
                continue

            decl_match = DECL_RE.match(statement.text.rstrip(';'))
            is_declaration = decl_match is not None

            folded = safe_eval_arithmetic(statement.expression)
            if folded is None or str(folded) == statement.expression:
                continue

            if is_declaration:
                after = f"{statement.target} = {folded};"
            else:
                after = f"{statement.target} = {folded};"
            
            context.optimized = context.optimized.replace(statement.text, after, 1)
            context.suggestions.append(
                Suggestion(
                    title="Fold constant expression",
                    explanation="The expression contains only constants, so the compiler can calculate it once.",
                    before=statement.text,
                    after=after,
                    confidence=0.99,
                    strategy="constant_folding",
                    pass_name=self.name,
                    line=statement.line,
                    impact="medium",
                )
            )

