#!/usr/bin/env python3.12
"""W39 body and edge readers (charter v2 clause 7, "The edge law", X25; c9a §5.184).

W37 G0b's per-side reader (`2026-09-25-w37-g0b-edge-identification/canonical.py`)
generalised, never edited in place:

- positions come from each surface's ATTESTED supplied `frameOrigin` and size, never
  from a centred declaration; a supplied path is what SwiftUI handed the fill or
  material, not an attestation of the window server's raster phase;
- a circular capsule is its exact stadium; every other kind (the radius-22
  continuous rrect, W34's continuous capsule and radius-12 rectangle) is solved
  against its supplied path, flattened by W34's `instrument.segments` (chord error
  <= 1/1024 CSS px), so no circular corner is substituted for a continuous one;
- a `column` has one path, one body and one set of bins per member; a pixel belongs
  to the member whose contour is nearest;
- shells are one DEVICE pixel wide from -14*scale inward through +4*scale outward
  (the declaration's required range; wider exterior reach is a diagnostic option);
  top/bottom/left/right straights are separate; arcs use W37's 16 nearest-normal
  bins of 22.5 degrees; top/bottom pairs are read at equal depth from ONE image;
- an interior shell admits only whole pixels (all four corners inside) and an
  exterior shell only pixels wholly outside, so a pixel straddling the path is the
  separate `boundary` stratum and never silently joins a shell;
- a required bin that is absent or holds fewer than four pixels is listed as
  UNMEASURED with its reason, never dropped;
- opaque coverage is calibrated separately, from the opaque control's own deep fill
  and its own exterior (or the no-glass reference): nothing about the ordinary
  fill's registration is transferred to the glass path.

Everything here takes arrays and attested metadata; payload access belongs to the
guarded role readers (W34's `wave.Reader`, W39's wave reader). The one W34 adapter
at the bottom opens payloads only through `wave.Reader` at its default roles,
calibration and validation, so W34's spent holdout is refused before any byte.
"""
import base64
import gzip
import importlib.util
import json
import math
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
W34 = HERE.parent / '2026-09-23-w34-g0-contour-bed'
W34_SITTING = HERE.parent / '2026-09-23-w34-g1-contour-sitting'
SIDES = ('top', 'bottom', 'left', 'right')
INNER_CSS = 14
OUTER_CSS = 4
DEEP_CSS = 6
MIN_POPULATION = 4
WHOLE_RADIUS = math.sqrt(.5)  # the farthest pixel corner from its centre, device px


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


I = _load('w39_w34_instrument', W34 / 'instrument.py')


# --------------------------------------------------------------------------- shapes

@dataclass(frozen=True)
class Shape:
    kind: str
    size: tuple          # CSS px, fractional kept
    frame_origin: tuple  # CSS px, image-down, top-left of the surface's frame
    elements: tuple = ()
    opaque: bool = False

    @property
    def circular(self): return self.kind == 'capsule-circular'

    def rect(self, scale, translation=(0, 0)):
        o = np.asarray(self.frame_origin, float) * scale + np.asarray(translation, float)
        return np.array([*o, *(o + np.asarray(self.size, float) * scale)])


def shapes_of(component):
    """The attested surfaces of a declared component with its supplied paths merged.

    Accepts a single shape, a `column` (`items` + two supplied paths) or `none`.
    The declared size must equal the supplied rect's: a disagreement means the
    manifest and the declaration describe different surfaces, which is refused.
    """
    kind = component['kind']
    if kind == 'none': return []
    items = component['items'] if kind == 'column' else [component]
    paths = component.get('suppliedPaths')
    if not paths or len(paths) != len(items):
        raise ValueError('every surface needs its attested supplied path')
    shapes = []
    for item, path in zip(items, paths):
        size = tuple(float(v) for v in path['rect'][2:4])
        if tuple(float(v) for v in item['size']) != size:
            raise ValueError('declared size disagrees with the supplied path rect')
        if path.get('kind', item['kind']) != item['kind']:
            raise ValueError('declared kind disagrees with the supplied path')
        shapes.append(Shape(item['kind'], size, tuple(float(v) for v in path['frameOrigin']),
                            tuple(json.dumps(e, sort_keys=True) for e in path.get('elements', [])),
                            bool(path.get('opaque', item.get('opaque', False)))))
    return shapes


def _elements(shape): return [json.loads(e) for e in shape.elements]


def straight_extents(shape, scale, translation=(0, 0)):
    """Device-px extent along each side's straight run, or None where a side is all curve."""
    x0, y0, x1, y1 = shape.rect(scale, translation)
    out = {}
    if shape.circular:
        r = min(shape.size) / 2 * scale
        horizontal = (x0 + r, x1 - r) if x1 - x0 > 2 * r + 1e-9 else None
        vertical = (y0 + r, y1 - r) if y1 - y0 > 2 * r + 1e-9 else None
        return dict(top=horizontal, bottom=horizontal, left=vertical, right=vertical)
    origin = np.asarray(shape.frame_origin, float) * scale + np.asarray(translation, float)
    runs = {s: None for s in SIDES}
    for a, b, arc in I.segments(_elements(shape)):
        if arc: continue
        a = a * scale + origin; b = b * scale + origin
        for side, axis, edge in [('top', 1, y0), ('bottom', 1, y1), ('left', 0, x0), ('right', 0, x1)]:
            if abs(a[axis] - edge) < 1e-9 and abs(b[axis] - edge) < 1e-9:
                lo, hi = sorted([a[1 - axis], b[1 - axis]])
                if hi - lo > 1e-9:
                    runs[side] = (lo, hi) if runs[side] is None else (min(lo, runs[side][0]), max(hi, runs[side][1]))
    return runs


# ------------------------------------------------------------------------- geometry

def _path_field(q, shape, scale, translation):
    """Signed distance, outward normal and curve flag of points q against the supplied path."""
    origin = np.asarray(shape.frame_origin, float) * scale + np.asarray(translation, float)
    nearest = np.full(len(q), np.inf); signed = np.zeros(len(q))
    normal = np.zeros((len(q), 2)); curve = np.zeros(len(q), bool)
    for a, b, is_arc in I.segments(_elements(shape)):
        a = a * scale + origin; b = b * scale + origin; v = b - a
        t = np.clip(((q - a) @ v) / (v @ v), 0, 1)
        delta = q - (a + t[:, None] * v)
        distance = np.hypot(delta[:, 0], delta[:, 1])
        outward = np.array([v[1], -v[0]]) / np.linalg.norm(v)
        update = distance < nearest
        nearest[update] = distance[update]
        signed[update] = distance[update] * np.where(delta[update] @ outward >= 0, 1, -1)
        normal[update] = outward; curve[update] = is_arc
    return signed, normal[:, 0], normal[:, 1], curve


_CACHE = {}


def _member_field(hw, shape, scale, translation):
    key = (hw, shape, scale, tuple(translation))
    if key in _CACHE: return _CACHE[key]
    h, w = hw
    x0, y0, x1, y1 = shape.rect(scale, translation)
    y, x = np.mgrid[:h, :w].astype(float)
    if shape.circular:
        radius = min(shape.size) / 2 * scale
        d, nx, ny, arc = I.stadium(x + .5, y + .5, [x0, y0, x1, y1], radius)
        corners = [I.stadium(x + dx, y + dy, [x0, y0, x1, y1], radius)[0] for dx, dy in
                   [(0, 0), (0, 1), (1, 0), (1, 1)]]
        whole = np.logical_and.reduce([c <= 0 for c in corners])
        outside = np.logical_and.reduce([c >= 0 for c in corners])
    else:
        # A coarse stadium classifies pixels far from the contour; every pixel within
        # reach of a shell, of the deep boundary or of a transect is solved exactly.
        radius = min(shape.size) / 2 * scale
        d, nx, ny, arc = I.stadium(x + .5, y + .5, [x0, y0, x1, y1], radius)
        reach = (max(INNER_CSS, DEEP_CSS) + 2) * scale + 2
        band = (x + .5 > x0 - reach) & (x + .5 < x1 + reach) & (y + .5 > y0 - reach) & (y + .5 < y1 + reach)
        yy, xx = np.nonzero(band)
        s, sx, sy, sa = _path_field(np.column_stack((xx + .5, yy + .5)), shape, scale, translation)
        d = d.copy(); nx = nx.copy(); ny = ny.copy(); arc = arc.copy()
        d[yy, xx] = s; nx[yy, xx] = sx; ny[yy, xx] = sy; arc[yy, xx] = sa
        # The distance field is 1-Lipschitz: a centre deeper than half a diagonal proves
        # every corner inside. On an exact axis-aligned straight, half a pixel does.
        axis = (np.maximum(abs(nx), abs(ny)) > 1 - 1e-10) & ~arc
        whole = (d <= -WHOLE_RADIUS) | (axis & (d <= -.5 + 1e-10))
        outside = (d >= WHOLE_RADIUS) | (axis & (d >= .5 - 1e-10))
    angle = np.floor(np.mod(np.arctan2(ny, nx), 2 * np.pi) / (2 * np.pi / 16) + .5).astype(int) % 16
    side = np.full((h, w), -1)
    straight = ~arc & (np.maximum(abs(nx), abs(ny)) > 1 - 1e-10)
    for i, (sx, sy) in enumerate([(0, -1), (0, 1), (-1, 0), (1, 0)]):
        side[straight & (np.rint(nx) == sx) & (np.rint(ny) == sy)] = i
    _CACHE[key] = (d, nx, ny, arc, angle, whole, outside, side)
    return _CACHE[key]


@dataclass
class Geometry:
    shapes: list
    scale: int
    d: np.ndarray        # signed distance to the nearest member, device px, negative inside
    nx: np.ndarray
    ny: np.ndarray
    arc: np.ndarray
    angle: np.ndarray    # W37's 16 nearest-normal bins; 12 is the top normal, 4 the bottom
    whole: np.ndarray    # all four corners inside
    outside: np.ndarray  # all four corners outside
    side: np.ndarray     # 0..3 = SIDES on exact straights, -1 elsewhere
    member: np.ndarray   # index of the nearest member


def geometry(hw, shapes, scale, translation=(0, 0)):
    """Per-pixel fields for the attested surfaces. `translation` stays zero for W39:
    positions are attested, and per-run registration is never fitted (charter clause 7)."""
    if not shapes: raise ValueError('a no-glass component has no geometry')
    fields = [_member_field(tuple(hw), s, scale, tuple(translation)) for s in shapes]
    member = np.argmin(np.stack([f[0] for f in fields]), axis=0)
    pick = lambda k: np.choose(member, [f[k] for f in fields])
    return Geometry(list(shapes), scale, pick(0), pick(1), pick(2), pick(3).astype(bool), pick(4),
                    pick(5).astype(bool), pick(6).astype(bool), pick(7), member)


# ----------------------------------------------------------------------- statistics

def deep_body(rgb, geo, member=0):
    """Per-channel median at d <= -6 CSS px, at least four pixels, else UNMEASURED."""
    mask = (geo.member == member) & (geo.d <= -DEEP_CSS * geo.scale)
    values = np.asarray(rgb, float)[mask]
    if len(values) < MIN_POPULATION:
        return dict(status='UNMEASURED', reason='deep population below four', pixels=int(len(values)),
                    medianRGB=None, minimumRGB=None, maximumRGB=None)
    return dict(status='measured', pixels=int(len(values)), medianRGB=np.median(values, 0).tolist(),
                minimumRGB=values.min(0).tolist(), maximumRGB=values.max(0).tolist())


def _shell(geo):
    return np.floor(geo.d + 1e-12).astype(int)  # shell s holds s <= d < s+1


def edge_bins(geo, member=0, inner_css=INNER_CSS, outer_css=OUTER_CSS, min_population=MIN_POPULATION):
    """Every required bin of one member, measured or explicitly UNMEASURED.

    Returns (bins, labels): each bin is a dict and `labels` maps every pixel to its
    bin's index (-1 for none), so a reader never rebuilds a mask per bin.
    """
    s = geo.scale
    shells = list(range(-inner_css * s, outer_css * s))
    shell = _shell(geo)
    mine = geo.member == member
    admitted = np.where(geo.d < 0, geo.whole, geo.outside) & mine
    labels = np.full(geo.d.shape, -1)
    bins = []

    def add(part, key, sh, mask, **extra):
        count = int(mask.sum())
        info = dict(member=member, part=part, shell=sh, depthCss=-(sh + .5) / s, pixels=count,
                    admissible=count >= min_population, **key, **extra)
        info['status'] = 'measured' if info['admissible'] else 'UNMEASURED'
        if not info['admissible']:
            info['reason'] = 'absent bin' if count == 0 else 'population below four'
        labels[mask] = len(bins)
        bins.append(info)

    for sh in shells:
        at = admitted & (shell == sh)
        for i, side in enumerate(SIDES):
            add('straight', dict(side=side, bin=[12, 4, 8, 0][i]), sh, at & (geo.side == i))
        for a in range(16):
            add('arc', dict(side=None, bin=a), sh, at & (geo.side < 0) & (geo.angle == a))
    # Pixels straddling the path belong to no shell; they are counted, per side, so
    # that a phase or registration change that moves them is visible.
    straddle = mine & ~geo.whole & ~geo.outside & (abs(geo.d) < 2)
    for i, side in enumerate(SIDES):
        m = straddle & (geo.side == i)
        bins.append(dict(member=member, part='boundary', side=side, bin=[12, 4, 8, 0][i], shell=None,
                         depthCss=None, pixels=int(m.sum()), admissible=False, status='DIAGNOSTIC',
                         reason='partial coverage; never a closure bin'))
        labels[m & (labels < 0)] = len(bins) - 1
    return bins, labels


def read_bins(rgb, bins, labels, deep):
    """Mean, minimum and maximum RGB per bin and the excess over the member's deep median."""
    rgb = np.asarray(rgb, float).reshape(-1, 3); flat = labels.ravel()
    keep = flat >= 0; idx = flat[keep]; values = rgb[keep]
    n = np.bincount(idx, minlength=len(bins)).astype(float)
    sums = np.stack([np.bincount(idx, values[:, c], minlength=len(bins)) for c in range(3)], 1)
    order = np.argsort(idx, kind='stable'); sorted_idx = idx[order]; sorted_values = values[order]
    starts = np.searchsorted(sorted_idx, np.arange(len(bins)))
    deepRGB = None if deep is None or deep.get('medianRGB') is None else np.asarray(deep['medianRGB'])
    out = []
    for k, info in enumerate(bins):
        row = dict(info)
        if n[k]:
            block = sorted_values[starts[k]:starts[k] + int(n[k])]
            mean = sums[k] / n[k]
            row.update(meanRGB=mean.tolist(), minimumRGB=block.min(0).tolist(), maximumRGB=block.max(0).tolist(),
                       excessRGB=None if deepRGB is None else (mean - deepRGB).tolist())
        else:
            row.update(meanRGB=None, minimumRGB=None, maximumRGB=None, excessRGB=None)
        out.append(row)
    return out


def paired(read, a='top', b='bottom'):
    """Equal-depth pairs of two straight sides of one member, from one image.

    UNMEASURED unless both sides' bins at that shell are measured. The difference is
    a - b per channel; the depths are equal by construction (one shell index).
    """
    sides = {(r['member'], r['side'], r['shell']): r for r in read if r['part'] == 'straight'}
    out = []
    for (member, side, sh), ra in sorted(sides.items(), key=lambda kv: (kv[0][0], kv[0][2])):
        if side != a: continue
        rb = sides[(member, b, sh)]
        row = dict(member=member, shell=sh, depthCss=ra['depthCss'], pair=[a, b],
                   pixels=[ra['pixels'], rb['pixels']])
        if ra['status'] == 'measured' and rb['status'] == 'measured':
            row.update(status='measured', meanRGB=[ra['meanRGB'], rb['meanRGB']],
                       differenceRGB=(np.asarray(ra['meanRGB']) - rb['meanRGB']).tolist())
        else:
            row.update(status='UNMEASURED', reason='a side is absent or below population at this depth',
                       meanRGB=[ra['meanRGB'], rb['meanRGB']], differenceRGB=None)
        out.append(row)
    return out


def paired_arcs(read):
    """Vertical mirror pairs of arc bins (angle a against 16 - a) at equal depth."""
    arcs = {(r['member'], r['bin'], r['shell']): r for r in read if r['part'] == 'arc'}
    out = []
    for (member, a, sh), ra in sorted(arcs.items()):
        if not 8 < a < 16: continue  # upward normals (image y negative) paired with their mirror
        rb = arcs[(member, 16 - a, sh)]
        ok = ra['status'] == 'measured' and rb['status'] == 'measured'
        out.append(dict(member=member, shell=sh, depthCss=ra['depthCss'], bins=[a, 16 - a],
                        pixels=[ra['pixels'], rb['pixels']], status='measured' if ok else 'UNMEASURED',
                        differenceRGB=(np.asarray(ra['meanRGB']) - rb['meanRGB']).tolist() if ok else None))
    return out


# ----------------------------------------------------------------- opaque coverage

def opaque_coverage(rgb, background_rgb, fill_rgb):
    """Per-pixel coverage alpha = <rgb-bg, fill-bg>/|fill-bg|^2, unclipped.

    Unclipped on purpose: a mis-stated fill or background shows as alpha outside
    [0, 1] instead of being hidden by a clamp.
    """
    rgb = np.asarray(rgb, float); bg = np.broadcast_to(np.asarray(background_rgb, float), rgb.shape)
    contrast = np.asarray(fill_rgb, float) - bg
    norm = np.sum(contrast * contrast, -1)
    if np.any(norm < 1): raise ValueError('opaque fill and background have no usable contrast')
    return np.sum((rgb - bg) * contrast, -1) / norm


def calibrate_opaque(opaque_rgb, geo, background_rgb=None, member=0):
    """The ordinary fill's own levels: deep fill median and exterior (or no-glass) level."""
    o = np.asarray(opaque_rgb, float)
    deep = deep_body(o, geo, member)
    if background_rgb is None:
        far = (geo.d >= (OUTER_CSS + 2) * geo.scale)
        background = np.median(o[far], 0); source = 'opaque exterior median beyond 6 CSS px'
    else:
        background = np.asarray(background_rgb, float); source = 'no-glass reference per pixel'
    return dict(fillRGB=deep['medianRGB'], fillPixels=deep['pixels'], background=background,
                backgroundSource=source)


APEX_TOLERANCE = 1 / 16  # device px an apex line's path may fall short of the extreme tangent


def _extreme_along(shape, scale, side, lines, translation=(0, 0)):
    """For each raster line's centre, the path's extreme coordinate toward `side`.

    Lines are rows for left/right and columns for top/bottom. None where the
    line misses the surface. Circular capsules use their exact arcs; every other
    kind the flattened supplied path.
    """
    x0, y0, x1, y1 = shape.rect(scale, translation)
    across = side in ('left', 'right')
    centres = np.asarray(lines, float) + .5
    out = np.full(len(centres), np.nan)
    if shape.circular:
        # A stadium is every point within r of its spine segment.
        r = min(shape.size) / 2 * scale; cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
        spine_x, spine_y = ((x0 + r, x1 - r), (cy, cy)) if x1 - x0 >= y1 - y0 else ((cx, cx), (y0 + r, y1 - r))
        fixed, free = (spine_y, spine_x) if across else (spine_x, spine_y)
        gap = np.maximum(np.maximum(fixed[0] - centres, centres - fixed[1]), 0)
        hit = gap <= r
        reach = np.sqrt(np.maximum(r * r - gap * gap, 0))
        out[hit] = (free[1] + reach if side in ('right', 'bottom') else free[0] - reach)[hit]
        return out
    origin = np.asarray(shape.frame_origin, float) * scale + np.asarray(translation, float)
    axis = 1 if across else 0          # coordinate the line is fixed in
    for p, q, _ in I.segments(_elements(shape)):
        p = p * scale + origin; q = q * scale + origin
        lo, hi = sorted([p[axis], q[axis]])
        hit = (centres >= lo) & (centres <= hi) & (hi > lo)
        if not hit.any(): continue
        t = (centres[hit] - p[axis]) / (q[axis] - p[axis])
        value = p[1 - axis] + t * (q[1 - axis] - p[1 - axis])
        current = out[hit]
        if side in ('right', 'bottom'): out[hit] = np.where(np.isnan(current), value, np.maximum(current, value))
        else: out[hit] = np.where(np.isnan(current), value, np.minimum(current, value))
    return out


def straight_profile(image, shape, scale, side, inner_css=INNER_CSS, outer_css=OUTER_CSS, translation=(0, 0)):
    """Raster lines across one side of one surface, in ABSOLUTE device coordinates.

    `coords` are the raster columns (left/right) or rows (top/bottom) from inner_css
    inside the supplied edge to outer_css outside; `pathEdge` is the supplied edge's
    device coordinate, fractional kept; `inward` is +1 when inward is increasing
    coordinate. `band` lists the lines averaged: in mode 'straight' the side's
    straight run shortened by inner_css at each end (so no line reaches a corner);
    in mode 'apex', for a side with no straight run (the radius-22 rrect's 44-px
    ends), every whole raster line whose centre lies where the supplied path falls
    less than 1/16 device px short of the extreme tangent. `meanRGB` is the band
    mean per coord; `raw` keeps band x coords samples for byte-identity checks.
    An empty band is UNMEASURED, not an exception.
    """
    image = np.asarray(image)
    x0, y0, x1, y1 = shape.rect(scale, translation)
    across = side in ('left', 'right')     # the transect runs along x
    edge = {'left': x0, 'right': x1, 'top': y0, 'bottom': y1}[side]
    inward = 1 if side in ('left', 'top') else -1
    if inward > 0: lo, hi = edge - outer_css * scale, edge + inner_css * scale
    else: lo, hi = edge - inner_css * scale, edge + outer_css * scale
    coords = np.arange(math.floor(lo), math.ceil(hi))
    limit = image.shape[1] if across else image.shape[0]
    coords = coords[(coords >= 0) & (coords < limit)]
    run = straight_extents(shape, scale, translation)[side]
    band = np.array([], int); mode = 'straight'
    if run is not None:
        a, b = run[0] + inner_css * scale, run[1] - inner_css * scale
        band = np.arange(math.floor(a), math.ceil(b))
        band = band[(band + .5 >= a) & (band + .5 <= b)]
    if not len(band):
        mode = 'apex'
        span = (y0, y1) if across else (x0, x1)
        lines = np.arange(math.floor(span[0]), math.ceil(span[1]))
        extreme = _extreme_along(shape, scale, side, lines, translation)
        band = lines[np.isfinite(extreme) & (abs(extreme - edge) < APEX_TOLERANCE)]
    result = dict(side=side, mode=mode, band=band.tolist(), inward=inward, pathEdge=float(edge),
                  coords=coords.tolist())
    if not len(band):
        return dict(result, status='UNMEASURED', reason='no raster line within the straight run or apex tolerance',
                    meanRGB=None, raw=None)
    if across: raw = image[np.ix_(band, coords)]
    else: raw = image[np.ix_(coords, band)].swapaxes(0, 1)
    return dict(result, status='measured', meanRGB=np.asarray(raw, float).mean(0).tolist(), raw=raw)


def coverage_profile(alpha, shape, scale, side, inner_css=INNER_CSS, outer_css=OUTER_CSS, translation=(0, 0)):
    """straight_profile over a coverage map: `meanRGB` holds the band-mean ALPHA per
    coord (one value, not three) and `raw` the float alpha samples; same keys, and
    `measuredEdge`/`offset` from the area integral (see coverage_edge)."""
    profile = straight_profile(np.asarray(alpha, float), shape, scale, side, inner_css, outer_css, translation)
    if profile['status'] == 'measured': profile.update(coverage_edge(profile))
    return profile


def coverage_edge(profile):
    """The fill's measured edge from a coverage profile's area integral, device px.

    Across the lines, sum(alpha) is the covered length; the measured edge minus the
    supplied `pathEdge` is the ordinary fill's registration on that side, which is a
    diagnostic of the fill path only and is never transferred to the glass.
    """
    alpha = np.asarray(profile['meanRGB'], float); coords = np.asarray(profile['coords'])
    if profile['inward'] > 0: edge = coords[-1] + 1 - alpha.sum()
    else: edge = coords[0] + alpha.sum()
    return dict(measuredEdge=float(edge), offset=float(edge - profile['pathEdge']))


def area_average(coords, edge_pos_device, scale, G, inward, quad=8):
    """Per raster line [i, i+1), the mean of G(u_css) by quad-point midpoint quadrature,
    u_css = inward * (x - edge_pos_device) / scale, positive inside. The one place the
    W37 area-integrated model lives; G must be vectorised."""
    u = (np.arange(quad) + .5) / quad
    x = np.asarray(coords, float)[:, None] + u[None, :]
    return np.asarray(G(inward * (x - edge_pos_device) / scale), float).mean(1)


def integrate_ramp(coords, edge, scale, width_css, amplitude=1., inward=1, quad=8):
    """W37's line L_w(t) = max(1 - t/w, 0) for t >= 0 else 0, area-averaged per line."""
    line = lambda t: np.where(t >= 0, np.maximum(1 - t / width_css, 0), 0)
    return amplitude * area_average(coords, edge, scale, line, inward, quad)


# Names the preflight imports (agreed interface).
shape_from_supplied = lambda entry, item=None: shapes_of(
    dict(item or dict(kind=entry['kind'], size=entry['rect'][2:4]), suppliedPaths=[entry]))[0]
shapes_from_supplied = lambda entries, items=None: [shape_from_supplied(e, i) for e, i in
                                                    zip(entries, items or [None] * len(entries))]
paired_top_bottom = lambda read: paired(read, 'top', 'bottom')


# ------------------------------------------------------------------------- analyse

def _json(value):
    if isinstance(value, dict): return {k: _json(v) for k, v in value.items() if not isinstance(v, np.ndarray)}
    if isinstance(value, (list, tuple)): return [_json(v) for v in value]
    if isinstance(value, np.generic): return value.item()
    return value


def analyse(payload):
    """Per-run statistics of one captured cell, JSON-able (the archive producer's call).

    payload: rgb, noGlass, opaque (HxWx3 uint8 full frames; noGlass/opaque may be
    None), component (declared, with the manifest's suppliedPaths merged), scale,
    scheme, pose, backgroundKind. For an opaque cell `rgb` is itself the ordinary
    fill and is read as coverage; for a glass cell `opaque` is its paired control.
    """
    rgb = np.asarray(payload['rgb']); scale = int(payload['scale']); comp = payload['component']
    if rgb.ndim != 3 or rgb.shape[2] != 3: raise ValueError('rgb must be HxWx3')
    no_glass = None if payload.get('noGlass') is None else np.asarray(payload['noGlass'])
    opaque = None if payload.get('opaque') is None else np.asarray(payload['opaque'])
    for name, a in [('noGlass', no_glass), ('opaque', opaque)]:
        if a is not None and a.shape != rgb.shape: raise ValueError(name + ' frame differs from rgb')
    out = dict(schema='w39-readers/1', scale=scale, scheme=payload.get('scheme'), pose=payload.get('pose'),
               backgroundKind=payload.get('backgroundKind'), componentKind=comp['kind'],
               frame=[int(rgb.shape[1]), int(rgb.shape[0])],
               attestation='supplied path origins and sizes; not a raster-phase attestation')
    shapes = shapes_of(comp)
    if no_glass is not None:
        f = no_glass.reshape(-1, 3).astype(float)
        out['noGlassFrame'] = dict(medianRGB=np.median(f, 0).tolist(), minimumRGB=f.min(0).tolist(),
                                   maximumRGB=f.max(0).tolist())
    if not shapes:
        f = rgb.reshape(-1, 3).astype(float)
        out['reference'] = dict(medianRGB=np.median(f, 0).tolist(), minimumRGB=f.min(0).tolist(),
                                maximumRGB=f.max(0).tolist(),
                                identicalToNoGlass=None if no_glass is None else bool(np.array_equal(rgb, no_glass)))
        return out
    geo = geometry(rgb.shape[:2], shapes, scale)
    cell_is_opaque = all(s.opaque for s in shapes)
    out['shapes'] = [dict(kind=s.kind, sizeCss=list(s.size), frameOriginCss=list(s.frame_origin),
                          rectDevice=s.rect(scale).tolist(), opaque=s.opaque,
                          straightRuns={k: (None if v is None else list(v))
                                        for k, v in straight_extents(s, scale).items()}) for s in shapes]
    members = []
    for m, shape in enumerate(shapes):
        bins, labels = edge_bins(geo, m)
        row = dict(member=m)
        if not cell_is_opaque:
            deep = deep_body(rgb, geo, m)
            read = read_bins(rgb, bins, labels, deep)
            row.update(deep=deep, bins=read, topBottom=paired(read), leftRight=paired(read, 'left', 'right'),
                       arcMirror=paired_arcs(read))
            if no_glass is not None:
                row['noGlassBins'] = [dict(part=r['part'], side=r['side'], bin=r['bin'], shell=r['shell'],
                                           meanRGB=r['meanRGB'])
                                      for r in read_bins(no_glass, bins, labels, None)]
                row['noGlassDeep'] = deep_body(no_glass, geo, m)
            row['profiles'] = {side: {k: v for k, v in straight_profile(rgb, shape, scale, side).items()
                                      if k != 'raw'} for side in SIDES}
        control = rgb if cell_is_opaque else opaque
        if control is not None:
            cal = calibrate_opaque(control, geo, no_glass, m)
            if cal['fillRGB'] is None:
                row['coverage'] = dict(status='UNMEASURED', reason='opaque fill population below four')
            else:
                alpha = opaque_coverage(control, cal['background'], cal['fillRGB'])
                cov = read_bins(np.repeat(alpha[..., None], 3, -1), bins, labels, None)
                sides = {}
                for side in SIDES:
                    sides[side] = {k: v for k, v in coverage_profile(alpha, shape, scale, side).items()
                                   if k != 'raw'}
                row['coverage'] = dict(status='measured', source='cell' if cell_is_opaque else 'paired opaque control',
                                       fillRGB=cal['fillRGB'], backgroundSource=cal['backgroundSource'],
                                       backgroundRGB=np.median(np.broadcast_to(cal['background'], control.shape)
                                                               .reshape(-1, 3), 0).tolist(),
                                       bins=[dict(part=r['part'], side=r['side'], bin=r['bin'], shell=r['shell'],
                                                  pixels=r['pixels'], alpha=None if r['meanRGB'] is None else r['meanRGB'][0])
                                             for r in cov],
                                       edges=sides)
        members.append(row)
    out['members'] = members
    required = [b for r in members for b in r.get('bins', []) if b['part'] != 'boundary']
    out['status'] = 'measured' if required and all(b['status'] == 'measured' for b in required) else 'UNMEASURED'
    out['unmeasuredBins'] = sum(b['status'] != 'measured' for b in required)
    return _json(out)


# ------------------------------------------------------------------ W34 adapter

def w34_wave():
    return _load('w39_w34_wave', W34 / 'wave.py').default_wave()


def w34_payload(cell, wave=None):
    """One W34 calibration/validation cell as an `analyse` payload, through the guard.

    `wave.reader` at its default roles refuses holdout before any payload opens. The
    native image is the probe PNG; the component and its supplied path come from the
    first admitted normal run's lossless crop, as W37 read them.
    """
    from PIL import Image
    import io
    wave = wave or w34_wave()
    repeat = wave.reader(W34_SITTING / 'repeat'); probe = wave.reader(W34_SITTING / 'probe')
    crop = json.loads(gzip.decompress(repeat.read(cell, 'crop')))
    run = next(r for r in crop['runs'] if r['admitted'] and r['protocol'] == 'normal')
    p = I.unpack(base64.b64decode(crop['states'][run['state']]))
    native = np.asarray(Image.open(io.BytesIO(probe.read(cell, 'png'))).convert('RGB'))
    profile = cell.split('/')[0]
    # W34's crop carries its paired opaque control (fill 0 on grey-255, whatever the
    # glass cell's backdrop), so the control's own exterior calibrates it, not a no-glass.
    return dict(rgb=native, noGlass=None, opaque=p.get('opaque'), component=p['component'], scale=p['scale'],
                scheme='dark' if '-dark-' in profile else 'light',
                pose='active' if cell.endswith('__rest') else 'inactive',
                backgroundKind=p['backgroundKind'], role=wave.roles[cell.split('/')[1]],
                translationDevicePx=p['alignment']['translationDevicePx'])
