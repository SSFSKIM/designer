"""W24 by-eye sheets: the edge lit, and the collapse that keeps its transmission.

W23's sheet script with its crops re-aimed at this wave's terms. The frame is the whole canvas at
zoom 2 at 1x and zoom 1 at 2x — the same screen size per CSS px at both scales — and two kinds of
row are added beside it, because both of this wave's findings are invisible at that zoom:

  * **the ARCS, at 4× per CSS px, nearest neighbour**, cropped to the whole declared surface with a
    small margin. The user's finding is the arcs: a light on the diagonal projects EQUALLY on all
    four straight sides, so a per-side reader and an ordinary sheet both show a rim that looks
    right, and the whole of the difference between a drawn line and a lit edge lives in the corners.
    Apple's 2x dark capsule runs 0.007 at its north-east arc to 0.031 at its north-west; vitrea drew
    one number the whole way round.
  * **the impulse capsule's CENTRE DOT, at 4×**, cropped to the middle of the canvas. That dot is
    the collapse's transmission in one place: the reference passes a peak four times its body
    through the collapsed capsule and vitrea passed nothing.

The rows are contract X6's list: every untinted solid-backdrop cell in both schemes, the impulse
cells, and the TINTED capsules.

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
AFTER_LABEL = {'g2': 'W24 G2 dry run', 'g3': 'W24 G3 LANDED (the canonical bed)'}
# The declared component boxes, in CSS px, from apps/reference-apple/scenes.json — the crops below
# are taken from the declaration and not from the pixels, so a capture that drew nothing is still
# cropped to where the surface should have been.
CANVAS = (320.0, 200.0)
COMPONENT_BOX = {
    'capsule-button': (120.0, 44.0),
    'rrect-md': (160.0, 96.0),
    'rrect-ml': (224.0, 128.0),
}

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
# The cells whose ARCS carry this wave's first finding, shown a second time at 4× per CSS px: the
# dark capsules the user's eye named, and the collapsed pair beside them.
ARCS = (
    'dark-solid__capsule-button__rest',
    'dark-solid__rrect-md__rest',
    'mid-dark-solid__capsule-button__rest',
    'impulse__capsule-button__rest',
    'dark-solid__capsule-button__rest-tint-orange',
)
# And the cell whose centre dot carries the second, shown a third time cropped to the dot itself.
DOT = ('impulse__capsule-button__rest', 'impulse__rrect-md__rest')


def maybe(path):
    return Image.open(path).convert('RGB') if os.path.exists(path) else None


def zoomed(image, zoom):
    return image if zoom == 1 else image.resize(
        (image.width * zoom, image.height * zoom), Image.NEAREST)


def surface_box(component, scale, margin_css=8.0):
    """The declared surface's box in device px, with a margin, centred on the canvas."""
    width, height = COMPONENT_BOX[component]
    left = (CANVAS[0] - width) / 2 - margin_css
    top = (CANVAS[1] - height) / 2 - margin_css
    return (
        int(round(left * scale)),
        int(round(top * scale)),
        int(round((left + width + 2 * margin_css) * scale)),
        int(round((top + height + 2 * margin_css) * scale)),
    )


def arcs(image, component, scale, zoom):
    """The whole declared surface with a margin, magnified — both arcs and both straight spans in
    one strip, which is what makes a LIT edge legible against a drawn one."""
    box = surface_box(component, scale)
    box = (max(0, box[0]), max(0, box[1]), min(image.width, box[2]), min(image.height, box[3]))
    return zoomed(image.crop(box), zoom)


def centre_dot(image, scale, zoom, extent_css=28.0):
    """The canvas's centre, where the impulse background's centre dot sits."""
    half = extent_css * scale / 2
    cx, cy = image.width / 2, image.height / 2
    box = (
        int(round(max(0, cx - half))),
        int(round(max(0, cy - half))),
        int(round(min(image.width, cx + half))),
        int(round(min(image.height, cy + half))),
    )
    return zoomed(image.crop(box), zoom)


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
            component = scene.split('__')[1]
            if scene in ARCS and component in COMPONENT_BOX:
                rows.append((
                    f'{scheme}  {scene}   THE ARCS at 4x per CSS px, nearest neighbour — the '
                    f'corners are where a lit edge differs from a drawn one',
                    [arcs(panel, component, args.scale, zoom4) for panel in panels],
                ))
            if scene in DOT:
                rows.append((
                    f'{scheme}  {scene}   THE CENTRE DOT at 4x per CSS px — what the collapsed '
                    f'material transmits',
                    [centre_dot(panel, args.scale, zoom4) for panel in panels],
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
    banner = ('1 Apple native (the canonical fixture)   2 GPU tier BEFORE (the W23 bed at 0.12.0: '
              'one rim brightness the whole way round, and a collapse that passes nothing)   '
              f'3 GPU tier, {AFTER_LABEL[args.gate]}   4 CSS tier, same document, same run   '
              f'-- both schemes at {args.scale}x, whole canvas at zoom {zoom}, '
              f'the arcs and the centre dot again at 4x per CSS px')
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
