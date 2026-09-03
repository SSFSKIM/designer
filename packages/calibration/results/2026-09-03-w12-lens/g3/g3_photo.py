"""G3 reading 7: the photo family as the null check, at both scales (5.41 3's method).

A law fitted on checkerboards rides structured content by construction; the broadband `photo` plate
is close to invariant under a change of blur width at these amplitudes, so it can only confirm a law
or catch it making things worse. The candidates are laid over the photo plate with only (a, t) free
per cell, against the landed model (F0) at the same scale.
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np

from g3lib import *  # noqa: F401,F403

PHOTO_COMPS = ['rrect-sm', 'rrect-md', 'rrect-lg']
F = json.load(open(f'{OUT}/parts/forms.json'))['forms']
P_F1 = F['F1-gpu-sharp-css_k-scale-term']['params']
P_F2 = F['F2-quarter-buffer-scale-term']['params']
P_F1CSS = F['F1-css-sharp-css_k-shared']['params']


def k_of(span, k0, span_max, dk, scale):
    k = k0 + (1 - k0) * smoothstep(32, span_max, span) + (dk if scale == 2 else 0.0)
    return min(max(k, 0.0), 1.0)


def col_f0(comp, scale, P, key, css=False):
    k = k_of(SPAN[comp], 0.4, 256.0, 0.0, scale)
    f = structure_css if css else structure_gpu
    return f(P, key, scale, 1.25, 10.0, k)


def col_f1(comp, scale, P, key, p=None, css=False):
    p = p or P_F1
    k = k_of(SPAN[comp], p['k0'], p['span_max'], p['dk'], scale)
    f = structure_css if css else structure_gpu
    return f(P, key, scale, p['sigma_sharp'], p['sigma_heavy_dev'] / scale, k)


def col_f2(comp, scale, P, key):
    w_edge = min(P_F2['w_edge'] + (P_F2['dw'] if scale == 2 else 0.0), 1.0)
    return structure_f2(P, key, comp, scale, P_F2['c'], w_edge, P_F2['end_frac'], P_F2['gamma'])


out = dict(params=dict(F0=dict(blurSigma=1.25, heavy=10.0, k0=0.4, span_max=256.0),
                       F1=P_F1, F1_css=P_F1CSS, F2=P_F2), cells={}, totals={})
tot = {}
for scale in SCALES:
    P = plate('photo', scale)
    for comp in PHOTO_COMPS:
        Y = capture(f'photo__{comp}__rest', scale)
        m = box_mask(comp, scale)
        rec = {}
        for name, col in (('F0-gpu', col_f0(comp, scale, P, 'photo')),
                          ('F1-gpu', col_f1(comp, scale, P, 'photo')),
                          ('F2-gpu', col_f2(comp, scale, P, 'photo')),
                          ('F0-css', col_f0(comp, scale, P, 'photo', css=True)),
                          ('F1-css', col_f1(comp, scale, P, 'photo', P_F1CSS, css=True))):
            coef, rms, r2 = lstsq_cols(Y[m], [col[m]])
            rec[name] = dict(a=float(coef[0]), t=float(coef[1]), rms=rms, r2=r2)
            tot.setdefault(f'{name}@{scale}x', [0.0, 0])
            tot[f'{name}@{scale}x'][0] += rms ** 2 * int(m.sum())
            tot[f'{name}@{scale}x'][1] += int(m.sum())
        out['cells'][f'{comp}@{scale}x'] = rec
        print(f'{scale}x {comp:10s} ' + ' | '.join(f'{k} {v["rms"]:.4f}' for k, v in rec.items()))
out['totals'] = {k: float(np.sqrt(v[0] / v[1])) for k, v in tot.items()}
print('\n== overall photo RMS')
for k, v in out['totals'].items():
    print(f'   {k:12s} {v:.4f}')

write_part('photo', out)
