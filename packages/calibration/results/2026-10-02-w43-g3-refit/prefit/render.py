#!/usr/bin/env python3.12
"""W43 G3 (i), step 1: the pre-fit render, the 0.5 documents drawn on the 0.25 cells.

Charter clause 10 and G3 step 1; Decision Log 5 (b) as RULED 2026-10-02: the pre-fit render is
L1's growth baseline and M2's and E2's reference. It is the shipped 0.5 material read against the
0.25 fixtures, a comparison between two positions, so it runs under `--cross-position` and every
row and capture is stamped `crossPosition=shipped-glass0.5-against-glass0.25`, scratch only
(W43 G0 (f); X45).

Why strict shipped mode and not candidate mode. Candidate mode refuses a candidate whose name or
endpoint keys are a shipped document's (`src/material-selection.ts`, "names a shipped document":
"A shipped material is read in strict mode, where the runtime's own document draws"), so the 0.5
documents themselves can be drawn only in strict mode. Relabelling their content under scratch
`-glass0.25` keys (G0 (f)'s byte-identity proof candidate) would draw the same pixels but erase the
cross-position stamp, which is the label X45 requires on exactly this comparison. The recipe flags
are the canonical 0.5 generation's own (`--material-profile` + `--receded-profile`), so every row
names both shipped documents at their live hashes, as the 0.5 rows do; G0 (f) proved the recipe
and the runtime pose byte-identical (64/64).

    python3.12 -B render.py run [--tier webgpu|css] [--scheme light|dark]
                                [--relaunch-after-stop REASON]

One compare process per (profile, tier), a fresh X6 observation (W41's observer) before each
launch, every launch logged to runs.jsonl beside this file with its log under logs/. A started
pass with no completion record is a stop, never a silent relaunch: `--relaunch-after-stop REASON`
records the stop with its reason and relaunches the pass under a new label (`.../relaunch-N`).
Each compare process writes the scratch matrix once, at its end, so a stopped pass leaves no row. Output is outside the
repository: matrix and captures under SCRATCH (raw renders stay on the machine).
"""
import datetime
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys

HERE = Path(__file__).resolve().parent
CAL = HERE.parents[2]
SCRATCH = Path.home() / "vitrea-w43" / "g3-scratch" / "prefit"
MATRIX = SCRATCH / "matrix.json"
CAPTURES = SCRATCH / "web-captures"
SETS = "calibration,validation,recorded,probe"  # holdout is never read in this child
PROFILES = {
    "light": ["apple-macos-27.0-1x-light-standard-glass0.25",
              "apple-macos-27.0-2x-light-standard-glass0.25"],
    "dark": ["apple-macos-27.0-1x-dark-standard-glass0.25",
             "apple-macos-27.0-2x-dark-standard-glass0.25"],
}
DOCUMENTS = {
    scheme: (f"profiles/apple-macos-27.0-1x-{scheme}-standard-glass0.5.json",
             f"profiles/apple-macos-27.0-1x-{scheme}-standard-glass0.5-receded.json")
    for scheme in PROFILES
}

spec = importlib.util.spec_from_file_location(
    "w41_x6", CAL / "results/2026-09-27-w41-g1-identification/x6/observe.py")
x6 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(x6)


def now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def log(row):
    with (HERE / "runs.jsonl").open("a") as f:
        f.write(json.dumps(row, sort_keys=True) + "\n")


def launch(argv, label):
    observation = x6.observe()
    verdict = observation["verdict"]
    log(dict(label=label, at=observation["recordedAt"], x6=verdict,
             foreign=[p[2][:160] for p in observation["foreignProcesses"]]))
    if not verdict["passes"]:
        print("X6 REFUSED", label, verdict["refusals"], flush=True)
        sys.exit(3)
    env = {k: v for k, v in os.environ.items() if not k.startswith("VITREA_")}
    env.update(VITREA_WEB_CAPTURES=str(CAPTURES))
    started = now()
    with (HERE / "logs" / (label.replace("/", "__") + ".txt")).open("x") as out:
        result = subprocess.run(argv, cwd=CAL, env=env, stdout=out, stderr=subprocess.STDOUT)
    log(dict(label=label, started=started, completed=now(), exitCode=result.returncode,
             argv=argv))
    print(label, "exit", result.returncode, flush=True)
    return result.returncode


def main():
    if len(sys.argv) < 2 or sys.argv[1] != "run":
        raise SystemExit(__doc__)
    args = sys.argv[2:]
    stop_reason = args[args.index("--relaunch-after-stop") + 1] if "--relaunch-after-stop" in args else None
    tiers = [args[args.index("--tier") + 1]] if "--tier" in args else ["webgpu", "css"]
    schemes = [args[args.index("--scheme") + 1]] if "--scheme" in args else ["light", "dark"]
    SCRATCH.mkdir(parents=True, exist_ok=True)
    (HERE / "logs").mkdir(exist_ok=True)
    for tier in tiers:
        for scheme in schemes:
            active, receded = DOCUMENTS[scheme]
            for profile in PROFILES[scheme]:
                label = f"prefit/{tier}/{profile}"
                marker = HERE / "logs" / (label.replace("/", "__") + ".started")
                done = [json.loads(l) for l in (HERE / "runs.jsonl").read_text().splitlines()] \
                    if (HERE / "runs.jsonl").exists() else []
                attempt = 0
                while marker.exists():
                    if any(r.get("label") == label and "exitCode" in r for r in done):
                        break
                    if stop_reason is None:
                        raise SystemExit("started pass without completion is a stop: " + label)
                    # A stopped pass is recorded as stopped, and the relaunch is a NEW logged
                    # label; nothing is ever relaunched under the label that was stopped.
                    if not any(r.get("label") == label and r.get("stopped") for r in done):
                        log(dict(label=label, stopped=stop_reason, at=now()))
                    attempt += 1
                    label = f"prefit/{tier}/{profile}/relaunch-{attempt}"
                    marker = HERE / "logs" / (label.replace("/", "__") + ".started")
                if any(r.get("label") == label and "exitCode" in r for r in done):
                    continue
                argv = ["pnpm", "run", "-s", "compare", "--", "--profile", profile,
                        "--renderer", tier, "--material-profile", active,
                        "--receded-profile", receded, "--cross-position", "--set", SETS,
                        "--alpha", "--write-partial", "--out-matrix", str(MATRIX)]
                marker.write_text(now() + "\n")
                code = launch(argv, label)
                if code not in (0, 1):
                    raise SystemExit(f"{label}: exit {code}; stop")


if __name__ == "__main__":
    main()
