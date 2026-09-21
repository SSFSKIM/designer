#!/usr/bin/env python3
"""W32 G1 — the transmission profile per band, both sides, and what one scale would buy.

    python3 band-profile.py <matrix.json> <exterior-cut.json>

The reader G0 wrote reports `T` and `Δa`; this one reports the two sides the
difference is taken between, because a fit needs to know whether it is looking at
a shape error or a scale error and `Δa` alone cannot say.

**The quantity.** Per bed, per span, per admitted band: the median over the
population's cells of `1 − a`, the OCCLUSION that band applies to its backdrop,
on Apple's render and on vitrea's. Population: WebGPU tier, active, non-holdout,
cells whose identified band set equals their span's admitted set — C1's own
population, so the numbers here and the numbers a clause is read on are of the
same cells.

**`k*`, and what it is not.** `k*` is the single multiplier on vitrea's occlusion
profile that minimises the width-weighted mean `|occ_native − k · occ_web|` at
that bed and span — which is `T` if the shape were right and only the scale
wrong. It is a DIAGNOSTIC and not a fitted constant: the anchors are solved in
closed form from the window-restricted departure (`anchor-solve.py`), the lengths
are searched on rendered rounds, and nothing in this file is written into a
document. Its use is to separate the two questions before a round is spent —
where `k*` is far from 1 and the residual at `k*` is small, the error is a scale
and the anchors can reach it; where the residual at `k*` stays large, the error
is in the SHAPE and only the lengths can.

A per-span `k*` is comparable to an anchor because the material's amplitude is
anchored per span (`thickOcclusionAt96` / `128` / `160`, and the thin regime's
three keyed on the backdrop class), and `outerShadowAlpha` is very nearly linear
in the anchor at these magnitudes. "Very nearly" is the caveat the round is for.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from statistics import median

WIDTH = {"3-6": 3, "6-12": 6, "12-24": 12, "24-48": 24}
BEDS = ["1x light", "2x light", "1x dark", "2x dark"]


def affine(shadow, side):
    return {b["ringLabel"]: b for b in shadow.get(f"affine{side}", []) if b["direction"] == "all"}


def main(argv) -> int:
    if len(argv) != 2:
        raise SystemExit(__doc__)
    matrix = json.loads(Path(argv[0]).read_text())
    cut = json.loads(Path(argv[1]).read_text())
    index = {(r["profile"], r["scene"], r["tier"]): r for r in cut["rows"]}

    data: dict[tuple[str, int, str], list[tuple[float, float]]] = {}
    for cell in matrix["cells"]:
        if cell["tier"] != "texture":
            continue
        row = index.get((cell["key"]["profileKey"], cell["key"]["sceneId"], "webgpu"))
        if row is None or row["T"] is None:
            continue
        if tuple(row["bandsUsed"]) != tuple(row["admitted"]):
            continue
        if row["state"] == "inactive" or row["set"] == "holdout":
            continue
        native, web = affine(cell["shadow"], "Native"), affine(cell["shadow"], "Web")
        for band in row["admitted"]:
            n, w = native.get(band), web.get(band)
            if n is None or w is None:
                continue
            if n.get("slopeALinear") is None or w.get("slopeALinear") is None:
                continue
            data.setdefault((row["bed"], row["span"], band), []).append(
                (1 - n["slopeALinear"], 1 - w["slopeALinear"]))

    print("W32 G1 — the occlusion profile per band, both sides")
    print("=" * 104)
    print(f"  matrix   {argv[0]}")
    print(f"  cut      {argv[1]}")
    print(f"  documents {', '.join(cut['documents'])}")
    print()
    print(f"  {'bed':<12}{'span':>5} {'band':<7}{'n':>4}{'occ native':>12}{'occ web':>10}"
          f"{'web/nat':>9}")
    for (bed, span, band), values in sorted(
            data.items(), key=lambda kv: (kv[0][0], kv[0][1], WIDTH[kv[0][2]])):
        n = median(v[0] for v in values)
        w = median(v[1] for v in values)
        print(f"  {bed:<12}{span:>5} {band:<7}{len(values):>4}{n:>12.5f}{w:>10.5f}"
              f"{(w / n if n else float('nan')):>9.3f}")
    print()
    print("  k* — the ONE scale on vitrea's profile that minimises the width-weighted |Δ|,")
    print("  and the `T` it would leave. A diagnostic: nothing here is written to a document.")
    print(f"  {'bed':<12}{'span':>5}{'T now':>10}{'k*':>8}{'T at k*':>10}   bands")
    for bed in BEDS:
        for span in sorted({s for (b, s, _) in data if b == bed}):
            bands = sorted({b for (bd, sp, b) in data if bd == bed and sp == span},
                           key=lambda b: WIDTH[b])
            native = [median(v[0] for v in data[(bed, span, b)]) for b in bands]
            web = [median(v[1] for v in data[(bed, span, b)]) for b in bands]
            weights = [WIDTH[b] for b in bands]
            total = sum(weights)
            now = sum(wt * abs(a - c) for wt, a, c in zip(weights, native, web)) / total
            best = min(((k / 1000,
                         sum(wt * abs(a - (k / 1000) * c)
                             for wt, a, c in zip(weights, native, web)) / total)
                        for k in range(0, 2001)), key=lambda kv: kv[1])
            print(f"  {bed:<12}{span:>5}{now:>10.5f}{best[0]:>8.3f}{best[1]:>10.5f}   "
                  f"{'/'.join(bands)}")
    print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
