#!/usr/bin/env python3
"""W30 G3b — WHICH cells the fix moved, and the claim that it is only the deep ones.

    python3 moved-cells.py > moved-cells.txt

Run BEFORE the split, while `results/matrix.json` holds both generations: W30
G3's read at the four documents before their `$comment-w30-g3b`, and this gate's
read at the four after it. Same material, same documents' values, same machine,
one renderer fix between them — so every cell that moves is the fix, and the
claim `diagnosis.md` makes is falsifiable here in one line.

The claim: **a cell moves if and only if its component is a span-44 caster**
(`capsule-button`, or `toolbar-group`, whose three members are 44 × 44). Every
other component in the bed is either shallower than 10.06 σ — `rrect-sm` at span
32, where the σ law's floor puts 10.06 σ at 21.4 CSS px against a half-depth of
16 — or wide enough that its own σ grows faster than its depth.

`--per-metric` prints the per-metric tally instead of the per-cell one.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PACKAGE = HERE.parent.parent
MATRIX = PACKAGE / "results/matrix.json"
PROFILES = PACKAGE / "profiles"
CLAUSE = re.compile(r"(?:materialProfile|recededProfile)=(\S+) sha256:([0-9a-f]{12})")
AXES = ("shape", "perceptual", "material", "shadow", "tierCoherence", "motion")

# The bed's components, by the span each casts. `apps/reference-apple/scenes.json`
# is the source; the two deep-enough ones are named so the claim can fail.
SPAN_44 = ("capsule-button", "toolbar-group")


def sha12(path: Path) -> str:
    import hashlib

    return hashlib.sha256(path.read_bytes()).hexdigest()[:12]


def current() -> dict[str, str]:
    return {
        f"packages/calibration/profiles/{p.name}": sha12(p)
        for p in sorted(PROFILES.glob("*.json"))
    }


def generation(cell: dict, hashes: dict[str, str]) -> str:
    named = CLAUSE.findall(cell["key"]["web"]["capturePath"])
    if not named:
        return "unkeyed"
    return "after" if all(hashes.get(k) == v for k, v in named) else "before"


def numbers(cell: dict) -> dict[str, float]:
    out: dict[str, float] = {}
    for axis in AXES:
        block = cell.get(axis)
        if not isinstance(block, dict):
            continue
        for name, value in block.items():
            if isinstance(value, dict) and isinstance(value.get("value"), (int, float)):
                out[f"{axis}.{name}"] = value["value"]
    return out


def main(argv: list[str]) -> int:
    hashes = current()
    before: dict[tuple, dict] = {}
    after: dict[tuple, dict] = {}
    for cell in json.loads(MATRIX.read_text())["cells"]:
        if not cell["key"]["profileKey"].startswith("apple-macos-27.0-"):
            continue
        side = generation(cell, hashes)
        key = (cell["key"]["profileKey"], cell["key"]["sceneId"], cell["tier"])
        (after if side == "after" else before)[key] = cell

    paired = sorted(set(before) & set(after))
    moved_cells, still_cells = [], []
    per_metric: dict[str, int] = {}
    for key in paired:
        a, b = numbers(before[key]), numbers(after[key])
        moved = [name for name in sorted(set(a) & set(b)) if a[name] != b[name]]
        if moved:
            moved_cells.append((key, moved))
            for name in moved:
                per_metric[name] = per_metric.get(name, 0) + 1
        else:
            still_cells.append(key)

    print("W30 G3b — the cells the renderer fix moved, over one read of results/matrix.json")
    print("=" * 100)
    print(f"  {len(paired)} cells present in both generations; "
          f"{len(moved_cells)} moved, {len(still_cells)} bit-identical")
    print()

    def component(scene: str) -> str:
        return scene.split("__")[1] if "__" in scene else scene

    wrong_moved = [k for k, _ in moved_cells if component(k[1]) not in SPAN_44]
    wrong_still = [k for k in still_cells if component(k[1]) in SPAN_44 and k[2] == "texture"]
    print("THE CLAIM — a cell moves if and only if it casts at span 44")
    print("-" * 100)
    print(f"  moved and NOT a span-44 caster:        {len(wrong_moved)}")
    for key in wrong_moved[:20]:
        print(f"    {key[1]} / {key[0]} / {key[2]}")
    print(f"  a span-44 texture cell that did NOT move: {len(wrong_still)}")
    for key in wrong_still[:20]:
        print(f"    {key[1]} / {key[0]} / {key[2]}")
    print()
    print("  (A span-44 cell on the `dom` tier is expected NOT to move: the CSS tier has no")
    print("   shader and never evaluated the falloff for a pixel.)")
    print()

    if "--per-metric" in argv:
        print("Per metric, how many cells moved")
        print("-" * 100)
        for name, count in sorted(per_metric.items(), key=lambda kv: -kv[1]):
            print(f"  {name:44s}{count:>6}")
        print()

    print("Every moved cell")
    print("-" * 100)
    for key, moved in moved_cells:
        print(f"  {key[1]:52s}{key[2]:9s}{key[0]}")
        print(f"      {len(moved)} metrics: {', '.join(moved)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
