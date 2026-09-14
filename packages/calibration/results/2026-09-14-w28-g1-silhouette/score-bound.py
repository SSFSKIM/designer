#!/usr/bin/env python3
"""W28 G2: G1d score-bound.py arithmetic, bound and seven-run bed unchanged.

Only admission and publication differ: this gate accepts ONLY the W28 seal,
records W28's empty checking-set fit spend, and writes exclusively to a named
scratch output. G1's dry run invokes only --check-renderer, never scoring or fixture I/O.

python3 score-bound.py /tmp/w28-g2/checking.json /tmp/w28-g2/verdict.json
"""
import hashlib
import json
import os
import sys
from statistics import mean

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = HERE.split("/packages/")[0]
G1B = os.path.join(HERE, "../2026-09-11-w27c-g1b")


def scratch_path(path, repo):
    import subprocess
    common = subprocess.check_output([
        "git", "-C", str(repo), "rev-parse", "--path-format=absolute", "--git-common-dir"
    ], text=True).strip()
    roots = (os.path.realpath(repo), os.path.dirname(os.path.realpath(common)))
    output = os.path.realpath(path)
    if any(os.path.commonpath([output, root]) == root for root in roots):
        raise SystemExit("score-bound: output must be outside the repository")


def verify_files(hashes, repo):
    for file, expected in hashes.items():
        with open(os.path.join(repo, file), "rb") as handle:
            actual = hashlib.sha256(handle.read()).hexdigest()
        if actual != expected:
            raise SystemExit("score-bound: fingerprint mismatch " + file)


def measurement_evidence(row):
    """Validate persisted evidence, independently of the reader's resume admission."""
    import math
    import re
    def require(condition):
        if not condition:
            raise SystemExit("score-bound: incomplete or invalid measurement evidence")
    def finite(value):
        return type(value) in (int, float) and math.isfinite(value) and value >= 0
    def pair(value):
        return isinstance(value, list) and len(value) == 2 and all(
            type(v) is int and v > 0 for v in value)
    body = row.get("body") or {}
    require(finite((row.get("deltaE") or {}).get("mean")))
    require(type(body.get("n")) is int and body["n"] > 0)
    require(all(finite(body.get(k)) for k in (
        "deltaE", "webY", "nativeY", "webSD", "nativeSD", "webChroma", "nativeChroma")))
    require(row.get("repeats") == 2 and row.get("isControl") is False)
    require(all(type(row.get(k)) is bool for k in ("isHoldout", "preAttestationRecovered", "scored")))
    require(isinstance(row.get("groups"), list) and bool(row["groups"]))
    require(all(isinstance(row.get(k), str) and row[k] for k in ("capture", "nativePath")))
    require(all(isinstance(row.get(k), str) and re.fullmatch(r"[a-f0-9]{64}", row[k])
                for k in ("captureSha256", "nativeSha256", "backgroundSha256")))
    g = row.get("geometry") or {}
    require(pair(g.get("capturedPixels")) and pair(g.get("pixelSize")))
    require(g["capturedPixels"] == g["pixelSize"] and body["n"] <= g["pixelSize"][0] * g["pixelSize"][1])
    scale = row.get("scale")
    require(scale in (1, 2) and g.get("requestedScale") == scale and g.get("devicePixelRatio") == scale)
    canvas = g.get("canvas") or {}
    require(finite(canvas.get("width")) and finite(canvas.get("height")))
    require([canvas["width"] * scale, canvas["height"] * scale] == g["pixelSize"])
    adapter = row.get("adapter") or {}
    require(adapter.get("ok") is True and adapter.get("isFallback") is False)
    groups = row.get("actualGroups")
    require(isinstance(groups, list) and bool(groups))
    require(all((g.get("state") or {}).get("activeRenderer") == "webgpu" for g in groups))
    require(row.get("problems") == [])
    if row["preAttestationRecovered"]:
        require(row["isHoldout"] and not row["scored"] and "H" in row["groups"] and
                row.get("nativeSource") == "recovered" and row.get("nativeRun") is None)
        lineage = row.get("recoveredLineage") or {}
        require(all(isinstance(lineage.get(k), str) and re.fullmatch(r"[a-f0-9]{40}", lineage[k])
                    for k in ("nativeBlobOid", "backgroundBlobOid")))
    else:
        require(row.get("nativeSource") in ("sitting", "bundle") and
                isinstance(row.get("nativeRun"), str) and bool(row["nativeRun"]))
        proof = row.get("nativeAttestation") or {}
        require(row.get("state") in ("rest", "pressed", "inactive"))
        if row["state"] == "inactive":
            p = proof.get("presentation") or {}
            require(proof.get("presentedActive") is False and p.get("observedPose") == "inactive"
                    and p.get("isKeyWindow") is False and p.get("appIsActive") is False)
        else:
            require(proof.get("presentedActive") is True)


def bound_renderer(renderer):
    if renderer != "webgpu":
        raise SystemExit("score-bound: only WebGPU reads may be scored; CSS is record-only")


def check_renderer_command(args):
    """The DRY harness exercises the actual tier gate without entering scoring or fixture I/O."""
    if not args or args[0] != "--check-renderer":
        return False
    if len(args) != 2:
        raise SystemExit("usage: score-bound.py --check-renderer RENDERER")
    bound_renderer(args[1])
    return True


def main():
    if len(sys.argv) != 3:
        raise SystemExit("usage: score-bound.py SCRATCH_MATRIX SCRATCH_VERDICT")
    output = os.path.realpath(sys.argv[2])
    scratch_path(output, REPO)
    if os.path.exists(output):
        raise SystemExit("score-bound: refusing output overwrite")
    read = json.load(open(sys.argv[1]))
    bound_renderer(read.get("renderer"))
    bound = json.load(open(os.path.join(G1B, "bound.json")))
    bed = json.load(open(os.path.join(G1B, "checking-bed.json")))
    decomposition = json.load(open(os.path.join(G1B, "decomposition.json")))

    clause1 = next(c for c in bound["clauses"] if c["id"] == "1")["thresholds"]
    clause2 = next(c for c in bound["clauses"] if c["id"] == "2")["thresholds"]
    checking = set(next(g for g in bed["groups"] if g["id"] == "D")["scenes"])

    rows = read["rows"]
    for row in rows:
        if row.get("scored") != (row["scene"] in checking):
            raise SystemExit("score-bound: checking role mismatch")

    # The contract the matrix has to satisfy before any of it is scored.
    #
    # Completeness is not enough on its own. Every threshold in `bound.json` is a
    # WebGPU-tier number, so a CSS matrix scored against them would read as a
    # verdict rather than as a category error; `--once` drops the independent
    # repeat the frozen instrument requires and its rows cannot be called settled;
    # a duplicated `profile/scene` pair silently reweights a mean; and a matrix
    # produced against some other endpoint is not this gate's read at all. Each is
    # cheap to state and none of them announces itself in the numbers.
    fitted = json.load(open(os.path.join(HERE, "fitted-endpoint.json")))
    partition = json.load(open(os.path.join(HERE, "partition.json")))
    verify_files(fitted["sourceSha256"], REPO)
    verify_files(fitted["instrumentSha256"], REPO)

    admissible = {fitted["patchSha256"]: "the W28 G1 sealed endpoint (claims §5.145)"}
    if read.get("readAgainst") != fitted["profiles"]:
        raise SystemExit("score-bound: matrix resolved declarations differ from the seal")
    for scheme in ("light", "dark"):
        if read.get("endpointUnderTest", {}).get(scheme + "InactiveSha256") != fitted["profiles"][scheme]["inactiveSha256"]:
            raise SystemExit("score-bound: resolved endpoint mismatch")
    for field in ("sourceSha256", "instrumentSha256", "sceneSpecSha256"):
        if read.get(field) != fitted.get(field):
            raise SystemExit("score-bound: sealed " + field + " mismatch")
    if {r["cell"] for r in partition["rows"] if r["scene"] in checking}:
        raise SystemExit("score-bound: W28 fit spent the checking set")
    expected_holdout = set(fitted["holdout"]["cells"])
    plurality = json.load(open(os.path.join(HERE, "../2026-09-14-w27c-g1d/plurality.json")))
    for row in rows:
        measurement_evidence(row)
        cell = row["profile"] + "/" + row["scene"]
        if row["isHoldout"] != (cell in expected_holdout):
            raise SystemExit("score-bound: holdout role mismatch")
        if row["preAttestationRecovered"]:
            if row["recoveredLineage"] != fitted["holdout"]["recoveredLineage"].get(cell):
                raise SystemExit("score-bound: recovered holdout lineage mismatch")
        else:
            tally = next((p["cellTally"][cell] for p in plurality["passes"]
                          if cell in p["cellTally"]), None)
            if not tally or row["nativeSha256"] != tally["pluralitySha256"] or \
                    tally["perRunSha256"].get(row["nativeRun"]) != row["nativeSha256"]:
                raise SystemExit("score-bound: native plurality mismatch")
    if not expected_holdout.issubset({r["profile"] + "/" + r["scene"] for r in rows}):
        raise SystemExit("score-bound: the sealed holdout read is incomplete")
    pairs = [(r["profile"], r["scene"]) for r in rows]
    duplicated = sorted({p for p in pairs if pairs.count(p) > 1})
    breaches = []
    not_repeated = sorted({f"{r['profile']}/{r['scene']}" for r in rows if r.get("repeats") != 2})
    if not_repeated:
        breaches.append(f"{len(not_repeated)} row(s) were captured once rather than twice, so "
                        f"their determinism was never checked: {', '.join(not_repeated[:6])}")
    if duplicated:
        breaches.append(f"{len(duplicated)} profile/scene pair(s) appear more than once: "
                        + ", ".join(f"{p}/{s}" for p, s in duplicated[:6]))
    if read.get("patchSha256") not in admissible:
        breaches.append(
            f"the read applied patch {read.get('patchSha256')}, not the W28 sealed endpoint")
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
        "gate": "W28 G2 frozen bound read",
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
                row["cell"] for row in partition["rows"]
                if row["scene"] in checking
            ),
        },
        "bound": "packages/calibration/results/2026-09-11-w27c-g1b/bound.json, declared 2026-09-11",
        "read": sys.argv[1] if len(sys.argv) > 1 else "/tmp/w27c-g2/checking.json",
        "holdingIs": bound["whatHoldingMeans"]["g2Unblocks"],
        "profilesHolding": sorted(p for p in verdict if verdict[p]["holdsJointly"]),
        "profilesFailing": sorted(p for p in verdict if not verdict[p]["holdsJointly"]),
        "perProfile": verdict,
        "supplyingGroups": supplying,
        "holdout": {
            "rule": fitted["holdout"]["rule"],
            "limitation": fitted["holdout"]["limitation"],
            "rows": [r for r in rows if r["isHoldout"]],
            "scoredByBound": False,
        },
    }
    with open(output, "x") as handle:
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


if __name__ == "__main__":
    if not check_renderer_command(sys.argv[1:]):
        sys.exit(main())
