#!/usr/bin/env python3.12
"""W43 G3 (ii): the two 0.25 publication stages, read by the CLAUDE.md recipe (charter clause 10).

  read.py declare <scheme>              matrix stage: the scheme's two -glass0.25 standard profiles,
                                        both tiers, calibration,validation,holdout,recorded,probe,
                                        the sealed active/receded document pair. No capture.
  read.py measure <scheme> <tier>       calibration,validation,recorded,probe, one compare process
                                        per profile, `--write-partial`, a fresh census before each.
  read.py holdout <scheme> <tier>       holdout, once per tier, only after the cross-gate holdout
                                        ledger's last record names this exact configuration
                                        (`configuration.py record --documents glass0.25`).

Strict shipped mode at the (macOS 27.0, glass 0.25) pair: `--material-profile` and
`--receded-profile` name the sealed documents under `profiles/`, the runtime selects
`macos27Glass025MaterialProfileDocument` by its pair, and no `--cross-position` appears anywhere.
Stages live at ~/vitrea-w43/g3-stage-<scheme>/ with `membership.json` beside `matrix.json`; the
captures land in this worktree's `packages/calibration/web-captures` (gitignored), the tree that is
copied to the canonical path when the read lands.

Every launch is logged (runs.jsonl beside this file, logs under logs/). A pass writes an
exclusive start marker and is never re-launched silently: a started pass with no completion is a
stop, relaunched only under `--relaunch-after-stop REASON` as a new labelled pass. The machine read
before each launch is `census.py`'s (the coordinator's census ruling for web passes).
"""
import datetime
import json
import os
from pathlib import Path
import subprocess
import sys

HERE = Path(__file__).resolve().parent
CAL = HERE.parents[2]
sys.path.insert(0, str(HERE))
import census  # noqa: E402

STAGES = {s: Path.home() / "vitrea-w43" / f"g3-stage-{s}" for s in ("light", "dark")}
PROFILES = {s: [f"apple-macos-27.0-1x-{s}-standard-glass0.25", f"apple-macos-27.0-2x-{s}-standard-glass0.25"]
            for s in ("light", "dark")}
DOCS = {s: (f"profiles/apple-macos-27.0-1x-{s}-standard-glass0.25.json",
            f"profiles/apple-macos-27.0-1x-{s}-standard-glass0.25-receded.json") for s in ("light", "dark")}
MEASURED = "calibration,validation,recorded,probe"
CONFIG = CAL / "results/holdout-configuration/configuration.py"


def now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def log(row):
    with (HERE / "runs.jsonl").open("a") as f:
        f.write(json.dumps(row, sort_keys=True) + "\n")


def done(label):
    rows = [json.loads(l) for l in (HERE / "runs.jsonl").read_text().splitlines()] \
        if (HERE / "runs.jsonl").exists() else []
    return any(r.get("label") == label and "exitCode" in r for r in rows), rows


def launch(argv, label):
    machine = census.observe()
    log(dict(label=label, machine=machine))
    if not machine["passes"]:
        print("CENSUS REFUSED", label, machine["refusals"], machine["refuse"], flush=True)
        sys.exit(3)
    if machine["annotate"]:
        print("annotated", label, [(p["pid"], p["why"]) for p in machine["annotate"]], flush=True)
    env = {k: v for k, v in os.environ.items() if not k.startswith("VITREA_")}
    started = now()
    with (HERE / "logs" / (label.replace("/", "__") + ".txt")).open("x") as out:
        result = subprocess.run(argv, cwd=CAL, env=env, stdout=out, stderr=subprocess.STDOUT)
    log(dict(label=label, started=started, completed=now(), exitCode=result.returncode, argv=argv))
    print(label, "exit", result.returncode, flush=True)
    return result.returncode


def main():
    args = sys.argv[1:]
    if len(args) < 2:
        raise SystemExit(__doc__)
    mode, scheme = args[0], args[1]
    stage = STAGES[scheme]
    active, receded = DOCS[scheme]
    (HERE / "logs").mkdir(exist_ok=True)
    if mode == "declare":
        argv = ["pnpm", "run", "-s", "matrix", "--", "stage", str(stage), "--profile",
                ",".join(PROFILES[scheme]), "--renderer", "webgpu,css",
                "--set", "calibration,validation,holdout,recorded,probe",
                "--material-profile", active, "--receded-profile", receded]
        result = subprocess.run(argv, cwd=CAL, capture_output=True, text=True)
        log(dict(label=f"declare/{scheme}", at=now(), argv=argv, exitCode=result.returncode,
                 output=(result.stdout + result.stderr)[-2000:]))
        print(result.stdout, result.stderr)
        sys.exit(result.returncode)
    tier = args[2]
    stop_reason = args[args.index("--relaunch-after-stop") + 1] if "--relaunch-after-stop" in args else None
    if mode == "holdout":
        import importlib.util
        spec = importlib.util.spec_from_file_location("hc", CONFIG)
        hc = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(hc)
        last = hc.load_log()[-1]
        assert last.get("documentSet") == "glass0.25", last
        assert last["documents"] == hc.document_hashes("glass0.25"), "the ledger's last read is not these documents"
        assert last["sourceSha256"] == hc.source_hash()[0], "the sources moved since the ledger's record"
        committed = subprocess.check_output(
            ["git", "show", "HEAD:packages/calibration/results/holdout-configuration/configuration-log.json"],
            cwd=CAL, text=True)
        assert json.loads(committed)["reads"][-1] == last, "the ledger's record is not committed"
        sets = "holdout"
    elif mode == "measure":
        sets = MEASURED
    else:
        raise SystemExit(__doc__)
    for profile in PROFILES[scheme]:
        label = f"{mode}/{tier}/{profile}"
        marker = HERE / "logs" / (label.replace("/", "__") + ".started")
        attempt = 0
        complete, rows = done(label)
        while marker.exists() and not complete:
            if stop_reason is None:
                raise SystemExit("started pass without completion is a stop: " + label)
            if not any(r.get("label") == label and r.get("stopped") for r in rows):
                log(dict(label=label, stopped=stop_reason, at=now()))
            attempt += 1
            label = f"{mode}/{tier}/{profile}/relaunch-{attempt}"
            marker = HERE / "logs" / (label.replace("/", "__") + ".started")
            complete, rows = done(label)
        if complete:
            continue
        argv = ["pnpm", "run", "-s", "compare", "--", "--stage", str(stage), "--profile", profile,
                "--renderer", tier, "--material-profile", active, "--receded-profile", receded,
                "--set", sets, "--alpha", "--write-partial"]
        marker.write_text(now() + "\n")
        code = launch(argv, label)
        if code not in (0, 1):
            raise SystemExit(f"{label}: exit {code}; stop")


if __name__ == "__main__":
    main()
