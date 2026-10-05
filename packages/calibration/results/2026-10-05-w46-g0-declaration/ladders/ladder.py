#!/usr/bin/env python3.12
"""W46 G0 (e): the ladders, built, rendered and read under the hashed protocol (charter clause 4; Design
"The ladders", MARKED). W45 G0's ladder driver (`results/2026-10-03-w45-g0-operator/ladders/ladder.py`),
ported for W46's protocol; W45's committed copy is untouched.

    python3.12 -B ladder.py plan             # every rung: label, ladder, slot, leaf, value, cells, scales
    python3.12 -B ladder.py build            # build every rung's candidate (fit/build-candidate.ts)
    python3.12 -B ladder.py render [LABEL..] # render every rung (control first), 1x then 2x
    python3.12 -B ladder.py read             # results.json and results.txt (read.py)

What W46 changes from W45's driver:
- **The rungs are one-leaf moves of the snapshots** (`protocol.json`): `control` (no override) and,
  per lever, each value with every other leaf at its snapshot value. Labels are `<lever>-<value>`.
- **The cells per rung are `ladders/cells.json`'s, by the arm's pose**: ladder (i)'s active arm its rest
  cells, its receded arm its inactive cells (a document's tintAlpha moves no pixel of the other pose);
  ladder (ii) its rest cells and its two inactive bar cells; ladder (iii) its inactive cells; the control
  the union. Every cell is checked against the planner adapter (no referee) and scenes.json (no holdout,
  declared by both dark profiles) before any launch.
- **Both scales, every rung**, so the reader can hold a lever's other scale to the control's bytes.
- **W46's bindings**: part 1 hashed and `declare.py check` passing before any render; scratch
  `~/vitrea-w46/g0-ladders/<label>/<scale>x/`; every launch through `../with-gpu.sh`; W44's and W45's
  places refused.
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

PROTOCOL_PATH = HERE / "protocol.json"
CANDIDATES = HERE / "candidates"
SCRATCH = W.refuse_other_wave_path(W.LADDER_SCRATCH, "the ladder scratch")


def protocol() -> dict:
    p = json.loads(PROTOCOL_PATH.read_text())
    if p["cells"]["sha256"] != W.file_sha(W.LADDER_CELLS):
        raise W.Refusal("protocol.json pins another ladders/cells.json")
    return p


def now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def log(row):
    with (HERE / "runs.jsonl").open("a") as f:
        f.write(json.dumps(row, sort_keys=True) + "\n")


def fmt(v) -> str:
    return f"{v:g}"


def levers(p: dict) -> list[tuple[dict, dict]]:
    return [(lad, lev) for lad in p["ladders"] for lev in lad.get("arms", []) + lad.get("levers", [])]


def pose_of(lad: dict, lev: dict) -> str:
    spec = lad["cellsByArm"]
    return spec.get(lev["id"], spec.get("*"))


def cells_for(lad_id: str | None, pose: str) -> list[str]:
    body = json.loads(W.LADDER_CELLS.read_text())
    if lad_id is None:
        return sorted(body["union"])
    lad = body["ladders"][lad_id]
    out = []
    for part in pose.split("+"):
        out += lad[part]
    return sorted(set(out))


def rungs() -> list[dict]:
    p = protocol()
    out = [dict(label=p["control"]["label"], ladder=None, lever=None, slot=None, leaf=None, value=None,
                overrides={}, cells=cells_for(None, ""), actsAt="both")]
    for lad, lev in levers(p):
        for v in lev["values"]:
            lo, hi = lev["domain"]
            if not lo <= v <= hi:
                raise W.Refusal(f"{lev['id']} {v} is outside its domain {lev['domain']}")
            out.append(dict(label=f"{lev['id']}-{fmt(v)}", ladder=lad["id"], lever=lev["id"], slot=lev["slot"],
                            leaf=lev["leaf"], value=v, shipped=lev["shipped"], actsAt=lev["actsAt"],
                            overrides={lev["slot"]: {lev["leaf"]: v}}, cells=cells_for(lad["id"], pose_of(lad, lev))))
    labels = [r["label"] for r in out]
    if len(set(labels)) != len(labels):
        raise W.Refusal("two rungs share a label")
    return out


def admitted(cells: list[str]) -> list[str]:
    """Every rendered cell: declared by both dark profiles, not a holdout scene, not a referee."""
    plan = W.referee_plan()
    scenes = plan.load_scenes()
    held = set(plan.load_manifest(scenes=scenes)["scenes"])
    for sid in cells:
        role = scenes["role"].get(sid)
        why = ("a holdout scene" if role == "holdout" else "a referee" if sid in held else
               f"in no set the ladders render ({role})" if role not in protocol()["sets"].split(",") else
               "undeclared" if any(sid not in scenes["declared"][p] for p in W.DARK_025) else None)
        if why:
            raise W.Refusal(f"ladder REFUSES: {sid} is {why}")
    return cells


def build() -> int:
    for r in rungs():
        folder = CANDIDATES / r["label"]
        if folder.exists():
            continue
        spec = SCRATCH / "specs" / f"{r['label']}.json"
        spec.parent.mkdir(parents=True, exist_ok=True)
        spec.write_text(json.dumps(dict(label=r["label"], note=f"W46 ladder {r['ladder']} {r['lever']} {r['value']}",
                                        overrides=r["overrides"]), indent=2) + "\n")
        got = subprocess.run(["pnpm", "exec", "tsx", str(W.BUILDER), str(spec)], cwd=W.CAL, capture_output=True,
                             text=True, env=dict(os.environ, W46_CANDIDATE_ROOT=str(CANDIDATES)))
        print(r["label"], "build exit", got.returncode, got.stderr[-400:] if got.returncode else "", flush=True)
        if got.returncode:
            return got.returncode
    return 0


def preflight() -> None:
    W.require_part(1)
    got = subprocess.run([sys.executable, "-B", str(W.DECLARE), "check"], capture_output=True, text=True, cwd=EVIDENCE)
    if got.returncode:
        raise W.Refusal("render REFUSES: declare.py check fails:\n" + got.stdout[-2000:])


def render(labels: list[str]) -> int:
    preflight()
    done = [json.loads(ln) for ln in (HERE / "runs.jsonl").read_text().splitlines()] \
        if (HERE / "runs.jsonl").exists() else []
    (HERE / "logs").mkdir(exist_ok=True)
    for r in rungs():
        if labels and r["label"] not in labels:
            continue
        cells = admitted(r["cells"])
        candidate = CANDIDATES / r["label"] / "candidate.json"
        if not candidate.exists():
            raise W.Refusal(f"{r['label']} is not built")
        for scale in (1, 2):
            run_label = f"{r['label']}/{scale}x"
            if any(x.get("label") == run_label and x.get("exitCode") == 0 for x in done):
                continue
            attempt = 0
            logfile = HERE / "logs" / (run_label.replace("/", "__") + ".txt")
            while logfile.exists():
                attempt += 1
                logfile = HERE / "logs" / (run_label.replace("/", "__") + f".relaunch-{attempt}.txt")
            out = SCRATCH / r["label"] / f"{scale}x"
            out.mkdir(parents=True, exist_ok=True)
            argv = ["pnpm", "run", "-s", "compare", "--", "--profile", W.PROFILE[scale], "--renderer", "webgpu",
                    "--candidate-document", str(candidate.relative_to(W.CAL)), "--set", protocol()["sets"],
                    "--scene", ",".join(cells), "--alpha", "--write-partial", "--out-matrix", str(out / "matrix.json")]
            env = {k: v for k, v in os.environ.items() if not k.startswith("VITREA_")}
            env["VITREA_WEB_CAPTURES"] = str(out / "web-captures")
            started = now()
            log(dict(label=run_label, started=started, cells=len(cells), attempt=attempt,
                     argv=[a if a != ",".join(cells) else f"<{len(cells)} scenes>" for a in argv]))
            with logfile.open("x") as f:
                result = subprocess.run([str(W.WITH_GPU), f"ladder {run_label}", *argv], cwd=W.CAL, env=env,
                                        stdout=f, stderr=subprocess.STDOUT)
            log(dict(label=run_label, started=started, completed=now(), exitCode=result.returncode))
            print(run_label, "exit", result.returncode, flush=True)
            if result.returncode != 0:
                return result.returncode
    return 0


def main() -> int:
    verb = sys.argv[1] if len(sys.argv) > 1 else ""
    if verb == "plan":
        rs = rungs()
        for r in rs:
            print(f"{r['label']:<16} {str(r['ladder']):<5} {str(r['slot']):<13} {str(r['leaf']):<30} "
                  f"{str(r['value']):<6} acts at {r['actsAt']:<4} {len(r['cells'])} cells")
        print(len(rs), "rungs,", 2 * len(rs), "launches")
        return 0
    if verb == "build":
        return build()
    if verb == "render":
        return render(sys.argv[2:])
    if verb == "read":
        sys.path.insert(0, str(HERE))
        import read  # noqa: PLC0415
        return read.main()
    raise SystemExit(__doc__)


if __name__ == "__main__":
    raise SystemExit(main())
