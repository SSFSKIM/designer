#!/usr/bin/env python3.12
"""W46 G1: the LIGHT strict-mode stage that proves X60 by render (charter X60; clause 6; Design "The
populations per phase"; Decision Log 8 item 4).

X60 holds every light 0.25 row byte-identical while the dark 0.25 documents move. G0's `x60.py render`
reads a stage's light rows against the published light generation `ebc3d9105a4a`; G0's `stage.py`
stages the dark pair only. This declares and measures the light stage `x60.py render` reads:

  declare         `matrix stage` at ~/vitrea-w46/g1-stage-x60-light/: the two light -glass0.25 standard
                  profiles, both tiers, every set the generation carries, over the LIVE light documents,
                  which must be the light snapshots' bytes (X62). No capture. Scratch: never published.
  cells           writes `x60-light-cells.json` beside this file: per light profile, the declared scenes
                  less the light holdout and W44's six referees (spent at read 7 and never re-rendered):
                  138 per scale, the charter's count, refused if it is not.
  measure <tier>  per light profile, ONE launch of exactly those scenes in strict mode
                  (`--stage --material-profile --receded-profile`, `--set calibration,validation,
                  recorded,probe --scene <the 138> --alpha --write-partial`), captures into the stage's
                  own `web-captures`, through G1's `with-gpu.sh` (the GPU lock, the classifying census,
                  the browser pin). A started launch with no completion is a stop.
  read            G0's `x60.py render --stage <the stage>` into G1's `stage/x60-render.json`.

The launches use G0's `stage.launch` with a mode this script adds to the imported module at run time
(G0's file is not edited).
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
G1 = HERE.parent
G0 = G1.parent / "2026-10-05-w46-g0-declaration"
sys.path.insert(0, str(G0))
import bindings as W  # noqa: E402

STAGE_DIR = W.SCRATCH / "g1-stage-x60-light"
OUT = HERE / "x60-light"
CELLS = HERE / "x60-light-cells.json"
ACTIVE = "profiles/apple-macos-27.0-1x-light-standard-glass0.25.json"
RECEDED = "profiles/apple-macos-27.0-1x-light-standard-glass0.25-receded.json"
SETS = "calibration,validation,recorded,probe"
PER_SCALE = 138


def module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def g0_stage():
    stage = module("w46_g0_stage", G0 / "stage" / "stage.py")
    stage.W.WITH_GPU = G1 / "with-gpu.sh"         # G1's census log, the same lock
    stage.MODES["x60"] = dict(stage=STAGE_DIR, out=OUT, captures=STAGE_DIR / "web-captures", tiers="webgpu,css")
    return stage


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


def cells() -> int:
    got = light_cells()
    body = dict(what="W46 G1: X60's light strict-mode stage, its declared cells (the light profiles' "
                     "non-withheld scenes: no holdout, no W44 referee)", sets=SETS, stage=str(STAGE_DIR),
                perProfile={p: dict(count=len(v), sha256=hashlib.sha256(",".join(v).encode()).hexdigest(), scenes=v)
                            for p, v in got.items()})
    CELLS.write_text(json.dumps(body, indent=1) + "\n")
    print({p: v["count"] for p, v in body["perProfile"].items()})
    return 0


def declare() -> int:
    require_light_snapshots()
    W.refuse_other_wave_path(STAGE_DIR, "the stage")
    argv = ["pnpm", "run", "-s", "matrix", "--", "stage", str(STAGE_DIR), "--profile", ",".join(W.LIGHT_025),
            "--renderer", "webgpu,css", "--set", "calibration,validation,holdout,recorded,probe",
            "--material-profile", ACTIVE, "--receded-profile", RECEDED]
    got = subprocess.run(argv, cwd=W.CAL, capture_output=True, text=True)
    g0_stage().log(OUT, dict(label="x60-declare", argv=argv, exitCode=got.returncode,
                             output=(got.stdout + got.stderr)[-2000:]))
    print(got.stdout[-1500:], got.stderr[-1500:])
    return got.returncode


def measure(tier: str) -> int:
    require_light_snapshots()
    stage = g0_stage()
    if not (STAGE_DIR / "membership.json").exists():
        raise W.Refusal(f"{STAGE_DIR}: not a declared stage (run `declare` first)")
    declared = json.loads(CELLS.read_text())["perProfile"]
    live = light_cells()
    for p in W.LIGHT_025:
        scenes = declared[p]["scenes"]
        if scenes != live[p]:
            raise W.Refusal(f"{p}: the declared cells are not the non-withheld light scenes")
        label = f"x60/{tier}/{p}"
        complete, _ = stage.done(OUT, label)
        if complete:
            continue
        marker = OUT / "logs" / (label.replace("/", "__") + ".started")
        if marker.exists():
            raise W.Refusal(f"started pass without completion is a stop: {label}")
        marker.parent.mkdir(parents=True, exist_ok=True)
        marker.write_text(stage.now() + "\n")
        argv = ["pnpm", "run", "-s", "compare", "--", "--stage", str(STAGE_DIR), "--profile", p, "--renderer", tier,
                "--material-profile", ACTIVE, "--receded-profile", RECEDED, "--set", SETS, "--scene",
                ",".join(scenes), "--alpha", "--write-partial"]
        code = stage.launch(argv, label, OUT, "x60", scenes)
        if code not in (0, 1):
            raise W.Refusal(f"{label}: exit {code}; stop")
    return 0


def read() -> int:
    got = subprocess.run([sys.executable, "-B", str(G0 / "stage" / "x60.py"), "render", "--stage", str(STAGE_DIR),
                          "--out", str(HERE / "x60-render.json")], cwd=G0 / "stage")
    return got.returncode


def main(argv) -> int:
    W.require_shared()
    verb = argv[1] if len(argv) > 1 else ""
    if verb == "cells":
        return cells()
    if verb == "declare":
        return declare()
    if verb == "measure":
        return measure(argv[2])
    if verb == "read":
        return read()
    print(__doc__)
    return 64


if __name__ == "__main__":
    sys.exit(main(sys.argv))
