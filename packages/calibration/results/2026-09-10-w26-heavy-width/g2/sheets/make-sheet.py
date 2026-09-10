"""W26 by-eye sheets: the thick surface's HAZE, at a heavy component a third narrower.

W25 G3's sheet script with its crops re-aimed at this wave's term. That wave landed a rim factor and
its sheets were built around corners; this one lands the WIDTH of the body's heavy component —
13.418 → 9 device px at dpr 1 — so what the eye is being asked to judge is interior haze, and a
corner strip would show almost nothing.

Three kinds of row, and each exists because the previous kind hides what it carries:

  * the whole canvas, zoom 2 at 1x and zoom 1 at 2x — the same screen size per CSS px at both
    scales, which is where a body that washes a checkerboard flatter or less flat than Apple's is
    visible at all;
  * **the nested pane's BASE at 2x**, cropped with the overlay's own box left in frame — the user's
    cell, "Apple's bottom glass is very slightly less transparent", and W25 clause 3's;
  * **the impulse rrect's centre dot at 4x**, which is where the kernel is read and where a third
    off the heavy width has its largest single effect on one feature.

The three columns are native | 0.14.0 | the candidate, with the CSS tier's own capture beside them,
because this is the first wave in which BOTH tiers' heavy widths move and the CSS panel is a claim
rather than a control.

    python3 make-sheet.py --scale 1 \
        --gpu-after <dry-run web-captures> --gpu-before <the 0.14.0 control's web-captures> \
        --probe-after <dry-run web-captures> --probe-before <the 0.14.0 probe control> \
        --matrix <dry-run matrix.json>
"""
import argparse
import json
import os

from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..', '..', '..', '..'))
FIXTURES = os.path.join(ROOT, 'apps', 'reference-apple', 'fixtures')
SCENES = os.path.join(ROOT, 'apps', 'reference-apple', 'scenes.json')
GAP = 6
LABEL_H = 18
BANNER_H = 44
CANVAS = (320.0, 200.0)

# The canonical thick cells: the rrects the wave is named for, on the backdrops that carry a body.
CANONICAL = (
    'dark-solid__rrect-md__rest',
    'light-solid__rrect-md__rest',
    'checkerboard__rrect-md__rest',
    'checkerboard__rrect-ml__rest',
    'photo__rrect-md__rest',
    'photo__rrect-ml__rest',
    'impulse__rrect-md__rest',
    'checkerboard__glass-over-glass__rest',
)
# The probe rows the width was FITTED on, which is what the eye should see it on: the coarse
# checkerboards, whose pitch is where a heavy component's width is visible at all, and the second
# impulse span. `checkerboard-64` is the row that reads the 1x width where the impulse tile cannot
# (claims §5.120 §7), so it is the one to look at first.
SWEEP = (
    'checkerboard-64__rrect-md__rest',
    'checkerboard-64__rrect-lg__rest',
    'checkerboard-32__rrect-md__rest',
    'checkerboard-32__rrect-lg__rest',
    'checkerboard-8__rrect-md__rest',
    'impulse__rrect-lg__rest',
)
# No corner strip this wave: the mechanism is a body width and the corners carry the rim.
CORNERS = ()
# The cells whose centre dot carries the kernel, and where a third off the heavy width shows most.
DOT = ('impulse__rrect-md__rest', 'impulse__rrect-lg__rest')
# The user's cell.
STACK = ('checkerboard__glass-over-glass__rest',)


def maybe(path):
    return Image.open(path).convert('RGB') if os.path.exists(path) else None


def zoomed(image, zoom):
    return image if zoom == 1 else image.resize(
        (image.width * zoom, image.height * zoom), Image.NEAREST)


def placed(spec):
    """`component-region.ts`'s rule: centred on the canvas, then displaced by its own offset."""
    width, height = float(spec['size'][0]), float(spec['size'][1])
    offset = spec.get('offset', (0, 0))
    left = round((CANVAS[0] - width) / 2) + float(offset[0])
    top = round((CANVAS[1] - height) / 2) + float(offset[1])
    return left, top, width, height


def box_of(component, comps):
    """The declared surface's box in CSS px — the base's box for a stack, the union for a group."""
    spec = comps[component]
    if spec['kind'] == 'stack':
        return placed(spec['base'])
    if spec['kind'] == 'group':
        items = spec['items']
        spacing = float(spec['spacing'])
        total = sum(i['size'][0] for i in items) + spacing * (len(items) - 1)
        height = max(i['size'][1] for i in items)
        return round((CANVAS[0] - total) / 2), round((CANVAS[1] - height) / 2), total, height
    return placed(spec)


def crop_css(image, scale, left, top, width, height):
    box = (int(round(left * scale)), int(round(top * scale)),
           int(round((left + width) * scale)), int(round((top + height) * scale)))
    box = (max(0, box[0]), max(0, box[1]), min(image.width, box[2]), min(image.height, box[3]))
    return image.crop(box)


def corner_strip(image, component, comps, scale, zoom, reach=34.0):
    """The two BRIGHT corners beside the two dim ones, in one strip.

    The field is `+1` at the top-left and bottom-right and `−1` at the top-right and bottom-left, so
    the difference the eye has to judge is between corners of the SAME image and not between two
    images. The strip is TL | BR | TR | BL, each a `reach` CSS px square of the surface's own
    corner, magnified.
    """
    left, top, width, height = box_of(component, comps)
    reach = min(reach, width / 2, height / 2)
    quads = [(left, top), (left + width - reach, top + height - reach),
             (left + width - reach, top), (left, top + height - reach)]
    tiles = [zoomed(crop_css(image, scale, x, y, reach, reach), zoom) for x, y in quads]
    strip = Image.new('RGB', (sum(t.width for t in tiles) + 3 * 2, max(t.height for t in tiles)),
                      (24, 24, 24))
    x = 0
    for tile in tiles:
        strip.paste(tile, (x, 0))
        x += tile.width + 2
    return strip


def stack_base(image, component, comps, scale, zoom, margin=6.0):
    """The nested pane's BASE with the overlay still in frame — the user's cell."""
    left, top, width, height = box_of(component, comps)
    return zoomed(crop_css(image, scale, left - margin, top - margin,
                           width + 2 * margin, height + 2 * margin), zoom)


def centre_dot(image, scale, zoom, extent_css=28.0):
    half = extent_css * scale / 2
    cx, cy = image.width / 2, image.height / 2
    box = (int(round(max(0, cx - half))), int(round(max(0, cy - half))),
           int(round(min(image.width, cx + half))), int(round(min(image.height, cy + half))))
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
    parser.add_argument('--scale', type=int, choices=(1, 2), default=1)
    parser.add_argument('--gpu-after', required=True)
    # W25 G3b's third GPU column: the pair G3 declared, kept beside the pair G3b declares so the
    # eye judges the CHANGE OF RULING and not only the change from the shipped bed. Absent, the
    # sheet is G3's four-panel form.
    parser.add_argument('--gpu-mid', default=None)
    parser.add_argument('--gpu-before', required=True)
    parser.add_argument('--probe-after', required=True)
    parser.add_argument('--probe-before', required=True)
    parser.add_argument('--matrix', required=True)
    parser.add_argument('--bed-matrix', default=None)
    args = parser.parse_args()
    bed_matrix = args.bed_matrix or os.path.join(
        ROOT, 'packages', 'calibration', 'results', 'matrix.json')
    zoom = 2 if args.scale == 1 else 1
    zoom4 = 4 if args.scale == 1 else 2

    scenes = json.load(open(SCENES))
    comps = scenes['components']
    dry = json.load(open(args.matrix))
    bed = json.load(open(bed_matrix))

    rows = []
    for scheme in ('light', 'dark'):
        profile = f'apple-macos-26.5-{args.scale}x-{scheme}-standard'
        for scene, source in ([(s, 'canonical') for s in CANONICAL]
                              + [(s, 'probe') for s in SWEEP]):
            after_root = args.gpu_after if source == 'canonical' else args.probe_after
            before_root = args.gpu_before if source == 'canonical' else args.probe_before
            # The CSS panel is the CANDIDATE's on both sources, and that is a change from W25:
            # this wave moves the CSS tier's own heavy width, so its panel is a claim rather than a
            # control and it has to be the material the other three panels are about. The dry run
            # captured the probe set on both tiers for exactly this reason.
            css_root = args.gpu_after if source == 'canonical' else args.probe_after
            native = maybe(os.path.join(FIXTURES, profile, f'{scene}.png'))
            before = maybe(os.path.join(before_root, profile, scene, f'{scene}__webgpu.png'))
            after = maybe(os.path.join(after_root, profile, scene, f'{scene}__webgpu.png'))
            css = maybe(os.path.join(css_root, profile, scene, f'{scene}__css.png'))
            mid = (maybe(os.path.join(args.gpu_mid, profile, scene, f'{scene}__webgpu.png'))
                   if args.gpu_mid else None)
            panels = ([native, before, mid, after, css] if args.gpu_mid and mid is not None
                      else [native, before, after, css])
            if any(panel is None for panel in panels):
                names = ('native', 'GPU before', 'GPU after', 'CSS after')
                missing = [n for n, p in zip(names, panels) if p is None]
                print(f'{scheme} {scene} @ {args.scale}x: missing {", ".join(missing)} — skipped')
                continue
            if source == 'canonical':
                was, now = delta_e(bed, profile, 'webgpu', scene), delta_e(dry, profile, 'webgpu',
                                                                          scene)
                css_now = delta_e(dry, profile, 'css', scene)
                fmt = lambda v: 'n/a' if v is None else f'{v:.5f}'  # noqa: E731
                caption = (f'{scheme}  {scene}   GPU dE {fmt(was)} -> {fmt(now)}   '
                           f'CSS dE now {fmt(css_now)}')
            else:
                caption = (f'{scheme}  {scene}   PROBE (not a gated set): before = the 0.14.0 '
                           f'control rung, after = the candidate')
            rows.append((caption, [zoomed(panel, zoom) for panel in panels]))
            component = scene.split('__')[1]
            if scene in CORNERS:
                rows.append((
                    f'{scheme}  {scene}   THE RIM\'S CORNERS at 4x per CSS px — TL | BR | TR | BL. '
                    f'The field draws the first pair bright and the second pair dim.',
                    [corner_strip(panel, component, comps, args.scale, zoom4) for panel in panels],
                ))
            if scene in STACK:
                rows.append((
                    f'{scheme}  {scene}   THE NESTED PANE\'S BASE at 2x per CSS px — the eye\'s '
                    f'cell: Apple\'s bottom glass is very slightly less transparent',
                    [stack_base(panel, component, comps, args.scale, 2) for panel in panels],
                ))
            if scene in DOT:
                rows.append((
                    f'{scheme}  {scene}   THE CENTRE DOT at {zoom4}x per CSS px — the kernel, and '
                    f'where a third off the heavy width shows most on one feature',
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
    banner = ('1 Apple native (the canonical or probe fixture)   '
              '2 GPU tier at 0.14.0 (the heavy component the chain\'s clamped level 4 drew: '
              '13.418 device px at dpr 1, half again wider than Apple\'s)   '
              '3 GPU tier at the candidate (sizeHeavyTapSigma 9 / 9)   '
              '4 CSS tier at the candidate, whose own heavy layer moves 13.800 -> 9.000 CSS px   '
              f'-- both schemes at {args.scale}x, whole canvas at zoom {zoom}, the nested base at '
              f'2x and the centre dot at {zoom4}x again')
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
    out = os.path.join(HERE, f'g2-{args.scale}x.png')
    sheet.save(out)
    print(out, sheet.size, f'{len(rows)} rows')


if __name__ == '__main__':
    main()
