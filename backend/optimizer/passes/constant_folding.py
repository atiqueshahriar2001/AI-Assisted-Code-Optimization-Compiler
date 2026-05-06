from __future__ import annotations

import re

from ..models import OptimizationContext, Suggestion
from .base import OptimizationPass
from .common import safe_eval_arithmetic


DECL_RE = re.compile(
    r'^(?P<prefix>(?:int|void|float|double|char|long|short|unsigned|signed|static|const)\s+)'
    r'(?P<target>[A-Za-z_]\w*)\s*=\s*(?P<expr>.+)$'
)


class ConstantFoldingPass(OptimizationPass):
    name = "constant_folding"
    description = "Evaluates arithmetic expressions made only from constants."

    def apply(self, context: OptimizationContext) -> None:
        program = self.program(context)

        for statement in program.statements:
            if statement.kind not in ("assignment", "declaration") or not statement.expression or not statement.target:
                continue

            decl_match = DECL_RE.match(statement.text.rstrip(";"))
            prefix = decl_match.group("prefix") if decl_match else ""

            folded = safe_eval_arithmetic(statement.expression)
            if folded is None or str(folded) == statement.expression:
                continue

            after = f"{prefix}{statement.target} = {folded};"
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

