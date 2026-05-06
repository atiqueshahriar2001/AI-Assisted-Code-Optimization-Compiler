from __future__ import annotations

import re

from ..models import OptimizationContext, Suggestion
from .base import OptimizationPass


FUNCTION_DEF_RE = re.compile(
    r'(?:int|void|float|double|char)\s+(?P<name>[A-Za-z_]\w*)\s*\(([^)]*)\)\s*\{'
    r'(?P<body>[^}]+)\}'
)
SIMPLE_FUNC_RE = re.compile(
    r'(?:int|void|float|double|char)\s+(?P<name>[A-Za-z_]\w*)\s*\(\s*\)\s*\{'
    r'(?P<body>[^}]+)\}'
)


class FunctionInliningPass(OptimizationPass):
    name = "function_inlining"
    description = "Inlines simple function calls for performance gain."

    def apply(self, context: OptimizationContext) -> None:
        func_defs = self._find_simple_functions(context.optimized)
        
        for func_name, body in func_defs.items():
            if len(body) > 50:
                continue
                
            pattern = re.compile(rf'\b{re.escape(func_name)}\s*\(\s*\)')
            matches = list(pattern.finditer(context.optimized))
            
            for match in reversed(matches):
                context.optimized = context.optimized[:match.start()] + body + context.optimized[match.end():]
                context.suggestions.append(
                    Suggestion(
                        title="Inline simple function",
                        explanation=f"Function '{func_name}' has been inlined to eliminate call overhead.",
                        before=f"{func_name}()",
                        after=body,
                        confidence=0.85,
                        strategy="function_inlining",
                        pass_name=self.name,
                        line=self._find_line(context.optimized, match.start()),
                        impact="medium",
                    )
                )

    def _find_simple_functions(self, source: str) -> dict[str, str]:
        funcs = {}
        for match in SIMPLE_FUNC_RE.finditer(source):
            name = match.group('name')
            body = match.group('body').strip()
            if ';' not in body[:-1] if body.endswith(';') else ';' not in body:
                funcs[name] = body.rstrip(';')
        return funcs

    def _find_line(self, source: str, pos: int) -> int:
        return source[:pos].count('\n') + 1