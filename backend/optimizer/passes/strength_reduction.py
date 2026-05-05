from __future__ import annotations

import re

from optimizer.models import OptimizationContext, Suggestion
from optimizer.passes.base import OptimizationPass


POWER_TWO_RE = re.compile(
    r"^(?:(?P<value_left>[A-Za-z_]\w*)\s*\*\s*(?P<constant_right>2|4|8|16|32|64)|"
    r"(?P<constant_left>2|4|8|16|32|64)\s*\*\s*(?P<value_right>[A-Za-z_]\w*))$"
)


class StrengthReductionPass(OptimizationPass):
    name = "strength_reduction"
    description = "Replaces expensive arithmetic with equivalent cheaper operations."

    def apply(self, context: OptimizationContext) -> None:
        program = self.program(context)

        for statement in program.statements:
            if statement.kind != "assignment" or not statement.expression or not statement.target:
                continue

            match = POWER_TWO_RE.match(statement.expression)
            if not match:
                continue

            constant = int(match.group("constant_right") or match.group("constant_left"))
            value = match.group("value_left") or match.group("value_right")
            shift = constant.bit_length() - 1
            after = f"{statement.target} = {value} << {shift};"
            context.optimized = context.optimized.replace(statement.text, after, 1)
            context.suggestions.append(
                Suggestion(
                    title="Use shift for power-of-two multiplication",
                    explanation="Multiplication by a power of two can be represented as a left shift in low-level code.",
                    before=statement.text,
                    after=after,
                    confidence=0.78,
                    strategy="strength_reduction",
                    pass_name=self.name,
                    line=statement.line,
                    impact="medium",
                )
            )
