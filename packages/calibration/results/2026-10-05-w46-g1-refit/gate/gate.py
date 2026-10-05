#!/usr/bin/env python3.12
"""W46 G1 step 5: the freeze-free gate reading of a fit point (charter clause 6; Design "The populations
per phase"; Decision Log 9: "Both are carried through the freeze-free gate reading (step 5) so the gate
report shows both; the freeze (step 3) seals only the point the parent names after the gate report").

Decision Log 9 puts the freeze after the gate report, so the gate is read on each point's CANDIDATE
document (candidate mode, nothing injected; W43 G0 (f)) rather than on a strict-mode stage of sealed
bytes. It reads every row the strict-mode stage would carry before the exposure:

  render <label> [--tiers webgpu,css] [--light]
                                        per dark scale and tier, ONE launch of the dark profile's
                                        non-withheld scenes (its declared scenes less the seven
                                        holdout scenes and W46's six referees: 104 per scale), sets
                                        calibration,validation,recorded,probe, `--alpha --write-partial`,
                                        the point's candidate document, through G1's `with-gpu.sh`
                                        (the GPU lock, the classifying census, the browser pin), into
                                        ~/vitrea-w46/g1-scratch/gate/<label>/<tier>-<s>x/.
  read <label>                          W46's cuts (`cuts.py --kind candidate`) on the four matrices
                                        and their captures, against d0219cd684bf (every regression
                                        row's reference and T1's): `gate/<label>/cut.json.gz`, `cut.txt`.
  matrix <label>                        the four matrices as ONE matrix file (scratch), the form the
                                        sheets read.

A withheld cell refuses before any launch; a light profile is never rendered here (X60's light stage
is `stage/x60-light.py`). Every launch is logged in `gate/runs.jsonl` with its compare log under
`gate/logs/`; matrices and PNGs stay on the machine.
"""
from __future__ import annotations

import datetime
import gzip
import json
import os
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
G1 = HERE.parent
G0 = G1.parent / "2026-10-05-w46-g0-declaration"
sys.path.insert(0, str(G0))
import bindings as W  # noqa: E402

SCRATCH = W.SCRATCH / "g1-scratch" / "gate"
SETS = "calibration,validation,recorded,probe"
PER_SCALE = 104
WITH_GPU = G1 / "with-gpu.sh"
CANONICAL = W.CANONICAL_CAPTURES


def now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def log(row):
    with (HERE / "runs.jsonl").open("a") as f:
        f.write(json.dumps(row, sort_keys=True) + "\n")


def candidate(label: str) -> Path:
    path = W.refuse_other_wave_path(W.G1_FIT / "candidates" / label / "candidate.json", "the candidate")
    if not path.exists():
        raise W.Refusal(f"gate: {label} is not a built fit point")
    return path


LIGHT_PER_SCALE = 138


def light_scenes(profile: str) -> list[str]:
    """A light profile's non-withheld scenes (X60's 138 per scale: no light holdout, no W44 referee)."""
    B, _, _ = W.load_cuts()
    held = {s for q, s in B.LIGHT_WITHHELD if q == profile}
    out = sorted(s for s in B.SCENES.declared(profile) if s not in held and B.SCENES.role[s] != "holdout")
    if len(out) != LIGHT_PER_SCALE:
        raise W.Refusal(f"{profile}: {len(out)} non-withheld light scenes, not {LIGHT_PER_SCALE}")
    return out


def gate_scenes(profile: str) -> list[str]:
    """The dark profile's non-withheld scenes: declared, not a holdout scene, not a W46 referee."""
    if profile in W.LIGHT_025:
        return light_scenes(profile)
    B, _, _ = W.load_cuts()
    plan = W.referee_plan()
    held = set(plan.load_manifest()["scenes"])
    out = sorted(s for s in B.SCENES.declared(profile) if B.SCENES.role[s] != "holdout" and s not in held)
    if len(out) != PER_SCALE:
        raise W.Refusal(f"{profile}: {len(out)} non-withheld dark scenes, not the charter's {PER_SCALE}")
    if any(B.SCENES.role[s] not in SETS.split(",") for s in out):
        raise W.Refusal(f"{profile}: a non-withheld scene outside {SETS}")
    return out


def out_dir(label: str, name: str, scale: int) -> Path:
    return W.refuse_other_wave_path(SCRATCH / label / f"{name}-{scale}x", "the gate's scratch")


def render(label: str, tiers: list[str], light: bool = False) -> int:
    """`light`: the light profiles' non-withheld cells as well, in candidate mode (the candidate's light
    endpoints are the light snapshots, X60), so the gate cut reads the light rows its pooled sections
    (the light tables, C1, S1, X1, E2) need beside the dark ones."""
    cand = candidate(label)
    if tiers.index("webgpu") if "webgpu" in tiers else 0:
        raise W.Refusal("gate: the WebGPU tier renders first (the CSS rows read it as their twin)")
    for tier in tiers:
        for scale, profile in [(sc, W.PROFILE[sc]) for sc in (1, 2)] + \
                ([(1, W.LIGHT_025[0]), (2, W.LIGHT_025[1])] if light else []):
            scenes = gate_scenes(profile)
            dark = profile in W.DARK_025
            out = out_dir(label, tier if dark else f"light-{tier}", scale)
            # A census refusal launches nothing and leaves no matrix; the directory is reused.
            if (out / "matrix.json").exists():
                have = {r["key"]["sceneId"] for r in json.loads((out / "matrix.json").read_bytes())["cells"]}
                if set(scenes) <= have:
                    continue
                raise W.Refusal(f"{out}: a partial matrix exists; a gate directory is written once")
            out.mkdir(parents=True, exist_ok=True)
            run_label = f"{label}/{'' if dark else 'light-'}{tier}-{scale}x"
            argv = ["pnpm", "run", "-s", "compare", "--", "--profile", profile, "--renderer", tier,
                    "--candidate-document", str(cand.relative_to(W.CAL)), "--set", SETS, "--scene", ",".join(scenes),
                    "--alpha", "--write-partial", "--out-matrix", str(out / "matrix.json")]
            env = {k: v for k, v in os.environ.items() if not k.startswith("VITREA_")}
            # One capture tree per scale, shared by the two tiers, so the CSS row reads its WebGPU twin
            # and carries the cross-tier coherence rows a stage's row carries (the WebGPU tier first).
            env["VITREA_WEB_CAPTURES"] = str(captures_of(label, scale))
            started = now()
            log(dict(label=run_label, started=started, scenes=len(scenes),
                     argv=[a if a != ",".join(scenes) else f"<{len(scenes)} scenes>" for a in argv]))
            (HERE / "logs").mkdir(exist_ok=True)
            log_path = HERE / "logs" / f"{label}__{'' if dark else 'light-'}{tier}-{scale}x.txt"
            n = 0
            while log_path.exists():            # a census-refused launch's log, kept; this is a relaunch
                n += 1
                log_path = HERE / "logs" / f"{label}__{'' if dark else 'light-'}{tier}-{scale}x.relaunch-{n}.txt"
            with log_path.open("x") as f:
                got = subprocess.run([str(WITH_GPU), f"w46-gate {run_label}", *argv], cwd=W.CAL, env=env,
                                     stdout=f, stderr=subprocess.STDOUT)
            first = log_path.read_text().splitlines()[:1]
            code = 3 if got.returncode == 1 and first and ": REFUSES" in first[0] else got.returncode
            log(dict(label=run_label, started=started, completed=now(), exitCode=code))
            print(run_label, "exit", code, flush=True)
            if code not in (0, 1):
                return code             # 3: the census refused; nothing launched, rerun later
    return 0


def captures_of(label: str, scale: int) -> Path:
    return W.refuse_other_wave_path(SCRATCH / label / f"captures-{scale}x", "the gate's captures")


def matrices(label: str) -> list[Path]:
    return sorted((SCRATCH / label).glob("*-*x/matrix.json"))


def merged_captures(label: str) -> Path:
    merged = SCRATCH / label / "merged-captures"
    trees = [m.parent / "web-captures" for m in matrices(label)] + [captures_of(label, s) for s in (1, 2)]
    for tree in trees:
        if not tree.exists():
            continue
        for prof in tree.iterdir():
            for cell in prof.iterdir():
                (merged / prof.name / cell.name).mkdir(parents=True, exist_ok=True)
                for f in cell.iterdir():
                    link = merged / prof.name / cell.name / f.name
                    if not link.exists():
                        os.link(f, link)
    return merged


def merged_matrix(label: str) -> Path:
    cells, head = [], None
    for m in matrices(label):
        body = json.loads(m.read_bytes())
        head = head or {k: v for k, v in body.items() if k != "cells"}
        cells += body["cells"]
    path = SCRATCH / label / "merged-matrix.json"
    path.write_text(json.dumps(dict(head, cells=cells)))
    return path


def read(label: str) -> int:
    cand = candidate(label)
    out = HERE / label
    out.mkdir(exist_ok=True)
    scratch = SCRATCH / label / "cut.json"
    scratch.unlink(missing_ok=True)
    (out / "cut.txt").unlink(missing_ok=True)
    argv = [sys.executable, "-B", str(W.CUTS / "cuts.py"), "--kind", "candidate",
            "--candidate-document", str(cand.relative_to(W.ROOT))]
    for m in matrices(label):
        argv += ["--bed", str(m)]
    argv += ["--captures", str(merged_captures(label)), "--out", str(scratch), "--text", str(out / "cut.txt")]
    got = subprocess.run(argv, cwd=W.CUTS, capture_output=True, text=True)
    if got.returncode:
        print(got.stderr[-3000:])
        return got.returncode
    (out / "cut.json.gz").write_bytes(gzip.compress(scratch.read_bytes(), mtime=0))
    print((out / "cut.txt").read_text()[:3000])
    return 0


def main(argv) -> int:
    W.require_shared()
    verb = argv[1] if len(argv) > 2 else ""
    if verb == "render":
        tiers = (argv[argv.index("--tiers") + 1] if "--tiers" in argv else "webgpu,css").split(",")
        return render(argv[2], tiers, light="--light" in argv)
    if verb == "read":
        return read(argv[2])
    if verb == "matrix":
        print(merged_matrix(argv[2]))
        return 0
    print(__doc__)
    return 64


if __name__ == "__main__":
    sys.exit(main(sys.argv))
