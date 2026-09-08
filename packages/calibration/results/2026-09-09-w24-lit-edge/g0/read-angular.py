"""W24 G0 (a) — the wave's instrument: the rim read AROUND THE WHOLE CONTOUR, binned by the
normal's ANGLE.

W23's `read-contour.py` reads the rim per SIDE, on the straight span, with the corner arcs excluded
by construction; W21's band reader reads one peak per side of the declared box. Both are per-side
readers, and the W24 finding is exactly what a per-side reader cannot see: a light on the 45°
diagonal projects EQUALLY on all four straight sides, so `L−R` and `T−B` are 0 for the reference and
0 for vitrea and the two agree while the corners differ by a factor of seven. The variation lives in
the corner arcs. This reader parametrises the WHOLE boundary and reports the rim as a function of
the direction the contour's normal points in.

## The definition, one place, so every gate of W24 reads the same number

- **the boundary** — the DECLARED shape, from `scenes.json`: the component's size centred on the
  declared canvas and multiplied by the scale, with a capsule's radius `min(w, h) / 2` and a
  rounded rectangle's the declared one. A capsule is two straight spans and two semicircles; a
  rounded rectangle is four straight spans and four quarter arcs. It is sampled at a spacing of
  `--spacing` (0.25) device px, never fewer than `--min-points` (720) points, so that every 22.5°
  bin of every cell of both scales is populated by hundreds of samples.

  The arcs are CIRCULAR, which Apple's continuous corner is not (W23 measured the curvature spread
  to about 1.6 radii). The instrument does not model the squircle; it measures instead how far the
  peak it found sits from the declared contour, per bin (`peakDepth`), and a bin whose peak has run
  to the end of the search window is reported as TRUNCATED rather than as a number. `instrument.txt`
  records that diagnostic on every cell of the read.

- **the body** — W21's and W23's, unchanged: the mean linear Rec.709 luminance over the declared box
  eroded `--erode` (6) CSS px on every side. One number per capture, so that the native fixture and
  the web capture are each measured against their own level.

- **the excess** — at each boundary sample, the MAXIMUM linear luminance along the inward normal
  from `--outside` (1) CSS px outside the declared contour to `--depth` (4) CSS px inside it, minus
  that capture's own body. A peak and not a sum: this reader's question is the AMPLITUDE the edge
  reaches in a given direction, and W23's contour reader already owns the band integral on the
  straight spans (it is reported beside this one, X1).

- **the bins** — sixteen of 22.5°, CENTRED on the compass directions, with the normal's angle
  measured clockwise from straight up in screen coordinates (y down): `N` is the top side's normal,
  `E` the right side's, `SE` the bottom-right diagonal, `NW` the top-left. Centring and not
  edge-aligning them is what makes a rounded rectangle legible: its four straight sides each carry
  exactly one normal direction, and centred bins put each side wholly inside one bin (`N`, `E`, `S`,
  `W`) instead of splitting it across two. The four diagonal bins (`NE`, `SE`, `SW`, `NW`) are then
  the corner arcs' own, which is where the lit edge lives.

- **the verdict per cell** — the ratio of the brightest bin to the dimmest, the compass direction and
  angle of the brightest bin, and the ambient floor as the dimmest bin over the brightest. A rim
  that is a drawn line reads a ratio near 1; a lit one reads the reference's.

Everything is in LINEAR light: the rim is a compositing amplitude and only adds in light.

## The injection test

`--inject` paints a synthetic rim of KNOWN angular profile `A·(a + (1 − a)·|cos(θ − φ)|^p)` one CSS
px deep inside the declared contour and reads it back. Two forms, because they answer two questions:

- `flat` — the contour band of the capture is first replaced by the capture's own body colour, so
  the only edge in the raster is the painted one and the reader must return the painted profile
  exactly. This is the test of the GEOMETRY, THE UNITS AND THE BINNING, and it is run both
  unquantised (the bound is the reader's own arithmetic) and re-encoded to the 8 bits a real capture
  has (the bound is then the BED's resolution at that body level, in codes, and is reported as such).
- `over` — painted onto the untouched capture, and the recovery is `read(after) − read(before)`.
  Where the painted line dominates the cell's own rim this is additive and recovers the profile;
  where it does not, the max is the capture's own and the bin is reported as DOMINATED rather than
  as an error. It is the check that the reader composes on real pixels, not a bound.

Usage:

    read-angular.py --scenes <scenes.json> --fixtures <dir> --profile <key>
                    [--captures <dir> --tier webgpu] [--sets calibration,validation]
                    [--json <out.json>] [--label <text>]
    read-angular.py --parent-compat ...      # the parent's finding reader's window, for the crosscheck
    read-angular.py --inject <capture.png> --scenes ... --profile ... --scene <id>
                    --amplitude 0.05 --inject-out <stem>
"""

import argparse
import hashlib
import json
import math
import os
import sys

import numpy as np
from PIL import Image

# Sixteen bins of 22.5°, centred on the compass directions; index 0 is straight up (the top side's
# outward normal) and the index increases clockwise, so 4 is E, 8 is S and 12 is W.
COMPASS = ("N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE",
           "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW")
NBINS = len(COMPASS)
BIN_DEG = 360.0 / NBINS


def linearise(a: np.ndarray) -> np.ndarray:
    """sRGB EOTF, the same transfer the runtime decodes a backdrop with."""
    a = a / 255.0
    return np.where(a <= 0.04045, a / 12.92, ((a + 0.055) / 1.055) ** 2.4)


def encode(a: np.ndarray) -> np.ndarray:
    """The sRGB OETF; used only by the injection test, which paints in encoded bytes."""
    return np.where(a <= 0.0031308, a * 12.92, 1.055 * np.maximum(a, 0.0) ** (1 / 2.4) - 0.055)


def rgb_of(path: str) -> np.ndarray:
    """8-bit RGB from a PNG, or unquantised RGB from the injection test's `.npy`."""
    if path.endswith(".npy"):
        return np.load(path)
    return np.asarray(Image.open(path).convert("RGB"), dtype=np.float64)


def luma_of_rgb(rgb: np.ndarray) -> np.ndarray:
    c = linearise(rgb)
    return 0.2126 * c[..., 0] + 0.7152 * c[..., 1] + 0.0722 * c[..., 2]


def quantisation_step(level: float) -> float:
    """The linear luminance one 8-bit code is worth at `level` — the bed's resolution there."""
    code = float(encode(np.asarray(level))) * 255.0
    hi = float(linearise(np.asarray(min(code + 0.5, 255.0))))
    lo = float(linearise(np.asarray(max(code - 0.5, 0.0))))
    return hi - lo


def component_geometry(components, name):
    """Size and corner radius in CSS px, or None for a composite with no single box."""
    c = components.get(name)
    if c is None or "size" not in c:
        return None
    w, h = float(c["size"][0]), float(c["size"][1])
    radius = float(c["radius"]) if c["kind"] == "rrect" else min(w, h) / 2.0
    return w, h, radius, c["kind"]


def declared_box(canvas, geom, scale):
    """The declared box in device px: the component centred on the declared canvas, times the scale."""
    w, h, radius, kind = geom
    cx, cy = canvas["width"] / 2.0, canvas["height"] / 2.0
    return ((cx - w / 2.0) * scale, (cy - h / 2.0) * scale,
            (cx + w / 2.0) * scale, (cy + h / 2.0) * scale, radius * scale, kind)


def boundary_points(box, spacing, min_points):
    """The declared boundary, as (x, y, nx, ny, segment) with the OUTWARD unit normal.

    Straight spans first and arcs between them, in the same clockwise order the eye reads: top,
    top-right, right, bottom-right, bottom, bottom-left, left, top-left. A capsule's left and right
    spans are empty by construction (its radius is half its height), so it reduces to two spans and
    two semicircles without a special case.
    """
    x0, y0, x1, y1, r, kind = box
    sx, sy = (x1 - x0) - 2 * r, (y1 - y0) - 2 * r
    if kind == "capsule":
        # The declared radius is half the SHORT side; the long axis keeps its straight spans.
        r = min(x1 - x0, y1 - y0) / 2.0
        sx, sy = (x1 - x0) - 2 * r, (y1 - y0) - 2 * r
    quarter = math.pi / 2.0 * r
    segs = [("top", sx), ("tr", quarter), ("right", sy), ("br", quarter),
            ("bottom", sx), ("bl", quarter), ("left", sy), ("tl", quarter)]
    perimeter = sum(length for _, length in segs)
    n = max(min_points, int(math.ceil(perimeter / spacing)))
    centres = {"tr": (x1 - r, y0 + r, -math.pi / 2.0), "br": (x1 - r, y1 - r, 0.0),
               "bl": (x0 + r, y1 - r, math.pi / 2.0), "tl": (x0 + r, y0 + r, math.pi)}
    pts = []
    for i in range(n):
        s = (i + 0.5) / n * perimeter
        acc = 0.0
        for name, length in segs:
            if length <= 0.0:
                continue
            if s < acc + length:
                u = s - acc
                if name == "top":
                    pts.append((x0 + r + u, y0, 0.0, -1.0, name))
                elif name == "right":
                    pts.append((x1, y0 + r + u, 1.0, 0.0, name))
                elif name == "bottom":
                    pts.append((x1 - r - u, y1, 0.0, 1.0, name))
                elif name == "left":
                    pts.append((x0, y1 - r - u, -1.0, 0.0, name))
                else:
                    cx, cy, a0 = centres[name]
                    a = a0 + u / r
                    pts.append((cx + r * math.cos(a), cy + r * math.sin(a),
                                math.cos(a), math.sin(a), name))
                break
            acc += length
    return pts


def normal_angle(nx, ny):
    """The outward normal's compass angle: 0 straight up, increasing clockwise, screen y down."""
    return math.degrees(math.atan2(nx, -ny)) % 360.0


def angular_read(lum, white, box, scale, body, outside_css, depth_css, step_css, points):
    """Per boundary sample: the peak excess along the inward normal and where it was found.

    Returns parallel arrays (angle°, excess, peakDepth in CSS px inward, segment). The search runs
    from `outside_css` CSS px OUTSIDE the declared contour to `depth_css` CSS px inside it, at
    `step_css` CSS px steps, and reads the nearest pixel — the peak of a one-pixel line is a pixel's
    own value, and interpolating would report a line dimmer than the raster actually carries.
    """
    h, w = lum.shape
    offsets = np.arange(-outside_css, depth_css + 1e-9, step_css)
    angles, excess, depth, segs, clip, band = [], [], [], [], [], []
    for (x, y, nx, ny, seg) in points:
        best, best_at, best_clip, total = -np.inf, float("nan"), False, 0.0
        for t in offsets:
            d = t * scale
            xi = int(math.floor(x - nx * d))
            yi = int(math.floor(y - ny * d))
            if 0 <= yi < h and 0 <= xi < w:
                v = lum[yi, xi]
                # Ties go to the offset NEAREST the declared contour. Consecutive offsets land on
                # the same pixel wherever the step is finer than a device pixel, so a tie broken by
                # scan order would report a peak "outside the contour" that is the very pixel just
                # inside it, and `outsideFraction` — which decides whether a bin is reading the
                # backdrop — would be a reading of the scan's direction.
                if v > best or (v == best and abs(t) < abs(best_at)):
                    best, best_at, best_clip = v, t, bool(white[yi, xi])
                if t >= 0.0:
                    total += (v - body) * step_css
        if not np.isfinite(best):
            continue
        angles.append(normal_angle(nx, ny))
        excess.append(best - body)
        depth.append(best_at)
        segs.append(seg)
        clip.append(best_clip)
        band.append(total)
    return (np.asarray(angles), np.asarray(excess), np.asarray(depth), np.asarray(segs),
            np.asarray(clip), np.asarray(band))


def bin_of(angles):
    return (np.rint(np.asarray(angles) / BIN_DEG).astype(int)) % NBINS


def summarise(angles, excess, depth, segs, clip, band, depth_css):
    """The cell's verdict: the bins, the segments, the ratio, the brightest direction, the floor."""
    b = bin_of(angles)
    bins, counts, truncated, clipped, outside, integral = [], [], [], [], [], []
    for k in range(NBINS):
        m = b == k
        counts.append(int(m.sum()))
        bins.append(float(excess[m].mean()) if m.any() else float("nan"))
        # A bin whose peak sits at the last sample of the window has not been bounded by the reader.
        truncated.append(float((depth[m] >= depth_css - 1e-9).mean()) if m.any() else float("nan"))
        # A bin whose peak pixel is white in all three channels cannot say how much brighter the
        # reference wanted to be; the fit is not allowed to be pulled down to a clipped value.
        clipped.append(float(clip[m].mean()) if m.any() else float("nan"))
        # A bin whose peak was found OUTSIDE the declared contour is reading the backdrop and not
        # the rim. The window reaches 1 CSS px outside so that a rim drawn a fraction of a pixel
        # proud of the declared edge is still caught, and over a backdrop DARKER than the body that
        # costs nothing; over a brighter one it reads the backdrop's own level as a rim of 0.7. The
        # fraction is reported per bin and the fit excludes the bin rather than the reader
        # narrowing a window the wave's design binds.
        outside.append(float((depth[m] < 0.0).mean()) if m.any() else float("nan"))
        # The band INTEGRAL beside the peak, in luminance per CSS px, summed from the declared
        # contour inward. A rasterised curve spreads a one-pixel line over two pixels at partial
        # coverage, so its PEAK falls where a straight edge's does not — the corner arcs of a 1x
        # fixture are read a fifth to two fifths low by any peak reader, which is exactly the
        # scale-dependent corner deficit this wave would otherwise fit a constant to. The integral
        # is conserved under that spreading, and it is W23's own contour quantity, so the two
        # instruments meet on the straight spans.
        integral.append(float(band[m].mean()) if m.any() else float("nan"))
    bins = np.asarray(bins)
    finite = bins[np.isfinite(bins)]
    brightest = int(np.nanargmax(bins))
    dimmest = int(np.nanargmin(bins))
    peak, floor = float(bins[brightest]), float(bins[dimmest])
    segments = {}
    for name in dict.fromkeys(segs.tolist()):
        m = segs == name
        segments[name] = float(excess[m].mean())
    return {
        "bins": [None if not np.isfinite(v) else float(v) for v in bins],
        "counts": counts,
        "truncatedFraction": [None if not np.isfinite(v) else float(v) for v in truncated],
        "clipFraction": [None if not np.isfinite(v) else float(v) for v in clipped],
        "outsideFraction": [None if not np.isfinite(v) else float(v) for v in outside],
        "integral": [None if not np.isfinite(v) else float(v) for v in integral],
        "segments": segments,
        "brightestBin": brightest,
        "brightestCompass": COMPASS[brightest],
        "brightestAngleDeg": brightest * BIN_DEG,
        "dimmestBin": dimmest,
        "dimmestCompass": COMPASS[dimmest],
        "ratio": float(peak / floor) if floor > 1e-6 else float("inf"),
        "ambientFraction": float(floor / peak) if abs(peak) > 1e-9 else float("nan"),
        "peakBin": peak,
        "floorBin": floor,
        "minSample": float(excess.min()),
        "maxSample": float(excess.max()),
        "meanPeakDepthCssPx": float(depth.mean()),
    }


def read_one(path, canvas, geom, erode, outside_css, depth_css, step_css, spacing, min_points):
    rgb = rgb_of(path)
    lum = luma_of_rgb(rgb)
    scale = lum.shape[1] / canvas["width"]
    box = declared_box(canvas, geom, scale)
    x0, y0, x1, y1, _r, _k = box
    e = erode * scale
    yy, xx = np.mgrid[0:lum.shape[0], 0:lum.shape[1]]
    xx = xx + 0.5
    yy = yy + 0.5
    mask = (xx >= x0 + e) & (xx < x1 - e) & (yy >= y0 + e) & (yy < y1 - e)
    body = float(lum[mask].mean())
    white = np.all(rgb >= 254.5, axis=-1)
    pts = boundary_points(box, spacing, min_points)
    angles, excess, depth, segs, clip, band = angular_read(lum, white, box, scale, body,
                                                           outside_css, depth_css, step_css, pts)
    out = summarise(angles, excess, depth, segs, clip, band, depth_css)
    out["body"] = body
    out["scale"] = scale
    out["points"] = len(pts)
    out["quantisationStep"] = quantisation_step(body)
    out["sha256"] = hashlib.sha256(open(path, "rb").read()).hexdigest()[:12] \
        if not path.endswith(".npy") else "npy"
    return out


# ---------------------------------------------------------------------------
# The injection test
# ---------------------------------------------------------------------------

def rounded_box_sdf(box, shape):
    """Signed distance to the declared contour (negative inside) and the outward normal, per pixel."""
    x0, y0, x1, y1, r, kind = box
    if kind == "capsule":
        r = min(x1 - x0, y1 - y0) / 2.0
    cx, cy = (x0 + x1) / 2.0, (y0 + y1) / 2.0
    hx, hy = (x1 - x0) / 2.0, (y1 - y0) / 2.0
    yy, xx = np.mgrid[0:shape[0], 0:shape[1]]
    px = xx + 0.5 - cx
    py = yy + 0.5 - cy
    qx = np.abs(px) - (hx - r)
    qy = np.abs(py) - (hy - r)
    mx = np.maximum(qx, 0.0)
    my = np.maximum(qy, 0.0)
    d = np.hypot(mx, my) - r + np.minimum(np.maximum(qx, qy), 0.0)
    # The gradient: radial in the corner quadrant, axis-aligned along a straight span.
    corner = (qx > 0) & (qy > 0)
    norm = np.maximum(np.hypot(qx, qy), 1e-9)
    nx = np.where(corner, np.sign(px) * qx / norm, np.where(qx > qy, np.sign(px), 0.0))
    ny = np.where(corner, np.sign(py) * qy / norm, np.where(qx > qy, 0.0, np.sign(py)))
    return d, nx, ny


def inject(path, canvas, geom, amplitude, axis_deg, ambient, exponent, flatten, out_path,
           quantise, erode):
    """Paint `A·(a + (1 − a)·|cos(θ − φ)|^p)`, one CSS px deep, inside the declared contour."""
    rgb = rgb_of(path)
    scale = rgb.shape[1] / canvas["width"]
    box = declared_box(canvas, geom, scale)
    lin = linearise(rgb)
    d, nx, ny = rounded_box_sdf(box, rgb.shape[:2])
    if flatten:
        # The capture's own contour band replaced by its own body colour, so the only edge in the
        # raster is the painted one. The eroded body is untouched: the band stops 1 CSS px short of
        # where the erosion begins.
        x0, y0, x1, y1, _r, _k = box
        e = erode * scale
        yy, xx = np.mgrid[0:rgb.shape[0], 0:rgb.shape[1]]
        xx = xx + 0.5
        yy = yy + 0.5
        inner = (xx >= x0 + e) & (xx < x1 - e) & (yy >= y0 + e) & (yy < y1 - e)
        body_rgb = lin[inner].mean(axis=0)
        band = (d > -(erode - 1.0) * scale) & (d < 3.0 * scale)
        lin[band] = body_rgb
    theta = np.degrees(np.arctan2(nx, -ny)) % 360.0
    factor = ambient + (1.0 - ambient) * np.abs(np.cos(np.radians(theta - axis_deg))) ** exponent
    paint = (d <= 0.0) & (d > -1.0 * scale)
    lin[paint] += (amplitude * factor)[paint][:, None]
    encoded = encode(np.clip(lin, 0.0, 1.0)) * 255.0
    if quantise:
        Image.fromarray(np.clip(np.rint(encoded), 0, 255).astype(np.uint8)).save(out_path)
    else:
        np.save(out_path, encoded)
    return out_path


def expected_bin_profile(canvas, geom, scale, amplitude, axis_deg, ambient, exponent,
                         spacing, min_points):
    """What the painted profile is worth in each bin, averaged over the SAME boundary samples.

    Not the profile evaluated at the bin's centre angle: `|cos|` has a kink at its zero, so over
    the 22.5° of the dimmest bin its mean stands 40 % above its centre value, and a reader that
    recovered the painted line perfectly would look 5 codes wrong there. The expectation is
    therefore binned exactly as the read is, from the boundary sample angles themselves.
    """
    box = declared_box(canvas, geom, scale)
    pts = boundary_points(box, spacing, min_points)
    angles = np.asarray([normal_angle(nx, ny) for (_x, _y, nx, ny, _s) in pts])
    values = amplitude * (ambient + (1.0 - ambient)
                          * np.abs(np.cos(np.radians(angles - axis_deg))) ** exponent)
    b = bin_of(angles)
    return [float(values[b == k].mean()) if (b == k).any() else float("nan")
            for k in range(NBINS)]


# ---------------------------------------------------------------------------

def scene_rows(spec, profile, sets):
    which = {}
    for role in ("calibration", "validation", "holdout", "recorded"):
        for sid in spec.get("split", {}).get(role, []):
            which[sid] = role
    declared = None
    for p in spec["profiles"]:
        if p["key"] == profile:
            declared = p.get("scenes")
    ids = [s["id"] for s in spec["scenes"]]
    if isinstance(declared, list):
        ids = [s for s in ids if s in declared]
    wanted = set(sets.split(","))
    return [(sid, which.get(sid, "calibration")) for sid in ids
            if which.get(sid, "calibration") in wanted], which


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--scenes", required=True)
    ap.add_argument("--fixtures", default=None)
    ap.add_argument("--profile", default=None)
    ap.add_argument("--captures", default=None)
    ap.add_argument("--tier", default="webgpu")
    ap.add_argument("--sets", default="calibration,validation,holdout,recorded")
    ap.add_argument("--erode", type=float, default=6.0)
    ap.add_argument("--outside", type=float, default=1.0, help="CSS px outside the contour")
    ap.add_argument("--depth", type=float, default=4.0, help="CSS px inside the contour")
    ap.add_argument("--step", type=float, default=0.25, help="CSS px between samples on the normal")
    ap.add_argument("--spacing", type=float, default=0.25, help="device px between boundary samples")
    ap.add_argument("--min-points", type=int, default=720)
    ap.add_argument("--parent-compat", action="store_true",
                    help="the parent finding reader's window: -1..4 DEVICE px at 0.5 device px, "
                         "720 points binned by arclength rather than by angle")
    ap.add_argument("--json", default=None)
    ap.add_argument("--label", default=None)
    ap.add_argument("--inject", default=None)
    ap.add_argument("--scene", default=None)
    ap.add_argument("--amplitude", type=float, default=0.05)
    ap.add_argument("--axis", type=float, default=315.0, help="the injected axis, compass degrees")
    ap.add_argument("--ambient", type=float, default=0.2)
    ap.add_argument("--exponent", type=float, default=1.0)
    ap.add_argument("--inject-out", default=None)
    args = ap.parse_args()

    spec = json.load(open(args.scenes))
    canvas = spec["canvas"]
    components = spec["components"]

    if args.inject:
        scene = next(s for s in spec["scenes"] if s["id"] == args.scene)
        geom = component_geometry(components, scene["component"])
        stem = args.inject_out or (args.inject + ".injected")
        scale = Image.open(args.inject).size[0] / canvas["width"]
        want = expected_bin_profile(canvas, geom, scale, args.amplitude, args.axis, args.ambient,
                                    args.exponent, args.spacing, args.min_points)
        print(f"injection on {os.path.basename(args.inject)} ({args.scene}); "
              f"A={args.amplitude:.4f} linear, axis {args.axis:.1f}° ({COMPASS[int(round(args.axis / BIN_DEG)) % NBINS]}), "
              f"ambient {args.ambient:.2f}, exponent {args.exponent:.2f}, one CSS px deep")
        for flatten, quantise, suffix, label, bound in (
            (True, False, "-flat-exact.npy", "flat, unquantised (the reader's own arithmetic)", 5e-4),
            (True, True, "-flat-u8.png", "flat, 8-bit (the bed's own resolution)", None),
            (False, True, "-over-u8.png", "over the capture, 8-bit (composition, not a bound)", None),
        ):
            out_path = stem + suffix
            inject(args.inject, canvas, geom, args.amplitude, args.axis, args.ambient,
                   args.exponent, flatten, out_path, quantise, args.erode)
            before = read_one(args.inject, canvas, geom, args.erode, args.outside, args.depth,
                              args.step, args.spacing, args.min_points)
            after = read_one(out_path, canvas, geom, args.erode, args.outside, args.depth,
                             args.step, args.spacing, args.min_points)
            step = quantisation_step(before["body"])
            print(f"  -- {label}: body {before['body']:.5f}; one 8-bit code there is "
                  f"{step:.6f} linear")
            print(f"     {'bin':5s} {'want':>9s} {'before':>9s} {'after':>9s} {'recovered':>10s} "
                  f"{'error':>10s} {'codes':>7s}")
            worst, worst_bin = 0.0, None
            arc_rel, arc_bin = 0.0, None
            for k in range(NBINS):
                b, a = before["bins"][k], after["bins"][k]
                got = a if flatten else a - b
                err = got - want[k]
                dominated = (not flatten) and b > want[k]
                straight = k % (NBINS // 4) == 0
                if not dominated:
                    if straight and abs(err) > worst:
                        worst, worst_bin = abs(err), COMPASS[k]
                    if not straight and abs(err) / max(want[k], 1e-9) > arc_rel:
                        arc_rel, arc_bin = abs(err) / max(want[k], 1e-9), COMPASS[k]
                print(f"     {COMPASS[k]:5s} {want[k]:9.5f} {b:9.5f} {a:9.5f} {got:10.5f} "
                      f"{err:10.5f} {err / step:7.2f}"
                      + ("   DOMINATED by the cell's own rim — excluded" if dominated else ""))
            # The two are reported apart because they are two different quantities. On a STRAIGHT
            # side the painted line lands on whole pixels and what comes back is the reader's own
            # arithmetic, which is what the bound is on. On an ARC the same one-CSS-px line is
            # rasterised across two pixels at partial coverage, so its peak is genuinely lower in
            # the raster than it is in the paint, and the reader returns what the raster holds. That
            # is the instrument's DECLARED LIMIT on the corners and the arcs — a systematic
            # under-read, measured here rather than assumed — and it is why every corner contrast
            # in this gate's tables is a LOWER BOUND on the reference's own.
            print(f"     worst |error| on the four STRAIGHT bins {worst:.6f} at {worst_bin}"
                  + (f"   bound {bound:g}: {'PASS' if worst < bound else 'FAIL'}"
                     if bound is not None else f" ({worst / step:.2f} codes)"))
            print(f"     worst RELATIVE error on the twelve ARC bins {arc_rel * 100:.1f} % at "
                  f"{arc_bin} — the raster's own limit on a curve, not the reader's")
            print(f"     the eroded body must not move: {after['body'] - before['body']:+.9f}")
            print(f"     the recovered axis: brightest bin {after['brightestCompass']} "
                  f"({after['brightestAngleDeg']:.1f}°), ratio {after['ratio']:.2f}, "
                  f"ambient {after['ambientFraction']:.3f}")
        return 0

    profiles = [p["key"] for p in spec["profiles"]]
    profile = args.profile or (profiles[0] if len(profiles) == 1 else None)
    if profile is None:
        raise SystemExit(f"--profile required; the bed declares {profiles}")
    rows_wanted, _which = scene_rows(spec, profile, args.sets)

    outside, depth, step, spacing, min_points = (args.outside, args.depth, args.step,
                                                 args.spacing, args.min_points)
    rows = []
    for sid, role in rows_wanted:
        scene = next(s for s in spec["scenes"] if s["id"] == sid)
        geom = component_geometry(components, scene["component"])
        if geom is None:
            print(f"# {sid}: {scene['component']} has no single declared box, skipped",
                  file=sys.stderr)
            continue
        native_png = os.path.join(args.fixtures, profile, f"{sid}.png")
        if not os.path.exists(native_png):
            continue
        if args.parent_compat:
            # The parent's finding reader worked in DEVICE px with a 0.5 px step; this reproduces
            # its window so the two readers can be compared on the cells it read.
            sc = Image.open(native_png).size[0] / canvas["width"]
            outside, depth, step = 1.0 / sc, 4.0 / sc, 0.5 / sc
            min_points, spacing = 720, 1e9
        nat = read_one(native_png, canvas, geom, args.erode, outside, depth, step,
                       spacing, min_points)
        row = {"scene": sid, "set": role, "background": scene["background"],
               "component": scene["component"], "tint": scene.get("tint"),
               "kind": geom[3], "radius": geom[2], "native": nat}
        if args.captures:
            web_png = os.path.join(args.captures, profile, sid, f"{sid}__{args.tier}.png")
            if os.path.exists(web_png):
                row["web"] = read_one(web_png, canvas, geom, args.erode, outside, depth, step,
                                      spacing, min_points)
        rows.append(row)

    label = args.label or f"{profile} / {args.tier if args.captures else 'native only'}"
    print(f"== {label}   fixtures={args.fixtures} captures={args.captures}")
    print(f"   window: {outside if not args.parent_compat else 'parent-compat'} CSS px outside … "
          f"{depth if not args.parent_compat else ''} CSS px inside, erode {args.erode}, "
          f"bins {NBINS} × {BIN_DEG}° centred on the compass")
    header = f"{'scene':40s} {'set':11s} {'src':6s} {'body':>7s} " + \
        " ".join(f"{c:>7s}" for c in COMPASS) + \
        f" {'ratio':>7s} {'bright':>7s} {'floor':>6s}"
    print(header)
    for r in rows:
        for tag in ("native", "web"):
            if tag not in r:
                continue
            v = r[tag]
            cells = " ".join("      -" if b is None else f"{b:7.4f}" for b in v["bins"])
            ratio = "    inf" if not math.isfinite(v["ratio"]) else f"{v['ratio']:7.2f}"
            print(f"{r['scene']:40s} {r['set']:11s} {tag:6s} {v['body']:7.4f} {cells} "
                  f"{ratio} {v['brightestCompass']:>7s} {v['ambientFraction']:6.3f}")

    if args.json:
        with open(args.json, "w") as fh:
            json.dump({"profile": profile, "tier": args.tier if args.captures else None,
                       "scenes": os.path.abspath(args.scenes),
                       "fixtures": os.path.abspath(args.fixtures),
                       "captures": os.path.abspath(args.captures) if args.captures else None,
                       "compass": list(COMPASS), "binDeg": BIN_DEG,
                       "erodeCssPx": args.erode, "outsideCssPx": outside, "depthCssPx": depth,
                       "rows": rows}, fh, indent=2)
        print(f"\n-> {args.json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
