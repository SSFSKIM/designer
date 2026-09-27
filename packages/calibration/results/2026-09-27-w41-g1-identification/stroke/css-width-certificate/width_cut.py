"""Exact CSS-width occupancy necessary cut on identical uniform top straights.

Every channel/input gets an arbitrary real z = A(top)*(S(b)-b), relaxing all
three materials, their bounds and coupling. No numerical optimizer is used.
All strict-support threshold points and open intervals are evaluated separately.
Feasibility of this relaxation is not survival of any material or geometry.
"""
from fractions import Fraction as F


def states(threshold_groups):
    """Complete partition of [0,2] for the finite predicates 0<d/scale<w.

    A predicate can change only at its threshold. Distinct sorted thresholds
    partition the real width interval into singleton points and open intervals;
    every predicate is constant on each open interval. Midpoints represent
    those intervals exactly; equality is deliberately excluded at each point.
    """
    points = sorted({F(0), F(2), *(F(t) for ts in threshold_groups.values()
                                  for t in ts if 0 <= F(t) <= 2)})
    out = []
    for i, p in enumerate(points):
        out.append(dict(kind='point', lower=str(p), upper=str(p), representative=str(p)))
        if i+1 < len(points):
            q = points[i+1]
            out.append(dict(kind='open', lower=str(p), upper=str(q),
                            representative=str((p+q)/2)))
    return out


def fraction(thresholds, width):
    ts = list(map(F, thresholds))
    if not ts:
        raise ValueError('empty sample population')
    w = F(width)
    if not 0 <= w <= 2:
        raise ValueError('width outside declared interval')
    return F(sum(0 < t < w for t in ts), len(ts))


def intersect(rows, fractions):
    """Intersect f*z departure intervals, keeping exact infeasibility witnesses.

    None is an unbounded side. Each row's interval already reflects an exact
    Jensen constraint or hard censor rail, never a signed-error substitute.
    """
    lower = upper = None
    lower_row = upper_row = None
    for i, row in enumerate(rows):
        f = F(fractions[row['geometry']])
        lo = None if row['lower'] is None else F(row['lower'])
        hi = None if row['upper'] is None else F(row['upper'])
        if f < 0:
            raise ValueError('coverage fraction negative')
        if f == 0:
            if (lo is not None and lo > 0) or (hi is not None and hi < 0):
                return dict(feasible=False, reason='zero-coverage-outside-required-interval',
                            row=i, fraction='0', lower=row['lower'], upper=row['upper'])
            continue
        if lo is not None and (lower is None or lo/f > lower):
            lower, lower_row = lo/f, i
        if hi is not None and (upper is None or hi/f < upper):
            upper, upper_row = hi/f, i
    if lower is not None and upper is not None and lower > upper:
        return dict(feasible=False, reason='disjoint-z-intervals', lower=str(lower),
                    upper=str(upper), lowerRow=lower_row, upperRow=upper_row,
                    separation=str(lower-upper))
    witness = max(F(0), lower) if lower is not None else min(F(0), upper) if upper is not None else F(0)
    if upper is not None:
        witness = min(witness, upper)
    if lower is not None:
        witness = max(witness, lower)
    for row in rows:
        value = F(fractions[row['geometry']])*witness
        assert row['lower'] is None or F(row['lower']) <= value
        assert row['upper'] is None or value <= F(row['upper'])
    return dict(feasible=True, lower=None if lower is None else str(lower),
                upper=None if upper is None else str(upper), witnessZ=str(witness))


def solve(threshold_groups, groups):
    """Width is shared across independent relaxed z groups (input and channel)."""
    outcomes = []
    for state in states(threshold_groups):
        fractions = {k: str(fraction(v, state['representative'])) for k,v in threshold_groups.items()}
        intersections = {k:intersect(v, fractions) for k,v in groups.items()}
        outcomes.append(dict(**state, fractions=fractions, groups=intersections,
                             feasible=all(v['feasible'] for v in intersections.values())))
    feasible = [i for i, v in enumerate(outcomes) if v['feasible']]
    return dict(status='CERTIFIED_INFEASIBLE_RELAXATION' if not feasible else 'NOT_REJECTED_BY_RELAXATION',
                stateCount=len(outcomes), pointCount=sum(v['kind']=='point' for v in outcomes),
                openIntervalCount=sum(v['kind']=='open' for v in outcomes),
                feasibleStateIndices=feasible, states=outcomes)
