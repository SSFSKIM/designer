"""W42 G0 instrument: scene geometry, backdrops and signed distances (charter Design, "The instrument").

A cell is a backdrop raster, one glass shape placed on the 320x200 canvas and a display scale. This module
builds all three from the same JSON vocabulary the harness reads (`apps/reference-apple/scenes.json` and the
wave-local scenes file the bed stream declares), so a synthetic render and a native capture of one declared
cell share their geometry by construction rather than by transcription.

The backdrop generators replicate `apps/reference-apple/Sources/Backgrounds.swift`. Two details matter and are
easy to get wrong:
- the CoreGraphics kinds (solid, checkerboard, impulse, text-rows) are drawn in a context whose origin is the
  BOTTOM-left, so their first row and column of the pattern sit at the image's bottom edge;
- the arithmetic kinds (split, linear-gradient, synthetic-photo) are evaluated at pixel centres, image-down.
`verify_backgrounds()` checks every committed canonical background byte for byte, so the replica is proved and
not assumed.

The signed distance is the circular-corner rounded rectangle memos B, C and E used. Apple's paths use
continuous corners (`cornerCurve continuous`, memo D §2); the difference is confined to the corners and is
below the deep masks every reader uses, which is recorded as a limit rather than modelled.
"""
import json
import os

import numpy as np
from PIL import Image

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), *(['..'] * 5)))
MAIN_REPO = '/Users/new/Developer/GitHub/designer'
FIXTURES = f'{REPO}/apps/reference-apple/fixtures'
CANON_SCENES = f'{REPO}/apps/reference-apple/scenes.json'
CANVAS = (320.0, 200.0)

_CANON = json.load(open(CANON_SCENES))
BACKGROUNDS = {k: v for k, v in _CANON['backgrounds'].items() if not k.startswith('$')}
COMPONENTS = {k: v for k, v in _CANON['components'].items() if not k.startswith('$')}
# H's unseen span (charter Design, "The bed", H): s = 112, t = 0.5. The bed stream owns its exact size and
# radius; this placeholder keeps rrect-lg's radius-to-short-side ratio (34 / 160) so synthetic renders exist
# before the bed's scenes file does, and `load_scenes()` replaces it with the declared one.
COMPONENTS.setdefault('rrect-112', {'kind': 'rrect', 'size': [196, 112], 'radius': 23.8})


def load_scenes(path):
    """Merge a wave-local scenes file's backgrounds and components over the canonical ones; return its scenes."""
    spec = json.load(open(path))
    BACKGROUNDS.update({k: v for k, v in spec.get('backgrounds', {}).items() if not k.startswith('$')})
    COMPONENTS.update({k: v for k, v in spec.get('components', {}).items() if not k.startswith('$')})
    return spec.get('scenes', [])


# ---------------------------------------------------------------- backdrops (Backgrounds.swift, replicated)

def _cg_fill(img, rgb, x, y, w, h):
    """CGContext.fill of a rect in a bottom-left-origin bitmap with antialiasing off. CoreGraphics sets every
    pixel the rect touches (the text-rows bars end at fractional x, which is how this rule was established:
    centre sampling misses 24-96 px per text raster, the touched rule matches every raster byte for byte)."""
    H, W = img.shape[:2]
    x0, x1 = int(np.floor(x + 1e-9)), int(np.ceil(x + w - 1e-9))
    y0, y1 = int(np.floor(y + 1e-9)), int(np.ceil(y + h - 1e-9))
    x0, x1 = max(0, x0), min(W, x1)
    y0, y1 = max(0, y0), min(H, y1)
    if x1 <= x0 or y1 <= y0:
        return
    img[H - y1:H - y0, x0:x1] = rgb


def _photo_channel(x, y, k, p):
    v = (0.42 + 0.26 * np.sin(x / 47.0 + k * 1.7 + p) + 0.18 * np.sin(y / 31.0 - k * 2.3 + p * 0.5)
         + 0.11 * np.sin((x + y) / 17.0 + k * 0.9) + 0.07 * np.sin((x - 2 * y) / 9.0 - k * 1.1)
         + 0.05 * np.sin(x / 5.0 + y / 6.0 + k))
    # Swift's .rounded() is half away from zero; v * 255 is non-negative after the clamp.
    return np.clip(np.floor(v * 255 + 0.5), 0, 255)


def render_background(spec, scale, canvas=CANVAS):
    """One background at `scale` as uint8 HxWx3 (encoded sRGB), identical to the harness's raster."""
    if isinstance(spec, str):
        spec = BACKGROUNDS[spec]
    W, H = int(round(canvas[0] * scale)), int(round(canvas[1] * scale))
    kind = spec['kind']
    if kind in ('split', 'linear-gradient', 'synthetic-photo'):
        ys, xs = np.mgrid[0:H, 0:W].astype(np.float64)
        if kind == 'split':
            coord = ((xs if spec['axis'] == 'x' else ys) + 0.5) / scale
            out = np.where((coord < spec['position'])[..., None], np.array(spec['from']), np.array(spec['to']))
            return out.astype(np.uint8)
        if kind == 'linear-gradient':
            a = spec['angle'] * np.pi / 180
            nx, ny = np.cos(a), np.sin(a)
            ext = abs(nx) * canvas[0] + abs(ny) * canvas[1]
            px = (xs + 0.5) / scale - canvas[0] / 2
            py = (ys + 0.5) / scale - canvas[1] / 2
            t = np.clip(0.5 + (px * nx + py * ny) / ext, 0, 1)[..., None]
            v = np.array(spec['from'], float) * (1 - t) + np.array(spec['to'], float) * t
            return np.floor(v + 0.5).astype(np.uint8)
        p = (spec['seed'] % 1000) / 1000.0 * 2 * np.pi
        x, y = xs / scale, ys / scale
        return np.stack([_photo_channel(x, y, k, p) for k in (0, 1.9, 3.7)], -1).astype(np.uint8)
    img = np.zeros((H, W, 3), np.uint8)
    if kind == 'solid':
        img[:] = spec['srgb']
    elif kind == 'checkerboard':
        c = spec['cell'] * scale
        img[:] = spec['b']
        row, y = 0, 0.0
        while y < H:
            col, x = 0, 0.0
            while x < W:
                if (row + col) % 2 == 0:
                    _cg_fill(img, spec['a'], x, y, c, c)
                x += c
                col += 1
            y += c
            row += 1
    elif kind == 'impulse':
        img[:] = spec['background']
        s, gap = spec['size'] * scale, spec['spacing'] * scale
        y = gap / 2
        while y < H:
            x = gap / 2
            while x < W:
                # Swift: (x - s/2).rounded(), half away from zero; operands are non-negative here.
                _cg_fill(img, spec['foreground'], np.floor(x - s / 2 + 0.5), np.floor(y - s / 2 + 0.5), s, s)
                x += gap
            y += gap
    elif kind == 'text-rows':
        img[:] = spec['background']
        rh, bh, margin = spec['rowHeight'] * scale, spec['barHeight'] * scale, 12.0 * scale
        y, row = margin, 0
        while y + bh <= H - margin:
            frac = 0.55 + 0.4 * ((row * 7 + 3) % 10) / 10.0
            _cg_fill(img, spec['foreground'], margin, y, (W - 2 * margin) * frac, bh)
            y += rh
            row += 1
    else:
        raise ValueError(f'unknown background kind {kind!r}')
    return img


def verify_backgrounds():
    """Byte identity of the replica against every committed canonical background PNG (both scales)."""
    rows = []
    for name, spec in BACKGROUNDS.items():
        for s in (1, 2):
            p = f'{FIXTURES}/backgrounds/{name}@{s}x.png'
            if not os.path.exists(p):
                continue
            ref = np.asarray(Image.open(p).convert('RGB'))
            got = render_background(spec, s)
            rows.append((name, s, ref.shape == got.shape and bool(np.array_equal(ref, got)),
                         int((ref != got).any(-1).sum()) if ref.shape == got.shape else -1))
    return rows


# ---------------------------------------------------------------- shapes

def shape_frame(comp, canvas=CANVAS):
    """(cx, cy, w, h, r) in canvas CSS px for a single-shape component (SceneSpec.swift `frame(in:)`)."""
    if isinstance(comp, str):
        comp = COMPONENTS[comp]
    if comp['kind'] not in ('capsule', 'capsule-circular', 'rrect'):
        raise ValueError(f"the instrument reads single shapes only, not {comp['kind']!r}")
    w, h = comp['size']
    if comp.get('position') is not None:
        cx, cy = comp['position']
    else:
        off = comp.get('offset') or [0, 0]
        cx, cy = canvas[0] / 2 + off[0], canvas[1] / 2 + off[1]
    r = min(w, h) / 2 if comp['kind'].startswith('capsule') else comp['radius']
    return cx, cy, w, h, r


def rrect_sdf_pt(X, Y, cx, cy, w, h, r):
    """Signed distance (CSS px, negative inside) of a circular-corner rounded rectangle at points X, Y (CSS px)."""
    qx = np.abs(X - cx) - (w / 2 - r)
    qy = np.abs(Y - cy) - (h / 2 - r)
    return np.hypot(np.maximum(qx, 0), np.maximum(qy, 0)) + np.minimum(np.maximum(qx, qy), 0) - r


def sdf(comp, scale, canvas=CANVAS):
    """Signed distance in CSS px at every device-pixel centre of the canvas."""
    cx, cy, w, h, r = shape_frame(comp, canvas)
    W, H = int(round(canvas[0] * scale)), int(round(canvas[1] * scale))
    ys, xs = np.mgrid[0:H, 0:W].astype(np.float64)
    return rrect_sdf_pt((xs + 0.5) / scale, (ys + 0.5) / scale, cx, cy, w, h, r)


def span(comp):
    if isinstance(comp, str):
        comp = COMPONENTS[comp]
    return float(min(comp['size']))


def size_t(s):
    """The one size variable of memo D: t = clamp((s - 64) / 96, 0, 1); above 160 the declared clamp."""
    return float(min(max((s - 64.0) / 96.0, 0.0), 1.0))


def backdrop_texel_dev(comp):
    """Device px per backdrop texel: 2 at both display scales, 4 on rrect-lg (memo D §3, §4; memo E Q1).
    The dumps place the scale step between rrect-ml (224x128) and rrect-lg (280x160) without saying whether
    span or area sets it (charter Risks). A shape at or beyond rrect-lg's size takes 4; anything smaller 2."""
    if isinstance(comp, str):
        comp = COMPONENTS[comp]
    w, h = comp['size']
    return 4 if (w >= 280 and h >= 160) else 2


W709 = np.array([0.2126, 0.7152, 0.0722])


def luma(img):
    img = np.asarray(img, np.float64)
    return img @ W709 if img.ndim == 3 else img


if __name__ == '__main__':
    bad = [r for r in verify_backgrounds() if not r[2]]
    for r in verify_backgrounds():
        print(f'{r[0]:22s} @{r[1]}x  identical={r[2]}  differing px={r[3]}')
    print('ALL IDENTICAL' if not bad else f'{len(bad)} MISMATCHES')
