#!/usr/bin/env python3.12
"""W43 G0 (e): the w-test — one knob, one prediction (charter Design "The w-test", clause 8; X46).

The algebra (W42's LT; light written out, dark the mirror), averaging in encoded space:

    N = C + lam * max(0, W - C),    M = (1 - w) N + w W,    y = T(M).

On the FREE side (light C >= W, dark C <= W) the hinge does not act: M - C = w (W - C), whatever k, lam and
T are. If C and W do not move with the slider, the free side's pre-tone excursion scales with w:

    r = (T25^-1(y25) - C) / (T50^-1(y50) - C) = w(0.25) / w(0.5) = 0.5     (memo D: Normal = the slider).

This module is the statistic, its support, its resolution and its verdict. It reads pixels only when given
them; `rehearse.py` drives it on synthetic renders and on W42's 0.5 frames, and G2 drives it once on the probe.

The declared choices (each a constant below, each argued where it is set):

- **Regions.** For each structured probe cell, ONE free-side region and ONE lifted-side region: the union of
  W42's own region populations (`regions.populations`: checker square cores, step bins and plateaus, patch
  cores and rings, all on the deep mask) restricted to the pixels whose backdrop LEVEL is the free (or lifted)
  level of the cell's two levels, and where the narrow term sits at that level: |C_k - B| <= C_TOL for every k
  in K_GRID under LT's maps. The free level is the brighter in light and the darker in dark: W is a convex
  mixture of the two levels, so C >= W in light exactly where C is at the brighter level, whatever k.
  Pooling a side's populations is exact for the statistic: T is monotone and M - C = w (W - C) holds per
  pixel, so the region median of y is T of the median M, and the median of C + w Delta is C + w median(Delta).
- **The statistic.** Per channel c, M_x,c = T_x,c^-1(median_c(y_x)); the region's M_x is the mean over the
  three channels (the backdrops are neutral; the channels read within one code, §5.196 §2.3), and
  r = (M25 - C) / (M50 - C). Per-channel ratios are reported beside it.
- **T at each position** is native and per channel: `tone.TableT` through the deep medians of the probe's own
  greys at that position, per stratum (capsule for t = 0, rrect-md for s = 96). In dark at s >= 96 only the
  ordinates at or below 208 enter the table, because native T falls above 208 there (§5.196 §2.1) and could
  not be inverted; a region whose inverted M50 exceeds 208 there is excluded.
- **Resolution** per region: dr = (dM25 + |r| dM50) / |M50 - C|, with dM_x = (Q + ORD) / slope_x(M_x) +
  interp_x(M_x) / slope_x(M_x). Q is the median's quantisation (half a code at the floor bar; the measured
  bar where the runs disagree), ORD the grey ordinates' own half-code quantisation, and interp the table's
  interpolation error, estimated from the curvature of the three nearest ordinates (`interp_error`).
- **Exclusions before the read** (fixed at the hash by rehearsal 3 on W42's 0.5 frames): a region under
  MIN_PX pixels; a 0.5 median censored on any channel (X21: >= 250 or <= 5); |M50 - C| < MIN_EXCURSION; a
  predicted dr (at r = 0.5, T25 stood in by T50) above DR_MAX. At the read a censored 0.25 median makes the
  region UNMEASURED (X31), never a pass.
- **The verdict** per endpoint: PASS iff |r - r_pred| <= dr on every supported, measured region, with at least
  one measured region; FAIL otherwise, with the measured ratios (which are themselves the reading of
  w(0.25) / w(0.5)). r_pred is Normal(0.25) / Normal(0.5) as memo F reads it (0.5 if the Normal input equals
  the slider, as W29 G0 and memo D read it).
- **memo F's hook** (`prediction`): the prediction is stated for an endpoint only if none of the inputs that
  set C or W moves between 0.5 and 0.25 there. An input that moves and that the declaration cannot state
  keeps the declaration open (clause 2's stop); an endpoint whose C or W inputs move is recorded as
  "no prediction stated" and read descriptively.
"""
import json
import os
from pathlib import Path
import sys

os.environ.setdefault('OPENBLAS_NUM_THREADS', '1')
os.environ.setdefault('OMP_NUM_THREADS', '1')

import numpy as np  # noqa: E402

HERE = Path(__file__).resolve().parent
EVID = HERE.parent
ROOT = HERE.parents[4]
W42 = ROOT / 'packages/calibration/results/2026-09-29-w42-g0-declaration'
sys.path.insert(0, str(W42 / 'instrument'))
import bed as IB  # noqa: E402,F401  W42's instrument, unchanged: loads the pinned bed's backgrounds and scenes
import forward as F  # noqa: E402
import geometry as G  # noqa: E402
import regions as R  # noqa: E402
from tone import TableT  # noqa: E402

PROBE_BED = EVID / 'bed' / 'probe-bed.json'
ENDPOINTS = ('light-rest', 'light-inactive', 'dark-rest', 'dark-inactive')
POSE_OF = {'rest': 'active', 'inactive': 'receded'}
GREY_SHAPE = {0: 'capsule-button', 96: 'rrect-md'}  # the probe's two grey strata: t = 0 and s = 96


def stratum(c):
    """The grey stratum a cell's T is read at: t = 0 for every s <= 64, else its span (only 96 in the probe)."""
    return 0 if c.span <= 64 else int(c.span)

# --- the declared constants ------------------------------------------------------------------------------
# k: every C-at-level test must hold over the span of W42's fitted scales, least squares 2.02-2.22 and the
# minimax points 1.40-2.48 (§5.196 §3, §4, §6), so the support does not depend on which point is right.
K_GRID = (1.4, 1.6, 1.8, 2.0, 2.2, 2.5)
K_GRID_LS = (2.0, 2.1, 2.2, 2.25)   # the least-squares span alone (2.02-2.22): a sensitivity, not the declaration
C_TOL = 0.5            # codes: the narrow term within half a code of the backdrop's own level
MIN_W_CONTRAST = 24.0  # codes: |W - C| under LT's maps at every k of the grid, so a pixel carries an excursion
MIN_PX = R.MIN_PX      # 12, W42's
CENSOR_HI, CENSOR_LO = 250.0, 5.0     # X21
DARK_T_TOP = 208.0     # dark native T is monotone only up to 208 at s >= 96 (§5.196 §2.1)
Q = 0.5                # codes: an integer median's quantisation at the floor bar (W42 G1: 0.5 everywhere)
ORD = 0.5              # codes: a grey ordinate's own quantisation
MIN_EXCURSION = 12.0   # codes: |M50 - C| observed at 0.5; below it a region carries no ratio
DR_MAX = 0.10          # the resolution a region must reach to separate 0.5 from the nearest alternative read,
#                        0.7 (a weight that tracks the slider only partly), by at least twice dr
# The declared hinge ramps at 0.25 against 0.5: Lighten 0.9 -> 0.7875 (W29 G0; memo F) and Darken the same in dark
# (memo F, memo-f/MEMO.md §1), each read as a ratio or as a difference.
LAM_SCALINGS = {'light': {'ratio': 0.7875 / 0.9, 'difference': 0.7875 - 0.9},
                'dark': {'ratio': 0.7875 / 0.9, 'difference': 0.7875 - 0.9}}


# --- cells -------------------------------------------------------------------------------------------------

def probe():
    return json.loads(PROBE_BED.read_text())


def scene_of(cid, pose):
    sid = f'{cid}__{pose}'
    return next(s for s in IB.SCENES if s['id'] == sid)


_CELLS = {}


def cell(ep, cid, rgb=True):
    """The instrument's cell for a probe cell id at an endpoint (2x, narrow mask), memoised: a cell is a pure
    function of its declaration, and its blur store is keyed by its own token."""
    key = (ep, cid, rgb)
    if key not in _CELLS:
        _CELLS[key] = _cell(ep, cid, rgb)
    return _CELLS[key]


def _cell(ep, cid, rgb):
    scheme, pose = ep.split('-')
    s = scene_of(cid, pose)
    c = F.Cell(f'2x|{cid}', s['background'], s['component'], 2, scheme, pose, rgb=rgb, kernel='n')
    c.bed_id = cid
    return c


def two_levels(spec):
    k = spec['kind']
    if k == 'checkerboard':
        return float(np.dot(spec['a'], G.W709)), float(np.dot(spec['b'], G.W709))
    if k == 'split':
        return float(np.dot(spec['from'], G.W709)), float(np.dot(spec['to'], G.W709))
    if k in ('impulse', 'patch'):
        return float(np.dot(spec['background'], G.W709)), float(np.dot(spec['foreground'], G.W709))
    return None


def free_level(scheme, levels):
    return max(levels) if scheme == 'light' else min(levels)


# --- the support -------------------------------------------------------------------------------------------

def model_conditions(c_luma, k_grid=K_GRID):
    """Per deep-mask pixel, over every k of the grid under LT's maps: the narrow term within C_TOL of the
    backdrop's level, and the wide term at least MIN_W_CONTRAST away from it. Neither depends on lam or w."""
    B = c_luma.B[c_luma.mask] * 255.0
    at_level = np.ones(B.shape, bool)
    contrast = np.ones(B.shape, bool)
    fam = F.Family()
    for k in k_grid:
        mp = F.maps(c_luma, fam, F.expand(fam, {'k': k, 'lam': 0.8}))
        at_level &= np.abs(mp['C'] * 255.0 - B) <= C_TOL
        contrast &= np.abs(mp['W'] * 255.0 - B) >= MIN_W_CONTRAST
    return at_level, contrast


def side_regions(ep, cid, k_grid=K_GRID):
    """{'free': flat canvas indices, 'lifted': ...} for one structured cell, with the populations used."""
    scheme = ep.split('-')[0]
    cl = cell(ep, cid, rgb=False)
    levels = two_levels(cl.bg_spec)
    if levels is None or abs(levels[0] - levels[1]) < 1:
        return None, 'not a two-level backdrop'
    at_level, contrast = model_conditions(cl, k_grid)
    ok_mask = np.zeros(cl.mask.size, bool)
    ok_mask[np.flatnonzero(cl.mask)] = at_level & contrast
    level_only = np.zeros(cl.mask.size, bool)
    level_only[np.flatnonzero(cl.mask)] = at_level
    level = (G.luma(G.render_background(cl.bg_spec, 2).astype(np.float64))).reshape(-1)
    union = np.zeros(cl.mask.size, bool)
    names = []
    for name, kind, idx in R.populations(cl):
        if kind in ('checker-pooled',):
            continue
        union[idx] = True
        names.append(name)
    fl = free_level(scheme, levels)
    ll = levels[0] if fl == levels[1] else levels[1]
    out = {}
    for side, lv in (('free', fl), ('lifted', ll)):
        on = union & (np.abs(level - lv) < 0.5)
        sel = on & ok_mask
        out[side] = dict(level=lv, idx=np.flatnonzero(sel), pixels=int(sel.sum()), populationPixels=int(on.sum()),
                         atLevelPixels=int((on & level_only).sum()))
    return out, None


# --- T at a position ---------------------------------------------------------------------------------------

def tables(grey_medians, scheme):
    """{stratum: [TableT per channel]} from {stratum: {level: (r, g, b) deep medians}} at one position."""
    out = {}
    for s, by_level in grey_medians.items():
        levels = sorted(by_level)
        if scheme == 'dark' and s >= 96:
            levels = [L for L in levels if L <= DARK_T_TOP]
        out[s] = [TableT(levels, [by_level[L][c] for L in levels], name=f's{s}c{c}') for c in range(3)]
    return out


def interp_error(T, M):
    """The piecewise-linear table's interpolation error at M (codes of y), estimated as the largest gap
    between the chord of M's segment and a quadratic through three neighbouring ordinates that contain it."""
    xs, ys = T.xs, T.ys
    i = int(np.clip(np.searchsorted(xs, M, side='right') - 1, 0, len(xs) - 2))
    chord = ys[i] + (ys[i + 1] - ys[i]) * (M - xs[i]) / (xs[i + 1] - xs[i])
    worst = 0.0
    for j in (i - 1, i):
        if j < 0 or j + 2 >= len(xs):
            continue
        q = np.polyfit(xs[j:j + 3], ys[j:j + 3], 2)
        worst = max(worst, abs(float(np.polyval(q, M)) - chord))
    return worst


def invert(Ts, y):
    """Per channel M = T_c^-1(y_c); the mean over channels, the mean slope and the mean interpolation error."""
    M = np.array([Ts[c].inv(y[c]) for c in range(3)])
    slope = np.array([max(float(Ts[c].slope(M[c])), 1e-6) for c in range(3)])
    interp = np.array([interp_error(Ts[c], M[c]) for c in range(3)])
    return dict(M=float(M.mean()), Mc=M.tolist(), slope=float(slope.mean()), interp=float(interp.mean()))


def ratio(C, inv25, inv50, q25=Q, q50=Q):
    """The region's r, its per-channel ratios and its propagated resolution dr."""
    D = inv50['M'] - C
    r = (inv25['M'] - C) / D if abs(D) > 1e-9 else float('nan')
    rc = [(a - C) / (b - C) if abs(b - C) > 1e-9 else float('nan') for a, b in zip(inv25['Mc'], inv50['Mc'])]
    dM25 = (q25 + ORD + inv25['interp']) / inv25['slope']
    dM50 = (q50 + ORD + inv50['interp']) / inv50['slope']
    dr = (dM25 + abs(r) * dM50) / abs(D) if abs(D) > 1e-9 else float('inf')
    return dict(r=r, rChannels=rc, dr=dr, D=D, dM25=dM25, dM50=dM50)


def invert_pixels(Ts, img, idx):
    """The per-pixel alternative (proposal P1): every pixel inverted through its channel's T, then averaged over
    the region and the channels. Exact under the algebra as the median is (M - C = w Delta per pixel is linear),
    and its region term dithers below the half-code quantisation of one median wherever the region's y spans
    several codes. Returns the same shape as `invert`, plus the number of distinct codes the region reads."""
    flat = img.reshape(-1, 3)[idx]
    Mc = [float(np.mean(Ts[c].inv(flat[:, c]))) for c in range(3)]
    M = float(np.mean(Mc))
    slope = np.array([max(float(Ts[c].slope(Mc[c])), 1e-6) for c in range(3)])
    interp = np.array([interp_error(Ts[c], Mc[c]) for c in range(3)])
    return dict(M=M, Mc=Mc, slope=float(slope.mean()), interp=float(interp.mean()),
                distinct=int(min(len(np.unique(flat[:, c])) for c in range(3))))


def censored(y):
    return any(v >= CENSOR_HI or v <= CENSOR_LO for v in y)


def medians(img, idx):
    flat = img.reshape(-1, 3)[idx]
    return [float(np.median(flat[:, c])) for c in range(3)]


def deep_medians(img, c):
    return medians(img, np.flatnonzero(c.mask))


# --- memo F's hook ----------------------------------------------------------------------------------------

# The declared inputs that set C (the narrow term, its support and capture) and W (the wide term). Field names
# are memo D's records (dumpcheck.records); `G.` is the glassBackground filter.
C_INPUTS = ('glassBackground.inputBlurRadius', 'glassBackground.inputBlurOpacity0', 'glassBackground.inputBlurOpacity1',
            'glassBackground.inputBlurOpacity2', 'glassBackground.inputBlurOpacity3', 'glassBackground.inputBlurDistance0',
            'glassBackground.inputBlurDistance1', 'glassBackground.inputBlurDistance2', 'glassBackground.inputBlurDistance3',
            'bd.scale', 'bd.marginWidth')
W_INPUTS = ('glassBackground.inputBlurFillBlurRadius', 'bd.scale', 'bd.marginWidth')
NORMAL = 'glassBackground.inputBlurFillNormalOpacity'


def prediction(memo_f=None):
    """Per endpoint: whether the prediction is stated, and r_pred. `memo_f` is memo F's reading at 0.25 against
    0.5 per endpoint: {endpoint: {'moving': [field, ...], 'normal25': float, 'normal50': float}}. Without it
    (before memo F) every endpoint carries the charter's a-priori prediction, marked pending."""
    out = {}
    for ep in ENDPOINTS:
        if memo_f is None:
            out[ep] = dict(stated=None, rPred=0.5, note='pending memo F: the a-priori prediction, w = the slider')
            continue
        m = memo_f[ep]
        moving_c = sorted(set(m['moving']) & set(C_INPUTS))
        moving_w = sorted(set(m['moving']) & set(W_INPUTS))
        stated = not moving_c and not moving_w
        out[ep] = dict(stated=stated, rPred=m['normal25'] / m['normal50'], movingC=moving_c, movingW=moving_w,
                       note='stated' if stated else 'no prediction stated: an input that sets C or W moves with x')
    return out


def prediction_from_fold(fold, tables):
    """memo F's reading as `prediction` takes it, restricted to the support's spans. `fold` is
    memo-f/reading/fold.json (fold.py), `tables` memo-f/reading/tables.json (memo_f_read.py). An input that
    moves only on a shape outside the support (memo F: the capture scale on rrect-lg at 0.25) does not
    withhold the prediction; one that moves on a support span does."""
    ep_of = {'light-rest': '2x-light-active', 'light-inactive': '2x-light-receded', 'dark-rest': '2x-dark-active',
             'dark-inactive': '2x-dark-receded'}
    memo_f = {}
    for ep, key in ep_of.items():
        ramp = tables['endpoints'][key]['ramps'][NORMAL]['values']
        normal = {x: v for pts in ramp.values() for x, v in pts.items()}
        memo_f[ep] = dict(moving=fold['endpoints'][key]['cOrWMovingAt025OnSupport'], normal25=normal['0.25'],
                          normal50=normal['0.5'])
    return prediction(memo_f)


def verdict(rows, r_pred):
    """rows: [{'region', 'status': 'measured'|'UNMEASURED', 'r', 'dr'}] over the supported regions."""
    measured = [x for x in rows if x['status'] == 'measured']
    if not measured:
        return dict(verdict='UNMEASURED', measured=0)
    fails = [x for x in measured if abs(x['r'] - r_pred) > x['dr']]
    return dict(verdict='FAIL' if fails else 'PASS', measured=len(measured), failing=len(fails),
                rMedian=float(np.median([x['r'] for x in measured])),
                worst=max(measured, key=lambda x: abs(x['r'] - r_pred) / x['dr'])['region'])


# --- the lifted side (read and reported, never gated) ------------------------------------------------------

LAM50_FITTED = {'light-rest': 0.868, 'light-inactive': 0.767, 'dark-rest': 0.851, 'dark-inactive': 0.759}
#   LT's lam at the k@global least-squares point (§5.196 §4): the 0.5 reference the lifted reading is scaled from.


def lifted_reading(ep, r_lift, w25=0.25, w50=0.5):
    """On the lifted side M - C = (w + lam (1 - w)) (W - C), so r_lift = (w25 + lam25 (1 - w25)) /
    (w50 + lam50 (1 - w50)). Returns lam25 implied by the reading and the two scalings the declared ramps
    allow: Lighten (light) and Darken (dark) 0.9 -> 0.7875, as a ratio, 0.875, or as a difference, -0.1125."""
    lam50 = LAM50_FITTED[ep]
    lam25 = (r_lift * (w50 + lam50 * (1 - w50)) - w25) / (1 - w25)
    scheme = ep.split('-')[0]
    out = dict(lam50=lam50, lam25=lam25)
    if scheme in LAM_SCALINGS:
        out.update(byRatio=lam50 * LAM_SCALINGS[scheme]['ratio'], byDifference=lam50 + LAM_SCALINGS[scheme]['difference'])
    else:
        out['note'] = f'no declared hinge ramp for scheme {scheme!r}'
    return out
