#!/usr/bin/env python3.12
"""W43 G3 (i), step 3: the refit's measuring loop, in scratch (charter clause 10; Decision Log 7).

W29 G3's loop (``results/2026-09-19-w29-g3-refit/fit.py``) carried to candidate mode: build a
candidate (``build-candidate.ts``), render it, read the residual the law is stated in, move the
candidate by that residual, render again. Every candidate's documents are committed under
``candidates/<label>/``; every render is logged in ``runs.jsonl`` with its compare log under
``logs/``; the matrices and PNGs stay on the machine under SCRATCH/<label>/. Before every launch
W41's X6 observer is read and logged; a web pass refuses on WEB_REFUSALS (below).

    python3.12 -B fit.py build <spec.json>
    python3.12 -B fit.py render <label> [--profile P,...] [--renderer webgpu|css]
                                [--set calibration] [--scene a,b] [--tag T]
    python3.12 -B fit.py table <label> [--renderer webgpu] [--sets calibration]

The holdout is refused by construction: ``render`` refuses a ``--set`` or ``--scene`` naming a
declared holdout id (ids read from scenes.json's split, never named here), and ``table`` reads
through ``cuts/bed.py``, which refuses a holdout row. Every render names one complete candidate
declaration; nothing is injected beside it, and nothing renders into a stage (``compare`` refuses
a candidate there) or into the canonical capture tree.
"""
from __future__ import annotations

import datetime
import importlib.util
import json
import os
import statistics as st
import subprocess
import sys
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
EVIDENCE = HERE.parent
CAL = EVIDENCE.parents[1]
SCRATCH = Path.home() / "vitrea-w43" / "g3-scratch" / "fit"
sys.path.insert(0, str(EVIDENCE / "cuts"))
import bed as B  # noqa: E402

spec = importlib.util.spec_from_file_location(
    "w41_x6", CAL / "results/2026-09-27-w41-g1-identification/x6/observe.py")
x6 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(x6)


def now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def log(row):
    with (HERE / "runs.jsonl").open("a") as f:
        f.write(json.dumps(row, sort_keys=True) + "\n")


def candidate_path(label: str) -> Path:
    return HERE / "candidates" / label / "candidate.json"


def build(spec_path: str) -> int:
    argv = ["npx", "tsx", str(HERE / "build-candidate.ts"), str(Path(spec_path).resolve())]
    result = subprocess.run(argv, cwd=CAL, capture_output=True, text=True)
    sys.stdout.write(result.stdout)
    sys.stderr.write(result.stderr)
    log(dict(label="build", spec=str(spec_path), at=now(), exitCode=result.returncode))
    return result.returncode


def render(label: str, args: list[str]) -> int:
    opt = lambda name, default=None: args[args.index(name) + 1] if name in args else default  # noqa: E731
    profiles = (opt("--profile") or ",".join(B.PROFILES)).split(",")
    renderer = opt("--renderer", "webgpu")
    sets = opt("--set", "calibration")
    scenes = opt("--scene")
    tag = opt("--tag", sets.replace(",", "+") + ("-" + scenes.replace(",", "+")[:40] if scenes else ""))
    if "holdout" in sets.split(","):
        raise SystemExit("fit: the holdout is never read in G3 (i)")
    if scenes and any(s in B.SCENES.holdout for s in scenes.split(",")):
        raise SystemExit("fit: a declared holdout scene was named")
    for p in profiles:
        if p not in B.PROFILES:
            raise SystemExit(f"fit: {p} is not a -glass0.25 standard profile")
    candidate = candidate_path(label)
    if not candidate.exists():
        raise SystemExit(f"fit: no candidate {candidate}")
    out = SCRATCH / label
    out.mkdir(parents=True, exist_ok=True)
    (HERE / "logs").mkdir(exist_ok=True)
    for profile in profiles:
        run_label = f"{label}/{renderer}/{profile}/{tag}"
        done = [json.loads(l) for l in (HERE / "runs.jsonl").read_text().splitlines()] \
            if (HERE / "runs.jsonl").exists() else []
        completed = lambda name: any(r.get("label") == name and "completed" in r for r in done)  # noqa: E731
        logfile = HERE / "logs" / (run_label.replace("/", "__") + ".txt")
        attempt = 0
        while logfile.exists() and not completed(run_label):
            # A pass with a log and no completion record was stopped (a HOLD, a crash): it is
            # recorded as stopped and relaunched under a NEW label, never re-run under its own.
            if not any(r.get("label") == run_label and r.get("stopped") for r in done):
                log(dict(label=run_label, stopped="no completion record; relaunched", at=now()))
            attempt += 1
            run_label = f"{label}/{renderer}/{profile}/{tag}/relaunch-{attempt}"
            logfile = HERE / "logs" / (run_label.replace("/", "__") + ".txt")
        if completed(run_label):
            print("already rendered", run_label)
            continue
        observation = x6.observe()
        verdict = observation["verdict"]
        refusals = [fact for fact in verdict["refusals"] if fact in WEB_REFUSALS]
        log(dict(label=run_label, at=observation["recordedAt"], x6=verdict, refusals=refusals,
                 foreign=[p[2][:160] for p in observation["foreignProcesses"]]))
        if refusals:
            print("X6 REFUSED", run_label, refusals, flush=True)
            return 3
        argv = ["pnpm", "run", "-s", "compare", "--", "--profile", profile, "--renderer", renderer,
                "--candidate-document", str(candidate.relative_to(CAL)), "--set", sets,
                "--alpha", "--write-partial", "--out-matrix", str(out / "matrix.json")]
        if scenes:
            argv += ["--scene", scenes]
        env = {k: v for k, v in os.environ.items() if not k.startswith("VITREA_")}
        env.update(VITREA_WEB_CAPTURES=str(out / "web-captures"))
        started = now()
        with logfile.open("x") as f:
            result = subprocess.run(argv, cwd=CAL, env=env, stdout=f, stderr=subprocess.STDOUT)
        log(dict(label=run_label, started=started, completed=now(), exitCode=result.returncode,
                 argv=argv))
        print(run_label, "exit", result.returncode, flush=True)
        if result.returncode not in (0, 1):
            return result.returncode
    return 0


# The facts a WEB read refuses on. W41's observer reads five; a web render depends on two of them
# (Reduce Transparency and Increase Contrast reach the page through the browser's preferences)
# and on a third, no foreign browser or harness sharing the machine (X7). The slider does not
# reach a web page, and HID idle protects a NATIVE capture from input; both are still observed
# and logged before every launch, and neither refuses a web pass (2026-10-02: a pass refused on
# idle while the user was at the Mac rendered nothing).
WEB_REFUSALS = ("reduceTransparency", "increaseContrast", "foreignProcessCountZero")

CLASS = {"capsule-button": "thin44", "rrect-sm": "thin32", "rrect-48": "s48", "rrect-64": "s64",
         "rrect-80": "s80", "rrect-md": "thick96", "rrect-md-clear20": "clear20",
         "rrect-ml": "thick128", "rrect-lg": "thick160", "toolbar-group": "group",
         "glass-over-glass": "stack"}


def load_bed(label: str, renderer: str, sets: set[str]):
    if label == "prefit":
        bed = B.load([str(Path.home() / "vitrea-w43/g3-scratch/prefit/matrix.json")], "prefit")
    else:
        bed = B.load([str(SCRATCH / label / "matrix.json")], "candidate",
                     str(candidate_path(label).relative_to(B.ROOT)))
    return [r for r in bed.rows if r["key"]["web"]["renderer"] == renderer and r["fixtureSet"] in sets]


def table(label: str, args: list[str]) -> int:
    opt = lambda name, default=None: args[args.index(name) + 1] if name in args else default  # noqa: E731
    renderer = opt("--renderer", "webgpu")
    sets = set(opt("--sets", "calibration").split(","))
    rows = load_bed(label, renderer, sets)
    groups = defaultdict(list)
    for r in rows:
        sid = r["key"]["sceneId"]
        bg, comp, pose = sid.split("__")
        tinted = "-tint-" in pose
        key = (B.scheme_of(r["key"]["profileKey"]), "inactive" if pose.startswith("inactive") else "rest",
               bg + (" tint" if tinted else ""), CLASS.get(comp, comp))
        v = lambda m: B.value(r, "material", m)  # noqa: E731
        n, w = v("interiorMeanNative"), v("interiorMeanWeb")
        sn, sw = v("interiorStdDevNative"), v("interiorStdDevWeb")
        groups[key].append(dict(scale=B.scale_of(r["key"]["profileKey"]),
                                level=None if None in (n, w) else w - n,
                                sd=None if None in (sn, sw) or not sn else sw / sn))
    print(f"# {label} {renderer} sets={sorted(sets)}: level = web - native interiorMean (linear); "
          "sd = interiorStdDev web / native")
    for key in sorted(groups):
        g = groups[key]
        lv = [x["level"] for x in g if x["level"] is not None]
        sd = [x["sd"] for x in g if x["sd"] is not None]
        print(f"{key[0]:<6}{key[1]:<9}{key[2]:<22}{key[3]:<10} n={len(g)}  level "
              f"{st.mean(lv) if lv else float('nan'):+.4f}  sd x{st.mean(sd) if sd else float('nan'):.3f}   "
              + " ".join(f"{x['scale']}x:{x['level']:+.3f}" for x in g if x["level"] is not None))
    return 0


def main() -> int:
    if len(sys.argv) < 3:
        raise SystemExit(__doc__)
    cmd, arg, rest = sys.argv[1], sys.argv[2], sys.argv[3:]
    if cmd == "build":
        return build(arg)
    if cmd == "render":
        return render(arg, rest)
    if cmd == "table":
        return table(arg, rest)
    raise SystemExit(__doc__)


if __name__ == "__main__":
    raise SystemExit(main())
