"""Fit the declared encoded TARGET chart to exposed uniform observations.

This is an analytical initializer/identification diagnostic, not a rendered verdict. The
complete material, current references, structured scenes, both tiers and the one exposure
still require their independent referees. In particular, this does not infer native data at
unobserved knots, add a DPR coefficient, or identify a spatial operator.
"""
import math
import numpy as np
from scipy.optimize import Bounds, LinearConstraint, linprog, minimize

ROWS = (44, 96, 160)
KNOTS = (0, 8, 28, 40)
TOLERANCE_CODES = 1e-8


def number(value):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        raise ValueError('Expected a finite numerical observation')
    return float(value)


def weights(input_code, span):
    """Twelve bilinear weights through code40; the actual-span64 join is separate."""
    x, span = number(input_code), number(span)
    if not 0 <= x <= 40 or not 32 <= span <= 224:
        raise ValueError('Observation is outside the declared target-chart domain')
    row = 0 if span < 96 else 1
    st = min(1, max(0, (span - ROWS[row]) / (ROWS[row + 1] - ROWS[row])))
    knot = 0 if x <= 8 else 1 if x <= 28 else 2
    xt = (x - KNOTS[knot]) / (KNOTS[knot + 1] - KNOTS[knot])
    result = np.zeros(12)
    for r, sw in ((row, 1 - st), (row + 1, st)):
        result[r * 4 + knot] += sw * (1 - xt)
        result[r * 4 + knot + 1] += sw * xt
    return result


def fit(readings, *, joins):
    """Minimax, then mean absolute error, then squared normalized ordinate distance.

    Each reading is one support/channel observation, in encoded output codes. Repeated
    equal observations retain their multiplicity in the mean-error objective. `joins`
    supplies OLD-law code64 outputs evaluated at actual spans and scales by the production
    oracle; they are constraints, never fitted coefficients. The caller must bind the full
    required observation population and its provenance before calling this pure solver.
    """
    if not readings or not joins:
        raise ValueError('Missing exposed observations or fixed-join constraints')
    data = []
    for obs in readings:
        if obs.get('role') not in ('calibration', 'validation'):
            raise ValueError('Only native calibration/validation may identify the chart')
        y = number(obs['value'])
        if not 0 <= y <= 255:
            raise ValueError('Native encoded observation outside [0,255]')
        data.append(np.r_[weights(obs['inputCode'], obs['span']), y])
    unique, counts = np.unique(np.asarray(data), axis=0, return_counts=True)
    a, y = unique[:, :12], unique[:, 12]
    count = len(y)
    constraints, limits = [], []
    for row in range(3):
        for knot in range(3):
            c = np.zeros(12)
            c[row * 4 + knot], c[row * 4 + knot + 1] = 1, -1
            constraints.append(c)
            limits.append(0)
    for join in joins:
        value = number(join['value'])
        if not 0 <= value <= 255:
            raise ValueError('Invalid fixed old-law join')
        constraints.append(weights(40, join['span']))
        limits.append(value)
    g, h = np.asarray(constraints), np.asarray(limits)
    first_a = np.vstack((np.c_[a, -np.ones(count)], np.c_[-a, -np.ones(count)],
                         np.c_[g, np.zeros(len(g))]))
    first_b = np.r_[y, -y, h]
    options = dict(primal_feasibility_tolerance=1e-9, dual_feasibility_tolerance=1e-9)
    first = linprog(np.r_[np.zeros(12), 1], A_ub=first_a, b_ub=first_b,
                    bounds=[(0, 255)] * 12 + [(0, None)], method='highs', options=options)
    if not first.success:
        raise ValueError('Target-chart minimax solve failed: ' + first.message)
    worst = float(first.x[-1])
    second_a = np.vstack((np.c_[a, -np.eye(count)], np.c_[-a, -np.eye(count)],
                          np.c_[g, np.zeros((len(g), count))]))
    second_b = np.r_[y, -y, h]
    mean_objective = np.r_[np.zeros(12), counts / counts.sum()]
    upper = np.r_[np.full(12, 255.), np.full(count, worst + TOLERANCE_CODES)]
    second = linprog(mean_objective, A_ub=second_a, b_ub=second_b,
                     bounds=list(zip(np.zeros(12 + count), upper)), method='highs', options=options)
    if not second.success:
        raise ValueError('Target-chart mean-error solve failed: ' + second.message)
    third_a = np.vstack((second_a, mean_objective))
    third_b = np.r_[second_b, second.fun + TOLERANCE_CODES]
    objective = lambda v: float(np.dot(v[:12], v[:12]) / 255 ** 2)
    jacobian = lambda v: np.r_[2 * v[:12] / 255 ** 2, np.zeros(count)]
    third = minimize(objective, second.x, jac=jacobian, method='SLSQP',
                     bounds=Bounds(np.zeros(12 + count), upper),
                     constraints=LinearConstraint(third_a, -np.inf, third_b),
                     options=dict(ftol=1e-12, maxiter=2000))
    if not third.success or np.max(third_a @ third.x - third_b) > 1e-7:
        raise ValueError('Target-chart distance tie-break failed: ' + third.message)
    # Remove sub-roundoff ordering noise before strict material tuple validation. Recheck all
    # constraints and objective tolerances; this is not a native or renderer error allowance.
    code_rows = np.maximum.accumulate(third.x[:12].reshape(3, 4), axis=1)
    coefficients = code_rows.ravel()
    errors = np.abs(a @ coefficients - y)
    if (np.max(g @ coefficients - h) > 1e-7 or errors.max() > worst + 1e-7 or
            np.average(errors, weights=counts) > second.fun + 1e-7):
        raise ValueError('Numerical polishing moved the identified solution')
    return dict(kind='analytical-chart-target-fit-not-rendered-verdict',
                rows=(code_rows / 255).tolist(), observations=len(data),
                worstErrorCodes=float(errors.max()),
                meanAbsoluteErrorCodes=float(np.average(errors, weights=counts)),
                squaredNormalizedDistance=float(np.dot(coefficients, coefficients) / 255 ** 2),
                minimaxLowerBoundCodes=worst, meanLowerBoundCodes=float(second.fun),
                numericalToleranceCodes=TOLERANCE_CODES)
