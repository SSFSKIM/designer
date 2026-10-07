"""Create references.json once from immutable evidence; --check recomputes without writing.

All twenty constraints are scene identities, not an iteration over authorisations. The fifteen
historical targets retain their reference even when repaired; DL1 only requires ten to repair in
this wave. The other five remain listed and have the stricter current-growth-zero protection.
The five prior W49a repairs remain historically binding. Gate tools never render withheld cells.
"""
import argparse
import importlib.util
import json
from pathlib import Path
import subprocess

HERE = Path(__file__).resolve().parent
s = importlib.util.spec_from_file_location("w49b_common", HERE / "common.py")
C = importlib.util.module_from_spec(s); s.loader.exec_module(C)
CAL = C.CAL
G = CAL / "results/2026-10-08-w49b-grounding"
A = CAL / "results/2026-10-07-w49a-g0-declaration/documents"
CUT = CAL / "results/2026-10-07-w49a-g1-landing/cuts/cut-025-dark-w49a-landing.json"
CURRENT = "b2d074d2df24-940384c06f73"
# These declarations outlive the current exception list. Historical inputs only supply values.
BINDING = [(scale, f"{bg}__rrect-lg__rest") for scale in (1, 2)
           for bg in ("checkerboard-32", "checkerboard-64", "hc-text-28")] + [
    (1, "impulse__rrect-ml__inactive"), (2, "impulse__rrect-ml__inactive"),
    (2, "impulse__rrect-lg__inactive"), (2, "checkerboard-32__rrect-lg__inactive")]
PROTECTED = [(1, "checkerboard-lc16__rrect-md__rest"), (2, "checkerboard-lc16__rrect-md__rest"),
             (1, "impulse__capsule-button__rest"), (2, "checkerboard__capsule-button__inactive"),
             (2, "checkerboard__capsule-button__inactive-tint-orange")]
PRIOR = [(scale, f"{bg}__rrect-lg__inactive") for scale in (1, 2)
         for bg in ("checkerboard-64", "photo")] + [(1, "checkerboard-32__rrect-lg__inactive")]


def pin(path):
    return {"path": str(path.relative_to(CAL)), "sha256": C.sha256(path)}


def registry():
    cut = json.loads(CUT.read_text())
    attributed = json.loads((G / "attribution.json").read_text())
    if attributed["sourceCutSha256"] != C.sha256(CUT): raise ValueError("Attribution cut moved")
    current = {(c["scale"], c["scene"]): c for c in cut["T1"]["cells"]
               if c["scheme"] == "dark" and c["tier"] == "webgpu"}
    if len(current) != 154: raise ValueError("Dark current T1 membership is not 154")
    roles = {k: role for role, keys in (("binding", BINDING), ("protected", PROTECTED),
                                       ("prior-repair", PRIOR)) for k in keys}
    if len(roles) != 20 or not set(roles).issubset(current): raise ValueError("Standing membership changed")
    auth = {(a["scale"], a["scene"]): a for a in attributed["authorised"]}
    if set(auth) != set(BINDING + PROTECTED): raise ValueError("Grounding does not carry the fifteen targets")
    common_git = subprocess.check_output(["git", "rev-parse", "--path-format=absolute", "--git-common-dir"],
                                        cwd=CAL, text=True).strip()
    main = Path(common_git).parent
    canonical = main / "packages/calibration/web-captures"
    generations = {}
    pairs = {CURRENT: (G / "documents/b2d074d2df24.json", G / "documents/940384c06f73.json"),
             "d0219cd684bf": (A / "d0219cd684bf.json", A / "f0b36a71772a.json"),
             "b2d074d2df24": (A / "b2d074d2df24.json", A / "29da6a888a23.json")}
    for name, (active, receded) in pairs.items():
        matrix = CAL / "results/generations" / f"{name}.json"
        docs = {"active.dark": pin(active), "receded.dark": pin(receded)}
        generations[name] = {"matrix": pin(matrix), "documents": docs,
            "documentPair": {slot: entry["sha256"] for slot, entry in docs.items()},
            "captureTree": str(canonical if name == CURRENT else
                               canonical.parent / "web-captures-superseded" / name)}
    cells = []
    for key, c in sorted(current.items()):
        low = c["bands"]["low"] if c["stratum"] == "T" else c
        fine = c["bands"]["fine"] if c["stratum"] == "T" else c
        historical = None
        if key in roles:
            generation = auth[key]["referenceGeneration"] if key in auth else "d0219cd684bf"
            value = (low["reference"] if c["stratum"] == "T" else
                     auth[key]["reference"] if key in auth else c["reference"])
            historical = {"generation": generation, "value": value, "maxGrowthInB": 1,
                          "enforced": roles[key] != "protected", "captureTree": generations[generation]["captureTree"],
                          "documentPair": generations[generation]["documentPair"]}
        cells.append({"profile": c["profile"], "renderer": "webgpu", "scene": c["scene"],
            "scale": c["scale"], "pose": c["pose"], "set": c["set"], "partition": c["partition"],
            "stratum": c["stratum"], "role": roles.get(key),
            "statistic": "T1-low" if c["stratum"] == "T" else "T1-full-silhouette",
            "native": low["native"], "current": low["candidate"], "B": c["B"],
            "currentMaxGrowthInB": 0 if roles.get(key) == "protected" else 1,
            "currentGeneration": CURRENT, "currentDocumentPair": generations[CURRENT]["documentPair"],
            "currentCaptureTree": generations[CURRENT]["captureTree"],
            "historical": historical,
            "fidelity": {"statistic": "T1-fine" if c["stratum"] == "T" else "T1-full-silhouette",
                         "native": fine["native"], "current": fine["candidate"],
                         "reference": fine["reference"]},
            "nativeFixture": str(main / "apps/reference-apple/fixtures" / c["profile"] / f'{c["scene"]}.png')})
    index = json.loads((G / "documents/index.json").read_text())
    endpoints = {slot: {"path": str((G / "documents" / f'{entry["sha256"][:12]}.json').relative_to(CAL)),
                       "sha256": entry["sha256"], "source": entry["source"]} for slot, entry in index.items()}
    for endpoint in endpoints.values(): C.read_pinned(endpoint)
    inputs = {"cut": pin(CUT), "attribution": pin(G / "attribution.json"),
              "snapshotIndex": pin(G / "documents/index.json"),
              "scenes": {"path": str(C.ROOT / "apps/reference-apple/scenes.json"),
                         "sha256": C.sha256(C.ROOT / "apps/reference-apple/scenes.json")},
              "manifest": {"path": str(main / "apps/reference-apple/fixtures/manifest.json"),
                           "sha256": C.sha256(main / "apps/reference-apple/fixtures/manifest.json")}}
    if inputs["scenes"]["sha256"] != cut["scenesSha256"]: raise ValueError("Scene declaration moved")
    return {"schemaVersion": 1, "currentGeneration": CURRENT, "inputs": inputs,
            "endpoints": endpoints, "generations": generations,
            "contract": {"binding": 10, "protected": 5, "priorRepairs": 5,
                         "generalCurrentGrowthMaxInB": 1, "protectedCurrentGrowthMaxInB": 0,
                         "historicalGrowthMaxInB": 1, "withheld": "UNMEASURED",
                         "selection": "No selection or complete landing verdict at G0"},
            "cells": cells,
            "standingConstraints": [{"profile": c["profile"], "renderer": c["renderer"],
                "scene": c["scene"], "statistic": c["statistic"], "role": c["role"],
                "currentMaxGrowthInB": c["currentMaxGrowthInB"], "historical": c["historical"]}
                for c in cells if c["role"]]}


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__); p.add_argument("--check", action="store_true")
    args = p.parse_args(); result = registry(); out = C.DECLARATION / "references.json"
    if args.check:
        if json.loads(out.read_text()) != result: raise ValueError("Registry differs from recomputation")
    else: C.write_new_json(out, result)
    C.load_registry(out)
    print(f"{'Checked' if args.check else 'Created'} {len(result['cells'])} T1 cells; 20 standing constraints (10/5/5)")
