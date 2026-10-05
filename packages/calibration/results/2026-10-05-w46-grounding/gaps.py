#!/usr/bin/env python3.12
"""W46 grounding: the candidate waves' cells, read off `t1-union.json`, `rows-union.json` and the
published rows (current generations, and c05 `6d18c059eb42` where a named gap was stated on c05).
Writes `gaps.json` and prints the memo's per-candidate tables.

    python3.12 -B gaps.py > gaps.txt
"""
from __future__ import annotations

import json
import math
import statistics
import sys
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
CAL = HERE.parents[1]
sys.path.insert(0, str(CAL / "results" / "2026-10-03-w44-g1-refit" / "cuts"))
import bed as B  # noqa: E402
import matrix_store  # noqa: E402

T1 = json.loads((HERE / "t1-union.json").read_text())["cells"]
ROWS = json.loads((HERE / "rows-union.json").read_text())["perGeneration"]
REGRESSIONS = ["checkerboard__rrect-md__pressed", "checkerboard__capsule-button__pressed",
               "checkerboard-32__rrect-sm__rest", "checkerboard-32__rrect-lg__rest",
               "checkerboard__rrect-lg__rest", "checkerboard-64__rrect-sm__rest",
               "hc-text-7__rrect-md__inactive", "checkerboard__glass-over-glass__rest",
               "checkerboard-8__rrect-lg__rest", "hc-text__rrect-lg__inactive",
               "photo__toolbar-group__inactive"]
out = {}


def sel(gen, scale=None, tier=None, stratum=None, pose=None, holdout=None):
    return [c for c in T1 if c["generation"] == gen and (scale is None or c["scale"] == scale)
            and (tier is None or c["tier"] == tier) and (stratum is None or c["stratum"] == stratum)
            and (pose is None or c["pose"] == pose)
            and (holdout is None or (c["partition"] == "holdout") == holdout)
            and "-standard-" in c["profile"]]


def summary(cells):
    miss = [c for c in cells if c["readFidelity"] == "miss"]
    if not cells:
        return dict(cells=0)
    return dict(cells=len(cells), miss=len(miss),
                medianAbsLog=statistics.median(abs(math.log(c["readRatio"])) for c in cells if c["readRatio"]),
                A=statistics.median(c["readLogError"] for c in cells),
                sumMissLogError=sum(c["readLogError"] for c in miss),
                medianRatio=statistics.median(c["readRatio"] for c in cells if c["readRatio"]))


def line(c):
    return (f"  {c['scene']:44} {c['spanClass']:5} {c['pose']:8} {c['partition']:8} n {c['readNative']:.4f} "
            f"web {c['readWeb']:.4f} x{c['readRatio']:.2f} {c['readFidelity']}")


# (a) 2x light 0.25 WebGPU F by span, with 0.5's and 1x's beside it.
print("(a)/(d) F stratum, WebGPU, by generation and scale (T1, web/native)")
fa = {}
for gen in ("light 0.25", "light 0.5", "dark 0.25", "dark 0.5"):
    for scale in (2, 1):
        cells = sorted(sel(gen, scale, "webgpu", "F"), key=lambda c: (c["pose"], c["scene"]))
        fa[f"{gen} {scale}x"] = [dict(scene=c["scene"], span=c["spanClass"], pose=c["pose"], ratio=c["readRatio"],
                                      fidelity=c["readFidelity"], native=c["readNative"], web=c["readWeb"]) for c in cells]
        print(f"{gen} {scale}x webgpu F: {summary(cells)}")
        for c in cells:
            print(line(c))
out["F_webgpu"] = fa

# The thick/mid over-structure cells (a): F and C with ratio > 1.1 at 2x light 0.25 rest mid/thick.
a_cells = [c for c in sel("light 0.25", 2, "webgpu") if c["stratum"] in ("F", "C") and c["pose"] == "rest"
           and c["spanClass"] in ("mid", "thick") and c["readFidelity"] == "miss"]
print("\n(a) 2x light 0.25 WebGPU rest mid/thick F+C misses:", summary(a_cells))
for c in sorted(a_cells, key=lambda c: -c["readLogError"]):
    print(line(c))
out["a_midThickMisses"] = [dict(scene=c["scene"], span=c["spanClass"], ratio=c["readRatio"]) for c in a_cells]

# (b) dark 0.25: T1 by stratum both scales, both tiers; L1 / S1.
print("\n(b) dark 0.25 T1, non-holdout, by scale x tier x stratum")
for scale in (1, 2):
    for tier in ("webgpu", "css"):
        for st in "FTCP":
            print(f"  {scale}x {tier} {st}: {summary(sel('dark 0.25', scale, tier, st, holdout=False))}")
lv = []
for r in matrix_store.load_generation("d0219cd684bf"):
    if r["key"]["web"]["renderer"] != "webgpu":
        continue
    n, w = B.value(r, "material", "interiorMeanNative"), B.value(r, "material", "interiorMeanWeb")
    if None not in (n, w) and B.SCENES.role[r["key"]["sceneId"]] != "holdout":
        lv.append((w - n, r["key"]["sceneId"], r["key"]["profileKey"]))
print(f"  dark 0.25 webgpu level (web-native mean, linear), non-holdout, every set: n {len(lv)}, median "
      f"{statistics.median(x for x, *_ in lv):+.4f}, |>0.02| {sum(abs(x) > 0.02 for x, *_ in lv)}, "
      f"|>0.055| {sum(abs(x) > 0.055 for x, *_ in lv)}; worst {sorted(lv, key=lambda t: -abs(t[0]))[:5]}")
out["b_darkLevel"] = dict(cells=len(lv), over002=sum(abs(x) > 0.02 for x, *_ in lv),
                          over0055=sum(abs(x) > 0.055 for x, *_ in lv),
                          worst=sorted(lv, key=lambda t: -abs(t[0]))[:10])

# (c) 1x light 0.25 WebGPU T1.
c1x = sel("light 0.25", 1, "webgpu")
print(f"\n(c) 1x light 0.25 WebGPU T1, all 116 (holdout included): {summary(c1x)}")
for st in "FTCP":
    for pose in ("rest", "inactive"):
        print(f"  {st} {pose}: {summary([c for c in c1x if c['stratum'] == st and c['pose'] == pose])}")
over = sorted([c for c in c1x if c["readFidelity"] == "miss"], key=lambda c: -c["readLogError"])[:12]
for c in over:
    print(line(c))

# (e) CSS fine-pitch: F on css, every generation.
print("\n(e) CSS tier F (and T on T1-fine), non-holdout")
for gen in ("light 0.5", "dark 0.5", "light 0.25", "dark 0.25"):
    for scale in (1, 2):
        for pose in ("rest", "inactive"):
            s = summary(sel(gen, scale, "css", "F", pose))
            if s["cells"]:
                print(f"  {gen} {scale}x css F {pose}: {s}")

# (f) the eleven W45 regressions at 2x light 0.25 WebGPU, current reading against native.
print("\n(f) T1_AUTHORISED_REGRESSIONS, 2x light 0.25 WebGPU, current (ebc3d9105a4a) against native")
by = {c["scene"]: c for c in sel("light 0.25", 2, "webgpu")}
f_rows = []
for sid in REGRESSIONS:
    c = by[sid]
    band = c["bands"]["low"] if c["stratum"] == "T" else None
    ratio = band["candidate"] / band["native"] if band else c["readRatio"]
    ref_ratio = band["reference"] / band["native"] if band else c["referenceRatio"]
    f_rows.append(dict(scene=sid, stratum=c["stratum"], partition=c["partition"],
                       metric="T1-low" if band else c["readMetric"], ratio=ratio,
                       fidelity=(band["fidelity"] if band else c["readFidelity"])))
    print(f"  {sid:44} {c['partition']:8} {'T1-low' if band else 'T1':6} x{ratio:.2f} "
          f"{band['fidelity'] if band else c['readFidelity']}")
out["f_regressions"] = f_rows

# (g) light photo thin rest level, and the light receded tint, on the current generation and c05.
print("\n(g) light 0.25 level and tint (WebGPU), current ebc3d9105a4a and c05 6d18c059eb42")
g_out = {}
for label, active in (("current", "ebc3d9105a4a"), ("c05", "6d18c059eb42")):
    rows = [r for r in matrix_store.load_generation(active) if r["key"]["web"]["renderer"] == "webgpu"]
    photo = []
    tint = []
    for r in rows:
        sid = r["key"]["sceneId"]
        scene = B.SCENES.by_id[sid]
        if B.SCENES.role[sid] == "holdout":
            continue
        n, w = B.value(r, "material", "interiorMeanNative"), B.value(r, "material", "interiorMeanWeb")
        span = B.SCENES.span(sid)
        if scene["background"] == "photo" and scene["state"] == "rest" and span is not None and span <= 44 \
                and "-tint-" not in sid:
            photo.append(dict(scene=sid, scale=B.scale_of(r["key"]["profileKey"]), set=B.SCENES.role[sid],
                              error=w - n))
        if "-tint-" in sid and B.SCENES.inactive(sid):
            ln, lw = B.value(r, "material", "tintDeltaLNative"), B.value(r, "material", "tintDeltaLWeb")
            if None not in (ln, lw):
                tint.append(dict(scene=sid, scale=B.scale_of(r["key"]["profileKey"]), set=B.SCENES.role[sid],
                                 dL=lw - ln))
    g_out[label] = dict(photoThinRest=photo, recededTint=tint)
    print(f"  {label}: photo thin rest (web - native mean, linear):")
    for p in sorted(photo, key=lambda p: (p["scale"], p["scene"])):
        print(f"    {p['scale']}x {p['scene']:40} {p['set']:11} {p['error']:+.4f}")
    if tint:
        print(f"  {label}: receded tint dL web - native over {len(tint)} inactive tinted cells: mean "
              f"{statistics.mean(t['dL'] for t in tint):+.4f}, by set "
              f"{ {s: round(statistics.mean(t['dL'] for t in tint if t['set'] == s), 4) for s in {t['set'] for t in tint}} }")
out["g"] = g_out
(HERE / "gaps.json").write_text(json.dumps(out, indent=1) + "\n")
