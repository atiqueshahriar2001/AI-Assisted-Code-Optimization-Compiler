from __future__ import annotations

import re

from ..models import OptimizationContext, Suggestion
from .base import OptimizationPass


class AlgebraicSimplificationPass(OptimizationPass):
    name = "algebraic_simplification"
    description = "Applies algebraic identities to simplify expressions."

    def apply(self, context: OptimizationContext) -> None:
        patterns = [
            (r'x\s*\*\s*1', 'x', "Multiplication by 1 identity"),
            (r'x\s*\*\s*0', '0', "Multiplication by 0 identity"),
            (r'x\s*\+ 0', 'x', "Addition of 0 identity"),
            (r'x\s*-\s*0', 'x', "Subtraction of 0 identity"),
            (r'x\s*/\s*1', 'x', "Division by 1 identity"),
            (r'x\s*\+\s*x', 'x * 2', "Addition of variable to itself"),
            (r'x\s*-\s*x', '0', "Subtraction of variable from itself"),
        ]
        
        for pattern, replacement, explanation in patterns:
            def make_replacer(repl, expl):
                def replacer(match):
                    return repl
                return replacer
            
            for match in re.finditer(pattern, context.optimized):
                start, end = match.span()
                before = match.group(0)
                after = re.sub(pattern, replacement, before)
                
                if before != after:
                    context.optimized = context.optimized[:start] + after + context.optimized[end:]
                    context.suggestions.append(
                        Suggestion(
                            title="Algebraic simplification",
                            explanation=explanation,
                            before=before,
                            after=after,
                            confidence=0.90,
                            strategy="algebraic_simplification",
                            pass_name=self.name,
                            line=context.optimized[:start].count("\n") + 1,
                            impact="low",
                        )
                    )