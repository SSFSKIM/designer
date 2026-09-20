#!/usr/bin/env python3
"""W30 G3 — the scatter's shape, chosen on the pitch ladder read at a macOS 27 document.

    VITREA_G3_SCRATCH=/tmp/w30g3 python3 scatter-solve.py <label> [<label> ...]

This is the reading W30 G0 could not have. The macOS 27 generation of
`results/matrix.json` carries no probe row at all (claims §5.156 §3), so the
pitch ladder — the only evidence that can identify a scale-selective scatter —
had never been read at a macOS 27 material, and the cut could not choose between
the two candidates the spanning set spans. Every label named here is the same 45
ladder scenes at the same fitted shadow with one scatter leaf moved, so the
column differences are the operator's own response and nothing else.

The quantity is B4's: `interiorStdDevWeb / interiorStdDevNative`, linear light
over the shared mask, per backdrop per bed. Above 1 vitrea passes more of the
backdrop's structure than Apple does; below 1 it passes less. The thick spans
(96, 128, 160) are printed apart from the thin ones because `sizeThickness` has
saturated there and the 2x trio has taken over — which is where the scale axis
§5.156 §3 found lives.

**What a column difference means, per candidate.** `sizeScatterScaleGain` adds
`gain · (edgeDensity − ref)` to `kScatter`, the deep component's share, so its
response per source is proportional to that source's own edge density: a reading
at one gain and a reference of 0 IS a measurement of the edge density per source,
up to the constant the gain sets. `sizeHeavySecondShare` mixes a second heavy
sample at its own width into the deep colour, so its response is a mid-band one
whose sign turns on whether that width is narrower or wider than the first.
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PACKAGE = HERE.parent.parent
ROOT = PACKAGE.parent.parent
SCENES = ROOT / "apps/reference-apple/scenes.json"
SCRATCH = Path(os.environ.get("VITREA_G3_SCRATCH", "/tmp/g3scratch"))

sys.path.insert(0, str(HERE.parent / "2026-09-19-w29-g3-refit"))
from fit import cells as fit_cells  # noqa: E402

PITCH = {
    "checkerboard-4": 4, "hc-text-7": 7, "checkerboard-8": 8, "hc-text": 14,
    "checkerboard": 16, "checkerboard-lc16": 16, "hc-text-28": 28,
    "checkerboard-32": 32, "checkerboard-64": 64,
}
THICK = (96, 128, 160)


def spans() -> dict[str, float]:
    spec = json.loads(SCENES.read_text())
    return {name: float(min(c["size"])) for name, c in spec["components"].items()
            if isinstance(c.get("size"), list) and len(c["size"]) == 2}


def at(block: dict, name: str) -> float | None:
    entry = (block or {}).get(name)
    return entry["value"] if isinstance(entry, dict) else None


def bed_of(profile: str) -> str:
    return profile.replace("apple-macos-27.0-", "").replace("-standard-glass0.5", "")


def median(values: list[float]) -> float:
    return sorted(values)[len(values) // 2]


def main(labels: list[str]) -> int:
    component_span = spans()
    rows: list[dict] = []
    for label in labels:
        for matrix in sorted((SCRATCH / "fit-log" / label).glob("*.json")):
            for cell in fit_cells(matrix):
                material = cell.get("material") or {}
                native, web = at(material, "interiorStdDevNative"), at(material, "interiorStdDevWeb")
                if native is None or web is None or native == 0:
                    continue
                if (cell.get("state") or "rest") == "inactive":
                    continue
                scene = cell["key"]["sceneId"]
                parts = scene.split("__")
                rows.append({
                    "label": label,
                    "bed": bed_of(cell["key"]["profileKey"]),
                    "tier": "webgpu" if cell["tier"] == "texture" else "css",
                    "scene": scene,
                    "backdrop": parts[0],
                    "pitch": PITCH.get(parts[0]),
                    "span": component_span.get(parts[1]) if len(parts) > 1 else None,
                    "ratio": web / native,
                })

    print(f"W30 G3 — the structure ratio on the ladder, per backdrop per bed: "
          f"{', '.join(labels)}")
    print("=" * 112)
    print(f"  {len(rows)} active ladder rows over {len(labels)} labels")
    print()

    backdrops = sorted({r["backdrop"] for r in rows},
                       key=lambda b: (PITCH.get(b) or 1e9, b))
    for tier in ("webgpu", "css"):
        here = [r for r in rows if r["tier"] == tier]
        if not here:
            continue
        print(f"{tier} tier — thick spans (96/128/160) only, median W/N per backdrop")
        print("-" * 112)
        print(f"  {'bed':<22}{'backdrop':<20}" + "".join(f"{label[-12:]:>16}" for label in labels))
        for bed in sorted({r["bed"] for r in here}):
            for backdrop in backdrops:
                cells = {
                    label: [r["ratio"] for r in here
                            if r["bed"] == bed and r["backdrop"] == backdrop
                            and r["label"] == label and r["span"] in THICK]
                    for label in labels
                }
                if not any(cells.values()):
                    continue
                line = f"  {bed:<22}{backdrop:<20}"
                for label in labels:
                    line += (f"{'—':>16}" if not cells[label]
                             else f"{median(cells[label]):>12.3f} ({len(cells[label]):>1})")
                print(line)
            print()
        print()

    print("The response per backdrop, as a difference from the first label")
    print("-" * 112)
    base = labels[0]
    for tier in ("webgpu", "css"):
        here = [r for r in rows if r["tier"] == tier]
        if not here:
            continue
        for bed in sorted({r["bed"] for r in here}):
            print(f"  {tier} / {bed}")
            print(f"    {'backdrop':<20}{'base':>10}"
                  + "".join(f"{('Δ ' + label[-10:]):>16}" for label in labels[1:]))
            for backdrop in backdrops:
                values = {}
                for label in labels:
                    cells = [r["ratio"] for r in here
                             if r["bed"] == bed and r["backdrop"] == backdrop
                             and r["label"] == label and r["span"] in THICK]
                    if cells:
                        values[label] = median(cells)
                if base not in values:
                    continue
                line = f"    {backdrop:<20}{values[base]:>10.3f}"
                for label in labels[1:]:
                    line += ("—".rjust(16) if label not in values
                             else f"{values[label] - values[base]:>+16.3f}")
                print(line)
            print()
    print("The bed's own aggregate, per label: mean |ln(W/N)| over the thick ladder rows")
    print("-" * 112)
    print("  B4 is reported per pitch and bounded on one cell, so choosing between candidates")
    print("  needs one number per bed. This is it: the mean absolute log ratio over every")
    print("  structured backdrop at the thick spans, which is symmetric in 'passes twice as")
    print("  much' and 'passes half as much' where a plain difference is not. The gated 16 px")
    print("  cell is printed beside it because that is the cell the clause is stated on.")
    print()
    import math

    print(f"  {'bed':<22}{'quantity':<26}" + "".join(f"{label[-14:]:>16}" for label in labels))
    for bed in sorted({r["bed"] for r in rows if r["tier"] == "webgpu"}):
        for title, keep in (
            ("mean |ln W/N|, ladder", lambda r: r["pitch"] is not None and r["span"] in THICK),
            ("worst |ln W/N|, ladder", lambda r: r["pitch"] is not None and r["span"] in THICK),
            ("gated checkerboard 16", lambda r: r["scene"] == "checkerboard__rrect-md__rest"),
        ):
            line = f"  {bed:<22}{title:<26}"
            for label in labels:
                sel = [abs(math.log(r["ratio"])) for r in rows
                       if r["tier"] == "webgpu" and r["bed"] == bed and r["label"] == label
                       and keep(r) and r["ratio"] > 0]
                if not sel:
                    line += f"{'—':>16}"
                elif title.startswith("worst"):
                    line += f"{max(sel):>16.4f}"
                elif title.startswith("gated"):
                    raw = [r["ratio"] for r in rows
                           if r["tier"] == "webgpu" and r["bed"] == bed and r["label"] == label
                           and keep(r)]
                    line += f"{raw[0]:>16.4f}"
                else:
                    line += f"{sum(sel) / len(sel):>16.4f}"
            print(line)
        print()
    # The table is the evidence; see `anchor-solve.py` for why no JSON beside it.
    return 0


if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise SystemExit(__doc__)
    raise SystemExit(main(sys.argv[1:]))
