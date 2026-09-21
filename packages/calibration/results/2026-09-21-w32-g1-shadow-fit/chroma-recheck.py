#!/usr/bin/env python3
"""W32 G1 — M1 and M2 re-derived from a matrix, so "unmoved" has a before and an after.

    python3 chroma-recheck.py <matrix.json> [<matrix.json> ...]

`stops.py` §4 reads M1 and M2 out of **W31 G4's committed `chroma-cut.json`** —
the cut `adopted-thresholds.test.ts` points at — and that is the right thing for
a stop's declared reading, because the cut's population is a filtered one and a
second implementation of the filter would be a second thing to keep true. It is
the wrong thing for a BEFORE and an AFTER: the committed cut is one number and
does not move when a round does.

So this file re-derives the two quantities from a matrix, cell by cell, over the
cut's own population, and prints them per profile. The population is taken FROM
the cut rather than restated — every cell the cut names — so the two readings are
of the same cells and only the material differs. A cell the cut names and the
matrix does not carry is counted and named.

`R` is `chromaStructureRatioWeb / chromaStructureRatioNative`, M1's quantity.
`interiorStdDevWeb` is M2's; M2's bound is a fraction of the PRE-FIT generation's
value, which the cut carries as `structureDeltaFraction` and which this file does
not recompute — what it prints is the raw `interiorStdDevWeb`, so a move is
visible as a move whatever the reference.

The authority remains `adopted-thresholds.test.ts`, which re-reads every cell
from `results/matrix.json` and asserts to twelve places. This file is a reading
for the verdict, not a gate.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from statistics import median

HERE = Path(__file__).resolve().parent
PACKAGE = HERE.parent.parent
CHROMA_CUT = PACKAGE / "results/2026-09-21-w31-g4-landing/chroma-cut.json"


def value(axis, name):
    field = (axis or {}).get(name)
    return field["value"] if isinstance(field, dict) and "value" in field else None


def main(argv) -> int:
    if not argv:
        raise SystemExit(__doc__)
    cut = json.loads(CHROMA_CUT.read_text())
    rows = cut.get("rows") or cut.get("cells") or []
    wanted = {(r["profile"], r["scene"]) for r in rows if "profile" in r and "scene" in r}
    if not wanted:
        raise SystemExit(f"chroma-recheck: no (profile, scene) pairs in {CHROMA_CUT}")

    print("W32 G1 — M1 and M2 re-derived from the matrix, over W31 G4's own population")
    print("=" * 110)
    print(f"  population {len(wanted)} cells, from {CHROMA_CUT.relative_to(PACKAGE.parent.parent)}")
    print()
    for path in argv:
        matrix = json.loads(Path(path).read_text())
        per_profile: dict[str, list[tuple[float, float]]] = {}
        seen = set()
        for cell in matrix["cells"]:
            key = (cell["key"]["profileKey"], cell["key"]["sceneId"])
            if key not in wanted or cell["tier"] != "texture":
                continue
            seen.add(key)
            material = cell.get("material") or {}
            native = value(material, "chromaStructureRatioNative")
            web = value(material, "chromaStructureRatioWeb")
            sd = value(material, "interiorStdDevWeb")
            if native is None or web is None or not native:
                continue
            per_profile.setdefault(key[0], []).append((web / native, sd if sd is not None else 0.0))
        print(f"  {path}")
        print(f"    {'profile':<58}{'n':>4}{'median R':>11}{'min':>10}{'max':>10}"
              f"{'median sdW':>12}")
        for profile in sorted(per_profile):
            values = per_profile[profile]
            ratios = [v[0] for v in values]
            print(f"    {profile:<58}{len(values):>4}{median(ratios):>11.5f}"
                  f"{min(ratios):>10.5f}{max(ratios):>10.5f}"
                  f"{median(v[1] for v in values):>12.5f}")
        missing = sorted(wanted - seen)
        print(f"    {len(missing)} of the cut's cells are not in this matrix"
              + ("" if not missing else ":"))
        for key in missing[:10]:
            print(f"      absent  {key[0]} {key[1]}")
        print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
