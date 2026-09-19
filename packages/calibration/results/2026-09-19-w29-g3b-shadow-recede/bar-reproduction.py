#!/usr/bin/env python3
"""W29 G3b — does this gate's bar reproduce G2's on the metrics G2 barred?

    python3 bar-reproduction.py > bar-reproduction.txt

The shadow axis is added to `NATIVE_DELTA_METRICS`, so `bar` re-derives the
thirty-one metrics G2 barred from the same raw runs on the way past. That the
two agree is a check and not an assumption: it is what says the instrument's
extension changed nothing about the readings the ledger already rests on, and a
disagreement would be a finding about this gate's own code rather than about the
bed.

G2's committed `noise-bar.json` is read and never written. It stays the bar its
verdicts were read against; this file only reports whether the new one says the
same thing where the two overlap.
"""
from __future__ import annotations

import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
RESULTS = HERE.parent

G2 = RESULTS / "2026-09-19-w29-g2-native-delta" / "noise-bar.json"
MINE = HERE / "noise-bar.json"

g2 = json.loads(G2.read_text())
mine = json.loads(MINE.read_text())

shared = [m for m in g2["metrics"] if m in mine["metrics"]]
added = [m for m in mine["metrics"] if m not in g2["metrics"]]
dropped = [m for m in g2["metrics"] if m not in mine["metrics"]]

print(f"G2  metrics {len(g2['metrics'])}, cells {len(g2['cells'])}")
print(f"G3b metrics {len(mine['metrics'])}, cells {len(mine['cells'])}")
print(f"shared {len(shared)}, added {len(added)}, dropped {len(dropped)}")
if dropped:
    print(f"DROPPED (a finding, not an addition): {', '.join(dropped)}")
print(f"added: {', '.join(added)}")
print()

index = {(c["profileKey"], c["sceneId"]): c for c in g2["cells"]}
missing = 0
compared = 0
disagree: list[tuple[str, str, str, str, float, float]] = []
presence = 0
for cell in mine["cells"]:
    key = (cell["profileKey"], cell["sceneId"])
    other = index.get(key)
    if other is None:
        missing += 1
        continue
    for block in ("pairwise", "runVsPublished"):
        for metric in shared:
            a = other[block].get(metric)
            b = cell[block].get(metric)
            if (a is None) != (b is None):
                presence += 1
                continue
            if a is None:
                continue
            for field in ("n", "min", "median", "p95", "max"):
                compared += 1
                if a[field] != b[field]:
                    disagree.append((key[0], key[1], block, f"{metric}.{field}", a[field], b[field]))
    for name, value in other["readingSpread"].items():
        compared += 1
        if cell["readingSpread"].get(name) != value:
            disagree.append((key[0], key[1], "readingSpread", name, value, cell["readingSpread"].get(name)))

print(f"cells in this bar with no G2 counterpart: {missing}")
print(f"readings compared: {compared}")
print(f"rows present in one bar and absent in the other: {presence}")
print(f"readings that disagree: {len(disagree)}")
for row in disagree[:40]:
    print("  ", row)

bed = 0
bed_bad = []
for metric in shared:
    a = g2["bedMinimumNonZeroBar"].get(metric)
    b = mine["bedMinimumNonZeroBar"].get(metric)
    bed += 1
    if a != b:
        bed_bad.append((metric, a, b))
print(f"bedMinimumNonZeroBar entries compared: {bed}, disagreeing: {len(bed_bad)}")
for row in bed_bad:
    print("  ", row)

verdict = "REPRODUCES" if not disagree and not bed_bad and not presence and not missing else "DISAGREES"
print()
print(f"verdict: this gate's bar {verdict} G2's on the thirty-one metrics they share.")
