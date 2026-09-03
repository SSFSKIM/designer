"""W16 G0 — the readings that are not the body's RMS or the ramp's windows.

Five questions, one script, all of them on the captures `capture.mjs` wrote:

  §0   does `mask-image` compose with `backdrop-filter` and `opacity` on one element
  §1.2 is the capture's residual against the reference the ENCODED space, measured
  §1.4 the contour ring: the tint under the two layers against the tint over them
  §2.1 each mask carrier's realised alpha against the shader's k(u), read without a filter
  §4   the lift: what a blend mode does to a filtered layer, and what it costs on the bed

Everything is read in the space the question lives in: the mask and the blend
questions in the page's ENCODED values, because that is what CSS composites in and
what makes their predictions exact arithmetic; the body's residual in linear
luminance, because that is the space the reference's law is linear in.
"""
import json
import os
import sys

import numpy as np
from scipy.ndimage import gaussian_filter

G3 = '/Users/new/Developer/GitHub/designer/packages/calibration/results/2026-09-03-w12-lens/g3'
if G3 not in sys.path:
    sys.path.insert(0, G3)
import g3lib  # noqa: E402

CAP = os.environ.get('W16_CAP', '/Users/new/.claude/jobs/5c70e47f/tmp/w16/g0/cap')
OUT = os.path.dirname(os.path.abspath(__file__))
LAW = json.load(open(f'{OUT}/pages/law.json'))
P4 = g3lib.PITCHES4
WEB = '/Users/new/Developer/GitHub/designer/packages/calibration/web-captures'
FIX = '/Users/new/Developer/GitHub/designer/apps/reference-apple/fixtures'

lin = lambda i: g3lib.luma_lin(g3lib.load_rgb(f'{CAP}/{i}.png'))          # noqa: E731
enc = lambda i: g3lib.load_rgb(f'{CAP}/{i}.png').mean(-1)                 # noqa: E731
srgb_enc = lambda c: np.where(np.clip(c, 0, 1) <= 0.0031308, np.clip(c, 0, 1) * 12.92,   # noqa: E731
                              1.055 * np.clip(c, 0, 1) ** (1 / 2.4) - 0.055)
srgb_dec = lambda c: np.where(np.clip(c, 0, 1) <= 0.04045, np.clip(c, 0, 1) / 12.92,     # noqa: E731
                              ((np.clip(c, 0, 1) + 0.055) / 1.055) ** 2.4)


def section0():
    m = g3lib.box_mask('rrect-md', 1)
    full = np.ones_like(m, bool)
    rows = []
    for a, b, label in (('mq-two-040', 'mq-mask-040', 'opacity 0.40 vs mask alpha 0.40'),
                        ('mq-two-040', 'mq-mask08-op05', 'opacity 0.40 vs mask 0.80 x opacity 0.5'),
                        ('mq-two-000', 'mq-mask-000', 'opacity 0 vs mask alpha 0'),
                        ('mq-two-100', 'mq-mask-100', 'opacity 1 vs mask alpha 1')):
        A, B = lin(a), lin(b)
        d = A - B
        rows.append(dict(pair=label, rms_box=float(np.sqrt((d[m] ** 2).mean())),
                         max_box=float(np.abs(d[m]).max()), max_canvas=float(np.abs(d[full]).max())))
    S, T, H = lin('md-two-000'), lin('md-two-040'), lin('md-two-100')
    r = lambda Y, R: float(np.sqrt(((Y - R)[m] ** 2).mean()))              # noqa: E731
    variants = {}
    for v in ('opacity', 'png-alpha', 'png-plain', 'webkit-png', 'gradient', 'webkit-gradient',
              'mask-opaque', 'clip-path', 'parent-mask', 'will-change'):
        Y = lin(f'md-{v}')
        a, b, c = r(Y, S), r(Y, T), r(Y, H)
        verdict = ('the filter is inert' if a < 1e-9 else 'composes' if b < 1e-9
                   else 'the carrier is inert' if c < 1e-9 else 'other')
        variants[v] = dict(vs_sharp_only=a, vs_share_040=b, vs_heavy_full=c, verdict=verdict)
    return dict(pairs=rows, variants=variants)


def section1_2():
    out = {}
    for comp in g3lib.COMPS:
        span, m = g3lib.SPAN[comp], g3lib.box_mask(comp, 1)
        k = LAW['spans'][f'{span}@1x']['kDeep']
        y = np.concatenate([g3lib.capture(f'{b}__{comp}__rest', 1)[m] for b in P4])
        cols = {}
        chain = {}
        for b in P4:
            P = g3lib.plate(b, 1)
            e = srgb_enc(P)
            sharp = gaussian_filter(e, 1.25, mode='nearest')
            heavy = gaussian_filter(sharp, 1.25 * np.sqrt(63), mode='nearest')
            chain[b] = srgb_dec((1 - k) * sharp + k * heavy)
            cols[b] = ((1 - k) * srgb_dec(gaussian_filter(e, 1.25, mode='nearest'))
                       + k * srgb_dec(gaussian_filter(e, 10.0, mode='nearest')))
        fit = lambda c: g3lib.lstsq_cols(y, [np.concatenate([c[b][m] for b in P4])])[1]  # noqa: E731
        cap = {b: lin(f'twoK-{comp}-{b}-1x') for b in P4}
        # the capture against the forward model of what the page was asked to draw
        own = max(g3lib.lstsq_cols(cap[b][m], [chain[b][m]])[1] for b in P4)
        out[comp] = dict(encoded_two_component=float(fit(cols)), encoded_chain=float(fit(chain)),
                         capture=float(fit(cap)), capture_vs_own_model=float(own))
    return out


def section1_4():
    out = {}
    for comp in ('rrect-md', 'rrect-lg'):
        u = g3lib.depth(comp, 1)
        U, O = enc(f'tint-under-{comp}'), enc(f'tint-over-{comp}')
        bands = {}
        for lo, hi in ((0, 1), (1, 2), (2, 4), (4, 8), (8, 16), (16, 32)):
            m = (u >= lo) & (u < hi)
            if m.any():
                bands[f'{lo}-{hi}'] = dict(under=float(U[m].mean()), over=float(O[m].mean()),
                                           delta=float(U[m].mean() - O[m].mean()))
        m = u > 0
        bands['silhouette'] = dict(under=float(U[m].mean()), over=float(O[m].mean()),
                                   delta=float(U[m].mean() - O[m].mean()))
        out[comp] = bands
    return out


def section2_1():
    out = {}
    for comp, span in (('rrect-md', 96), ('rrect-lg', 160)):
        kk = np.array([r['k'] for r in LAW['spans'][f'{span}@1x']['ramp']])
        u = g3lib.depth(comp, 1)
        kex = np.interp(np.clip(u, 0, None), np.arange(len(kk)), kk)
        w, h, r = g3lib.COMP[comp]
        ys, xs = np.mgrid[0:200, 0:320]
        corner = (np.abs(xs + 0.5 - 160) >= w / 2 - r) & (np.abs(ys + 0.5 - 100) >= h / 2 - r)
        inside = u > 1.0                       # the contour pixel is antialiased, not carried
        for c in ('raster', 'svg', 'gradient'):
            field = enc(f'field-{c}-{comp}')
            for name, mask in (('inside', inside), ('straight', inside & ~corner),
                               ('corners', inside & corner)):
                d = np.abs((field - kex)[mask])
                out[f'{c}@{comp}:{name}'] = dict(mean=float(d.mean()), p99=float(np.percentile(d, 99)),
                                                 max=float(d.max()))
    return out


def section4():
    u = g3lib.depth('rrect-md', 1)
    ring = (u < -4) & (u > -20)
    g, f = 128 / 255, min(1.0, 1.5 * 128 / 255)
    blends = {}
    for prefix, wrapped in (('lf2', False), ('lf3-wrap', True)):
        names = ('plus-lighter', 'normal', 'screen') if not wrapped else ('plus-lighter', 'normal')
        for b in names:
            for a in ('0.4', '1'):
                key = f'{prefix}-{b}' + ('' if (a == '0.4' and not wrapped) else
                                         ('-a1' if not wrapped else f'-{a}'))
                if not os.path.exists(f'{CAP}/{key}.png'):
                    continue
                A = float(a)
                blends[f'{"wrapped " if wrapped else ""}{b} @ opacity {a}'] = dict(
                    measured=float(enc(key)[ring].mean()), ground=g,
                    normal_predicts=g * (1 - A) + A * f, plus_predicts=min(1.0, g + A * f),
                    screen_predicts=g * (1 - A) + A * (1 - (1 - g) * (1 - f)))
    m = g3lib.box_mask('rrect-md', 1)
    B = enc('lf-body-only')
    reroot = {}
    for v in ('lf-body-ring-after', 'lf-body-ring-first', 'lf3-wrap-body'):
        if os.path.exists(f'{CAP}/{v}.png'):
            d = (enc(v) - B)[m]
            reroot[v] = dict(rms=float(np.sqrt((d ** 2).mean())), max=float(np.abs(d).max()))
    bed = {}
    for scene, comp in (('photo__rrect-md__rest', 'rrect-md'),
                        ('light-solid__rrect-md__rest', 'rrect-md'),
                        ('light-solid__rrect-ml__rest', 'rrect-ml')):
        d = f'{WEB}/apple-macos-26.5-1x-light-standard/{scene}'
        if not os.path.exists(f'{d}/{scene}__webgpu.png'):
            bed[scene] = 'no canonical capture on this machine'
            continue
        G = g3lib.load_rgb(f'{d}/{scene}__webgpu.png').mean(-1)
        C = g3lib.load_rgb(f'{d}/{scene}__css.png').mean(-1)
        N = g3lib.load_rgb(f'{FIX}/apple-macos-26.5-1x-light-standard/{scene}.png').mean(-1)
        uu = g3lib.depth(comp, 1)
        rg = (uu < 0) & (uu > -25)
        bed[scene] = dict(gpu_minus_css=float((G - C)[rg].mean()),
                          native_minus_css=float((N - C)[rg].mean()),
                          native_minus_gpu=float((N - G)[rg].mean()))
    return dict(blends=blends, re_rooting=reroot, canonical_ring=bed)


def main():
    out = dict(mask_composition=section0(), colour_space=section1_2(), contour_ring=section1_4(),
               carrier_alpha=section2_1(), lift=section4())
    os.makedirs(f'{OUT}/parts', exist_ok=True)
    json.dump(g3lib.to_jsonable(out), open(f'{OUT}/parts/g0-reads.json', 'w'), indent=1, sort_keys=True)
    print(json.dumps(g3lib.to_jsonable(out), indent=1, sort_keys=True)[:1400])
    print(f'\n[wrote] {OUT}/parts/g0-reads.json')


if __name__ == '__main__':
    main()
