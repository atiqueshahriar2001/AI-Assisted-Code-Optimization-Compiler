from __future__ import annotations

import re

from ..models import OptimizationContext, Suggestion
from .base import OptimizationPass


TYPE_DECL = r"(?:int|long|float|double|char|short)\s+"

SUMMATION_RE = re.compile(
    r"(?:(?:" + TYPE_DECL + r"))?(?P<sum>\w+)\s*=\s*0\s*;\s*"
    r"for\s*\(\s*(?:(?:" + TYPE_DECL + r"))?(?P<i>\w+)\s*=\s*1\s*;\s*"
    r"(?P=i)\s*<=\s*(?P<n>\w+)\s*;\s*"
    r"(?P=i)\s*=\s*(?P=i)\s*\+\s*1\s*"
    r"\)\s*\{\s*"
    r"(?P=sum)\s*=\s*(?P=sum)\s*\+\s*(?P=i)\s*;?\s*"
    r"\}",
    re.DOTALL,
)

SUMMATION_RE_MULTILINE = re.compile(
    r"(?:(?:" + TYPE_DECL + r"))?(?P<sum>\w+)\s*=\s*0\s*;"
    r".*?"
    r"for\s*\(\s*(?:(?:" + TYPE_DECL + r"))?(?P<i>\w+)\s*=\s*1\s*;\s*(?P=i)\s*<=\s*(?P<n>\w+)\s*;\s*(?P=i)\s*=\s*(?P=i)\s*\+\s*1\s*\)\s*\{"
    r".*?"
    r"(?P=sum)\s*=\s*(?P=sum)\s*\+\s*(?P=i)\s*;\s*"
    r"\}",
    re.DOTALL,
)

SUMMATION_RE_ALT = re.compile(
    r"(?:(?:" + TYPE_DECL + r"))?(?P<sum>\w+)\s*=\s*0\s*;"
    r".*?"
    r"for\s*\(\s*(?:(?:" + TYPE_DECL + r"))?(?P<i>\w+)\s*=\s*0\s*;\s*(?P=i)\s*<\s*(?P<n>\w+)\s*;\s*(?P=i)\s*\+\s*\+\s*\)\s*\{"
    r".*?"
    r"(?P=sum)\s*=\s*(?P=sum)\s*\+\s*(?P=i)\s*;\s*"
    r"\}",
    re.DOTALL,
)


class LoopPatternPass(OptimizationPass):
    name = "loop_patterns"
    description = "Recognizes common loop algorithms and replaces them with closed forms."

    def apply(self, context: OptimizationContext) -> None:
        for regex, formula_func in [
            (SUMMATION_RE_MULTILINE, self._formula_n),
            (SUMMATION_RE, self._formula_n),
            (SUMMATION_RE_ALT, self._formula_n_minus_1),
        ]:
            new_code = regex.sub(self._make_replacer(formula_func, context), context.optimized)
            if new_code != context.optimized:
                context.optimized = new_code
                break

    def _make_replacer(self, formula_func, context):
        def replacer(match):
            total, n = formula_func(match)
            line = context.optimized[: match.start()].count("\n") + 1
            context.suggestions.append(
                Suggestion(
                    title="Replace summation loop",
                    explanation="Loop converted to closed-form formula.",
                    before=match.group(0),
                    after=f"{total} = {n};",
                    confidence=0.94,
                    strategy="loop_to_formula",
                    pass_name=self.name,
                    line=line,
                    impact="high",
                )
            )
            return f"{total} = {n};"
        return replacer

    def _formula_n(self, match):
        total = match.group("sum")
        n = match.group("n")
        return total, f"({n} * ({n} + 1)) / 2"

    def _formula_n_minus_1(self, match):
        total = match.group("sum")
        n = match.group("n")
        return total, f"({n} * ({n} - 1)) / 2"