#!/usr/bin/env python3.12
"""W46 G0 (e): the per-cell predictions part 1 hashes (charter Decision Log 4: "predictions per target from
the rows, hashed"; G0 (e); the brief's item 6). PREDICTIONS, every one: the ladders and the level check
replace them with renders, and nothing here is fitted or gated.

1. **The transmission's structure share** (Design "The targets", target P). The neutral carries no
   structure, so a cell's interior structure is the transmitted share `1 − α` of the scattered
   backdrop's, `α = sizedAlpha = a + gain·sizeK·(1 − a)` (`arith.ts`, the runtime's own size law). At
   held scatter a cell's web SD at `tintAlpha` a is predicted as `web(shipped)·(1 − α(a))/(1 − α(shipped))`
   — each rest cell under the active rung, each inactive cell under the receded one — on every dark T1
   gate cell, both scales, from the published `d0219cd684bf` rows. Per target, the predicted aggregate
   `A` (the rule's arithmetic) at every grid value, and the `a` at which each target cell's predicted
   ratio crosses 1.
2. **The level** (X61). The W9 solve per cell at every grid value (`arith.ts` through `level.predict`):
   whether the neutral clamps at 0 and by how much the composite then exceeds its target, or where the
   authority is partial — on L1's declared population and on every level probe of ladder (i); and per
   cell the CLAMP BOUNDARY, the largest `a` on a 0.01 grid at which the clamp bites.
3. **S1** (Decision Log 5). S1's dark reading is `V = w(0.25) − w(0.5)` against Apple's `dA` per cell;
   at held ordinates the refit's level change is the clamp's excess where the clamp bites and 0 where
   the solve holds, so the predicted dark medians at each grid value add that change to `V` on S1's
   dark WebGPU cells (spans 128 and 160 named apart, as the charter asks).

    python3.12 -B predict.py        (writes predictions.json and predictions.txt; refuses to overwrite)
"""
from __future__ import annotations

import gzip
import json
import math
import statistics
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
EVIDENCE = HERE.parent
sys.path.insert(0, str(EVIDENCE))
sys.path.insert(0, str(EVIDENCE / "level"))
import bindings as W  # noqa: E402
import level as L  # noqa: E402

B, T1, RULE = L.B, L.T1, L.RULE
GRID = {"rest": [0.9, 0.8, 0.7, 0.6, 0.5], "inactive": [0.89, 0.8, 0.7, 0.6, 0.5]}
FINE_GRID = [round(0.5 + 0.01 * i, 2) for i in range(41)]
SHIPPED = {"rest": 0.9, "inactive": 0.89}
GAIN = 0.05                     # sizeOcclusionGain, the dark documents inherit the default


def endpoints_at(tmp: Path, a_rest: float, a_inactive: float) -> dict:
    out = {}
    for pose, slot, a in (("active", "active.dark", a_rest), ("receded", "receded.dark", a_inactive)):
        body = json.loads(W.document_path(slot).read_text())
        body["patch"]["optics"]["regular"]["tintAlpha"] = a
        path = tmp / f"{slot}-{a}.json"
        path.write_text(json.dumps(body))
        out[pose] = str(path)
    return out


def sized(a: float, k: float) -> float:
    return a + GAIN * k * (1 - a)


def main() -> int:
    out_json, out_txt = HERE / "predictions.json", HERE / "predictions.txt"
    if out_json.exists() or out_txt.exists():
        raise SystemExit("predict: committed evidence is not overwritten")
    cut = json.loads(gzip.open(EVIDENCE / "rehearsal/d0219-cuts.json.gz").read())
    cells = [c for c in cut["T1"]["cells"] if c["tier"] == "webgpu" and c["profile"] in W.DARK_025
             and c["partition"] == "gate"]
    span = {c["scene"]: B.SCENES.span(c["scene"]) for c in cells}
    sizek = {}
    with tempfile.TemporaryDirectory() as tmp:
        shipped = L.predict(endpoints_at(Path(tmp), 0.9, 0.89),
                            [dict(id=s, pose="rest", span=span[s], encoded=0.5, linear=0.5) for s in span])
        sizek = {s: shipped[s]["sizeK"] for s in span}

    # 1. the transmission's structure share
    per_cell, targets = [], {}
    for c in cells:
        pose = "inactive" if c["pose"] == "inactive" else "rest"
        k = sizek[c["scene"]]
        a0 = SHIPPED[pose]
        share0 = 1 - sized(a0, k)
        pred = {}
        for a in GRID[pose]:
            web = c["candidate"] * (1 - sized(a, k)) / share0
            pred[str(a)] = dict(web=web, ratio=web / c["native"] if c["native"] else None,
                                within=T1.classify(c["native"], c["reference"], web, c["bar"], c["code"])["fidelity"])
        # The 2x `impulse__capsule-button__inactive` native SD is exactly 0 (the memo's §4): no ratio.
        # The a (0.01 grid, descending from the shipped value) at which an UNDER-structured cell's
        # predicted ratio reaches 1; an over-structured cell is over at every a (the transmission
        # only raises it), recorded as "over".
        if not c["native"]:
            cross = None
        elif c["candidate"] >= c["native"]:
            cross = "over"
        else:
            cross = next((a for a in sorted(FINE_GRID, reverse=True)
                          if a <= a0 and c["candidate"] * (1 - sized(a, k)) / share0 >= c["native"]), None)
        per_cell.append(dict(profile=c["profile"], scene=c["scene"], stratum=c["stratum"], pose=c["pose"],
                             target=RULE.is_target(c), span=span[c["scene"]], sizeK=k, native=c["native"],
                             web=c["candidate"], ratio=c["candidate"] / c["native"] if c["native"] else None, transmittedShare=share0,
                             predicted=pred, ratioOneAt=cross))
    for profile in W.DARK_025:
        for t in RULE.TARGETS:
            members = [p for p in per_cell if p["profile"] == profile and p["target"] == t]
            pose = "inactive" if t == "F inactive" else None
            agg = {}
            grids = GRID["inactive"] if pose else GRID["rest"]
            for i in range(len(grids)):
                vals = []
                for p in members:
                    g = GRID["inactive" if p["pose"] == "inactive" else "rest"][i]
                    c = next(x for x in cells if x["profile"] == profile and x["scene"] == p["scene"])
                    vals.append(abs(math.log((p["predicted"][str(g)]["web"] + c["code"]) / (c["native"] + c["code"]))))
                agg[f"rung {i}"] = statistics.median(vals)
            targets[f"{profile} {t}"] = dict(cells=len(members), rungs=["rest " + "/".join(map(str, GRID["rest"])),
                                                                        "inactive " + "/".join(map(str, GRID["inactive"]))],
                                             A=agg, reference=agg["rung 0"],
                                             halvedAt=[k for k, v in agg.items() if v <= 0.5 * agg["rung 0"]])

    # 2. the level, on ladder (i)'s cells
    ladder = json.loads(W.LADDER_CELLS.read_text())["ladders"]["i"]
    level_cells = [(p, s) for p in W.DARK_025 for s in ladder["rest"] + ladder["inactive"]]
    silhouette = {"rest": L.abscissa_silhouette(W.document("active.dark")),
                  "inactive": L.abscissa_silhouette(W.document("receded.dark"))}
    arith_cells = L.arithmetic_cells(level_cells, silhouette)
    level, boundary = {}, {}
    with tempfile.TemporaryDirectory() as tmp:
        for a in FINE_GRID:
            got = L.predict(endpoints_at(Path(tmp), a, a), arith_cells)
            for key, p in got.items():
                if p["clamped"]:
                    boundary[key] = max(boundary.get(key, 0), a)
                if a in GRID["rest"] or a in GRID["inactive"]:
                    level.setdefault(key, {})[str(a)] = dict(clamped=p["clamped"], excess=p["excess"],
                                                               achieved=p["achieved"], authority=p["authority"],
                                                               mechanism=L.mechanism(p), sizedAlpha=p["sizedAlpha"])
        shipped = L.predict(endpoints_at(Path(tmp), 0.9, 0.89), arith_cells)
    for key in level:
        pose = "inactive" if "__inactive" in key else "rest"
        level[key]["shipped"] = dict(clamped=shipped[key]["clamped"], excess=shipped[key]["excess"],
                                     achieved=shipped[key]["achieved"], authority=shipped[key]["authority"])
        level[key]["clampBoundary"] = boundary.get(key)
        level[key]["inputs"] = next(dict(encoded=c["encoded"], linear=c["linear"], span=c["span"])
                                    for c in arith_cells if c["id"] == key)
        level[key]["deltaFromShipped"] = {a: v["achieved"] - shipped[key]["achieved"] for a, v in level[key].items()
                                          if a.replace(".", "").isdigit()}
        level[key]["pose"] = pose

    # 3. S1
    s1 = {}
    s1_cells = [c for c in cut["S1"]["webgpu"]["cells"] if c["profile"] in W.DARK_025]
    s1_keys = [(c["profile"], c["cell"].split("/", 1)[1]) for c in s1_cells]
    s1_arith = L.arithmetic_cells(s1_keys, silhouette)
    with tempfile.TemporaryDirectory() as tmp:
        base = L.predict(endpoints_at(Path(tmp), 0.9, 0.89), s1_arith)
        for i in range(len(GRID["rest"])):
            ar, ai = GRID["rest"][i], GRID["inactive"][i]
            got = L.predict(endpoints_at(Path(tmp), ar, ai), s1_arith)
            for profile in W.DARK_025:
                ratios, thick = [], []
                for c in s1_cells:
                    if c["profile"] != profile:
                        continue
                    key = c["cell"]
                    dv = got[key]["achieved"] - base[key]["achieved"]
                    r = (c["V"] + dv) / c["dA"]
                    ratios.append(r)
                    if B.SCENES.span(key.split("/", 1)[1]) in (128, 160):
                        thick.append(dict(cell=key, predictedLevelChange=dv, ratio=r))
                s1.setdefault(profile, {})[f"{ar}/{ai}"] = dict(
                    median=L.C.upper_middle(ratios), cells=len(ratios),
                    thickCellsMoved=[t for t in thick if abs(t["predictedLevelChange"]) > 1e-6])
    result = dict(
        schema="w46-predictions-1",
        what="W46 G0 (e): per-cell PREDICTIONS from the published d0219cd684bf rows and the runtime's own "
             "arithmetic; the ladders and the level check replace them",
        reference=dict(cut="rehearsal/d0219-cuts.json.gz", sha256=W.file_sha(EVIDENCE / "rehearsal/d0219-cuts.json.gz")),
        grids=GRID, transmission=dict(perCell=per_cell, targets=targets,
                                      law="web(a) = web(shipped) · (1 − α(a)) / (1 − α(shipped)), α = a + 0.05·sizeK·(1 − a), scatter held"),
        level=dict(perCell=level, note="arith.ts on the backdrop's group means: a clamp excess is the composite "
                                         "above its target where the neutral clamps at 0 (no darkward alpha solve)"),
        s1=dict(perProfile=s1, sentence="after a dark 0.25 refit with dark 0.5 frozen, S1's dark reading is the "
                                        "refit's change plus the slider's, and says nothing about Apple's slider "
                                        "until dark 0.5 is refit under the same families (Decision Log 1)"))
    lines = ["W46 G0 (e): per-cell predictions (PREDICTIONS; the ladders and the level check replace them)", ""]
    lines.append("1. The transmission's structure share, scatter held (web(a) = web · (1 − α(a))/(1 − α(shipped))):")
    for k, v in targets.items():
        lines.append(f"  {k:<58} n={v['cells']:<3} A " + " ".join(f"{x:.3f}" for x in v["A"].values())
                     + f"   (rungs {', '.join(v['rungs'])}); halved at {v['halvedAt'] or 'no rung'}")
    lines.append("  per target cell: the a at which the predicted ratio reaches 1 (None: not on [0.5, 0.9])")
    for p in per_cell:
        if p["target"]:
            lines.append(f"    {p['profile'].split('-')[3]} {p['scene']:<46} ×{p['ratio']:.2f} -> ×1 at {p['ratioOneAt']}")
    lines.append("")
    lines.append("2. The level (W9 solve; clamp boundary = the largest a, 0.01 grid, at which the neutral clamps):")
    for key, v in sorted(level.items()):
        excess = {a: x["excess"] for a, x in v.items() if a.replace(".", "").isdigit() and x["clamped"]}
        auth = min(x["authority"] for a, x in v.items() if a.replace(".", "").isdigit())
        if excess or v["clampBoundary"] or auth < 0.999:
            lines.append(f"  {key:<84} clamp below {v['clampBoundary']}; excess "
                         + ", ".join(f"{a} {e:+.4f}" for a, e in excess.items())
                         + (f"; authority {auth:.3f}" if auth < 0.999 else ""))
    lines.append("")
    lines.append("3. S1's dark medians, predicted (rest/inactive rung):")
    for profile, v in s1.items():
        lines.append(f"  {profile}: " + "; ".join(f"{k} median {x['median']:.3f} ({len(x['thickCellsMoved'])} thick cells moved)"
                                                  for k, x in v.items()))
    lines.append(f"  {result['s1']['sentence']}")
    with out_json.open("x") as f:
        json.dump(result, f, indent=1)
        f.write("\n")
    with out_txt.open("x") as f:
        f.write("\n".join(lines) + "\n")
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    sys.exit(main())
