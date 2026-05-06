from __future__ import annotations

import re

from ..models import OptimizationContext, Suggestion
from .base import OptimizationPass


TYPE_DECL = r"(?:int|long|float|double|char|short)\s+"

SUMMATION_RE = re.compile(
    rf"(?:(?:{TYPE_DECL})?(?P<sum>\w+)\s*=\s*0\s*;)"
    rf"\s*for\s*\(\s*(?:(?:{TYPE_DECL})?(?P<i1>\w+)\s*=\s*1\s*;\s*(?P<i2>\w+)\s*<=\s*(?P<n>\w+)\s*;\s*(?P<inc>(?P<i3>\w+)\s*\+\+|(?P<i4>\w+)\s*\+=\s*1|(?P<i5>\w+)\s*=\s*(?P<i6>\w+)\s*\+\s*1))\s*\)\s*\{{"
    r"\s*(?P<sum2>\w+)\s*(?:=\s*(?P<sum3>\w+)\s*\+\s*(?P<i7>\w+)|\+=\s*(?P<i8>\w+))\s*;?\s*"
    r"\}",
    re.DOTALL,
)

SUMMATION_RE_MULTILINE = re.compile(
    rf"(?:(?:{TYPE_DECL})?(?P<sum>\w+)\s*=\s*0\s*;)"
    r".*?"
    rf"for\s*\(\s*(?:(?:{TYPE_DECL})?(?P<i1>\w+)\s*=\s*1\s*;\s*(?P<i2>\w+)\s*<=\s*(?P<n>\w+)\s*;\s*(?P<inc>(?P<i3>\w+)\s*\+\+|(?P<i4>\w+)\s*\+=\s*1|(?P<i5>\w+)\s*=\s*(?P<i6>\w+)\s*\+\s*1))\s*\)\s*\{{"
    r".*?"
    r"\s*(?P<sum2>\w+)\s*(?:=\s*(?P<sum3>\w+)\s*\+\s*(?P<i7>\w+)|\+=\s*(?P<i8>\w+))\s*;?\s*"
    r"\}",
    re.DOTALL,
)

SUMMATION_RE_ALT = re.compile(
    rf"(?:(?:{TYPE_DECL})?(?P<sum>\w+)\s*=\s*0\s*;)"
    r".*?"
    rf"for\s*\(\s*(?:(?:{TYPE_DECL})?(?P<i1>\w+)\s*=\s*0\s*;\s*(?P<i2>\w+)\s*<\s*(?P<n>\w+)\s*;\s*(?P<inc>(?P<i3>\w+)\s*\+\+|(?P<i4>\w+)\s*\+=\s*1|(?P<i5>\w+)\s*=\s*(?P<i6>\w+)\s*\+\s*1))\s*\)\s*\{{"
    r".*?"
    r"\s*(?P<sum2>\w+)\s*(?:=\s*(?P<sum3>\w+)\s*\+\s*(?P<i7>\w+)|\+=\s*(?P<i8>\w+))\s*;?\s*"
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
            if not self._is_valid_sum_loop(match):
                return match.group(0)

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

    def _is_valid_sum_loop(self, match):
        sum_var = match.group("sum")
        if match.group("sum2") != sum_var:
            return False

        sum3 = match.group("sum3")
        if sum3 and sum3 != sum_var:
            return False

        first_var = match.group("i1")
        if first_var != match.group("i2"):
            return False

        loop_var = match.group("i3") or match.group("i4") or match.group("i5")
        if not loop_var:
            return False

        if match.group("i5") and match.group("i6") != loop_var:
            return False

        body_var = match.group("i7") or match.group("i8")
        if body_var != loop_var:
            return False

        return True

    def _formula_n(self, match):
        total = match.group("sum")
        n = match.group("n")
        return total, f"({n} * ({n} + 1)) / 2"

    def _formula_n_minus_1(self, match):
        total = match.group("sum")
        n = match.group("n")
        return total, f"({n} * ({n} - 1)) / 2"
