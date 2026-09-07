"""W21 by-eye sheets: the dark scheme, before and after the response law stands up.

W20's sheet script with its columns and its frame re-aimed at what this wave changes. W20 was a
geometry correction and its sheet cropped hard on one corner; this wave changes the BODY LEVEL, the
RIM AMPLITUDE and the PASSTHROUGH across the whole surface, and the largest component on the dark
bed (`rrect-lg`, 280 x 160) is most of the 320 x 200 canvas. So the frame is the whole canvas, at
zoom 2 at 1x and 1 at 2x — the same screen size per CSS px at both scales, and the frame in which
the body against its backdrop is what the eye compares.

Four panels per row, which is contract X5's list:

  1  Apple's own capture — the canonical fixture for the cell (`apps/reference-apple/fixtures/`).
  2  the GPU tier BEFORE — the canonical capture on the capture machine, which is the W20 bed.
  3  the GPU tier at this gate's dry run.
  4  the CSS tier at this gate's dry run, derived from the same patch (wave Decision Log 23 (a)).

There is deliberately no difference panel. W20's fourth column was a signed difference because its
change was a silhouette a difference makes legible; this wave's change is a level, and a level is
read by putting the render beside the reference and the CSS tier beside the GPU one. The numbers
live in `g1-tables.txt` and in the caption.

    python3 make-sheet.py --gate g1 --scale 1 \
        --gpu-after <dry-run web-captures> --css-after <dry-run web-captures> \
        --gpu-before <canonical web-captures> --matrix <dry-run matrix.json>
"""
import argparse
import json
import os

from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..', '..', '..'))
FIXTURES = os.path.join(ROOT, 'apps', 'reference-apple', 'fixtures')
CANVAS = (320, 200)
GAP = 6
LABEL_H = 18
BANNER_H = 44


def maybe(path):
    return Image.open(path).convert('RGB') if os.path.exists(path) else None


def zoomed(image, zoom):
    return image if zoom == 1 else image.resize(
        (image.width * zoom, image.height * zoom), Image.NEAREST)


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
    profile = f'apple-macos-26.5-{args.scale}x-dark-standard'
    zoom = 2 if args.scale == 1 else 1

    scenes = json.load(open(os.path.join(ROOT, 'apps', 'reference-apple', 'scenes.json')))
    declared = next(p['scenes'] for p in scenes['profiles'] if p['key'] == profile)
    dry = json.load(open(args.matrix))
    bed = json.load(open(bed_matrix))

    rows = []
    for scene in declared:
        native = maybe(os.path.join(FIXTURES, profile, f'{scene}.png'))
        before = maybe(os.path.join(args.gpu_before, profile, scene, f'{scene}__webgpu.png'))
        after = maybe(os.path.join(args.gpu_after, profile, scene, f'{scene}__webgpu.png'))
        css = maybe(os.path.join(css_after, profile, scene, f'{scene}__css.png'))
        panels = [native, before, after, css]
        if any(panel is None for panel in panels):
            names = ('native', 'GPU before', 'GPU after', 'CSS after')
            missing = [n for n, p in zip(names, panels) if p is None]
            print(f'{scene} @ {args.scale}x: missing {", ".join(missing)} — row skipped')
            continue
        was = delta_e(bed, profile, 'webgpu', scene)
        now = delta_e(dry, profile, 'webgpu', scene)
        css_now = delta_e(dry, profile, 'css', scene)
        caption = (f'{scene}   GPU ΔE {was:.5f} → {now:.5f}   CSS ΔE now {css_now:.5f}'
                   if was is not None and now is not None and css_now is not None else scene)
        rows.append((caption, [zoomed(panel, zoom) for panel in panels]))

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
    third = 'GPU tier, W21 landed' if args.gate == 'g2' else 'GPU tier, W21 G1 dry run'
    banner = ('1 Apple native (the canonical fixture)   2 GPU tier BEFORE (the W20 bed: the response '
              f'law stood down, the two-light rim)   3 {third}   4 CSS tier, same patch, same run   '
              f'-- {profile}, whole canvas, zoom {zoom}')
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
