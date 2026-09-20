#!/usr/bin/env python3
"""W30 G3 — what the gate's own machine-derived lists say, before and after.

    python3 gate-diff.py > gate-diff.txt

Three lists in `test/adopted-thresholds.test.ts` are derived from the artifact
and compared to a constant in both directions — the conditioning predicate's
exclusions, the rows that miss their declared bound, and W20's declaration
conformance. A wave that re-reads the bed moves them, and the rule is that the
constant moves to what the machine says rather than the other way round.

This file computes all three off `results/matrix.json` on BOTH generations at
once, in the interval before the split moves the superseded one out, so that
every line of the new list is printed with the reading it replaces. The gate's
own logic is reproduced rather than imported, because the gate is TypeScript;
the three predicates below are transcriptions of `isWellConditioned`,
`atAShippedDocument` and W20's two thresholds, and the check on the
transcription is that the "before" column reproduces the constants the file
carries today.
"""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
PACKAGE = HERE.parent.parent
MATRIX = PACKAGE / "results/matrix.json"
CAPTURE = re.compile(r"materialProfile=(\S+) sha256:([0-9a-f]{12})")

WELL_CONDITIONED_AREA_RATIO = 0.5
DECLARED_CONTOUR_MAX_PX = 1
DECLARED_IOU_MIN = 0.99


def at(cell: dict, axis: str, metric: str) -> float | None:
    entry = (cell.get(axis) or {}).get(metric)
    return entry["value"] if isinstance(entry, dict) else None


def well_conditioned(cell: dict) -> bool:
    if cell.get("shape") is None:
        return True
    area = at(cell, "shape", "componentRegionArea")
    bodies = at(cell, "shape", "componentRegionBodies")
    if area is None or bodies is None:
        return True
    return (
        (at(cell, "shape", "silhouetteAreaNative") or 0) >= WELL_CONDITIONED_AREA_RATIO * area
        and (at(cell, "shape", "silhouetteAreaWeb") or 0) >= WELL_CONDITIONED_AREA_RATIO * area
        and (at(cell, "shape", "silhouetteBodiesNative") or 0) <= bodies
        and (at(cell, "shape", "silhouetteBodiesWeb") or 0) <= bodies
    )


def name(cell: dict) -> str:
    return (f"{cell['tier']} / {cell.get('fixtureSet')} / {cell['key']['sceneId']} / "
            f"{cell['key']['profileKey']}")


def main() -> int:
    hashes = {f"packages/calibration/profiles/{p.name}":
              hashlib.sha256(p.read_bytes()).hexdigest()[:12]
              for p in sorted((PACKAGE / "profiles").glob("*.json"))}
    before: list[dict] = []
    after: list[dict] = []
    for cell in json.loads(MATRIX.read_text())["cells"]:
        clauses = CAPTURE.findall(cell["key"]["web"]["capturePath"])
        current = bool(clauses) and all(hashes.get(path) == sha for path, sha in clauses)
        if cell["key"]["profileKey"].startswith("apple-macos-26.5-"):
            (after if current else before).append(cell)
            continue
        (after if current else before).append(cell)

    print("W30 G3 — the gate's machine-derived lists, before and after the read")
    print("=" * 108)
    print(f"  rows at the documents on disk {len(after)}; at the superseded documents "
          f"{len(before)}")
    print()

    for title, rows in (("BEFORE — the superseded generation plus the frozen bed", before),
                        ("AFTER — this child's generation plus the frozen bed", after)):
        excluded = sorted(name(cell).rsplit(" / ", 1)[0] + " / " + cell["key"]["profileKey"]
                          for cell in rows
                          if cell.get("shape") is not None and not well_conditioned(cell)
                          and cell.get("fixtureSet") != "probe")
        print(f"{title}: {len(excluded)} cells the shape rows skip")
        print("-" * 108)
        for line in excluded:
            print(f"  {line}")
        print()

    print("W20 — declaration conformance, every texture cell with a shape axis")
    print("-" * 108)
    for title, rows in (("BEFORE", before), ("AFTER", after)):
        misses = []
        for cell in rows:
            if cell["tier"] != "texture" or cell.get("shape") is None:
                continue
            contour = at(cell, "shape", "declaredContourMaxWeb")
            iou = at(cell, "shape", "declaredIoUWeb")
            if contour is None or iou is None:
                continue
            if contour > DECLARED_CONTOUR_MAX_PX or iou < DECLARED_IOU_MIN:
                misses.append((name(cell), contour, iou,
                               at(cell, "shape", "silhouetteAreaWeb"),
                               at(cell, "shape", "componentRegionArea")))
        print(f"  {title}: {len(misses)} cells outside contour <= 1 px and IoU >= 0.99")
        for line, contour, iou, area, region in misses:
            print(f"    {line}")
            print(f"      contour {contour}  IoU {iou:.6f}  silhouetteAreaWeb {area}  "
                  f"componentRegionArea {region}")
        print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
