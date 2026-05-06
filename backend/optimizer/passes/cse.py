from __future__ import annotations

import re
from collections import defaultdict

from ..models import OptimizationContext, Suggestion
from .base import OptimizationPass


class CommonSubexpressionEliminationPass(OptimizationPass):
    name = "cse"
    description = "Eliminates redundant computations of the same expression."

    def apply(self, context: OptimizationContext) -> None:
        program = self.program(context)
        
        loop_vars = set()
        for stmt in program.statements:
            if stmt.kind == 'for_loop' and stmt.metadata:
                body = stmt.metadata.get('body', '')
                update = stmt.metadata.get('update', '')
                init = stmt.metadata.get('init', '')
                for match in re.finditer(r'\b(i|j|k)\b', init + update + body):
                    loop_vars.add(match.group(1))
        
        seen_expressions = {}
        
        for statement in program.statements:
            if statement.kind != 'assignment' or not statement.target or not statement.expression:
                continue
            
            expr = statement.expression.strip()
            
            if len(expr) < 3 or len(expr) > 20:
                continue
            
            if any(var in re.findall(r'\b\w+\b', expr) for var in loop_vars):
                continue
            
            if expr in seen_expressions:
                prev_target, prev_text = seen_expressions[expr]
                context.suggestions.append(
                    Suggestion(
                        title="Common subexpression elimination",
                        explanation=f"Expression '{expr}' computed multiple times - could use previous result.",
                        before=expr,
                        after=f"// reuse {prev_target}",
                        confidence=0.7,
                        strategy="cse",
                        pass_name=self.name,
                        line=statement.line,
                        impact="low",
                    )
                )
            else:
                seen_expressions[expr] = (statement.target, statement.text)