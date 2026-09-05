"""W20 by-eye sheets: the capsule's corner, before and after the fix.

W19's sheet script with its columns re-aimed at what this wave changes. The wave is a geometry
correction on the GPU tier alone, so the sheet is a GPU sheet: what has to be visible is the
shoulders at the ends of the capsule disappearing, and the round ends reading as round.

Four panels per row:

  1  Apple's own capture — the canonical fixture for the cell (`apps/reference-apple/fixtures/`).
  2  the GPU tier BEFORE, the canonical capture on the capture machine (the W19 bed), which is the
     render with the corner clamped to `min(halfW, halfH) / APPLE_REACH`.
  3  the GPU tier AFTER, this gate's dry-run capture.
  4  a signed difference of column 3 against column 1 in LINEAR luminance — grey is zero, full
     scale ±0.25. It is a diagnostic and not a render: what it shows is where the residual sits
     once the shoulders are gone, and the shoulders themselves are what it showed before.

The crop is the component's own box plus a margin, so the corner fills the panel; the zoom is 3 at
1x and 2 at 2x, which is the same screen size per CSS px at both scales and the same zoom the W19
landing sheet used, because the finding was made by eye at it.

    python3 make-sheet.py --gate g1 --scale 1 --gpu-after <dry-run web-captures root>
"""
import argparse
import os

import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..', '..', '..'))
FIXTURES = os.path.join(ROOT, 'apps', 'reference-apple', 'fixtures')
CANONICAL = os.path.join(ROOT, 'packages', 'calibration', 'web-captures')

# Width and height in CSS px, from `apps/reference-apple/scenes.json`. The toolbar group is three
# 44 px capsules at spacing 12, which is 156 across — the row that shows three corners at once.
COMPONENTS = {'capsule-button': (120, 44), 'toolbar-group': (156, 44)}
ROWS = (
    ('photo__capsule-button__rest', 'capsule-button'),
    ('checkerboard__capsule-button__rest', 'capsule-button'),
    ('light-solid__capsule-button__rest', 'capsule-button'),
    ('hc-text__capsule-button__rest', 'capsule-button'),
    ('photo__toolbar-group__rest', 'toolbar-group'),
)
MARGIN = 8
DIFF_FULL_SCALE = 0.25
GAP = 6
LABEL_H = 18


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


def diff_panel(reference8, web8):
    d = (luma_linear(web8) - luma_linear(reference8)) / DIFF_FULL_SCALE
    g = np.clip(128 + d * 127, 0, 255).astype(np.uint8)
    return Image.fromarray(np.stack([g, g, g], axis=-1), 'RGB')


def zoomed(img, z):
    return img.resize((img.width * z, img.height * z), Image.NEAREST)


def maybe(path):
    return Image.open(path).convert('RGB') if os.path.exists(path) else None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--gate', required=True)
    ap.add_argument('--scale', type=int, choices=(1, 2), default=1)
    ap.add_argument('--gpu-after', required=True, help="the dry run's web-captures root")
    ap.add_argument('--gpu-before', default=CANONICAL, help='the W19 bed captures')
    args = ap.parse_args()
    profile = f'apple-macos-26.5-{args.scale}x-light-standard'
    zoom = 3 if args.scale == 1 else 2

    rows = []
    for scene, component in ROWS:
        native = maybe(os.path.join(FIXTURES, profile, f'{scene}.png'))
        before = maybe(os.path.join(args.gpu_before, profile, scene, f'{scene}__webgpu.png'))
        after = maybe(os.path.join(args.gpu_after, profile, scene, f'{scene}__webgpu.png'))
        if native is None or before is None or after is None:
            missing = [n for n, v in (('native', native), ('before', before), ('after', after))
                       if v is None]
            print(f'{scene} @ {args.scale}x: missing {", ".join(missing)} — row skipped')
            continue
        b = box(component, args.scale)
        panels = [native.crop(b), before.crop(b), after.crop(b)]
        panels.append(diff_panel(np.asarray(panels[0]), np.asarray(panels[2])))
        rows.append((f'{scene}  ({profile})', [zoomed(p, zoom) for p in panels]))

    if not rows:
        raise SystemExit('no rows')
    width = max(sum(p.width for p in panels) + GAP * (len(panels) - 1) for _, panels in rows) + 2 * GAP
    banner_h = 44
    height = banner_h + sum(max(p.height for p in panels) + LABEL_H + GAP for _, panels in rows) + GAP
    sheet = Image.new('RGB', (width, height), (24, 24, 24))
    draw = ImageDraw.Draw(sheet)
    try:
        from PIL import ImageFont
        font = ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc', max(16, width // 130))
    except Exception:
        font = None
    third = 'W20 landed, canonical' if args.gate == 'g2' else 'W20 candidate'
    banner = ('1 Apple native (the canonical fixture)   2 GPU tier BEFORE (the W19 bed, corner '
              f'clamped)   3 GPU tier, {third}   4 diff (column 3 - column 1), linear luminance, '
              'full scale +-0.25 -- a DIAGNOSTIC, not a render')
    draw.text((GAP, GAP), banner, fill=(230, 230, 230), font=font)
    y = banner_h
    for label, panels in rows:
        draw.text((GAP, y), label, fill=(230, 230, 230))
        y += LABEL_H
        x = GAP
        for p in panels:
            sheet.paste(p, (x, y))
            x += p.width + GAP
        y += max(p.height for p in panels) + GAP
    out = os.path.join(HERE, f'{args.gate}-{args.scale}x.png')
    sheet.save(out)
    print(out, sheet.size, f'{len(rows)} rows')


if __name__ == '__main__':
    main()
