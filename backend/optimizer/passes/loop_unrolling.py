from __future__ import annotations

import re

from ..models import OptimizationContext, Suggestion
from .base import OptimizationPass


LOOP_UNROLL_RE = re.compile(
    r'for\s*\(\s*(?:int\s+)?(?P<var>[A-Za-z_]\w*)\s*=\s*(?P<start>\d+)\s*;\s*'
    r'(?P<var2>[A-Za-z_]\w*)\s*(?P<cond><=|>=)\s*(?P<limit>\d+)\s*;\s*'
    r'(?P=var)\s*\+\+\s*\)'
    r'\s*\{\s*(?P<body>[^{}]+)\s*\}',
    re.DOTALL
)


class LoopUnrollingPass(OptimizationPass):
    name = "loop_unrolling"
    description = "Unrolls simple counted loops for performance."

    def apply(self, context: OptimizationContext) -> None:
        def replace_loop(match: re.Match[str]) -> str:
            var = match.group('var')
            start = int(match.group('start'))
            limit = int(match.group('limit'))
            body = match.group('body').strip()
            cond = match.group('cond')
            
            if cond != '<=' or limit - start > 8:
                return match.group(0)
            
            iterations = limit - start + 1
            unrolled = []
            for i in range(iterations):
                unrolled_body = body.replace(var, str(start + i))
                unrolled.append(f"    {unrolled_body}")
            
            result = f"/* Unrolled loop */\n" + "\n".join(unrolled)
            
            line = context.optimized[: match.start()].count("\n") + 1
            context.suggestions.append(
                Suggestion(
                    title="Unroll simple loop",
                    explanation=f"Loop unrolled {iterations} times to eliminate loop overhead.",
                    before=match.group(0),
                    after=result,
                    confidence=0.80,
                    strategy="loop_unrolling",
                    pass_name=self.name,
                    line=line,
                    impact="high",
                )
            )
            return result

        context.optimized = LOOP_UNROLL_RE.sub(replace_loop, context.optimized)