"""W20 G0 — read Apple's corner contour off the probe captures and score the four candidates.

The question this answers is what Apple draws for ``RoundedRectangle(cornerRadius: r, style:
.continuous)`` once ``APPLE_REACH * r`` no longer fits half the short side. vitrea clamps the RADIUS
there (``packages/geometry/src/apple.ts``); nothing measured that. This reads the contour out of the
native captures and puts four candidate constructions — all of them things the geometry package can
actually build, emitted by ``candidates.ts`` — against it.

Two independent extractions, because a contour read one way is a reading and read two ways is a
measurement:

``light-solid``
    The material's rim is a bright line one pixel wide against a flat backdrop, so the surface's
    boundary is a step from the (slightly shadowed) background level up to the rim. The contour is
    the SUB-PIXEL crossing of the half-coverage level between those two, found by scanning inward
    along every row and every column. Dense — one point per row from each side and one per column
    from each side — and it needs no model of the material.

``checkerboard``
    A LOCAL-CONTRAST rule, as the charter's instrument section asks. The material blurs the checker,
    so a 3x3 local range collapses inside the surface; the outer shadow darkens the checker but is
    very nearly multiplicative, so the range collapses there in the same proportion as the mean and
    the RATIO to the background raster's own local range does not move. The silhouette is the
    outermost place that ratio falls and stays below a half. The rim sits ON the boundary and is
    itself high-contrast, so the rule reads inside the true contour by a fixed amount along the
    scan; the capsule controls, whose true shape is known exactly, are what that offset is measured
    on, and it is declared as `CHECKER_SCAN_BIAS` and applied to every cell alike. The reading has
    one-pixel resolution either way, so it is the cross-check and `light-solid` is the measurement.

The grid's floor is 0.5 px: the captures are 1x, one device pixel is one CSS pixel, and no contour
read off a pixel grid can claim better than half of one. Every distance below is in device px.

Usage:
  read-contours.py --probe <fixturesDir> --candidates <candidates.json> --out <dir>

``--probe`` is the probe's own fixtures directory (``…/w20-capsule-corner/probe/``); the canonical
``apps/reference-apple/fixtures`` is never written and is only read when it is passed explicitly.
"""

import argparse
import json
import math
import os

import numpy as np
from PIL import Image, ImageDraw

PROFILE = "apple-macos-26.5-1x-light-standard"
CANVAS = (320, 200)
#: The pixel grid's own floor. A contour read off a raster cannot claim better than half a pixel.
GRID_FLOOR = 0.5
#: The checkerboard rule's measured offset along the scan, in px — see `contour_checkerboard`.
CHECKER_SCAN_BIAS = 1.5


# ---------------------------------------------------------------------------
# extraction
# ---------------------------------------------------------------------------


def load_gray(path):
    return np.asarray(Image.open(path).convert("RGB")).astype(np.float64).mean(axis=2)


def local_range(a, k=3):
    """Local max minus local min over a k x k window, by shifted stacks (no scipy dependency)."""
    r = k // 2
    pad = np.pad(a, r, mode="edge")
    stack = np.stack(
        [pad[i : i + a.shape[0], j : j + a.shape[1]] for i in range(k) for j in range(k)]
    )
    return stack.max(axis=0) - stack.min(axis=0)


def crossings_along(values, threshold, rising):
    """Sub-pixel index where `values` first crosses `threshold`, scanning from index 0 upward.

    `rising` selects the direction of the crossing. Returns None if it never crosses. The
    interpolation is linear in the sample value, which is what an anti-aliased edge is: a coverage
    mix of the two levels either side of it.
    """
    inside = values >= threshold if rising else values <= threshold
    idx = np.flatnonzero(inside)
    if idx.size == 0 or idx[0] == 0:
        return None
    i = int(idx[0])
    v0, v1 = values[i - 1], values[i]
    if v1 == v0:
        return float(i)
    return (i - 1) + (threshold - v0) / (v1 - v0)


def contour_light_solid(img, box):
    """Sub-pixel silhouette from the rim step over a flat backdrop.

    `box` is the surface's declared bounding box (x0, y0, x1, y1) in pixel coordinates; it bounds
    the search to the surface and its immediate surround, never to its shape.
    """
    x0, y0, x1, y1 = box
    pts = []
    # The two levels the crossing sits between: the shadowed background just outside the box, and
    # the rim's own peak just inside it. Both are read from the capture rather than assumed.
    outside = float(np.median(np.r_[img[y0:y1, x0 - 6 : x0 - 2].ravel(),
                                    img[y0:y1, x1 + 2 : x1 + 6].ravel()]))
    rim = float(np.percentile(img[y0 - 1 : y1 + 1, x0 - 1 : x1 + 1], 99.5))
    thr = 0.5 * (outside + rim)

    # Sample j of a slice starting at `a` is the pixel `a + j`, whose CENTRE is at `a + j + 0.5`;
    # a crossing at fractional index t is therefore at `a + t + 0.5`, and on a reversed slice
    # ending at `b` it is at `b - t - 0.5`. Getting that half pixel wrong reads every shape one
    # pixel too wide, which is twice the grid's floor.
    a_x, b_x = x0 - 8, x1 + 8
    a_y, b_y = y0 - 8, y1 + 8
    for y in range(y0 - 2, y1 + 2):
        row = img[y]
        left = crossings_along(row[a_x:b_x], thr, True)
        if left is not None:
            pts.append((a_x + left + 0.5, y + 0.5))
        right = crossings_along(row[a_x:b_x][::-1], thr, True)
        if right is not None:
            pts.append((b_x - right - 0.5, y + 0.5))
    for x in range(x0 - 2, x1 + 2):
        col = img[:, x]
        top = crossings_along(col[a_y:b_y], thr, True)
        if top is not None:
            pts.append((x + 0.5, a_y + top + 0.5))
        bot = crossings_along(col[a_y:b_y][::-1], thr, True)
        if bot is not None:
            pts.append((x + 0.5, b_y - bot - 0.5))
    return np.array(pts), {"outside": outside, "rim": rim, "threshold": thr}


def contour_checkerboard(img, bg, box):
    """Silhouette from the collapse of local contrast, relative to the background's own contrast."""
    x0, y0, x1, y1 = box
    rc = local_range(img)
    rb = local_range(bg)
    valid = rb > 120.0
    ratio = np.where(valid, rc / np.maximum(rb, 1e-6), np.nan)

    pts = []

    def scan(series, base, axis_pos, horizontal):
        # "Inside" is three consecutive valid samples below a half; the run requirement is what
        # keeps a single blurred sample at a checker edge from being read as the boundary.
        below = np.where(np.isnan(series), False, series < 0.5)
        run = np.convolve(below.astype(int), np.ones(3, int), mode="valid")
        idx = np.flatnonzero(run == 3)
        if idx.size == 0:
            return None
        return base + float(idx[0])

    # The rule reads INSIDE the true contour by a fixed amount along the scan, for two reasons that
    # are both properties of the rule rather than of the shape: the rim occupies the boundary pixel
    # and is itself high-contrast, and the run-of-three requirement then costs two more samples.
    # Measured on the 120 x 44 capsule control against its exact stadium: median -1.5 px, mean
    # -1.31. `CHECKER_SCAN_BIAS` is that median, declared once and applied along the scan direction
    # — which is where the error is generated — to every cell alike. The residual after it is what
    # the control section of the findings quotes.
    a_x, b_x = x0 - 8, x1 + 8
    a_y, b_y = y0 - 8, y1 + 8
    k = CHECKER_SCAN_BIAS
    for y in range(y0 - 2, y1 + 2):
        left = scan(ratio[y, a_x:b_x], a_x, y, True)
        if left is not None:
            pts.append((left + 0.5 - k, y + 0.5))
        right = scan(ratio[y, a_x:b_x][::-1], 0, y, True)
        if right is not None:
            pts.append((b_x - right - 0.5 + k, y + 0.5))
    for x in range(x0 - 2, x1 + 2):
        top = scan(ratio[a_y:b_y, x], a_y, x, False)
        if top is not None:
            pts.append((x + 0.5, top + 0.5 - k))
        bot = scan(ratio[a_y:b_y, x][::-1], 0, x, False)
        if bot is not None:
            pts.append((x + 0.5, b_y - bot - 0.5 + k))
    return np.array(pts), {"validSamples": int(valid.sum()), "scanBias": k}


# ---------------------------------------------------------------------------
# scoring
# ---------------------------------------------------------------------------


def to_centred(pts, w, h):
    """Pixel coordinates to the geometry package's centred, y-up frame in CSS px."""
    cx, cy = CANVAS[0] / 2.0, CANVAS[1] / 2.0
    return np.stack([pts[:, 0] - cx, cy - pts[:, 1]], axis=1)


def distances(points, polyline):
    """Nearest-vertex distance from every point to a polyline sampled at 0.02 px."""
    out = np.empty(len(points))
    poly = np.asarray(polyline)
    for i, p in enumerate(points):
        d = poly - p
        out[i] = math.sqrt(float((d[:, 0] ** 2 + d[:, 1] ** 2).min()))
    return out


def candidate_separation(entry, stride=25):
    """Max distance between each pair of candidate polylines, in px.

    A verdict is only worth what the instrument can separate. Two candidates whose curves are closer
    together than the reader's own residual cannot be told apart by it, and saying so is part of the
    reading rather than a caveat on it.
    """
    names = list(entry["candidates"].keys())
    out = {}
    for i, a in enumerate(names):
        for b in names[i + 1 :]:
            pa = np.asarray(entry["candidates"][a])[::stride]
            pb = np.asarray(entry["candidates"][b])[::stride]
            d = np.sqrt(
                ((pa[:, None, 0] - pb[None, :, 0]) ** 2 + (pa[:, None, 1] - pb[None, :, 1]) ** 2)
            )
            out[f"{a} vs {b}"] = float(max(d.min(axis=1).max(), d.min(axis=0).max()))
    return out


def fit_circle(points):
    """Algebraic (Kasa) circle fit. Returns (cx, cy, r, rms residual)."""
    x, y = points[:, 0], points[:, 1]
    a = np.stack([x, y, np.ones_like(x)], axis=1)
    b = x**2 + y**2
    sol, *_ = np.linalg.lstsq(a, b, rcond=None)
    cx, cy = sol[0] / 2, sol[1] / 2
    r = math.sqrt(float(sol[2] + cx**2 + cy**2))
    res = np.hypot(x - cx, y - cy) - r
    return cx, cy, r, float(np.sqrt((res**2).mean()))


def fold(points, half_w, half_h):
    """The four corners folded into one, as inward offsets `(u, v)` from the corner vertex."""
    u = half_w - np.abs(points[:, 0])
    v = half_h - np.abs(points[:, 1])
    return u, v


def corner_band(points, half_w, half_h, budget, width=0.75):
    """The corner's arc section, as points in the first quadrant.

    A point is kept when it lies within a band around the corner's 45-degree diagonal — where every
    candidate puts its circular arc — so a fitted radius is the ARC's radius and not an average over
    the shoulders, which is exactly the quantity that separates a clamped radius from a compressed
    shoulder. The band is wide (0.75 of the budget in `u - v`) because a circle fit over a short arc
    is ill-conditioned: on the 120 x 44 stadium a 34-degree band reads 17.9 for a radius of 22 while
    a 60-degree band reads it correctly.
    """
    u, v = fold(points, half_w, half_h)
    keep = (np.abs(u - v) < width * budget) & (u < 1.3 * budget) & (v < 1.3 * budget)
    return np.stack([half_w - u[keep], half_h - v[keep]], axis=1)


def diagonal_depth(points, half_w, half_h, budget):
    """Distance from the corner's vertex to the contour along the 45-degree diagonal.

    One scalar per shape, and the best-conditioned corner measurement a pixel grid supports: the
    contour crosses the diagonal transversally, so a local linear fit of `u` against `u - v` near
    zero is stable where a circle fit over a short arc is not. It is a pure measurement — no family
    is assumed — and the same number is computed from each candidate's own polyline, so the
    comparison is like for like. For a corner whose arc is a true circle of radius R centred at
    `(half_w - R, half_h - R)` it equals `R * (sqrt(2) - 1)`.
    """
    u, v = fold(points, half_w, half_h)
    g = u - v
    keep = np.abs(g) < 0.5 * budget
    if keep.sum() < 6:
        return float("nan")
    coeff = np.polyfit(g[keep], u[keep], 2)
    return math.sqrt(2.0) * float(np.polyval(coeff, 0.0))


# ---------------------------------------------------------------------------
# crops
# ---------------------------------------------------------------------------

CANDIDATE_COLOURS = {
    "vitrea-clamp": (255, 0, 0),
    "shoulder-compress": (0, 160, 255),
    "circular-arc": (0, 200, 0),
    "apple-overflow": (255, 0, 255),
    "stadium": (0, 160, 255),
}


def write_crop(img_path, entry, out_path, zoom=8, pad=5):
    """One panel per candidate: the native corner, zoomed, with that candidate's contour over it.

    Panels rather than one overlay, because four curves within half a pixel of each other in the
    same picture is a picture of a smudge. The crop is contrast-stretched — over `light-solid` the
    whole scene lives in the top 8 % of the range and the material's edge is invisible at native
    contrast — and the stretch is stated in the findings so nobody reads it as a level.
    """
    w, h = entry["size"]
    x1 = int(CANVAS[0] / 2 + w / 2)
    y0 = int(CANVAS[1] / 2 - h / 2)
    budget = min(w, h) / 2
    side = int(budget * 1.4) + pad
    box = (x1 - side, y0 - pad, x1 + pad, y0 + side)

    src = np.asarray(Image.open(img_path).convert("RGB").crop(box)).astype(np.float64)
    lo, hi = src.min(), src.max()
    src = (src - lo) / max(hi - lo, 1e-6) * 255.0
    base = Image.fromarray(src.astype(np.uint8)).resize(
        ((box[2] - box[0]) * zoom, (box[3] - box[1]) * zoom), Image.NEAREST
    )

    names = list(entry["candidates"].keys())
    gap = 6
    strip = Image.new("RGB", (len(names) * base.width + (len(names) - 1) * gap, base.height),
                      (32, 32, 32))
    for k, name in enumerate(names):
        panel = base.copy()
        d = ImageDraw.Draw(panel)
        colour = CANDIDATE_COLOURS.get(name, (255, 255, 0))
        for cx, cy in entry["candidates"][name][::4]:
            px = (cx + CANVAS[0] / 2 - box[0]) * zoom
            py = (CANVAS[1] / 2 - cy - box[1]) * zoom
            if 0 <= px < panel.width and 0 <= py < panel.height:
                d.point((px, py), fill=colour)
        strip.paste(panel, (k * (base.width + gap), 0))
    strip.save(out_path)
    return {"box": list(box), "zoom": zoom, "stretch": [float(lo), float(hi)],
            "panelOrder": names}


# ---------------------------------------------------------------------------


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--probe", required=True)
    ap.add_argument("--candidates", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    cand = json.load(open(args.candidates))
    entries = {e["component"]: e for e in cand["entries"]}
    os.makedirs(args.out, exist_ok=True)
    os.makedirs(os.path.join(args.out, "crops"), exist_ok=True)

    bg_checker = load_gray(os.path.join(args.probe, "backgrounds", "checkerboard@1x.png"))
    results = []

    for background in ("light-solid", "checkerboard"):
        for component, entry in entries.items():
            scene = f"{background}__{component}__rest"
            path = os.path.join(args.probe, PROFILE, f"{scene}.png")
            if not os.path.exists(path):
                results.append({"scene": scene, "error": "no capture"})
                continue
            img = load_gray(path)
            w, h = entry["size"]
            box = (
                int(CANVAS[0] / 2 - w / 2),
                int(CANVAS[1] / 2 - h / 2),
                int(CANVAS[0] / 2 + w / 2),
                int(CANVAS[1] / 2 + h / 2),
            )
            if background == "light-solid":
                pts, meta = contour_light_solid(img, box)
            else:
                pts, meta = contour_checkerboard(img, bg_checker, box)
            if len(pts) == 0:
                results.append({"scene": scene, "error": "no contour points"})
                continue
            cpts = to_centred(pts, w, h)
            half_w, half_h = w / 2.0, h / 2.0
            budget = min(half_w, half_h)
            arc = corner_band(cpts, half_w, half_h, budget)
            # A circle fit needs a populated arc. The checkerboard rule yields points only where
            # the background raster itself has contrast — about an eighth of the scanlines — so the
            # fit is refused there rather than reported at whatever a dozen points happen to give.
            cx, cy, r_fit, rms = (
                fit_circle(arc) if len(arc) >= 20 else (0, 0, float("nan"), float("nan"))
            )
            depth = diagonal_depth(cpts, half_w, half_h, budget)

            row = {
                "scene": scene,
                "background": background,
                "component": component,
                "size": [w, h],
                "declaredRadius": entry["radius"],
                "ratio": entry["ratio"],
                "points": int(len(cpts)),
                "arcPoints": int(len(arc)),
                "circleFitRadius": r_fit,
                "circleFitRms": rms,
                "diagonalDepth": depth,
                "impliedCircularRadius": depth / (math.sqrt(2.0) - 1.0),
                "extraction": meta,
                "candidateSeparation": candidate_separation(entry),
                "candidates": {},
            }
            for name, poly in entry["candidates"].items():
                d = distances(cpts, poly)
                poly_a = np.asarray(poly)
                # The reverse direction, from the candidate onto the measured points. A one-sided
                # native-to-candidate distance cannot see a candidate that draws EXTRA curve: the
                # overflow control self-intersects and still scores well one way round, because
                # every measured point finds something of it nearby. The native points sit about a
                # pixel apart, so a correct candidate reads about half a pixel here.
                back = distances(poly_a[::25], cpts)
                row["candidates"][name] = {
                    "max": float(d.max()),
                    "p95": float(np.percentile(d, 95)),
                    "mean": float(d.mean()),
                    "withinFloor": bool(np.percentile(d, 95) <= GRID_FLOOR),
                    "maxCandidateToNative": float(back.max()),
                    "p95CandidateToNative": float(np.percentile(back, 95)),
                    "circleFitRadius": (
                        fit_circle(corner_band(poly_a, half_w, half_h, budget))[2]
                        if len(corner_band(poly_a, half_w, half_h, budget)) >= 8
                        else float("nan")
                    ),
                    "diagonalDepth": diagonal_depth(poly_a, half_w, half_h, budget),
                }
            results.append(row)

            if background == "light-solid":
                row["crop"] = write_crop(
                    path, entry, os.path.join(args.out, "crops", f"{scene}.png")
                )

    json.dump(
        {"gridFloor": GRID_FLOOR, "results": results},
        open(os.path.join(args.out, "contours.json"), "w"),
        indent=1,
    )
    for r in results:
        if "error" in r:
            print(f"{r['scene']:52s} {r['error']}")
            continue
        best = min(r["candidates"].items(), key=lambda kv: kv[1]["p95"])
        print(
            f"{r['scene']:52s} n={r['points']:4d} rFit={r['circleFitRadius']:6.2f} "
            f"depth={r['diagonalDepth']:5.2f} rImplied={r['impliedCircularRadius']:6.2f} "
            f"best={best[0]:18s} p95={best[1]['p95']:.3f} max={best[1]['max']:.3f}"
        )


if __name__ == "__main__":
    main()
