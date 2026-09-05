"""W19 G1 — the pre-check's tables, printed from the readers' JSON.

Every number in `g1-precheck.md` comes out of this, so a reader can regenerate the tables rather
than trust a transcription. It reads only the parts directories it is given and writes nothing.

Usage, from `packages/calibration`:
    python3 results/2026-09-05-w19-author-tint-fold/g1/tables.py <afterParts> [<beforeParts>]

`<beforeParts>` defaults to G0's own `parts/`, which is what the before columns are read from.
"""

import json
import os
import sys

AFTER = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(__file__), "parts")
BEFORE = sys.argv[2] if len(sys.argv) > 2 else os.path.join(os.path.dirname(__file__), "..", "g0", "parts")

def load(root, name):
    return json.load(open(os.path.join(root, name)))

RUNGS = ["orange-010", "orange-020", "orange-035", "orange-half", "orange-075", "orange",
         "blue-020", "blue-050", "blue"]
STRENGTH = {"orange-010": 0.10, "orange-020": 0.20, "orange-035": 0.35, "orange-half": 0.50,
            "orange-075": 0.75, "orange": 1.00, "blue-020": 0.20, "blue-050": 0.50, "blue": 1.00}
FLOOR = 0.2668228970218852

print("=== S4 — CSS − GPU, declared component region, standard light ===")
for scale in (1, 2):
    rows = {r["scene"]: r for r in load(AFTER, f"ladder-{scale}x.json") if "whole" in r}
    gran = {r["scene"]: r for r in load(AFTER, f"granularity-{scale}x.json") if "granularityTerm" in r}
    before = {r["scene"]: r for r in load(BEFORE, f"ladder-{scale}x.json") if "whole" in r}
    print(f"-- dpr {scale}")
    for bg in ("photo", "checkerboard"):
        key = f"{bg}__capsule-button__rest"
        print(f"  {bg:12s} untinted          before {before[key]['whole']['declared']['delta']:+.4f}"
              f"  after {rows[key]['whole']['declared']['delta']:+.4f}  form={rows[key]['cssTint'][0]}")
        for rung in RUNGS:
            key = f"{bg}__capsule-button__rest-tint-{rung}"
            if key not in rows:
                continue
            after = rows[key]["whole"]["declared"]["delta"]
            term = gran.get(key, {}).get("granularityTerm", float("nan"))
            mark = "" if abs(after) <= 0.005 else "  MISSES 0.005"
            print(f"  {bg:12s} {rung:11s} s={STRENGTH[rung]:.2f} "
                  f"before {before[key]['whole']['declared']['delta']:+.4f}  after {after:+.4f}"
                  f"  granularity {term:+.4f}  form={rows[key]['cssTint'][0]}{mark}")

print()
print("=== S4 — the fold profiles at 1x over the photo: movement against the untinted control ===")
for acc in ("increased-contrast", "reduced-transparency"):
    b = {r["scene"]: r for r in load(BEFORE, f"ladder-fold-{acc}.json") if "whole" in r}
    a = {r["scene"]: r for r in load(AFTER, f"ladder-fold-{acc}.json") if "whole" in r}
    key = "photo__capsule-button__rest"
    b0 = b[key]["whole"]["declared"]["delta"]
    a0 = a[key]["whole"]["declared"]["delta"]
    print(f"-- {acc}: untinted control before {b0:+.4f}  after {a0:+.4f}")
    for rung in ("orange-020", "orange-half", "orange"):
        key = f"photo__capsule-button__rest-tint-{rung}"
        if key not in a:
            continue
        d0 = b[key]["whole"]["declared"]["delta"]
        d1 = a[key]["whole"]["declared"]["delta"]
        mark = "" if abs(d1 - a0) <= 0.01 else "  MISSES 0.01"
        print(f"   {rung:11s} CSS−GPU {d0:+.4f} -> {d1:+.4f} | movement {d0-b0:+.4f} -> {d1-a0:+.4f}"
              f"  form={a[key]['cssTint'][0]}{mark}")

print()
print("=== S5 — measured against predFold + c, c the cell's own decoration constant at s = 1 ===")
for scale in (1, 2):
    rows = {r["scene"]: r for r in load(AFTER, f"predict-{scale}x.json") if "measuredCss" in r}
    print(f"-- dpr {scale}")
    for bg in ("photo", "checkerboard"):
        for seed in ("orange", "blue"):
            full = rows.get(f"{bg}__capsule-button__rest-tint-{seed}")
            if full is None:
                continue
            c = full["measuredCss"] - full["predictedFold"]
            print(f"   {bg}/{seed}: c = {c:+.5f}")
            for rung in RUNGS:
                if not rung.startswith(seed):
                    continue
                key = f"{bg}__capsule-button__rest-tint-{rung}"
                if key not in rows:
                    continue
                r = rows[key]
                miss = r["measuredCss"] - (r["predictedFold"] + c)
                mark = "" if abs(miss) <= 0.005 else "  MISSES 0.005"
                print(f"     {rung:11s} measured {r['measuredCss']:.5f}  predFold {r['predictedFold']:.5f}"
                      f"  miss {miss:+.5f}  clamp today {r['clampedChannelShareToday']*100:6.3f}%"
                      f"  clamp fold {r['clampedChannelShareFold']*100:.4f}%{mark}")

print()
print("=== S3 by capture — the CSS captures, pre-fold to post-fold ===")
for scale in (1, 2):
    for r in load(AFTER, f"moved-{scale}x.json"):
        if "identical" not in r:
            continue
        if r["identical"]:
            state = "BYTE-IDENTICAL"
        else:
            state = (f"differing {r['differingPixels']:6d} px, {r['differingInRegion']:6d} in region, "
                     f"{r['differingInErodedInterior']:6d} in the eroded interior, worst code "
                     f"{r['worstChannelCode']:3d}, interior mean {r['interiorMeanMove']:+.5f}")
        print(f"  dpr{scale} {r['scene']:52s} {state}")

print()
print("=== The hue — cross-tier OKLab ΔE mean under the declared region ===")
for scale in (1, 2):
    b = {r["scene"]: r for r in load(AFTER, f"hue-before-{scale}x.json") if "oklabDeltaEMean" in r}
    a = {r["scene"]: r for r in load(AFTER, f"hue-after-{scale}x.json") if "oklabDeltaEMean" in r}
    for key in sorted(b):
        print(f"  dpr{scale} {key:52s} {b[key]['oklabDeltaEMean']:.5f} -> {a[key]['oklabDeltaEMean']:.5f}"
              f"  ({a[key]['oklabDeltaEMean']-b[key]['oklabDeltaEMean']:+.5f})")

print()
print("=== The floor — the alpha L3 paints, per strength (α″ = 1 − (1 − s)(1 − α₃)) ===")
print(f"  α₃ = {FLOOR:.7f}")
for s in (0.10, 0.20, 0.35, 0.50, 0.75, 1.00):
    alpha = 1 - (1 - s) * (1 - FLOOR)
    written = round(alpha * 1000) / 1000
    print(f"  s={s:.2f}  before {s:.3f}  after {alpha:.5f} (written {written:.3f})"
          f"  margin over the floor {written - FLOOR:+.5f}"
          f"  {'UNDER THE FLOOR before' if s < FLOOR else ''}")
