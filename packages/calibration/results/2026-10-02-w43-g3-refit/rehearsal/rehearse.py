#!/usr/bin/env python3.12
"""W43 G3 (i), clause 10 step 2: the rehearsal of every cut on the pre-fit render.

The pre-fit render is the UNMOVED endpoint: the shipped 0.5 documents drawn on the 0.25 cells.
Every cut is read on it (``cuts.py --kind prefit``, the bed and the reference the same render), and
S1/R2 is read beside G2's perfect-endpoint map (``2026-10-02-w43-g2-reading/s1/s1-null.json``,
R2's row: Apple's own 0.25 in vitrea's place) and G2's offline unmoved-endpoint reading.

What "fails by construction" means here, declared before the read: a cut that NO endpoint the
ruling permits could pass. Two kinds are checked.
  (a) Against a perfect endpoint (Apple's own 0.25 pixels in vitrea's place): every cut is
      stated against Apple's reading (tables, M1, C1, X1, L1 absolute: error 0; M2: w = n is
      toward Apple and not past it, so within or named, never a failure; E2: residual 0 is
      never above the pre-fit's; L1 growth: error 0 cannot grow), except S1, whose sign clause
      G2 measured on the null. So (a) is S1's row, read from G2's map.
  (b) Against the ruled holds (Decision Log 7 items 6, 7 and 9; X44): a cut that fails on the
      pre-fit where its reading depends only on leaves the ruling holds (the outer shadow for
      C1 and X1's exterior; the contour and shape for the tables' shape rows) cannot be moved
      by any permitted candidate. Each pre-fit failure is listed with the mechanism it reads.

    python3.12 -B rehearse.py      # writes prefit-cuts.json/.txt and rehearsal.txt beside itself
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
EVIDENCE = HERE.parent
sys.path.insert(0, str(EVIDENCE / "cuts"))
import cuts  # noqa: E402

SCRATCH = Path.home() / "vitrea-w43" / "g3-scratch" / "prefit"
G2_NULL = EVIDENCE.parent / "2026-10-02-w43-g2-reading" / "s1" / "s1-null.json"

# The mechanism each table metric reads, for (b): rows whose reading the ruled holds fix.
HELD_METRICS = {"silhouetteIoU": "shape (geometry held; Apple's did not move, §5.200 §4)",
                "contourDistanceMean": "shape (geometry held)",
                "contourDistanceP95": "shape (geometry held)",
                "ssimOutside": "exterior (outer shadow held, item 7)"}


def main() -> int:
    out_json, out_txt = HERE / "prefit-cuts.json", HERE / "prefit-cuts.txt"
    cuts.main(["--bed", str(SCRATCH / "matrix.json"), "--kind", "prefit",
               "--captures", str(SCRATCH / "web-captures"),
               "--prefit", str(SCRATCH / "matrix.json"),
               "--prefit-captures", str(SCRATCH / "web-captures"),
               "--out", str(out_json), "--text", str(out_txt)])
    result = json.loads(out_json.read_text())
    g2 = json.loads(G2_NULL.read_text())["restated"]
    lines = ["W43 G3 (i) step 2: the rehearsal on the pre-fit render (the unmoved endpoint)", ""]
    lines.append("verdicts on the pre-fit render")
    for k, v in result["summary"].items():
        lines.append(f"  {k:<64} {v}")
    lines.append("")
    lines.append("S1 as R2, beside G2's map")
    for renderer in ("webgpu", "css"):
        s = result["S1"][renderer]
        null = g2.get(f"interiorMean/{renderer}/R2", {})
        lines.append(f"  {renderer}: population {s['population']}")
        lines.append(f"    perfect endpoint (G2, Apple's 0.25 in vitrea's place): median ratio "
                     f"{null.get('medianRatioNull')}, sign holds {null.get('signHoldsOnNull')}, "
                     f"passes {null.get('perfectEndpointPasses')}")
        lines.append(f"    unmoved endpoint, G2 offline (0.5 capture under the 0.25 silhouette): "
                     f"median ratio {null.get('medianRatioAnti')}, passes {null.get('unmovedEndpointPasses')}")
        lines.append(f"    unmoved endpoint, RENDERED here: median ratio {s['pooledMedianRatio']}, "
                     f"{len(s['wrongSign'])} of {s['measured']} wrong sign, verdict {s['verdict']}")
    lines.append("")
    lines.append("(b) pre-fit failures whose reading the ruled holds fix")
    held = []
    for pt, t in result["tables"].items():
        for miss in t["misses"]:
            if miss["metric"] in HELD_METRICS:
                held.append(f"  tables {pt}: {miss['scene']} {miss['metric']} {miss['measured']} vs "
                            f"{miss['bound']} -> {HELD_METRICS[miss['metric']]}")
    c1 = result["C1"]["webgpu"]
    for k, e in c1["perBedSpan"].items():
        if e["verdict"] == "MISS":
            held.append(f"  C1 {k}: {e['statistic']} > {cuts.C1_TOLERANCE} -> outer shadow held (item 7)")
    x1 = result["X1"]["webgpu"]
    for c in x1["failing"]:
        held.append(f"  X1 {c['cell']}: exterior above native black -> shadow held, black branch movable")
    lines += held or ["  none"]
    (HERE / "rehearsal.txt").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
