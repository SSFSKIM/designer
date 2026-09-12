#!/usr/bin/env python3
"""W27c G2 read: the declared bound applied to the checking bed, clause by clause.

`bound.json` was declared on 2026-09-11, before the bed it scores existed. This
applies it exactly as written and scoped as written — clauses 1, 2 and 3 over the
checking set (group D), clause 4's publication over every cell the read produced,
clause 5's refusals enforced inside the driver — and reports per profile whether
it holds. It narrows nothing, re-scopes nothing and re-declares nothing: where a
clause fails, the failure is the output.

    python3 score-bound.py /tmp/w27c-g2/checking.json
"""
import json
import os
import sys
from statistics import mean

HERE = os.path.dirname(os.path.abspath(__file__))
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
        "gate": "W27c G2 read / claims §5.139",
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
