#!/usr/bin/env python3
"""W14 close-up strip: the band just below the surface where the shadow's two terms live.

For each named cell, two rows of three panels — native | W12 close | candidate — cropped to the
strip beneath the surface's bottom edge and zoomed so one CSS px is six screen px at either scale.
The first row is the capture as encoded. The second is the same crop with its levels stretched
four times about black (a diagnostic, not a render): the lift the reference adds to the black
squares below a thick surface is about 7 of 255 codes, which the eye does not resolve unstretched,
and the stretch is what makes "the blacks are lifted" readable beside "the blacks are not".

    cd packages/calibration && python3 results/2026-09-03-w14-shadow/sheets/make-closeup.py \
        --gate g1 --scale 1 --candidate <scratch captures dir>
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

# (scene, crop in CSS px: x0, y0, x1, y1). Surfaces are centred on the 320x200 canvas; the
# bottom edge of a 160-tall surface is at y 180, of a 96-tall one at 148, of a 44-tall one at 122.
CELLS = [
    ('checkerboard__rrect-lg__rest', (40, 172, 280, 200)),
    ('checkerboard__rrect-md__rest', (60, 140, 260, 196)),
    ('light-solid__capsule-button__rest', (60, 114, 260, 170)),
    ('dark-solid__rrect-md__rest', (60, 140, 260, 196)),
]
GAP = 6


def load(path):
    if not os.path.exists(path):
        sys.exit(f'missing: {path}')
    return Image.open(path).convert('RGB')


def stretch(img, k=4):
    a = np.asarray(img).astype(np.float64)
    return Image.fromarray(np.clip(a * k, 0, 255).astype(np.uint8), 'RGB')


def zoomed(img, z):
    return img.resize((img.width * z, img.height * z), Image.NEAREST)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--gate', required=True)
    ap.add_argument('--scale', type=int, choices=(1, 2), default=1)
    ap.add_argument('--candidate', required=True)
    ap.add_argument('--renderer', default='webgpu')
    args = ap.parse_args()
    profile = f'apple-macos-26.5-{args.scale}x-light-standard'
    zoom = 6 // args.scale

    rows = []
    for scene, (x0, y0, x1, y1) in CELLS:
        b = tuple(v * args.scale for v in (x0, y0, x1, y1))
        native = load(os.path.join(FIXTURES, profile, f'{scene}.png')).crop(b)
        before = load(os.path.join(CANONICAL, profile, scene, f'{scene}__{args.renderer}.png')).crop(b)
        after = load(os.path.join(args.candidate, profile, scene, f'{scene}__{args.renderer}.png')).crop(b)
        rows.append((f'{scene}  ({profile}) -- as encoded', [zoomed(p, zoom) for p in (native, before, after)]))
        rows.append((f'{scene}  -- levels x4 about black (diagnostic, NOT a render)',
                     [zoomed(stretch(p), zoom) for p in (native, before, after)]))

    label_h = 18
    banner_h = 40
    width = max(sum(p.width for p in ps) + GAP * 2 for _, ps in rows) + 2 * GAP
    height = banner_h + sum(max(p.height for p in ps) + label_h + GAP for _, ps in rows) + GAP
    sheet = Image.new('RGB', (width, height), (24, 24, 24))
    draw = ImageDraw.Draw(sheet)
    try:
        from PIL import ImageFont
        font = ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc', max(18, width // 110))
    except Exception:
        font = None
    draw.text((GAP, GAP), 'LEFT: Apple native   MIDDLE: vitrea W12 close   RIGHT: vitrea W14 candidate   '
              '-- the strip just below the surface, 6 screen px per CSS px', fill=(230, 230, 230), font=font)
    y = banner_h
    for label, ps in rows:
        draw.text((GAP, y), label, fill=(230, 230, 230))
        y += label_h
        x = GAP
        for p in ps:
            sheet.paste(p, (x, y))
            x += p.width + GAP
        y += max(p.height for p in ps) + GAP
    out = os.path.join(HERE, f'{args.gate}-closeup-{args.scale}x.png')
    sheet.save(out)
    print(out, sheet.size)


if __name__ == '__main__':
    main()
