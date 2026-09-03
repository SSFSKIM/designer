#!/usr/bin/env python3
"""W13 by-eye sheet (contract X5, `docs/doperpowers/specs/2026-09-03-w13-body-depth-ramp.md`).

The W14 sheet's five-panel layout (native | the bed before | the candidate | two signed
differences) with the W12 sheet's tight crop, because the ramp's subject is the band just inside
the contour and not the exterior: an 8 CSS px margin, the checkerboard ladder and `photo` at the
middle span, and no solids (a flat backdrop has nothing for a mix to reveal).

What follows is the W14 sheet's own header, kept for the panel semantics.


Derived from W12's sheet (`results/2026-09-03-w12-lens/sheets/make-sheet.py`) with two changes
for a wave whose subject is OUTSIDE the contour. The crop margin is 48 CSS px instead of 8, so
the shadow's whole falloff (offset 7.95, sigma 15.55, reaching about 40 px below the surface) is
in the frame, clamped to the canvas where the large spans run out of it. And each row has five
panels rather than three: the native fixture, the W12 close bed (the canonical capture, before
this wave), the candidate (the confirmation capture), then two signed difference panels — the
W12 close against native and the candidate against native — so the eye reads what the wave
changed and not only where it landed. Differences are (vitrea - native) in LINEAR luminance,
mid-grey at zero, +/-0.25 full scale, written straight to 8-bit so a code value is a linear
difference; they are diagnostics and not renders.

    cd packages/calibration && python3 results/2026-09-03-w14-shadow/sheets/make-sheet.py \
        --gate g1 --scale 1 --candidate <scratch captures dir> [--renderer webgpu]

Reads the fixtures under apps/reference-apple/fixtures and the W12 close from
packages/calibration/web-captures; writes `<gate>-<scale>x.png` beside this script.
"""
import argparse
import os
import sys

import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..', '..', '..'))
FIXTURES = os.path.join(ROOT, 'apps', 'reference-apple', 'fixtures')
CANONICAL = os.path.join(ROOT, 'packages', 'calibration', 'web-captures')

COMPONENTS = {
    'rrect-sm': (64, 32), 'capsule-button': (120, 44), 'rrect-md': (160, 96),
    'rrect-ml': (224, 128), 'rrect-lg': (280, 160),
}
# The checkerboard ladder the wave was fitted on; the light-solid capsule (2.29x at the W12
# close, S3); the two dark-solid cells (S1's miss, and the un-keyed thick law's 50% cost); photo
# and hc-text at the middle span (the other backdrops the lift is read over).
ROWS = [
    ('checkerboard__rrect-sm__rest', 'rrect-sm'),
    ('checkerboard__capsule-button__rest', 'capsule-button'),
    ('checkerboard__rrect-md__rest', 'rrect-md'),
    ('checkerboard__rrect-ml__rest', 'rrect-ml'),
    ('checkerboard__rrect-lg__rest', 'rrect-lg'),
    ('photo__rrect-md__rest', 'rrect-md'),
]
MARGIN = 8
DIFF_FULL_SCALE = 0.25
GAP = 6


def srgb_to_linear(c):
    return np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)


def luma_linear(rgb8):
    c = srgb_to_linear(rgb8.astype(np.float64) / 255.0)
    return 0.2126 * c[..., 0] + 0.7152 * c[..., 1] + 0.0722 * c[..., 2]


def box(component, scale, margin=MARGIN):
    w, h = COMPONENTS[component]
    x0, y0 = max(0, 160 - w / 2 - margin), max(0, 100 - h / 2 - margin)
    x1, y1 = min(320, 160 + w / 2 + margin), min(200, 100 + h / 2 + margin)
    return tuple(int(round(v * scale)) for v in (x0, y0, x1, y1))


def diff_panel(native8, web8):
    d = (luma_linear(web8) - luma_linear(native8)) / DIFF_FULL_SCALE
    g = np.clip(128 + d * 127, 0, 255).astype(np.uint8)
    return Image.fromarray(np.stack([g, g, g], axis=-1), 'RGB')


def zoomed(img, z):
    return img.resize((img.width * z, img.height * z), Image.NEAREST)


def load(path):
    if not os.path.exists(path):
        sys.exit(f'missing: {path}')
    return Image.open(path).convert('RGB')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--gate', required=True)
    ap.add_argument('--scale', type=int, choices=(1, 2), default=1)
    ap.add_argument('--profile', default=None)
    # The `W12 close` column reads the canonical captures, which the LANDING rebuild
    # overwrites with the candidate itself. `--before` names where that column comes
    # from, so a landing sheet can point it at the pre-rebuild copy kept in scratch;
    # unset, it is the canonical directory the dry-run sheets read.
    ap.add_argument('--before', default=CANONICAL, help='the W12-close captures dir')
    ap.add_argument('--candidate', required=True, help='scratch captures dir (VITREA_WEB_CAPTURES)')
    ap.add_argument('--renderer', default='webgpu')
    args = ap.parse_args()
    profile = args.profile or f'apple-macos-26.5-{args.scale}x-light-standard'
    scale = args.scale
    zoom = 3 if scale == 1 else 2  # the same screen size per CSS px at both scales

    rows = []
    label_h = 18
    for scene, component in ROWS:
        native = load(os.path.join(FIXTURES, profile, f'{scene}.png'))
        before = load(os.path.join(args.before, profile, scene, f'{scene}__{args.renderer}.png'))
        after = load(os.path.join(args.candidate, profile, scene, f'{scene}__{args.renderer}.png'))
        for img, name in ((before, 'W12 close'), (after, 'candidate')):
            if img.size != native.size:
                sys.exit(f'{scene}: fixture {native.size} and {name} {img.size} differ in size')
        b = box(component, scale)
        n, w0, w1 = native.crop(b), before.crop(b), after.crop(b)
        d0 = diff_panel(np.asarray(n), np.asarray(w0))
        d1 = diff_panel(np.asarray(n), np.asarray(w1))
        panels = [zoomed(p, zoom) for p in (n, w0, w1, d0, d1)]
        rows.append((f'{scene}  ({profile}, {args.renderer})', panels))

    width = max(sum(p.width for p in panels) + GAP * (len(panels) - 1) for _, panels in rows) + 2 * GAP
    banner_h = 40
    height = banner_h + sum(max(p.height for p in panels) + label_h + GAP for _, panels in rows) + GAP
    sheet = Image.new('RGB', (width, height), (24, 24, 24))
    draw = ImageDraw.Draw(sheet)
    try:
        from PIL import ImageFont
        font = ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc', max(18, width // 110))
    except Exception:
        font = None
    banner = ('1 Apple native   2 vitrea W14 bed (before the ramp)   3 vitrea W13 candidate   '
              '4 diff (W14 bed - native)   5 diff (candidate - native)   -- 4 and 5 are diagnostics, NOT renders')
    draw.text((GAP, GAP), banner, fill=(230, 230, 230), font=font)
    y = banner_h
    for label, panels in rows:
        draw.text((GAP, y), label, fill=(230, 230, 230))
        y += label_h
        x = GAP
        for p in panels:
            sheet.paste(p, (x, y))
            x += p.width + GAP
        y += max(p.height for p in panels) + GAP
    out = os.path.join(HERE, f'{args.gate}-{scale}x.png')
    sheet.save(out)
    print(out, sheet.size)


if __name__ == '__main__':
    main()
