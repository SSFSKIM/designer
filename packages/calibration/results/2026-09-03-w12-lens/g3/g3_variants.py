"""G3 reading 8a: F1', the 1x-preserving variant, and the frequency-settled exclusion refit.

F1 (section 6) moves four constants that are landed at 1x and costs 0.0017 of 1x residual. F1' asks
what is left if every landed 1x constant is held and *only* scale terms are added:

    sigma_sharp = blurSigma 1.25 CSS px,  sigma_heavy = blurSigma x sizeScatterGainMax = 10 CSS px,
    k = 0.4 + 0.6 x smoothstep(32, 256, span)                          <- all landed, untouched at 1x
    sigma_heavy,css = 10 / dpr        (the heavy width read in device px)
    k' = min(k + dk x (dpr - 1), 1)   (the one scale term on the scatter weight)

so at dpr 1 the form *is* the landed law and its 1x numbers are the landed ones by construction.
Three variants of the sharp term at 2x: (a) 1.25 CSS px; (b) 1.25 device px = 0.625 CSS px, which is
nearer section 3's 2x core; (c) as (a) with the heavy read as 9 device px instead of 10.

The exclusion refit repeats F1's own grid and F1's dk sweep with the three frequency-settled 2x
`rrect-sm` cells of claims 5.53 removed, to see whether any winning constant is theirs.

Grid sweeps are computed from least-squares moments (as `g3_forms.py`; the helpers are repeated here
rather than imported so that each script runs on its own) and every winner is re-checked on the
images.
"""
import itertools
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np

from g3lib import *  # noqa: F401,F403

PITCHES = PITCHES4
HOLDOUT = ['rrect-lg']
SETTLED_2X = {('rrect-sm', 2, 'checkerboard-8'), ('rrect-sm', 2, 'checkerboard-64'),
              ('rrect-sm', 2, LC16)}   # claims 5.53 2; `lc16` is not one of the fit pitches

DATA = {}
for scale in SCALES:
    for comp in COMPS:
        m = box_mask(comp, scale)
        DATA[(comp, scale)] = dict(mask=m, y={b: capture(f'{b}__{comp}__rest', scale)[m]
                                              for b in PITCHES})

_pair, _single = {}, {}


def _ymom(comp, scale, b):
    y = DATA[(comp, scale)]['y'][b]
    return len(y), float(y.sum()), float((y * y).sum())


def pair_moments(b, scale, s1, s2):
    k = (b, scale, round(s1, 4), round(s2, 4))
    if k not in _pair:
        A, B = G(plate(b, scale), b, s1, scale), G(plate(b, scale), b, s2, scale)
        rec = {}
        for comp in COMPS:
            m = DATA[(comp, scale)]['mask']
            a, bb, y = A[m], B[m], DATA[(comp, scale)]['y'][b]
            n, Sy, Syy = _ymom(comp, scale, b)
            rec[comp] = dict(n=n, Sy=Sy, Syy=Syy, SA=float(a.sum()), SB=float(bb.sum()),
                             SAA=float(a @ a), SAB=float(a @ bb), SBB=float(bb @ bb),
                             SAy=float(a @ y), SBy=float(bb @ y))
        _pair[k] = rec
    return _pair[k]


def mix(rec, k):
    p, q = 1 - k, k
    return dict(n=rec['n'], Sy=rec['Sy'], Syy=rec['Syy'], Sx=p * rec['SA'] + q * rec['SB'],
                Sxx=p * p * rec['SAA'] + 2 * p * q * rec['SAB'] + q * q * rec['SBB'],
                Sxy=p * rec['SAy'] + q * rec['SBy'])


def sse_of(M):
    det = M['n'] * M['Sxx'] - M['Sx'] ** 2
    if abs(det) < 1e-12:
        return M['Syy'] - M['Sy'] ** 2 / M['n']
    t = (M['n'] * M['Sxy'] - M['Sx'] * M['Sy']) / det
    a = (M['Sy'] - t * M['Sx']) / M['n']
    return max(M['Syy'] - 2 * a * M['Sy'] - 2 * t * M['Sxy'] + a * a * M['n']
               + 2 * a * t * M['Sx'] + t * t * M['Sxx'], 0.0)


def pool(ms):
    o = dict.fromkeys(['n', 'Sy', 'Syy', 'Sx', 'Sxx', 'Sxy'], 0.0)
    for m in ms:
        for kk in o:
            o[kk] += m[kk]
    return o


def pitches_for(comp, scale, exclude):
    return [b for b in PITCHES if not (exclude and (comp, scale, b) in SETTLED_2X)]


def fast_rms(moment_of, comps, scales=SCALES, exclude=False):
    sse = n = 0.0
    for scale in scales:
        for comp in comps:
            ps = pitches_for(comp, scale, exclude)
            if not ps:
                continue
            M = pool([moment_of(comp, scale, b) for b in ps])
            sse += sse_of(M)
            n += M['n']
    return float(np.sqrt(sse / n))


def evaluate(struct, comps, scales=SCALES, exclude=False, detail=False):
    """The image path: (a, t) free per (comp, scale), pooled over the pitches."""
    sse, n, per = 0.0, 0, {}
    for scale in scales:
        for comp in comps:
            ps = pitches_for(comp, scale, exclude)
            if not ps:
                continue
            d = DATA[(comp, scale)]
            xs = [struct(comp, scale, b) for b in ps]
            y = np.concatenate([d['y'][b] for b in ps])
            coef, rms, r2 = lstsq_cols(y, [np.concatenate(xs)])
            sse += rms ** 2 * len(y)
            n += len(y)
            if detail:
                pp = {}
                for b, xb in zip(ps, xs):
                    mod = coef[0] + coef[1] * xb
                    res = d['y'][b] - mod
                    pp[b] = dict(rms=float(np.sqrt(np.mean(res ** 2))),
                                 std_ref=float(d['y'][b].std()), std_model=float(mod.std()),
                                 contrast_ratio=float(mod.std() / max(d['y'][b].std(), 1e-9)))
                per[f'{comp}@{scale}x'] = dict(a=float(coef[0]), t=float(coef[1]), rms=rms,
                                               per_pitch=pp)
    return float(np.sqrt(sse / n)), per


def k_of(span, k0, span_max):
    return k0 + (1 - k0) * smoothstep(32, span_max, span)


def two_scaled(sb_by_scale, sh_by_scale, k0, span_max, dk=0.0):
    """The two-component body with the two widths given per scale, in CSS px.

    F1' is written this way because it must be the landed law exactly at dpr 1 whatever it does at
    dpr 2: the 1x pair is always (1.25, 10) and only the 2x pair and the weight carry a scale term.
    """
    def sig(comp, scale):
        k = min(max(k_of(SPAN[comp], k0, span_max) + dk * (scale - 1), 0.0), 1.0)
        return sb_by_scale[scale], sh_by_scale[scale], k

    def st(comp, scale, b):
        lo, hi, k = sig(comp, scale)
        m = DATA[(comp, scale)]['mask']
        return ((1 - k) * G(plate(b, scale), b, lo, scale) + k * G(plate(b, scale), b, hi, scale))[m]

    def mo(comp, scale, b):
        lo, hi, k = sig(comp, scale)
        return mix(pair_moments(b, scale, lo, hi)[comp], k)
    return st, mo


def two(sh, sb, k0, span_max, dk=0.0, sb_unit='css', sh_unit='device'):
    """Returns (struct on masked vectors, moment function) for the two-component body."""
    def sig(comp, scale):
        k = min(max(k_of(SPAN[comp], k0, span_max) + dk * (scale - 1), 0.0), 1.0)
        return (sb / scale if sb_unit == 'device' else sb,
                sh / scale if sh_unit == 'device' else sh, k)

    def st(comp, scale, b):
        lo, hi, k = sig(comp, scale)
        m = DATA[(comp, scale)]['mask']
        return ((1 - k) * G(plate(b, scale), b, lo, scale) + k * G(plate(b, scale), b, hi, scale))[m]

    def mo(comp, scale, b):
        lo, hi, k = sig(comp, scale)
        return mix(pair_moments(b, scale, lo, hi)[comp], k)
    return st, mo


out = dict(settled_excluded=[list(x) for x in sorted(SETTLED_2X)], variants={}, exclusion={})

# ---------------------------------------------------------------- 1. F1', the 1x-preserving form
DK = [round(0.2 + 0.05 * i, 2) for i in range(11)]      # 0.20 … 0.70
# every variant is (1.25, 10) CSS px at 1x — the landed pair — and differs only at 2x
VARIANTS = {
    'F1p-a_sharp-1.25css_heavy-10dev': dict(sb2=1.25, sh2=5.0),    # heavy 10 device px
    'F1p-b_sharp-1.25dev_heavy-10dev': dict(sb2=0.625, sh2=5.0),   # sharp also in device px
    'F1p-c_sharp-1.25css_heavy-9dev': dict(sb2=1.25, sh2=4.5),     # heavy 9 device px at 2x only
}
print('== F1\': every landed 1x constant held, only scale terms added; dk fitted on the 2x probe alone')
landed_st, landed_mo = two_scaled({1: 1.25, 2: 1.25}, {1: 10.0, 2: 10.0}, 0.4, 256.0, 0.0)
land_fit = evaluate(landed_st, FIT_COMPS, scales=[1])[0]
land_hold = evaluate(landed_st, HOLDOUT, scales=[1])[0]
out['landed_1x'] = dict(fit=land_fit, holdout=land_hold)
print(f'   the landed law at 1x (F1\' at dpr 1, by construction): fit {land_fit:.4f} holdout {land_hold:.4f}')

for name, kw in VARIANTS.items():
    SB = {1: 1.25, 2: kw['sb2']}
    SH = {1: 10.0, 2: kw['sh2']}
    sweep = []
    for dk in DK:
        st, mo = two_scaled(SB, SH, 0.4, 256.0, dk)
        sweep.append((dk, fast_rms(mo, FIT_COMPS, scales=[2])))
    best_dk = min(sweep, key=lambda r: r[1])[0]
    st, mo = two_scaled(SB, SH, 0.4, 256.0, best_dk)
    fit2, per2 = evaluate(st, FIT_COMPS, scales=[2], detail=True)
    hold2, perh = evaluate(st, HOLDOUT, scales=[2], detail=True)
    fit1 = evaluate(st, FIT_COMPS, scales=[1])[0]
    hold1 = evaluate(st, HOLDOUT, scales=[1])[0]
    out['variants'][name] = dict(params=dict(kw, sigma_sharp_1x=1.25, sigma_heavy_1x=10.0,
                                            k0=0.4, span_max=256.0, dk=best_dk),
                                 dk_sweep=sweep, rms_2x_fit=fit2, rms_2x_holdout=hold2,
                                 rms_1x_fit=fit1, rms_1x_holdout=hold1,
                                 fit_cells=per2, holdout_cells=perh)
    assert abs(fit1 - land_fit) < 1e-9 and abs(hold1 - land_hold) < 1e-9, '1x must be untouched'
    print(f'   {name:38s} dk {best_dk:.2f}  2x fit {fit2:.4f}  2x holdout {hold2:.4f}  '
          f'(1x {fit1:.4f}/{hold1:.4f}, identical to the landed law)')
    print('      dk sweep: ' + '  '.join(f'{d}:{r:.4f}' for d, r in sweep))

print('\n== per-pitch contrast ratio at 2x (model std / reference std)')
for name in VARIANTS:
    v = out['variants'][name]
    for key in list(v['fit_cells']) + list(v['holdout_cells']):
        c = v['fit_cells'].get(key) or v['holdout_cells'][key]
        print(f'   {name[:12]:12s} {key:18s} ' + ' '.join(
            f'{b.split("-")[-1] if "-" in b else "16"}:{c["per_pitch"][b]["contrast_ratio"]:.2f}'
            for b in PITCHES))

# ---------------------------------------------------------------- the photo null at 2x
PHOTO_COMPS = ['rrect-sm', 'rrect-md', 'rrect-lg']
print('\n== the photo null at 2x (only a, t free per cell)')
photo = {}
F = json.load(open(f'{OUT}/parts/forms.json'))['forms']
P_F1 = F['F1-gpu-sharp-css_k-scale-term']['params']
cands = {'F0-landed': dict(sh=10.0, sb=1.25, k0=0.4, sm=256.0, dk=0.0, u='css', hu='css'),
         'F1': dict(sh=P_F1['sigma_heavy_dev'], sb=P_F1['sigma_sharp'], k0=P_F1['k0'],
                    sm=P_F1['span_max'], dk=P_F1['dk'], u='css', hu='device')}
for name, kw in VARIANTS.items():
    cands[name] = dict(sh=kw['sh2'] * 2, sb=kw['sb2'] * 2, k0=0.4, sm=256.0,
                       dk=out['variants'][name]['params']['dk'], u='device', hu='device')
for name, c in cands.items():
    tot = [0.0, 0]
    row = {}
    for comp in PHOTO_COMPS:
        P = plate('photo', 2)
        Y = capture(f'photo__{comp}__rest', 2)
        m = box_mask(comp, 2)
        k = min(max(k_of(SPAN[comp], c['k0'], c['sm']) + c['dk'], 0.0), 1.0)
        lo = c['sb'] / 2 if c['u'] == 'device' else c['sb']
        hi = c['sh'] / 2 if c['hu'] == 'device' else c['sh']
        col = structure_gpu(P, 'photo', 2, lo, hi, k)[m]
        coef, rms, r2 = lstsq_cols(Y[m], [col])
        row[comp] = rms
        tot[0] += rms ** 2 * int(m.sum())
        tot[1] += int(m.sum())
    photo[name] = dict(per_cell=row, overall=float(np.sqrt(tot[0] / tot[1])))
    print(f'   {name:38s} ' + ' '.join(f'{k} {v:.4f}' for k, v in row.items())
          + f'  overall {photo[name]["overall"]:.4f}')
out['photo_2x'] = photo

# ---------------------------------------------------------------- 2. the exclusion refit
SH_DEV = [6.0, 7.0, 8.0, 9.0, 10.0, 11.0, 12.0, 14.0, 16.0]
SB_CSS = [0.75, 1.0, 1.25, 1.5, 1.75, 2.0]
K0 = [0.2, 0.3, 0.4, 0.5, 0.6, 0.7]
SPANMAX = [128.0, 160.0, 192.0, 224.0, 256.0, 320.0]
DK_F1 = [-0.3, -0.2, -0.1, 0.0, 0.1, 0.2, 0.3, 0.35, 0.4, 0.45, 0.5, 0.6]

print('\n== the exclusion refit: F1\'s whole grid, with and without the three settled 2x rrect-sm cells')
for tag, excl in (('with-settled', False), ('without-settled', True)):
    best = None
    for sh, sb, k0, sm, dk in itertools.product(SH_DEV, SB_CSS, K0, SPANMAX, DK_F1):
        r = fast_rms(two(sh, sb, k0, sm, dk)[1], FIT_COMPS, exclude=excl)
        if best is None or r < best[0]:
            best = (r, dict(sigma_heavy_dev=sh, sigma_sharp=sb, k0=k0, span_max=sm, dk=dk))
    st, _ = two(best[1]['sigma_heavy_dev'], best[1]['sigma_sharp'], best[1]['k0'],
                best[1]['span_max'], best[1]['dk'])
    rec = dict(params=best[1], rms_fit=evaluate(st, FIT_COMPS, exclude=excl)[0],
               rms_holdout=evaluate(st, HOLDOUT, exclude=excl)[0],
               rms_fit_on_full_set=evaluate(st, FIT_COMPS)[0])
    out['exclusion'][f'F1-{tag}'] = rec
    print(f'   F1 {tag:16s} {best[1]}  fit {rec["rms_fit"]:.4f} holdout {rec["rms_holdout"]:.4f}')
    # and the F1' dk sweep under the same exclusion
    for name, kw in VARIANTS.items():
        sw = [(dk, fast_rms(two_scaled({1: 1.25, 2: kw['sb2']}, {1: 10.0, 2: kw['sh2']},
                                       0.4, 256.0, dk)[1],
                            FIT_COMPS, scales=[2], exclude=excl)) for dk in DK]
        bd = min(sw, key=lambda r: r[1])
        out['exclusion'][f'{name}-{tag}'] = dict(dk=bd[0], rms_2x_fit=bd[1])
        print(f'      {name:38s} dk {bd[0]:.2f}  2x fit {bd[1]:.4f}')

write_part('variants', out)
