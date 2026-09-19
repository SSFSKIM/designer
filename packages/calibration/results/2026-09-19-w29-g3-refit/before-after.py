#!/usr/bin/env python3
"""W29 G3 — what the refit moved, per profile per tier, on the same cells.

    python3 before-after.py <baseline-matrix.json>

"Before" is the 27 bed read against the material vitrea shipped for macOS 26.5 —
the honest baseline, because that is what a page drew on a 27 machine the day the
OS landed. "After" is the canonical matrix's 27 rows. Both are restricted to the
cells the two runs share, so the comparison is per cell and not per population;
the baseline never read holdout, so holdout is out of it on both sides.
"""
from __future__ import annotations

import json
import statistics
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
METRICS = ["ssimMean", "oklabDeltaEMean", "oklabDeltaEP95", "edgeWeightedMean", "ssimOutside"]


def index(path: Path) -> dict:
    out = {}
    for c in json.loads(path.read_text())["cells"]:
        if not c["key"]["profileKey"].startswith("apple-macos-27.0-"):
            continue
        if c.get("fixtureSet") == "probe" or c.get("state") == "inactive":
            continue
        out[(c["key"]["profileKey"], c["tier"], c["key"]["sceneId"])] = c
    return out


before = index(Path(sys.argv[1]))
after = index(ROOT / "results" / "matrix.json")
shared = sorted(set(before) & set(after))
print(f"{len(shared)} cells read both before and after\n")

profiles = sorted({k[0] for k in shared})
for profile in profiles:
    for tier in ("texture", "dom"):
        keys = [k for k in shared if k[0] == profile and k[1] == tier]
        if not keys:
            continue
        print(f"{profile} / {tier}  ({len(keys)} cells)")
        for metric in METRICS:
            pairs = [
                (before[k]["perceptual"][metric]["value"], after[k]["perceptual"][metric]["value"])
                for k in keys
                if metric in before[k].get("perceptual", {}) and metric in after[k].get("perceptual", {})
            ]
            if not pairs:
                continue
            worse_is_lower = metric.startswith("ssim")
            b = [p[0] for p in pairs]
            a = [p[1] for p in pairs]
            worst = (min, min) if worse_is_lower else (max, max)
            print(
                f"  {metric:<18} mean {statistics.mean(b):.5f} → {statistics.mean(a):.5f}"
                f"   worst {worst[0](b):.5f} → {worst[1](a):.5f}"
            )
        print()
