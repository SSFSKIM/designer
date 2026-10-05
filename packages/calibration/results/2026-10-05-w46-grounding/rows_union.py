#!/usr/bin/env python3.12
"""W46 grounding: every other adopted row over the whole current macOS 27 union, by generation x
scale x tier, gated or not.

Each row is read with the owner test's or the 0.25 cuts' own derivation, never a new threshold:
  tables  the owner test's tables (`cuts.owner_tables`, read out of adopted-thresholds.test.ts and
          followed through the 27 aliases; a 0.25 profile carries its 0.5 twin's). GATED bed as the
          owner test's `inGatedBed` + conditioning predicate: no probe, no recorded, rest pose, every
          set INCLUDING holdout (holdout misses are counted in their own column); shape rows only on
          well-conditioned cells. The same table over the rows the gate drops (probe, recorded,
          inactive) is reported as NOT GATED. Gated misses are cross-checked against MISSED_27_ROWS.
  M1      R = chromaStructureRatioWeb / Native on the untinted photo calibration/validation cells,
          both poses (`cuts.chroma_member`); median per scheme x pose in [0.8, 1.2], cell in
          [0.6, 1.4]. Gated: WebGPU standard. Computed on both tiers and every generation.
  M2      a regression stop against a per-gate reference, so it is read off the cut each owner
          block pins (0.5: W36's chroma-cut; 0.25: W45's landing cut), not recomputed.
  C1      `cuts.cut_c1` (W32's T per bed x span, upper middle <= 0.0042) on every generation, both
          tiers. Gated: WebGPU (0.5 and 0.25).
  X1      `cuts.cut_x1` on the canonical capture tree (native-black exterior, 2 device px out, web
          max channel 0), every generation, both tiers. Gated: WebGPU.
  L1      |interiorMeanWeb - interiorMeanNative| <= 0.055 on calibration/validation, recomputed from
          the rows; the growth clause is a per-gate reference and is read off the pinned cuts
          (0.5: W36's l1-cut; 0.25: W45's landing cut).
  E2      the absolute per-cell edge residual in codes (`cuts.cut_e2`'s meanAbsCodes, W38's bins).
          It is gated only as growth against a reference (0.25, W45's landing cut: failing and
          named-miss cells are read off it); on the 0.5 generation it has no reference and is
          computed here as an absolute reading (reference = itself), NOT GATED.

    VITREA_WEB_CAPTURES=<canonical tree> python3.12 -B rows_union.py
"""
from __future__ import annotations

import json
import os
import re
import statistics
import sys
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
CAL = HERE.parents[1]
sys.path.insert(0, str(CAL / "results" / "2026-10-03-w44-g1-refit" / "cuts"))
import bed as B  # noqa: E402
import cuts as C  # noqa: E402

CAPTURES = Path(os.environ.get("VITREA_WEB_CAPTURES", str(C.CANONICAL_CAPTURES)))
GENERATIONS = {"light 0.5": "85ad7f7e3e0d", "dark 0.5": "0eac5b294cc2",
               "light 0.25": "ebc3d9105a4a", "dark 0.25": "d0219cd684bf"}
LANDING = json.loads((CAL / "results/2026-10-03-w45-g2-landing/cuts/cut-025-w45-landing.json").read_text())
CHROMA_05 = json.loads((CAL / "results/2026-09-24-w36-g1-black-branch/chroma-cut.json").read_text())
L1_05 = json.loads((CAL / "results/2026-09-24-w36-g2-landing/l1-cut.json").read_text())
TIER = {"webgpu": "texture", "css": "dom"}


def mine(cell: str, scheme: str) -> bool:
    """Is a cut's `profile/scene` label of this scheme? Read on the PROFILE half only: a scene id
    such as `mid-dark-solid__...` carries a scheme word of its own."""
    return f"-{scheme}-" in cell.split("/")[0]


def short(p):
    return p.replace("apple-macos-27.0-", "")


def standard(profile):
    return "-standard-" in profile


def all_rows(active):
    import matrix_store
    return matrix_store.load_generation(active)


def missed_27():
    src = C.TEST.read_text()
    body = src[src.index("const MISSED_27_ROWS"):]
    body = body[:body.index("\n};")]
    out = Counter()
    for key in re.findall(r'^\s*"([^"]+ :: [^"]+)":', body, re.M):
        head, metric = key.split(" :: ")
        tier, _set, _scene, profile = head.split(" / ")
        out[(profile, tier, metric)] += 1
    return out


def tables(rows, owner):
    """Per (profile, renderer): gated misses (by set column) and not-gated misses."""
    out = {}
    by = defaultdict(list)
    for r in rows:
        by[(r["key"]["profileKey"], r["key"]["web"]["renderer"])].append(r)
    for (profile, renderer), group in sorted(by.items()):
        twin = profile.replace("-glass0.25", "-glass0.5")
        table = owner["profiles"][twin][TIER[renderer]]
        gated, ungated = [], []
        for r in group:
            sid = r["key"]["sceneId"]
            in_gate = (r["fixtureSet"] not in ("probe", "recorded") and B.SCENES.role.get(sid) != "recorded"
                       and r.get("state") != "inactive" and not B.SCENES.inactive(sid))
            (gated if in_gate else ungated).append(r)

        def misses(rs):
            found, checks = [], 0
            for axis, metric, cmp, threshold in table:
                for r in rs:
                    if axis == "shape" and (r.get("shape") is None or not C.well_conditioned(r)):
                        continue
                    v = B.value(r, axis, metric)
                    checks += 1
                    ok = v is not None and (v >= threshold if cmp == "≥" else v <= threshold)
                    if not ok:
                        found.append(dict(scene=r["key"]["sceneId"], set=r["fixtureSet"], metric=metric,
                                          measured=v, bound=f"{cmp} {threshold}",
                                          margin=None if v is None else (v - threshold if cmp == "≥" else threshold - v)))
            return found, checks
        gm, gc = misses(gated)
        um, uc = misses(ungated)
        out[f"{profile} {renderer}"] = dict(
            table=[list(t) for t in table], gatedCells=len(gated), gatedChecks=gc,
            gatedMisses=[m for m in gm if m["set"] != "holdout"],
            gatedHoldoutMisses=[m for m in gm if m["set"] == "holdout"],
            notGatedCells=len(ungated), notGatedChecks=uc, notGatedMisses=um)
    return out


def m1(rows):
    out = {}
    for renderer in ("webgpu", "css"):
        cells = []
        for r in rows:
            sid = r["key"]["sceneId"]
            if r["key"]["web"]["renderer"] != renderer or not standard(r["key"]["profileKey"]):
                continue
            if not C.chroma_member(sid):
                continue
            web = B.value(r, "material", "chromaStructureRatioWeb")
            nat = B.value(r, "material", "chromaStructureRatioNative")
            if None in (web, nat):
                cells.append(dict(cell=f"{short(r['key']['profileKey'])}/{sid}", R=None))
                continue
            cells.append(dict(cell=f"{short(r['key']['profileKey'])}/{sid}", R=web / nat,
                              pose="inactive" if B.SCENES.inactive(sid) else "active",
                              scale=B.scale_of(r["key"]["profileKey"])))
        ok = [c for c in cells if c["R"] is not None]
        beds = {}
        for pose in ("active", "inactive"):
            g = [c["R"] for c in ok if c["pose"] == pose]
            if g:
                beds[pose] = dict(cells=len(g), median=statistics.median(g), min=min(g), max=max(g))
        out[renderer] = dict(cells=len(cells), unmeasured=[c["cell"] for c in cells if c["R"] is None],
                             beds=beds,
                             medianOutside=[p for p, b in beds.items() if not 0.8 <= b["median"] <= 1.2],
                             cellMisses=[c for c in ok if not 0.6 <= c["R"] <= 1.4])
    return out


def l1_absolute(rows):
    out = {}
    for renderer in ("webgpu", "css"):
        cells = []
        for r in rows:
            sid = r["key"]["sceneId"]
            if r["key"]["web"]["renderer"] != renderer or not standard(r["key"]["profileKey"]):
                continue
            if B.SCENES.role.get(sid) not in ("calibration", "validation"):
                continue
            n, w = B.value(r, "material", "interiorMeanNative"), B.value(r, "material", "interiorMeanWeb")
            cells.append(dict(cell=f"{short(r['key']['profileKey'])}/{sid}", native=n, web=w,
                              error=None if None in (n, w) else abs(w - n),
                              signed=None if None in (n, w) else w - n))
        ok = [c for c in cells if c["error"] is not None]
        out[renderer] = dict(cells=len(cells), measured=len(ok),
                             unmeasured=[c["cell"] for c in cells if c["error"] is None],
                             misses=[c for c in ok if c["error"] > C.L1_ABSOLUTE],
                             maxError=max(c["error"] for c in ok),
                             medianError=statistics.median(c["error"] for c in ok))
    return out


def main() -> int:
    owner = C.owner_tables()
    missed = missed_27()
    result = dict(what="W46 grounding: every adopted row but T1 over the current macOS 27 union",
                  generations=GENERATIONS, captures=str(CAPTURES), perGeneration={})
    C.REFEREES = set()  # the referees were spent at read 7; every member is read as an ordinary one
    for label, active in GENERATIONS.items():
        rows = all_rows(active)
        bed = B.load_published(active)  # standard rows, documents checked against the index
        B.PROFILES = tuple(sorted({r["key"]["profileKey"] for r in bed.rows}))
        g = dict(tables=tables(rows, owner), M1=m1(rows), L1absolute=l1_absolute(rows))
        g["C1"] = {t: C.cut_c1(bed, t, {}) for t in ("webgpu", "css")}
        g["X1"] = {t: {k: v for k, v in C.cut_x1(bed, CAPTURES, t).items() if k != "perCell"}
                   for t in ("webgpu", "css")}
        if "0.25" in label:
            scheme = label.split()[0]
            g["M2"] = {t: dict(source="W45 landing cut (reference c05 light / d0219 dark)",
                               misses=[m for m in LANDING["M2"][t]["misses"] if mine(m["cell"], scheme)])
                       for t in ("webgpu", "css")}
            g["L1growth"] = {t: dict(source="W45 landing cut",
                                     growthMisses=[c for c in LANDING["L1"][t]["growthMisses"] if mine(c["cell"], scheme)],
                                     maxGrowth=max((c["growth"] for c in LANDING["L1"][t]["cells"]
                                                    if mine(c["cell"], scheme) and c["growth"] is not None), default=None))
                             for t in ("webgpu", "css")}
            e2 = {}
            for t in ("webgpu", "css"):
                per = [c for c in LANDING["E2"][t]["perCell"] if mine(c["cell"], scheme)]
                e2[t] = dict(source="W45 landing cut (growth against c05 light / itself dark)",
                             cells=len(per), failing=[c["cell"] for c in LANDING["E2"][t]["failing"] if mine(c["cell"], scheme)],
                             namedMissCells=[c for c in LANDING["E2"][t]["namedMissCells"] if mine(c, scheme)],
                             perCell=[dict(cell=c["cell"], meanAbsCodes=c.get("meanAbsCodes"), change=c.get("change")) for c in per])
            g["E2"] = e2
        else:
            scheme = label.split()[0]
            g["M2"] = {"webgpu": dict(source="W36 chroma-cut (reference W33 6e509c7f76cc / eab099cc6698)",
                                      misses=[c for c in CHROMA_05["cells"] if c["scheme"] == scheme
                                              and abs(c["structureDeltaFraction"]) > C.M2_TOLERANCE],
                                      cells=sum(c["scheme"] == scheme for c in CHROMA_05["cells"]))}
            g["L1growth"] = {"webgpu": dict(source="W36 l1-cut (baseline W33)",
                                            growthMisses=[c["cell"] for c in L1_05["growthFailures"] if mine(c["cell"], scheme)],
                                            absoluteMissesRecorded=[c["cell"] for c in L1_05["absoluteMisses"] if mine(c["cell"], scheme)])}
            e2 = {}
            for t in ("webgpu", "css"):
                got = C.cut_e2(bed, CAPTURES, bed, CAPTURES, t)
                e2[t] = dict(source="computed here, absolute only (no reference): NOT GATED",
                             cells=got["cells"], unmeasured=got["unmeasured"], noRow=got["noRow"],
                             perCell=[dict(cell=c["cell"], meanAbsCodes=c.get("meanAbsCodes")) for c in got["perCell"]])
            g["E2"] = e2
        # Cross-check the tables' gated misses against MISSED_27_ROWS (table metrics only).
        table_metrics = {"silhouetteIoU", "contourDistanceMean", "contourDistanceP95", "ssimMean",
                         "oklabDeltaEMean", "oklabDeltaEP95", "edgeWeightedMean", "ssimOutside"}
        check = {}
        for key, t in g["tables"].items():
            profile, renderer = key.rsplit(" ", 1)
            ours = Counter(m["metric"] for m in t["gatedMisses"] + t["gatedHoldoutMisses"])
            theirs = Counter({m: n for (p, tier, m), n in missed.items()
                              if p == profile and tier == TIER[renderer] and m in table_metrics})
            check[key] = dict(agree=ours == theirs, mine=dict(ours), missed27=dict(theirs))
        g["tablesVsMissed27"] = check
        result["perGeneration"][label] = g
        print(label, "done")
    (HERE / "rows-union.json").write_text(json.dumps(result, indent=1, default=str) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
