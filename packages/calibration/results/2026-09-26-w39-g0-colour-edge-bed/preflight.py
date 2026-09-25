#!/usr/bin/env python3.12
"""W39 phase preflight: drive its captures and score its pass rule (charter clause 4, X22;
bounds-declaration.txt "PHASE PREFLIGHT"; c9a §5.184).

ONE actuator is tested: fractional SIZE on the radius-22 120x44 rrect with the near edge
pinned by `position` (position = pinned edge + size/2). Per scale, the preflight pass's
run 1 captures nine geometries x opaque/glass (the shared zero, x1-x3 as width + k/4
device px, y1-y3 as height + k/4 device px, and the integer controls width 121 / height
45 CSS px at phase zero), and run 2 captures the phase-zero pair again at the pass's END.
Light active, both scales: 36 + 4 = 40 captures. The x axis pins the LEFT edge and reads
the RIGHT, both through the capsule's apex rows (its 44-px ends have no straight run);
the y axis pins the TOP and reads the BOTTOM along the straight run. Every reading goes
through `w39_readers.py` from the ATTESTED supplied frame, never the declaration alone.

An axis is REACHABLE only when every criterion holds at BOTH scales:

(i)   opaque: the near band's raw bytes identical across the four phases; the far band
      shows >= 3 distinct byte states;
(ii)  glass near: every pair of phases within max(0.5, D_int_near) at every coordinate and
      channel, D_int_near being the integer control's near-profile difference from phase
      zero (the near edge is pinned, so no alignment);
(iii) glass far: >= 3 states counted greedily in phase order, a new state differing from
      EVERY kept one by more than max(0.5, D_int_far), D_int_far being the integer
      control's far profile index-aligned by its whole shift (scale device px) against
      phase zero; and the SHIFT model beats the AMPLITUDE model:
        SHIFT: one shared profile (a step at the edge plus piecewise-linear knots every
          1.0 device px over the -14 CSS inward / +4 CSS outward window) integrated over
          each raster line, at four fitted per-phase edges (zero's edge is the gauge);
        AMPLITUDE: the same profile at ONE fitted shared edge, with four per-phase gains on
          (profile - exterior level) (zero's gain is the gauge);
      (a) RSS_shift <= 0.5 * RSS_amplitude; (b) fitted edges nondecreasing in requested
      phase within 1/32 device px; (c) the shared-profile design matrix at the fitted edges
      has full column rank (condition number reported; rank deficient = NOT IDENTIFIED);
      (d) leave one phase out: refit the profile and the other edges on three phases, fit
      ONLY the held-out phase's edge, and at every knot-sampled coordinate and channel
      |residual| <= max(0.5, D_int_far) + 0.5*|w_i|_1, w_i being that sample's row of the
      prediction operator (held-out basis x pinv of the three-phase design): the exact
      worst case of the three fitted phases' 8-bit rounding reaching the prediction.
The literal W37 area-integrated ramp is fitted beside as a diagnostic, never a criterion.

Why 1.0 and not 0.5 device px knots, and why the propagated term (ruled 2026-09-26 on the
synthetic beds in test-preflight.py, whose committed output test-preflight.txt is the
record): unit-pixel area integration has an exact null vector on a half-pixel knot grid,
the alternating triangle wave, which integrates to zero over every unit window whatever the phases, so a 0.5 px
grid is rank deficient by construction (75/76 at 2x, condition ~4e16) and (c) could never
hold. And a held-out sample carries its own +-0.5 rounding plus the fitted phases'
rounding propagated through the fit, so a 0.5-code bound fails a true subpixel shift
(1.41 codes at 1x) whenever a whole-pixel size step changes nothing (D_int_far = 0).

The phase-zero END repeat must match run 1 on all four side profiles: opaque raw bands
byte-identical, glass band means within 0.5 at every coordinate and channel. Otherwise
that scale is UNMEASURED for drift, both axes are unadmitted, and nothing is said about
the actuator. Branches: both axes reachable admit 14 phase scenes per scheme and pose;
one admits that axis's 8; neither admits none. The admitted list is computed by
`sitting.phase_scenes`, the same function the sitting re-checks the verdict with.
"""
import argparse
import datetime
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

import numpy as np
from PIL import Image

HERE = Path(__file__).resolve().parent


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


R = _load('w39_readers_for_preflight', HERE / 'w39_readers.py')
S = _load('w39_sitting_for_preflight', HERE / 'sitting.py')

# Mirrored by closure.json["preflight"] and pinned to it by test-preflight.py.
DECLARATION_CONSTANTS = dict(
    geometryCaptures=36, endSentinelCaptures=4, totalCaptures=40,
    knotsDevicePx=1.0, shiftRSSRatio=0.5, edgeMonotonicitySlackDevicePx=1 / 32,
    minimumStates=3, nearTolerance='max(0.5,D_int_near)', farTolerance='max(0.5,D_int_far)',
    phaseZeroDriftTolerance=0.5, fullRank=True, leaveOnePhaseOut=True,
    lopoQuantizationHalfCode=0.5)
FLOOR = 0.5                 # the quantisation floor: one run has no observed repeat spread
KNOT = DECLARATION_CONSTANTS['knotsDevicePx']
RATIO = DECLARATION_CONSTANTS['shiftRSSRatio']
SLACK = DECLARATION_CONSTANTS['edgeMonotonicitySlackDevicePx']
STATES = DECLARATION_CONSTANTS['minimumStates']
DRIFT = DECLARATION_CONSTANTS['phaseZeroDriftTolerance']
HALF_CODE = DECLARATION_CONSTANTS['lopoQuantizationHalfCode']
INNER_CSS, OUTER_CSS = 14, 4
QUAD = 8                    # W37's midpoint quadrature per raster line
AXES = dict(x=dict(near='left', far='right', dim=0), y=dict(near='top', far='bottom', dim=1))
PHASES = ('zero', '1', '2', '3')
BASE = (120.0, 44.0)


def geometry_name(axis, k):
    return 'zero' if k == 'zero' else f'{axis}{k}'


# ---------------------------------------------------------------------- profiles

def profile(image, shape, scale, side):
    p = R.straight_profile(image, shape, scale, side, INNER_CSS, OUTER_CSS)
    if p['status'] != 'measured':
        raise ValueError(f'{side} profile UNMEASURED: {p.get("reason")}')
    return p


def aligned(a, b, shift=0, key='meanRGB'):
    """Values of a at coords c and of b at c + shift, over the coords both carry."""
    ca, cb = list(a['coords']), list(b['coords'])
    common = [c for c in ca if c + shift in set(cb)]
    va = np.asarray(a[key], float if key == 'meanRGB' else np.uint8)
    vb = np.asarray(b[key], float if key == 'meanRGB' else np.uint8)
    ia = [ca.index(c) for c in common]
    ib = [cb.index(c + shift) for c in common]
    if key == 'raw':
        return va[:, ia], vb[:, ib], common
    return va[ia], vb[ib], common


def common_coords(profiles):
    sets = [set(p['coords']) for p in profiles]
    return sorted(set.intersection(*sets))


def at(p, coords, key='meanRGB'):
    idx = [p['coords'].index(c) for c in coords]
    v = np.asarray(p[key])
    return v[:, idx] if key == 'raw' else np.asarray(v, float)[idx]


def maxabs(a, b):
    return float(np.max(np.abs(np.asarray(a, float) - np.asarray(b, float)))) if np.size(a) else 0.0


def greedy_states(values, threshold):
    """Phase-order greedy states: a phase opens a state if it differs from EVERY kept
    representative by more than `threshold`; otherwise it joins the first within it."""
    reps, labels = [], []
    for i, v in enumerate(values):
        for s, r in enumerate(reps):
            if maxabs(v, values[r]) <= threshold:
                labels.append(s)
                break
        else:
            reps.append(i)
            labels.append(len(reps) - 1)
    return len(reps), labels


# ------------------------------------------------------------------ the models

def _u(coords, edge, inward):
    """Device-px signed inward distance at each line's QUAD midpoints (the reader's grid)."""
    q = (np.arange(QUAD) + .5) / QUAD
    return inward * (np.asarray(coords, float)[:, None] + q[None, :] - edge)


def basis(coords, edge, inward, knots):
    """Area-averaged columns: the step at the edge, then one hat per knot (device px)."""
    u = _u(coords, edge, inward)
    step = (u >= 0).mean(1)
    hats = np.clip(1 - np.abs(u[:, :, None] - knots[None, None, :]) / KNOT, 0, None).mean(1)
    return np.column_stack([step, hats])


def knot_grid(coords, edges, inward):
    u = np.concatenate([_u(coords, e, inward).ravel() for e in edges])
    lo = np.floor((u.min() - 1.5) / KNOT) * KNOT
    hi = np.ceil((u.max() + 1.5) / KNOT) * KNOT
    return np.arange(lo, hi + KNOT / 2, KNOT)


def solve(A, Y):
    """Least squares on the supported columns; returns (theta_full, rss, supported)."""
    supported = np.linalg.norm(A, axis=0) > 0
    theta = np.zeros((A.shape[1], Y.shape[1]))
    sol = np.linalg.lstsq(A[:, supported], Y, rcond=None)[0]
    theta[supported] = sol
    r = Y - A @ theta
    return theta, float(np.sum(r * r)), supported


def shift_design(coords, edges, inward, knots):
    return np.vstack([basis(coords, e, inward, knots) for e in edges])


def _descend(objective, x0, free, lo, hi, cycles=3):
    """Coordinate descent on a 1/64 grid, then golden refinement to 1/2048 device px."""
    x = list(x0)
    for _ in range(cycles):
        for i in free:
            grid = np.arange(lo[i], hi[i] + 1e-9, 1 / 64)
            scores = [objective(x[:i] + [g] + x[i + 1:]) for g in grid]
            x[i] = float(grid[int(np.argmin(scores))])
    for i in free:
        a, b = x[i] - 1 / 64, x[i] + 1 / 64
        g = (np.sqrt(5) - 1) / 2
        while b - a > 1 / 2048:
            c, d = b - g * (b - a), a + g * (b - a)
            if objective(x[:i] + [c] + x[i + 1:]) <= objective(x[:i] + [d] + x[i + 1:]):
                b = d
            else:
                a = c
        x[i] = (a + b) / 2
    return x


def fit_shift(coords, Y, attested, inward, knots, gauge=0):
    """Shared profile at per-phase fitted edges; phase `gauge` sits at its attested edge."""
    Ys = np.vstack(Y)
    rss = lambda e: solve(shift_design(coords, e, inward, knots), Ys)[1]
    lo = [attested[gauge] - 0.5] * len(Y)
    hi = [attested[gauge] + 1.5] * len(Y)
    free = [i for i in range(len(Y)) if i != gauge]
    edges = _descend(rss, list(attested), free, lo, hi)
    A = shift_design(coords, edges, inward, knots)
    theta, value, supported = solve(A, Ys)
    As = A[:, supported]
    return dict(edges=edges, rss=value, theta=theta, supported=supported,
                rank=int(np.linalg.matrix_rank(As)), columns=int(supported.sum()),
                condition=float(np.linalg.cond(As)))


def fit_amplitude(coords, Y, attested, inward, knots, iterations=200):
    """One shared edge, per-phase gains on (profile - exterior level), zero's gain 1."""
    n = len(Y)

    def at_edge(e):
        B = basis(coords, e, inward, knots)
        g = np.ones(n)
        prev = np.inf
        for _ in range(iterations):
            A = np.vstack([np.column_stack([np.ones(len(coords)), g[p] * B]) for p in range(n)])
            theta, value, _ = solve(A, np.vstack(Y))
            F = B @ theta[1:]
            L = theta[0]
            for p in range(1, n):
                denom = float(np.sum(F * F))
                g[p] = float(np.sum((Y[p] - L) * F) / denom) if denom > 0 else 1.0
            if prev - value <= 1e-10 * max(prev, 1):
                break
            prev = value
        A = np.vstack([np.column_stack([np.ones(len(coords)), g[p] * B]) for p in range(n)])
        theta, value, _ = solve(A, np.vstack(Y))
        return value, g

    grid = np.arange(attested[0] - 1, attested[0] + 1 + 1e-9, 1 / 16)
    scores = [at_edge(e)[0] for e in grid]
    best = float(grid[int(np.argmin(scores))])
    a, b = best - 1 / 16, best + 1 / 16
    gold = (np.sqrt(5) - 1) / 2
    while b - a > 1 / 1024:
        c, d = b - gold * (b - a), a + gold * (b - a)
        if at_edge(c)[0] <= at_edge(d)[0]:
            b = d
        else:
            a = c
    edge = (a + b) / 2
    value, gains = at_edge(edge)
    return dict(edge=edge, rss=value, gains=gains.tolist())


def leave_one_out(coords, Y, attested, inward, knots, tolerance):
    rows = []
    for h in range(len(Y)):
        keep = [p for p in range(len(Y)) if p != h]
        sub = fit_shift(coords, [Y[p] for p in keep], [attested[p] for p in keep], inward, knots)
        theta, supported = sub['theta'], sub['supported']

        def residual(e):
            B = basis(coords, e, inward, knots)
            sampled = ~np.any(B[:, ~supported] > 0, axis=1)   # rows the three-phase fit covers
            return Y[h][sampled] - B[sampled] @ theta, sampled

        rss = lambda e: float(np.sum(residual(e[0])[0] ** 2))
        edge = _descend(rss, [attested[h]], [0], [attested[h] - 1.0], [attested[h] + 1.0])[0]
        r, sampled = residual(edge)
        # Worst-case propagation of the 8-bit rounding of the three fitted phases into
        # each predicted sample: prediction = W @ data, so |error| <= 0.5 * |W_i|_1.
        A3 = shift_design(coords, sub['edges'], inward, knots)[:, supported]
        B = basis(coords, edge, inward, knots)[sampled][:, supported]
        propagated = HALF_CODE * np.abs(B @ np.linalg.pinv(A3)).sum(1)
        worst = float(np.max(np.abs(r))) if r.size else None
        excess = float(np.max(np.abs(r) - propagated[:, None])) if r.size else None
        rows.append(dict(heldOut=PHASES[h], edge=edge, edgeOffsetFromAttested=edge - attested[h],
                         sampledCoordinates=int(sampled.sum()), maxResidual=worst,
                         coordinates=[c for c, keep in zip(coords, sampled) if keep],
                         residualRGB=r.tolist(), propagatedRoundingPerSample=propagated.tolist(),
                         tolerancePerSample=(tolerance + propagated).tolist(),
                         maxPropagatedRounding=float(propagated.max()) if r.size else None,
                         maxResidualBeyondPropagated=excess,
                         passes=bool(r.size) and bool(np.all(np.abs(r) <= tolerance + propagated[:, None]))))
    return rows


def ramp_diagnostic(coords, Y, edges, inward, scale):
    """W37's literal area-integrated ramp at the shift fit's edges: exterior a + b*u,
    interior c + A*max(1 - u/w, 0), w in CSS px on a 0.1 grid. Diagnostic only."""
    best = None
    for w in np.arange(0.4, 3.01, 0.1):
        cols = []
        for e in edges:
            u = _u(coords, e, inward) / scale
            out, inn = (u < 0), (u >= 0)
            cols.append(np.column_stack([out.mean(1), (out * u).mean(1), inn.mean(1),
                                         (inn * np.maximum(1 - u / w, 0)).mean(1)]))
        A = np.vstack(cols)
        theta, value, _ = solve(A, np.vstack(Y))
        worst = float(np.max(np.abs(np.vstack(Y) - A @ theta)))
        if best is None or value < best['rss']:
            best = dict(widthCss=round(float(w), 2), rss=value, maxResidual=worst,
                        rmsResidual=float(np.sqrt(value / np.vstack(Y).size)))
    return best


# --------------------------------------------------------------------- scoring

def score_axis(axis, cells, scale):
    """cells[(geometry, opaque)] = (uint8 image, Shape). Returns every number and a status."""
    near, far = AXES[axis]['near'], AXES[axis]['far']
    dim = AXES[axis]['dim']
    names = [geometry_name(axis, k) for k in PHASES]
    control = f'{axis}-integer'
    out = dict(axis=axis, scale=scale, nearSide=near, farSide=far)

    # The actuator as attested: sizes are base + k/4 device px, the near edge pinned.
    shapes = {g: cells[(g, False)][1] for g in names + [control]}
    requested = [(shapes[g].size[dim] - BASE[dim]) * scale for g in names]
    if not np.allclose(requested, [0, .25, .5, .75], atol=1e-9, rtol=0):
        raise ValueError(f'{axis}: attested sizes are not the declared device quarters: {requested}')
    if abs((shapes[control].size[dim] - BASE[dim]) - 1) > 1e-9:
        raise ValueError(f'{axis}: the integer control is not one CSS px larger')
    pinned = [shapes[g].frame_origin[dim] for g in names + [control]]
    if max(pinned) - min(pinned) > 1e-9:
        raise ValueError(f'{axis}: the near edge is not pinned in the attested frames')
    out['requestedDeviceOffsets'] = requested

    # (i) opaque.
    op = {g: {s: profile(cells[(g, True)][0], cells[(g, True)][1], scale, s) for s in (near, far)}
          for g in names}
    nc = common_coords([op[g][near] for g in names])
    near_raw = [at(op[g][near], nc, 'raw') for g in names]
    near_same = all(np.array_equal(near_raw[0], r) for r in near_raw[1:])
    fc = common_coords([op[g][far] for g in names])
    far_raw = [at(op[g][far], fc, 'raw').tobytes() for g in names]
    far_states = len(set(far_raw))
    coverage = []
    for g in names:
        image, shape = cells[(g, True)]
        alpha = R.opaque_coverage(image, cells['background'], cells['fill'])
        coverage.append(R.coverage_profile(alpha, shape, scale, far, INNER_CSS, OUTER_CSS)['measuredEdge'])
    out['opaque'] = dict(nearByteIdentical=near_same, nearBand=op[names[0]][near]['band'],
                         nearMode=op[names[0]][near]['mode'], farDistinctByteStates=far_states,
                         farMode=op[names[0]][far]['mode'],
                         farMeasuredEdgesDiagnostic=coverage,
                         passes=bool(near_same and far_states >= STATES))

    # (ii) glass near, against the integer control's near difference.
    gl = {g: {s: profile(cells[(g, False)][0], cells[(g, False)][1], scale, s) for s in (near, far)}
          for g in names + [control]}
    a, b, _ = aligned(gl[control][near], gl[names[0]][near])
    d_near = maxabs(a, b)
    nc = common_coords([gl[g][near] for g in names])
    nv = [at(gl[g][near], nc) for g in names]
    near_max = max(maxabs(nv[i], nv[j]) for i in range(4) for j in range(i + 1, 4))
    near_tol = max(FLOOR, d_near)
    out['glassNear'] = dict(D_int_near=d_near, tolerance=near_tol, maxPairwise=near_max,
                            passes=near_max <= near_tol)

    # (iii) glass far: the integer control aligned by its whole shift.
    shift = gl[control][far]['pathEdge'] - gl[names[0]][far]['pathEdge']
    if abs(shift - scale) > 1e-9:
        raise ValueError(f'{axis}: the integer control moved its far edge {shift}, not {scale}')
    a, b, _ = aligned(gl[names[0]][far], gl[control][far], shift=int(round(shift)))
    d_far = maxabs(a, b)
    far_tol = max(FLOOR, d_far)
    fc = common_coords([gl[g][far] for g in names])
    Y = [at(gl[g][far], fc) for g in names]
    n_states, labels = greedy_states(Y, far_tol)
    inward = gl[names[0]][far]['inward']
    attested = [gl[g][far]['pathEdge'] for g in names]
    if not np.allclose(np.asarray(attested) - attested[0], requested, atol=1e-9, rtol=0):
        raise ValueError(f'{axis}: attested far edges disagree with the requested phases')
    knots = knot_grid(fc, [attested[0] - 0.5, attested[0] + 1.5], inward)
    sh = fit_shift(fc, Y, attested, inward, knots)
    am = fit_amplitude(fc, Y, attested, inward, knots)
    order = np.argsort(requested)
    edges = np.asarray(sh['edges'])[order]
    direction = -inward                     # the far edge moves outward as the size grows
    monotone = bool(np.all(np.diff(edges) * direction >= -SLACK))
    identified = sh['rank'] == sh['columns']
    lopo = leave_one_out(fc, Y, attested, inward, knots, far_tol)
    ratio_ok = sh['rss'] <= RATIO * am['rss']
    out['glassFar'] = dict(
        D_int_far=d_far, tolerance=far_tol, distinctStates=n_states, stateOfPhase=labels,
        statesPass=n_states >= STATES,
        shift=dict(rss=sh['rss'], fittedEdges=sh['edges'],
                   fittedOffsets=[float(e - attested[0]) for e in sh['edges']], attestedEdges=attested,
                   rank=sh['rank'], columns=sh['columns'], conditionNumber=sh['condition'],
                   knots=len(knots), samples=len(fc) * 4),
        amplitude=dict(rss=am['rss'], sharedEdge=am['edge'], gains=am['gains']),
        rssRatio=(sh['rss'] / am['rss']) if am['rss'] > 0 else None,
        criteria=dict(a_rssRatio=bool(ratio_ok), b_monotone=monotone, c_identified=bool(identified),
                      d_leaveOneOut=all(r['passes'] for r in lopo)),
        leaveOneOut=lopo,
        rampDiagnostic=ramp_diagnostic(fc, Y, sh['edges'], inward, scale))
    far_ok = n_states >= STATES and ratio_ok and monotone and all(r['passes'] for r in lopo)
    if not identified:
        status = 'not-identified'
    elif out['opaque']['passes'] and out['glassNear']['passes'] and far_ok:
        status = 'pass'
    else:
        status = 'fail'
    out['status'] = status
    return out


SIDES = ('left', 'right', 'top', 'bottom')


def end_sentinel(opening, repeat, scale):
    """Run-1 zero pair against the run-2 END repeat, all four side profiles."""
    rows = {}
    ok = True
    for opaque in (True, False):
        (img_a, shape_a), (img_b, shape_b) = opening[opaque], repeat[opaque]
        if shape_a != shape_b:
            raise ValueError('the end repeat is not the opening geometry')
        for side in SIDES:
            pa, pb = profile(img_a, shape_a, scale, side), profile(img_b, shape_b, scale, side)
            if opaque:
                same = np.array_equal(pa['raw'], pb['raw'])
                rows[f'opaque-{side}'] = dict(byteIdentical=same)
                ok &= same
            else:
                worst = maxabs(pa['meanRGB'], pb['meanRGB'])
                rows[f'glass-{side}'] = dict(maxDifference=worst, within=worst <= DRIFT)
                ok &= worst <= DRIFT
        rows[('opaque' if opaque else 'glass') + '-wholeImageMaxDiagnostic'] = maxabs(img_a, img_b)
    return dict(passes=bool(ok), readings=rows)


def score_scale(cells, repeat, scale):
    sentinel = end_sentinel({o: cells[('zero', o)] for o in (True, False)}, repeat, scale)
    axes = {}
    for axis in AXES:
        if not sentinel['passes']:
            axes[axis] = dict(status='UNMEASURED-drift')
            continue
        axes[axis] = score_axis(axis, cells, scale)
    return dict(endSentinel=sentinel, axes=axes)


def decide(scales):
    """Axis status across both scales, and the branch."""
    verdicts = {}
    for axis in AXES:
        statuses = [scales[s]['axes'][axis]['status'] for s in ('1x', '2x')]
        if all(s == 'pass' for s in statuses):
            status = 'reachable'
        elif 'fail' in statuses:
            status = 'unreachable'
        elif 'not-identified' in statuses:
            status = 'not-identified'
        else:
            status = 'UNMEASURED-drift'
        verdicts[axis] = dict(status=status, perScale=dict(zip(('1x', '2x'), statuses)))
    reachable = [a for a in AXES if verdicts[a]['status'] == 'reachable']
    branch = {2: 'both', 0: 'neither'}.get(len(reachable), f'{reachable[0]}-only' if reachable else 'neither')
    return verdicts, reachable, branch


# ------------------------------------------------------------------- run input

def read_run(run, spec):
    """(geometry, opaque) -> (uint8 image, Shape) for an ADMITTED preflight run."""
    admission = run / 'admission.json'
    if not admission.is_file() or not json.loads(admission.read_text()).get('admitted'):
        raise ValueError(f'{run} was not admitted by the sitting')
    raw = (run / 'manifest.json').read_bytes()
    manifest = json.loads(raw)
    scenes = {s['id']: s for s in spec['scenes']}
    cells = {}
    for p in manifest['profiles']:
        for f in p['fixtures']:
            scene = scenes[f['sceneId']]
            component = spec['components'][scene['component']]
            shape, = R.shapes_of(dict(component, suppliedPaths=f['suppliedPaths']))
            image = np.asarray(Image.open(run / f['file']).convert('RGB'))
            cells[(scene['$geometry'], bool(component.get('opaque')))] = (image, shape)
            cells['fill'] = component.get('fillSRGB', cells.get('fill'))
    background = {s['background'] for s in spec['scenes']}
    if len(background) != 1:
        raise ValueError('the preflight is over one background')
    cells['background'] = spec['backgrounds'][background.pop()]['srgb']
    return cells, hashlib.sha256(raw).hexdigest()


def verdict(root, out=None):
    root = Path(root).expanduser().resolve()
    if S.inside(root, S.REPO) or S.inside(root, S.MAIN):
        raise ValueError('the sitting root must be outside every checkout of the repository')
    out = Path(out) if out else root / 'preflight-verdict.json'
    if out.exists():
        raise ValueError(f'{out} exists: the verdict is frozen once written')
    scales, inputs = {}, {}
    for scale in (1, 2):
        passdir = root / f'preflight-{scale}x'
        spec1 = json.loads((passdir / 'scenes-run-1.json').read_text())
        spec2 = json.loads((passdir / 'scenes-run-2.json').read_text())
        cells, sha1 = read_run(passdir / 'run-1', spec1)
        repeat, sha2 = read_run(passdir / 'run-2', spec2)
        inputs[f'{scale}x'] = dict(run1ManifestSha256=sha1, run2ManifestSha256=sha2)
        scales[f'{scale}x'] = score_scale(cells, {o: repeat[('zero', o)] for o in (True, False)}, scale)
    return write_verdict(scales, inputs, out)


def write_verdict(scales, inputs, out):
    verdicts, reachable, branch = decide(scales)
    declaration = HERE / 'bounds-declaration.txt'
    doc = dict(schema='w39-preflight-verdict-1',
               computedAt=datetime.datetime.now(datetime.timezone.utc).isoformat(),
               boundsDeclarationSha256=hashlib.sha256(declaration.read_bytes()).hexdigest()
               if declaration.exists() else None,
               constants=DECLARATION_CONSTANTS, inputs=inputs, scales=scales, axes=verdicts,
               reachableAxes=reachable, branch=branch,
               admittedScenes=sorted(S.phase_scenes(tuple(reachable))))
    text = json.dumps(doc, indent=2, default=_plain) + '\n'
    Path(out).write_text(text)
    return doc


def _plain(value):
    if isinstance(value, np.generic):
        return value.item()
    if isinstance(value, np.ndarray):
        return value.tolist()
    raise TypeError(type(value))


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest='action', required=True)
    run = sub.add_parser('run', help='one scale\'s preflight pass through the sitting (runs 1-2)')
    run.add_argument('scale', type=int, choices=[1, 2])
    run.add_argument('--rehearse-refusal', action='store_true')
    score = sub.add_parser('verdict', help='score both scales and freeze preflight-verdict.json')
    score.add_argument('--root', required=True, type=Path)
    score.add_argument('--out', type=Path)
    sub.add_parser('constants', help='print the declared constants')
    args = ap.parse_args(argv)
    if args.action == 'run':
        S.main(['preflight', str(args.scale)] + (['--rehearse-refusal'] if args.rehearse_refusal else []))
    elif args.action == 'verdict':
        doc = verdict(args.root, args.out)
        print(json.dumps(dict(reachableAxes=doc['reachableAxes'], branch=doc['branch'],
                              axes=doc['axes'], admittedScenes=len(doc['admittedScenes'])), indent=2))
    else:
        print(json.dumps(DECLARATION_CONSTANTS, indent=2))


if __name__ == '__main__':
    main()
