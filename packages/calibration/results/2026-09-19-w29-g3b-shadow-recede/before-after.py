#!/usr/bin/env python3
"""W29 G3b — this read against G3's, cell for cell, on the rows a bound is stated on.

    python3 before-after.py > before-after.txt

Both generations are in `results/matrix.json` — the read appended and rewrote
nothing — so this is a join on (profile, scene, tier) between the rows whose
`capturePath` names G3's sealed documents and the rows whose `capturePath` names
this child's. No number is recomputed; both sides are read off the committed file.

What it prints: the four whole-cell rows every 27 table gates, per profile per
tier, before and after; the population each side carries, because a cell that
measures on one side and not the other is a finding rather than a gap; and the
worst mover in both directions.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
PACKAGE = HERE.parent.parent

G3 = {"fa872c683f3e", "96b36eedf1c4"}
G3B = {"f42ddec1cf5a", "272d1b0c3e10"}
CLAUSE = re.compile(r"materialProfile=\S+ sha256:([0-9a-f]{12})")

METRICS = [
    ("perceptual", "ssimMean", 5),
    ("perceptual", "ssimOutside", 5),
    ("perceptual", "oklabDeltaEMean", 5),
    ("perceptual", "oklabDeltaEP95", 5),
    ("material", "interiorMeanNative", 4),
    ("material", "interiorMeanWeb", 4),
]

matrix = json.loads((PACKAGE / "results" / "matrix.json").read_text())

before: dict[tuple, dict] = {}
after: dict[tuple, dict] = {}
for cell in matrix["cells"]:
    profile = cell["key"]["profileKey"]
    if not profile.startswith("apple-macos-27.0-"):
        continue
    match = CLAUSE.search(cell["key"]["web"]["capturePath"])
    if match is None:
        continue
    index = (profile, cell["key"]["sceneId"], cell["tier"])
    if match.group(1) in G3:
        before[index] = cell
    elif match.group(1) in G3B:
        after[index] = cell


def at(cell: dict, axis: str, field: str) -> float | None:
    entry = (cell.get(axis) or {}).get(field)
    return entry["value"] if isinstance(entry, dict) else None


print(f"G3 generation: {len(before)} rows   G3b generation: {len(after)} rows")
only_before = sorted(set(before) - set(after))
only_after = sorted(set(after) - set(before))
print(f"rows G3 measured and this read did not: {len(only_before)}")
for index in only_before:
    print(f"    {index[0]:<62}{index[2]:<9}{index[1]}")
print(f"rows this read measured and G3 did not: {len(only_after)}")
for index in only_after:
    print(f"    {index[0]:<62}{index[2]:<9}{index[1]}")

shared = sorted(set(before) & set(after))
print(f"\nrows in both: {len(shared)}\n")

for axis, field, digits in METRICS:
    moves = []
    for index in shared:
        was, now = at(before[index], axis, field), at(after[index], axis, field)
        if was is None or now is None:
            continue
        moves.append((now - was, index, was, now))
    if not moves:
        continue
    moves.sort()
    mean = sum(abs(d) for d, *_ in moves) / len(moves)
    print(f"── {field} ── {len(moves)} cells, mean |Δ| {mean:.{digits}f}")
    for delta, index, was, now in moves[:4] + moves[-4:]:
        print(
            f"    {delta:+.{digits}f}  {was:.{digits}f} -> {now:.{digits}f}   "
            f"{index[0].replace('apple-macos-27.0-', ''):<44}{index[2]:<9}{index[1]}"
        )
    print()

# The active whole-cell summary each profile/tier is judged on, before and after.
print("\n── per profile per tier, the active rows a table gates ──")
print(f"{'profile / tier':<58}{'ssimMean worst':>18}{'ssimOutside worst':>20}{'ΔE mean, mean':>18}{'ΔE p95 worst':>16}")
profiles = sorted({index[0] for index in shared})
for profile in profiles:
    for tier in ("texture", "dom"):
        rows = [
            i
            for i in shared
            if i[0] == profile and i[2] == tier and before[i].get("state") != "inactive"
        ]
        rows = [i for i in rows if "__inactive" not in i[1] and before[i].get("fixtureSet") != "probe"]
        if not rows:
            continue

        def summary(side: dict[tuple, dict]) -> str:
            ssim = [at(side[i], "perceptual", "ssimMean") for i in rows]
            outside = [at(side[i], "perceptual", "ssimOutside") for i in rows]
            de = [at(side[i], "perceptual", "oklabDeltaEMean") for i in rows]
            p95 = [at(side[i], "perceptual", "oklabDeltaEP95") for i in rows]
            ssim = [v for v in ssim if v is not None]
            outside = [v for v in outside if v is not None]
            de = [v for v in de if v is not None]
            p95 = [v for v in p95 if v is not None]
            return (
                f"{min(ssim):>18.5f}{min(outside):>20.5f}"
                f"{sum(de) / len(de):>18.5f}{max(p95):>16.5f}"
            )

        label = f"{profile.replace('apple-macos-27.0-', '')} / {tier}"
        print(f"{label:<58}{summary(before)}   (G3)")
        print(f"{'':<58}{summary(after)}   (G3b, {len(rows)} cells)")
