"""G3 reading 8b: the canonical SSIM dry run for F1 and F1' (claims 5.41 4's method).

vitrea's own capture with its deep body — the 5.41 interior box, rim band and outside untouched —
replaced by the candidate law evaluated at the *reference* cell's own level and transmission, hue
kept by scaling the capture's RGB by the luminance ratio; then whole-crop `ssimMean` against the
native fixture with the numpy replica of the compare's metric (`../g1/w11lib.py`, the replica 5.38
proved reproduces every checkerboard row of `results/matrix.json` to four decimals).

Baselines are the captures of the material now on main: the webgpu tier from the omega-0.8 round
(`web-captures-g2b/`) and the CSS tier from the G2 landing (`web-captures-g2/`, unchanged since).
The `before` column is checked against the measured rows of the scratch matrices those captures were
scored into, which is the instrument check for this section.

The CSS tier's law is derived from the same constants by the K5 contract: one blur of
sigma_css = sigma_sharp x (1 + (gain_eff - 1) x k'), gain_eff = sigma_heavy,css / sigma_sharp, which
is identically sigma_sharp x (1 - k') + sigma_heavy,css x k'.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, f'{HERE}/../g1')
import numpy as np

from g3lib import *  # noqa: F401,F403
from w11lib import ssim_mean, lin_to_srgb  # the compare's SSIM replica

SCRATCH = '/Users/new/.claude/jobs/5c70e47f/tmp/w12'
CAP = {'webgpu': f'{SCRATCH}/web-captures-g2b', 'css': f'{SCRATCH}/web-captures-g2'}
MATRIX = {'webgpu': f'{SCRATCH}/matrix-g2b.json', 'css': f'{SCRATCH}/matrix-g2.json'}
PROF = {1: 'apple-macos-26.5-1x-light-standard', 2: 'apple-macos-26.5-2x-light-standard'}
TIER = {'webgpu': 'texture', 'css': 'dom'}
BOUND = {(1, 'texture'): 0.88, (1, 'dom'): 0.90, (2, 'texture'): 0.93, (2, 'dom'): 0.92}
FLOOR = {  # packages/calibration/test/adopted-thresholds.test.ts, UNMET_ROWS
    ('dom', 'rrect-md', 1): 0.8952, ('dom', 'rrect-md', 2): 0.9159,
    ('dom', 'rrect-ml', 1): 0.8470, ('dom', 'rrect-ml', 2): 0.8754,
    ('dom', 'rrect-lg', 1): 0.8361, ('dom', 'rrect-lg', 2): 0.8686,
    ('texture', 'rrect-ml', 2): 0.9013, ('texture', 'rrect-lg', 2): 0.9002,
}
STOP = 0.002  # W12's stop: no 1x row below its landing value by more than this


def native(comp, scale):
    return load_rgb(f'{ROOT}/apps/reference-apple/fixtures/{PROF[scale]}/checkerboard__{comp}__rest.png')


def web(comp, scale, side):
    s = f'checkerboard__{comp}__rest'
    return load_rgb(f'{CAP[side]}/{PROF[scale]}/{s}/{s}__{side}.png')


def measured_rows(side):
    M = json.load(open(MATRIX[side]))
    rows = {}
    for c in M['cells']:
        k = c['key']
        if k['web']['renderer'] != side or k['profileKey'] not in PROF.values():
            continue
        if not (k['sceneId'].startswith('checkerboard__') and k['sceneId'].endswith('__rest')):
            continue
        scale = 1 if '1x' in k['profileKey'] else 2
        comp = k['sceneId'].split('__')[1]
        prev = rows.get((comp, scale))
        if prev is None or c['capturedAt'] > prev[1]:
            rows[(comp, scale)] = (c['perceptual']['ssimMean']['value'], c['capturedAt'])
    return rows


# ---- the candidate laws, as (sigma_sharp, sigma_heavy, k) per (comp, scale)
V = json.load(open(f'{OUT}/parts/variants.json'))
F = json.load(open(f'{OUT}/parts/forms.json'))['forms']
P_F1 = F['F1-gpu-sharp-css_k-scale-term']['params']
P_F1P = V['variants']['F1p-b_sharp-1.25dev_heavy-10dev']['params']


def smooth_k(span, k0, span_max, dk, scale):
    return min(max(k0 + (1 - k0) * smoothstep(32, span_max, span) + dk * (scale - 1), 0.0), 1.0)


def law_params(name, comp, scale):
    if name == 'F0':
        return 1.25, 10.0, smooth_k(SPAN[comp], 0.4, 256.0, 0.0, scale)
    if name == 'F1':
        return (P_F1['sigma_sharp'], P_F1['sigma_heavy_dev'] / scale,
                smooth_k(SPAN[comp], P_F1['k0'], P_F1['span_max'], P_F1['dk'], scale))
    if name == "F1'":
        sb = 1.25 if scale == 1 else P_F1P['sb2']
        sh = 10.0 if scale == 1 else P_F1P['sh2']
        return sb, sh, smooth_k(SPAN[comp], 0.4, 256.0, P_F1P['dk'], scale)
    raise ValueError(name)


def structure(name, comp, scale, side):
    lo, hi, k = law_params(name, comp, scale)
    P = plate('checkerboard', scale)
    if side == 'css':
        return structure_css(P, 'checkerboard', scale, lo, hi, k)
    return structure_gpu(P, 'checkerboard', scale, lo, hi, k)


out = dict(bounds={f'{s}x-{t}': v for (s, t), v in BOUND.items()}, stop=STOP,
           laws={n: {f'{c}@{s}x': dict(zip(('sigma_sharp', 'sigma_heavy', 'k'),
                                           law_params(n, c, s)))
                     for s in SCALES for c in COMPS} for n in ('F0', 'F1', "F1'")},
           rows={}, instrument_check={})

for side in ('webgpu', 'css'):
    meas = measured_rows(side)
    for scale in SCALES:
        for comp in COMPS:
            nat = native(comp, scale)
            cap = web(comp, scale, side)
            before = ssim_mean(nat, cap)[0]
            m = box_mask(comp, scale)
            Yn = luma_lin(nat)
            Yw = luma_lin(cap)
            rec = dict(before=before, tier=TIER[side], bound=BOUND[(scale, TIER[side])],
                       floor=FLOOR.get((TIER[side], comp, scale)))
            mrow = meas.get((comp, scale))
            if mrow:
                rec['matrix_measured'] = mrow[0]
                rec['matrix_captured_at'] = mrow[1]
                out['instrument_check'][f'{side}|{comp}|{scale}x'] = dict(
                    replica=before, matrix=mrow[0], delta=abs(before - mrow[0]))
            for name in ('F0', 'F1', "F1'"):
                X = structure(name, comp, scale, side)
                coef, rms, r2 = lstsq_cols(Yn[m], [X[m]])
                law = coef[0] + coef[1] * X
                w2 = cap.copy()
                ratio = np.clip(law[m] / np.maximum(Yw[m], 1e-4), 0, 10)
                w2[m] = lin_to_srgb(srgb_to_lin(cap[m]) * ratio[:, None])
                rec[name] = dict(after=ssim_mean(nat, w2)[0], body_fit_rms=rms,
                                 a=float(coef[0]), t=float(coef[1]))
            out['rows'][f'{side}|{comp}|{scale}x'] = rec
            print(f'{scale}x {TIER[side]:7s} {comp:15s} [{rec["bound"]:.2f}] before {before:.4f}'
                  + (f' (matrix {mrow[0]:.4f})' if mrow else '')
                  + ''.join(f' | {n} {rec[n]["after"]:.4f}' for n in ('F0', 'F1', "F1'")), flush=True)

print('\n== instrument check: the SSIM replica against the scratch matrices\' own rows')
worst = max(out['instrument_check'].values(), key=lambda v: v['delta'])
print(f'   largest |replica − matrix| over {len(out["instrument_check"])} rows: {worst["delta"]:.5f}')

print('\n== the stop: 1x rows moving down by more than 0.002')
flagged = []
for key, r in out['rows'].items():
    if not key.endswith('1x'):
        continue
    for n in ('F1', "F1'"):
        d = r[n]['after'] - r['before']
        if d < -STOP:
            flagged.append((key, n, r['before'], r[n]['after'], d))
out['stop_flags'] = [dict(row=k, law=n, before=b, after=a, delta=d) for k, n, b, a, d in flagged]
if flagged:
    for k, n, b, a, d in flagged:
        print(f'   FLAG {k:22s} {n:4s} {b:.4f} → {a:.4f} ({d:+.4f})')
else:
    print('   none')

write_part('dryrun', out)
