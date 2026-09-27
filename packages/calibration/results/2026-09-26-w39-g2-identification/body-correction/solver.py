"""H3 global encoded minimax by monotone interval feasibility, never gradients.

For fixed code tolerance e, each channel satisfies y-e <= E(clamp(v)) <= y+e.
An interior lower limit becomes v >= D((y-e)/255); an interior upper limit
becomes v <= D((y+e)/255). Limits reaching 0/255 impose no constraint on that
side BEFORE clipping. Since v = z_B + q0*(z_R-z_B) + q1*(z_G-z_B), these are
linear inequalities in two unconstrained real coefficients per channel. Row
sums are one by construction. Bisection therefore bounds the GLOBAL optimum.

The lower endpoint carries a rational Farkas witness for the floating-point
linear inequalities: nonnegative weights, EXACT zero weighted coefficients,
and strictly negative weighted RHS. This is not a formal interval proof of
IEC transcendental arithmetic, but it does not depend on solver success flags
or approximate stationarity. The feasible upper is checked by the original
forward function. The reported bracket is in output codes, not a survival bar.
"""
from fractions import Fraction as F
from pathlib import Path
import sys
import numpy as np
from scipy.optimize import linprog

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / 'instrument'))
import body


def channel_constraints(z, target, epsilon):
    design = z[:, :2] - z[:, 2, None]
    a, b, labels = [], [], []
    for i, y in enumerate(target):
        if y + epsilon < 255:
            a.append(design[i]); b.append(float(body.decode((y + epsilon) / 255) - z[i, 2]))
            labels.append((i, 'upper'))
        if y - epsilon > 0:
            a.append(-design[i]); b.append(float(z[i, 2] - body.decode((y - epsilon) / 255)))
            labels.append((i, 'lower'))
    return np.array(a).reshape(-1, 2), np.array(b), labels


def rational_weights(a):
    """Solve A.T*w=0, sum(w)=1 exactly for a basic dual support (at most 3)."""
    n = len(a)
    rows = [[F(float(a[j, i])) for j in range(n)] + [F(0)] for i in range(2)]
    rows.append([F(1)] * n + [F(1)])
    pivots = []
    for col in range(n):
        pivot = next((i for i in range(len(pivots), 3) if rows[i][col]), None)
        if pivot is None:
            return None
        k = len(pivots); rows[k], rows[pivot] = rows[pivot], rows[k]
        value = rows[k][col]; rows[k] = [v / value for v in rows[k]]
        for i in range(3):
            if i != k:
                value = rows[i][col]
                rows[i] = [u - value * v for u, v in zip(rows[i], rows[k])]
        pivots.append(col)
    if any(all(v == 0 for v in row[:-1]) and row[-1] != 0 for row in rows):
        return None
    return [rows[i][-1] for i in range(n)]


def farkas_valid(cert):
    if cert is None:
        return False
    weights = [F(v) for v in cert['weights']]
    a = [[F(float(v)) for v in row] for row in cert['a']]
    b = [F(float(v)) for v in cert['b']]
    return (all(v >= 0 for v in weights) and sum(weights) == 1 and
            all(sum(w * row[j] for w, row in zip(weights, a)) == 0 for j in range(2)) and
            sum(w * v for w, v in zip(weights, b)) < 0)


def feasibility(z, target, epsilon):
    coefficients = []
    for channel in range(3):
        a, b, labels = channel_constraints(z, target[:, channel], epsilon)
        if len(b) == 0:
            coefficients.extend([0., 0.]); continue
        # Phase I: min slack, with the two matrix coefficients genuinely free.
        fit = linprog([0., 0., 1.], A_ub=np.column_stack((a, -np.ones(len(b)))),
                      b_ub=b, bounds=[(None, None), (None, None), (0, None)],
                      method='highs', options={'primal_feasibility_tolerance': 1e-9,
                                               'dual_feasibility_tolerance': 1e-9})
        if not fit.success:
            raise RuntimeError(f'LP failed: {fit.message}')
        support = np.flatnonzero(-fit.ineqlin.marginals > 1e-12)
        if 0 < len(support) <= 3:
            weights = rational_weights(a[support])
            if weights is not None:
                cert = dict(channel=channel, epsilonCodes=float(epsilon),
                            a=a[support].tolist(), b=b[support].tolist(),
                            constraints=[list(labels[i]) for i in support],
                            weights=[str(v) for v in weights])
                if farkas_valid(cert):
                    return None, cert
        coefficients.extend(fit.x[:2])
    return np.array(coefficients), None


def solve_h3(x, neutral, target, gap_codes=1e-5):
    x = np.asarray(x, float); target = np.asarray(target, float)
    if x.shape != target.shape or x.ndim != 2 or x.shape[1] != 3:
        raise ValueError('H3 needs matching nonempty n x 3 input and target arrays')
    if not len(x) or not np.all(np.isfinite(x)) or not np.all(np.isfinite(target)):
        raise ValueError('H3 needs finite nonempty arrays')
    if np.any(target < 0) or np.any(target > 255):
        raise ValueError('Target must be encoded codes in [0,255]')
    z = body.decode(body.h1(x, neutral))
    q = np.array([1., 0., 0., 1., 0., 0.])
    hi = float(np.max(abs(body.h3(x, neutral, q) * 255 - target)))
    lo = 0.; lower_cert = None
    for iteration in range(100):
        if hi - lo <= gap_codes:
            break
        middle = (hi + lo) / 2
        candidate, cert = feasibility(z, target, middle)
        if cert is not None:
            lo = middle; lower_cert = cert
        else:
            achieved = float(np.max(abs(body.h3(x, neutral, candidate) * 255 - target)))
            if achieved < hi:
                hi = achieved; q = candidate
            else:
                raise RuntimeError('Numerical feasibility stalled before certified bracket closed')
    else:
        raise RuntimeError('Bisection did not close')
    if lo > 0 and not farkas_valid(lower_cert):
        raise RuntimeError('Missing global lower-bound certificate')
    return dict(coefficients=q.tolist(), lowerCodes=lo, upperCodes=hi,
                bracketWidthCodes=hi-lo, lowerCertificate=lower_cert,
                certificateScope='exact rational Farkas for float64-decoded LP; forward-checked upper',
                converged=True, iterations=iteration,
                status='global minimax bracket (numerical IEC arithmetic)')
