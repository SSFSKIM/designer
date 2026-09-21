#!/usr/bin/env python3
"""W31 G4 — the accessibility rows against 0.20.0's, off the committed matrix (claims §5.165 §2).

    python3 accessibility-identity.py > accessibility-identity.txt

W31 G3c proved its stand-down at the RASTER — 48 of 48 PNGs identical to the
pre-fit tree — and in `standard-row-identity-matrix.txt`, whose generator is not
committed beside it (2026-09-21, G3c review, folded at G4; §5.165). This is the
same claim taken by a different route and from artefacts that are: the two
accessibility profiles' rows in `results/matrix.json`, field by field against the
0.20.0 generation the split moved to `results/superseded/d0c389d70456.json`.

It is the eye's other half. `eye.md` §1 says the four accessibility sheets show
no regression; this says how many numbers that sentence is standing on and
whether any of them moved. A field present on one side and absent on the other is
reported separately and NOT as a movement: this wave's instrument added 24
optional schema-5 fields, so every 0.21.0 row carries readings no 0.20.0 row
could have.
"""
from __future__ import annotations

import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
PACKAGE = HERE.parent.parent

PROFILES = {
    "apple-macos-27.0-1x-light-reduced-transparency-glass0.5",
    "apple-macos-27.0-1x-light-increased-contrast-coupled-glass0.5",
}
AXES = ("perceptual", "shape", "material", "shadow", "coherence")
BASELINE = "d0c389d70456.json"


def rows(path: Path) -> dict[tuple[str, str, str], dict]:
    return {
        (cell["key"]["profileKey"], cell["key"]["sceneId"], cell["tier"]): cell
        for cell in json.loads(path.read_text())["cells"]
        if cell["key"]["profileKey"] in PROFILES
    }


def main() -> int:
    current = rows(PACKAGE / "results" / "matrix.json")
    before = rows(PACKAGE / "results" / "superseded" / BASELINE)

    print("W31 G4 — the two macOS 27 accessibility profiles, 0.21.0 against 0.20.0")
    print(f"  0.21.0: results/matrix.json                      {len(current)} row(s)")
    print(f"  0.20.0: results/superseded/{BASELINE}   {len(before)} row(s)\n")

    compared = 0
    moved: list[str] = []
    added: dict[str, int] = {}
    missing: list[str] = []
    for key in sorted(current):
        if key not in before:
            missing.append(f"{key}: no 0.20.0 row")
            continue
        for axis in AXES:
            now = current[key].get(axis) or {}
            was = before[key].get(axis) or {}
            for field in sorted(set(now) | set(was)):
                a, b = now.get(field), was.get(field)
                if not isinstance(a, dict) or not isinstance(b, dict):
                    if isinstance(a, dict) and b is None:
                        added[field] = added.get(field, 0) + 1
                    elif isinstance(b, dict) and a is None:
                        missing.append(f"{key} :: {axis}.{field}: on the 0.20.0 row and not here")
                    continue
                compared += 1
                if a["value"] != b["value"]:
                    moved.append(
                        f"{key} :: {axis}.{field}: {b['value']} -> {a['value']}"
                    )

    print(f"  {compared} numeric readings compared, field for field, across every axis")
    print(f"  MOVED: {len(moved)}")
    for line in moved[:40]:
        print(f"    {line}")
    print(f"  rows or readings present at 0.20.0 and absent here: {len(missing)}")
    for line in missing[:20]:
        print(f"    {line}")
    print(f"\n  fields added by this wave's instrument (additions, not movements): {len(added)}")
    for field, count in sorted(added.items()):
        print(f"    {field:<36} on {count} row(s)")

    verdict = "IDENTICAL" if not moved and not missing else "*** SOMETHING MOVED ***"
    print(f"\n  {verdict}: the accessibility beds draw what 0.20.0 drew (W31 Decision Log 3 (d)).")
    return 0 if not moved and not missing else 1


if __name__ == "__main__":
    raise SystemExit(main())
