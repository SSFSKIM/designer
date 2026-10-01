"""W42 G2 step 3, the implementation design: how far the WebGPU realisation of LT's two blurred terms
can sit from the EXACT Gaussians the law declares (charter Design, "The law"; the declaration's item
`law`; the instrument's `forward.py` is the oracle the shader must reproduce).

Nothing here reads a native pixel. Inputs are the committed canonical backdrop rasters, replicated by
the instrument's `geometry.py` (verified byte for byte against the fixtures by its own check), and the
declared geometry of the canonical shapes.

The law, as the instrument renders it: S = G(0.4 f dev) * B on R_fp (f = 2, 4 on rrect-lg), all in
ENCODED values; C = G(sigma_n(d)) * S with sigma_n = k 5 pt o(s, d, pose); W = G(k 8 pt) * S;
N = C + lam max(0, W - C) (light; dark the mirror); M = 0.5 N + 0.5 W; y = T(255 M).

The exact reference is evaluated PER SAMPLED PIXEL at that pixel's own sigma: a direct Gaussian with
ndimage's own truncation (radius int(4 sigma + 0.5)) and its clamp-to-edge ('nearest') or normalised
edge, so no level stack or interpolation stands under it. The strategies:

  narrow term, ACTIVE pose (sigma graded in depth; t > 0 only: at t = 0 the interior sigma is 0 and
  C = S exactly):
    lin-L       L fixed-sigma levels uniform in sigma over the interior range [k 5 0.4t, k 5 0.8t] pt,
                plus one level at the contour's o = 0.5 where it lies outside that range; the pixel's
                value interpolated linearly in sigma between its two bracketing levels
    var-L       the same levels, the interpolation weight chosen so that the mixed kernel carries the
                pixel's own VARIANCE: w = (s^2 - a^2) / (b^2 - a^2)
    sepvar      ONE separable pair at the output pixel's own sigma in each pass (the horizontal pass at
                the row pixel's sigma, the vertical at the output pixel's): no levels, error from the
                sigma gradient alone
    mip         a 2x2 box mip chain of S, trilinear at lod = log2(2 sigma) (the "interpolate pyramid
                levels" option, for comparison)
  every level and W as a direct Gaussian, or DECIMATED from a threshold sigma_q (forward.py's own
  `_blur_decimated`: a q-times box average, the reduced sigma, a bilinear return; q = 2 below 48 dev,
  4 above), and with every stored texture rounded to float16 (the tile format, rgba16float) or not.

Reported per strategy, over the sampled pixels of every cell: the error of C in ENCODED CODES
(x 255), on the deep mask (d <= -(20 + 16.8 t) pt active, d <= -8 pt receded) and weighted by the
active band's blend weight smoothstep(0, 20 pt, depth) (Decision Log 5e) over the whole body; and the
error of the OUTPUT y through LT and memo C's native-T stand-in (instrument `tone.memo_c_T`), light
and dark, at memo E's k and memo C's lambda, which is what a shader-against-oracle comparison reads.

    taskpolicy -b nice -n 19 env OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python3.12 -B narrow_error.py
"""
import json
import os
import sys
import time

import numpy as np
from scipy import ndimage

HERE = os.path.dirname(os.path.abspath(__file__))
INSTRUMENT = os.path.abspath(os.path.join(HERE, '..', '..', '2026-09-29-w42-g0-declaration', 'instrument'))
sys.path.insert(0, INSTRUMENT)
import geometry as G  # noqa: E402
import forward as F  # noqa: E402
from tone import memo_c_T  # noqa: E402

RN, RW, WN = 5.0, 8.0, 0.5
K = {'light': 1.983, 'dark': 2.094}          # memo E's k, active (families.TRUTH_K)
K_REC = {'light': 2.035, 'dark': 2.074}      # receded
LAM = {'light': 0.88, 'dark': 0.90}          # families.TRUTH_LAM, active
LAM_REC = {'light': 0.80, 'dark': 0.80}
SAMPLES = 700                                # per region per cell
BACKDROPS = ('checkerboard', 'checkerboard-8', 'checkerboard-64', 'hc-text', 'photo', 'impulse')
ACTIVE_SHAPES = ('rrect-80', 'rrect-md', 'rrect-ml', 'rrect-lg')
RECEDED_SHAPES = ('capsule-button', 'rrect-md', 'rrect-lg')
SCALES = (1, 2)
NEVER = 1e9                                  # sigma_q: never decimate
# (float16 tiles, decimate from sigma_q dev) combinations, per scheme: light carries the sweep, dark the
# two ends of it.
COMBOS = {'light': ((False, NEVER), (False, 12.0), (False, 6.0), (False, 4.0), (True, NEVER), (True, 6.0)),
          'dark': ((False, NEVER), (True, 6.0))}


def f16(x, on):
    return x.astype(np.float16).astype(np.float64) if on else x


def smoothstep(e0, e1, x):
    t = np.clip((x - e0) / (e1 - e0), 0, 1)
    return t * t * (3 - 2 * t)


def o_active(d, s):
    t = G.size_t(s)
    return np.interp(d, [-s / 2, -1.0, 0.0], [0.8 * t, 0.4 * t, 0.5])


def kernel(sig):
    r = int(4.0 * sig + 0.5)
    x = np.arange(-r, r + 1, dtype=np.float64)
    w = np.exp(-0.5 * (x / sig) ** 2)
    return x.astype(int), w / w.sum()


def exact_at(S, y, x, sig, mode, weight=None):
    """The exact Gaussian of S at one pixel (clamp: 'nearest'; norm: normalised zero padding or over
    `weight`), with ndimage's own truncation."""
    if sig < 1e-3:
        return S[y, x]
    off, g = kernel(sig)
    H, Wd = S.shape
    ys, xs = y + off, x + off
    if mode == 'clamp':
        blk = S[np.clip(ys, 0, H - 1)][:, np.clip(xs, 0, Wd - 1)]
        return g @ blk @ g
    wt = np.ones_like(S) if weight is None else weight
    vy, vx = (ys >= 0) & (ys < H), (xs >= 0) & (xs < Wd)
    gy, gx = g * vy, g * vx
    yc, xc = np.clip(ys, 0, H - 1), np.clip(xs, 0, Wd - 1)
    num = gy @ (S * wt)[yc][:, xc] @ gx
    den = gy @ wt[yc][:, xc] @ gx
    return num / den if den > 1e-12 else S[y, x]


def sepvar_at(S, y, x, sig_map):
    """One separable pair at per-pixel sigma: horizontal at each row pixel's own sigma, vertical at the
    output pixel's. Clamp-to-edge."""
    H, Wd = S.shape
    off, gv = kernel(sig_map[y, x])
    rows = np.clip(y + off, 0, H - 1)
    hv = np.empty(len(rows))
    for i, q in enumerate(rows):
        oq, gq = kernel(max(sig_map[q, x], 1e-3))
        hv[i] = S[q, np.clip(x + oq, 0, Wd - 1)] @ gq
    return gv @ hv


def blur(X, sig, mode, sig_q, half, weight=None):
    """A stored blur: direct or decimated (forward.py's `_blur_decimated`), each separable pass rounded
    to float16 when `half` (the tile format)."""
    if sig < 1e-3:
        return X
    if sig >= sig_q:
        return f16(F._blur_decimated(X, sig, mode, weight), half)
    if mode == 'clamp':
        h = f16(ndimage.gaussian_filter1d(X, sig, axis=1, mode='nearest', truncate=4.0), half)
        return f16(ndimage.gaussian_filter1d(h, sig, axis=0, mode='nearest', truncate=4.0), half)
    wt = np.ones_like(X) if weight is None else weight
    num = ndimage.gaussian_filter(X * wt, sig, mode='constant', truncate=4.0)
    den = ndimage.gaussian_filter(wt, sig, mode='constant', truncate=4.0)
    return f16(np.where(den > 1e-9, num / np.maximum(den, 1e-12), X), half)


def mip_trilinear(S, sig_map, py, px):
    """2x2 box mip chain of S returned bilinearly, trilinear at lod log2(2 sigma)."""
    H, Wd = S.shape
    levels = [S]
    while min(levels[-1].shape) >= 4 and len(levels) < 8:
        L = levels[-1]
        h2, w2 = L.shape[0] // 2 * 2, L.shape[1] // 2 * 2
        levels.append(L[:h2, :w2].reshape(h2 // 2, 2, w2 // 2, 2).mean(axis=(1, 3)))
    ups = []
    for n, L in enumerate(levels):
        f = 2 ** n
        yy = (py + 0.5) / f - 0.5
        xx = (px + 0.5) / f - 0.5
        ups.append(ndimage.map_coordinates(L, [yy, xx], order=1, mode='nearest'))
    ups = np.array(ups)
    lod = np.clip(np.log2(np.maximum(2 * sig_map[py, px], 1e-6)), 0, len(levels) - 1)
    lo = np.floor(lod).astype(int)
    hi = np.minimum(lo + 1, len(levels) - 1)
    fr = lod - lo
    ar = np.arange(len(py))
    return (1 - fr) * ups[lo, ar] + fr * ups[hi, ar]


def window(comp, scale, active, d):
    s = G.span(comp)
    inside = d <= 0
    ys, xs = np.nonzero(inside)
    m = (0.35 * s if s > 64 else 16.0) if active else 1.0 / scale
    mp = int(round(m * scale))
    H, Wd = d.shape
    return (max(0, ys.min() - mp), min(H, ys.max() + 1 + mp), max(0, xs.min() - mp), min(Wd, xs.max() + 1 + mp))


def sample(rng, mask, n):
    ys, xs = np.nonzero(mask)
    if len(ys) == 0:
        return ys, xs
    pick = rng.choice(len(ys), min(n, len(ys)), replace=False)
    return ys[pick], xs[pick]


def lt_out(C, W, scheme, lam, span, pose):
    sg = 1.0 if scheme == 'light' else -1.0
    N = C + sg * lam * np.maximum(0, sg * (W - C))
    M = (1 - WN) * N + WN * W
    ep = f"{scheme}-{'rest' if pose == 'active' else 'inactive'}"
    return memo_c_T(ep, span)(255 * M)


def levels_for(s, scale, k, L):
    t = G.size_t(s)
    lo, hi, ct = k * RN * 0.4 * t * scale, k * RN * 0.8 * t * scale, k * RN * 0.5 * scale
    lv = list(np.linspace(lo, hi, L))
    if ct > hi + 1e-9:
        lv.append(ct)
    return np.array(sorted(lv))


def interp_levels(stack, levels, sig, how):
    idx = np.clip(np.searchsorted(levels, sig) - 1, 0, len(levels) - 2)
    a, b = levels[idx], levels[idx + 1]
    s = np.clip(sig, levels[0], levels[-1])
    w = (s - a) / (b - a) if how == 'lin' else (s * s - a * a) / (b * b - a * a)
    ar = np.arange(len(sig))
    return (1 - w) * stack[idx, ar] + w * stack[idx + 1, ar]


def run_active(rows):
    rng = np.random.default_rng(20260930)
    for bg in BACKDROPS:
        for comp in ACTIVE_SHAPES:
            for scale in SCALES:
                t0 = time.time()
                s, t = G.span(comp), G.size_t(G.span(comp))
                fdev = G.backdrop_texel_dev(comp)
                B = G.luma(G.render_background(bg, scale).astype(np.float64)) / 255.0
                d = G.sdf(comp, scale)
                y0, y1, x0, x1 = window(comp, scale, True, d)
                dw = d[y0:y1, x0:x1]
                band = (dw < 0) & (dw > -20)
                deep = dw <= -(20 + 16.8 * t)
                py1, px1 = sample(rng, band, SAMPLES)
                py2, px2 = sample(rng, deep, SAMPLES)
                py, px = np.concatenate([py1, py2]), np.concatenate([px1, px2])
                isdeep = np.concatenate([np.zeros(len(py1), bool), np.ones(len(py2), bool)])
                wb = smoothstep(0, 20, -dw[py, px])
                for scheme in ('light', 'dark'):
                    k, lam = K[scheme], LAM[scheme]
                    sig_map = k * RN * o_active(dw, s) * scale
                    sig = sig_map[py, px]
                    sw = k * RW * scale
                    S0 = ndimage.gaussian_filter(B[y0:y1, x0:x1], 0.4 * fdev, mode='nearest', truncate=4.0)
                    Cx = np.array([exact_at(S0, a, b, sg, 'clamp') for a, b, sg in zip(py, px, sig)])
                    Wx = np.array([exact_at(S0, a, b, sw, 'clamp') for a, b in zip(py, px)])
                    yx = lt_out(Cx, Wx, scheme, lam, s, 'active')

                    def record(name, C, W, half, sq):
                        dC = np.abs(C - Cx) * 255
                        dy = np.abs(lt_out(C, W, scheme, lam, s, 'active') - yx)
                        rows.append(dict(pose='active', bg=bg, comp=comp, scale=scale, scheme=scheme,
                                         strategy=name, f16=half, sigma_q=sq,
                                         C_deep_max=float(dC[isdeep].max()) if isdeep.any() else None,
                                         C_deep_rms=float(np.sqrt((dC[isdeep] ** 2).mean())) if isdeep.any() else None,
                                         C_bandw_max=float((wb * dC).max()),
                                         y_deep_max=float(dy[isdeep].max()) if isdeep.any() else None,
                                         y_bandw_max=float((wb * dy).max()),
                                         y_body_rms=float(np.sqrt((dy ** 2).mean()))))

                    for half, sq in COMBOS[scheme]:
                        S = f16(S0, half)
                        W = blur(S, sw, 'clamp', sq, half)[py, px]
                        cache = {}
                        for L in (2, 3, 4, 6, 8):
                            lv = levels_for(s, scale, k, L)
                            stack = np.array([cache[round(v, 6)] if round(v, 6) in cache else
                                              cache.setdefault(round(v, 6), blur(S, v, 'clamp', sq, half)[py, px])
                                              for v in lv])
                            for how in ('lin', 'var'):
                                record(f'{how}-{L}', interp_levels(stack, lv, sig, how), W, half, sq)
                        if not half and sq == NEVER:
                            record('sepvar', np.array([sepvar_at(S, a, b, sig_map) for a, b in zip(py, px)]),
                                   W, half, sq)
                            record('mip', mip_trilinear(S, sig_map, py, px), W, half, sq)
                print(f'active {bg:15s} {comp:9s} {scale}x  {time.time() - t0:5.1f}s', file=sys.stderr, flush=True)


def run_receded(rows):
    rng = np.random.default_rng(20260931)
    for bg in BACKDROPS:
        for comp in RECEDED_SHAPES:
            for scale in SCALES:
                s = G.span(comp)
                fdev = G.backdrop_texel_dev(comp)
                B = G.luma(G.render_background(bg, scale).astype(np.float64)) / 255.0
                d = G.sdf(comp, scale)
                y0, y1, x0, x1 = window(comp, scale, False, d)
                dw = d[y0:y1, x0:x1]
                body = dw < 0
                deep = dw <= -8
                py, px = sample(rng, body, 2 * SAMPLES)
                isdeep = deep[py, px]
                for scheme in ('light', 'dark'):
                    k, lam = K_REC[scheme], LAM_REC[scheme]
                    sn, sw = k * RN * (0.4 + 0.4 * G.size_t(s)) * scale, k * RW * scale
                    S0 = ndimage.gaussian_filter(B[y0:y1, x0:x1], 0.4 * fdev, mode='nearest', truncate=4.0)
                    Cx = np.array([exact_at(S0, a, b, sn, 'norm') for a, b in zip(py, px)])
                    Wx = np.array([exact_at(S0, a, b, sw, 'norm') for a, b in zip(py, px)])
                    yx = lt_out(Cx, Wx, scheme, lam, s, 'receded')
                    for half, sq in COMBOS[scheme]:
                        S = f16(S0, half)
                        if True:
                            C = blur(S, sn, 'norm', sq, half)[py, px]
                            W = blur(S, sw, 'norm', sq, half)[py, px]
                            dC = np.abs(C - Cx) * 255
                            dW = np.abs(W - Wx) * 255
                            dy = np.abs(lt_out(C, W, scheme, lam, s, 'receded') - yx)
                            rows.append(dict(pose='receded', bg=bg, comp=comp, scale=scale, scheme=scheme,
                                             strategy='one-level', f16=half, sigma_q=sq,
                                             C_deep_max=float(dC[isdeep].max()), C_body_max=float(dC.max()),
                                             W_body_max=float(dW.max()),
                                             y_deep_max=float(dy[isdeep].max()), y_body_max=float(dy.max()),
                                             y_body_rms=float(np.sqrt((dy ** 2).mean()))))
                print(f'receded {bg:15s} {comp:14s} {scale}x', file=sys.stderr, flush=True)


def summarise(rows):
    out = []
    key = lambda r: (r['pose'], r['strategy'], r['f16'], r['sigma_q'])
    groups = {}
    for r in rows:
        groups.setdefault(key(r), []).append(r)
    # The active rows print no unweighted body rms: it is set by the outermost point, where the o law jumps
    # from 0.4t to 0.5 inside one pt and one linear segment spans it, and where the band weight is at most
    # smoothstep(0, 20, 1) = 0.0073. The JSON keeps it (y_body_rms); the band-weighted max is what renders.
    out.append('pose     strategy  f16   sigma_q  cells | C deep max  C deep rms(worst)  C band-weighted max | '
               'y deep max  y band-weighted max')
    for k_ in sorted(groups, key=lambda k: (k[0], k[1], k[2], -k[3])):
        g = groups[k_]
        pose, strat, half, sq = k_

        def mx(f):
            v = [r[f] for r in g if r.get(f) is not None]
            return max(v) if v else float('nan')
        sqs = 'never' if sq > 1e8 else f'{sq:g}'
        if pose == 'active':
            out.append(f'{pose:8s} {strat:8s} {str(half):5s} {sqs:>7s} {len(g):5d} | {mx("C_deep_max"):10.3f} '
                       f'{mx("C_deep_rms"):18.3f} {mx("C_bandw_max"):20.3f} | {mx("y_deep_max"):10.3f} '
                       f'{mx("y_bandw_max"):19.3f}')
        else:
            out.append(f'{pose:8s} {strat:9s} {str(half):5s} {sqs:>6s} {len(g):5d} | C deep max {mx("C_deep_max"):.3f}, '
                       f'C body max {mx("C_body_max"):.3f}, W body max {mx("W_body_max"):.3f} | y deep max '
                       f'{mx("y_deep_max"):.3f}, y body max {mx("y_body_max"):.3f}, y body rms {mx("y_body_rms"):.3f}')
    return '\n'.join(out)


def main():
    if sys.argv[1:] == ['--summarise']:
        rows = json.load(open(os.path.join(HERE, 'narrow_error.json')))['rows']
        text = summarise(rows)
        old = open(os.path.join(HERE, 'narrow_error.txt')).read()
        tail = old[old.rindex('run time'):]
        open(os.path.join(HERE, 'narrow_error.txt'), 'w').write(__doc__.split('\n\n')[0] + '\n\n' + text +
                                                            '\n\n' + tail)
        print(text)
        return
    rows = []
    t0 = time.time()
    run_receded(rows)
    run_active(rows)
    json.dump(dict(rows=rows, k=K, k_receded=K_REC, lam=LAM, lam_receded=LAM_REC, samples=SAMPLES),
              open(os.path.join(HERE, 'narrow_error.json'), 'w'), indent=0)
    text = summarise(rows)
    open(os.path.join(HERE, 'narrow_error.txt'), 'w').write(
        __doc__.split('\n\n')[0] + '\n\n' + text + f'\n\nrun time {time.time() - t0:.0f} s\n')
    print(text)


if __name__ == '__main__':
    main()
