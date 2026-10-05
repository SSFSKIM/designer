#!/usr/bin/env python3.12
"""W47 G0 (g): the four ladders, built, rendered and read under the hashed protocol (charter clause 5;
Design "The ladders", MARKED; X69, X70). W46 G0's driver (`results/2026-10-05-w46-g0-declaration/
ladders/ladder.py`), ported by copy and re-bound; W46's committed copy is untouched.

    python3.12 -B ladder.py plan             # every rung: label, ladder, overrides, cells, X70 per scale
    python3.12 -B ladder.py build            # build every buildable rung (fit/build-candidate.ts)
    python3.12 -B ladder.py render [LABEL..] # render every buildable rung (control first), 1x then 2x
    python3.12 -B ladder.py read             # results.json, results.txt, selections.json (read.py)

What W47 changes from W46's driver:
- **The rungs are the protocol's, listed** (`protocol.json` `ladders[].rungs`): W47's ladders move
  several leaves at once (a base tintAlpha with a far delta, a span top or a gain; the second tap's
  three leaves at a top), so each rung states its `overrides` whole, every other leaf at its snapshot
  value. `control` is the snapshots on the union.
- **Every override is admitted and inside its domain before anything is built** (X67, X68): a key the
  slot's snapshot does not name must be in `bindings.ADMITTED`, and every value in `bindings.DOMAINS`.
- **A rung whose value depends on an earlier reading** names it `{"select": NAME}`; it is resolved from
  `selections.json`, which read.py writes, and refused (never guessed) until that selection exists.
- **A rung needing an operator the runtime does not yet know** (operator 1's `tintAlphaFar*`, operator
  2's `sizeFineTap*`) is WAITING: `build` and `render` skip it and say why, and nothing renders it.
- **X70**: per rung and scale the cells requested (`cells.json` by the rung's poses), the cells
  `compare` plans for them (`compare_selects` over the protocol's `sets`, the referee loader's
  transcription of `cli/compare.ts`) and, at read, the rows measured (`read.py`). `x70_plan` refuses
  BEFORE any launch when planned differs from requested; W46's `admitted` (declared by both dark
  profiles, not a holdout scene, not a referee, in a rendered set) runs beside it.
- **W47's bindings**: part 1 hashed and `declare.py check` passing before any render; scratch
  `~/vitrea-w47/g0-ladders/<label>/<scale>x/`; every launch through `../with-gpu.sh`; W44–W46's places
  refused; `W47_CANDIDATE_ROOT` for the builder.

W46 G0's text follows, unchanged; where it says W46 it is W47.

W46 G0 (e): the ladders, built, rendered and read under the hashed protocol (charter clause 4; Design
"The ladders", MARKED). W45 G0's ladder driver (`results/2026-10-03-w45-g0-operator/ladders/ladder.py`),
ported for W46's protocol; W45's committed copy is untouched.

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

import copy
import datetime
import json
import os
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
EVIDENCE = HERE.parent
sys.path.insert(0, str(EVIDENCE))
import bindings as W  # noqa: E402

PROTOCOL_PATH = W.LADDER_PROTOCOL
CANDIDATES = HERE / "candidates"
SELECTIONS = HERE / "selections.json"
SCRATCH = W.refuse_other_wave_path(W.LADDER_SCRATCH, "the ladder scratch")
MATERIAL_TS = W.ROOT / "packages/renderer-webgpu/src/material.ts"
OPERATOR_LEAVES = {"operator 1": W.OPERATOR_1, "operator 2": W.OPERATOR_2}
LABEL = re.compile(r"^[a-z0-9][a-z0-9.-]*$")


def protocol(path: Path = PROTOCOL_PATH) -> dict:
    p = json.loads(Path(path).read_text())
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


def cells_for(lad_id: str | None, poses: str) -> list[str]:
    body = json.loads(W.LADDER_CELLS.read_text())
    if lad_id is None:
        return sorted(body["union"])
    lad = body["ladders"][lad_id]
    out = []
    for part in poses.split("+"):
        out += lad[part]
    return sorted(set(out))


def runtime_knows(leaf: str, material: str | None = None) -> bool:
    """Whether this tree's runtime defines `leaf` in `DEFAULT_MATERIAL_PROFILE` (the operators land on
    sibling branches; until they merge a rung naming one is WAITING, never built)."""
    material = material if material is not None else MATERIAL_TS.read_text()
    return f"\n  {leaf}:" in material


def waiting(rung: dict, material: str | None = None) -> str | None:
    """None when the runtime knows every operator leaf the rung needs, else the WAITING reason."""
    missing = [leaf for op in rung.get("needsOperator", []) for leaf in OPERATOR_LEAVES[op]
               if not runtime_knows(leaf, material)]
    if missing:
        return (f"WAITING: {rung['label']} needs {', '.join(rung['needsOperator'])}; this runtime's material.ts defines "
                f"no {', '.join(missing)} (G0 (a)/(b) not merged)")
    return None


def selections(path: Path = SELECTIONS) -> dict:
    return json.loads(path.read_text())["selections"] if path.exists() else {}


def resolve_overrides(rung: dict, chosen: dict) -> dict:
    """The rung's overrides with every `{"select": NAME}` value and its `select` merge filled from the
    recorded selections; a selection not yet recorded refuses (the value is never guessed)."""
    out = copy.deepcopy(rung["overrides"])
    for slot, leaves in out.items():
        for leaf, value in list(leaves.items()):
            if isinstance(value, dict):
                name = value["select"]
                if name not in chosen:
                    raise W.Refusal(f"{rung['label']}: {leaf} depends on the reading {name!r}, not yet recorded in "
                                    "selections.json (read the earlier rungs first)")
                if chosen[name]["value"] is None:
                    raise W.Refusal(f"{rung['label']}: the reading {name!r} found no admissible value "
                                    f"({chosen[name].get('why')}); the rung is not built")
                leaves[leaf] = chosen[name]["value"]
    for slot, name in rung.get("select", {}).items():
        if name not in chosen:
            raise W.Refusal(f"{rung['label']}: depends on the reading {name!r}, not yet recorded in selections.json")
        if chosen[name]["overrides"] is None:
            raise W.Refusal(f"{rung['label']}: the reading {name!r} found no admissible rung ({chosen[name].get('why')})")
        out.setdefault(slot, {}).update(chosen[name]["overrides"].get(slot, {}))
    return out


def snapshot_leaf(slot: str, key: str):
    node = W.document(slot)["patch"]
    for part in key.split("."):
        if not isinstance(node, dict) or part not in node:
            return None
        node = node[part]
    return node


def check_overrides(label: str, overrides: dict) -> None:
    """X60, X67, X68: dark slots only; each key named by the slot's snapshot or admitted (ADMITTED);
    each value inside its declared domain (DOMAINS); finite numbers. Operator 2 is receded-only (X66)."""
    for slot, leaves in overrides.items():
        if slot not in W.MOVING_SLOTS:
            raise W.Refusal(f"{label}: {slot} is not a dark slot; the light material never moves (X60)")
        for key, value in leaves.items():
            if isinstance(value, dict):
                continue                                   # a selection, checked once resolved
            if snapshot_leaf(slot, key) is None and key not in W.ADMITTED[slot]:
                raise W.Refusal(f"{label}: {slot} {key} is neither a snapshot leaf nor admitted (X67)")
            if not isinstance(value, (int, float)) or isinstance(value, bool) or value != value:
                raise W.Refusal(f"{label}: {slot} {key} {value!r} is not a finite number")
            if not W.in_domain(slot, key, value):
                raise W.Refusal(f"{label}: {slot} {key} {value} is outside its declared domain (X68)")


def rungs(p: dict | None = None, chosen: dict | None = None, resolve: bool = False) -> list[dict]:
    """Every rung in protocol order; `resolve` fills dependent rungs from `chosen` (or selections.json),
    leaving unresolvable ones with `unresolved` set."""
    p = p or protocol()
    chosen = selections() if chosen is None else chosen
    out = [dict(label=p["control"]["label"], ladder=None, overrides={}, cells=cells_for(None, ""), actsAt="both",
                poses="rest+inactive")]
    for lad in p["ladders"]:
        for r in lad["rungs"]:
            entry = dict(r, ladder=lad["id"], cells=cells_for(lad["id"], r["poses"]))
            check_overrides(r["label"], r["overrides"])
            if r.get("dependsOn") or r.get("select"):
                entry["dependent"] = True
                if resolve:
                    try:
                        entry["overrides"] = resolve_overrides(r, chosen)
                        check_overrides(r["label"], entry["overrides"])
                    except W.Refusal as refusal:
                        entry["unresolved"] = str(refusal)
            out.append(entry)
    labels = [r["label"] for r in out]
    if len(set(labels)) != len(labels):
        raise W.Refusal("two rungs share a label")
    bad = [x for x in labels if not LABEL.match(x)]
    if bad:
        raise W.Refusal(f"labels outside the grammar: {bad}")
    return out


def admitted(cells: list[str], sets: str | None = None) -> list[str]:
    """Every rendered cell: declared by both dark profiles, not a holdout scene, not a referee (X69)."""
    ref = W.referees()
    scenes = ref.load_scenes()
    held = set(ref.load_manifest(scenes=scenes)["scenes"])
    sets = sets or protocol()["sets"]
    for sid in cells:
        role = scenes["role"].get(sid)
        why = ("a holdout scene" if role == "holdout" else "a referee" if sid in held else
               f"in no set the ladders render ({role})" if role not in sets.split(",") else
               "undeclared" if any(sid not in scenes["declared"][p] for p in W.DARK_025) else None)
        if why:
            raise W.Refusal(f"ladder REFUSES: {sid} is {why}")
    return cells


def planned(cells: list[str], scale: int, sets: str, scenes: dict | None = None) -> set[tuple[str, str]]:
    """The cells `compare --profile <scale> --set <sets> --scene <cells>` will plan (X70)."""
    ref = W.referees()
    scenes = scenes or ref.load_scenes()
    return ref.compare_selects(scenes, [W.PROFILE[scale]], sets.split(","), set(cells))


def x70_plan(label: str, cells: list[str], sets: str, scenes: dict | None = None) -> dict[int, set]:
    """X70 before rendering: per scale, the planned set must equal the requested set."""
    out = {}
    for scale in (1, 2):
        want = {(W.PROFILE[scale], s) for s in cells}
        got = planned(cells, scale, sets, scenes)
        if got != want:
            raise W.Refusal(f"{label} {scale}x: X70 REFUSES before rendering: compare would plan {len(got)} of the "
                            f"{len(want)} requested cells; not planned {sorted(s for _, s in want - got)[:6]}, "
                            f"unrequested {sorted(s for _, s in got - want)[:6]}")
        out[scale] = got
    return out


def build() -> int:
    for r in rungs(resolve=True):
        if r["label"] == "control" and (CANDIDATES / "control").exists():
            continue
        folder = CANDIDATES / r["label"]
        if folder.exists():
            continue
        why = waiting(r) or r.get("unresolved")
        if why:
            print(r["label"], "not built:", why, flush=True)
            continue
        spec = SCRATCH / "specs" / f"{r['label']}.json"
        spec.parent.mkdir(parents=True, exist_ok=True)
        spec.write_text(json.dumps(dict(label=r["label"], note=f"W47 ladder {r['ladder']} {r.get('moves', 'control')}",
                                        overrides=r["overrides"]), indent=2) + "\n")
        got = subprocess.run(["pnpm", "exec", "tsx", str(W.BUILDER), str(spec)], cwd=W.CAL, capture_output=True,
                             text=True, env=dict(os.environ, W47_CANDIDATE_ROOT=str(CANDIDATES)))
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
    p = protocol()
    done = [json.loads(ln) for ln in (HERE / "runs.jsonl").read_text().splitlines()] \
        if (HERE / "runs.jsonl").exists() else []
    (HERE / "logs").mkdir(exist_ok=True)
    for r in rungs(p, resolve=True):
        if labels and r["label"] not in labels:
            continue
        why = waiting(r) or r.get("unresolved")
        if why:
            print(r["label"], "not rendered:", why, flush=True)
            continue
        cells = admitted(r["cells"], p["sets"])
        x70_plan(r["label"], cells, p["sets"])
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
                    "--candidate-document", str(candidate.relative_to(W.CAL)), "--set", p["sets"],
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
        p = protocol()
        scenes = W.referees().load_scenes()
        rs = rungs(p, resolve=True)
        for r in rs:
            state = waiting(r) or r.get("unresolved") or "buildable"
            admitted(r["cells"], p["sets"])
            x70_plan(r["label"], r["cells"], p["sets"], scenes)
            print(f"{r['label']:<22} {str(r['ladder']):<4} {len(r['cells']):>3} cells (X70 planned = requested at 1x "
                  f"and 2x)  {json.dumps(r['overrides'], sort_keys=True)}  [{state[:60]}]")
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
