#!/usr/bin/env python3.12
"""W44 G0 (f): the ladders, built, rendered and read under the hashed protocol (charter clause 3).

    python3.12 -B ladder.py plan             # every rung's label, base and overrides (no write)
    python3.12 -B ladder.py build            # build every rung's candidate (build-candidate.ts)
    python3.12 -B ladder.py render [LABEL..] # render the rungs, 2x then 1x, one compare per profile
    python3.12 -B ladder.py read             # results.json and results.txt from the renders

Everything here follows `protocol.json`, which part 1 pins (`declaration.sha256`, `fdecebbf…`).
`render` refuses unless part 1 is hashed and `declare.py check` passes, and refuses a scene list
holding a referee or a holdout scene. Each launch is preceded by the classifying web census
(W43 G3 (ii)'s `stage/census.py`, the coordinator's ruling recorded in §5.201 §21): it refuses on
Reduce Transparency, Increase Contrast or a real capture process and only annotates the user's
own Chrome and a browserless Playwright relay. Every launch is logged in `runs.jsonl` (census,
start, completion) with its compare log under `logs/`; the matrices and PNGs stay in scratch at
`~/vitrea-w44/g0-ladders/<label>/`. `compare` runs through the calibration package's own script,
so the Playwright and Chromium it launches are the ones the package pins.
"""
from __future__ import annotations

import datetime
import hashlib
import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
EVIDENCE = HERE.parent
CAL = EVIDENCE.parents[1]
ROOT = CAL.parent.parent
SCRATCH = Path.home() / "vitrea-w44" / "g0-ladders"
PROTOCOL = json.loads((HERE / "protocol.json").read_text())
sys.path.insert(0, str(EVIDENCE / "referees"))
import plan  # noqa: E402

_spec = importlib.util.spec_from_file_location(
    "w43_census", CAL / "results/2026-10-02-w43-g3-refit/stage/census.py")
census = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(census)


def now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def log(row):
    with (HERE / "runs.jsonl").open("a") as f:
        f.write(json.dumps(row, sort_keys=True) + "\n")


def fmt(v) -> str:
    return "-".join(f"{x:g}" for x in v) if isinstance(v, list) else f"{v:g}"


def rungs() -> list[dict]:
    """Every rung the protocol declares, bases first: label, ladder, base, overrides, values."""
    out = []
    for name, base in PROTOCOL["bases"].items():
        out.append(dict(label=base["label"], ladder="base", base=name, overrides=base["overrides"], value=None))
    for lad in PROTOCOL["ladders"]:
        for base, values in lad["readAt"].items():
            for v in values:
                over = json.loads(json.dumps(PROTOCOL["bases"][base]["overrides"]))
                slot = over.setdefault(lad["slot"], {})
                pairs = list(zip(lad["leaves"], v)) if isinstance(v, list) else [(leaf, v) for leaf in lad["leaves"]]
                for leaf, x in pairs:
                    slot[leaf] = x
                for leaf, x in lad.get("fixed", {}).items():
                    slot[leaf] = x
                label = f"{lad['id'].lower()}-{base}-{fmt(v)}"
                if base == "c05" and lad["id"] == "L1" and v == 1.0:
                    label = PROTOCOL["bases"]["floor1"]["label"]
                out.append(dict(label=label, ladder=lad["id"], base=base, overrides=over, value=v))
    seen = {}
    for r in out:
        if r["label"] in seen and seen[r["label"]]["overrides"] != r["overrides"]:
            raise SystemExit(f"two rungs share the label {r['label']}")
        seen[r["label"]] = r
    return out


def unique_rungs() -> list[dict]:
    seen, out = set(), []
    for r in rungs():
        if r["label"] not in seen:
            seen.add(r["label"])
            out.append(r)
    return out


def build() -> int:
    for r in unique_rungs():
        folder = HERE / "candidates" / r["label"]
        if folder.exists():
            print("built already", r["label"])
            continue
        spec = dict(label=r["label"], note=f"{r['ladder']} rung {r['value']} at base {r['base']}",
                    overrides=r["overrides"])
        path = SCRATCH / "specs" / f"{r['label']}.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(spec, indent=2) + "\n")
        got = subprocess.run(["npx", "tsx", str(HERE / "build-candidate.ts"), str(path)], cwd=CAL,
                             capture_output=True, text=True)
        print(r["label"], "exit", got.returncode, got.stderr[-300:] if got.returncode else "")
        if got.returncode:
            return got.returncode
    return 0


def preflight():
    if not (EVIDENCE / "declaration.sha256").exists():
        raise SystemExit("render REFUSES: part 1 is not hashed (X50)")
    got = subprocess.run([sys.executable, "-B", str(EVIDENCE / "declare.py"), "check"], capture_output=True, text=True)
    if got.returncode:
        raise SystemExit("render REFUSES: declare.py check fails:\n" + got.stdout[-2000:])
    scenes = plan.load_scenes()
    held = {s for _, s in plan.referee_cells(plan.load_manifest())}
    for sid in PROTOCOL["fixedCells"]["scenes"]:
        if sid in held or scenes["role"][sid] == "holdout":
            raise SystemExit(f"render REFUSES: {sid} is a referee or holdout scene")


def render(labels: list[str]) -> int:
    preflight()
    todo = [r for r in unique_rungs() if not labels or r["label"] in labels]
    done = [json.loads(l) for l in (HERE / "runs.jsonl").read_text().splitlines()] \
        if (HERE / "runs.jsonl").exists() else []
    (HERE / "logs").mkdir(exist_ok=True)
    for r in todo:
        candidate = HERE / "candidates" / r["label"] / "candidate.json"
        if not candidate.exists():
            raise SystemExit(f"render: {r['label']} is not built")
        for profile in PROTOCOL["profiles"]:
            run_label = f"{r['label']}/{profile}"
            if any(x.get("label") == run_label and "completed" in x and x.get("exitCode") == 0 for x in done):
                continue
            attempt = 0
            logfile = HERE / "logs" / (run_label.replace("/", "__") + ".txt")
            while logfile.exists():
                attempt += 1
                logfile = HERE / "logs" / (run_label.replace("/", "__") + f".relaunch-{attempt}.txt")
            observation = census.observe()
            log(dict(label=run_label, at=observation["recordedAt"], census=dict(
                refusals=observation["refusals"], refuse=observation["refuse"],
                annotate=[a["why"] for a in observation["annotate"]], x6=observation["x6"])))
            if not observation["passes"]:
                print("CENSUS REFUSED", run_label, observation["refusals"], flush=True)
                return 3
            out = SCRATCH / r["label"]
            out.mkdir(parents=True, exist_ok=True)
            argv = ["pnpm", "run", "-s", "compare", "--", "--profile", profile, "--renderer", PROTOCOL["tier"],
                    "--candidate-document", str(candidate.relative_to(CAL)),
                    "--set", PROTOCOL["fixedCells"]["sets"], "--scene", ",".join(PROTOCOL["fixedCells"]["scenes"]),
                    "--write-partial", "--out-matrix", str(out / "matrix.json")]
            env = {k: v for k, v in os.environ.items() if not k.startswith("VITREA_")}
            env.update(VITREA_WEB_CAPTURES=str(out / "web-captures"))
            started = now()
            log(dict(label=run_label, started=started, argv=argv, attempt=attempt))
            with logfile.open("x") as f:
                result = subprocess.run(argv, cwd=CAL, env=env, stdout=f, stderr=subprocess.STDOUT)
            log(dict(label=run_label, started=started, completed=now(), exitCode=result.returncode))
            print(run_label, "exit", result.returncode, flush=True)
            if result.returncode not in (0, 1):
                return result.returncode
    return 0


def main() -> int:
    verb = sys.argv[1] if len(sys.argv) > 1 else ""
    if verb == "plan":
        for r in unique_rungs():
            print(f"{r['label']:<28} {r['ladder']:<5} {r['base']:<7} {json.dumps(r['overrides'])}")
        print(len(unique_rungs()), "candidates")
        return 0
    if verb == "build":
        return build()
    if verb == "render":
        return render(sys.argv[2:])
    if verb == "read":
        import read  # noqa: E402  (beside this file)
        return read.main()
    raise SystemExit(__doc__)


if __name__ == "__main__":
    raise SystemExit(main())
