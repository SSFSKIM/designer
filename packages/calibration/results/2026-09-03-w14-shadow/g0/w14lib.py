"""W14 G0 measurement library: the outer shadow read as an affine map of the backdrop.

Everything here is analysis. No constant under `packages/**/src` is touched, no profile is edited and
nothing is captured; the only inputs are committed native fixtures, committed backdrop rasters, the
committed web captures, the two committed probe beds and (for the 1x probe's pitch rasters) the
scratch background set the W9 probe was generated from.

Lengths are CSS px unless a name says device px; a capture at scale s has s device px per CSS px.
Captures and plates are read as linear luminance (Rec.709 of sRGB-decoded channels), the space the
reference's own averaging was measured in (claims 5.31) and the space the shadow axis normalises in
(claims 5.12).

The instrument. For a cell:

  * the declared component region is the union of the rounded rects `scenes.json` declares, placed by
    `placeComponent`'s rule (centre on the canvas, then the shape's own offset) — never read off the
    image (claims 5.12's bounding rule);
  * `d` is the exact signed distance to that union in CSS px, positive OUTSIDE;
  * every exterior pixel is classified by the NORMAL of the nearest declared rect — `below`, `above`,
    `left`, `right`, or `corner` when the nearest point is on a corner arc (the corner class is kept
    and reported separately rather than folded into a side);
  * rings are 0-3, 3-6, 6-12, 12-24, 24-48 CSS px of `d`;
  * per side x ring the capture is fitted as y = a*bg + c in linear luminance by least squares over
    the ring's pixels, with a, c, R^2, n recorded, and the plain occlusion ratio
    mean((bg - y)/bg) over the pixels whose backdrop clears the shadow axis's 0.05 floor recorded
    beside it.

On a constant backdrop a and c are not separable: the design matrix's two columns are collinear, so
`fit_affine` reports `identifiable: False` and gives the level (mean y) and the implied combination
a*bg + c instead. That is said, never smoothed over.

Run from the repository root with the analysis venv:
    /Users/new/.claude/jobs/5c70e47f/tmp/venv/bin/python \
        packages/calibration/results/2026-09-03-w14-shadow/g0/g0_*.py
"""
import json
import math
import os

import numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter

ROOT = os.environ.get('VITREA_ROOT', '/Users/new/Developer/GitHub/designer')
FIX = f'{ROOT}/apps/reference-apple/fixtures'
BG_FIX = f'{FIX}/backgrounds'
WEB = f'{ROOT}/packages/calibration/web-captures'
PROBE = {
    1: f'{ROOT}/packages/calibration/results/2026-09-02-w9-probe/apple-macos-26.5-1x-light-standard',
    2: (f'{ROOT}/packages/calibration/results/2026-09-03-w12-lens/probe-2x/'
        'apple-macos-26.5-2x-light-standard'),
}
PROBE_BG = {
    1: '/Users/new/.claude/jobs/5c70e47f/tmp/w9-probe-fixtures/backgrounds',
    2: f'{ROOT}/packages/calibration/results/2026-09-03-w12-lens/probe-2x/backgrounds',
}
OUT = f'{ROOT}/packages/calibration/results/2026-09-03-w14-shadow/g0'
PARTS = f'{OUT}/parts'

CANVAS = (320, 200)  # CSS px, from scenes.json

# ---------------------------------------------------------------- W8's shadow, as landed

W8_SIGMA = 15.55
W8_OFFSET = 7.95
W8_SPREAD = 3.1
W8_OCCLUSION = 0.285
SRGB_EXP = 2.4

# The reference's own inputs, claims 5.50 2 (span laws).
def apple_shadow_amount(span):      return min(0.625 * span, 75.0)
def apple_shadow_height(span):      return 0.4 * span
def apple_shadow_blur_radius(span): return 40.0 if span > 64 else 0.0
def apple_shadow_opacity(span):     return min(0.5, 0.5 - (span - 48.0) / 448.0)
def apple_vibrancy(span):           return min(max((span - 64.0) / 96.0, 0.0), 1.0)
def apple_sdr_opacity(span):        return 0.08 + (span - 48.0) / 700.0

# The thin material's shadow fill alpha by backdrop, claims 5.50 2's adaptation table.
APPLE_THIN_SHADOW_ALPHA = {
    'impulse': None, 'dark-solid': None, 'mid-dark-solid': 0.30, 'photo': 0.285,
    'checkerboard': 0.278, 'hc-text': 0.278, 'light-solid': 0.05,
}
APPLE_BACKDROP_MEAN_L = {  # scenes.json's measured table, linear light
    'impulse': 0.003750, 'dark-solid': 0.011711, 'mid-dark-solid': 0.059511,
    'photo': 0.214065, 'checkerboard': 0.500000, 'hc-text': 0.740031, 'light-solid': 0.890969,
}


def outer_shadow_alpha(occlusion=W8_OCCLUSION):
    """`outerShadowAlpha` in material.ts: the compositing-space alpha for a linear occlusion."""
    occ = min(1.0, max(0.0, occlusion))
    return 1.0 - (1.0 - occ) ** (1.0 / SRGB_EXP)


def outer_shadow_falloff(d, sigma=W8_SIGMA):
    """`outerShadowFalloff` in material.ts, the tanh form of the Gaussian CDF. d outside the shape."""
    x = -np.asarray(d, dtype=np.float64) / max(sigma, 1e-4)
    return 0.5 * (1.0 + np.tanh(0.7978845608028654 * (x + 0.044715 * x ** 3)))


# ---------------------------------------------------------------- colour


def srgb_to_lin(c):
    return np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)


def load_rgb_lin(path):
    """The image as LINEAR RGB, HxWx3."""
    return srgb_to_lin(np.asarray(Image.open(path).convert('RGB')).astype(np.float64) / 255.0)


def luma_of(lin):
    return 0.2126 * lin[..., 0] + 0.7152 * lin[..., 1] + 0.0722 * lin[..., 2]


_img_cache = {}


def image_lin(path):
    if path not in _img_cache:
        _img_cache[path] = load_rgb_lin(path)
    return _img_cache[path]


def image_luma(path):
    return luma_of(image_lin(path))


_srgb_cache = {}


def image_srgb(path):
    """The image as ENCODED sRGB in 0..1 — the domain both tiers composite the shadow in."""
    if path not in _srgb_cache:
        _srgb_cache[path] = np.asarray(Image.open(path).convert('RGB')).astype(np.float64) / 255.0
    return _srgb_cache[path]


# ---------------------------------------------------------------- the bed


_scenes = None


def scenes():
    global _scenes
    if _scenes is None:
        with open(f'{ROOT}/apps/reference-apple/scenes.json') as fh:
            _scenes = json.load(fh)
    return _scenes


def component_spec(name):
    return scenes()['components'][name]


def radius_of(shape):
    if shape['kind'] == 'capsule':
        return min(shape['size']) / 2.0
    return shape.get('radius', 0.0)


def place_component(name):
    """`placeComponent`'s rule, in CSS px: list of (cx, cy, halfW, halfH, radius) on the canvas."""
    spec = component_spec(name)
    cw, ch = CANVAS
    out = []
    if spec['kind'] == 'group':
        items = spec['items']
        spacing = spec['spacing']
        total = sum(i['size'][0] for i in items) + spacing * (len(items) - 1)
        height = max(i['size'][1] for i in items)
        top = round((ch - height) / 2)
        left = round((cw - total) / 2)
        for item in items:
            w, h = item['size']
            t = top + round((height - h) / 2)
            out.append((left + w / 2, t + h / 2, w / 2, h / 2, radius_of(item)))
            left += w + spacing
        return out
    shapes = [spec['base'], spec['over']] if spec['kind'] == 'stack' else [spec]
    for shape in shapes:
        w, h = shape['size']
        ox, oy = shape.get('offset', [0, 0])
        left = round((cw - w) / 2) + ox
        top = round((ch - h) / 2) + oy
        out.append((left + w / 2, top + h / 2, w / 2, h / 2, radius_of(shape)))
    return out


def span_of(name):
    """The shorter side of the component's primary shape, CSS px — the span every law keys on."""
    shapes = place_component(name)
    return min(min(2 * s[2], 2 * s[3]) for s in shapes) if name == 'toolbar-group' \
        else min(2 * shapes[0][2], 2 * shapes[0][3])


SIDES = ('below', 'above', 'left', 'right', 'corner')
RINGS = ((0.0, 3.0), (3.0, 6.0), (6.0, 12.0), (12.0, 24.0), (24.0, 48.0), (0.0, 6.0))
RING_LABELS = ('0-3', '3-6', '6-12', '12-24', '24-48', '0-6')
"""The charter's five rings, plus the 0-6 ring claims 5.60 3 reported its lift on, so this
instrument's readings and the ledger's can be put side by side without re-binning either."""


def _grid(scale):
    W, H = CANVAS[0] * scale, CANVAS[1] * scale
    ys, xs = np.mgrid[0:H, 0:W]
    return (xs + 0.5) / scale, (ys + 0.5) / scale  # pixel centres, CSS px


def _rrect_parts(x, y, shape):
    cx, cy, hw, hh, r = shape
    qx = np.abs(x - cx) - (hw - r)
    qy = np.abs(y - cy) - (hh - r)
    d = np.hypot(np.maximum(qx, 0), np.maximum(qy, 0)) + np.minimum(np.maximum(qx, qy), 0) - r
    return d, qx, qy


_geom_cache = {}


def geometry(comp, scale, shapes=None):
    """(d, side) for a component: d CSS px positive outside, side an index into SIDES."""
    key = (comp, scale)
    cacheable = shapes is None
    if cacheable and key in _geom_cache:
        return _geom_cache[key]
    shapes = shapes if shapes is not None else place_component(comp)
    x, y = _grid(scale)
    ds, qxs, qys = [], [], []
    for shape in shapes:
        d, qx, qy = _rrect_parts(x, y, shape)
        ds.append(d); qxs.append(qx); qys.append(qy)
    D = np.stack(ds)
    which = np.argmin(D, axis=0)
    d = np.take_along_axis(D, which[None], 0)[0]
    QX = np.take_along_axis(np.stack(qxs), which[None], 0)[0]
    QY = np.take_along_axis(np.stack(qys), which[None], 0)[0]
    CX = np.array([s[0] for s in shapes])[which]
    CY = np.array([s[1] for s in shapes])[which]
    side = np.full(d.shape, SIDES.index('corner'), dtype=np.int8)
    flat = ~((QX > 0) & (QY > 0))
    horiz = flat & (QX >= QY)
    vert = flat & (QX < QY)
    side[horiz & (x < CX)] = SIDES.index('left')
    side[horiz & (x >= CX)] = SIDES.index('right')
    side[vert & (y < CY)] = SIDES.index('above')
    side[vert & (y >= CY)] = SIDES.index('below')
    if cacheable:
        _geom_cache[key] = (d, side)
    return d, side


def ring_side_mask(d, side, ring, side_name):
    lo, hi = ring
    m = (d >= lo) & (d < hi)
    if side_name is not None:
        m &= (side == SIDES.index(side_name))
    return m


# ---------------------------------------------------------------- fits


MIN_N = 32
"""Fewer pixels than this in a ring x side cell and the fit is not reported: the canvas runs out
before the outer rings do on the large spans, and a fit on a handful of pixels describes the corner
of the frame rather than the shadow."""

MIN_BG_STD = 0.02
"""Linear-luminance standard deviation of the backdrop under the mask beneath which `a` and `c` are
not separable. The checkerboard's own std over a ring is ~0.5 and `photo`'s ~0.15; a solid's is 0."""


def fit_affine(y, bg):
    """y ~ a*bg + c by least squares. Returns a dict; `identifiable` False on a flat backdrop."""
    n = int(y.size)
    if n < MIN_N:
        return dict(n=n, identifiable=False, reason='too-few-samples')
    s = float(bg.std())
    level = float(y.mean())
    bgm = float(bg.mean())
    if s < MIN_BG_STD:
        return dict(n=n, identifiable=False, reason='flat-backdrop', bg_std=s,
                    bg_mean=bgm, level=level, ratio=(level / bgm if bgm > 1e-9 else float('nan')))
    X = np.stack([bg, np.ones_like(bg)], 1)
    coef, *_ = np.linalg.lstsq(X, y, rcond=None)
    res = y - X @ coef
    ss = float(np.sum((y - y.mean()) ** 2))
    return dict(n=n, identifiable=True, a=float(coef[0]), c=float(coef[1]),
                rms=float(np.sqrt(np.mean(res ** 2))),
                r2=(1.0 - float(res @ res) / ss if ss > 0 else float('nan')),
                bg_std=s, bg_mean=bgm, level=level)


def fit_pair(Y_lin, BG_lin, Y_enc, BG_enc, m):
    """The affine fit in BOTH spaces over the same pixels, and which space it is affine in.

    vitrea composites its shadow in the canvas's ENCODED space, so a black multiply is EXACTLY
    affine there (c = 0 to the last digit, a = 1 - alpha*F) and only approximately affine in linear
    light. The reference's own compositing space is not known from the layer tree, and the two fits
    answer different questions, so both are recorded on every ring: `lin` is the space the charter
    binds and the shadow axis normalises in, `enc` is the space claims 5.60 3's +0.039 was read in
    (encoded Rec.709 luma) and the space a `box-shadow` and a premultiplied canvas composite in.
    """
    lin = fit_affine(Y_lin[m], BG_lin[m])
    enc = fit_affine(Y_enc[m], BG_enc[m])
    lin['occlusion'] = occlusion_ratio(Y_lin[m], BG_lin[m])
    return dict(lin=lin, enc=enc)


def occlusion_ratio(y, bg, floor=0.05):
    """The shadow axis's quantity: mean (bg - y)/bg over pixels whose backdrop clears the floor."""
    m = bg >= floor
    if m.sum() < MIN_N:
        return None
    return float(np.mean((bg[m] - y[m]) / bg[m]))


def profile_cell(Y, BG, d, side, sides=SIDES, rings=RINGS, labels=RING_LABELS):
    """The instrument, per side x ring. Returns {side: {ring_label: {...}}} plus an 'all' side."""
    out = {}
    for side_name in list(sides) + ['all']:
        rows = {}
        for ring, label in zip(rings, labels):
            m = ring_side_mask(d, side, ring, None if side_name == 'all' else side_name)
            if side_name == 'all':
                m &= (side != SIDES.index('corner'))
            y, bg = Y[m], BG[m]
            rec = fit_affine(y, bg)
            rec['occlusion'] = occlusion_ratio(y, bg)
            rows[label] = rec
        out[side_name] = rows
    return out


# ---------------------------------------------------------------- W8's own prediction


def w8_falloff_field(comp, scale, sigma=W8_SIGMA, offset=W8_OFFSET, spread=W8_SPREAD, shapes=None):
    """F(x, y): W8's blurred-edge falloff of the component's silhouette, offset down and outset.

    The shader samples the distance field at (x, y - offset) and evaluates
    `outer_shadow_falloff(d - spread, sigma)`, which is exactly the silhouette translated DOWN by
    `offset`, outset by `spread`, and blurred by a Gaussian of standard deviation `sigma`.
    """
    shapes = shapes if shapes is not None else place_component(comp)
    x, y = _grid(scale)
    ds = [_rrect_parts(x, y - offset, s)[0] for s in shapes]
    d = np.min(np.stack(ds), axis=0)
    return outer_shadow_falloff(d - spread, sigma)


def w8_predicted_capture(bg_srgb, F, occlusion=W8_OCCLUSION, quantise=True):
    """The capture vitrea's GPU tier produces over this backdrop, as LINEAR luminance.

    Both tiers paint a pure BLACK layer at `outerShadowAlpha(occlusion) * F` and the composite lands
    in the canvas's ENCODED space, so the ENCODED backdrop keeps (1 - alpha_enc*F) of itself. The
    linear-light multiplier is therefore NOT (1 - alpha_enc*F)^2.4: sRGB's decode carries the 0.055
    offset, so the linear factor is srgb_to_lin(e*(1 - alpha_enc*F)) / srgb_to_lin(e) and depends on
    the backdrop's own encoded level e. Predicting the composite in the encoded domain and decoding
    it is exact and needs no such factor at all.

    Measured on this bed: reading vitrea's white checkerboard squares in the ENCODED domain recovers
    alpha_enc = 0.1302 against `outerShadowAlpha(0.285)` = 0.13045, while the pure-power form would
    have said the linear amplitude was 0.271 rather than 0.285 — a 5% phantom, which is the whole
    reason this function works in the encoded domain.
    """
    alpha = outer_shadow_alpha(occlusion)
    enc = bg_srgb * (1.0 - alpha * F[..., None])
    if quantise:
        enc = np.round(enc * 255.0) / 255.0
    return luma_of(srgb_to_lin(enc))


def w8_linear_factor_charter(F, occlusion=W8_OCCLUSION):
    """The charter's stated form of the same model: a linear-light multiply 1 - occlusion*F.

    Exact at F = 0 and F = 1 and within 0.001 of the encoded composite in between on this bed."""
    return 1.0 - occlusion * F


def predict_affine_from(y_pred, bg, mask):
    """The (a, c) the instrument WOULD report for a known predicted capture."""
    return fit_affine(y_pred[mask], bg[mask])


def predict_affine(a_pix, bg, mask):
    """The (a, c) the instrument WOULD report for a known per-pixel multiplier field.

    A ring is not one distance, so a per-pixel model a(d) projects onto the ring's affine fit rather
    than equalling it. Regressing the model's own output a(d)*bg on bg over the same mask is the
    apples-to-apples prediction, and it removes the ring-width caveat from the comparison.
    """
    y = a_pix[mask] * bg[mask]
    return fit_affine(y, bg[mask])


# ---------------------------------------------------------------- paths


def native_path(profile, scene):
    return f'{FIX}/{profile}/{scene}.png'


def web_path(profile, scene, renderer='webgpu'):
    return f'{WEB}/{profile}/{scene}/{scene}__{renderer}.png'


def backdrop_path(backdrop, scale):
    return f'{BG_FIX}/{backdrop}@{scale}x.png'


def probe_path(scene, scale):
    return f'{PROBE[scale]}/{scene}.png'


def probe_backdrop_path(backdrop, scale):
    return f'{PROBE_BG[scale]}/{backdrop}@{scale}x.png'


def profile_key(scale, scheme='light', a11y='standard'):
    return f'apple-macos-26.5-{scale}x-{scheme}-{a11y}'


def scene_parts(scene):
    backdrop, comp, state = scene.split('__')
    return backdrop, comp, state


def has_native(profile, scene):
    return os.path.exists(native_path(profile, scene))


def has_web(profile, scene, renderer='webgpu'):
    return os.path.exists(web_path(profile, scene, renderer))


PITCH = {'checkerboard-4': 4, 'checkerboard-8': 8, 'checkerboard': 16, 'checkerboard-32': 32,
         'checkerboard-64': 64}


def blur_css(P, sigma_css, scale):
    """Gaussian of a plate, sigma given in CSS px and applied in device px."""
    s = sigma_css * scale
    return gaussian_filter(P, s, mode='nearest') if s > 1e-6 else P


def dump(name, obj):
    os.makedirs(PARTS, exist_ok=True)
    path = f'{PARTS}/{name}.json'
    with open(path, 'w') as fh:
        json.dump(obj, fh, indent=1, sort_keys=True, default=float)
    return path


def fmt(v, nd=4):
    if v is None or (isinstance(v, float) and math.isnan(v)):
        return '—'
    return f'{v:.{nd}f}'
