"""The shipped-body replica against the canonical shipped captures (rehearsal proof).

`body.shipped_body` (memo B's float64 replica, lensed) against the WebGPU capture the matrix
names, per depth band, codes rms, on a sample covering every endpoint, both scales, every
component kind and each backdrop family. Beyond 2 CSS px of the contour the capture holds only
the body (the rim, highlight and inner shadow live at the edge), so these rows are the replica's
error; the swap adds the difference of two replica bodies and keeps the rest of the capture.

    python3.12 -B replica_check.py > replica-check.txt
"""
import sys, time
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parent))
import body as B
from swap import rgb, CANONICAL
CELLS = [('light', 'rest', 2, 'photo__capsule-button__rest'), ('light', 'rest', 1, 'checkerboard__rrect-md__rest'),
         ('light', 'rest', 2, 'checkerboard-8__rrect-lg__rest'), ('light', 'rest', 1, 'hc-text-7__rrect-md__rest'),
         ('light', 'inactive', 2, 'checkerboard__capsule-button__inactive'), ('light', 'inactive', 1, 'photo__rrect-md__inactive'),
         ('light', 'inactive', 2, 'photo__toolbar-group__inactive'), ('light', 'inactive', 2, 'impulse__rrect-ml__inactive'),
         ('dark', 'rest', 2, 'photo__rrect-md__rest'), ('dark', 'rest', 1, 'checkerboard__capsule-button__rest'),
         ('dark', 'rest', 2, 'checkerboard-64__rrect-lg__rest'), ('dark', 'inactive', 1, 'checkerboard__rrect-md__inactive'),
         ('dark', 'inactive', 2, 'photo__capsule-button__inactive'), ('dark', 'inactive', 2, 'checkerboard-8__rrect-lg__inactive')]
BANDS = [('2-8', 2, 8), ('8-18', 8, 18), ('18+', 18, 1e9)]
print(__doc__.split('\n\n')[0])
print(f"{'endpoint':14s} {'cell':44s} " + ' '.join(f'{b[0]:>7s}' for b in BANDS) + '   (rms codes; unlensed 2-8 in brackets)')
for scheme, pose, s, scene in CELLS:
    bg, comp = scene.split('__')[:2]
    ep = B.endpoint_of(scheme, pose)
    prof = f'apple-macos-27.0-{s}x-{scheme}-standard-glass0.5'
    web = rgb(CANONICAL / prof / scene / f'{scene}__webgpu.png')
    dep = -B.field(comp, s).d
    lensed = B.enc(B.shipped_body(ep, s, bg, comp, True)) * 255 - web
    flat = B.enc(B.shipped_body(ep, s, bg, comp, False)) * 255 - web
    cols = []
    for _, lo, hi in BANDS:
        m = (dep > lo) & (dep <= hi)
        cols.append(f'{np.sqrt((lensed[m] ** 2).mean()):7.2f}' if m.any() else '      -')
    m = (dep > 2) & (dep <= 8)
    print(f'{ep:14s} {s}x {scene:41s} ' + ' '.join(cols) + f'   [{np.sqrt((flat[m] ** 2).mean()):.1f}]')
