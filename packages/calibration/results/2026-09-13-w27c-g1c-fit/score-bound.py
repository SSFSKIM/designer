#!/usr/bin/env python3
"""W27c G1c: the SAME declared bound re-applied to the re-read, clause by clause.

This is `2026-09-13-w27c-g2-read/score-bound.py` with one thing changed and
nothing loosened. `bound.json` was declared on 2026-09-11, before the bed it
scores existed, and it is applied here exactly as written and scoped as written —
clauses 1, 2 and 3 over the checking set (group D), clause 4's publication over
every cell the read produced, clause 5's refusals enforced inside the driver. No
clause is narrowed, re-scoped or re-declared, and where a clause fails the
failure is the output.

The one change is the endpoint the read is allowed to have been taken against.
The G2 scorer refuses a matrix whose `patchSha256` is not the frozen G1
declaration's, which is exactly right for a read OF that endpoint and exactly
wrong for a read of the endpoint that replaces it. So the refusal now admits
either the frozen document or the one this child declared in
`fitted-endpoint.json`, and names which one the matrix carried. A second refusal
is added rather than removed: a matrix that does not record both of the machine's
accessibility settings off is refused, because the browser suites inherit them
and a capture taken under either is not evidence.

Beside the verdict it publishes `declaredSpend`, from `partition.json`: the cells
this child's fit selected on that the bound also scores. Nothing about the
scoring changes — a spent cell is scored exactly as it would be otherwise — but a
profile's verdict may not be read as an unspent check on a cell the fit saw, and
that has to travel with the number rather than sit in prose somewhere else.

    python3 score-bound.py /tmp/w27c-g1c/checking.json
"""
import hashlib
import json
import os
import sys
from statistics import mean

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = HERE.split("/packages/")[0]
G1B = os.path.join(HERE, "../2026-09-11-w27c-g1b")


def main():
    read = json.load(open(sys.argv[1] if len(sys.argv) > 1 else "/tmp/w27c-g2/checking.json"))
    bound = json.load(open(os.path.join(G1B, "bound.json")))
    bed = json.load(open(os.path.join(G1B, "checking-bed.json")))
    decomposition = json.load(open(os.path.join(G1B, "decomposition.json")))

    clause1 = next(c for c in bound["clauses"] if c["id"] == "1")["thresholds"]
    clause2 = next(c for c in bound["clauses"] if c["id"] == "2")["thresholds"]
    checking = set(next(g for g in bed["groups"] if g["id"] == "D")["scenes"])

    rows = read["rows"]
    for row in rows:
        assert row["scored"] == (row["scene"] in checking), row["scene"]

    # The contract the matrix has to satisfy before any of it is scored.
    #
    # Completeness is not enough on its own. Every threshold in `bound.json` is a
    # WebGPU-tier number, so a CSS matrix scored against them would read as a
    # verdict rather than as a category error; `--once` drops the independent
    # repeat the frozen instrument requires and its rows cannot be called settled;
    # a duplicated `profile/scene` pair silently reweights a mean; and a matrix
    # produced against some other endpoint is not this gate's read at all. Each is
    # cheap to state and none of them announces itself in the numbers.
    frozen = json.load(open(os.path.join(
        REPO, "packages/calibration/results/2026-09-10-w27c-g1-corrected-declaration.json")))
    fitted = json.load(open(os.path.join(HERE, "fitted-endpoint.json")))
    partition = json.load(open(os.path.join(HERE, "partition.json")))

    # The driver's own `sha(JSON.stringify(candidate))`: compact separators and
    # the document's own key order, which is the order the export was serialised
    # in. Two digests are admissible and the verdict names which one the matrix
    # carried — the frozen G1 endpoint, and the endpoint this child declared.
    def patch_digest(patch):
        return hashlib.sha256(
            json.dumps(patch, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
        ).hexdigest()

    admissible = {
        patch_digest(frozen["patch"]): "the frozen G1 endpoint (claims §5.130 §7)",
        patch_digest(fitted["patch"]): "the W27c G1c fitted endpoint (claims §5.141)",
    }
    pairs = [(r["profile"], r["scene"]) for r in rows]
    duplicated = sorted({p for p in pairs if pairs.count(p) > 1})
    breaches = []
    if read.get("renderer") != "webgpu":
        breaches.append(f"the read is on the {read.get('renderer')} tier and every threshold in "
                        "bound.json is a WebGPU-tier number")
    not_repeated = sorted({f"{r['profile']}/{r['scene']}" for r in rows if r.get("repeats") != 2})
    if not_repeated:
        breaches.append(f"{len(not_repeated)} row(s) were captured once rather than twice, so "
                        f"their determinism was never checked: {', '.join(not_repeated[:6])}")
    if duplicated:
        breaches.append(f"{len(duplicated)} profile/scene pair(s) appear more than once: "
                        + ", ".join(f"{p}/{s}" for p, s in duplicated[:6]))
    if read.get("patchSha256") not in admissible:
        breaches.append(
            f"the read applied patch {read.get('patchSha256')}, which is neither the frozen G1 "
            "endpoint nor the endpoint fitted-endpoint.json declares")
    machine = read.get("machineAccessibility") or {}
    if machine.get("reduceTransparency") != 0 or machine.get("increaseContrast") != 0:
        breaches.append(
            "the read does not record both of the machine's own accessibility settings off: the "
            "browser suites inherit them and a capture taken under either is not evidence")
    if breaches:
        raise SystemExit("score-bound: refusing to score. The read is outside this gate's "
                         "declared contract.\n" + "".join(f"  {b}\n" for b in breaches))

    # What the checking set IS, taken from the declaration: group D crossed with
    # the profiles `scenes.json` declares each of its ids for.
    #
    # Deriving the population from the rows instead would let this scorer score
    # whatever it was handed. A partial read is the ordinary way that happens — a
    # driver stopped part-way, a filtered re-run — and it does not announce
    # itself: drop `dark-solid__rrect-48__inactive` from the increased-contrast
    # profile and that profile goes from FAILS to HOLDS, on a mean over eleven
    # cells that reads exactly like a mean over twelve. A bound scored on a
    # population the bound did not name is not the bound.
    scenes_doc = json.load(open(os.path.join(REPO, "apps/reference-apple/scenes.json")))
    every_scene = [s["id"] for s in scenes_doc["scenes"]]
    expected = set()
    for p in scenes_doc["profiles"]:
        declared = every_scene if p["scenes"] == "all" else p["scenes"]
        expected.update((p["key"], i) for i in declared if i in checking)
    present = {(r["profile"], r["scene"]) for r in rows if r["scored"]}
    missing = sorted(expected - present)
    surplus = sorted(present - expected)
    if missing or surplus:
        raise SystemExit(
            "score-bound: refusing to score. The read does not carry the checking set the bound "
            f"names ({len(expected)} cells, group D of checking-bed.json crossed with the profiles "
            "scenes.json declares each id for).\n"
            + "".join(f"  missing   {p}/{s}\n" for p, s in missing)
            + "".join(f"  unnamed   {p}/{s}\n" for p, s in surplus)
        )

    profiles = sorted({r["profile"] for r in rows})
    verdict = {}
    for profile in profiles:
        scored = [r for r in rows if r["profile"] == profile and r["scored"]]
        every = [r for r in rows if r["profile"] == profile]
        ceiling = clause1[profile]
        threshold = clause2[profile]
        over_ceiling = [
            {"scene": r["scene"], "deltaE": r["deltaE"]["mean"],
             "multipleOfCeiling": r["deltaE"]["mean"] / ceiling}
            for r in scored if r["deltaE"]["mean"] > ceiling
        ]
        body_mean = mean(r["body"]["deltaE"] for r in scored) if scored else None
        over_floor = [
            {"scene": r["scene"], "bodyDeltaE": r["body"]["deltaE"],
             "multipleOfThreshold": r["body"]["deltaE"] / threshold}
            for r in scored if r["body"]["deltaE"] > 2 * threshold
        ]
        # Clause 4: reported, explicitly not a gate quantity.
        key = profile.replace("apple-macos-26.5-", "")
        cal = decomposition["perProfile"][key]["calibration"]
        verdict[profile] = {
            "checkingCells": len(scored),
            "cellsRead": len(every),
            "clause1": {
                "ceiling": ceiling,
                "worst": max((r["deltaE"]["mean"] for r in scored), default=None),
                "worstCell": max(scored, key=lambda r: r["deltaE"]["mean"])["scene"] if scored else None,
                "exceedances": over_ceiling,
                "holds": not over_ceiling,
            },
            "clause2": {
                "threshold": threshold,
                "meanBodyDeltaE": body_mean,
                "multipleOfThreshold": (body_mean / threshold) if body_mean else None,
                "holds": body_mean is not None and body_mean <= threshold,
            },
            "clause3": {
                "floor": 2 * threshold,
                "exceedances": sorted(over_floor, key=lambda e: -e["multipleOfThreshold"]),
                "holds": not over_floor,
            },
            "clause4Reported": {
                "$comment": "reported, and explicitly NOT a gate quantity (bound.json clause 4): "
                            "the sets differ in footprint composition by construction",
                "frozenCalibrationMeanFullCanvas": cal["meanFullCanvasDeltaE"],
                "checkingMeanFullCanvas": mean(r["deltaE"]["mean"] for r in scored) if scored else None,
                "fullCanvasRatioToCalibration":
                    (mean(r["deltaE"]["mean"] for r in scored) / cal["meanFullCanvasDeltaE"]) if scored else None,
                "frozenCalibrationMeanBody": cal["meanBodyDeltaE"],
                "bodyRatioToCalibration":
                    (body_mean / cal["meanBodyDeltaE"]) if body_mean else None,
                "frozenCalibrationFootprint": cal["meanFootprintAreaFraction"],
                "checkingFootprint": mean(
                    r["body"]["n"] / (r["geometry"]["capturedPixels"][0] * r["geometry"]["capturedPixels"][1])
                    for r in scored) if scored else None,
            },
        }
        verdict[profile]["holdsJointly"] = (
            verdict[profile]["clause1"]["holds"]
            and verdict[profile]["clause2"]["holds"]
            and verdict[profile]["clause3"]["holds"]
        )

    # The supplying groups, published because they are what the bed measures.
    supplying = {}
    for group in bed["groups"]:
        if group["role"] == "checking":
            continue
        members = [r for r in rows if group["id"] in (r["groups"] or [])]
        supplying[group["id"]] = {
            "name": group["name"],
            "decides": group.get("decides"),
            "cellsRead": len(members),
            "rows": sorted(
                [{"profile": r["profile"], "scene": r["scene"],
                  "bodyDeltaE": r["body"]["deltaE"],
                  "webY": r["body"]["webY"], "nativeY": r["body"]["nativeY"],
                  "webSD": r["body"]["webSD"], "nativeSD": r["body"]["nativeSD"],
                  "webChroma": r["body"]["webChroma"], "nativeChroma": r["body"]["nativeChroma"]}
                 for r in members],
                key=lambda r: (r["profile"], r["scene"]),
            ),
        }

    out = {
        "gate": "W27c G1c re-read / claims §5.141",
        "endpointScored": admissible[read["patchSha256"]],
        "patchSha256": read["patchSha256"],
        "machineAccessibility": read.get("machineAccessibility"),
        "declaredSpend": {
            "$comment": "partition.json, declared before the fit: the cells this child's fit "
                        "selected on that the bound also scores. The bound is applied unchanged "
                        "and a spent cell is scored exactly as it would be otherwise, but a "
                        "profile whose verdict rests on one of these is not an unspent check on "
                        "that cell.",
            "cells": sorted(
                cell
                for term in partition["terms"]
                for cell in term["calibration"]["cells"]
                if cell.split("/")[1] in checking
            ),
        },
        "bound": "packages/calibration/results/2026-09-11-w27c-g1b/bound.json, declared 2026-09-11",
        "read": sys.argv[1] if len(sys.argv) > 1 else "/tmp/w27c-g2/checking.json",
        "holdingIs": bound["whatHoldingMeans"]["g2Unblocks"],
        "profilesHolding": sorted(p for p in verdict if verdict[p]["holdsJointly"]),
        "profilesFailing": sorted(p for p in verdict if not verdict[p]["holdsJointly"]),
        "perProfile": verdict,
        "supplyingGroups": supplying,
    }
    with open(os.path.join(HERE, "verdict.json"), "w") as handle:
        json.dump(out, handle, indent=1)
        handle.write("\n")

    for profile in profiles:
        v = verdict[profile]
        print(f"\n{profile}  ({v['checkingCells']} checking cells)")
        print(f"  clause 1 ceiling {v['clause1']['ceiling']}: "
              f"{'HOLDS' if v['clause1']['holds'] else 'FAILS'} "
              f"(worst {v['clause1']['worst']:.5f} on {v['clause1']['worstCell']})")
        print(f"  clause 2 threshold {v['clause2']['threshold']}: "
              f"{'HOLDS' if v['clause2']['holds'] else 'FAILS'} "
              f"(mean body ΔE {v['clause2']['meanBodyDeltaE']:.5f}, "
              f"{v['clause2']['multipleOfThreshold']:.2f}×)")
        print(f"  clause 3 floor {v['clause3']['floor']}: "
              f"{'HOLDS' if v['clause3']['holds'] else 'FAILS'} "
              f"({len(v['clause3']['exceedances'])} cell(s) over)")
        for e in v["clause3"]["exceedances"]:
            print(f"      {e['scene']:48s} {e['bodyDeltaE']:.5f}  {e['multipleOfThreshold']:.2f}×")
        print(f"  JOINT: {'HOLDS' if v['holdsJointly'] else 'FAILS'}")
    print(f"\nprofiles holding the bound: {len(out['profilesHolding'])} of {len(profiles)}")


sys.exit(main())
