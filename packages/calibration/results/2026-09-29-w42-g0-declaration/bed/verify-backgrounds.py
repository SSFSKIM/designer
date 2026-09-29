#!/usr/bin/env python3.12
"""Check the side bundle's non-captured background rasters against the W42 declaration.

Usage: verify-backgrounds.py <dir holding the harness `backgrounds` output> [--out FILE]

The side bundle's `backgrounds` command (no window, no ScreenCaptureKit, no grant) loads and
validates scenes-w42-body.json and writes one PNG per background per scale. This script:

1. re-renders every solid, checkerboard, impulse and split background independently in
   numpy, following Backgrounds.swift (CoreGraphics fills from the BOTTOM-left, integer
   rects, antialiasing off; per-pixel arithmetic for splits at pixel centres), and requires
   byte equality at 1x and 2x;
2. requires the synthetic photo and every background whose declaration equals a canonical
   one to decode byte-identically to the canonical fixture raster (the bridges' identity);
3. reads every declared patch and step back from the raster itself: the patch count, its
   centre against bed.json's patchCentre, and the step's column against stepX;
4. recomputes family E's Rec.709 luma on codes.

These are generated sRGB rasters, not ScreenCaptureKit observations.
"""
import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
from PIL import Image

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]
CANONICAL = ROOT / 'apps/reference-apple'


def swift_round(v):
    """Swift's Double.rounded(): to nearest, ties away from zero."""
    return float(np.sign(v) * np.floor(abs(v) + 0.5))


def render(spec, canvas, scale):
    w, h = int(round(canvas['width'] * scale)), int(round(canvas['height'] * scale))
    out = np.zeros((h, w, 3), np.uint8)
    kind = spec['kind']
    if kind == 'solid':
        out[:] = spec['srgb']
    elif kind == 'split':
        coord = (np.arange(w if spec['axis'] == 'x' else h) + 0.5) / scale
        mask = coord < spec['position']
        colours = np.where(mask[:, None], np.array(spec['from'], np.uint8), np.array(spec['to'], np.uint8))
        if spec['axis'] == 'x':
            out[:] = colours[None, :, :]
        else:
            out[:] = colours[:, None, :]
    elif kind == 'checkerboard':
        c = spec['cell'] * scale
        if c != int(c):
            raise ValueError('non-integer device cell: the independent renderer assumes integer rects')
        c = int(c)
        j = (h - 1 - np.arange(h))[:, None] // c      # CoreGraphics row, from the bottom
        i = np.arange(w)[None, :] // c
        even = (i + j) % 2 == 0
        out[:] = np.where(even[..., None], np.array(spec['a'], np.uint8), np.array(spec['b'], np.uint8))
    elif kind == 'impulse':
        out[:] = spec['background']
        s, gap = spec['size'] * scale, spec['spacing'] * scale
        y = gap / 2
        while y < h:
            x = gap / 2
            while x < w:
                x0, y0 = int(swift_round(x - s / 2)), int(swift_round(y - s / 2))
                rows = slice(max(0, h - (y0 + int(s))), max(0, h - y0))
                cols = slice(max(0, x0), max(0, x0 + int(s)))
                out[rows, cols] = spec['foreground']
                x += gap
            y += gap
    else:
        return None
    return out


def read(path):
    with Image.open(path) as image:
        return np.asarray(image.convert('RGB'))


def components(mask):
    """Axis-aligned bounding boxes of 4-connected regions (patches are squares)."""
    seen = np.zeros_like(mask, bool)
    boxes = []
    for y, x in zip(*np.nonzero(mask)):
        if seen[y, x]:
            continue
        stack, ys, xs = [(y, x)], [], []
        seen[y, x] = True
        while stack:
            cy, cx = stack.pop()
            ys.append(cy); xs.append(cx)
            for ny, nx in ((cy + 1, cx), (cy - 1, cx), (cy, cx + 1), (cy, cx - 1)):
                if 0 <= ny < mask.shape[0] and 0 <= nx < mask.shape[1] and mask[ny, nx] and not seen[ny, nx]:
                    seen[ny, nx] = True
                    stack.append((ny, nx))
        boxes.append((min(ys), max(ys), min(xs), max(xs)))
    return boxes


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('backgrounds', type=Path)
    ap.add_argument('--out', type=Path)
    args = ap.parse_args()
    spec = json.loads((HERE / 'scenes-w42-body.json').read_text())
    bed = json.loads((HERE / 'bed.json').read_text())
    canonical = json.loads((CANONICAL / 'scenes.json').read_text())
    canon_by_decl = {}
    for cid, c in canonical['backgrounds'].items():
        decl = json.dumps({k: v for k, v in c.items() if not k.startswith('$')}, sort_keys=True)
        canon_by_decl[decl] = cid
    canvas = spec['canvas']
    rows, problems = [], []
    for scale in (1, 2):
        for bid, b in sorted(spec['backgrounds'].items()):
            path = args.backgrounds / f'{bid}@{scale}x.png'
            got = read(path)
            row = dict(background=bid, scale=scale, kind=b['kind'], png=path.name,
                       sha256=hashlib.sha256(path.read_bytes()).hexdigest(), shape=list(got.shape))
            want = render(b, canvas, scale)
            if want is not None:
                row['independentRender'] = bool(np.array_equal(got, want))
                if not row['independentRender']:
                    problems.append(f'{bid}@{scale}x differs from the independent render at '
                                    f'{int((got != want).any(-1).sum())} px')
            twin = canon_by_decl.get(json.dumps(b, sort_keys=True))
            if twin is not None:
                ref = read(CANONICAL / 'fixtures/backgrounds' / f'{twin}@{scale}x.png')
                row['canonicalTwin'] = twin
                row['canonicalPixelsIdentical'] = bool(np.array_equal(got, ref))
                if not row['canonicalPixelsIdentical']:
                    problems.append(f'{bid}@{scale}x differs from canonical {twin}')
            elif want is None:
                problems.append(f'{bid}: no independent check for kind {b["kind"]}')
            rows.append(row)
    # Read the declared geometry back from the rasters.
    geometry = []
    for cid, cell in sorted(bed['cells'].items()):
        g = cell['geometry']
        b = spec['backgrounds'][cell['background']]
        for scale in (1, 2):
            if not any(k.startswith(f'{scale}x-') for k in cell['passes']):
                continue
            img = read(args.backgrounds / f'{cell["background"]}@{scale}x.png').astype(int)
            if 'patchSize' in g and b['kind'] == 'impulse':
                fg = np.array(b['foreground'])
                boxes = components((img == fg).all(-1))
                centres = [((x0 + x1 + 1) / 2 / scale, (y0 + y1 + 1) / 2 / scale) for y0, y1, x0, x1 in boxes]
                sizes = {((x1 - x0 + 1) / scale, (y1 - y0 + 1) / scale) for y0, y1, x0, x1 in boxes}
                record = dict(cell=cid, scale=scale, patches=len(boxes), sizes=sorted(sizes))
                if sizes != {(g['patchSize'], g['patchSize'])}:
                    problems.append(f'{cid}@{scale}x: patch sizes {sizes}')
                if g.get('patchesInCanvas') == 1 and len(boxes) != 1:
                    problems.append(f'{cid}@{scale}x: {len(boxes)} patches where one is declared')
                if 'patchCentre' in g:
                    want = tuple(g['patchCentre'])
                    record['patchCentreRead'] = [c for c in centres if c == want]
                    if want not in centres:
                        problems.append(f'{cid}@{scale}x: no patch at the declared centre {want}; read {centres[:4]}')
                    rel = [want[0] - g['shapeCentre'][0], want[1] - g['shapeCentre'][1]]
                    if rel != g['patchFromShapeCentre']:
                        problems.append(f'{cid}: patchFromShapeCentre {g["patchFromShapeCentre"]} != {rel}')
                    half = [s / 2 for s in spec['components'][cell['component']]['size']]
                    depth = min(half[0] - abs(rel[0]), half[1] - abs(rel[1]))
                    record['depthRead'] = depth
                    if depth != g['depth']:
                        problems.append(f'{cid}: declared depth {g["depth"]}, geometry gives {depth}')
                    # Nearest other patch, for the grid cells.
                    others = [((c[0] - want[0]) ** 2 + (c[1] - want[1]) ** 2) ** 0.5 for c in centres if c != want]
                    record['nearestOtherPatch'] = min(others) if others else None
                geometry.append(record)
            if 'stepX' in g:
                row0 = img[img.shape[0] // 2]
                change = [x for x in range(1, row0.shape[0]) if (row0[x] != row0[x - 1]).any()]
                read_x = [c / scale for c in change]
                geometry.append(dict(cell=cid, scale=scale, stepXRead=read_x))
                if read_x != [g['stepX']]:
                    problems.append(f'{cid}@{scale}x: step read at {read_x}, declared {g["stepX"]}')
    luma = {name: [round(0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2], 4) for c in pair]
            for name, pair in bed['levels']['isoluminant']['pairs'].items()}
    result = dict(schema='w42-backgrounds-verification-1',
                  scenesSha256=hashlib.sha256((HERE / 'scenes-w42-body.json').read_bytes()).hexdigest(),
                  backgrounds=len(spec['backgrounds']), rasters=len(rows),
                  independentlyRendered=sum(1 for r in rows if r.get('independentRender')),
                  canonicalTwins=sum(1 for r in rows if r.get('canonicalPixelsIdentical')),
                  isoluminantLuma709OnCodes=luma, problems=problems, rows=rows, geometry=geometry)
    text = json.dumps(result, indent=1) + '\n'
    if args.out:
        args.out.write_text(text)
    print(json.dumps({k: v for k, v in result.items() if k not in ('rows', 'geometry')}, indent=1))
    raise SystemExit(1 if problems else 0)


if __name__ == '__main__':
    main()
