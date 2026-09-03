"""G3 reading 6: candidate scale-aware body forms, fitted jointly on both probes.

Fit set: spans 32 / 44 / 96 / 128 at *both* scales, four pitches each (8 / 16 / 32 / 64), the same
inset interior box and the same (a, t)-per-cell nuisance as 5.41 6. Holdout: `rrect-lg` at both
scales, never fitted. Every form is evaluated in the GPU form (two components the optics pass can
mix) and in the CSS form (one `blur()` whose σ in CSS px may depend on span and devicePixelRatio).

  F0  the landed law (blurSigma 1.25, sizeScatterGainMax 8, floor 0.4, spanMax 256), in CSS px at
      both scales, and the naive device-px variant (σ divided by the scale).
  F1  a device-pixel heavy σ: σ_heavy is one number in device px, so σ_heavy,css = σ_dev / scale;
      the sharp σ and the share law k(span) are shared across scales, or carry one scale term.
  F2  the reference's own mechanism (5.50 1–2): the plate downsampled to the quarter-device-scale
      buffer, blurred by σ = c·r with r = max(4/3, (span + 8)/42) buffer px, bilinearly upsampled,
      mixed with the *unblurred* buffer by the depth ramp (weight w0 at the contour rising to 1 at
      u = end·span, with exponent γ). One mechanism, one set of constants, both scales.

A grid sweep never materialises a model image: for a one-column least squares the residual depends
only on the sums (n, Σy, Σy², Σx, Σx², Σxy), and for a two-component mix those sums are quadratic in
the mixing weight, so one pair of convolutions serves every weight. The winner of each sweep is then
re-evaluated on the images themselves and the two RMS values are asserted equal — `moment_check`.
"""
import itertools
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np

from g3lib import *  # noqa: F401,F403

PITCHES = PITCHES4
HOLDOUT = ['rrect-lg']
SIGMA_QUANT = 0.05  # the CSS form's σ is a continuous function of the grid; quantised to this

DATA = {}
for scale in SCALES:
    for comp in COMPS:
        m = box_mask(comp, scale)
        DATA[(comp, scale)] = dict(mask=m, u=depth(comp, scale)[m],
                                   y={b: capture(f'{b}__{comp}__rest', scale)[m] for b in PITCHES})


def _ymom(comp, scale, b):
    y = DATA[(comp, scale)]['y'][b]
    return len(y), float(y.sum()), float((y * y).sum())


_pair, _single = {}, {}


def pair_moments(b, scale, s1, s2):
    """Per comp: the sums a two-component mix of G_s1 and G_s2 needs, over one pitch."""
    k = (b, scale, round(s1, 4), round(s2, 4))
    if k not in _pair:
        A = G(plate(b, scale), b, s1, scale)
        B = G(plate(b, scale), b, s2, scale)
        rec = {}
        for comp in COMPS:
            m = DATA[(comp, scale)]['mask']
            a, bb = A[m], B[m]
            y = DATA[(comp, scale)]['y'][b]
            n, Sy, Syy = _ymom(comp, scale, b)
            rec[comp] = dict(n=n, Sy=Sy, Syy=Syy, SA=float(a.sum()), SB=float(bb.sum()),
                             SAA=float(a @ a), SAB=float(a @ bb), SBB=float(bb @ bb),
                             SAy=float(a @ y), SBy=float(bb @ y))
        _pair[k] = rec
    return _pair[k]


def single_moments(b, scale, sigma):
    k = (b, scale, round(sigma / SIGMA_QUANT) * SIGMA_QUANT)
    if k not in _single:
        X = G(plate(b, scale), b, k[2], scale)
        rec = {}
        for comp in COMPS:
            m = DATA[(comp, scale)]['mask']
            x = X[m]
            y = DATA[(comp, scale)]['y'][b]
            n, Sy, Syy = _ymom(comp, scale, b)
            rec[comp] = dict(n=n, Sy=Sy, Syy=Syy, Sx=float(x.sum()), Sxx=float(x @ x),
                             Sxy=float(x @ y))
        _single[k] = rec
    return _single[k]


def sse_of(M):
    """Least-squares SSE of y ≈ a + t·x from the pooled sums."""
    det = M['n'] * M['Sxx'] - M['Sx'] ** 2
    if abs(det) < 1e-12:
        return M['Syy'] - M['Sy'] ** 2 / M['n']
    t = (M['n'] * M['Sxy'] - M['Sx'] * M['Sy']) / det
    a = (M['Sy'] - t * M['Sx']) / M['n']
    return max(M['Syy'] - 2 * a * M['Sy'] - 2 * t * M['Sxy'] + a * a * M['n']
               + 2 * a * t * M['Sx'] + t * t * M['Sxx'], 0.0)


def mix(rec, k):
    """The pooled sums of x = (1 − k)·A + k·B from a pair record."""
    p, q = 1 - k, k
    return dict(n=rec['n'], Sy=rec['Sy'], Syy=rec['Syy'],
                Sx=p * rec['SA'] + q * rec['SB'],
                Sxx=p * p * rec['SAA'] + 2 * p * q * rec['SAB'] + q * q * rec['SBB'],
                Sxy=p * rec['SAy'] + q * rec['SBy'])


def pool(ms):
    out = dict.fromkeys(['n', 'Sy', 'Syy', 'Sx', 'Sxx', 'Sxy'], 0.0)
    for m in ms:
        for kk in out:
            out[kk] += m[kk]
    return out


def fast_rms(moment_of, comps, scales=SCALES):
    """moment_of(comp, scale, backdrop) → pooled sums for one pitch."""
    sse = n = 0.0
    for scale in scales:
        for comp in comps:
            M = pool([moment_of(comp, scale, b) for b in PITCHES])
            sse += sse_of(M)
            n += M['n']
    return float(np.sqrt(sse / n))


# ---- the slow path, used for the reports and as the check on the fast one
def evaluate(struct, comps, scales=SCALES, detail=False):
    sse, n, per = 0.0, 0, {}
    for scale in scales:
        for comp in comps:
            d = DATA[(comp, scale)]
            xs = [struct(comp, scale, b) for b in PITCHES]
            y = np.concatenate([d['y'][b] for b in PITCHES])
            coef, rms, r2 = lstsq_cols(y, [np.concatenate(xs)])
            sse += rms ** 2 * len(y)
            n += len(y)
            if detail:
                pp = {}
                for b, xb in zip(PITCHES, xs):
                    mod = coef[0] + coef[1] * xb
                    res = d['y'][b] - mod
                    pp[b] = dict(rms=float(np.sqrt(np.mean(res ** 2))),
                                 std_ref=float(d['y'][b].std()), std_model=float(mod.std()),
                                 contrast_ratio=float(mod.std() / max(d['y'][b].std(), 1e-9)))
                per[f'{comp}@{scale}x'] = dict(a=float(coef[0]), t=float(coef[1]), rms=rms, per_pitch=pp)
    return float(np.sqrt(sse / n)), per


def report(name, struct, extra=None, fast=None):
    fit_rms, fit_per = evaluate(struct, FIT_COMPS, detail=True)
    hold_rms, hold_per = evaluate(struct, HOLDOUT, detail=True)
    per_scale = {f'{s}x': dict(fit=evaluate(struct, FIT_COMPS, scales=[s])[0],
                               holdout=evaluate(struct, HOLDOUT, scales=[s])[0]) for s in SCALES}
    rec = dict(name=name, rms_fit=fit_rms, rms_holdout=hold_rms, per_scale=per_scale,
               fit_cells=fit_per, holdout_cells=hold_per, params=extra or {})
    if fast is not None:
        rec['moment_check'] = dict(fast=fast, slow=fit_rms, delta=abs(fast - fit_rms))
        assert abs(fast - fit_rms) < 2e-4, (name, fast, fit_rms)
    print(f'{name:38s} fit {fit_rms:.4f}  holdout {hold_rms:.4f}  | '
          + '  '.join(f'{k} fit {v["fit"]:.4f}/hold {v["holdout"]:.4f}' for k, v in per_scale.items()),
          flush=True)
    return rec


out = dict(fit_comps=FIT_COMPS, holdout=HOLDOUT, pitches=PITCHES, sigma_quantum=SIGMA_QUANT, forms={})


def k_of(span, k0, span_max):
    return k0 + (1 - k0) * smoothstep(32, span_max, span)


# ---------------------------------------------------------------- F0 / F1 (two components)
def sigmas(comp, scale, sh, sb, k0, span_max, dk=0.0, sb_unit='css', sh_unit='device'):
    """(σ_sharp, σ_heavy) in CSS px at this scale, and the mixing weight k."""
    k = min(max(k_of(SPAN[comp], k0, span_max) + (dk if scale == 2 else 0.0), 0.0), 1.0)
    lo = sb / scale if sb_unit == 'device' else sb
    hi = sh / scale if sh_unit == 'device' else sh
    return lo, hi, k


def two_struct(sh, sb, k0, span_max, dk=0.0, sb_unit='css', sh_unit='device', css=False):
    def s(comp, scale, b):
        lo, hi, k = sigmas(comp, scale, sh, sb, k0, span_max, dk, sb_unit, sh_unit)
        m = DATA[(comp, scale)]['mask']
        if css:
            sig = round((lo * (1 - k) + hi * k) / SIGMA_QUANT) * SIGMA_QUANT
            return G(plate(b, scale), b, sig, scale)[m]
        return ((1 - k) * G(plate(b, scale), b, lo, scale) + k * G(plate(b, scale), b, hi, scale))[m]
    return s


def two_moment(sh, sb, k0, span_max, dk=0.0, sb_unit='css', sh_unit='device', css=False):
    def f(comp, scale, b):
        lo, hi, k = sigmas(comp, scale, sh, sb, k0, span_max, dk, sb_unit, sh_unit)
        if css:
            return single_moments(b, scale, lo * (1 - k) + hi * k)[comp]
        return mix(pair_moments(b, scale, lo, hi)[comp], k)
    return f


print('== F0: the landed law at both scales, and the naive device-px variant')
P0 = dict(blurSigma=1.25, sizeScatterGainMax=8, sizeScatterFloor=0.4, sizeScatterSpanMax=256)
for tag, unit, css in (('gpu-css-px', 'css', False), ('gpu-device-px', 'device', False),
                       ('css-css-px', 'css', True), ('css-device-px', 'device', True)):
    kw = dict(sb_unit=unit, sh_unit=unit, css=css)
    out['forms'][f'F0-{tag}'] = report(
        f'F0 {tag}', two_struct(10.0, 1.25, 0.4, 256.0, **kw), dict(P0, variant=tag, unit=unit),
        fast=fast_rms(two_moment(10.0, 1.25, 0.4, 256.0, **kw), FIT_COMPS))

# ---------------------------------------------------------------- F1
SH_DEV = [6.0, 7.0, 8.0, 9.0, 10.0, 11.0, 12.0, 14.0, 16.0]
SB_CSS = [0.75, 1.0, 1.25, 1.5, 1.75, 2.0]
K0 = [0.2, 0.3, 0.4, 0.5, 0.6, 0.7]
SPANMAX = [128.0, 160.0, 192.0, 224.0, 256.0, 320.0]
DK = [-0.3, -0.2, -0.1, 0.0, 0.1, 0.2, 0.3, 0.35, 0.4, 0.45, 0.5, 0.6]  # the one scale term: k0(2x) − k0(1x)

print('\n== F1: heavy σ in device px (grid on the fit set, the holdout untouched)')
F1_VARIANTS = (('css', False, 'sharp-css_k-shared'), ('device', False, 'sharp-device_k-shared'),
               ('css', True, 'sharp-css_k-scale-term'))
for css in (False, True):
    tier = 'css' if css else 'gpu'
    for sb_unit, use_dk, label in F1_VARIANTS:
        best = None
        for sh, sb, k0, sm in itertools.product(SH_DEV, SB_CSS, K0, SPANMAX):
            for dk in (DK if use_dk else [0.0]):
                r = fast_rms(two_moment(sh, sb, k0, sm, dk, sb_unit, 'device', css), FIT_COMPS)
                if best is None or r < best[0]:
                    best = (r, dict(sigma_heavy_dev=sh, sigma_sharp=sb, k0=k0, span_max=sm, dk=dk))
        p = best[1]
        p['sigma_sharp_unit'] = sb_unit
        out['forms'][f'F1-{tier}-{label}'] = report(
            f'F1 {tier.upper()} ({label})',
            two_struct(p['sigma_heavy_dev'], p['sigma_sharp'], p['k0'], p['span_max'], p['dk'],
                       sb_unit, 'device', css), p, fast=best[0])
        print(f'      best: {p}')

# ---------------------------------------------------------------- F2, the quarter-scale buffer
C = [0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.1, 1.25, 1.4, 1.6, 1.8, 2.0]
W0 = [0.2, 0.3, 0.4, 0.5, 0.6, 0.7]
END = [0.25, 0.375, 0.5, 0.75, 1.0]
GAMMA = [0.25, 0.35, 0.5, 0.75, 1.0, 1.5, 2.0]

_qm = {}


def qbuf(b, scale, comp, c, filt='box'):
    """(U, B − U) cropped to the cell's box, for σ_buffer = c·r(span)."""
    k = (b, scale, comp, round(c * blur_radius_buffer_px(SPAN[comp]), 4), filt)
    if k not in _qm:
        U, B = quarter_buffer(plate(b, scale), b, scale, k[3], filt)
        m = DATA[(comp, scale)]['mask']
        _qm[k] = (U[m], (B - U)[m])
    return _qm[k]


def f2_struct(c, w0, end, gamma, filt='box', dw=0.0):
    """dw is the one scale term the ramp may carry: w_edge(2x) = w_edge(1x) + dw."""
    def s(comp, scale, b):
        U, D = qbuf(b, scale, comp, c, filt)
        u = DATA[(comp, scale)]['u']
        w_edge = min(max(w0 + (dw if scale == 2 else 0.0), 0.0), 1.0)
        w = w_edge + (1 - w_edge) * np.clip(u / max(end * SPAN[comp], 1e-6), 0, 1) ** gamma
        return U + w * D
    return s


def f2_moment(c, w0, end, gamma, filt='box', dw=0.0):
    st = f2_struct(c, w0, end, gamma, filt, dw)

    def f(comp, scale, b):
        x = st(comp, scale, b)
        y = DATA[(comp, scale)]['y'][b]
        n, Sy, Syy = _ymom(comp, scale, b)
        return dict(n=n, Sy=Sy, Syy=Syy, Sx=float(x.sum()), Sxx=float(x @ x), Sxy=float(x @ y))
    return f


print("\n== F2: the reference's quarter-device-scale buffer (box downsample unless said otherwise)")
best = None
for c, w0, end, gamma in itertools.product(C, W0, END, GAMMA):
    r = fast_rms(f2_moment(c, w0, end, gamma), FIT_COMPS)
    if best is None or r < best[0]:
        best = (r, dict(c=c, w_edge=w0, end_frac=end, gamma=gamma))
p2 = best[1]
out['forms']['F2-quarter-buffer'] = report('F2 quarter buffer (box)',
                                           f2_struct(p2['c'], p2['w_edge'], p2['end_frac'], p2['gamma']),
                                           dict(p2, filter='box'), fast=best[0])
print(f'      best: {p2}; σ in CSS px = 4·c·r/scale → '
      + ', '.join(f'{c}: {4 * p2["c"] * blur_radius_buffer_px(SPAN[c]):.1f}/'
                  f'{2 * p2["c"] * blur_radius_buffer_px(SPAN[c]):.1f}' for c in COMPS) + '  (1x/2x)')
out['forms']['F2-quarter-buffer-bilinear'] = report(
    'F2 quarter buffer (bilinear down)',
    f2_struct(p2['c'], p2['w_edge'], p2['end_frac'], p2['gamma'], 'bilinear'), dict(p2, filter='bilinear'))

DW = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6]
bestb = None
for c, w0, end, gamma, dw in itertools.product(C, W0, END, GAMMA, DW):
    r = fast_rms(f2_moment(c, w0, end, gamma, 'box', dw), FIT_COMPS)
    if bestb is None or r < bestb[0]:
        bestb = (r, dict(c=c, w_edge=w0, end_frac=end, gamma=gamma, dw=dw))
p2b = bestb[1]
out['forms']['F2-quarter-buffer-scale-term'] = report(
    'F2 quarter buffer + ramp scale term',
    f2_struct(p2b['c'], p2b['w_edge'], p2b['end_frac'], p2b['gamma'], 'box', p2b['dw']),
    dict(p2b, filter='box'), fast=bestb[0])
print(f'      best: {p2b}')

C2 = [0.15, 0.2, 0.25, 0.3, 0.35, 0.4, 0.5, 0.6, 0.75, 1.0]


def f2css_struct(c2):
    def s(comp, scale, b):
        return G(plate(b, scale), b, c2 * 4 * blur_radius_buffer_px(SPAN[comp]) / scale,
                 scale)[DATA[(comp, scale)]['mask']]
    return s


def f2css_moment(c2):
    def f(comp, scale, b):
        return single_moments(b, scale, c2 * 4 * blur_radius_buffer_px(SPAN[comp]) / scale)[comp]
    return f


bc = min(((fast_rms(f2css_moment(c2), FIT_COMPS), c2) for c2 in C2))
out['forms']['F2-css-one-blur'] = report(
    'F2 CSS (σ = c·4r/scale)', f2css_struct(bc[1]),
    dict(c2=bc[1], sigma_css_1x={c: bc[1] * 4 * blur_radius_buffer_px(SPAN[c]) for c in COMPS}))
print(f'      best c2 {bc[1]} → σ (CSS px at 1x) '
      + ', '.join(f'{c}:{bc[1] * 4 * blur_radius_buffer_px(SPAN[c]):.2f}' for c in COMPS))

# the CSS tier's own ceiling: the best free single σ per (span, scale)
ceiling = {}
for scale in SCALES:
    for comp in COMPS:
        bs = None
        for s in SIG_SINGLE:
            M = pool([single_moments(b, scale, s)[comp] for b in PITCHES])
            rms = float(np.sqrt(sse_of(M) / M['n']))
            if bs is None or rms < bs['rms']:
                bs = dict(sigma=s, sigma_dev=s * scale, rms=rms)
        ceiling[f'{comp}@{scale}x'] = bs
out['css_single_sigma_ceiling'] = ceiling
print("\n== the CSS tier's ceiling: best free single σ per span and scale, pooled over the four pitches")
for k, v in ceiling.items():
    print(f'   {k:22s} σ {v["sigma"]:5.2f} css ({v["sigma_dev"]:5.2f} dev)  rms {v["rms"]:.4f}')

# ---------------------------------------------------------------- declared-grid discipline
print('\n== one-dimensional sweeps around each winner (is each constant at its own minimum?)')
b1 = out['forms']['F1-gpu-sharp-css_k-scale-term']['params']
sw1 = dict(
    sigma_heavy_dev=[(v, fast_rms(two_moment(v, b1['sigma_sharp'], b1['k0'], b1['span_max'], b1['dk']), FIT_COMPS)) for v in SH_DEV],
    sigma_sharp=[(v, fast_rms(two_moment(b1['sigma_heavy_dev'], v, b1['k0'], b1['span_max'], b1['dk']), FIT_COMPS)) for v in SB_CSS],
    k0=[(v, fast_rms(two_moment(b1['sigma_heavy_dev'], b1['sigma_sharp'], v, b1['span_max'], b1['dk']), FIT_COMPS)) for v in K0],
    span_max=[(v, fast_rms(two_moment(b1['sigma_heavy_dev'], b1['sigma_sharp'], b1['k0'], v, b1['dk']), FIT_COMPS)) for v in SPANMAX],
    dk=[(v, fast_rms(two_moment(b1['sigma_heavy_dev'], b1['sigma_sharp'], b1['k0'], b1['span_max'], v), FIT_COMPS)) for v in DK])
sw2 = dict(
    c=[(v, fast_rms(f2_moment(v, p2['w_edge'], p2['end_frac'], p2['gamma']), FIT_COMPS)) for v in C],
    w_edge=[(v, fast_rms(f2_moment(p2['c'], v, p2['end_frac'], p2['gamma']), FIT_COMPS)) for v in W0],
    end_frac=[(v, fast_rms(f2_moment(p2['c'], p2['w_edge'], v, p2['gamma']), FIT_COMPS)) for v in END],
    gamma=[(v, fast_rms(f2_moment(p2['c'], p2['w_edge'], p2['end_frac'], v), FIT_COMPS)) for v in GAMMA])
sw2b = dict(
    c=[(v, fast_rms(f2_moment(v, p2b['w_edge'], p2b['end_frac'], p2b['gamma'], 'box', p2b['dw']), FIT_COMPS)) for v in C],
    w_edge=[(v, fast_rms(f2_moment(p2b['c'], v, p2b['end_frac'], p2b['gamma'], 'box', p2b['dw']), FIT_COMPS)) for v in W0],
    end_frac=[(v, fast_rms(f2_moment(p2b['c'], p2b['w_edge'], v, p2b['gamma'], 'box', p2b['dw']), FIT_COMPS)) for v in END],
    gamma=[(v, fast_rms(f2_moment(p2b['c'], p2b['w_edge'], p2b['end_frac'], v, 'box', p2b['dw']), FIT_COMPS)) for v in GAMMA],
    dw=[(v, fast_rms(f2_moment(p2b['c'], p2b['w_edge'], p2b['end_frac'], p2b['gamma'], 'box', v), FIT_COMPS)) for v in DW])
out['sweeps'] = dict(F1_gpu_scale_term=sw1, F2=sw2, F2_scale_term=sw2b)
for form, sw in out['sweeps'].items():
    for k, vals in sw.items():
        print(f'   {form:22s} {k:18s} ' + '  '.join(f'{v}:{r:.4f}' for v, r in vals))

write_part('forms', out)
