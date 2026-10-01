"""W42 G2 step 3, U2: the realisation mirror as the exact planned storage graph (the design review's
R3), with the on-luma knees' flip fractions (R1). It replaces `narrow_error.py`'s 0.115 / 0.127 as the
budget and as the shader-against-oracle tolerance (`implementation-design.md` §11).

The planned graph, per surface, every stored pass rounded to its texture format:
  0  chain level 0, the pyramid's rgba16float LINEAR import of the 8-bit source (`chain16`), or the
     8-bit source read directly (`exact8`, the alternative R1's luma knees may need);
  1  capture: each texel encoded, stored (the tile format) with a weight channel of 1 on R_fp;
  2  the floor, 0.4 f device px: horizontal pass stored, vertical pass stored (clamp to the tile);
  3  every width (the narrow levels and W): direct below 6 device px, otherwise padded by the kernel's
     reach (edge replication for clamp, zeros for normalised), q x q box-averaged and stored, blurred at
     the reduced width with each separable pass stored; the normalised mode carries (numerator, weight)
     through every stored pass and divides at the read; the decimated read is an exact bilinear
     upsample;
  4  the composite at every drawn pixel in f32: the cubic in sigma through the four nearest levels (or
     linear, or single), the knee (three forms), the Normal fill, stored as A = (M, L(W)) in the tile
     format, M unclipped (the outputs without a suffix were produced before that fix, with M clipped
     to [0, 1] on both sides; `-unclipped` is the fixed run);
  5  the optics pass reads A at the pixel (texel centres; the lens's resampling mixes the same stored
     texels and is not modelled) and applies the tone in f32.
The oracle is f64 throughout on the exact 8-bit source: exact per-pixel Gaussians at each pixel's own
sigma (narrow_error.exact_at, per channel), the same knee and fill, the same tone.

Tones ("both implemented"): candidate 1 is the landed solve per pixel (the rehearsal's `landed_T`,
`body.solve` + `body.compose`) and, light receded, E3 with the (stand-in) F extension and g at L(W);
candidate 2 is the pre-read addendum's table on the stand-in ordinates (`native_t.py`) with W41 G1's
gain. Output errors are in 8-bit codes, before rounding.

The population is every drawn pixel: active cells are sampled in three strata (the 20 pt band, the
shell from 20 to 20 + 16.8t pt, and the deep mask beyond), receded cells uniformly over the body; each
stratum's statistics are weighted by its pixel count. The band's pixels count at Decision Log 5e's
weight smoothstep(0, 20 pt, depth). A FLIP is a sampled pixel where an on-luma knee's decision
h (L(W) - L(C)) > 0 differs between the implementation and the oracle.

    taskpolicy -b nice -n 19 env OPENBLAS_NUM_THREADS=1 python3.12 -B u2_mirror.py
"""
import json
import os
import sys
import time

import numpy as np
from scipy import ndimage

HERE = os.path.dirname(os.path.abspath(__file__))
G0 = os.path.abspath(os.path.join(HERE, '..', '..', '2026-09-29-w42-g0-declaration'))
sys.path.insert(0, os.path.join(G0, 'gate', 'rehearsal'))
sys.path.insert(0, HERE)
import narrow_error as N  # noqa: E402  (also puts the instrument on the path)
import native_t as NT  # noqa: E402
import body as BODY  # noqa: E402
from swap import g_fit  # noqa: E402

G = N.G
G.load_scenes(os.path.join(G0, 'bed', 'scenes-w42-body.json'))
W709 = np.array([0.2126, 0.7152, 0.0722])
FMT = {'f16': np.float16, 'f32': np.float32}
K = {'light': 1.983, 'dark': 2.094}
K_REC = {'light': 2.035, 'dark': 2.074}
LAM = {'light': 0.88, 'dark': 0.90}
LAM_REC = {'light': 0.80, 'dark': 0.80}
WN = 0.5
PER_STRATUM = 250
# The realisation's decimation threshold in device px and the active pose's interior level count.
# §2.4 first chose 6 and 4 (outputs u2_mirror-l4-q6.*); this mirror put the landed tone at 0.295 code
# near black, above the ~0.13 target, and the revision (§11) takes the oracle's own FAST_FROM_DEV, 12,
# and six levels. W42_DECIMATE_FROM, W42_LEVELS, W42_BACKDROPS and W42_SUFFIX run the alternatives.
DECIMATE_FROM = float(os.environ.get('W42_DECIMATE_FROM', '12'))
# The perf wave (§17) decimates the ACTIVE pose's narrow levels from a lower width than the receded
# level and W: W42_DECIMATE_ACTIVE_FROM sets that threshold alone (default: DECIMATE_FROM), and
# W42_POSES restricts the run to the poses it changes.
DECIMATE_ACTIVE_FROM = float(os.environ.get('W42_DECIMATE_ACTIVE_FROM', str(DECIMATE_FROM)))
POSES = tuple(os.environ.get('W42_POSES', 'active,receded').split(','))
LEVELS = int(os.environ.get('W42_LEVELS', '6'))
BACKDROPS = ('checkerboard', 'checkerboard-8', 'checkerboard-64', 'hc-text', 'photo', 'impulse')
ACTIVE = ('capsule-button', 'rrect-80', 'rrect-md', 'rrect-ml', 'rrect-lg')
RECEDED = ('capsule-button', 'rrect-md', 'rrect-lg')
FAMILY_E = (('checker-16-rg', 'rrect-md'), ('checker-64-rg', 'rrect-md'), ('checker-16-by', 'rrect-md'),
            ('checker-64-by', 'rrect-md'), ('checker-16-rg', 'rrect-lg'), ('checker-16-by', 'rrect-lg'))


def st(x, fmt):
    if fmt == 'c16':
        # A 16-bit store of sqrt(v) (the perf wave's companded candidate, §17): v in [0, 1] rounds
        # to (round(65535 sqrt v) / 65535)^2, so its absolute error falls toward black.
        u = np.round(np.sqrt(np.clip(x, 0, 1)) * 65535) / 65535
        return u * u
    return x.astype(FMT[fmt]).astype(np.float64)


def f32(x):
    return np.asarray(x, np.float64).astype(np.float32).astype(np.float64)


def enc(v):
    v = np.clip(v, 0, 1)
    return np.where(v <= 0.0031308, 12.92 * v, 1.055 * np.power(v, 1 / 2.4) - 0.055)


def dec(c):
    c = np.clip(c, 0, 1)
    return np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)


# ---------------------------------------------------------------- the stored blurs

def gauss1(X, sig, axis, mode):
    return ndimage.gaussian_filter1d(X, sig, axis=axis, mode='nearest' if mode == 'clamp' else 'constant',
                                     truncate=4.0)


def blur_direct(X, sig, mode, fmt):
    """X (H, W, 4): rgb and a weight channel. Each separable pass is stored."""
    h = st(gauss1(X, sig, 1, mode), fmt)
    return st(gauss1(h, sig, 0, mode), fmt)


def blur_decimated(X, sig, mode, fmt):
    q = 2 if sig < 48 else 4
    sd = np.sqrt(sig ** 2 - (q * q - 1) / 12.0 - q * q / 6.0) / q
    P = int(np.ceil(4.0 * sig / q + 2)) * q
    H, W, C = X.shape
    Xp = np.pad(X, ((P, P), (P, P), (0, 0)), mode='edge' if mode == 'clamp' else 'constant')
    Hp, Wp = Xp.shape[:2]
    ny, nx = -(-Hp // q), -(-Wp // q)
    Xp = np.pad(Xp, ((0, ny * q - Hp), (0, nx * q - Wp), (0, 0)), mode='edge')
    D = st(Xp.reshape(ny, q, nx, q, C).mean(axis=(1, 3)), fmt)
    D = st(ndimage.gaussian_filter1d(D, sd, axis=1, mode='nearest', truncate=4.0), fmt)
    D = st(ndimage.gaussian_filter1d(D, sd, axis=0, mode='nearest', truncate=4.0), fmt)
    yy = (np.arange(P, P + H) + 0.5) / q - 0.5
    xx = (np.arange(P, P + W) + 0.5) / q - 0.5
    Y, Xg = np.meshgrid(yy, xx, indexing='ij')
    return np.stack([ndimage.map_coordinates(D[..., c], [Y, Xg], order=1, mode='nearest') for c in range(C)], -1)


def stored_blur(X, sig, mode, fmt, threshold=None):
    if sig < 1e-3:
        return X
    threshold = DECIMATE_FROM if threshold is None else threshold
    return blur_direct(X, sig, mode, fmt) if sig < threshold else blur_decimated(X, sig, mode, fmt)


def read(X, mode):
    """The read: rgb, divided by the weight channel when normalised (f32)."""
    if mode == 'clamp':
        return X[..., :3]
    return f32(X[..., :3] / np.maximum(X[..., 3:4], 1e-12))


# ---------------------------------------------------------------- the plan (the TS plan's mirror)

def levels_for(s, u, kn, receded):
    t = G.size_t(s)
    sc = kn * 5.0 * u
    if receded:
        return [sc * (0.4 + 0.4 * t)], 'single'
    if t == 0:
        return [0.0, sc * 0.5], 'linear'
    lv = list(np.linspace(sc * 0.4 * t, sc * 0.8 * t, LEVELS))
    if sc * 0.5 > sc * 0.8 * t + 1e-9:
        lv.append(sc * 0.5)
    return lv, 'cubic'


def opacity(d, s, receded):
    t = G.size_t(s)
    if receded:
        return np.full_like(d, 0.4 + 0.4 * t)
    return np.interp(d, [-s / 2, -1.0, 0.0], [0.8 * t, 0.4 * t, 0.5])


def interp_levels(stack, levels, sig, how):
    """stack (L, n, 3); sig (n,). Mirrors body-law.ts bodyLawInterpolateLevels."""
    levels = np.asarray(levels)
    L = len(levels)
    if how == 'single' or L == 1:
        return stack[0]
    s = np.clip(sig, levels[0], levels[-1])
    upper = np.searchsorted(levels, s, side='left')
    ar = np.arange(len(s))
    if how == 'linear' or L < 4:
        i = np.clip(upper - 1, 0, L - 2)
        w = ((s - levels[i]) / (levels[i + 1] - levels[i]))[:, None]
        return np.clip(stack[i, ar] + w * (stack[i + 1, ar] - stack[i, ar]), 0, 1)
    start = np.clip(upper - 2, 0, L - 4)
    out = np.zeros(stack.shape[1:])
    for j in range(4):
        wj = np.ones(len(s))
        xj = levels[start + j]
        for m in range(4):
            if m != j:
                wj = wj * (s - levels[start + m]) / (xj - levels[start + m])
        out += wj[:, None] * stack[start + j, ar]
    return np.clip(out, 0, 1)


def composite(C, W, knee, h, lam):
    """Returns (A (n,3), LW (n,), decision (n,) bool or None)."""
    CL, WL = C @ W709, W @ W709
    if knee == 0:
        N_ = C + h * lam * np.maximum(0, h * (W - C))
        return (1 - WN) * N_ + WN * W, WL, None
    dec_ = h * (WL - CL) > 0
    if knee == 1:
        N_ = C + lam * dec_[:, None] * (W - C)
        return (1 - WN) * N_ + WN * W, WL, dec_
    NL = CL + h * lam * np.maximum(0, h * (WL - CL))
    ML = (1 - WN) * NL + WN * WL
    return ML[:, None] + (W - WL[:, None]), WL, dec_


# ---------------------------------------------------------------- tones

# W42_BRIDGED=1 reads candidate 1 through the black-join amendment (`candidate1-black-join-addendum.md`,
# `candidate1_black_join.bridge`), the tone the runtime has drawn since `2ce1c2d5`. Unset, the tone is the
# declared solve, which is what every output of this script before the perf wave (§17) read.
BRIDGED = os.environ.get('W42_BRIDGED') == '1'


def tone_landed(ep, s, A):
    e = BODY.RES[ep]
    x = np.clip((s - e['sizeSpanMin']) / (e['sizeSpanMax'] - e['sizeSpanMin']), 0, 1)
    sizeK = x * x * (3 - 2 * x)

    def solve(X):
        c = dec(X)
        lin = c @ W709
        level = dec(X @ W709) if e['abscissa'] != 'source(default)' else lin
        return BODY.compose(e, c, BODY.solve(e, sizeK, level, lin), c)

    if BRIDGED:
        import candidate1_black_join as CJ
        return 255 * enc(CJ.bridge(solve, e, A))
    return 255 * enc(solve(A))


def tone_e3(A, LW):
    A255, LW255 = 255 * A, 255 * LW
    L = A255 @ W709
    return np.clip(BODY.e3_F(L)[:, None] + BODY.e3_gain(LW255)[:, None] * (A255 - L[:, None]), 0, 255)


TABLES = {}


def tone_table(ep, s, A):
    scheme = ep.split('-')[0]
    if ep not in TABLES:
        mc = {'light-active': 'light-rest', 'light-receded': 'light-inactive',
              'dark-active': 'dark-rest', 'dark-receded': 'dark-inactive'}[ep]
        TABLES[ep] = NT.NativeT(NT.stand_in(mc, scheme), scheme).table()
    A255 = 255 * A
    L = A255 @ W709
    f = np.clip(NT.grid_eval(TABLES[ep], L, s), 0, 255)
    return np.clip(f[:, None] + g_fit(ep, L)[:, None] * (A255 - L[:, None]), 0, 255)


def tones(ep, s, A, LW):
    out = {'cand2-table': tone_table(ep, s, A)}
    out['cand1-landed'] = tone_e3(A, LW) if ep == 'light-receded' else tone_landed(ep, s, A)
    return out


# ---------------------------------------------------------------- one cell

def run_cell(bg, comp, scale, scheme, pose, configs, rng):
    receded = pose == 'receded'
    ep = f'{scheme}-{pose}'
    k = (K_REC if receded else K)[scheme]
    lam = (LAM_REC if receded else LAM)[scheme]
    h = 1 if scheme == 'light' else -1
    s = G.span(comp)
    t = G.size_t(s)
    f = G.backdrop_texel_dev(comp)
    B8 = G.render_background(bg, scale).astype(np.float64)
    d = G.sdf(comp, scale)
    y0, y1, x0, x1 = N.window(comp, scale, not receded, d)
    B8w, dw = B8[y0:y1, x0:x1], d[y0:y1, x0:x1]
    mode = 'norm' if receded else 'clamp'
    depth = -dw
    inside = dw < 0
    strata = [('body', inside)] if receded else [
        ('band', inside & (depth < 20)), ('shell', inside & (depth >= 20) & (depth < 20 + 16.8 * t)),
        ('deep', inside & (depth >= 20 + 16.8 * t))]
    picks = []
    for name, m in strata:
        cnt = int(m.sum())
        if cnt == 0:
            continue
        py, px = N.sample(rng, m, PER_STRATUM)
        picks.append((name, py, px, cnt))
    py = np.concatenate([p[1] for p in picks])
    px = np.concatenate([p[2] for p in picks])
    wpop = np.concatenate([np.full(len(p[1]), p[3] / len(p[1])) for p in picks])   # pixels per sample
    wb = np.ones(len(py)) if receded else N.smoothstep(0, 20, depth[py, px])
    isdeep = np.concatenate([np.full(len(p[1]), p[0] in ('deep', 'body')) for p in picks])
    sig = k * 5.0 * opacity(dw[py, px], s, receded) * scale
    levels, how = levels_for(s, scale, k, receded)
    sw = k * 8.0 * scale

    # the oracle, f64, exact 8-bit source
    S0 = np.stack([ndimage.gaussian_filter(B8w[..., c] / 255, 0.4 * f, mode='nearest', truncate=4.0)
                   for c in range(3)], -1)
    ex_mode = 'clamp' if mode == 'clamp' else 'norm'
    Cx = np.array([[N.exact_at(S0[..., c], a, b, sg, ex_mode) for c in range(3)]
                   for a, b, sg in zip(py, px, sig)])
    Wx = np.array([[N.exact_at(S0[..., c], a, b, sw, ex_mode) for c in range(3)] for a, b in zip(py, px)])
    oracle = {}
    for knee in (0, 1, 2):
        A, LW, dx = composite(Cx, Wx, knee, h, lam)
        # M is NOT clipped before the tone: forward.py passes T(255 * M) (compose), and the
        # rehearsal's tones clip where their own gamut step does (body.py dec, e3_F and the final
        # clip). Until the U3/U4 review's finding this line and the implementation's below both
        # clipped, so neither could see an out-of-range argument (implementation-design.md §14).
        oracle[knee] = (tones(ep, s, A, LW), dx)

    rows = []
    for fmt, src in configs:
        if src == 'chain16':
            S_raw = st(f32(enc(st(dec(B8w / 255), 'f16'))), fmt)
        else:
            S_raw = st(B8w / 255, fmt)
        X = np.concatenate([S_raw, np.ones(S_raw.shape[:2] + (1,))], -1)
        h1 = st(gauss1(X, 0.4 * f, 1, 'clamp'), fmt)
        S = st(gauss1(h1, 0.4 * f, 0, 'clamp'), fmt)
        S[..., 3] = 1.0
        narrow_from = DECIMATE_FROM if receded else DECIMATE_ACTIVE_FROM
        stack = np.array([read(stored_blur(S, v, mode, fmt, narrow_from), mode)[py, px] for v in levels])
        Wm = read(stored_blur(S, sw, mode, fmt), mode)[py, px]
        C = f32(interp_levels(stack, levels, sig, how))
        for knee in (0, 1, 2):
            A, LW, dm = composite(f32(C), f32(Wm), knee, h, lam)
            # A is float32 under the companded tiles: M is unclipped and can leave [0, 1].
            A, LW = st(A, 'f32' if fmt == 'c16' else fmt), st(LW, 'f32' if fmt == 'c16' else fmt)
            ty = tones(ep, s, A, LW)
            ox, dx = oracle[knee]
            flips = None if dm is None else (dm != dx)
            for tone, yv in ty.items():
                err = np.abs(yv - ox[tone]).max(axis=1)
                row = dict(bg=bg, comp=comp, scale=scale, scheme=scheme, pose=pose, fmt=fmt, src=src,
                           knee=knee, tone=tone,
                           bandw_max=float((wb * err).max()),
                           deep_max=float(err[isdeep].max()) if isdeep.any() else None,
                           bandw_rms=float(np.sqrt(np.sum(wpop * (wb * err) ** 2) / np.sum(wpop))))
                if flips is not None:
                    row['flip_fraction'] = float(np.sum(wpop * flips) / np.sum(wpop))
                    row['flip_worst'] = float((wb * err)[flips].max()) if flips.any() else 0.0
                    row['nonflip_bandw_max'] = float((wb * err)[~flips].max()) if (~flips).any() else 0.0
                rows.append(row)
    return rows


def main():
    only = os.environ.get('W42_BACKDROPS')
    suffix = os.environ.get('W42_SUFFIX', '')
    rng = np.random.default_rng(20261001)
    rows = []
    t0 = time.time()
    base = tuple((fmt, 'chain16') for fmt in os.environ.get('W42_FORMATS', 'f16,f32').split(','))
    cells = []
    for bg in (BACKDROPS if not only else only.split(',')):
        for scale in (1, 2):
            for scheme in ('light', 'dark'):
                if 'active' in POSES:
                    cells += [(bg, c, scale, scheme, 'active', base) for c in ACTIVE]
                if 'receded' in POSES:
                    cells += [(bg, c, scale, scheme, 'receded', base) for c in RECEDED]
    for bg, comp in (FAMILY_E if not only else ()):
        for scheme in ('light', 'dark'):
            for pose in POSES:
                cells.append((bg, comp, 2, scheme, pose, base + tuple((f, 'exact8') for f, _ in base)))
    for i, (bg, comp, scale, scheme, pose, cfg) in enumerate(cells):
        rows += run_cell(bg, comp, scale, scheme, pose, cfg, rng)
        print(f'{i + 1}/{len(cells)} {bg} {comp} {scale}x {scheme} {pose} {time.time() - t0:.0f}s',
              file=sys.stderr, flush=True)
    json.dump(dict(rows=rows, k=K, k_receded=K_REC, lam=LAM, lam_receded=LAM_REC, per_stratum=PER_STRATUM,
                   decimate_from=DECIMATE_FROM, decimate_active_from=DECIMATE_ACTIVE_FROM, poses=POSES,
                   levels=LEVELS, backdrops=only, bridged=BRIDGED),
              open(os.path.join(HERE, f'u2_mirror{suffix}.json'), 'w'), separators=(',', ':'))
    text = summarise(rows)
    open(os.path.join(HERE, f'u2_mirror{suffix}.txt'), 'w').write(
        __doc__.split('\n\n')[0] + '\n\n' + f'decimate from {DECIMATE_FROM:g} device px (active narrow levels from {DECIMATE_ACTIVE_FROM:g}); '
        f'{LEVELS} interior levels; poses {",".join(POSES)}; '
        f'backdrops {only or "all"}; candidate 1 {"bridged" if BRIDGED else "as declared"}\n\n'
        + text + f'\n\ncells {len(cells)}, run time {time.time() - t0:.0f} s\n')
    print(text)


def summarise(rows):
    out = []
    fam = lambda r: r['bg'].startswith('checker-')
    for label, pred in (('canonical backdrops', lambda r: not fam(r)), ('family E (isoluminant)', fam)):
        out.append(f'== {label}')
        out.append('knee fmt src      tone          cells | band-weighted max  deep max  band-weighted rms | '
                   'flip fraction (max over cells)  worst at a flip  max off the flips')
        keys = sorted({(r['knee'], r['fmt'], r['src'], r['tone']) for r in rows if pred(r)})
        for kk in keys:
            g = [r for r in rows if pred(r) and (r['knee'], r['fmt'], r['src'], r['tone']) == kk]
            mx = lambda f: max((r[f] for r in g if r.get(f) is not None), default=float('nan'))
            line = (f'{kk[0]:4d} {kk[1]:4s} {kk[2]:8s} {kk[3]:13s} {len(g):5d} | {mx("bandw_max"):17.3f} '
                    f'{mx("deep_max"):9.3f} {mx("bandw_rms"):18.3f} |')
            if kk[0] != 0:
                line += (f' {mx("flip_fraction"):29.4f} {mx("flip_worst"):16.3f} {mx("nonflip_bandw_max"):18.3f}')
            out.append(line)
    return '\n'.join(out)


if __name__ == '__main__':
    main()
