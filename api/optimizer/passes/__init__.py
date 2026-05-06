from .base import OptimizationPass
from .constant_folding import ConstantFoldingPass
from .dead_code import DeadAssignmentPass
from .loop_patterns import LoopPatternPass
from .strength_reduction import StrengthReductionPass
from .syntax_simplification import SyntaxSimplificationPass


DEFAULT_PASSES: list[OptimizationPass] = [
    LoopPatternPass(),
    ConstantFoldingPass(),
    StrengthReductionPass(),
    SyntaxSimplificationPass(),
    DeadAssignmentPass(),
]