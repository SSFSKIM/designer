"""W24 G0 (d) — the term the bins cannot see: the reference's rim varying ALONG a straight side.

The angular reader bins by the normal's angle, so a rounded rectangle's whole top edge falls in one
bin and its mean is what the law is fitted against. That is the right statistic for a directional
law and it is blind to a rim that varies along a side whose normal does not — which is what the
reference does on thick surfaces. This script is the measurement and its three controls.

- **the profile along each straight span**, first contour row, in eighths, every solid untinted cell
  of both probe grids and the canonical beds. A capsule (44 CSS px short side) and `rrect-sm` (32)
  are flat across the middle six eighths to four figures; `rrect-md` (96 — the size law's own
  `sizeSpanMax`) and `rrect-lg` (160) fall monotonically from the lit corner to the unlit one across
  the WHOLE span, not only near its ends.
- **the interior control**: the same rows at 1, 2, 4, 8, 12 and 20 CSS px inside. If the body under
  the rim carried a sheen the excess would inherit it. It does not: the body is one number to four
  figures at every depth and every position.
- **the silhouette control**: the sub-pixel row at which the top edge's transition crosses its own
  half level, per column, fitted for a slope. A shape sitting a fraction of a pixel askew would
  produce exactly this signature — bright at the top-left, dim at the top-right, and the opposite
  down the right side. It is not that: the edge is straight to a residual RMS of 0.05 px and the
  slope accounts for a tenth of a pixel across the span, where the read would need half of one.
- **the background control**: the fixture's own backdrop at eight margins of the canvas.

Usage: along-span.py
"""

import importlib.util
import json
import os

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location("read_angular", os.path.join(HERE, "read-angular.py"))
RA = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(RA)

WORKTREE = os.path.abspath(os.path.join(HERE, "..", "..", "..", "..", ".."))
MAIN = "/Users/new/Developer/GitHub/designer"
SOLID = ("dark-solid", "mid-dark-solid", "light-solid")

BEDS = [
    ("canonical 2x dark", os.path.join(WORKTREE, "apps/reference-apple/scenes.json"),
     os.path.join(MAIN, "apps/reference-apple/fixtures"), "apple-macos-26.5-2x-dark-standard"),
    ("canonical 2x light", os.path.join(WORKTREE, "apps/reference-apple/scenes.json"),
     os.path.join(MAIN, "apps/reference-apple/fixtures"), "apple-macos-26.5-2x-light-standard"),
    ("canonical 1x dark", os.path.join(WORKTREE, "apps/reference-apple/scenes.json"),
     os.path.join(MAIN, "apps/reference-apple/fixtures"), "apple-macos-26.5-1x-dark-standard"),
    ("W21 dark probe", os.path.join(WORKTREE, "apps/reference-apple/scenes-w21-probe.json"),
     os.path.join(WORKTREE, "packages/calibration/results/2026-09-06-w21-dark-scheme/probe"),
     "apple-macos-26.5-1x-dark-standard"),
    ("W9 light probe", os.path.join(WORKTREE, "apps/reference-apple/scenes-w9-probe.json"),
     "/Users/new/.claude/jobs/5c70e47f/tmp/w9-probe-fixtures", "apple-macos-26.5-1x-light-standard"),
]


def geometry(spec, scene, lum):
    geom = RA.component_geometry(spec["components"], scene["component"])
    scale = lum.shape[1] / spec["canvas"]["width"]
    x0, y0, x1, y1, r, kind = RA.declared_box(spec["canvas"], geom, scale)
    if kind == "capsule":
        r = min(x1 - x0, y1 - y0) / 2.0
    return geom, scale, (x0, y0, x1, y1, r)


def body_of(lum, box, scale, erode=6.0):
    x0, y0, x1, y1, _r = box
    e = erode * scale
    yy, xx = np.mgrid[0:lum.shape[0], 0:lum.shape[1]]
    m = (xx + .5 >= x0 + e) & (xx + .5 < x1 - e) & (yy + .5 >= y0 + e) & (yy + .5 < y1 - e)
    return float(lum[m].mean())


def eighths(strip):
    return " ".join(f"{q.mean():.4f}" for q in np.array_split(strip, 8))


def main() -> int:
    print("W24 G0 (d) — the rim along a straight side, and the three controls that say it is the")
    print("material and not the geometry.")
    for label, scenes_path, fixtures, profile in BEDS:
        spec = json.load(open(scenes_path))
        print(f"\n===== {label}  ({profile})")
        for scene in spec["scenes"]:
            if scene["background"] not in SOLID or scene.get("tint"):
                continue
            path = os.path.join(fixtures, profile, f"{scene['id']}.png")
            if not os.path.exists(path):
                continue
            rgb = RA.rgb_of(path)
            lum = RA.luma_of_rgb(rgb)
            geom, scale, box = geometry(spec, scene, lum)
            x0, y0, x1, y1, r = box
            body = body_of(lum, box, scale)
            lo, hi = int(np.ceil(x0 + r)), int(np.floor(x1 - r))
            print(f"\n  {scene['id']:38s} {geom[0]:5.0f}x{geom[1]:3.0f} r{geom[2]:4.1f}  "
                  f"body {body:.4f}  scale {scale:.0f}")
            if hi - lo >= 8:
                top = lum[int(y0), lo:hi] - body
                print(f"    TOP rim, left -> right, eighths:   {eighths(top)}"
                      f"   drop {top[:len(top)//8].mean() - top[-len(top)//8:].mean():+.4f}")
            ylo, yhi = int(np.ceil(y0 + r)), int(np.floor(y1 - r))
            if yhi - ylo >= 8:
                right = lum[ylo:yhi, int(x1) - 1] - body
                print(f"    RIGHT rim, top -> bottom, eighths: {eighths(right)}"
                      f"   rise {right[-len(right)//8:].mean() - right[:len(right)//8].mean():+.4f}")
            if hi - lo >= 8:
                for depth in (1, 2, 4, 8, 12, 20):
                    row = int(y0) + int(round(depth * scale))
                    if row >= lum.shape[0]:
                        continue
                    strip = lum[row, lo:hi]
                    print(f"    body at +{depth:2d} CSS px:                 {eighths(strip)}")
            # the silhouette's own sub-pixel position along the top edge
            backdrop = float(lum[4:12, 4:12].mean())
            half = 0.5 * (backdrop + max(body, backdrop + 0.02))
            pos = []
            for x in range(lo + 4, hi - 4):
                col = lum[int(y0) - 4:int(y0) + 4, x]
                for i in range(len(col) - 1):
                    a, b = col[i], col[i + 1]
                    if (a - half) * (b - half) <= 0 and a != b:
                        pos.append((x, int(y0) - 4 + i + (half - a) / (b - a)))
                        break
            if len(pos) > 16:
                p = np.asarray(pos)
                A = np.vstack([p[:, 0], np.ones(len(p))]).T
                slope, intercept = np.linalg.lstsq(A, p[:, 1], rcond=None)[0]
                span = p[:, 0].max() - p[:, 0].min()
                rms = float(np.std(p[:, 1] - (A @ [slope, intercept])))
                print(f"    silhouette: slope {slope:+.6f} px/px = {slope * span:+.3f} px across "
                      f"{span:.0f} px, residual rms {rms:.4f} px")
            h, w = lum.shape
            k = 10
            spots = {"tl": (0, 0), "tr": (0, w - k), "bl": (h - k, 0), "br": (h - k, w - k),
                     "t": (0, w // 2), "b": (h - k, w // 2), "l": (h // 2, 0), "r": (h // 2, w - k)}
            print("    backdrop at the eight margins: "
                  + " ".join(f"{n}={lum[y:y + k, x:x + k].mean():.5f}"
                             for n, (y, x) in spots.items()))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
