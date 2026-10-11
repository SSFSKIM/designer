"""W52-DL1 numerical comparisons, independent of scientific error allowances.

The tolerance is 64 binary64 ulps at the largest source operand, with a scale
floor of one in the component's declared units. Level operands are encoded
codes; texture operands are normalized linear-light standard deviations. This
is a prospective comparator convention, not a fitted budget or an error bound
for the renderer/estimator. The floor prevents near-zero arithmetic from having
zero practical headroom; even at 255 codes the allowance is below 2e-12 codes.

Callers include native/current/candidate values used in a subtraction, not only
its smaller residual. Comparisons after a bound override use the same function.
Hashes, source/value authentication, categorical statuses and the exact held-64
identity are not scientific inequalities and keep their existing exact checks.
Owner referee verdicts and aggregate laws remain source-owned and unchanged.
"""
from __future__ import annotations

import math

COMPARISON_ULPS = 64


def epsilon(*operands: float) -> float:
    """Return the declared allowance in the same units as finite operands."""
    if not operands or not all(math.isfinite(value) for value in operands):
        raise ValueError('comparison requires finite source operands')
    return COMPARISON_ULPS * math.ulp(max(1.0, *(abs(value) for value in operands)))


def less_equal(value: float, bound: float, *source_operands: float) -> bool:
    """Apply inclusive scientific bounds without a floating-point false miss."""
    return value <= bound + epsilon(value, bound, *source_operands)
