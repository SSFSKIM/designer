"""W13 G0, contract X6: the band-windowed SSIM rows, on the W12 close bed, as the baseline.

`ssimBand` and `ssimInterior` split the cell's silhouette at a fixed depth of 24 CSS px from
the contour — past where the landed lens's displacement reaches zero on every span (D < 1 px
from u ≈ 17–18, claims §5.49 §2) — so the band window is where the eye looks and the
interior window is the body alone. The split is fixed rather than per span (W13 Decision Log
1, question 3).

The SSIM here is `w11lib.ssim_map`, the replica of the compare's own
`packages/calibration/src/metrics/perceptual.ts` (11 × 11 Gaussian σ 1.5, valid windows,
encoded luma in 0…255) that W11 pinned against it; the map is computed on the whole canvas
and averaged inside each window, so these numbers are the same statistic the compare
reports, restricted to a mask. They are recorded here as the baseline the wave's later
gates move against — no bound is adopted at G0.
"""
import numpy as np

import w13lib as L

SCENES = [('checkerboard', c) for c in
          ('rrect-sm', 'capsule-button', 'rrect-md', 'rrect-ml', 'rrect-lg')]
SCENES += [('photo', 'rrect-md'), ('photo', 'rrect-lg'), ('hc-text', 'rrect-md')]
SPLIT = 24.0

out = {}
print('X6 baseline — SSIM inside the silhouette, split at 24 CSS px from the contour\n')
print(f'   {"cell":<34} {"whole":>8} {"band":>8} {"interior":>9} {"band px":>9} {"int px":>8}')
for scale in (1, 2):
    for backdrop, comp in SCENES:
        scene = f'{backdrop}__{comp}__rest'
        profile = f'apple-macos-26.5-{scale}x-light-standard'
        try:
            N = L.w11lib.load_rgb(f'{L.FIX}/{profile}/{scene}.png')
            V = L.w11lib.load_rgb(f'{L.WEB}/{profile}/{scene}/{scene}__webgpu.png')
        except FileNotFoundError:
            continue
        m = L.w11lib.ssim_map(L.w11lib.luma_enc(N), L.w11lib.luma_enc(V))
        r = 5  # the map is 'valid': it starts r device px in from every edge
        d = L.depth_map(comp, scale)[r:-r, r:-r]
        band = (d > 0) & (d < SPLIT)
        interior = d >= SPLIT
        sil = d > 0
        rec = dict(ssim_whole_silhouette=float(m[sil].mean()),
                   ssim_band=float(m[band].mean()) if band.any() else float('nan'),
                   ssim_interior=float(m[interior].mean()) if interior.any() else float('nan'),
                   n_band=int(band.sum()), n_interior=int(interior.sum()))
        out[f'{scene}@{scale}x'] = rec
        print(f'   {scene}@{scale}x{"":<3} {rec["ssim_whole_silhouette"]:>8.4f} '
              f'{rec["ssim_band"]:>8.4f} {rec["ssim_interior"]:>9.4f} '
              f'{rec["n_band"]:>9d} {rec["n_interior"]:>8d}')

L.write_part('g0-band-rows', out)
