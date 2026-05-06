from __future__ import annotations

from abc import ABC, abstractmethod

from ..models import OptimizationContext, PassReport
from ..c_parser import parse_c_code


class OptimizationPass(ABC):
    name: str
    description: str

    def run(self, context: OptimizationContext) -> None:
        before = len(context.suggestions)
        optimized_before = context.optimized
        self.apply(context)
        context.pass_reports.append(
            PassReport(
                name=self.name,
                description=self.description,
                changes=max(
                    len(context.suggestions) - before,
                    int(context.optimized != optimized_before),
                ),
            )
        )

    @abstractmethod
    def apply(self, context: OptimizationContext) -> None:
        raise NotImplementedError

    def program(self, context: OptimizationContext):
        return parse_c_code(context.optimized)
