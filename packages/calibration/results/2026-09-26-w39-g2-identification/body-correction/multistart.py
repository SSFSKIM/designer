"""Bounded deterministic search; a converged candidate is NOT a global minimum.

Every supplied start is retained in the report. We optimize the encoded-error
upper envelope directly from each start, avoiding the mandatory LS funnel that
can move all starts to the same clipped plateau. Parameters and epigraph
feasibility are checked independently of SLSQP's status. The start list and
iteration cap are numerical execution choices, not family or closure changes.
"""
import numpy as np
from scipy.optimize import minimize
from scipy.optimize._numdiff import approx_derivative


def diagnostics(forward, target, q):
    residual = np.asarray(forward(q)) - target
    j = approx_derivative(lambda p: np.asarray(forward(p)).ravel(), q).reshape(target.size, len(q))
    return dict(coefficients=np.asarray(q).tolist(), rss=float(np.sum(residual**2)),
                meanSquared=float(np.mean(residual**2)), maximum=float(np.max(abs(residual))),
                rank=int(np.linalg.matrix_rank(j)), columns=len(q),
                singularValues=np.linalg.svd(j, compute_uv=False).tolist())


def fit_multistart(forward, target, starts, bounds=None, monotone_start=None):
    target = np.asarray(target, float)
    bounds = bounds or [(None, None)] * len(starts[0])
    def residual(q):
        return (np.asarray(forward(q)) - target).ravel()
    def feasible(q):
        return (all((lo is None or v >= lo - 1e-10) and
                    (hi is None or v <= hi + 1e-10) for v, (lo, hi) in zip(q, bounds)) and
                (monotone_start is None or np.min(np.diff(q[monotone_start:])) >= -1e-10))
    results = []
    for index, initial in enumerate(starts):
        start = np.r_[initial, np.max(abs(residual(initial))) + 1e-8]
        constraints = [dict(type='ineq', fun=lambda p:
            np.r_[p[-1] - residual(p[:-1]), p[-1] + residual(p[:-1])])]
        if monotone_start is not None:
            constraints.append(dict(type='ineq', fun=lambda p: np.diff(p[monotone_start:-1])))
        fit = minimize(lambda p: p[-1], start, method='SLSQP',
                       bounds=[*bounds, (0, None)], constraints=constraints,
                       options=dict(ftol=1e-12, maxiter=1000))
        q = fit.x[:-1]
        maximum = float(np.max(abs(residual(q))))
        report = diagnostics(forward, target, q)
        report.update(startIndex=index, initial=np.asarray(initial).tolist(),
                      optimizerSuccess=bool(fit.success), parameterFeasible=bool(feasible(q)),
                      epigraphGap=maximum-float(fit.x[-1]), iterations=int(fit.nit),
                      message=str(fit.message),
                      converged=bool(fit.success and feasible(q) and maximum-fit.x[-1] <= 1e-8))
        results.append(report)
    admitted = [r for r in results if r['converged']]
    if not admitted:
        raise RuntimeError('No converged parameter-feasible multistart candidate')
    chosen = min(admitted, key=lambda r: (r['maximum'], r['startIndex']))
    return dict(**chosen, starts=results,
                classification='converged local nonlinear minimax candidate; global minimum not certified',
                numericalBudget=dict(maxIterationsPerStart=1000, ftol=1e-12))
