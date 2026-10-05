#!/usr/bin/env python3.12
"""W46 grounding: the ranked gap table. Each candidate wave's cells are selected off `t1-union.json`
(T1, the texture reading every candidate (a)-(f) is about) and its weight is cells x magnitude,
stated as S = the sum over the candidate's MISSING cells of |log((web + code) / (native + code))|
(W45's per-cell aggregate term; a cell within T1's bound contributes nothing), over the
non-holdout members. (g) is a level / tint
reading with no T1 term; its weight is stated in its own unit and it is ranked on that separately.

    python3.12 -B rank.py > rank.txt
"""
from __future__ import annotations

import json
import math
import statistics
from pathlib import Path

HERE = Path(__file__).resolve().parent
T1 = json.loads((HERE / "t1-union.json").read_text())["cells"]
GAPS = json.loads((HERE / "gaps.json").read_text())
STD = [c for c in T1 if "-standard-" in c["profile"]]
REGRESSIONS = {r["scene"] for r in GAPS["f_regressions"]}


def weigh(cells):
    """S is ranked over the NON-HOLDOUT members only (a holdout reading is never a fitting or
    chartering input, even spent); `SwithHoldout` is printed beside it."""
    every = cells
    cells = [c for c in every if c["partition"] != "holdout"]
    miss = [c for c in cells if c["readFidelity"] == "miss"]
    held = [c for c in every if c["partition"] == "holdout"]
    ratios = [c["readRatio"] for c in miss if c["readRatio"]]
    return dict(cells=len(cells), miss=len(miss),
                holdout=len(held), holdoutMiss=sum(c["readFidelity"] == "miss" for c in held),
                SwithHoldout=sum(c["readLogError"] for c in every if c["readFidelity"] == "miss"),
                referee=sum(c["partition"] == "referee" for c in cells),
                S=sum(c["readLogError"] for c in miss),
                medianRatioOfMisses=statistics.median(ratios) if ratios else None,
                worst=worst(miss))


def worst(miss):
    if not miss:
        return None
    c = max(miss, key=lambda c: c["readLogError"])
    where = f"{c['generation']} {c['scale']}x {c['tier']} {c['scene']}"
    return where + (f" x{c['readRatio']:.2f}" if c["readRatio"] else " (native 0)")


def is_(gen=None, scale=None, tier=None):
    return lambda c: ((gen is None or c["generation"] in gen) and (scale is None or c["scale"] == scale)
                      and (tier is None or c["tier"] == tier))


CANDIDATES = {
    "(a) per-span tap WIDTH: 2x light 0.25 WebGPU, F u C at mid/thick spans with web > native":
        [c for c in STD if is_(("light 0.25",), 2, "webgpu")(c) and c["stratum"] in ("F", "C")
         and c["spanClass"] in ("mid", "thick") and c["readRatio"] and c["readRatio"] > 1],
    "(b) dark 0.25 WebGPU, every stratum, both scales":
        [c for c in STD if is_(("dark 0.25",), None, "webgpu")(c)],
    "(c) 1x light 0.25 WebGPU, every stratum":
        [c for c in STD if is_(("light 0.25",), 1, "webgpu")(c)],
    "(d) the 0.5 generation, light and dark, WebGPU, every stratum, both scales":
        [c for c in STD if is_(("light 0.5", "dark 0.5"), None, "webgpu")(c)],
    "(e) CSS tier F (fine pitches), every generation, both poses":
        [c for c in STD if c["tier"] == "css" and c["stratum"] == "F"],
    "(f) the eleven W45 authorised regressions, 2x light 0.25 WebGPU":
        [c for c in STD if is_(("light 0.25",), 2, "webgpu")(c) and c["scene"] in REGRESSIONS],
}
# Context rows: overlapping re-cuts of the candidates above, not ranked against them.
CONTEXT = {
    "[ctx] (d) light half: light 0.5 WebGPU":
        [c for c in STD if is_(("light 0.5",), None, "webgpu")(c)],
    "[ctx] (d) dark half: dark 0.5 WebGPU":
        [c for c in STD if is_(("dark 0.5",), None, "webgpu")(c)],
    "[ctx] the dark scheme at both positions: (b) + (d) dark half":
        [c for c in STD if is_(("dark 0.25", "dark 0.5"), None, "webgpu")(c)],
    "[ctx] (a)'s shape on every generation and scale (F u C mid/thick, web > native, WebGPU)":
        [c for c in STD if c["tier"] == "webgpu" and c["stratum"] in ("F", "C")
         and c["spanClass"] in ("mid", "thick") and c["readRatio"] and c["readRatio"] > 1],
    "[ctx] (e) widened: the CSS tier, every stratum, every generation":
        [c for c in STD if c["tier"] == "css"],
}


def main():
    rows = []
    for name, cells in CANDIDATES.items():
        w = weigh(cells)
        rows.append(dict(candidate=name, **w))
    g = GAPS["g"]["current"]
    photo = g["photoThinRest"]
    tint = g["recededTint"]
    rows.append(dict(candidate="(g) light 0.25 photo thin rest level (WebGPU), and receded tint L",
                     cells=len(photo) + len(tint), miss=0, holdout=0, referee=0, S=None,
                     note=(f"photo thin rest: {len(photo)} cells, web - native mean "
                           f"{min(p['error'] for p in photo):+.3f} to {max(p['error'] for p in photo):+.3f} linear "
                           f"(L1 bound 0.055: all within); receded tint: {len(tint)} inactive tinted cells, mean "
                           f"dL {statistics.mean(t['dL'] for t in tint):+.4f} OKLab L (no adopted bound); "
                           "both identical to c05 (W45 moved neither)")))
    ranked = sorted([r for r in rows if r["S"] is not None], key=lambda r: -r["S"]) + [r for r in rows if r["S"] is None]
    ranked += [dict(candidate=name, context=True, **weigh(cells)) for name, cells in CONTEXT.items()]
    (HERE / "rank.json").write_text(json.dumps(ranked, indent=1) + "\n")
    for r in ranked:
        if r["S"] is None:
            print(f"-- {r['candidate']}\n   {r['note']}")
            continue
        print(f"S {r['S']:6.2f}  miss {r['miss']:3}/{r['cells']:3} non-holdout (referee {r['referee']}); "
              f"holdout {r['holdoutMiss']}/{r['holdout']} miss, S with holdout {r['SwithHoldout']:.2f}  "
              f"median ratio of misses x{r['medianRatioOfMisses']:.2f}  worst {r['worst']}\n   {r['candidate']}")


if __name__ == "__main__":
    main()
