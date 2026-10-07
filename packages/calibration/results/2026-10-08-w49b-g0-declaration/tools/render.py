"""Gate-only W49b launcher. Default is plan-only; --execute is the explicit render act.

Usage: python3.12 -I render.py batch.json --candidates /scratch/candidates --out /scratch/new-renders
       python3.12 -I render.py batch.json --candidates /scratch/candidates --out /scratch/new-renders --execute

Plans come from pinned W49a gate membership and the fixture manifest; requested/planned/measured
identity must agree. No holdout or referee is ever passed to compare. Every launch owns its lock,
passes the classifying census and browser pin, and preserves failure evidence without overwriting.
No other process is killed, no lock is waited on, and no publication path is present.
"""
import argparse
import importlib.util
import json
import os
from pathlib import Path
import subprocess

HERE = Path(__file__).resolve().parent
s = importlib.util.spec_from_file_location("w49b_common", HERE / "common.py")
C = importlib.util.module_from_spec(s); s.loader.exec_module(C)
CENSUS = C.CAL / "results/2026-10-02-w43-g3-refit/stage/census.py"
LOCK = Path("/tmp/w49-gpu.lock")


def plan_run(registry, point, scale):
    requested = C.gate_cells(registry, point, scale)
    manifest = C.read_pinned(registry["inputs"]["manifest"])
    spec = C.read_pinned(registry["inputs"]["scenes"])
    profile = f"apple-macos-27.0-{scale}x-dark-standard-glass0.25"
    entries = [p for p in manifest["profiles"] if p["profileKey"] == profile]
    if len(entries) != 1: raise ValueError("Profile has no unique fixture manifest entry")
    fixtures = {f["sceneId"]: f for f in entries[0]["fixtures"]}
    if len(fixtures) != len(entries[0]["fixtures"]): raise ValueError("Duplicate fixture scene")
    scenes = {s["id"]: s for s in spec["scenes"]}
    planned = []
    for cell in requested:
        scene = cell["scene"]; fixture = fixtures.get(scene)
        if fixture is None: raise ValueError(f"Requested cell would be skipped by planner: {scene}")
        declared_sets = [k for k, v in spec["split"].items() if isinstance(v, list) and scene in v]
        if declared_sets != [cell["set"]] or fixture["fixtureSet"] != cell["set"]:
            raise ValueError(f"Split disagreement for {scene}")
        if cell["set"] not in C.SETS or cell["partition"] != "gate":
            raise ValueError(f"Withheld cell cannot enter plan: {scene}")
        if not fixture["materialRendered"] or fixture.get("identicalToBackground", False):
            raise ValueError(f"Planner would refuse material-free cell {scene}")
        scene_entry = scenes[scene]
        # The owner cut's pose is the WINDOW pose: pressed still draws the active endpoint.
        window_pose = "inactive" if scene_entry["state"] == "inactive" else "rest"
        if window_pose != cell["pose"]: raise ValueError(f"Window pose disagreement for {scene}")
        if f'{scene_entry["background"]}@{scale}x' not in manifest["backgrounds"]:
            raise ValueError(f"Missing planned background {scene}")
        planned.append((profile, "webgpu", scene))
    wanted = [(c["profile"], c["renderer"], c["scene"]) for c in requested]
    if sorted(wanted) != sorted(planned): raise ValueError("Requested/planned membership differs")
    return {"label": point["label"], "scale": scale, "pose": point["pose"],
            "requested": [list(k) for k in wanted], "planned": [list(k) for k in planned],
            "scenes": [c["scene"] for c in requested], "profile": profile,
            "predictions": point.get("prediction"), "cells": len(requested)}


def verify_candidate(candidates, label, batch_path, references_path):
    built = json.loads((candidates / "build.json").read_text())
    if built["batchSha256"] != C.sha256(batch_path) or built["referencesSha256"] != C.sha256(references_path):
        raise ValueError("Candidate batch/references differ from built byte snapshots")
    if (candidates / "batch.json").read_bytes() != batch_path.read_bytes():
        raise ValueError("Built batch bytes differ")
    path = candidates / label / "candidate.json"
    records = [record for record in built["points"] if record["label"] == label]
    if len(records) != 1 or records[0]["candidateSha256"] != C.sha256(path):
        raise ValueError("Candidate differs from the builder's supplied-point byte witness")
    point_path = candidates / label / "point.json"
    if records[0]["pointSha256"] != C.sha256(point_path): raise ValueError("Built point bytes changed")
    expected = next(p for p in C.validate_batch(json.loads(batch_path.read_text()))["points"] if p["label"] == label)
    if json.loads(point_path.read_text()) != expected: raise ValueError("Built point is not the supplied point")
    subprocess.run(["pnpm", "exec", "tsx", str(HERE / "verify-candidate.ts"), str(path)],
                   cwd=C.CAL, check=True, capture_output=True, text=True)
    return path


def observation():
    s = importlib.util.spec_from_file_location("w43_census", CENSUS)
    census = importlib.util.module_from_spec(s); s.loader.exec_module(census)
    record = census.observe()
    script = ("const p=require.resolve('@playwright/test/package.json');const v=require(p).version;"
              "const core=require.resolve('playwright-core/package.json',{paths:[require('path').dirname(p)]});"
              "const b=require(require('path').join(require('path').dirname(core),'browsers.json'));"
              "const c=b.browsers.find(x=>x.name==='chromium');"
              "console.log(JSON.stringify({playwright:v,revision:c.revision,browserVersion:c.browserVersion}))")
    pin = json.loads(subprocess.check_output(["node", "-e", script], cwd=C.CAL, text=True))
    pinned = pin == {"playwright": "1.62.1", "revision": "1234", "browserVersion": C.ENGINE_VERSION}
    pinned = pinned and not os.environ.get("PLAYWRIGHT_BROWSERS_PATH")
    return {**record, "browserPin": pin, "passes": bool(record["passes"]) and pinned,
            "refusals": record["refusals"] + ([] if pinned else ["browserNotPinned"])}


def check_rows(plan, rows, candidate):
    C.assert_membership([tuple(k) for k in plan["planned"]], rows)
    spec = json.loads((C.ROOT / "apps/reference-apple/scenes.json").read_text())
    by_scene = {s["id"]: s for s in spec["scenes"]}
    stamp = f"materialProfile=candidate candidateDocument={candidate} declarationSha256={C.sha256(candidate)[:12]}"
    for row in rows:
        scene = row["key"]["sceneId"]
        if row["state"] != by_scene[scene]["state"]:
            raise ValueError("Measured pose differs from the plan")
        if row["fixtureSet"] not in C.SETS or scene not in spec["split"][row["fixtureSet"]]:
            raise ValueError("Measured split differs from the plan")
        capture = row["key"]["web"]["capturePath"]
        if stamp not in capture or "crossPosition=" in capture:
            raise ValueError("Measured row does not name the candidate bytes in candidate mode")
        if row["key"]["web"]["samplingBackend"] != "gpu-texture":
            raise ValueError("Requested GPU texture backend did not draw")


def scratch_destination(path):
    path = path.resolve()
    main = Path(subprocess.check_output(["git", "rev-parse", "--path-format=absolute", "--git-common-dir"],
                                       cwd=C.CAL, text=True).strip()).parent
    if path.is_relative_to(C.ROOT) or path.is_relative_to(main):
        raise ValueError("Scratch renders must live outside authoritative checkouts")
    if any(part in ("profiles", "generations", "web-captures-superseded") for part in path.parts):
        raise ValueError("Refuse an authoritative destination")
    return path


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("batch", type=Path); p.add_argument("--candidates", type=Path)
    p.add_argument("--out", type=Path); p.add_argument("--labels", nargs="+")
    p.add_argument("--execute", action="store_true")
    args = p.parse_args()
    references_path = C.DECLARATION / "references.json"
    registry = C.load_registry(references_path)
    batch_path = args.batch.resolve()
    batch = C.validate_batch(json.loads(batch_path.read_text()))
    labels = {point["label"] for point in batch["points"]}
    if args.labels and (not set(args.labels).issubset(labels) or len(args.labels) != len(set(args.labels))):
        raise ValueError("Requested label is absent or duplicated")
    points = [point for point in batch["points"] if not args.labels or point["label"] in args.labels]
    plans = [plan_run(registry, point, scale) for point in points for scale in point["scales"]]
    report = {"batchSha256": C.sha256(batch_path), "referencesSha256": C.sha256(references_path),
              "points": len(points), "runs": len(plans), "gateCells": sum(plan["cells"] for plan in plans),
              "plans": plans}
    if not args.execute:
        print(json.dumps(report, indent=2)); return
    if not args.candidates or not args.out: raise ValueError("Execution requires --candidates and --out")
    declaration = C.DECLARATION / "declare.py"
    if not declaration.is_file(): raise ValueError("Declaration checker missing; no render authorised")
    subprocess.run(["python3", "-I", str(declaration), "check"], cwd=C.DECLARATION, check=True)
    candidates = args.candidates.resolve()
    candidate_paths = {point["label"]: verify_candidate(candidates, point["label"], batch_path, references_path)
                       for point in points}
    output = scratch_destination(args.out)
    output.mkdir(parents=True, exist_ok=False)
    C.write_new_json(output / "plan.json", report)
    for plan in plans:
        candidate = candidate_paths[plan["label"]]
        out = output / plan["label"] / f'{plan["scale"]}x'
        out.mkdir(parents=True, exist_ok=False)
        argv = ["pnpm", "run", "-s", "compare", "--", "--profile", plan["profile"], "--renderer", "webgpu",
                "--candidate-document", str(candidate), "--set", ",".join(C.SETS),
                "--scene", ",".join(plan["scenes"]), "--alpha", "--write-partial", "--out-matrix", str(out / "matrix.json")]
        C.write_new_json(out / "request.json", {**plan, "argv": argv, "batchSha256": report["batchSha256"],
            "referencesSha256": report["referencesSha256"], "candidate": str(candidate),
            "candidateSha256": C.sha256(candidate)})
        with C.owned_lock(LOCK) as owner:
            C.write_new_json(out / "lock.json", owner)
            observed = observation()
            C.write_new_json(out / "census.json", observed)
            if not observed["passes"]: raise ValueError(f'Census refuses {plan["label"]}: {observed["refusals"]}')
            env = {k: v for k, v in os.environ.items() if not k.startswith("VITREA_")}
            env["VITREA_WEB_CAPTURES"] = str(out / "web-captures")
            with (out / "render.txt").open("x") as log:
                code = subprocess.run(argv, cwd=C.CAL, env=env, stdout=log, stderr=subprocess.STDOUT).returncode
            C.write_new_json(out / "exit.json", {"returncode": code})
            if code: raise ValueError(f"Render failed ({code}); partial evidence retained at {out}")
            rows = json.loads((out / "matrix.json").read_text())["cells"]
            check_rows(plan, rows, candidate)
            capture_evidence = {}
            for row in rows:
                scene = row["key"]["sceneId"]
                folder = out / "web-captures" / plan["profile"] / scene
                meta = folder / "cell__webgpu.json"
                if json.loads(meta.read_text()) != row["key"]["web"]:
                    raise ValueError("Capture metadata differs from measured row")
                for path in (meta, folder / f"{scene}__webgpu.png"):
                    capture_evidence[str(path.relative_to(out))] = C.sha256(path)
            C.write_new_json(out / "complete.json", {"matrixSha256": C.sha256(out / "matrix.json"),
                "requested": plan["requested"], "planned": plan["planned"], "captureEvidence": capture_evidence,
                "measured": [[r["key"]["profileKey"], r["key"]["web"]["renderer"], r["key"]["sceneId"]] for r in rows]})
        print(f'{plan["label"]} {plan["scale"]}x: {len(rows)} exact gate cells', flush=True)


if __name__ == "__main__": main()
