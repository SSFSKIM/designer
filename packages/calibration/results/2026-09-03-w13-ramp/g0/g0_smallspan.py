"""W13 G0, step 4: the heavy width on the small spans.

§5.55 §1 fitted one base width — σ 9 device px — on spans ≥ 96 only. The layer tree's own
`inputBlurRadius` law (claims §5.50 §2) floors at 4/3 buffer px on every span below 48, and
one buffer pixel is four DEVICE px, so the reference's own prediction for `rrect-sm` (32)
and `capsule-button` (44) is **5.33 device px at both scales** — 5.3 CSS px at 1x and 2.65
at 2x — against vitrea's fixed 10 CSS px at every span and scale.

Read here with g3lib's two-component kernel fit pooled over the pitches at once
(`fit_two_joint`, the estimator §5.55 §1 used), on the deep interior box, with σ_heavy swept
over 4 … 12 device px. The three frequency-settled 2x `rrect-sm` cells (§5.53 —
`checkerboard-8`, `checkerboard-64`, `checkerboard-lc16`) are excluded from the primary fit
and the fit is repeated with them so the difference is on the record.
"""
import numpy as np

import w13lib as L

g3 = L.g3lib
SETTLED_2X = {'checkerboard-8__rrect-sm', 'checkerboard-64__rrect-sm',
              'checkerboard-lc16__rrect-sm'}
PITCHES = ['checkerboard-8', 'checkerboard', 'checkerboard-32', 'checkerboard-64']
SIG_SHARP = [0.0, 0.25, 0.5, 0.75, 1.0, 1.25, 1.5, 2.0, 2.5, 3.0]


def sweep(comp, scale, pitches):
    """σ_heavy over 4 … 12 device px with σ_sharp free; returns the curve and the best."""
    Ys, Ps, ms = [], [], []
    for b in pitches:
        Ys.append(g3.capture(f'{b}__{comp}__rest', scale))
        Ps.append((b, g3.plate(b, scale)))
        ms.append(g3.box_mask(comp, scale))
    curve = []
    for dev in (4, 5, 5.33, 6, 7, 8, 9, 10, 11, 12):
        css = dev / scale
        r = g3.fit_two_joint(Ys, Ps, ms, scale, sig_sharp=SIG_SHARP, sig_heavy=[css],
                             min_gap=0.5)
        curve.append(dict(sigma_heavy_device=dev, sigma_heavy_css=css,
                          sigma_sharp_css=r['sigma_sharp'], rms=r['rms'], r2=r['r2'],
                          share=r['share'], t=r['t']))
    best = min(curve, key=lambda z: z['rms'])
    return curve, best


out = {}
print('the heavy width on the small spans, σ_heavy swept in device px '
      '(g3lib fit_two_joint over the pitches, the deep interior box)\n')
print(f'   {"cell":<24} {"best σ_h dev":>12} {"σ_sharp css":>12} {"heavy share":>12} '
      f'{"rms":>9}   radius law 5.33, large spans 9.0')
for scale in (1, 2):
    for comp in ('rrect-sm', 'capsule-button', 'rrect-md', 'rrect-ml', 'rrect-lg'):
        variants = {'all pitches': PITCHES}
        if scale == 2 and comp == 'rrect-sm':
            variants['settled excluded'] = [b for b in PITCHES
                                            if f'{b}__{comp}' not in SETTLED_2X]
        for vname, pitches in variants.items():
            curve, best = sweep(comp, scale, pitches)
            key = f'{comp}@{scale}x|{vname}'
            out[key] = dict(curve=curve, best=best, pitches=pitches)
            print(f'   {comp}@{scale}x {vname:<14} {best["sigma_heavy_device"]:>12.2f} '
                  f'{best["sigma_sharp_css"]:>12.2f} {best["share"]:>12.3f} '
                  f'{best["rms"]:>9.5f}')
            near = [c for c in curve if c['rms'] <= best['rms'] * 1.02]
            print(f'      within 2% of the best: σ_heavy {min(c["sigma_heavy_device"] for c in near):.2f}'
                  f'–{max(c["sigma_heavy_device"] for c in near):.2f} device px; '
                  f'rms at 5.33 {[c for c in curve if c["sigma_heavy_device"] == 5.33][0]["rms"]:.5f}, '
                  f'at 9.0 {[c for c in curve if c["sigma_heavy_device"] == 9][0]["rms"]:.5f}')

L.write_part('g0-small-spans', out)
