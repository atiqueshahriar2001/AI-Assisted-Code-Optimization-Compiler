from __future__ import annotations

import re

from ..models import OptimizationContext, Suggestion
from .base import OptimizationPass


SUMMATION_RE = re.compile(
    r"""
    (?P<sum>\w+)\s*=\s*0\s*;\s*
    for\s*\(\s*
        (?P<i>\w+)\s*=\s*1\s*;\s*
        (?P=i)\s*<=\s*(?P<n>\w+)\s*;\s*
        (?P=i)\s*=\s*(?P=i)\s*\+\s*1\s*
    \)\s*\{\s*
        (?P=sum)\s*=\s*(?P=sum)\s*\+\s*(?P=i)\s*;\s*
    \}
    """,
    re.VERBOSE,
)


class LoopPatternPass(OptimizationPass):
    name = "loop_patterns"
    description = "Recognizes common loop algorithms and replaces them with closed forms."

    def apply(self, context: OptimizationContext) -> None:
        def convert(match: re.Match[str]) -> str:
            total = match.group("sum")
            n_value = match.group("n")
            before = match.group(0)
            after = f"{total} = ({n_value} * ({n_value} + 1)) / 2;"
            line = context.optimized[: match.start()].count("\n") + 1
            context.suggestions.append(
                Suggestion(
                    title="Replace linear summation loop",
                    explanation="The loop computes the arithmetic series 1..n, which can be calculated in constant time.",
                    before=before,
                    after=after,
                    confidence=0.94,
                    strategy="loop_to_formula",
                    pass_name=self.name,
                    line=line,
                    impact="high",
                )
            )
            return after

        context.optimized = SUMMATION_RE.sub(convert, context.optimized)

