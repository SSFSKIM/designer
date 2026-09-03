#!/usr/bin/env python3
"""W12 by-eye sheet (contract X5, `docs/doperpowers/specs/2026-09-03-w12-lens-band-structure.md`).

One PNG per gate and scale: native fixture | vitrea webgpu capture | signed luma difference, 3x
nearest-neighbour, one row per cell, and a last row of 10x corner crops of `rrect-md` (native |
vitrea). The difference panel is (vitrea - native) in LINEAR luminance (Rec.709 of the sRGB-decoded
channels), mid-grey at zero, +/-0.25 full scale, written straight to 8-bit without a transfer curve
so that a code value is a linear difference. Each cell is cropped to its component box plus an
8 CSS px margin so the sheet stays readable.

    cd packages/calibration && python3 results/2026-09-03-w12-lens/sheets/make-sheet.py \
        --gate g1 --scale 2 [--captures web-captures] [--profile apple-macos-26.5-2x-light-standard]

Needs PIL and numpy only. Reads the fixtures under apps/reference-apple/fixtures and the captures
under packages/calibration/web-captures by default; `--captures` points it at a scratch capture
directory for a dry run. Writes `<gate>-<scale>x.png` beside this script.
"""
import argparse
import os
import sys

import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..', '..', '..'))
FIXTURES = os.path.join(ROOT, 'apps', 'reference-apple', 'fixtures')

# component boxes in CSS px on the 320x200 canvas: (w, h), centred
COMPONENTS = {
    'rrect-sm': (64, 32), 'capsule-button': (120, 44), 'rrect-md': (160, 96),
    'rrect-ml': (224, 128), 'rrect-lg': (280, 160),
}
ROWS = [
    ('checkerboard__rrect-sm__rest', 'rrect-sm'),
    ('checkerboard__capsule-button__rest', 'capsule-button'),
    ('checkerboard__rrect-md__rest', 'rrect-md'),
    ('checkerboard__rrect-ml__rest', 'rrect-ml'),
    ('checkerboard__rrect-lg__rest', 'rrect-lg'),
    ('photo__rrect-md__rest', 'rrect-md'),
]
MARGIN = 8
ZOOM = 3
CORNER_ZOOM = 10
DIFF_FULL_SCALE = 0.25
GAP = 6


def srgb_to_linear(c):
    return np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)


def luma_linear(rgb8):
    c = srgb_to_linear(rgb8.astype(np.float64) / 255.0)
    return 0.2126 * c[..., 0] + 0.7152 * c[..., 1] + 0.0722 * c[..., 2]


def box(component, scale, margin=MARGIN):
    w, h = COMPONENTS[component]
    x0, y0 = 160 - w / 2 - margin, 100 - h / 2 - margin
    return tuple(int(round(v * scale)) for v in (x0, y0, x0 + w + 2 * margin, y0 + h + 2 * margin))


def corner_box(component, scale, which, size=40):
    """A `size` CSS px square around one corner of the component, 4 px outside the contour."""
    w, h = COMPONENTS[component]
    x0, x1, y0, y1 = 160 - w / 2, 160 + w / 2, 100 - h / 2, 100 + h / 2
    bx, by = {'tl': (x0 - 4, y0 - 4), 'tr': (x1 + 4 - size, y0 - 4),
              'bl': (x0 - 4, y1 + 4 - size), 'br': (x1 + 4 - size, y1 + 4 - size)}[which]
    return tuple(int(round(v * scale)) for v in (bx, by, bx + size, by + size))


def zoomed(im, z):
    return im.resize((im.width * z, im.height * z), Image.NEAREST)


def diff_panel(native_rgb8, web_rgb8):
    d = luma_linear(web_rgb8) - luma_linear(native_rgb8)
    v = np.clip(0.5 + d / (2 * DIFF_FULL_SCALE), 0, 1)
    return Image.fromarray((v * 255 + 0.5).astype(np.uint8), 'L').convert('RGB')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--gate', required=True)
    ap.add_argument('--scale', type=int, choices=(1, 2), default=2)
    ap.add_argument('--profile', default=None)
    ap.add_argument('--captures', default=os.path.join(ROOT, 'packages', 'calibration', 'web-captures'))
    ap.add_argument('--renderer', default='webgpu')
    args = ap.parse_args()
    profile = args.profile or f'apple-macos-26.5-{args.scale}x-light-standard'
    scale = args.scale

    rows = []
    label_h = 18
    for scene, component in ROWS:
        native = Image.open(os.path.join(FIXTURES, profile, f'{scene}.png')).convert('RGB')
        web = Image.open(os.path.join(args.captures, profile, scene, f'{scene}__{args.renderer}.png')).convert('RGB')
        if native.size != web.size:
            sys.exit(f'{scene}: fixture {native.size} and capture {web.size} differ in size')
        b = box(component, scale)
        n, w = native.crop(b), web.crop(b)
        d = diff_panel(np.asarray(n), np.asarray(w))
        panels = [zoomed(p, ZOOM) for p in (n, w, d)]
        rows.append((f'{scene}  ({profile}, {args.renderer})', panels))
    # corner row: rrect-md, four corners, native | vitrea each
    scene = 'checkerboard__rrect-md__rest'
    native = Image.open(os.path.join(FIXTURES, profile, f'{scene}.png')).convert('RGB')
    web = Image.open(os.path.join(args.captures, profile, scene, f'{scene}__{args.renderer}.png')).convert('RGB')
    cz = CORNER_ZOOM if scale == 1 else CORNER_ZOOM // 2  # the same screen size per CSS px at both scales
    panels = []
    for which in ('tl', 'tr', 'bl', 'br'):
        cb = corner_box('rrect-md', scale, which)
        panels.append(zoomed(native.crop(cb), cz))
        panels.append(zoomed(web.crop(cb), cz))
    rows.append((f'{scene} corners, 10x per CSS px: native | vitrea, for tl, tr, bl, br', panels))

    width = max(sum(p.width for p in panels) + GAP * (len(panels) - 1) for _, panels in rows) + 2 * GAP
    height = sum(max(p.height for p in panels) + label_h + GAP for _, panels in rows) + GAP
    sheet = Image.new('RGB', (width, height), (24, 24, 24))
    draw = ImageDraw.Draw(sheet)
    y = GAP
    for label, panels in rows:
        draw.text((GAP, y), label, fill=(230, 230, 230))
        y += label_h
        x = GAP
        for p in panels:
            sheet.paste(p, (x, y))
            x += p.width + GAP
        y += max(p.height for p in panels) + GAP
    draw.text((width - 420, GAP), 'native | vitrea | (vitrea - native) linear, +/-0.25', fill=(230, 230, 230))
    # The column labels, large enough to read at any zoom (Decision Log 2 of the
    # W12 spec: the third column was once read as a render). A system font when
    # one is available; PIL's bitmap font otherwise.
    banner = 'LEFT: Apple native fixture     MIDDLE: vitrea GPU tier     RIGHT: signed difference (vitrea - native) - a diagnostic, NOT a render'
    try:
        from PIL import ImageFont
        font = ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc', max(18, width // 90))
    except Exception:
        font = None
    bbox = draw.textbbox((0, 0), banner, font=font)
    strip = Image.new('RGB', (width, bbox[3] - bbox[1] + 24), (16, 16, 16))
    ImageDraw.Draw(strip).text((GAP, 12 - bbox[1]), banner, fill=(255, 220, 120), font=font)
    banded = Image.new('RGB', (width, height + strip.height), (24, 24, 24))
    banded.paste(strip, (0, 0))
    banded.paste(sheet, (0, strip.height))
    sheet = banded
    out = os.path.join(HERE, f'{args.gate}-{scale}x.png')
    sheet.save(out, optimize=True)
    print(out, sheet.size, os.path.getsize(out))


if __name__ == '__main__':
    main()
