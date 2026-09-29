"""W42 G0 instrument: the synthetic bed the clause-2 proofs render on (charter Design, "The bed").

The bed stream owns the declared ids and levels (its wave-local scenes file). The proofs need the geometry
before that file exists, so this module transcribes the charter's family table into cells with the same
shapes, spans, pitches, levels, polarities and offsets. `from_scenes(path)` builds the same cells from the
bed stream's file instead, and every proof takes `--scenes` so the proofs can be re-run on the declared ids
at integration with no code change.

Two placements the harness vocabulary cannot express at every depth (one 8-pt patch under an rrect-lg at
the canvas centre; a patch at a chosen depth) use a synthetic `patch` kind: one square, integer-aligned at
both scales. It carries the same geometry the bed realises with `impulse` plus a shape `position`, and only
the synthetic proofs render it. H is not rendered here: the instrument is never tuned on the holdout's
geometry.
"""
import numpy as np

import geometry as G
import forward as F

def checker(a, b, pitch):
    return {'kind': 'checkerboard', 'cell': pitch, 'a': [a] * 3, 'b': [b] * 3}


def solid(g):
    return {'kind': 'solid', 'srgb': [g] * 3}


def split(lo, hi, position):
    return {'kind': 'split', 'from': [lo] * 3, 'to': [hi] * 3, 'axis': 'x', 'position': position}


def patch(fg, bg, size, cx, cy):
    return {'kind': 'patch', 'foreground': [fg] * 3, 'background': [bg] * 3, 'size': size, 'center': [cx, cy]}


_orig_render = G.render_background


def _render(spec, scale, canvas=G.CANVAS):
    if isinstance(spec, dict) and spec.get('kind') == 'patch':
        W, H = int(round(canvas[0] * scale)), int(round(canvas[1] * scale))
        img = np.empty((H, W, 3), np.uint8)
        img[:] = spec['background']
        cx, cy = spec['center']
        s2 = spec['size'] / 2
        x0, x1 = int(round((cx - s2) * scale)), int(round((cx + s2) * scale))
        y0, y1 = int(round((cy - s2) * scale)), int(round((cy + s2) * scale))
        img[y0:y1, x0:x1] = spec['foreground']
        return img
    return _orig_render(spec, scale, canvas)


G.render_background = _render

PAIRS = {'P1': (0, 255), 'P2': (48, 208), 'P3': (96, 160), 'P4': (16, 112), 'P5': (144, 240)}
# Family E's isoluminant hue pairs (Rec.709 luma of the encoded values within 0.5 code of 128); the bed
# stream names the declared pair and its matched luma, these only give the synthetic proof a hue axis.
CHROMA = {'E1': ([214, 105, 104], [48, 149, 157]), 'E2': ([108, 143, 40], [150, 114, 200])}


def _comp(name, dx=0.0):
    c = dict(G.COMPONENTS[name])
    if dx:
        c['offset'] = [dx, 0.0]
    return c


def spec_2x(pose, scheme='light'):
    """[(id, family letter, background spec, component spec)] per 2x pass, the charter's families B-E."""
    act = pose == 'rest'
    rows = []
    for nm in ('P2', 'P3', 'P4', 'P5'):
        a, b = PAIRS[nm]
        for p in (16, 64):
            rows.append((f'B:{nm}-p{p}:md', 'B', checker(a, b, p), _comp('rrect-md')))
    bp = [(8, 'capsule-button'), (32, 'capsule-button'), (64, 'capsule-button'), (8, 'rrect-ml'),
          (32, 'rrect-ml'), (64, 'rrect-ml'), (32, 'rrect-64'), (32, 'rrect-80'), (8, 'rrect-lg'), (32, 'rrect-lg')]
    for p, comp in bp:
        if not act and p == 8:
            continue
        rows.append((f"B':P1-p{p}:{comp}", "B'", checker(0, 255, p), _comp(comp)))
    # C: single patches at the shape centre (160, 100) unless a depth is named; both polarities.
    for S in (8, 32):
        for fg, bg in ((255, 0), (0, 255)):
            rows.append((f'C:S{S}-{fg}on{bg}:md', 'C', patch(fg, bg, S, 160, 100), _comp('rrect-md')))
    for fg, bg in ((255, 0), (0, 255)):
        rows.append((f'C:S16-{fg}on{bg}:capsule', 'C', patch(fg, bg, 16, 160, 100), _comp('capsule-button')))
    for depth_name, x in (('s/4', 160 - 80 + 24), ('4pt', 160 - 80 + 4 + 4)):
        rows.append((f'C:S8-depth{depth_name}:md', 'C', patch(255, 0, 8, x, 100), _comp('rrect-md')))
    for depth_name, x in (('ctr', 160), ('s/4', 160 - 140 + 40), ('4pt', 160 - 140 + 4 + 4)):
        rows.append((f'C:S8-depth{depth_name}:lg', 'C', patch(255, 0, 8, x, 100), _comp('rrect-lg')))
    imp = {'kind': 'impulse', 'background': [0, 0, 0], 'foreground': [255, 255, 255], 'size': 4, 'spacing': 64}
    rows.append(('C:impulse:ml', 'C', imp, _comp('rrect-ml')))
    rows.append(('C:impulse:lg', 'C', imp, _comp('rrect-lg')))
    # D: the step under the interior at shape offset delta (the step sits delta pt left of the centre).
    deltas = (0, 32) + (() if act else (12,))
    for dl in deltas:
        for lo, hi in ((0, 255), (255, 0)):
            rows.append((f'D:step-d{dl}-{lo}to{hi}:md', 'D', split(lo, hi, 160 - dl), _comp('rrect-md')))
    rows.append(('D:step-d0:capsule', 'D', split(0, 255, 160), _comp('capsule-button')))
    if not act:
        rows.append(('D:step-d12:capsule', 'D', split(0, 255, 160 - 12), _comp('capsule-button')))
    for out in (8, 16):
        for lo, hi in ((0, 255), (255, 0)):
            rows.append((f'D:step-out{out}-{lo}to{hi}:md', 'D', split(lo, hi, 160 - 80 - out), _comp('rrect-md')))
    if act:
        for lo, hi in ((0, 255), (255, 0)):
            rows.append((f'D:step-d0-{lo}to{hi}:lg', 'D', split(lo, hi, 160), _comp('rrect-lg')))
    for nm, (a, b) in CHROMA.items():
        for p in (16, 64):
            rows.append((f'E:{nm}-p{p}:md', 'E', {'kind': 'checkerboard', 'cell': p, 'a': a, 'b': b},
                         _comp('rrect-md')))
    return rows


def spec_1x(pose):
    rows = []
    for p in (4, 8):
        rows.append((f'1x:P1-p{p}:capsule', "B'", checker(0, 255, p), _comp('capsule-button')))
    rows.append(('1x:P1-p4-odd:capsule', "B'", checker(0, 255, 4), _comp('capsule-button', dx=1.0)))
    rows.append(('1x:P1-p4:md', "B'", checker(0, 255, 4), _comp('rrect-md')))
    for p in (4, 8, 16):
        rows.append((f'1x:P1-p{p}:lg', "B'", checker(0, 255, p), _comp('rrect-lg')))
    imp = {'kind': 'impulse', 'background': [0, 0, 0], 'foreground': [255, 255, 255], 'size': 4, 'spacing': 64}
    rows.append(('1x:impulse:lg', 'C', imp, _comp('rrect-lg')))
    rows.append(('1x:step-out8:md', 'D', split(0, 255, 160 - 80 - 8), _comp('rrect-md')))
    return rows


def cells(ep, scale=2, letters=None, ids=None, rgb=False):
    scheme, pose = ep.split('-')
    rows = spec_2x(pose, scheme) if scale == 2 else spec_1x(pose)
    out = []
    for cid, letter, bg, comp in rows:
        if letters and letter not in letters:
            continue
        if ids and cid not in ids:
            continue
        is_rgb = rgb or letter == 'E'
        out.append(F.Cell(f'{scale}x|{cid}', bg, comp, scale, scheme, pose, rgb=is_rgb))
        out[-1].letter = letter
    return out


def from_scenes(path, ep, scale):
    """Cells from the bed stream's wave-local scenes file (at integration)."""
    scheme, pose = ep.split('-')
    out = []
    for sc in G.load_scenes(path):
        if sc.get('state', 'rest') != pose and not sc['id'].endswith(pose):
            continue
        comp = G.COMPONENTS[sc['component']]
        if comp['kind'] not in ('capsule', 'capsule-circular', 'rrect'):
            continue
        out.append(F.Cell(f'{scale}x|{sc["id"]}', sc['background'], sc['component'], scale, scheme, pose))
    return out
