from optimizer.passes.base import OptimizationPass
from optimizer.passes.constant_folding import ConstantFoldingPass
from optimizer.passes.dead_code import DeadAssignmentPass
from optimizer.passes.loop_patterns import LoopPatternPass
from optimizer.passes.strength_reduction import StrengthReductionPass
from optimizer.passes.syntax_simplification import SyntaxSimplificationPass


DEFAULT_PASSES: list[OptimizationPass] = [
    LoopPatternPass(),
    ConstantFoldingPass(),
    StrengthReductionPass(),
    SyntaxSimplificationPass(),
    DeadAssignmentPass(),
]

