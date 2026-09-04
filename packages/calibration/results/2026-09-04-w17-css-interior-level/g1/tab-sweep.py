#!/usr/bin/env python3
"""W17 G1 — the k sweep of Decision Log 4 (b): the filter region's reach, in units of the composed
heavy width, against the level residual it leaves on the two `toolbar-group` scenes.

    python3 tab-sweep.py 2 2.5 3

Reads `matrix-k<k>.json` from the scratch root and prints the CSS tier's interior mean against the
GPU tier's on the same run, at both light-standard scales, with the W16 bed's reading beside it.
The smallest k whose residual is inside 0.005 on every cell is the constant, and the residual it
was chosen on is what `CSS_TIER_FILTER_REGION_SIGMA`'s doc comment records.
"""
import json
import sys

T = "/Users/new/.claude/jobs/5c70e47f/tmp/w17/g1"
BED = "/Users/new/Developer/GitHub/designer/packages/calibration/results/matrix.json"
PROFILES = ["apple-macos-26.5-1x-light-standard", "apple-macos-26.5-2x-light-standard"]
SCENES = ["checkerboard__toolbar-group__rest", "photo__toolbar-group__rest"]


def load(path):
    best = {}
    for c in json.load(open(path))["cells"]:
        k = (c["key"]["profileKey"], c["key"]["web"]["renderer"], c["key"]["sceneId"])
        if k not in best or c["capturedAt"] > best[k]["capturedAt"]:
            best[k] = c
    return best


def level(cell):
    if cell is None or cell.get("material") is None:
        return None
    return cell["material"]["interiorMeanWeb"]["value"]


bed = load(BED)
print("| k | cell | dpr | CSS | GPU | CSS−GPU | bed CSS−GPU |")
print("| --- | --- | --- | --- | --- | --- | --- |")
worst = {}
for k in sys.argv[1:]:
    run = load(f"{T}/matrix-k{k}.json")
    for profile in PROFILES:
        dpr = "2x" if "-2x-" in profile else "1x"
        for scene in SCENES:
            css, gpu = level(run.get((profile, "css", scene))), level(run.get((profile, "webgpu", scene)))
            b0, bg = level(bed.get((profile, "css", scene))), level(bed.get((profile, "webgpu", scene)))
            if css is None or gpu is None:
                continue
            d = css - gpu
            worst[k] = max(worst.get(k, 0.0), abs(d))
            bedd = "—" if b0 is None or bg is None else f"{b0 - bg:+.4f}"
            print(
                f"| {k} | `{scene.replace('__rest', '')}` | {dpr} | {css:.4f} | {gpu:.4f} "
                f"| **{d:+.4f}** | {bedd} |"
            )
print()
for k, w in sorted(worst.items(), key=lambda kv: float(kv[0])):
    print(f"k = {k}: worst |CSS − GPU| over the four readings {w:.4f}  {'inside' if w <= 0.005 else 'OUTSIDE'} 0.005")
