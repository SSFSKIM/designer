"""Validate the Python replica against the committed 0.14.0 `results/matrix.json`.

Every cell of the committed matrix whose captures are on disk is recomputed and
its five shape numbers compared. Nothing downstream in this spike is trusted
unless this reports an exact match on the counts and sub-1e-9 on the ratios.
"""

from __future__ import annotations

import json
import os
import sys

import w26extractor as X

MATRIX = os.path.join(X.REPO, "packages/calibration/results/matrix.json")


def rows():
    cells = json.load(open(MATRIX))["cells"]
    for c in cells:
        if c.get("shape") is None:
            continue
        yield c


def main():
    limit = int(sys.argv[1]) if len(sys.argv) > 1 else 10**9
    ok = bad = skipped = 0
    worst = 0.0
    failures = []
    for i, c in enumerate(rows()):
        if ok + bad >= limit:
            break
        key = c["key"]
        profile = key["profileKey"]
        scene_id = key["sceneId"]
        renderer = key["web"]["renderer"]
        try:
            native, web, bg, region, _ = X.cell_inputs(profile, scene_id, renderer)
        except FileNotFoundError:
            skipped += 1
            continue
        if native.shape[:2] != web.shape[:2] or native.shape[:2] != bg.shape[:2]:
            skipped += 1
            continue
        n = X.extract_luminance_delta(native, bg, region)
        w = X.extract_luminance_delta(web, bg, region)
        got = {
            "silhouetteAreaNative": int(n.sum()),
            "silhouetteAreaWeb": int(w.sum()),
            "silhouetteHolesNative": X.hole_count(n, region),
            "silhouetteHolesWeb": X.hole_count(w, region),
            "silhouetteIoU": X.iou(n, w),
            "componentRegionArea": int(region.sum()),
        }
        cd = X.contour_distance(n, w)
        got["contourDistanceMean"] = cd["meanPx"]
        got["contourDistanceP95"] = cd["p95Px"]
        want = {k: v["value"] for k, v in c["shape"].items() if isinstance(v, dict) and "value" in v}
        diffs = []
        for k, v in got.items():
            if k not in want:
                continue
            d = abs(v - want[k])
            worst = max(worst, d if k.endswith(("IoU",)) else 0.0)
            tol = 1e-9 if isinstance(v, float) else 0
            if d > tol:
                diffs.append(f"{k}: got {v} want {want[k]}")
        if diffs:
            bad += 1
            failures.append((profile, scene_id, renderer, diffs))
        else:
            ok += 1
    print(f"cells matched  {ok}")
    print(f"cells differing {bad}")
    print(f"cells skipped (captures absent / size mismatch) {skipped}")
    print(f"worst IoU |delta| {worst:.3e}")
    for f in failures[:20]:
        print("  MISMATCH", f[0], f[1], f[2])
        for d in f[3]:
            print("      ", d)


if __name__ == "__main__":
    main()
