"""Read completed W49b gate-only scratch renders. No imputation, selection, seal or publication.

python -I read.py batch.json --candidates /scratch/candidates --renders /scratch/renders \
    --out /scratch/new-readings.json [--labels LABEL ...]

Every requested gate cell is read, even when a leaf has no authority there. Withheld and
unrequested cells retain UNMEASURED status. T1-low guards T regression; T1-fine reads T fidelity.
All twenty standing constraints are emitted regardless of any authorisation-list contents.
Other owner rows are explicitly NOT_READ here: this is an identifying ladder, not a full gate.
"""
import argparse
import importlib.util
import json
import math
from pathlib import Path
from statistics import median
import sys

HERE = Path(__file__).resolve().parent
s = importlib.util.spec_from_file_location("w49b_common", HERE / "common.py")
C = importlib.util.module_from_spec(s); s.loader.exec_module(C)
s = importlib.util.spec_from_file_location("w49b_render", HERE / "render.py")
L = importlib.util.module_from_spec(s); s.loader.exec_module(L)


def summarize(registry, results):
    """Known gate failures are binding; missing evidence is never promoted to a pass."""
    measured = [r for r in results if r["measured"] is not None]
    failures = [r for r in measured if r["currentStatus"] == "FAIL" or
                (r["historical"] and r["historical"]["enforced"] and r["historicalStatus"] == "FAIL")]
    summary = {"standingConstraints": sum(r["role"] is not None for r in results),
               "measured": len(measured), "unmeasured": len(results)-len(measured),
               "measuredGateStatus": "FAIL" if failures else "PASS" if measured else "UNMEASURED",
               "acceptance": "UNMEASURED", "landingVerdict": "NOT_A_FULL_GATE",
               "newGrowthBeyondB": [{"scale": r["scale"], "scene": r["scene"]} for r in measured
                                    if r["growthCurrentInB"] > 1 + 1e-12],
               "growthPast3B": [{"scale": r["scale"], "scene": r["scene"]} for r in measured
                                if r["growthCurrentInB"] > 3 + 1e-12],
               "otherOwnerRows": {row: "NOT_READ" for row in ("M2", "L1", "E2", "coherence", "X76")}}
    for role in ("binding", "protected", "prior-repair"):
        group = [r for r in results if r["role"] == role]
        summary[role] = {"total": len(group), "unmeasured": sum(r["measured"] is None for r in group),
                         "currentFailures": sum(r["currentStatus"] == "FAIL" for r in group),
                         "historicalFailures": sum(r["historicalStatus"] == "FAIL" for r in group),
                         "repaired": sum(r["repaired"] for r in group),
                         "historicalEnforced": role != "protected"}
    # Population is declared from the registry, never from whichever rows happen to exist.
    summary["strata"] = []
    lookup = {(r["scale"], r["scene"]): r for r in results}
    for scale in (1, 2):
        for stratum in ("F", "T", "C", "P"):
            for pose in ("rest", "inactive"):
                members = [c for c in registry["cells"] if c["scale"] == scale and c["stratum"] == stratum
                           and c["pose"] == pose and c["partition"] == "gate"]
                if not members: continue
                values = [lookup[c["scale"], c["scene"]] for c in members]
                entry = {"scale": scale, "stratum": stratum, "pose": pose, "partition": "gate", "cells": len(members)}
                if any(r["measured"] is None for r in values):
                    entry["status"] = "UNMEASURED"
                else:
                    errors = [abs(math.log((r["fidelityValue"]+c["B"])/(c["fidelity"]["native"]+c["B"])))
                              for c, r in zip(members, values)]
                    current = [abs(math.log((c["fidelity"]["current"]+c["B"])/(c["fidelity"]["native"]+c["B"])))
                               for c in members]
                    historical = [abs(math.log((c["fidelity"]["reference"]+c["B"])/(c["fidelity"]["native"]+c["B"])))
                                  for c in members]
                    entry.update(status="MEASURED", medianLogError=median(errors),
                                 currentMedianLogError=median(current), historicalMedianLogError=median(historical),
                                 aggregateNoWorse=median(errors) <= median(current) + 1e-12,
                                 historicalHalved=median(errors) <= .5*median(historical) + 1e-12)
                summary["strata"].append(entry)
    return summary


def read_run(registry, plan, folder, candidate, batch_sha, references_sha):
    request = json.loads((folder / "request.json").read_text())
    complete = json.loads((folder / "complete.json").read_text())
    if (request["batchSha256"] != batch_sha or request["referencesSha256"] != references_sha or
            request["candidateSha256"] != C.sha256(candidate) or request["candidate"] != str(candidate)):
        raise ValueError("Request names different batch/reference/candidate bytes")
    for key in ("requested", "planned", "scenes", "scale", "profile", "label", "pose"):
        if request[key] != plan[key]: raise ValueError(f"Requested/planned manifest differs at {key}")
    if complete["matrixSha256"] != C.sha256(folder / "matrix.json"):
        raise ValueError("Completed matrix bytes moved")
    if not json.loads((folder / "census.json").read_text())["passes"]:
        raise ValueError("Census did not pass before this launch")
    if json.loads((folder / "exit.json").read_text())["returncode"] != 0:
        raise ValueError("Partial failed matrix is not a completed experiment")
    if not json.loads((folder / "lock.json").read_text()).get("token"):
        raise ValueError("Launch has no lock ownership record")
    for path, sha in complete["captureEvidence"].items():
        if C.sha256(folder / path) != sha: raise ValueError(f"Changed capture evidence {path}")
    rows = json.loads((folder / "matrix.json").read_text())["cells"]
    L.check_rows(plan, rows, candidate)
    got = [[r["key"]["profileKey"], r["key"]["web"]["renderer"], r["key"]["sceneId"]] for r in rows]
    if (sorted(complete["requested"]) != sorted(plan["requested"]) or
            sorted(complete["planned"]) != sorted(plan["planned"]) or sorted(complete["measured"]) != sorted(got)):
        raise ValueError("Requested/planned/measured completion witness differs")
    # Grounding's corrected reader uses this exact band instrument, not a fresh definition.
    sys.path.insert(0, str(C.CAL / "results/2026-10-03-w44-g1-refit/cuts"))
    import readings as R
    import numpy as np
    from PIL import Image
    references = {(c["scale"], c["scene"]): c for c in registry["cells"]}
    measured = {}
    for row in rows:
        scene = row["key"]["sceneId"]; ref = references[plan["scale"], scene]
        if ref["partition"] != "gate": raise ValueError("Withheld row cannot enter reader")
        web_path = folder / "web-captures" / plan["profile"] / scene / f"{scene}__webgpu.png"
        native_path = Path(ref["nativeFixture"])
        meta = web_path.parent / "cell__webgpu.json"
        if json.loads(meta.read_text()) != row["key"]["web"]:
            raise ValueError("Capture metadata differs from row")
        for path in (web_path, meta):
            if str(path.relative_to(folder)) not in complete["captureEvidence"]:
                raise ValueError("Capture lacks completed byte witness")
        native = np.asarray(Image.open(native_path).convert("RGB"))
        web = np.asarray(Image.open(web_path).convert("RGB"))
        if native.shape != web.shape or list(web.shape[:2][::-1]) != row["key"]["web"]["pixelSize"]:
            raise ValueError("Capture pixel sizes differ")
        geometry = R.cell_geometry(plan["profile"], scene, native)
        bands = R.read(plan["profile"], scene, native, web, geometry)
        raw = row["material"]["interiorStdDevWeb"]["value"]
        raw_native = row["material"]["interiorStdDevNative"]["value"]
        for image, recorded in ((native, raw_native), (web, raw)):
            recomputed = float(R.P.luminance(image)[geometry["silhouette"]].std())
            if not C.finite(recorded) or abs(recomputed-recorded) > 1e-9:
                raise ValueError("Full-silhouette T1 matrix metric differs from its capture pixels")
        if ref["stratum"] == "T":
            if (abs(bands["native"]["low"]-ref["native"]) > 1e-12 or
                    abs(bands["native"]["fine"]-ref["fidelity"]["native"]) > 1e-12):
                raise ValueError("Native text bands differ from the pinned reference cut")
        elif abs(raw_native-ref["native"]) > 1e-12:
            raise ValueError("Native T1 differs from the pinned reference cut")
        value = bands["web"]["low"] if ref["stratum"] == "T" else raw
        fidelity = bands["web"]["fine"] if ref["stratum"] == "T" else raw
        result = C.evaluate_cell(ref, value, fidelity)
        result.update(rawT1=raw, bands=bands, meanNative=row["material"]["interiorMeanNative"]["value"],
                      meanWeb=row["material"]["interiorMeanWeb"]["value"],
                      matrixSha256=complete["matrixSha256"], webSha256=C.sha256(web_path),
                      nativeSha256=C.sha256(native_path))
        # Disjoint native-silhouette regions preserve full T1 while exposing edge/deep structure.
        deep = geometry["silhouette"] & geometry["deep"]
        edge = geometry["silhouette"] & ~deep
        regions = {}
        for name, mask in (("deep", deep), ("edge", edge)):
            regions[name] = {"pixels": int(mask.sum())}
            for side, image in (("native", native), ("web", web)):
                lum = R.P.luminance(image)
                regions[name][side] = {"mean": float(lum[mask].mean()) if mask.any() else None,
                                      "stdDev": float(lum[mask].std()) if mask.any() else None}
        result["disjointRegions"] = regions
        measured[plan["scale"], scene] = result
    return measured


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("batch", type=Path); p.add_argument("--candidates", type=Path, required=True)
    p.add_argument("--renders", type=Path, required=True); p.add_argument("--out", type=Path, required=True)
    p.add_argument("--labels", nargs="+")
    args = p.parse_args()
    references_path = C.DECLARATION / "references.json"
    registry = C.load_registry(references_path)
    batch_path = args.batch.resolve(); batch = C.validate_batch(json.loads(batch_path.read_text()))
    labels = {p["label"] for p in batch["points"]}
    if args.labels and (not set(args.labels).issubset(labels) or len(set(args.labels)) != len(args.labels)):
        raise ValueError("Requested label is absent or duplicated")
    output = L.scratch_destination(args.out)
    if output.exists(): raise FileExistsError(f"Refuse existing readings {output}")
    root_plan = json.loads((args.renders / "plan.json").read_text())
    batch_sha, refs_sha = C.sha256(batch_path), C.sha256(references_path)
    if root_plan["batchSha256"] != batch_sha or root_plan["referencesSha256"] != refs_sha:
        raise ValueError("Root render plan names different bytes")
    reports = []
    for point in batch["points"]:
        if args.labels and point["label"] not in args.labels: continue
        candidate = L.verify_candidate(args.candidates.resolve(), point["label"], batch_path, references_path)
        measured = {}
        for scale in point["scales"]:
            plan = L.plan_run(registry, point, scale)
            if plan not in root_plan["plans"]: raise ValueError("Run is absent from root render plan")
            folder = args.renders / point["label"] / f"{scale}x"
            measured.update(read_run(registry, plan, folder, candidate, batch_sha, refs_sha))
        cells = [measured.get((c["scale"], c["scene"]), C.evaluate_cell(c, None)) for c in registry["cells"]]
        reports.append({"label": point["label"], "prediction": point.get("prediction"),
                        "candidateSha256": C.sha256(candidate), "summary": summarize(registry, cells), "cells": cells})
    C.write_new_json(output, {"schemaVersion": 1, "batchSha256": batch_sha, "referencesSha256": refs_sha,
                             "scope": "W49b G0 gate-only identification; withheld constraints UNMEASURED",
                             "points": reports})
    print(json.dumps({"points": len(reports), "measuredCells": sum(r["summary"]["measured"] for r in reports),
                      "standingConstraintsPerPoint": 20, "out": str(output)}))


if __name__ == "__main__": main()
