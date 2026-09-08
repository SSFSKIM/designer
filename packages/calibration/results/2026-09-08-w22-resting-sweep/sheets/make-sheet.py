"""W22 by-eye sheets: the resting sweep gated and the light rim's specular fitted to 0.

W21's sheet script with its scene list re-aimed and BOTH schemes on one sheet, because this wave's
constant is on the light profile and its consequence has to be read in the scheme it was fitted in
and in the one that already held it. The frame is the whole canvas at zoom 2 at 1x and zoom 1 at 2x
— the same screen size per CSS px at both scales — since what moved is a rim band around a whole
surface and a level inside it, not a corner.

The rows are contract X6's list: every untinted solid-backdrop cell in both schemes (the fit's own
rows and its holdout check, `mid-dark-solid`), the two stacked scenes in both schemes (the first
look at W22 G3's fix against the reference), and the dark `impulse` capsule (eye finding 1, which
this wave chartered rather than tuned — it is here so the user can see what was chartered).

Four panels per row:

  1  Apple's own capture — the canonical fixture for the cell (`apps/reference-apple/fixtures/`).
  2  the GPU tier BEFORE — the canonical capture on the capture machine, which is the W21 bed at
     the 0.10.0 landing: the resting specular band on every left edge, the light rim's specular at
     0.55, and the overlay of a stacked scene handed no backdrop at all.
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
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..', '..', '..'))
FIXTURES = os.path.join(ROOT, 'apps', 'reference-apple', 'fixtures')
GAP = 6
LABEL_H = 18
BANNER_H = 44

# Per scheme, in the order the sheet reads them. A scene a profile does not declare is skipped with
# a printed line rather than silently, so the sheet's absences are legible.
SOLIDS = (
    'light-solid__capsule-button__rest',
    'light-solid__rrect-md__rest',
    'light-solid__rrect-ml__rest',
    'dark-solid__capsule-button__rest',
    'dark-solid__rrect-md__rest',
    'mid-dark-solid__capsule-button__rest',
)
STACKS = ('checkerboard__glass-over-glass__rest', 'photo__glass-over-glass__rest')
EYE = ('impulse__capsule-button__rest',)


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
    zoom = 2 if args.scale == 1 else 1

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
        for scene in SOLIDS + STACKS + (EYE if scheme == 'dark' else ()):
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
    banner = ('1 Apple native (the canonical fixture)   2 GPU tier BEFORE (the W21 bed at 0.10.0: '
              'the resting specular band, specularGain 0.55, the overlay handed no backdrop)   '
              '3 GPU tier, W22 G1 dry run   4 CSS tier, same document, same run   '
              f'-- both schemes at {args.scale}x, whole canvas, zoom {zoom}')
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
