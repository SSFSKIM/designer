"""W16 G0 (a) and (c) — the Chromium two-layer body scored against the native probe bed.

The protocol is claims 5.42 5's, unchanged: the native probe cell is regressed on
ONE structure column with a level `a` and a transmission `t` free per span and
shared across the pitches 8 / 16 / 32 / 64, over 5.41's inset interior box, and
the residual's RMS in linear luminance is the reading. The only change is what
supplies the structure column: 5.42 5 supplied a MODEL (an analytic Gaussian mix
of the plate), and this supplies a CHROMIUM CAPTURE of a page that hand-builds the
same law out of two `backdrop-filter` layers. Reproducing 5.42 5's model columns
first is contract X4 for this reading: an instrument that cannot reproduce the
published number has no standing to report a new one.
"""
import json
import os
import sys

import numpy as np

G3 = '/Users/new/Developer/GitHub/designer/packages/calibration/results/2026-09-03-w12-lens/g3'
if G3 not in sys.path:
    sys.path.insert(0, G3)
import g3lib  # noqa: E402

CAP = os.environ.get('W16_CAP', '/Users/new/.claude/jobs/5c70e47f/tmp/w16/g0/cap')
OUT = os.path.dirname(os.path.abspath(__file__))
LAW = json.load(open(f'{OUT}/pages/law.json'))
COMPS = g3lib.COMPS
SPAN = g3lib.SPAN
P4 = g3lib.PITCHES4


def web(cell, scale):
    Y = g3lib.luma_lin(g3lib.load_rgb(f'{CAP}/{cell}.png'))
    assert Y.shape == (200 * scale, 320 * scale), (cell, Y.shape)
    return Y


def fit(comp, scale, columns):
    """RMS of the native cell against one structure column, (a, t) free, pitches pooled."""
    m = g3lib.box_mask(comp, scale)
    y = np.concatenate([g3lib.capture(f'{b}__{comp}__rest', scale)[m] for b in P4])
    x = np.concatenate([columns[b][m] for b in P4])
    coef, rms, r2 = g3lib.lstsq_cols(y, [x])
    return dict(a=float(coef[0]), t=float(coef[1]), rms=float(rms), r2=float(r2), n=int(len(y)))


def model_columns(comp, scale, kind):
    """5.42 5's own model columns, rebuilt here so the pipeline is checked on them."""
    span = SPAN[comp]
    L = LAW['spans'][f'{span}@{scale}x']
    out = {}
    for b in P4:
        P = g3lib.plate(b, scale)
        if kind == 'gpu-law':
            # the widths the GPU tier draws at THIS ratio: the sharp sigma is a
            # device-pixel quantity, so in CSS px it is blurSigma / dpr (W15 G1)
            out[b] = g3lib.structure_gpu(P, b, scale, L['sharpCss'], L['heavyCss'], L['kDeep'])
        elif kind == 'css-today':
            out[b] = g3lib.G(P, b, L['cssTierSigmaToday'], scale)
    return out


def capture_columns(prefix, comp, scale):
    return {b: web(f'{prefix}-{comp}-{b}-{scale}x', scale) for b in P4}


def best_single_sigma(comp, scale, columns):
    """The single Gaussian that best explains a capture — the tier's own ceiling."""
    m = g3lib.box_mask(comp, scale)
    y = np.concatenate([columns[b][m] for b in P4])
    best = None
    for s in np.arange(0.25, 12.01, 0.05):
        x = np.concatenate([g3lib.G(g3lib.plate(b, scale), b, float(s), scale)[m] for b in P4])
        coef, rms, r2 = g3lib.lstsq_cols(y, [x])
        if best is None or rms < best[1]:
            best = (float(s), float(rms))
    return best


SIGMA_542 = {'rrect-sm': 4.75, 'capsule-button': 4.79, 'rrect-md': 5.79,
             'rrect-ml': 6.82, 'rrect-lg': 7.93}
"""The single sigma per span 5.42 5 measured its own CSS column at (the W11c
projection). Today's tier draws a different number, so reproducing 5.42 5's
published RMS needs 5.42 5's own sigma — which is the point of the check."""


def main():
    rows = {}
    for scale in (1, 2):
        for comp in COMPS:
            span = SPAN[comp]
            L = LAW['spans'][f'{span}@{scale}x']
            rec = dict(comp=comp, span=span, scale=scale, kDeep=L['kDeep'], areaMix=L['areaMix'],
                       gain=L['gain'], sharpCss=L['sharpCss'], heavyCss=L['heavyCss'])
            rec['model_gpu_law'] = fit(comp, scale, model_columns(comp, scale, 'gpu-law'))
            rec['model_css_today'] = fit(comp, scale, model_columns(comp, scale, 'css-today'))
            if scale == 1:
                rec['model_css_542'] = fit(comp, 1, {
                    b: g3lib.G(g3lib.plate(b, 1), b, SIGMA_542[comp], 1) for b in P4})
            for prefix, key in (('single', 'cap_css_today'), ('twoK', 'cap_two_kdeep'),
                                ('twoA', 'cap_two_area'), ('ramp-raster', 'cap_ramp_raster'),
                                ('svgsRGB', 'cap_ref_srgb'), ('svglinearRGB', 'cap_ref_linear')):
                rec[key] = fit(comp, scale, capture_columns(prefix, comp, scale))
            # the moment-matched single sigma of the two layers, and the capture's own
            k = L['areaMix']
            rec['moment_sigma'] = float(np.sqrt((1 - k) * L['sharpCss'] ** 2 + k * L['heavyCss'] ** 2))
            s, r = best_single_sigma(comp, scale, capture_columns('twoA', comp, scale))
            rec['capture_best_single'] = dict(sigma=s, rms=r)
            s, r = best_single_sigma(comp, scale, capture_columns('ramp-raster', comp, scale))
            rec['capture_ramp_best_single'] = dict(sigma=s, rms=r)
            rows[f'{comp}@{scale}x'] = rec
    json.dump(g3lib.to_jsonable(rows), open(f'{OUT}/parts/g0-body.json', 'w'), indent=1, sort_keys=True)

    hdr = ('| cell | span | model GPU law | model CSS σ today | capture: one blur | '
           'capture: two flat (kDeep) | capture: two flat (area) | capture: two + raster ramp | '
           'capture: reference filter, sRGB | capture: reference filter, linearRGB |')
    for scale in (1, 2):
        print(f'\n### RMS against the native probe bed, dpr {scale}\n')
        print(hdr)
        print('| --- ' * 10 + '|')
        for comp in COMPS:
            r = rows[f'{comp}@{scale}x']
            print(f'| `{comp}` | {r["span"]} | {r["model_gpu_law"]["rms"]:.4f} | '
                  f'{r["model_css_today"]["rms"]:.4f} | {r["cap_css_today"]["rms"]:.4f} | '
                  f'{r["cap_two_kdeep"]["rms"]:.4f} | {r["cap_two_area"]["rms"]:.4f} | '
                  f'{r["cap_ramp_raster"]["rms"]:.4f} | {r["cap_ref_srgb"]["rms"]:.4f} | '
                  f'{r["cap_ref_linear"]["rms"]:.4f} |')
    print('\n### X4 — the published columns of claims 5.42 5, reproduced by this pipeline\n')
    print('| cell | GPU law, published | here | CSS sigma today, published | here (at 5.42 5 sigma) |')
    print('| --- | --- | --- | --- | --- |')
    PUB = {'rrect-sm': (0.0280, 0.0708), 'capsule-button': (0.0281, 0.0784),
           'rrect-md': (0.0138, 0.0615), 'rrect-ml': (0.0148, 0.0491),
           'rrect-lg': (0.0174, 0.0376)}
    for comp in COMPS:
        r = rows[f'{comp}@1x']
        print(f'| `{comp}` | {PUB[comp][0]:.4f} | {r["model_gpu_law"]["rms"]:.4f} | '
              f'{PUB[comp][1]:.4f} | {r["model_css_542"]["rms"]:.4f} |')
    print('\n### The second scale: the two layers projected onto one σ (CSS px)\n')
    print('| cell | moment-matched σ | the capture\'s own best single σ (RMS) | ramp capture\'s best single σ |')
    print('| --- | --- | --- | --- |')
    for comp in COMPS:
        r = rows[f'{comp}@2x']
        print(f'| `{comp}` | {r["moment_sigma"]:.3f} | {r["capture_best_single"]["sigma"]:.2f} '
              f'({r["capture_best_single"]["rms"]:.4f}) | {r["capture_ramp_best_single"]["sigma"]:.2f} |')


if __name__ == '__main__':
    main()
