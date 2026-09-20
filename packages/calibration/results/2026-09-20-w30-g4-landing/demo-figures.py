#!/usr/bin/env python3
"""W30 G4 — what the demo's calibration readout prints, before and after the wave.

    python3 demo-figures.py > demo-figures.txt

The page's figures are `figuresOf`'s seven metrics on the PRIMARY cell of a
scene — the texture tier under the profile of the scheme the page draws — and
since claims §5.159b §8 they arrive through `apps/demo/matrix-reduction.ts`, a
build-time projection of the same rows. So this file asks the projection's own
question of the committed evidence: for the scenes whose casting span the σ law
moved most, what does the current generation print, and what did the generation
it superseded print?

The "before" column is `results/superseded/f42ddec1cf5a.json` and
`.../272d1b0c3e10.json` — W29 G3b's rows at the documents 0.19.0 shipped, which
is what the page printed at that cut (the index names both `readUnderClaims`
c9a §5.154). The "after" column is the working file, W30 G3b's read at the
sealed macOS 27 documents. Both are read with the reduction's own filters:
primary profile, texture tier, and the seven projected metrics.

Nothing is written but this report; no row is read that the page would not show.
"""
from __future__ import annotations

import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
RESULTS = HERE.parent
MATRIX = RESULTS / "matrix.json"
SUPERSEDED = RESULTS / "superseded"

# The page's rule (`calibration.ts`'s `PRIMARY_PROFILE_KEY_BY_SCHEME`).
PRIMARY = {
    "light": "apple-macos-27.0-1x-light-standard-glass0.5",
    "dark": "apple-macos-27.0-1x-dark-standard-glass0.5",
}
TIER = "texture"

# `matrix-reduction.ts`'s `PROJECTED`, axis for axis.
PROJECTED = {
    "shape": ["silhouetteIoU", "contourDistanceMean", "contourDistanceP95"],
    "perceptual": ["ssimMean", "oklabDeltaEMean"],
    "material": ["luminanceSlopeNative", "luminanceSlopeWeb"],
    # Added to the page by this gate (claims §5.160): the σ law is the wave's
    # headline operator and not one of the seven figures above could see it.
    "shadow": ["falloffSigmaNative", "falloffSigmaWeb"],
}

# The spans are `apps/reference-apple/scenes.json`'s components; these are the
# picker's scenes at the two ends of the σ law — the thin regime the law
# re-shaped most and the thick regime where it grew the reach by a third.
SCENES = [
    ("checkerboard__capsule-button__rest", 44),
    ("photo__capsule-button__rest", 44),
    ("checkerboard__rrect-lg__rest", 160),
    ("photo__rrect-lg__rest", 160),
    ("checkerboard__rrect-sm__rest", 32),
    ("checkerboard__rrect-md__rest", 96),
]


def load(path: Path) -> list[dict]:
    return json.loads(path.read_text())["cells"]


def pick(cells: list[dict], scene: str, profile: str) -> dict | None:
    for cell in cells:
        key = cell["key"]
        if key["sceneId"] == scene and key["profileKey"] == profile and cell["tier"] == TIER:
            return cell
    return None


def figures(cell: dict | None) -> dict[str, float | None]:
    out: dict[str, float | None] = {}
    for axis, names in PROJECTED.items():
        for name in names:
            value = None
            if cell is not None:
                found = (cell.get(axis) or {}).get(name)
                if isinstance(found, dict):
                    value = found["value"]
            out[f"{axis}.{name}"] = value
    return out


def main() -> None:
    after = load(MATRIX)
    before: list[dict] = []
    for name in ("f42ddec1cf5a.json", "272d1b0c3e10.json"):
        before += load(SUPERSEDED / name)

    print("W30 G4 — the demo's calibration readout, at the wave's two ends")
    print("=" * 100)
    print()
    print("  after   packages/calibration/results/matrix.json (the generation the page reduces)")
    print("  before  results/superseded/f42ddec1cf5a.json + 272d1b0c3e10.json (W29 G3b's rows,")
    print("          what the page printed at the 0.19.0 cut)")
    print("  rule    primary profile per scheme, texture tier, `matrix-reduction.ts`'s PROJECTED")
    print()

    for scheme, profile in PRIMARY.items():
        print(f"{scheme} scheme — {profile}")
        print("-" * 100)
        for scene, span in SCENES:
            a = figures(pick(after, scene, profile))
            b = figures(pick(before, scene, profile))
            if all(value is None for value in a.values()) and all(
                value is None for value in b.values()
            ):
                print(f"  {scene:<44} span {span:>3}   no cell in either generation")
                continue
            print(f"  {scene:<44} span {span:>3}")
            for name in a:
                av, bv = a[name], b[name]
                if av is None and bv is None:
                    continue
                delta = "" if av is None or bv is None else f"{av - bv:+.6f}"
                print(
                    f"      {name:<36} "
                    f"{'—' if bv is None else f'{bv:.6f}':>12} -> "
                    f"{'—' if av is None else f'{av:.6f}':>12}   {delta}"
                )
        print()


if __name__ == "__main__":
    main()
