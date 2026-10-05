#!/usr/bin/env python3.12
"""W46 G0 (d): the level check's rendered test — the shipped rung reproduces the published generation
(charter G0 (d): "tested so that the shipped rung (0.9 active, 0.89 receded) reproduces the published
generation on every ladder cell as pixel identity and measurement identity ... and reads no change").

The shipped rung is the snapshot candidate with no override (`level/candidates/control`, built by W46's
`fit/build-candidate.ts`: every endpoint patch- and digest-identical to its snapshot). It renders, in
candidate mode on the WebGPU tier at both scales with `--alpha`, every cell of ladder (i)
(`ladders/cells.json`: L1's declared population, `photo__rrect-ml__inactive`, the non-withheld solid
probes and the impulse probes, both poses), through `../with-gpu.sh` (the GPU lock, the classifying
census and the browser pin). No referee or holdout row renders: the cells are the ladder's, which the
planner adapter keeps disjoint from the manifest, and `level.py` refuses a withheld row. Then
`level.py identity` reads pixel and measurement identity and the level check on every row.

This render is the INSTRUMENT's control, not a ladder rung: it moves nothing, and part 1 pins its
result as the level check's test (the brief's item 5 before item 6). Ladder (i)'s own shipped rung is
rendered again under the ladders and must read the same.

    python3.12 -B identity.py build | render | read
"""
from __future__ import annotations

import datetime
import json
import os
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
EVIDENCE = HERE.parent
sys.path.insert(0, str(EVIDENCE))
import bindings as W  # noqa: E402

LABEL = "control"
CANDIDATES = HERE / "candidates"
OUT = HERE / "identity"
SCRATCH = W.LEVEL_SCRATCH / LABEL
SETS = "calibration,validation,probe"


def now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def cells() -> list[str]:
    body = json.loads(W.LADDER_CELLS.read_text())
    lad = body["ladders"]["i"]
    return sorted(set(lad["rest"]) | set(lad["inactive"]))


def build() -> int:
    if (CANDIDATES / LABEL / "candidate.json").exists():
        print("built already")
        return 0
    spec = SCRATCH.parent / "specs" / f"{LABEL}.json"
    spec.parent.mkdir(parents=True, exist_ok=True)
    spec.write_text(json.dumps(dict(label=LABEL, note="the shipped rung: the snapshots, no override (X61's "
                                    "identity test)", overrides={}), indent=2) + "\n")
    got = subprocess.run(["pnpm", "exec", "tsx", str(W.BUILDER), str(spec)], cwd=W.CAL, capture_output=True, text=True,
                         env=dict(os.environ, W46_CANDIDATE_ROOT=str(CANDIDATES)))
    print(got.stdout[-1500:], got.stderr[-1500:])
    return got.returncode


def render() -> int:
    candidate = CANDIDATES / LABEL / "candidate.json"
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "logs").mkdir(exist_ok=True)
    for scale, profile in sorted(W.PROFILE.items()):
        out = SCRATCH / f"{scale}x"
        if (out / "matrix.json").exists():
            continue
        out.mkdir(parents=True, exist_ok=True)
        argv = ["pnpm", "run", "-s", "compare", "--", "--profile", profile, "--renderer", "webgpu",
                "--candidate-document", str(candidate.relative_to(W.CAL)), "--set", SETS,
                "--scene", ",".join(cells()), "--alpha", "--write-partial", "--out-matrix", str(out / "matrix.json")]
        env = {k: v for k, v in os.environ.items() if not k.startswith("VITREA_")}
        env["VITREA_WEB_CAPTURES"] = str(out / "web-captures")
        label = f"level-identity {LABEL}/{scale}x"
        with (OUT / "runs.jsonl").open("a") as f:
            f.write(json.dumps(dict(label=label, started=now(), scenes=len(cells())), sort_keys=True) + "\n")
        with (OUT / "logs" / f"{LABEL}__{scale}x.txt").open("x") as log:
            code = subprocess.run([str(W.WITH_GPU), label, *argv], cwd=W.CAL, env=env, stdout=log,
                                  stderr=subprocess.STDOUT).returncode
        with (OUT / "runs.jsonl").open("a") as f:
            f.write(json.dumps(dict(label=label, completed=now(), exitCode=code), sort_keys=True) + "\n")
        print(label, "exit", code, flush=True)
        if code != 0:
            return code
    return 0


def read() -> int:
    argv = [sys.executable, "-B", str(HERE / "level.py"), "identity", "--candidate", str(CANDIDATES / LABEL)]
    for scale in (1, 2):
        argv += ["--matrix", str(SCRATCH / f"{scale}x" / "matrix.json")]
    # One capture root per scale: the two trees hold disjoint profile directories, so a merged view
    # by hard links is the union (the fit driver's `merged-captures` form).
    merged = SCRATCH / "merged-captures"
    for scale in (1, 2):
        tree = SCRATCH / f"{scale}x" / "web-captures"
        for prof in tree.iterdir():
            for cell in prof.iterdir():
                (merged / prof.name / cell.name).mkdir(parents=True, exist_ok=True)
                for f in cell.iterdir():
                    link = merged / prof.name / cell.name / f.name
                    if not link.exists():
                        os.link(f, link)
    argv += ["--captures", str(merged), "--out", str(OUT / "identity.json")]
    got = subprocess.run(argv, cwd=HERE, capture_output=True, text=True)
    (OUT / "identity.txt").write_text(got.stdout + got.stderr)
    print(got.stdout[-4000:], got.stderr[-2000:])
    return got.returncode


if __name__ == "__main__":
    verb = sys.argv[1] if len(sys.argv) > 1 else ""
    sys.exit({"build": build, "render": render, "read": read}.get(verb, lambda: print(__doc__) or 64)())
