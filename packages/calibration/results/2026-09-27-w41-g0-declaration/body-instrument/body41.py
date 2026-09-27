"""W41 clause 4 numerical body instrument (§5.191); arrays only, no native I/O.

All public RGB inputs/outputs and neutral ordinates are encoded 0..255 codes.
Each call fits ONE endpoint; callers pool its scales, never endpoints. Observed
channels <=5 or >=250 are hard rails, independent of minimax epsilon. A bracket
certifies the float64 linear inequalities, not interval IEC/OKLab arithmetic.
Nonlinear fits are explicitly LOCAL and retain all sixteen deterministic starts.
"""
import importlib.util
from fractions import Fraction as F
from itertools import combinations
from pathlib import Path
import numpy as np
from scipy.optimize import least_squares, linprog, minimize
from scipy.optimize._numdiff import approx_derivative

# Reuse the immutable W39 colour implementation without importing a native reader.
_COLOUR_PATH = (Path(__file__).resolve().parents[2] /
                '2026-09-26-w39-g2-identification/instrument/body.py')
_spec = importlib.util.spec_from_file_location('w39_body_colour', _COLOUR_PATH)
colour = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(colour)
KNOTS = np.array([40, 56, 72, 88, 104, 128, 150.])
SIZES = {'E3': 3, 'EH6': 6, 'O12': 12}
MAX_DUAL_RECOVERY_ATTEMPTS = 2048
DUAL_EXTRA_OBSERVATIONS = 8
LP_MAXITER = 10000


def _rgb(x):
    x = np.asarray(x, float)
    if x.ndim != 2 or x.shape[1] != 3 or not len(x):
        raise ValueError('Expected a nonempty n x 3 array')
    if not np.all(np.isfinite(x)) or np.any((x < 0) | (x > 255)):
        raise ValueError('RGB must be finite encoded codes in [0,255]')
    return x


def _inputs(family, x, neutral):
    if family not in SIZES:
        raise ValueError('Undeclared body family')
    x = _rgb(x); neutral = np.asarray(neutral, float)
    if neutral.shape != (7,) or not np.all(np.isfinite(neutral)):
        raise ValueError('Seven finite neutral ordinates required')
    if np.any((neutral < 0) | (neutral > 255)):
        raise ValueError('Neutral ordinates must be codes in [0,255]')
    return x, neutral


def _weights(values, nodes):
    """Linear interpolation with held endpoints, returned as a design matrix."""
    values = np.clip(values, nodes[0], nodes[-1])
    i = np.clip(np.searchsorted(nodes, values, side='right')-1, 0, len(nodes)-2)
    t = (values-nodes[i])/(nodes[i+1]-nodes[i])
    weights = np.zeros((len(values), len(nodes)))
    weights[np.arange(len(values)), i] = 1-t
    weights[np.arange(len(values)), i+1] = t
    return weights


def linear_design(family, x, neutral):
    """Return offset (n,3), design (n,3,p), before output clipping."""
    x, neutral = _inputs(family, x, neutral)
    if family not in ('E3', 'EH6'):
        raise ValueError('Only E3 and EH6 are linear families')
    luma = x @ colour.W
    offset = np.repeat((colour.curve(luma, KNOTS, neutral/255)*255)[:, None], 3, axis=1)
    if family == 'E3':
        weights = _weights(luma, np.array([63., 93., 118.]))
    else:
        z = colour.lab(colour.decode(x/255))
        hue = np.mod(np.rad2deg(np.arctan2(z[:,2], z[:,1])), 360)/60
        i = np.floor(hue).astype(int) % 6; t = hue-np.floor(hue)
        weights = np.zeros((len(x), 6))
        weights[np.arange(len(x)), i] = 1-t
        weights[np.arange(len(x)), (i+1) % 6] = t
    chroma = x-luma[:, None]
    # The rounded luminance weights may leave neutral chroma at one ulp. The
    # declared achromatic input has zero contribution independent of its hue.
    chroma[np.ptp(x, axis=1) == 0] = 0
    return offset, chroma[:, :, None]*weights[:, None, :]


def forward(family, x, neutral, coefficients):
    x, neutral = _inputs(family, x, neutral)
    q = np.asarray(coefficients, float)
    bound = (-8, 8) if family == 'O12' else (0, 3)
    if (q.shape != (SIZES[family],) or not np.all(np.isfinite(q)) or
            np.any((q < bound[0]) | (q > bound[1]))):
        raise ValueError('Coefficients violate declared shape or bounds')
    if family != 'O12':
        offset, design = linear_design(family, x, neutral)
        return np.clip(offset + design @ q, 0, 255)
    z = colour.lab(colour.decode(x/255)); out = z.copy()
    nx = colour.lab(colour.decode(np.repeat(KNOTS[:,None]/255, 3, axis=1)))[:,0]
    ny = colour.lab(colour.decode(np.repeat(neutral[:,None]/255, 3, axis=1)))[:,0]
    out[:,0] = colour.curve(z[:,0], nx, ny)
    matrices = (_weights(z[:,0], np.cbrt([.05, .11, .18])) @ q.reshape(3,4)).reshape(-1,2,2)
    out[:,1:] = np.einsum('nij,nj->ni', matrices, z[:,1:])
    prediction = colour.encode(colour.unlab(out))*255
    if not np.all(np.isfinite(prediction)):
        raise ValueError('Nonfinite prediction')
    return prediction


def _target(x, target):
    target = _rgb(target)
    if target.shape != x.shape:
        raise ValueError('Input and target shapes differ')
    return target


def _tolerances(value, shape):
    try:
        value = np.broadcast_to(np.asarray(value, float), shape)
    except ValueError as e:
        raise ValueError('Tolerance must broadcast to target shape') from e
    if not np.all(np.isfinite(value)) or np.any(value < 0):
        raise ValueError('Tolerance must be finite and nonnegative')
    return value


def constraints(family, x, neutral, target, epsilon):
    """Aq <= b, including coefficient bounds. Rails NEVER absorb epsilon.

    Monotonic clipping removes an uncensored interval's side only when that
    side reaches the output cube boundary. Labels bind certificates to cells.
    """
    x, neutral = _inputs(family, x, neutral); target = _target(x, target)
    epsilon = _tolerances(epsilon, target.shape)
    offset, design = linear_design(family, x, neutral)
    a, rhs, labels = [], [], []
    for i in range(len(x)):
        for j in range(3):
            y, e, v, d = target[i,j], epsilon[i,j], offset[i,j], design[i,j]
            if y <= 5:
                a.append(d); rhs.append(5-v); labels.append([i,j,'low-rail'])
            elif y >= 250:
                a.append(-d); rhs.append(v-250); labels.append([i,j,'high-rail'])
            else:
                if y+e < 255:
                    a.append(d); rhs.append(y+e-v); labels.append([i,j,'upper'])
                if y-e > 0:
                    a.append(-d); rhs.append(v-y+e); labels.append([i,j,'lower'])
    for i, row in enumerate(np.eye(SIZES[family])):
        a.extend([row, -row]); rhs.extend([3., 0.])
        labels.extend([['gain',i,'upper'], ['gain',i,'lower']])
    return np.asarray(a), np.asarray(rhs), labels


def _rational_weights(a):
    """W39 basic-dual exact elimination generalised from two to p parameters."""
    n, p = a.shape
    rows = [[F(float(a[j,i])) for j in range(n)]+[F(0)] for i in range(p)]
    rows.append([F(1)]*n+[F(1)])
    for col in range(n):
        pivot = next((i for i in range(col, p+1) if rows[i][col]), None)
        if pivot is None:
            return None
        rows[col], rows[pivot] = rows[pivot], rows[col]
        value = rows[col][col]; rows[col] = [v/value for v in rows[col]]
        for i in range(p+1):
            if i != col:
                value = rows[i][col]
                rows[i] = [u-value*v for u,v in zip(rows[i], rows[col])]
    if any(all(v == 0 for v in row[:-1]) and row[-1] != 0 for row in rows):
        return None
    return [rows[i][-1] for i in range(n)]


def verify_certificate(cert, a, rhs):
    """Verify exact cancellation against caller-regenerated inequalities."""
    try:
        indices = cert['indices']; weights = [F(v) for v in cert['weights']]
        if (not indices or len(set(indices)) != len(indices) or
                len(indices) != len(weights) or
                any(type(i) is not int or not 0 <= i < len(rhs) for i in indices)):
            return False
        if any(v < 0 for v in weights) or sum(weights) != 1:
            return False
        if any(sum(w*F(float(a[i,j])) for w,i in zip(weights,indices)) != 0
               for j in range(a.shape[1])):
            return False
        return sum(w*F(float(rhs[i])) for w,i in zip(weights,indices)) < 0
    except (TypeError, ValueError, KeyError, ZeroDivisionError, IndexError):
        return False


def _recover_certificate(a, rhs, labels, fit):
    """Recover an exact dual; floating supports only order the bounded search.

    Near-dependent observation rows can cancel in HiGHS but not in rational
    arithmetic on their float64 coefficients. A coefficient-bound row with an
    arbitrarily small positive weight can complete the exact cancellation.
    Keep every positive floating weight, then augment/replace support from
    both observation and bound rows. No weight cutoff governs exact recovery.
    """
    p = a.shape[1]
    support = tuple(int(i) for i in np.flatnonzero(-fit.ineqlin.marginals > 0))
    if not support:
        return None, 0
    seen = set()
    attempts = 0

    def check(indices):
        nonlocal attempts
        indices = tuple(sorted(indices))
        if not indices or len(indices) > p+1 or indices in seen:
            return None
        seen.add(indices); attempts += 1
        weights = _rational_weights(a[list(indices)])
        if weights is None:
            return None
        cert = dict(indices=list(indices), weights=[str(w) for w in weights],
                    constraints=[labels[i] for i in indices])
        return cert if verify_certificate(cert, a, rhs) else None

    # The original basic support gets one exact attempt outside the recovery
    # budget. Zero recovery budget still allows already valid basic proofs.
    cert = check(support)
    if cert is not None:
        return cert, 0
    attempts = 0
    bounds = [i for i, label in enumerate(labels) if label[0] == 'gain' and i not in support]
    slack = rhs-a @ fit.x[:p]
    observations = [i for i in np.argsort(slack, kind='stable')
                    if labels[i][0] != 'gain' and i not in support][:DUAL_EXTRA_OBSERVATIONS]
    extra = bounds + [int(i) for i in observations]
    # Retain as much of the floating support as possible first. This tries all
    # one-row augmentations before replacements; later candidates can replace
    # observation rows as well as insert gain bounds. Never exceed p+1 rows.
    for retained in range(min(len(support), p+1), -1, -1):
        for added in range(0, p+2-retained):
            for base in combinations(support, retained):
                for extension in combinations(extra, added):
                    if attempts >= MAX_DUAL_RECOVERY_ATTEMPTS:
                        return None, attempts
                    cert = check(base+extension)
                    if cert is not None:
                        return cert, attempts
    return None, attempts


def _feasibility(a, rhs, labels):
    p = a.shape[1]
    fit = linprog(np.r_[np.zeros(p), 1.],
                  A_ub=np.column_stack((a, -np.ones(len(rhs)))), b_ub=rhs,
                  bounds=[(None,None)]*p+[(0,None)], method='highs',
                  options={'primal_feasibility_tolerance': 1e-9,
                           'dual_feasibility_tolerance': 1e-9, 'maxiter': LP_MAXITER})
    if not fit.success:
        return None, None, dict(reason='LP phase I failed: '+fit.message,
                               floatingBracket=dict(lower=None, upper=None, certified=False,
                                                    quantity='common phase-I row slack'))
    # This is just a proposed upper: the caller MUST check the original forward.
    q = np.clip(fit.x[:p], 0, 3)
    info = dict(phaseISlack=float(fit.fun), recoveryAttempts=0,
                floatingBracket=dict(lower=float(fit.fun),
                    upper=max(float(fit.fun), float(np.max(a @ q-rhs, initial=0))),
                    certified=False, quantity='common phase-I row slack; mixed gain/code units'))
    # No dual search is needed for an exactly feasible floating candidate.
    # The original forward remains the authority for every public positive.
    if np.any(a @ q > rhs):
        cert, attempts = _recover_certificate(a, rhs, labels, fit)
        info['recoveryAttempts'] = attempts
        if cert is not None:
            return q, cert, info
    # Move away from floating rail equality if needed. No certificate is taken
    # from this tightened system, and the original constraints remain authority.
    rails = np.array([str(label[-1]).endswith('-rail') for label in labels])
    if np.any((a @ q > rhs) & rails):
        guarded = linprog(np.zeros(p), A_ub=a, b_ub=rhs-rails*1e-8,
                          bounds=[(0,3)]*p, method='highs',
                          options={'primal_feasibility_tolerance': 1e-9,
                                   'maxiter': LP_MAXITER})
        if guarded.success:
            q = np.clip(guarded.x, 0, 3)
    return q, None, info


def _uncertified(reason, info, lo=None, hi=None, probe=None, q=None, lower_cert=None):
    """An exhausted numerical search is neither survival nor a family negative."""
    result = dict(status='uncertified', converged=False, reason=reason, phaseI=info,
                  floatingBracket=info['floatingBracket'])
    if lo is not None:
        # Keep the proven bracket separate from the unverified floating lower.
        result.update(lowerCodes=lo, upperCodes=hi, lowerCertificate=lower_cert,
                      coefficients=q.tolist(),
                      floatingBracket=dict(lower=max(lo, probe if probe is not None and
                          info.get('phaseISlack', 0) > 0 else lo), upper=hi,
                          certified=False, quantity='encoded minimax codes'))
    return result


def _rail_deficit(prediction, target):
    return np.where(target <= 5, np.maximum(prediction-5, 0),
                    np.where(target >= 250, np.maximum(250-prediction, 0), 0))


def _maximum(prediction, target):
    measured = (target > 5) & (target < 250)
    return float(np.max(np.abs(prediction-target)[measured], initial=0))


def solve_linear(family, x, neutral, target, gap_codes=1e-5):
    """Global encoded minimax bracket; hard-rail infeasibility is separate.

    No approximate dual, LP flag or nonlinear failure becomes a negative.
    Every positive lower endpoint carries a replayable rational certificate.
    Exhaustion returns uncertified, with the proven endpoints retained beside
    a separately labelled floating diagnostic bracket; it is not a verdict.
    """
    x, neutral = _inputs(family, x, neutral); target = _target(x, target)
    if not np.isfinite(gap_codes) or not 0 < gap_codes <= 1e-5:
        raise ValueError('Gap must be positive and <=1e-5 code')
    a, rhs, labels = constraints(family, x, neutral, target, 255.)
    q, cert, info = _feasibility(a, rhs, labels)
    if cert is not None:
        return dict(status='certified-hard-rail-infeasible', epsilonCodes=255.,
                    lowerCertificate=cert, converged=True)
    if q is None:
        return _uncertified('No phase-I candidate for hard-rail upper', info)
    prediction = forward(family, x, neutral, q)
    if np.any(_rail_deficit(prediction, target) > 0):
        return _uncertified('No forward-feasible hard-rail upper', info)
    hi = _maximum(prediction, target); lo = 0.; lower_cert = None
    zero_a, zero_rhs, zero_labels = constraints(family, x, neutral, target, 0.)
    exact_q, _, _ = _feasibility(zero_a, zero_rhs, zero_labels)
    # A zero probe may be exactly infeasible by a few ulps while its floating
    # candidate gives an excellent forward upper. Keep that independently of
    # the dual: an exact lower at zero does not refute a tiny positive upper.
    if exact_q is not None:
        exact_prediction = forward(family, x, neutral, exact_q)
        exact_error = _maximum(exact_prediction, target)
        if not np.any(_rail_deficit(exact_prediction, target) > 0) and exact_error < hi:
            hi = exact_error; q = exact_q
    for iteration in range(101):
        if hi-lo <= gap_codes:
            break
        middle = (hi+lo)/2
        a, rhs, labels = constraints(family, x, neutral, target, middle)
        candidate, cert, info = _feasibility(a, rhs, labels)
        if cert is not None:
            lo = middle; lower_cert = cert
        else:
            if candidate is None:
                return _uncertified('No phase-I candidate', info, lo, hi, middle, q, lower_cert)
            prediction = forward(family, x, neutral, candidate)
            achieved = _maximum(prediction, target)
            if np.any(_rail_deficit(prediction, target) > 0) or achieved >= hi:
                return _uncertified('Exact dual recovery exhausted; forward upper stalled',
                                    info, lo, hi, middle, q, lower_cert)
            hi = achieved; q = candidate
    else:
        return _uncertified('Bisection budget exhausted', info, lo, hi, q=q, lower_cert=lower_cert)
    return dict(coefficients=q.tolist(), lowerCodes=lo, upperCodes=hi,
                bracketWidthCodes=hi-lo, lowerCertificate=lower_cert,
                certificateScope='exact rational float64 inequalities; forward-checked upper',
                status='global minimax bracket', iterations=iteration, converged=True)


def survival_linear(family, x, neutral, target, bar):
    """Test max(1,bar) with hard rails; uncertified is neither pass nor fail."""
    x, neutral = _inputs(family, x, neutral); target = _target(x, target)
    bound = np.maximum(1, _tolerances(bar, target.shape))
    a, rhs, labels = constraints(family, x, neutral, target, bound)
    q, cert, info = _feasibility(a, rhs, labels)
    if cert is not None:
        return dict(status='certified-infeasible', certificate=cert)
    if q is None:
        return _uncertified('No phase-I survival candidate', info)
    report = score(forward(family, x, neutral, q), target, bar)
    if report['uncensoredFailures'] or report['railFailures']:
        return _uncertified('Exact dual recovery exhausted; survival forward check failed', info)
    return dict(status='forward-feasible', coefficients=q.tolist(), score=report)


def score(prediction, target, bar=.5):
    """Numerical scores only: caller must enforce populations/repeats/coverage.

    A measured status denotes an uncensored measurement, not a passing one;
    failure booleans stay beside it. Censored channels never claim RGB accuracy.
    """
    prediction = _rgb(prediction); target = _target(prediction, target)
    bound = np.maximum(1, _tolerances(bar, target.shape))
    measured = (target > 5) & (target < 250)
    errors = np.where(measured, abs(prediction-target), 0)
    deficit = _rail_deficit(prediction, target)
    failures = measured & (errors > bound)
    statuses = np.where(measured, 'measured',
                        np.where(deficit == 0, 'censored-bound-satisfied', 'UNMEASURED'))
    return dict(statuses=statuses.tolist(), uncensoredErrorCodes=np.where(measured, errors, None).tolist(),
                boundDeficitCodes=deficit.tolist(), uncensoredFailures=int(failures.sum()),
                railFailures=int((deficit > 0).sum()), worstChannelCodes=_maximum(prediction,target),
                failedCells=int(np.any(failures | (deficit > 0), axis=1).sum()),
                allChannelFailedCells=int(np.all(failures | (deficit > 0), axis=1).sum()),
                uncensoredChannels=int(measured.sum()), censoredChannels=int((~measured).sum()),
                heldoutCoverageEligible=np.all(measured, axis=1).tolist())


def fit_local(family, x, neutral, target):
    """Bounded 16-start LS and independent SLSQP epigraph search, seed 4100.

    LS gives equal cell mass, then equal uncensored channel mass within cell;
    censored channels contribute HARD constraints, never residual penalties.
    Least-squares uses the declared 3000 evaluation / 1e-10 budget. If rails
    exist, its result seeds a constrained SLSQP least-squares solve (same 3000
    iteration / 1e-10 budget); this extra solve is reported separately. Minimax
    always starts from each original start, not from the LS funnel. Equal mass
    leaves an L-infinity maximum unchanged. No convergence means no candidate,
    not a negative about the nonlinear family.
    """
    x, neutral = _inputs(family, x, neutral); target = _target(x, target)
    p = SIZES[family]; low, high = (-8.,8.) if family == 'O12' else (0.,3.)
    baseline = np.tile([1.,0.,0.,1.],3) if family == 'O12' else np.ones(p)
    starts = [baseline, *np.random.default_rng(4100).uniform(low,high,(15,p))]
    measured = (target > 5) & (target < 250)
    low_rail, high_rail = target <= 5, target >= 250
    has_rails = bool(np.any(~measured))
    counts = measured.sum(axis=1)
    mass = np.repeat((1/np.maximum(counts,1)/len(x))[:,None],3,axis=1)
    sqrt_mass = np.sqrt(mass[measured])
    # Cache fixed coordinates only; all chosen predictions are checked again
    # with the public forward before they are reported.
    if family == 'O12':
        z = colour.lab(colour.decode(x/255))
        nx = colour.lab(colour.decode(np.repeat(KNOTS[:,None]/255,3,axis=1)))[:,0]
        ny = colour.lab(colour.decode(np.repeat(neutral[:,None]/255,3,axis=1)))[:,0]
        tone = colour.curve(z[:,0],nx,ny)
        weights = _weights(z[:,0],np.cbrt([.05,.11,.18]))
        def predict(q):
            matrices = (weights @ q.reshape(3,4)).reshape(-1,2,2)
            out = np.column_stack((tone, np.einsum('nij,nj->ni',matrices,z[:,1:])))
            return colour.encode(colour.unlab(out))*255
    else:
        offset, design = linear_design(family,x,neutral)
        def predict(q):
            return np.clip(offset+design @ q,0,255)

    def residual(q):
        return (predict(q)-target)[measured]
    def weighted(q):
        return residual(q)*sqrt_mass
    def rails(q):
        prediction = predict(q)
        return np.r_[5-prediction[low_rail], prediction[high_rail]-250]
    def epigraph(packed):
        r = residual(packed[:-1])
        return np.r_[packed[-1]-r, packed[-1]+r, rails(packed[:-1])]
    def report(q, optimizer, epigraph_value=None):
        q = np.asarray(q)
        parameter_feasible = bool(np.all(np.isfinite(q)) and np.all(q >= low) and np.all(q <= high))
        if not parameter_feasible:
            raise RuntimeError('Optimizer returned out-of-bounds/nonfinite coefficients')
        prediction = forward(family,x,neutral,q)
        if np.max(abs(prediction-predict(q))) > 1e-10:
            raise RuntimeError('Cached optimizer forward differs from public forward')
        maximum = _maximum(prediction,target)
        rail_deficit = float(_rail_deficit(prediction,target).max(initial=0))
        jac = approx_derivative(lambda v: predict(v)[measured],q,
                                bounds=(np.full(p,low),np.full(p,high)))
        singular = np.linalg.svd(jac,compute_uv=False) if jac.size else np.array([])
        rank = int(np.linalg.matrix_rank(jac)) if jac.size else 0
        gap = None if epigraph_value is None else maximum-float(epigraph_value)
        return dict(coefficients=q.tolist(), maximumCodes=maximum,
                    weightedSquaredError=float(np.sum(weighted(q)**2)),
                    rank=rank, singularValues=singular.tolist(), columns=p,
                    railDeficitCodes=rail_deficit, parameterFeasible=parameter_feasible,
                    optimizerSuccess=bool(optimizer.success), message=str(optimizer.message),
                    evaluations=int(optimizer.nfev), iterations=int(getattr(optimizer,'nit',0)),
                    epigraphGapCodes=gap,
                    converged=bool(optimizer.success and rail_deficit == 0 and
                                   (gap is None or gap <= 1e-8)),
                    score=score(prediction,target))

    records = []
    for index, initial in enumerate(starts):
        ls = least_squares(weighted,initial,bounds=(low,high),max_nfev=3000,
                           ftol=1e-10,xtol=1e-10,gtol=1e-10)
        least = report(ls.x,ls)
        if has_rails:
            constrained = minimize(lambda q: np.sum(weighted(q)**2),ls.x,method='SLSQP',
                                   bounds=[(low,high)]*p,
                                   constraints=[dict(type='ineq',fun=rails)],
                                   options=dict(maxiter=3000,ftol=1e-10))
            least = report(constrained.x,constrained)
            least['unconstrainedSeed'] = dict(success=bool(ls.success),evaluations=int(ls.nfev))
        start = np.r_[initial,_maximum(predict(initial),target)+1e-8]
        mm = minimize(lambda v: v[-1],start,method='SLSQP',
                      bounds=[(low,high)]*p+[(0,None)],
                      constraints=[dict(type='ineq',fun=epigraph)],
                      options=dict(maxiter=3000,ftol=1e-10))
        minimax = report(mm.x[:-1],mm,mm.x[-1])
        records.append(dict(startIndex=index,initial=initial.tolist(),
                            leastSquares=least,minimax=minimax))
    def choose(key, objective):
        candidates = [r for r in records if r[key]['converged']]
        if not candidates:
            return None
        chosen = min(candidates,key=lambda r:(r[key][objective],r['startIndex']))
        return dict(**chosen[key],startIndex=chosen['startIndex'])
    return dict(classification='LOCAL; not a global family negative',starts=records,
                leastSquares=choose('leastSquares','weightedSquaredError'),
                minimax=choose('minimax','maximumCodes'),
                budget=dict(seed=4100,starts=16,lsMaxNfev=3000,lsFtol=1e-10,
                            lsXtol=1e-10,lsGtol=1e-10,minimaxMaxiter=3000,minimaxFtol=1e-10,
                            hardRailConstrainedLS=has_rails))
