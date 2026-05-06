from __future__ import annotations

import re

from ..models import OptimizationContext, Suggestion
from .base import OptimizationPass


FUNCTION_DEF_RE = re.compile(
    r'(?:int|void|float|double|char)\s+(?P<name>[A-Za-z_]\w*)\s*\((?P<params>[^)]*)\)\s*\{'
    r'(?P<body>[^}]+)\}',
    re.DOTALL,
)


class FunctionInliningPass(OptimizationPass):
    name = "function_inlining"
    description = "Inlines simple function calls for performance gain."

    def apply(self, context: OptimizationContext) -> None:
        func_defs = self._find_simple_functions(context.optimized)

        for func_name, func_info in func_defs.items():
            params, body = func_info
            if len(body) > 120:
                continue

            pattern = re.compile(rf'\b{re.escape(func_name)}\s*\((?P<args>[^)]*)\)')
            matches = list(pattern.finditer(context.optimized))

            for match in reversed(matches):
                call_span = context.optimized[match.start():match.end()]
                after_call = context.optimized[match.end():].lstrip()
                if after_call.startswith("{"):
                    continue

                replacement = self._inline_call(body, params, match.group("args"))
                if replacement is None:
                    continue

                context.optimized = context.optimized[:match.start()] + replacement + context.optimized[match.end():]
                context.suggestions.append(
                    Suggestion(
                        title="Inline simple function",
                        explanation=f"Function '{func_name}' has been inlined to eliminate call overhead.",
                        before=call_span,
                        after=replacement,
                        confidence=0.85,
                        strategy="function_inlining",
                        pass_name=self.name,
                        line=self._find_line(context.optimized, match.start()),
                        impact="medium",
                    )
                )

    def _find_simple_functions(self, source: str) -> dict[str, tuple[list[str], str]]:
        funcs: dict[str, tuple[list[str], str]] = {}
        for match in FUNCTION_DEF_RE.finditer(source):
            name = match.group("name")
            params = [p.strip() for p in match.group("params").split(",") if p.strip()]
            body = match.group("body").strip()
            if body.startswith("return ") and body.endswith(";"):
                expression = body[len("return ") : -1].strip()
                funcs[name] = (params, expression)
        return funcs

    def _inline_call(self, body: str, params: list[str], args_text: str) -> str | None:
        args = [arg.strip() for arg in args_text.split(",")] if args_text.strip() else []
        if len(args) != len(params):
            return None

        inlined = body
        for param, arg in zip(params, args):
            param_name = param.split()[-1]
            inlined = re.sub(rf'\b{re.escape(param_name)}\b', f'({arg})', inlined)

        return f"({inlined})"

    def _find_line(self, source: str, pos: int) -> int:
        return source[:pos].count("\n") + 1