from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Suggestion:
    title: str
    explanation: str
    before: str
    after: str
    confidence: float
    strategy: str
    pass_name: str
    line: int | None = None
    impact: str = "medium"


@dataclass
class Statement:
    kind: str
    text: str
    line: int
    target: str | None = None
    expression: str | None = None
    metadata: dict[str, str] = field(default_factory=dict)


@dataclass
class Program:
    source: str
    statements: list[Statement]


@dataclass
class PassReport:
    name: str
    description: str
    changes: int
    enabled: bool = True


@dataclass
class OptimizationContext:
    source: str
    optimized: str
    suggestions: list[Suggestion] = field(default_factory=list)
    pass_reports: list[PassReport] = field(default_factory=list)