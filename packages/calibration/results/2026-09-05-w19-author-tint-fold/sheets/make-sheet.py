"""W19 by-eye sheets (contract X5): the strength ladder, native where it was captured.

W18's script with its rows and its sources re-aimed at what this wave changes. Five panels per row:

  1  Apple's own capture — the 1x native probe for a ladder rung
     (`results/2026-09-05-w19-author-tint-fold/probe/`, W19 G0's twelve cells) or the canonical
     fixture for a cell that is on the bed. At 2x there is no native ladder (the charter's
     Deferred), so the column is dropped and the banner says so.
     A 2x sheet drops the column on EVERY row, including the bed's, so that one banner describes
     every row of the sheet: a bed cell does have a 2x fixture, but a sheet whose columns mean
     different things on different rows is a sheet that will be misread.
  2  the CSS tier BEFORE the fold — the W18 bed's canonical capture where the scene is on the bed,
     and G0's pre-fold scratch capture for the rungs that exist only on the ladder bed.
  3  the CSS tier WITH the fold — this wave's candidate.
  4  the GPU tier, which this wave binds byte-identical and which is the target both tiers'
     composite is held to (charter Decision Log 1, q0 (a)).
  5  a signed difference of the CSS candidate against column 1 in LINEAR luminance where a native
     panel exists, and against the GPU tier where it does not — grey is zero, full scale ±0.25.

What to look for is the thing the metrics under-report: the seed's hue at low strength. Before the
fold the transfer table saturated on the seed's darkest channel over most of the ladder, which is a
hue shift toward the material's neutral rather than a level error, and column 5 is a luminance
diagnostic that cannot show it. Columns 2 and 3 side by side can.

    python3 make-sheet.py --gate g1 --scale 1 \\
      --ladder-before <G0 scratch captures root> --ladder-after <G1 scratch captures root> \\
      --bed-after <dry-run web-captures>
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
PROBE = os.path.join(HERE, '..', 'probe')

COMPONENTS = {'capsule-button': (120, 44), 'rrect-lg': (280, 160)}
MARGIN = 8
DIFF_FULL_SCALE = 0.25
GAP = 6
LABEL_H = 18

# The ladder's six rungs on both structured backgrounds, then the bed's own tinted cells the
# coordinator named. `source` says where columns 2, 3 and 4 come from: `ladder` is the scratch bed
# G0 and G1 both captured, `bed` is the canonical one.
LADDER = ['orange-010', 'orange-020', 'orange-035', 'orange-half', 'orange-075', 'orange']
ROWS = (
    [(f'photo__capsule-button__rest-tint-{r}', 'capsule-button', 'ladder') for r in LADDER]
    + [(f'checkerboard__capsule-button__rest-tint-{r}', 'capsule-button', 'ladder') for r in LADDER]
    + [('photo__capsule-button__rest-tint-orange-half', 'capsule-button', 'bed'),
       ('hc-text__capsule-button__rest-tint-orange', 'capsule-button', 'bed')]
)


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


def load(path):
    img = maybe(path)
    if img is None:
        sys.exit(f'missing: {path}')
    return img


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--gate', required=True)
    ap.add_argument('--scale', type=int, choices=(1, 2), default=1)
    ap.add_argument('--ladder-before', required=True, help="G0's pre-fold scratch captures root")
    ap.add_argument('--ladder-after', required=True, help="G1's scratch captures root")
    ap.add_argument('--bed-after', required=True, help="the dry run's web-captures")
    ap.add_argument('--bed-before', default=CANONICAL, help='the W18 bed captures')
    args = ap.parse_args()
    profile = f'apple-macos-26.5-{args.scale}x-light-standard'
    scale = args.scale
    zoom = 3 if scale == 1 else 2  # the same screen size per CSS px at both scales
    sx = f'{scale}x'

    rows = []
    for scene, component, source in ROWS:
        if source == 'ladder':
            before = maybe(os.path.join(args.ladder_before, f'std-css-{sx}', scene, f'{scene}__css.png'))
            after = maybe(os.path.join(args.ladder_after, f'std-css-{sx}', scene, f'{scene}__css.png'))
            gpu = maybe(os.path.join(args.ladder_after, f'std-webgpu-{sx}', scene, f'{scene}__webgpu.png'))
            native = maybe(os.path.join(PROBE, profile, f'{scene}.png')) if scale == 1 else None
        else:
            before = maybe(os.path.join(args.bed_before, profile, scene, f'{scene}__css.png'))
            after = maybe(os.path.join(args.bed_after, profile, scene, f'{scene}__css.png'))
            gpu = maybe(os.path.join(args.bed_after, profile, scene, f'{scene}__webgpu.png'))
            native = maybe(os.path.join(FIXTURES, profile, f'{scene}.png')) if scale == 1 else None
        if after is None or before is None or gpu is None:
            print(f'{scene} @ {sx}: a capture is missing (holdout not read at this gate?) — row skipped')
            continue
        b = box(component, scale)
        panels, names = [], []
        if native is not None:
            panels.append(native.crop(b))
            names.append('native')
        panels += [before.crop(b), after.crop(b), gpu.crop(b)]
        names += ['CSS before', 'CSS candidate', 'GPU']
        reference = panels[0] if native is not None else panels[-1]
        panels.append(diff_panel(np.asarray(reference), np.asarray(after.crop(b))))
        names.append('diff')
        rows.append((f'{scene}  ({profile}, {source})', [zoomed(p, zoom) for p in panels]))

    if not rows:
        sys.exit('no rows')
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
    third = 'W19 landed, canonical' if args.gate == 'g2' else 'W19 candidate'
    if scale == 1:
        banner = ('1 Apple native (W19 G0 probe, or the canonical fixture on a bed cell)   '
                  '2 CSS tier before the fold   '
                  f'3 CSS tier, {third}   4 GPU tier   5 diff (column 3 - column 1), '
                  'linear luminance, full scale +-0.25 -- a DIAGNOSTIC, not a render')
    else:
        banner = ('NO NATIVE LADDER AT 2x (the charter Deferred it): 1 CSS tier before the fold   '
                  f'2 CSS tier, {third}   3 GPU tier   4 diff (CSS candidate - GPU tier), '
                  'linear luminance, full scale +-0.25 -- a DIAGNOSTIC, not a render')
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
    out = os.path.join(HERE, f'{args.gate}-{scale}x.png')
    sheet.save(out)
    print(out, sheet.size, f'{len(rows)} rows')


if __name__ == '__main__':
    main()
