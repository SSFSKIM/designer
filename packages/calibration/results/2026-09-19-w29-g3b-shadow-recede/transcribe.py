#!/usr/bin/env python3
"""W29 G3b — the two lists the gate says are the machine's output, printed for transcription.

    python3 transcribe.py > transcribe.txt

`MISSED_27_ROWS` and `PREDICATE_EXCLUDES` are not chosen — the gate file's own
header says they are transcribed from the canonical run. After a read that moves
either, somebody has to produce them; doing it by hand over 458 cells is how a
line goes wrong. This prints both in the gate file's exact string form, from the
committed matrix, under the same three drops the gate applies (the probe set, the
inactive pose, and a generation whose document is no longer on disk).

The declared tables are parsed out of `adopted-thresholds.test.ts` itself by
G3's `referee.py`, imported rather than re-implemented, so this file holds no
copy of a threshold either.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PACKAGE = HERE.parent.parent
REPO = PACKAGE.parents[1]

sys.path.insert(0, str(PACKAGE / "results" / "2026-09-19-w29-g3-refit"))
from importlib import import_module

referee = import_module("referee")

WELL_CONDITIONED_AREA_RATIO = 0.95
CLAUSE = re.compile(r"materialProfile=(\S+) sha256:([0-9a-f]{12})")

import hashlib

shipped = {}
for file in sorted((PACKAGE / "profiles").glob("*.json")):
    rel = f"packages/calibration/profiles/{file.name}"
    shipped[rel] = hashlib.sha256(file.read_bytes()).hexdigest()[:12]

spec = json.loads((REPO / "apps" / "reference-apple" / "scenes.json").read_text())
inactive = {s["id"] for s in spec["scenes"] if s["state"] == "inactive"}

matrix = json.loads((PACKAGE / "results" / "matrix.json").read_text())


def at_shipped(cell: dict) -> bool:
    match = CLAUSE.search(cell["key"]["web"]["capturePath"])
    return match is not None and shipped.get(match.group(1)) == match.group(2)


cells = [
    c
    for c in matrix["cells"]
    if c.get("fixtureSet") != "probe"
    and c.get("state") != "inactive"
    and c["key"]["sceneId"] not in inactive
    and at_shipped(c)
]
print(f"# gated bed: {len(cells)} cells")

tables, profiles = referee.declared()
name = lambda c: f"{c['tier']} / {c['fixtureSet']} / {c['key']['sceneId']} / {c['key']['profileKey']}"

# ---- MATRIX_PARTITION ------------------------------------------------------
partition: dict[str, int] = {}
for c in cells:
    partition[c["key"]["profileKey"]] = partition.get(c["key"]["profileKey"], 0) + 1
print("\nconst MATRIX_PARTITION: Readonly<Record<string, number>> = {")
for key in sorted(partition):
    print(f'  "{key}": {partition[key]},')
print("};")
print(f"\nconst MATRIX_CELLS = {len(cells)};")

per_tier: dict[tuple[str, str], int] = {}
for c in cells:
    per_tier[(c["key"]["profileKey"], c["tier"])] = per_tier.get((c["key"]["profileKey"], c["tier"]), 0) + 1
print("\n# cells per profile per tier (the `cells` field of each declared profile)")
for key in sorted(per_tier):
    print(f"#   {key[0]:<62}{key[1]:<9}{per_tier[key]}")

# ---- PREDICATE_EXCLUDES ----------------------------------------------------
excluded = []
for c in cells:
    shape = c.get("shape")
    if not shape:
        continue
    value = lambda m: (shape.get(m) or {}).get("value")
    floor = WELL_CONDITIONED_AREA_RATIO * value("componentRegionArea")
    ok = (
        value("silhouetteAreaNative") >= floor
        and value("silhouetteAreaWeb") >= floor
        and value("silhouetteBodiesNative") <= value("componentRegionBodies")
        and value("silhouetteBodiesWeb") <= value("componentRegionBodies")
    )
    if not ok:
        excluded.append(name(c))
print(f"\nconst PREDICATE_EXCLUDES = [   // {len(excluded)} lines")
for line in sorted(excluded):
    print(f'  "{line}",')
print("] as const;")

# ---- MISSED_27_ROWS --------------------------------------------------------
missed: dict[str, tuple[float, str]] = {}
for key in sorted(profiles):
    for tier, renderer in (("texture", "texture"), ("dom", "dom")):
        table = tables[profiles[key][tier]]
        mine = [c for c in cells if c["key"]["profileKey"] == key and c["tier"] == tier]
        for axis, metric, cmp, bound in table:
            for c in mine:
                if axis == "shape" and name(c) in excluded:
                    continue
                value = referee.value(c, axis, metric)
                if value is None:
                    continue
                if (value < bound) if cmp == "≥" else (value > bound):
                    missed[f"{name(c)} :: {metric}"] = (round(value, 5), f"{cmp} {bound}")
print(f"\nconst MISSED_27_ROWS: Readonly<Record<string, MissedRow>> = {{   // {len(missed)} rows")
for key in sorted(missed):
    value, bound = missed[key]
    print(f'  "{key}": {{ measured: {value}, bound: "{bound}" }},')
print("};")
