"""W42 G2 step 3 design, the second reading: can a higher-order interpolation in sigma replace levels?

`narrow_error.py` measures linear and variance-matched interpolation between L fixed-sigma levels. This
reads, on the same cells and the same exact per-pixel reference, Lagrange interpolation in sigma through
the 3 (quadratic) or 4 (cubic) nearest levels of the same uniform grids (light scheme), and two whole
realisations with decimation and float16 tiles in both schemes (below).
It imports `narrow_error.py` so the cells, samples, reference and LT output are one code path.

The first run of this file (its output kept beside it as `narrow_interp.first-run.txt`, where `chosen`
names the six-linear-level realisation that is `lin6-q12` here) found cubic Lagrange through four
levels at 0.097 code against six linear levels' 0.191, so the design moved to it; `chosen` below is that
realisation (cubic in sigma through the four nearest of four interior levels plus the contour level,
every width at or above 6 device px decimated, float16 at every stored pass), and `lin6-q12` is the
realisation first proposed (six linear levels, decimated from 12 device px, float16), both schemes.

    taskpolicy -b nice -n 19 env OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python3.12 -B narrow_interp.py
"""
import json
import os
import sys
import time

import numpy as np
from scipy import ndimage

import narrow_error as N

G = N.G


def lagrange(stack, levels, sig, order):
    """Lagrange interpolation in sigma through the `order` levels nearest each pixel's sigma."""
    n = len(levels)
    order = min(order, n)
    s = np.clip(sig, levels[0], levels[-1])
    idx = np.clip(np.searchsorted(levels, s) - (order // 2), 0, n - order)
    out = np.zeros(len(s))
    ar = np.arange(len(s))
    for j in range(order):
        wj = np.ones(len(s))
        xj = levels[idx + j]
        for m in range(order):
            if m != j:
                wj *= (s - levels[idx + m]) / (xj - levels[idx + m])
        out += wj * stack[idx + j, ar]
    return out


def main():
    rng = np.random.default_rng(20260930)
    rows = []
    t_start = time.time()
    for bg in N.BACKDROPS:
        for comp in N.ACTIVE_SHAPES:
            for scale in N.SCALES:
                s, t = G.span(comp), G.size_t(G.span(comp))
                fdev = G.backdrop_texel_dev(comp)
                B = G.luma(G.render_background(bg, scale).astype(np.float64)) / 255.0
                d = G.sdf(comp, scale)
                y0, y1, x0, x1 = N.window(comp, scale, True, d)
                dw = d[y0:y1, x0:x1]
                band = (dw < 0) & (dw > -20)
                deep = dw <= -(20 + 16.8 * t)
                py1, px1 = N.sample(rng, band, N.SAMPLES)
                py2, px2 = N.sample(rng, deep, N.SAMPLES)
                py, px = np.concatenate([py1, py2]), np.concatenate([px1, px2])
                isdeep = np.concatenate([np.zeros(len(py1), bool), np.ones(len(py2), bool)])
                wb = N.smoothstep(0, 20, -dw[py, px])
                S0 = ndimage.gaussian_filter(B[y0:y1, x0:x1], 0.4 * fdev, mode='nearest', truncate=4.0)
                for scheme in ('light', 'dark'):
                    k, lam = N.K[scheme], N.LAM[scheme]
                    sig_map = k * N.RN * N.o_active(dw, s) * scale
                    sig = sig_map[py, px]
                    Cx = np.array([N.exact_at(S0, a, b, sg, 'clamp') for a, b, sg in zip(py, px, sig)])
                    Wx = np.array([N.exact_at(S0, a, b, k * N.RW * scale, 'clamp') for a, b in zip(py, px)])
                    yx = N.lt_out(Cx, Wx, scheme, lam, s, 'active')

                    def record(name, C, Wv):
                        dC = np.abs(C - Cx) * 255
                        dy = np.abs(N.lt_out(C, Wv, scheme, lam, s, 'active') - yx)
                        rows.append(dict(bg=bg, comp=comp, scale=scale, scheme=scheme, strategy=name,
                                         C_deep_max=float(dC[isdeep].max()) if isdeep.any() else None,
                                         C_bandw_max=float((wb * dC).max()),
                                         y_deep_max=float(dy[isdeep].max()) if isdeep.any() else None,
                                         y_bandw_max=float((wb * dy).max()),
                                         y_bandw_rms=float(np.sqrt(((wb * dy) ** 2).mean()))))
                    if scheme == 'light':
                        W = N.blur(S0, k * N.RW * scale, 'clamp', N.NEVER, False)[py, px]
                        for L in (3, 4, 6):
                            lv = N.levels_for(s, scale, k, L)
                            stack = np.array([N.blur(S0, v, 'clamp', N.NEVER, False)[py, px] for v in lv])
                            record(f'lin-{L}', N.interp_levels(stack, lv, sig, 'lin'), W)
                            record(f'quad-{L}', lagrange(stack, lv, sig, 3), W)
                            record(f'cubic-{L}', lagrange(stack, lv, sig, 4), W)
                    Sh = N.f16(S0, True)
                    # The first proposal: 6 interior levels + the contour, linear in sigma, decimated from 12 dev
                    # (forward.py's FAST_FROM_DEV), float16 at every stored pass.
                    lv = N.levels_for(s, scale, k, 6)
                    stack = np.array([N.blur(Sh, v, 'clamp', 12.0, True)[py, px] for v in lv])
                    Wh = N.blur(Sh, k * N.RW * scale, 'clamp', 12.0, True)[py, px]
                    record('lin6-q12', N.f16(N.interp_levels(stack, lv, sig, 'lin'), True), Wh)
                    # The chosen realisation: 4 interior levels + the contour, cubic Lagrange in sigma through
                    # the four nearest, every width at or above 6 dev decimated, float16 at every stored pass.
                    lv = N.levels_for(s, scale, k, 4)
                    stack = np.array([N.blur(Sh, v, 'clamp', 6.0, True)[py, px] for v in lv])
                    Wh = N.blur(Sh, k * N.RW * scale, 'clamp', 6.0, True)[py, px]
                    record('chosen', N.f16(lagrange(stack, lv, sig, 4), True), Wh)
                print(f'{bg:15s} {comp:9s} {scale}x', file=sys.stderr, flush=True)
    json.dump(rows, open(os.path.join(N.HERE, 'narrow_interp.json'), 'w'), indent=0)
    lines = ['strategy  cells | C deep max  C band-weighted max | y deep max  y band-weighted max  '
             'y band-weighted rms   (active, worst over cells; the Lagrange rows light only)']
    for name in sorted({r['strategy'] for r in rows}, key=lambda n: (n.split('-')[0], n)):
        g = [r for r in rows if r['strategy'] == name]
        mx = lambda f: max(r[f] for r in g if r[f] is not None)
        lines.append(f'{name:9s} {len(g):5d} | {mx("C_deep_max"):10.3f} {mx("C_bandw_max"):19.3f} | '
                     f'{mx("y_deep_max"):10.3f} {mx("y_bandw_max"):19.3f} {mx("y_bandw_rms"):19.3f}')
    worst = sorted((r for r in rows if r['strategy'] == 'chosen'), key=lambda r: -r['y_bandw_max'])[:5]
    lines.append('\nchosen, the five worst cells by band-weighted output error:')
    for r in worst:
        lines.append(f"  {r['bg']:15s} {r['comp']:9s} {r['scale']}x {r['scheme']:5s}  C deep {r['C_deep_max']:.3f}  C bandw "
                     f"{r['C_bandw_max']:.3f}  y deep {r['y_deep_max']:.3f}  y bandw {r['y_bandw_max']:.3f}")
    text = '\n'.join(lines)
    open(os.path.join(N.HERE, 'narrow_interp.txt'), 'w').write(
        __doc__.split('\n\n')[0] + '\n\n' + text + f'\n\nrun time {time.time() - t_start:.0f} s\n')
    print(text)


if __name__ == '__main__':
    main()
