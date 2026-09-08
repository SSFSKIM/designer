"""W23 by-eye sheets: the rim's law landed, and the rim the collapse now keeps.

W22's sheet script with its scene list re-aimed at this wave's term. The frame is the whole canvas
at zoom 2 at 1x and zoom 1 at 2x — the same screen size per CSS px at both scales — and the
BLACK-ON-BLACK cells get a second row beside their own at 4× per CSS px, nearest neighbour, cropped
to the top edge: that is where the whole of the user's finding lives ("not one of our glasses is
visible on black, where Apple's clearly show their presence"), and it is +0.020 of linear luminance
on a body of 0.011, which at the sheet's ordinary zoom is a line nobody can judge.

The rows are contract X6's list: every untinted solid-backdrop cell in both schemes, the TINTED
capsules (this gate's own mechanism — the rim reads the material's level and not the painted one,
and the collapse keeps a painted rim of its own), and the collapsed pair at 4×.

Four panels per row:

  1  Apple's own capture — the canonical fixture for the cell (`apps/reference-apple/fixtures/`).
  2  the GPU tier BEFORE — the canonical capture on the capture machine, the W22 bed at the 0.11.0
     landing: an additive rim of one height on every cell, and no rim at all under the collapse.
  3  the GPU tier at this gate's dry run.
  4  the CSS tier at the same run, derived from the same document.

    python3 make-sheet.py --gate g1 --scale 1 \
        --gpu-after <dry-run web-captures> --gpu-before <canonical web-captures> \
        --matrix <dry-run matrix.json>
"""
import argparse
import json
import os

from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..', '..', '..', '..'))
FIXTURES = os.path.join(ROOT, 'apps', 'reference-apple', 'fixtures')
GAP = 6
LABEL_H = 18
BANNER_H = 44
AFTER_LABEL = {'g1': 'W23 G1 dry run', 'g2': 'W23 G2 LANDED (the canonical bed)'}

SOLIDS = (
    'light-solid__capsule-button__rest',
    'light-solid__rrect-md__rest',
    'light-solid__rrect-ml__rest',
    'dark-solid__capsule-button__rest',
    'dark-solid__rrect-md__rest',
    'mid-dark-solid__capsule-button__rest',
    'impulse__capsule-button__rest',
    'impulse__rrect-md__rest',
)
TINTED = (
    'dark-solid__capsule-button__rest-tint-orange',
    'impulse__capsule-button__rest-tint-orange',
    'checkerboard__capsule-button__rest-tint-orange',
    'photo__capsule-button__rest-tint-blue',
)
# The cells the user's eye named, and the ones this wave's clause 1 is written on: a body one code
# below its backdrop with a contour rim of +0.020 on it. Shown twice — once in the frame, once at
# 4× per CSS px cropped to the top edge, which is the only magnification that shows a one-pixel line
# on a near-black body at all.
BLACK_ON_BLACK = (
    'dark-solid__capsule-button__rest',
    'impulse__capsule-button__rest',
    'dark-solid__capsule-button__rest-tint-orange',
    'impulse__capsule-button__rest-tint-orange',
)


def maybe(path):
    return Image.open(path).convert('RGB') if os.path.exists(path) else None


def zoomed(image, zoom):
    return image if zoom == 1 else image.resize(
        (image.width * zoom, image.height * zoom), Image.NEAREST)


def top_edge(image, scale, zoom):
    """The surface's top edge, cropped and magnified: the whole width, the upper third."""
    height = max(8 * scale, image.height // 3)
    return zoomed(image.crop((0, 0, image.width, min(height, image.height))), zoom)


def delta_e(matrix, profile, renderer, scene):
    best = None
    for cell in matrix['cells']:
        key = cell['key']
        if (key['profileKey'], key['web']['renderer'], key['sceneId']) != (profile, renderer, scene):
            continue
        if best is None or cell['capturedAt'] > best['capturedAt']:
            best = cell
    if best is None:
        return None
    entry = (best.get('perceptual') or {}).get('oklabDeltaEMean')
    if entry is None:
        return None
    return entry['value'] if isinstance(entry, dict) else entry


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--gate', required=True)
    parser.add_argument('--scale', type=int, choices=(1, 2), default=1)
    parser.add_argument('--gpu-after', required=True, help="the dry run's web-captures root")
    parser.add_argument('--css-after', default=None, help='defaults to --gpu-after')
    parser.add_argument('--gpu-before', required=True, help='the canonical web-captures root')
    parser.add_argument('--matrix', required=True, help="the dry run's matrix")
    parser.add_argument('--bed-matrix', default=None, help='defaults to the canonical matrix')
    args = parser.parse_args()
    css_after = args.css_after or args.gpu_after
    bed_matrix = args.bed_matrix or os.path.join(
        ROOT, 'packages', 'calibration', 'results', 'matrix.json')
    zoom = 2 if args.scale == 1 else 1
    zoom4 = 4 if args.scale == 1 else 2

    scenes = json.load(open(os.path.join(ROOT, 'apps', 'reference-apple', 'scenes.json')))
    declared_for = {p['key']: p['scenes'] for p in scenes['profiles']}
    all_ids = [s['id'] for s in scenes['scenes']]
    dry = json.load(open(args.matrix))
    bed = json.load(open(bed_matrix))

    rows = []
    for scheme in ('light', 'dark'):
        profile = f'apple-macos-26.5-{args.scale}x-{scheme}-standard'
        declared = declared_for[profile]
        declared = all_ids if declared == 'all' else declared
        for scene in SOLIDS + TINTED:
            if scene not in declared:
                continue
            native = maybe(os.path.join(FIXTURES, profile, f'{scene}.png'))
            before = maybe(os.path.join(args.gpu_before, profile, scene, f'{scene}__webgpu.png'))
            after = maybe(os.path.join(args.gpu_after, profile, scene, f'{scene}__webgpu.png'))
            css = maybe(os.path.join(css_after, profile, scene, f'{scene}__css.png'))
            panels = [native, before, after, css]
            if any(panel is None for panel in panels):
                names = ('native', 'GPU before', 'GPU after', 'CSS after')
                missing = [n for n, p in zip(names, panels) if p is None]
                print(f'{scheme} {scene} @ {args.scale}x: missing {", ".join(missing)} — skipped')
                continue
            was = delta_e(bed, profile, 'webgpu', scene)
            now = delta_e(dry, profile, 'webgpu', scene)
            css_now = delta_e(dry, profile, 'css', scene)
            fmt = lambda v: 'n/a' if v is None else f'{v:.5f}'  # noqa: E731
            caption = (f'{scheme}  {scene}   GPU dE {fmt(was)} -> {fmt(now)}   '
                       f'CSS dE now {fmt(css_now)}')
            rows.append((caption, [zoomed(panel, zoom) for panel in panels]))
            if scene in BLACK_ON_BLACK:
                rows.append((
                    f'{scheme}  {scene}   TOP EDGE at {zoom4 * args.scale}x per device px, '
                    f'nearest neighbour — the rim the collapse keeps',
                    [top_edge(panel, args.scale, zoom4) for panel in panels],
                ))

    if not rows:
        raise SystemExit('no rows')
    width = max(sum(p.width for p in panels) + GAP * (len(panels) - 1)
                for _c, panels in rows) + 2 * GAP
    height = BANNER_H + sum(max(p.height for p in panels) + LABEL_H + GAP
                            for _c, panels in rows) + GAP
    sheet = Image.new('RGB', (width, height), (24, 24, 24))
    draw = ImageDraw.Draw(sheet)
    try:
        from PIL import ImageFont
        font = ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc', max(16, width // 150))
    except Exception:
        font = None
    banner = ('1 Apple native (the canonical fixture)   2 GPU tier BEFORE (the W22 bed at 0.11.0: '
              'an additive rim of one height, and none at all under the collapse)   '
              f'3 GPU tier, {AFTER_LABEL[args.gate]}   4 CSS tier, same document, same run   '
              f'-- both schemes at {args.scale}x, whole canvas at zoom {zoom}, '
              f'the black-on-black cells again at {zoom4}x')
    draw.text((GAP, GAP), banner, fill=(230, 230, 230), font=font)
    y = BANNER_H
    for caption, panels in rows:
        draw.text((GAP, y), caption, fill=(230, 230, 230))
        y += LABEL_H
        x = GAP
        for panel in panels:
            sheet.paste(panel, (x, y))
            x += panel.width + GAP
        y += max(p.height for p in panels) + GAP
    out = os.path.join(HERE, f'{args.gate}-{args.scale}x.png')
    sheet.save(out)
    print(out, sheet.size, f'{len(rows)} rows')


if __name__ == '__main__':
    main()
