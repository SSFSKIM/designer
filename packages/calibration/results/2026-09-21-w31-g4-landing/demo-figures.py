#!/usr/bin/env python3
"""W31 G4 — what the demo's calibration readout prints, before and after the wave.

    python3 demo-figures.py > demo-figures.txt

W30 G4's `demo-figures.py` (`results/2026-09-20-w30-g4-landing/demo-figures.py`),
copied on that directory's convention with the projection's list moved to what
this gate ships and the "before" generation moved to the one this wave started
from. It asks the page's own question of the committed evidence: on the scenes
the picker offers, what does the current generation print, and what did the
generation it superseded print?

**The "before" column is the PRE-FIT generation** — `results/superseded/
d0c389d70456.json` (the four light profiles) and `880ab1e31450.json` (the dark
pair), the rows read at the macOS 27 documents before any retention was fitted
into them, which is what the page printed at the 0.20.0 cut. Those rows carry no
`chromaStructureRatio*` at all, because the instrument entered the schema with
this wave — so the chroma pair reads "—" on the left, and that dash is the
finding rather than a gap in the script: **the page had no figure for the axis
0.21.0's operator moves**, which is the hole W30 G4 found on the shadow axis one
wave earlier and this gate closes one axis along.

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

# `matrix-reduction.ts`'s `PROJECTED`, axis for axis, at this gate's head.
PROJECTED = {
    "shape": ["silhouetteIoU", "contourDistanceMean", "contourDistanceP95"],
    "perceptual": ["ssimMean", "oklabDeltaEMean"],
    "material": [
        "luminanceSlopeNative",
        "luminanceSlopeWeb",
        # Added to the page by this gate (claims §5.165 §4), on W30 G4's rule
        # for the shadow pair: the wave's operator is not visible in any figure
        # above it.
        "chromaStructureRatioNative",
        "chromaStructureRatioWeb",
    ],
    "shadow": ["falloffSigmaNative", "falloffSigmaWeb"],
}

# The picker's scenes at the spans the retention's own residual runs along, plus
# one low-chroma backdrop as the control: `checkerboard` is a grey field, so its
# chroma pair should read near nothing on BOTH sides and a large movement there
# would be the operator reaching something it has no business in.
SCENES = [
    ("photo__rrect-sm__rest", 32),
    ("photo__capsule-button__rest", 44),
    ("photo__rrect-md__rest", 96),
    ("photo__rrect-lg__rest", 160),
    ("checkerboard__rrect-md__rest", 96),
]

BEFORE_FILES = ("d0c389d70456.json", "880ab1e31450.json")


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
    for name in BEFORE_FILES:
        before += load(SUPERSEDED / name)

    print("W31 G4 — the demo's calibration readout, at the wave's two ends")
    print("=" * 100)
    print()
    print("  after   packages/calibration/results/matrix.json (the generation the page reduces)")
    print(f"  before  results/superseded/{' + '.join(BEFORE_FILES)} — the PRE-FIT")
    print("          generation, what the page printed at the 0.20.0 cut")
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
                note = "  NEW AT THIS GATE" if bv is None and av is not None else ""
                print(
                    f"      {name:<36} "
                    f"{'—' if bv is None else f'{bv:.6f}':>12} -> "
                    f"{'—' if av is None else f'{av:.6f}':>12}   {delta}{note}"
                )
        print()


if __name__ == "__main__":
    main()
