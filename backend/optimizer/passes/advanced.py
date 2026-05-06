from __future__ import annotations

import re

from ..models import OptimizationContext, Suggestion
from .base import OptimizationPass


POINTER_DEREF_RE = re.compile(r'\*([A-Za-z_]\w*)')
ADDRESS_OF_RE = re.compile(r'&([A-Za-z_]\w*)')


class PointerOptimizationPass(OptimizationPass):
    name = "pointer_optimization"
    description = "Optimizes pointer operations and dereferences."

    def apply(self, context: OptimizationContext) -> None:
        for match in POINTER_DEREF_RE.finditer(context.optimized):
            var = match.group(1)
            suggestion_text = f"Consider using array indexing syntax (arr[i]) instead of pointer arithmetic (*ptr)"
            context.suggestions.append(
                Suggestion(
                    title="Pointer access pattern",
                    explanation=suggestion_text,
                    before=f"*{var}",
                    after=f"{var}[0]",
                    confidence=0.6,
                    strategy="pointer_optimization",
                    pass_name=self.name,
                    line=context.optimized[:match.start()].count('\n') + 1,
                    impact="low",
                )
            )


class LoopInvariantPass(OptimizationPass):
    name = "loop_invariant"
    description = "Moves loop-invariant computations outside the loop."

    def apply(self, context: OptimizationContext) -> None:
        program = self.program(context)
        
        for stmt in program.statements:
            if stmt.kind != 'for_loop' or not stmt.metadata:
                continue
            
            body = stmt.metadata.get('body', '')
            condition = stmt.metadata.get('condition', '')
            init = stmt.metadata.get('init', '')
            
            invariant_exprs = self._find_invariant_expressions(body, init, condition)
            
            for expr, var_name in invariant_exprs:
                context.suggestions.append(
                    Suggestion(
                        title="Loop invariant computation",
                        explanation=f"Expression '{expr}' does not change in the loop and can be computed once outside.",
                        before=expr,
                        after=f"// Move {expr} before loop",
                        confidence=0.7,
                        strategy="loop_invariant_motion",
                        pass_name=self.name,
                        line=stmt.line,
                        impact="medium",
                    )
                )

    def _find_invariant_expressions(self, body: str, init: str, condition: str) -> list[tuple[str, str]]:
        result = []
        identifiers_in_init = set(re.findall(r'\b([A-Za-z_]\w*)\b', init))
        identifiers_in_condition = set(re.findall(r'\b([A-Za-z_]\w*)\b', condition))
        
        for match in re.finditer(r'([A-Za-z_]\w*)\s*=\s*([A-Za-z_0-9+\-*/\s]+);', body):
            var = match.group(1)
            expr = match.group(2)
            all_vars = set(re.findall(r'\b([A-Za-z_]\w*)\b', expr))
            
            loop_vars = {'i', 'j', 'k'} & all_vars
            if not loop_vars and not any(v in all_vars for v in identifiers_in_init | identifiers_in_condition):
                result.append((expr, var))
        
        return result


class ArrayBoundsCheckElimination(OptimizationPass):
    name = "bounds_check_elimination"
    description = "Eliminates redundant bounds checks in array accesses."

    def apply(self, context: OptimizationContext) -> None:
        array_access = re.compile(r'([A-Za-z_]\w*)\[([A-Za-z_0-9+\-*/\s]+)\]')
        
        for match in array_access.finditer(context.optimized):
            arr = match.group(1)
            idx = match.group(2)
            
            if re.match(r'^\s*\d+\s*$', idx.strip()):
                context.suggestions.append(
                    Suggestion(
                        title="Literal array index",
                        explanation=f"Array access with literal index can be optimized at compile time if bounds are known.",
                        before=f"{arr}[{idx}]",
                        after=f"{arr}[{idx.strip()}]",
                        confidence=0.8,
                        strategy="bounds_check_optimization",
                        pass_name=self.name,
                        line=context.optimized[:match.start()].count('\n') + 1,
                        impact="low",
                    )
                )


class InductionVariablePass(OptimizationPass):
    name = "induction_variable"
    description = "Optimizes induction variables in loops."

    def apply(self, context: OptimizationContext) -> None:
        program = self.program(context)
        
        for stmt in program.statements:
            if stmt.kind != 'for_loop' or not stmt.metadata:
                continue
            
            init = stmt.metadata.get('init', '')
            condition = stmt.metadata.get('condition', '')
            update = stmt.metadata.get('update', '')
            body = stmt.metadata.get('body', '')
            
            if 'i = i +' in update or 'i += ' in update:
                linear_uses = re.findall(r'\b([A-Za-z_]\w*)\s*\*\s*i\s*\+', body)
                linear_uses += re.findall(r'i\s*\*\s*([A-Za-z_]\w*)', body)
                
                for coeff in linear_uses:
                    context.suggestions.append(
                        Suggestion(
                            title="Linear induction expression",
                            explanation="Linear expressions in loops can use strength reduction with incremental updates.",
                            before=f"{coeff}*i",
                            after=f"// incremental update",
                            confidence=0.75,
                            strategy="induction_variable_optimization",
                            pass_name=self.name,
                            line=stmt.line,
                            impact="medium",
                        )
                    )