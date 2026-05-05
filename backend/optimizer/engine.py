from __future__ import annotations

from dataclasses import asdict

from optimizer.analysis import analyze_program
from optimizer.models import OptimizationContext
from optimizer.parser import parse_program
from optimizer.passes import DEFAULT_PASSES


def optimize_code(source: str, enabled_passes: list[str] | None = None) -> dict:
    normalized = source.strip()
    context = OptimizationContext(source=normalized, optimized=normalized)
    enabled = set(enabled_passes or [item.name for item in DEFAULT_PASSES])
    source_analysis = analyze_program(parse_program(normalized))

    for optimization_pass in DEFAULT_PASSES:
        if optimization_pass.name in enabled:
            optimization_pass.run(context)
        else:
            context.pass_reports.append(
                {
                    "name": optimization_pass.name,
                    "description": optimization_pass.description,
                    "changes": 0,
                    "enabled": False,
                }
            )

    optimized_analysis = analyze_program(parse_program(context.optimized))
    score = calculate_score(context)

    return {
        "optimized_code": context.optimized,
        "suggestions": [asdict(item) for item in context.suggestions],
        "score": score,
        "analysis": source_analysis,
        "optimized_analysis": optimized_analysis,
        "passes": [
            asdict(item) if hasattr(item, "__dataclass_fields__") else item
            for item in context.pass_reports
        ],
    }


def calculate_score(context: OptimizationContext) -> int:
    if not context.suggestions:
        return 25

    impact_points = {"low": 7, "medium": 13, "high": 22}
    confidence_bonus = sum(int(item.confidence * 6) for item in context.suggestions)
    impact_bonus = sum(impact_points.get(item.impact, 10) for item in context.suggestions)
    return min(100, 25 + confidence_bonus + impact_bonus)
