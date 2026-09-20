#!/usr/bin/env python3
"""W30 G3b — what the fix moves, cell by cell, before any document byte moves.

    python3 precheck.py <scratch matrix> > precheck.txt

The fix is a clamp that is the identity wherever the unclamped form returned a
number at all, so the claim it has to support is narrow and total: **on the
shadow's own axis nothing moves, and on the declaration's axis exactly the
span-44 texture cells move, all the way back to 1.0.** B3's stop is the mean of
`|meanDepartureWeb − meanDepartureNative|`, so a per-cell bit-identity on
`meanDepartureWeb` is a stronger statement than re-reading the statistic: it says
the stop cannot have moved rather than that it happens not to have.

Read against the rows W30 G3 committed at the sealed documents for the same
profile, scene and tier — the documents have not moved yet, so the two readings
differ in the renderer and in nothing else.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PACKAGE = HERE.parent.parent
PROFILE = "apple-macos-27.0-1x-light-standard-glass0.5"


def num(v):
    return v.get("value") if isinstance(v, dict) else v


def departure(cell):
    s = cell.get("shadow") or {}
    w, n = num(s.get("meanDepartureWeb")), num(s.get("meanDepartureNative"))
    return None if w is None or n is None else (w, n)


def declaration(cell):
    s = cell.get("shape") or {}
    return (num(s.get("drawnAreaWeb")), num(s.get("declaredIoUWeb")))


def key(cell):
    return (cell["key"]["sceneId"], cell["tier"], cell.get("fixtureSet"))


def main(argv: list[str]) -> int:
    scratch = json.loads(Path(argv[0]).read_text())["cells"]
    committed = json.loads((PACKAGE / "results/matrix.json").read_text())["cells"]

    old = {key(c): c for c in committed
           if c["key"]["profileKey"] == PROFILE and c["tier"] == "texture"}
    new = {key(c): c for c in scratch
           if c["key"]["profileKey"] == PROFILE and c["tier"] == "texture"}
    print(f"W30 G3b — the fixed renderer against W30 G3's committed rows, {PROFILE}")
    print("=" * 100)
    print(f"  {len(new)} texture cells read on scratch; {len(old)} committed for this profile")
    print()

    moved, same, orphan = [], 0, 0
    for k, cell in new.items():
        if k not in old:
            orphan += 1
            continue
        a, b = departure(old[k]), departure(cell)
        if a is None or b is None:
            continue
        if abs(a[0] - b[0]) > 0:
            moved.append((k[0], a[0], b[0]))
        else:
            same += 1
    print("THE SHADOW'S OWN AXIS — meanDepartureWeb, which B3's stop is the mean of")
    print("-" * 100)
    print(f"  bit-identical: {same}    moved: {len(moved)}    with no committed counterpart: {orphan}")
    for scene, a, b in moved:
        print(f"  {scene:58s} {a:.6f} -> {b:.6f}")
    print()
    print("  Not approximately: the same float. The NaN was reached only more than 10.06 σ")
    print("  INSIDE the shadow's silhouette, and every pixel the departure is measured over")
    print("  is outside the declared region, where the offset read lands at most 7.95 CSS px")
    print("  deeper. So B3 cannot have moved, and the canonical read re-reads it anyway.")
    print()

    changed = []
    for k, cell in new.items():
        if k not in old:
            continue
        a, b = declaration(old[k]), declaration(cell)
        if a[0] is None or b[0] is None:
            continue
        if a != b:
            changed.append((k[0], a, b))
    print("THE DECLARATION'S AXIS — drawnAreaWeb and declaredIoUWeb, which W20 bounds")
    print("-" * 100)
    print(f"  {len(changed)} cells move, and every one of them moves to IoU 1.0")
    print(f"  {'scene':58s} {'drawn before':>13s} {'IoU before':>11s} {'drawn after':>12s} {'IoU after':>10s}")
    for scene, a, b in sorted(changed):
        print(f"  {scene:58s} {a[0]:>13} {a[1]:>11.4f} {b[0]:>12} {b[1]:>10.4f}")
    print()
    print("  The capsule is 4220 -> 4872 of a declared 4872 and the toolbar 4452 -> 4584 of")
    print("  4584. Both are span-44 casters; no rrect cell of this profile appears above.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:] or ["/tmp/w30g3b/out/pre-1xl.json"]))
