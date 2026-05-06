from .base import OptimizationPass
from .constant_folding import ConstantFoldingPass
from .dead_code import DeadAssignmentPass
from .loop_patterns import LoopPatternPass
from .strength_reduction import StrengthReductionPass
from .syntax_simplification import SyntaxSimplificationPass
from .function_inlining import FunctionInliningPass
from .loop_unrolling import LoopUnrollingPass
from .cse import CommonSubexpressionEliminationPass
from .algebraic import AlgebraicSimplificationPass
from .advanced import PointerOptimizationPass, LoopInvariantPass, ArrayBoundsCheckElimination, InductionVariablePass

DEFAULT_PASSES: list[OptimizationPass] = [
    ConstantFoldingPass(),
    StrengthReductionPass(),
    LoopPatternPass(),
    SyntaxSimplificationPass(),
    DeadAssignmentPass(),
    FunctionInliningPass(),
    LoopUnrollingPass(),
    CommonSubexpressionEliminationPass(),
    AlgebraicSimplificationPass(),
    PointerOptimizationPass(),
    LoopInvariantPass(),
    ArrayBoundsCheckElimination(),
    InductionVariablePass(),
]