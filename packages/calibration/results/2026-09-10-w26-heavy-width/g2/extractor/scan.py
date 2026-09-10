"""Is the 0.14.0 -> candidate IoU drop a fence effect or a shape change?

Scan the extractor's luminance-delta threshold over the floor cell and print, at
each rung, both columns' silhouette area, hole count and IoU against the native
extracted at the SAME threshold. A real shape difference moves smoothly and keeps
its sign; a fence effect appears and disappears as the rung crosses the level the
dark checker squares transmit at.
"""

from __future__ import annotations

import numpy as np

import w26extractor as X
from anatomy import CAND_ROOT, PROFILE, SCENE

RUNGS = [0.002, 0.004, 0.006, 0.008, 0.01, 0.012, 0.014, 0.016, 0.018, 0.019,
         0.02, 0.021, 0.022, 0.024, 0.026, 0.03, 0.035, 0.04, 0.05, 0.06, 0.08]


def main():
    native, web0, bg, region, _ = X.cell_inputs(PROFILE, SCENE, "webgpu")
    webc = X.load(X.web_path(PROFILE, SCENE, "webgpu", root=CAND_ROOT))

    print("threshold scan, texture / holdout / checkerboard__glass-over-glass__rest /")
    print("apple-macos-26.5-2x-dark-standard, GPU tier. Region area "
          f"{int(region.sum())} px. The adopted rung is 0.02; the floor is 0.9257.")
    print()
    print(f"{'thr':>7}{'nat area':>10}{'0.14 area':>11}{'cand area':>11}"
          f"{'nat holes':>11}{'0.14 holes':>12}{'cand holes':>12}"
          f"{'IoU 0.14':>10}{'IoU cand':>10}{'Δ IoU':>10}")
    for t in RUNGS:
        n = X.extract_luminance_delta(native, bg, region, t)
        a = X.extract_luminance_delta(web0, bg, region, t)
        c = X.extract_luminance_delta(webc, bg, region, t)
        i0 = X.iou(n, a)
        ic = X.iou(n, c)
        print(f"{t:>7.3f}{int(n.sum()):>10}{int(a.sum()):>11}{int(c.sum()):>11}"
              f"{X.hole_count(n, region):>11}{X.hole_count(a, region):>12}"
              f"{X.hole_count(c, region):>12}{i0:>10.5f}{ic:>10.5f}{ic - i0:>10.5f}")

    print()
    print("The same scan on HOLE-FILLED masks (the contour axis's own rule, applied to IoU):")
    print(f"{'thr':>7}{'IoU 0.14':>10}{'IoU cand':>10}{'Δ IoU':>10}")
    for t in RUNGS:
        n = X.fill_holes(X.extract_luminance_delta(native, bg, region, t))
        a = X.fill_holes(X.extract_luminance_delta(web0, bg, region, t))
        c = X.fill_holes(X.extract_luminance_delta(webc, bg, region, t))
        i0 = X.iou(n, a)
        ic = X.iou(n, c)
        print(f"{t:>7.3f}{i0:>10.5f}{ic:>10.5f}{ic - i0:>10.5f}")

    print()
    print("What the rule is testing over this backdrop. The checkerboard's dark cell,")
    print("in the committed background raster:")
    bgl = X.luma(bg)
    vals, counts = np.unique(np.round(bgl, 6), return_counts=True)
    order = np.argsort(-counts)[:4]
    for k in order:
        print(f"  linear luma {vals[k]:.6f}  {counts[k]} px of the raster")
    print("  -> over a cell at linear 0, |own - base| IS the surface's own absolute")
    print("     luminance, so the 0.02 rung is an absolute brightness test there.")


if __name__ == "__main__":
    main()
