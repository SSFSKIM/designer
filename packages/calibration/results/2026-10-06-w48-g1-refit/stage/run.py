#!/usr/bin/env python3.12
"""W48 G1 steps 4 and 7: the dark strict-mode stage, and X60's light strict-mode stage, through W47's
`stage/stage.py` and `stage/x60.py` inherited by path under W48's bindings (charter clauses 6-8;
Design "The populations per phase"; X53, X60, X69).

W47's `stage.py` launches through `bindings.WITH_GPU`, G0's `with-gpu.sh`, whose census log is G0's
committed `census.jsonl`; here the binding is re-pointed at G1's launcher (the same lock and census,
G1's log), as W46 G1's `x60-light.py` did. Nothing else of W47's tool changes (`inherit.REBIND` already
sets its `SEALED_BY` to "W48 G1").

  dark <stage.py verb> ...   W47's stage.py CLI on G1's dark stage (~/vitrea-w48/g1-stage-dark): declare,
                             measure <tier>, exposure <tier>; logs and runs under this directory.
  x60 cells                  `x60-light-cells.json`: per light 0.25 profile, the declared scenes less the
                             light holdout and W44's six referees (spent at read 7): 138 per scale.
  x60 declare                `matrix stage` at ~/vitrea-w48/g1-stage-x60-light over the LIVE light
                             documents, which must be the light snapshots' bytes (X62). Scratch only.
  x60 measure <tier>         per light profile, ONE strict-mode launch of exactly those scenes.
  x60 read                   W47's `x60.py render --stage <the light stage>` into `x60-render.json`.
  x60 evidence [--after-exposure]
                             W47's `x60.py evidence` over G1's candidates into `x60-evidence.json`.
"""
from __future__ import annotations

import contextlib
import hashlib
import io
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
G1 = HERE.parent
G0 = G1.parent / "2026-10-06-w48-g0-declaration"
sys.path.insert(0, str(G0))
import inherit  # noqa: E402

W = inherit.W
W.WITH_GPU = G1 / "with-gpu.sh"                       # G1's census log; G0's lock and census
STAGE = inherit.tool("stage/stage.py", "stage")
X60 = inherit.tool("stage/x60.py", "x60")

LIGHT_STAGE = W.SCRATCH / "g1-stage-x60-light"
X60_OUT = HERE / "x60-light"
CELLS = HERE / "x60-light-cells.json"
ACTIVE = "profiles/apple-macos-27.0-1x-light-standard-glass0.25.json"
RECEDED = "profiles/apple-macos-27.0-1x-light-standard-glass0.25-receded.json"
SETS = "calibration,validation,recorded,probe"
PER_SCALE = 138
STAGE.MODES["x60"] = dict(stage=LIGHT_STAGE, out=X60_OUT, captures=LIGHT_STAGE / "web-captures", tiers="webgpu,css")
if STAGE.MODES["g1"]["out"] != HERE:
    raise W.Refusal(f"the bindings put G1's stage evidence at {STAGE.MODES['g1']['out']}, not {HERE}")


def require_light_snapshots() -> None:
    for rel, slot in ((ACTIVE, "active.light"), (RECEDED, "receded.light")):
        got = hashlib.sha256((W.CAL / rel).read_bytes()).hexdigest()
        if got != W.DOCUMENT_SHA[slot]:
            raise W.Refusal(f"x60 stage REFUSES: {rel} is {got[:12]}, not the light snapshot (X62)")


def light_cells() -> dict:
    B, _, _ = W.load_cuts()
    out = {}
    for p in W.LIGHT_025:
        held = {s for q, s in B.LIGHT_WITHHELD if q == p}
        keep = sorted(s for s in B.SCENES.declared(p) if s not in held and B.SCENES.role[s] != "holdout")
        if len(keep) != PER_SCALE:
            raise W.Refusal(f"{p}: {len(keep)} non-withheld light scenes, not the charter's {PER_SCALE}")
        if any(B.SCENES.role[s] not in SETS.split(",") for s in keep):
            raise W.Refusal(f"{p}: a non-withheld scene outside {SETS}")
        out[p] = keep
    return out


def x60_cells() -> int:
    got = light_cells()
    body = dict(what="W48 G1: X60's light strict-mode stage, its declared cells (the light profiles' "
                     "non-withheld scenes: no holdout, no W44 referee)", sets=SETS, stage=str(LIGHT_STAGE),
                perProfile={p: dict(count=len(v), sha256=hashlib.sha256(",".join(v).encode()).hexdigest(), scenes=v)
                            for p, v in got.items()})
    CELLS.write_text(json.dumps(body, indent=1) + "\n")
    print({p: v["count"] for p, v in body["perProfile"].items()})
    return 0


def x60_declare() -> int:
    require_light_snapshots()
    W.refuse_other_wave_path(LIGHT_STAGE, "the stage")
    argv = ["pnpm", "run", "-s", "matrix", "--", "stage", str(LIGHT_STAGE), "--profile", ",".join(W.LIGHT_025),
            "--renderer", "webgpu,css", "--set", "calibration,validation,holdout,recorded,probe",
            "--material-profile", ACTIVE, "--receded-profile", RECEDED]
    got = subprocess.run(argv, cwd=W.CAL, capture_output=True, text=True)
    STAGE.log(X60_OUT, dict(label="x60-declare", argv=argv, exitCode=got.returncode,
                            output=(got.stdout + got.stderr)[-2000:]))
    print(got.stdout[-1500:], got.stderr[-1500:])
    return got.returncode


def x60_measure(tier: str) -> int:
    require_light_snapshots()
    if not (LIGHT_STAGE / "membership.json").exists():
        raise W.Refusal(f"{LIGHT_STAGE}: not a declared stage (run `x60 declare` first)")
    declared = json.loads(CELLS.read_text())["perProfile"]
    live = light_cells()
    for p in W.LIGHT_025:
        scenes = declared[p]["scenes"]
        if scenes != live[p]:
            raise W.Refusal(f"{p}: the declared cells are not the non-withheld light scenes")
        label = f"x60/{tier}/{p}"
        complete, _ = STAGE.done(X60_OUT, label)
        if complete:
            continue
        marker = X60_OUT / "logs" / (label.replace("/", "__") + ".started")
        if marker.exists():
            raise W.Refusal(f"started pass without completion is a stop: {label}")
        marker.parent.mkdir(parents=True, exist_ok=True)
        marker.write_text(STAGE.now() + "\n")
        argv = ["pnpm", "run", "-s", "compare", "--", "--stage", str(LIGHT_STAGE), "--profile", p, "--renderer", tier,
                "--material-profile", ACTIVE, "--receded-profile", RECEDED, "--set", SETS, "--scene",
                ",".join(scenes), "--alpha", "--write-partial"]
        code = STAGE.launch(argv, label, X60_OUT, "x60", scenes)
        if code not in (0, 1):
            raise W.Refusal(f"{label}: exit {code}; stop")
    return 0


def x60_main(args: list[str], out: Path) -> int:
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        code = X60.main(args + ["--out", str(out)])
    out.with_suffix(".txt").write_text(buf.getvalue())
    print(buf.getvalue(), end="")
    return code or 0


def main(argv) -> int:
    W.require_shared()
    what, verb = (argv[1:3] + ["", ""])[:2]
    if what == "dark":
        return STAGE.main(["stage.py", *argv[2:]])
    if what == "x60":
        if verb == "cells":
            return x60_cells()
        if verb == "declare":
            return x60_declare()
        if verb == "measure":
            return x60_measure(argv[3])
        if verb == "read":
            return x60_main(["render", "--stage", str(LIGHT_STAGE)], HERE / "x60-render.json")
        if verb == "evidence":
            extra = ["--after-exposure"] if "--after-exposure" in argv else []
            return x60_main(["evidence", *extra], HERE / ("x60-evidence-after-exposure.json" if extra
                                                          else "x60-evidence.json"))
    print(__doc__)
    return 64


if __name__ == "__main__":
    sys.exit(main(sys.argv))
