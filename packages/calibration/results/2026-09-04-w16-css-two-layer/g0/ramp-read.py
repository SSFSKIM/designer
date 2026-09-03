"""W16 G0 (b) — W13's depth-window instrument, pointed at the CSS tier's own captures.

Two changes to the instrument, both forced by what the CSS tier is and neither
touching the estimator:

1. **No lens.** The tier draws no displacement field, so `thickness=0` pins W13's
   fixed lens at zero displacement and the straight-edge reduction is exact.
2. **The encoded space.** `backdrop-filter: blur()` is an operator on the page's
   ENCODED values, so the tier's capture is linear in the encoded space and not in
   luminance. The instrument is therefore fed the capture's encoded grey and its
   analytic plate unchanged — which is exact rather than approximate, because the
   probe's plates are 0 and 1 in BOTH spaces, so a blur of the encoded plate and
   the encoded blur of the plate are the same array. The model
   `Y = a + t·[(1−k)·A + k·B]` then holds bit-for-bit on this tier.

Contract X4 travels with every reading: the same call, on a page whose k(u) is a
ramp the analysis knows and the profile does not, is reported beside it.
"""
import json
import os
import sys

import numpy as np

W13 = '/Users/new/Developer/GitHub/designer/packages/calibration/results/2026-09-03-w13-ramp/g0'
if W13 not in sys.path:
    sys.path.insert(0, W13)
import w13lib as L  # noqa: E402

CAP = os.environ.get('W16_CAP', '/Users/new/.claude/jobs/5c70e47f/tmp/w16/g0/cap')
OUT = os.path.dirname(os.path.abspath(__file__))
LAW = json.load(open(f'{OUT}/pages/law.json'))
PRIMARY = ['checkerboard', 'checkerboard-32', 'checkerboard-64']


def encoded_loader(prefix, comp, scale):
    def load(backdrop):
        rgb = L.g3lib.load_rgb(f'{CAP}/{prefix}-{comp}-{backdrop}-{scale}x.png')
        return rgb.mean(-1)          # the capture is grey; its encoded value is its own luma
    return load


def read(prefix, comp, scale, backdrops=PRIMARY):
    span = L.SPAN[comp]
    lw = LAW['spans'][f'{span}@{scale}x']
    sharp = ('gauss', lw['sharpCss'])
    heavy = ('gauss', lw['heavyCss'])
    sets, tags = L.build_sets(encoded_loader(prefix, comp, scale), comp, scale, backdrops,
                              u_fit_min=2.0, thickness=0.0)
    f = L.WindowFit(sets, L.windows_for(span))
    r = f.solve_shared_t(sharp, heavy, bounds=None, t_min=-9)
    rows = f.rows(r)
    for i, row in enumerate(rows):
        row['rms'] = float(r['rms_by_window'][i])
    return dict(comp=comp, scale=scale, prefix=prefix, sharp=list(sharp), heavy=list(heavy),
                rms=r['rms'], tags=tags, rows=rows)


def validated(rows, span):
    return [x for x in rows if x['u0'] >= 4 - 1e-9 and x['u1'] <= span / 2 - 4 + 1e-9]


def truth_profile(comp, scale, kind, k0=0.3, k1=0.9, reach=40.0):
    span = L.SPAN[comp]
    if kind == 'known':
        return lambda u: k0 + (k1 - k0) * np.clip(np.asarray(u, float) / reach, 0, 1)
    ramp = np.array([p['k'] for p in LAW['spans'][f'{span}@{scale}x']['ramp']])
    return lambda u: np.interp(np.clip(np.asarray(u, float) * scale, 0, None),
                               np.arange(len(ramp)), ramp)


def report(tag, res, truth):
    span = L.SPAN[res['comp']]
    v = validated(res['rows'], span)
    u = np.array([x['u_mid'] for x in v])
    k = np.array([x['k'] for x in v])
    t = truth(u)
    d = k - t
    return dict(tag=tag, comp=res['comp'], scale=res['scale'], n_windows=len(v),
                u_lo=float(u.min()), u_hi=float(u.max()), rms=res['rms'],
                max_abs=float(np.abs(d).max()), mean=float(d.mean()),
                k_first=float(k[0]), k_last=float(k[-1]),
                truth_first=float(t[0]), truth_last=float(t[-1]),
                windows=[dict(u=float(a), k=float(b), truth=float(c)) for a, b, c in zip(u, k, t)])


def main():
    out = []
    for comp in ('rrect-md', 'rrect-lg'):
        # X4 first: a k(u) the page was built from and the profile does not carry.
        out.append(report('X4 known ramp (0.30 -> 0.90 over 40 CSS px)',
                          read('x4-ramp', comp, 1), truth_profile(comp, 1, 'known')))
        # X4 second: a page with a KNOWN flat share, the estimator's level test.
        out.append(report('X4 known flat share 0.40',
                          read('x4-two', comp, 1), lambda u: np.full_like(np.asarray(u, float), 0.4)))
        for carrier in ('raster', 'svg', 'gradient'):
            out.append(report(f'carrier {carrier}', read(f'ramp-{carrier}', comp, 1),
                              truth_profile(comp, 1, 'shader')))
    json.dump(L.to_jsonable(out), open(f'{OUT}/parts/g0-ramp-windows.json', 'w'), indent=1, sort_keys=True)
    print('| reading | cell | windows | u range | max |k − truth| | mean (k − truth) | fit RMS |')
    print('| --- ' * 7 + '|')
    for r in out:
        print(f'| {r["tag"]} | `{r["comp"]}` | {r["n_windows"]} | '
              f'{r["u_lo"]:.0f}–{r["u_hi"]:.0f} | {r["max_abs"]:.4f} | {r["mean"]:+.4f} | {r["rms"]:.5f} |')


if __name__ == '__main__':
    main()
