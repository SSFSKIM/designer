#!/usr/bin/env python3
"""Did the material axis's MASK move at this gate? — W32 G1 review closure, B-2.

`§5.168 §7` and two comments in `adopted-thresholds.test.ts` attributed M2's
first miss to the silhouette extractor: `interiorStdDev*` is read over the
extracted silhouette, the extractor thresholds the render against its
background, so — the argument went — removing a shadow moves which edge pixels
the mask takes. That argument requires a WEB-derived mask, and the material axis
does not use one: `cli/measure.ts` takes `const interior = nativeSil`, and the
doc comment above it says why in as many words — a mask that shifts as the web
side is tuned moves the native figure it is being compared against.

This script is the measurement that settles it. It compares the 726 rows this
gate's read superseded against the same 726 keys in the working file — the same
cells at two materials — and reports:

  * how many moved on `silhouetteAreaNative`, the mask the material axis uses;
  * how many moved on `silhouetteAreaWeb`, which the SHAPE axis uses and which is
    the only silhouette a material change can move;
  * the miss cell's own four shape readings on both sides.

Run from `packages/calibration`:

    python3 results/2026-09-21-w32-g1-shadow-fit/b2-mask.py

Reads only. The superseded files and the working matrix are committed evidence.
"""

from __future__ import annotations

import json
from pathlib import Path

PACKAGE = Path(__file__).resolve().parents[2]
SUPERSEDED = (
    PACKAGE / "results/superseded/49490eb9ff7a.json",
    PACKAGE / "results/superseded/b5714a866288.json",
)
WORKING = PACKAGE / "results/matrix.json"

MISS_CELL = (
    "apple-macos-27.0-1x-light-standard-glass0.5",
    "photo__rrect-sm__inactive",
    "texture",
)


def cells(path: Path) -> list[dict]:
    return json.loads(path.read_text())["cells"]


def key(cell: dict) -> tuple:
    k = cell["key"]
    return (
        k.get("profileKey"),
        k["web"].get("sceneId"),
        cell["tier"],
        cell.get("fixtureSet"),
        k["web"].get("renderer"),
    )


def value(cell: dict, axis: str, name: str):
    field = (cell.get(axis) or {}).get(name)
    return field["value"] if isinstance(field, dict) and "value" in field else None


def main() -> int:
    before: dict[tuple, dict] = {}
    for path in SUPERSEDED:
        for cell in cells(path):
            before[key(cell)] = cell
    after = {key(cell): cell for cell in cells(WORKING)}
    common = [k for k in before if k in after]

    print("W32 G1 review closure B-2 — the material axis's mask, before and after the fit")
    print("=" * 96)
    print(f"  superseded rows {len(before)}   working rows {len(after)}   "
          f"same keys on both sides {len(common)}")
    print()

    for field, axis_note in (
        ("silhouetteAreaNative", "the material axis's mask (`const interior = nativeSil`)"),
        ("silhouetteAreaWeb", "the shape axis's own silhouette — a material CAN move this"),
    ):
        paired = moved = 0
        for k in common:
            b, a = value(before[k], "shape", field), value(after[k], "shape", field)
            if b is None or a is None:
                continue
            paired += 1
            moved += b != a
        print(f"  {field:<22} on both sides {paired:>4}   moved {moved:>4}   — {axis_note}")
    print()

    print("  the miss cell — texture / photo__rrect-sm__inactive / 1x light standard:")
    hit_before = [before[k] for k in common if k[:3] == MISS_CELL]
    hit_after = [after[k] for k in common if k[:3] == MISS_CELL]
    for label, found in (("before", hit_before), ("after", hit_after)):
        if not found:
            print(f"    {label:<8}(absent)")
            continue
        cell = found[0]
        shape = {
            name: value(cell, "shape", name)
            for name in (
                "silhouetteAreaNative",
                "silhouetteAreaWeb",
                "componentRegionArea",
                "silhouetteIoU",
            )
        }
        print(f"    {label:<8}{shape}")
        print(f"    {'':8}interiorStdDevWeb {value(cell, 'material', 'interiorStdDevWeb')!r}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
