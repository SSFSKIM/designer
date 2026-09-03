"""W15 G0: the W13 G0 instrument, re-pointed at the 2x width question.

Nothing new is modelled here. `w13lib` is imported whole — the same windowed fit (one
transmission per line set, one heavy share per 4 CSS px depth window, the lens pinned at
`main`'s landed law), the same analytic plates, the same probe beds. What this module adds
is the driver's vocabulary for W15's question: widths quoted in **device** pixels (the unit
the reference's kernel is one number in, claims §5.55 §1), the share held inside [0, 1]
because a mix cannot have a negative weight, and a read-off that names the *deep value* as
well as the start and the reach.

Every path is analysis of committed rasters. No capture is taken and no constant under
`packages/*/src` is read at runtime.
"""
import sys

import numpy as np

W13 = '/Users/new/Developer/GitHub/designer/packages/calibration/results/2026-09-03-w13-ramp/g0'
if W13 not in sys.path:
    sys.path.insert(0, W13)

import w13lib as L  # noqa: E402
import g3lib  # noqa: E402  (re-exported through w13lib's own sys.path work)

OUT = '/Users/new/Developer/GitHub/designer/packages/calibration/results/2026-09-04-w15-body-2x/g0'

COMPS = ['rrect-sm', 'capsule-button', 'rrect-md', 'rrect-ml', 'rrect-lg']
PRIMARY = ['checkerboard', 'checkerboard-32', 'checkerboard-64']

# The sharp width the pitch-axis fit reads at 2x: σ 0.5 CSS px = 1 device px (§5.55 §1).
SHARP_2X = ('gauss', 0.5)


def heavy(device_px, scale=2):
    """A heavy Gaussian quoted in device px, handed to the instrument in CSS px."""
    return ('gauss', float(device_px) / scale)


def validated(rows, span):
    return [r for r in rows if r['u0'] >= 4 - 1e-9 and r['u1'] <= span / 2 - 4 + 1e-9]


def build(comp, scale, loader=None, backdrops=None, edges=L.EDGES):
    loader = loader or L.probe_loader(comp, scale)
    sets, tags = L.build_sets(loader, comp, scale, backdrops or PRIMARY,
                              edges=edges, u_fit_min=2.0)
    return L.WindowFit(sets, L.windows_for(L.SPAN[comp])), tags


def solve(fit, sharp, hv, bounded=True):
    if bounded:
        r = fit.solve_shared_t(sharp, hv, bounds=(0.0, 1.0), t_min=0.0)
    else:
        r = fit.solve_shared_t(sharp, hv, bounds=None, t_min=-9)
    return r


def readoff(rows, span, deep_n=3):
    """Start, reach, deep value and linearity over the validated windows.

    The **deep value** is the mean sharp share over the deepest `deep_n` validated windows —
    the quantity W15's form calls `sDeep`, read where the ramp has run out. The reach is
    where a straight line through the validated windows crosses zero, as W13 G0 read it, so
    the two documents' reaches are the same statistic.
    """
    v = validated(rows, span)
    if len(v) < 1:
        return None
    u = np.array([x['u_mid'] for x in v])
    s = np.array([1 - x['k'] for x in v])
    if len(v) >= 3:
        # the reach is a straight line through the windows, as W13 G0 read it; on the two
        # thin spans there are fewer than three validated windows and no line is fitted.
        A = np.stack([np.ones_like(u), u], 1)
        c, *_ = np.linalg.lstsq(A, s, rcond=None)
        resid = s - A @ c
        ss = float(np.sum((s - s.mean()) ** 2))
        reach = float(-c[0] / c[1]) if c[1] < -1e-6 else float('inf')
    else:
        c = np.array([float('nan'), float('nan')])
        resid, ss, reach = np.zeros_like(s), 0.0, float('nan')
    n = min(deep_n, len(v))
    # Under the bound a deep tail of exact zeros drags a straight line through every window,
    # so two more read-offs travel with the reach: where the profile first arrives at zero,
    # and a line fitted only through the windows before that.
    zero = [i for i, x in enumerate(s) if x <= 5e-3]
    u_zero = float(u[zero[0]]) if zero else None
    if zero and zero[0] >= 3:
        uu, sn = u[:zero[0]], s[:zero[0]]
        cc, *_ = np.linalg.lstsq(np.stack([np.ones_like(uu), uu], 1), sn, rcond=None)
        reach_unclamped = float(-cc[0] / cc[1]) if cc[1] < -1e-6 else float('inf')
    else:
        reach_unclamped = reach
    return dict(u_zero=u_zero, reach_unclamped=reach_unclamped,
                n_clamped=int(sum(1 for x in s if x <= 5e-3)),s_first=float(s[0]), u_first=float(u[0]), s_last=float(s[-1]),
                u_last=float(u[-1]), s_min=float(s.min()), u_min=float(u[int(np.argmin(s))]),
                s_peak=float(s.max()), u_peak=float(u[int(np.argmax(s))]),
                s_deep=float(s[-n:].mean()), deep_n=int(n),
                slope=float(c[1]), intercept=float(c[0]),
                linear_r2=float(1 - np.sum(resid ** 2) / ss) if ss > 0 else float('nan'),
                reach_px=reach, reach_frac=(reach / (span / 2)) if np.isfinite(reach) else None,
                s=[float(x) for x in s], u=[float(x) for x in u])


def write_part(name, obj):
    import json
    import os
    os.makedirs(f'{OUT}/parts', exist_ok=True)
    with open(f'{OUT}/parts/{name}.json', 'w') as f:
        json.dump(L.to_jsonable(obj), f, indent=1, sort_keys=True)
    print(f'[wrote] {OUT}/parts/{name}.json')
