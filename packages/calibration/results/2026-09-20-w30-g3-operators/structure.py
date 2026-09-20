#!/usr/bin/env python3
"""W30 G3 — the interior structure ratio per pitch, the quantity B4 is read on.

    VITREA_G3_SCRATCH=/tmp/w30g3 python3 structure.py --labels a,b       # fit rounds
    python3 structure.py                                                 # the committed matrix

The quantity is `material.interiorStdDevWeb / …Native` — the body's spread in
LINEAR light over the shared mask — exactly as `tier-coherence.test.ts` reads it
and as W30 G0's `structure-cut.py` reads it. Above 1 vitrea passes more of the
backdrop's structure through the body than Apple does; below 1 it passes less.

The pitch is the backdrop's own, read from the scene id: the ladder is
`checkerboard-4/8/32/64`, `checkerboard-lc16` and `hc-text-7/28` beside the
gated `checkerboard` (16), `hc-text` (14), `photo` and the solids. The
low-contrast 16 px rung is kept SEPARATE from the plain 16 px one, because the
pair at one pitch and two contrasts is the discriminator between a kernel that
is linear in the backdrop (candidate (i)) and a mix keyed on a statistic of the
source (candidate (ii)) — claims §5.156 §3.

Two things it prints that a per-pitch mean would hide. The gated 16 px cell
`checkerboard__rrect-md__rest` is named on its own, because it is the cell B4's
"toward 1.0 and past it on none" clause is stated on and the cell
`tier-coherence.test.ts` pins. And the same pitch is printed per SPAN, because
the scale-selectivity the operator exists for is gated on `sizeThickness` and
the 2x trio takes over where it saturates.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PACKAGE = HERE.parent.parent
ROOT = PACKAGE.parent.parent
SCENES = ROOT / "apps/reference-apple/scenes.json"
SCRATCH = Path(os.environ.get("VITREA_G3_SCRATCH", "/tmp/g3scratch"))
CAPTURE = re.compile(r"materialProfile=(\S+) sha256:([0-9a-f]{12})")
TIER = {"texture": "webgpu", "dom": "css"}

sys.path.insert(0, str(HERE.parent / "2026-09-19-w29-g3-refit"))
from fit import cells as fit_cells  # noqa: E402

# The backdrop's spatial pitch in CSS px, and whether the rung is the
# low-contrast one. `None` is a backdrop with no single pitch.
PITCH: dict[str, tuple[float | None, str]] = {
    "checkerboard-4": (4, "ckbd"),
    "hc-text-7": (7, "text"),
    "checkerboard-8": (8, "ckbd"),
    "hc-text": (14, "text"),
    "checkerboard": (16, "ckbd"),
    "checkerboard-lc16": (16, "ckbd-lc"),
    "hc-text-28": (28, "text"),
    "checkerboard-32": (32, "ckbd"),
    "checkerboard-64": (64, "ckbd"),
    "photo": (None, "photo"),
    "impulse": (None, "solid"),
    "dark-solid": (None, "solid"),
    "mid-dark-solid": (None, "solid"),
    "mid-chroma-solid": (None, "solid"),
    "light-solid": (None, "solid"),
}

GATED_CELL = "checkerboard__rrect-md__rest"


def spans() -> dict[str, float]:
    spec = json.loads(SCENES.read_text())
    return {name: float(min(c["size"])) for name, c in spec["components"].items()
            if isinstance(c.get("size"), list) and len(c["size"]) == 2}


def at(block: dict, name: str) -> float | None:
    entry = (block or {}).get(name)
    return entry["value"] if isinstance(entry, dict) else None


def bed_of(profile: str) -> str:
    return profile.replace("apple-macos-27.0-", "").replace("-glass0.5", "")


def rows_from(cells, source: str, component_span: dict[str, float]) -> list[dict]:
    out = []
    for cell in cells:
        profile = cell["key"]["profileKey"]
        if not profile.startswith("apple-macos-27.0-"):
            continue
        scene = cell["key"]["sceneId"]
        parts = scene.split("__")
        material = cell.get("material") or {}
        native, web = at(material, "interiorStdDevNative"), at(material, "interiorStdDevWeb")
        if native is None or web is None or native == 0:
            continue
        pitch, family = PITCH.get(parts[0], (None, "?"))
        out.append({
            "source": source,
            "profile": profile,
            "bed": bed_of(profile),
            "tier": TIER.get(cell["tier"], cell["tier"]),
            "scene": scene,
            "set": cell.get("fixtureSet"),
            "state": cell.get("state") or "rest",
            "backdrop": parts[0],
            "pitch": pitch,
            "family": family,
            "span": component_span.get(parts[1]) if len(parts) > 1 else None,
            "native": native,
            "web": web,
            "ratio": web / native,
        })
    return out


def median(values: list[float]) -> float:
    return sorted(values)[len(values) // 2]


def main(argv: list[str]) -> int:
    component_span = spans()
    rows: list[dict] = []
    labels = []
    if "--labels" in argv:
        labels = argv[argv.index("--labels") + 1].split(",")
        for label in labels:
            for matrix in sorted((SCRATCH / "fit-log" / label).glob("*.json")):
                rows += rows_from(fit_cells(matrix), f"{label}/{matrix.name}", component_span)
    else:
        hashes = {f"packages/calibration/profiles/{p.name}":
                  hashlib.sha256(p.read_bytes()).hexdigest()[:12]
                  for p in sorted((PACKAGE / "profiles").glob("*.json"))}
        kept = []
        for cell in json.loads((PACKAGE / "results/matrix.json").read_text())["cells"]:
            clause = CAPTURE.search(cell["key"]["web"]["capturePath"])
            if clause is not None and hashes.get(clause.group(1)) == clause.group(2):
                kept.append(cell)
        rows = rows_from(kept, "matrix.json", component_span)

    print("W30 G3 — the interior structure ratio, "
          + (f"labels {', '.join(labels)}" if labels else "the committed matrix"))
    print("=" * 108)
    print(f"  {len(rows)} macOS 27 rows carry `interiorStdDev` on both sides")
    print()

    for tier in ("webgpu", "css"):
        here = [r for r in rows if r["tier"] == tier and r["state"] != "inactive"
                and r["set"] != "holdout"]
        if not here:
            continue
        print(f"{tier} tier — median W/N per pitch per bed, active, non-holdout")
        print("-" * 108)
        keys = sorted({(r["pitch"] if r["pitch"] is not None else 1e9, r["family"],
                        r["backdrop"]) for r in here})
        header = f"  {'bed':<30}" + "".join(f"{k[2][:13]:>14}" for k in keys)
        print(header)
        for bed in sorted({r["bed"] for r in here}):
            line = f"  {bed:<30}"
            for _, _, backdrop in keys:
                sel = [r["ratio"] for r in here if r["bed"] == bed and r["backdrop"] == backdrop]
                line += f"{'—':>14}" if not sel else f"{median(sel):>10.3f} ({len(sel):>1})"
            print(line)
        print()

    print("The gated cell B4's clause is stated on, per bed per tier")
    print("-" * 108)
    print(f"  {'bed':<46}{'tier':<9}{'native':>10}{'web':>10}{'W/N':>9}")
    for bed in sorted({r["bed"] for r in rows}):
        for tier in ("webgpu", "css"):
            sel = [r for r in rows if r["bed"] == bed and r["tier"] == tier
                   and r["scene"] == GATED_CELL]
            if not sel:
                continue
            row = sel[-1]
            print(f"  {bed:<46}{tier:<9}{row['native']:>10.4f}{row['web']:>10.4f}"
                  f"{row['ratio']:>9.4f}")
    print()

    print("The ladder per pitch per span — the scale-selectivity axis, WebGPU, standard beds")
    print("-" * 108)
    standard = [r for r in rows if r["tier"] == "webgpu" and r["state"] != "inactive"
                and r["set"] != "holdout" and "standard" in r["bed"]]
    spans_seen = sorted({r["span"] for r in standard if r["span"] is not None})
    print(f"  {'bed':<26}{'backdrop':<18}" + "".join(f"{int(s):>10}" for s in spans_seen))
    for bed in sorted({r["bed"] for r in standard}):
        for _, _, backdrop in sorted({(r["pitch"] if r["pitch"] is not None else 1e9,
                                       r["family"], r["backdrop"]) for r in standard}):
            line = f"  {bed:<26}{backdrop:<18}"
            any_cell = False
            for span in spans_seen:
                sel = [r["ratio"] for r in standard
                       if r["bed"] == bed and r["backdrop"] == backdrop and r["span"] == span]
                if sel:
                    any_cell = True
                line += f"{'—':>10}" if not sel else f"{median(sel):>10.3f}"
            if any_cell:
                print(line)
    print()

    # The tables above are the evidence. `--json` writes the per-row readings
    # beside them for a reader that wants them; it is not committed, because a
    # second copy of the matrix's own numbers is weight rather than evidence.
    if "--json" in argv:
        out = HERE / ("structure." + ("-".join(labels).replace("/", "_") if labels else "matrix")
                      + ".json")
        out.write_text(json.dumps({"labels": labels, "rows": rows}, indent=1) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
