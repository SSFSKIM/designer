#!/usr/bin/env python3.12
"""W46 G0 (a): the fit's measuring loop, W45 G0's (`results/2026-10-03-w45-g0-operator/fit/fit.py`)
ported for W46 (charter clauses 1 and 5; Design "The moves"; X60, X62, X64). W45's committed copy is
untouched. G1 runs it; G0 commits it, tested, before part 2 exists.

    python3.12 -B fit.py start                     build the declared starting point (`start-d0219`)
    python3.12 -B fit.py point <label> --stage S --family F [--scope S] [--note N] leaf@slot=value ...
    python3.12 -B fit.py render <label> --scope S  (one more scope of a built candidate)
    python3.12 -B fit.py read <label>

**What W46 changes from W45's driver, each a refusal rather than a convention:**
- **W46's part 2, by W46's hash** (`bindings.require_part(2)`; W44's and W45's part hashes refused),
  and `declare.py check-fit` passing, before anything runs.
- **The dark slots.** `check_overrides` admits exactly the (slot, leaf) pairs part 2 declares in
  `active.dark` and `receded.dark`, inside their domains; a light slot refuses (X60). An X64 key
  stated at its INHERITED value is not a move and is always admitted (Design "The moves": stage 2
  materialises the receded keys at the stage-1 active's resolved values, an unchanged start).
- **One starting point** (Design "The moves": `d0219cd684bf` by hash): `start-d0219`, the snapshots
  with no override, lineage `d0219`. W45's second (W44's joint point) has no W46 counterpart.
- **Both scales, every point.** The targets are read at 1x and 2x (Decision Log 3, per profile), so
  every render is two compare launches, one per dark profile, `--alpha --write-partial`, through
  `../with-gpu.sh` (the GPU lock, the classifying census and the browser pin), into
  `~/vitrea-w46/g1-scratch/fit/<label>/<scope>-<scale>x/`. W45's `x48` scope is gone: X60 is read by
  evidence on every candidate (`identity`: the light endpoints patch- and digest-identical to the
  light snapshots) and by render at the gate, which is G1's stage, not the fit's.
- **The scopes are the stages** (`cuts/rule.py STAGES`): `stage1` the rest cells, `stage2` the
  inactive cells; `fit` both, `rest-of-fit` what a label has not rendered. A scope's cells are the
  dark T1 gate cells of its pose (no referee, no holdout, every probe scene inside the planner's
  pre-gate whitelist) PLUS L1's declared population of that pose (the dark calibration and validation
  scenes), so L1 — the transmission's guard (X61) — is read at every fit point. A summary keys its
  cells `<scale>x <scene>`.
- **The identity** is the snapshots', not the live profiles' (X62): dark endpoints the snapshot's on
  every leaf but the declared overrides; light endpoints patch- and digest-identical to the light
  snapshots (X60).
- **The objective and the within clause** are W46's rule's (`rule.stage_objective`, `stage_within`,
  both scales pooled); the stage tie is computed ONCE from the published reference rows
  (`stage_tie_of`): `native` and `bar` are the cell's, so the tie's cell set is the stage's declared
  cells and never what a point happened to render (the W44 tracker note on the tie's cells).

W45's text follows, unchanged in substance where it still applies: build a candidate, render it on
the fit cells, read T1 and every cut against the reference (W46's `cuts/cuts.py`); every candidate's
documents, identity check and cuts are committed under G1's `fit/candidates/<label>/`; every launch
is logged in G1's `fit/runs.jsonl` with its compare log under `fit/logs/`; matrices and PNGs stay on
the machine. A content twin (`aliases.json`) MEASURES a point and never replaces its overrides; a
render of a scope draws only the cells the label has not rendered; a census refusal is told apart
from a partial matrix (exit 3).
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
sys.path.insert(0, str(HERE.parent))
import bindings as W  # noqa: E402

CAL, ROOT, G1 = W.CAL, W.ROOT, W.G1_FIT
SCRATCH = W.FIT_SCRATCH
PROFILE = W.PROFILE
SCALES = (1, 2)
SETS = "calibration,validation,recorded,probe"
SLOTS = W.MOVING_SLOTS
# The cell scopes (Design "The moves"): a stage is read on its pose's cells. Part 2's families name
# one of these as their scope (default: the stage's id).
SCOPES = {"stage1": dict(pose="rest"), "stage2": dict(pose="inactive")}
ALL_SCOPES = tuple(SCOPES)
STARTS = ("d0219",)
LABELS = json.loads((HERE / "labels.json").read_text())

_part2 = None
_declared = None
_ties: dict = {}


def now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def sha(data: bytes) -> str:
    return W.sha(data)


def aliases() -> dict:
    path = G1 / "aliases.json"
    return json.loads(path.read_text()) if path.exists() else {}


def record_alias(label: str, twin: str) -> None:
    table = aliases()
    if table.get(label, twin) != twin:
        raise W.Refusal(f"{label} is measured by {table[label]} already, not {twin}")
    if twin in table:
        raise W.Refusal(f"{twin} is itself measured by {table[twin]}; an alias names a rendered point")
    table[label] = twin
    G1.mkdir(parents=True, exist_ok=True)
    (G1 / "aliases.json").write_text(json.dumps(dict(sorted(table.items())), indent=1) + "\n")


def measured_label(label: str) -> str:
    """The label whose renders and cuts a point is read off: its content twin, or itself."""
    return aliases().get(label, label)


def log(row):
    G1.mkdir(parents=True, exist_ok=True)
    with (G1 / "runs.jsonl").open("a") as f:
        f.write(json.dumps(row, sort_keys=True) + "\n")


def cuts():
    """(bed, t1, rule) — W46's bed and rule, W44 G1's t1 shared by path."""
    return W.load_cuts()


def rule():
    return cuts()[2]


# ---------------------------------------------------------------------------------------------
# What part 2 declares
# ---------------------------------------------------------------------------------------------
def part2() -> dict:
    global _part2
    if _part2 is None:
        W.require_part(2)
        _part2 = json.loads(W.PART2.read_text())
    return _part2


def declared_leaves(body: dict) -> dict:
    """(slot, leaf) -> spec for every leaf part 2 lets a stage change: the searched leaves (a tied
    pair as both) and the families' fixed values."""
    out = {}
    for move in body["moves"]:
        for fam, fbody in move["families"].items():
            for key, spec in fbody.get("leaves", {}).items():
                for leaf in key.split("+"):
                    out[(spec["slot"], leaf)] = dict(spec, move=move["id"], family=fam)
            for leaf, spec in fbody.get("fixed", {}).items():
                out.setdefault((spec["slot"], leaf), dict(spec, move=move["id"], family=fam, fixedOnly=True))
    return out


def declared() -> dict:
    global _declared
    if _declared is None:
        _declared = declared_leaves(part2())
    return _declared


def snapshot_patch(slot: str) -> dict:
    return W.document(slot)["patch"]


def get_path(patch: dict, leaf: str):
    node = patch
    for part in leaf.split("."):
        if not isinstance(node, dict) or part not in node:
            return None
        node = node[part]
    return node


def active_value(overrides: dict, leaf: str):
    """The active dark value of `leaf`: the override, else the snapshot's, else X64's inherited value
    (the runtime default), else 0 (every other leaf a relative domain could name defaults to 0)."""
    if leaf in overrides.get("active.dark", {}):
        return overrides["active.dark"][leaf]
    got = get_path(snapshot_patch("active.dark"), leaf)
    if got is not None:
        return got
    return W.X64["active.dark"].get(leaf, 0)


def resolved_value(overrides: dict, slot: str, leaf: str):
    """The value of `leaf` the candidate resolves to in `slot`: the active as `active_value`; the
    receded its own override, else its snapshot's, else the active value (the receded document is a
    difference over its active document)."""
    if slot == "active.dark":
        return active_value(overrides, leaf)
    if slot != "receded.dark":
        raise W.Refusal(f"fit: {slot} is not a slot W46 moves (X60)")
    if leaf in overrides.get(slot, {}):
        return overrides[slot][leaf]
    got = get_path(snapshot_patch("receded.dark"), leaf)
    return got if got is not None else active_value(overrides, leaf)


def inherited(overrides: dict, slot: str, leaf: str):
    """What an X64 key resolves to in `slot` when the slot does NOT name it: the active's resolved
    value for the receded, the runtime default for the active. None for a leaf X64 does not list."""
    if leaf not in W.X64.get(slot, {}):
        return None
    if slot == "active.dark":
        return W.X64["active.dark"][leaf]
    rest = {s: {k: v for k, v in leaves.items() if not (s == slot and k == leaf)} for s, leaves in overrides.items()}
    return active_value(rest, leaf)


def materialise_x64(overrides: dict, slot: str) -> dict:
    """`overrides` with every X64 key of `slot` it does not name stated at its inherited value: the
    unchanged start stage 2 holds or moves each from (Design "The moves", X64)."""
    out = json.loads(json.dumps(overrides))
    for leaf in W.X64[slot]:
        if leaf not in out.get(slot, {}):
            out.setdefault(slot, {})[leaf] = inherited(out, slot, leaf)
    return out


def check_overrides(overrides: dict, table: dict | None = None) -> None:
    """Refuse an override part 2 does not declare, a value outside its declared domain, or a point
    outside a declared JOINT domain. An X64 key at its inherited value is never a move."""
    table = declared() if table is None else table
    for slot, leaves in overrides.items():
        if slot not in SLOTS:
            raise W.Refusal(f"fit: {slot} is not a slot W46 moves (the light material never moves; X60)")
        for leaf, value in leaves.items():
            spec = table.get((slot, leaf))
            if spec is None:
                if inherited(overrides, slot, leaf) == value:
                    continue
                raise W.Refusal(f"fit: {slot} {leaf} is not a leaf part 2 declares (clause 5)")
            if spec.get("fixedOnly"):
                if value != spec["value"]:
                    raise W.Refusal(f"fit: {slot} {leaf} is held at {spec['value']} by part 2, not {value}")
                continue
            lo, hi = domain_of(spec, overrides, leaf)
            if not lo <= value <= hi or (spec.get("domainOpenAt") is not None and value == spec["domainOpenAt"]):
                raise W.Refusal(f"fit: {slot} {leaf} {value} is outside its declared domain [{lo}, {hi}]")
    failures = joint_domain_failures(overrides, table)
    if failures:
        raise W.Refusal("fit: " + "; ".join(failures))


def domain_of(spec: dict, overrides: dict, leaf: str) -> tuple[float, float]:
    lo, hi = spec["domain"]
    if spec.get("domainRelativeTo"):
        active = active_value(overrides, leaf)
        lo, hi = sorted((lo * active, hi * active))
    return lo, hi


JOINT_TOLERANCE = 1e-9


def joint_domain_failures(overrides: dict, table: dict | None = None) -> list[str]:
    """A leaf whose part-2 spec names `domainLowerIsMinus: <other>` lies in [−other, 0] at the point's
    own slot, both resolved there (W45 part 2's second amendment, kept)."""
    table = declared() if table is None else table
    out = []
    for (slot, leaf), spec in sorted(table.items()):
        other = spec.get("domainLowerIsMinus")
        if other is None:
            continue
        value, bound = resolved_value(overrides, slot, leaf), resolved_value(overrides, slot, other)
        if value < -bound - JOINT_TOLERANCE:
            out.append(f"{slot} {leaf} {value:g} is outside its joint domain [−{other}, 0] = [{-bound:g}, 0]")
    return out


def in_joint_domain(overrides: dict) -> bool:
    return not joint_domain_failures(overrides)


def scope_of(move: dict, family: str) -> str:
    fbody = move["families"][family]
    scope = fbody.get("scope") or move.get("scope") or move["id"]
    if scope not in SCOPES:
        raise W.Refusal(f"part 2 {move['id']}/{family}: scope {scope!r} is not one of {sorted(SCOPES)}")
    return scope


def in_scope(c, scope: str) -> bool:
    """A rule-scope cell (dark WebGPU gate) of a stage's pose."""
    r = rule()
    return r.in_scope(c) and c["pose"] == SCOPES[scope]["pose"]


def cell_key(c) -> str:
    return f"{c['scale']}x {c['scene']}"


def l1_population(pose: str | None = None) -> list[str]:
    """L1's declared population on a dark profile (the calibration and validation scenes), by pose."""
    B, t1, _ = cuts()
    return sorted(sid for sid in B.SCENES.declared(PROFILE[2]) if B.SCENES.role[sid] in ("calibration", "validation")
                  and (pose is None or t1.pose(sid) == pose))


def scenes_for(scope: str, scale: int = 2) -> list[str]:
    """The fit cells of `scope` at `scale`: the dark T1 gate cells of the scope's pose (never a referee
    or holdout; every probe scene inside the planner's pre-gate whitelist) and L1's population of it."""
    B, t1, _ = cuts()
    plan = W.referee_plan()
    held = plan.referee_cells(plan.load_manifest())
    pregate = set(plan.lists()["pregateProbe"]["scenes"])
    if scope not in (*SCOPES, "fit", "rest-of-fit"):
        raise W.Refusal(f"scope {scope!r} is not one of {list(SCOPES) + ['fit', 'rest-of-fit']}")
    pose = SCOPES[scope]["pose"] if scope in SCOPES else None
    profile = PROFILE[scale]
    out = set()
    for p, sid in t1.population([profile]):
        if t1.partition(p, sid, held) != "gate" or (pose is not None and t1.pose(sid) != pose):
            continue
        if B.SCENES.role[sid] == "probe" and sid not in pregate:
            raise W.Refusal(f"{sid}: a probe scene outside the planner's pre-gate whitelist")
        out.add(sid)
    for sid in l1_population(pose):
        if (profile, sid) in held or B.SCENES.role[sid] == "holdout":
            raise W.Refusal(f"{sid}: an L1 scene withheld")
        out.add(sid)
    return sorted(out)


def selection_members(scope: str) -> list[str]:
    """The `<scale>x <scene>` keys of a scope's objective members (T1's F u C u P cells)."""
    _, t1, r = cuts()
    return [f"{s}x {sid}" for s in SCALES for sid in scenes_for(scope, s)
            if t1.B.SCENES.by_id[sid]["background"] in t1.T1_BACKDROPS and t1.stratum(sid) in r.SELECTION_STRATA]


def stage_tie_of(scope: str) -> float:
    """The stage tie, ONCE, from the published reference rows: `rule.stage_tie` over the stage's
    declared cells (native and bar are the cell's; the candidate is not read)."""
    if scope not in _ties:
        B, t1, r = cuts()
        plan = W.referee_plan()
        held = plan.referee_cells(plan.load_manifest())
        rows = B.load_published(W.REFERENCE["dark"]).rows
        cut = t1.cut(rows, rows, W.DARK_025, t1.load_bars(), held, tiers=("webgpu",), partitions=("gate",))
        _ties[scope] = r.stage_tie(cut["cells"], scope)
    return _ties[scope]


def preflight() -> None:
    W.require_shared()
    W.refuse_other_wave_path(G1, "G1's evidence")
    W.refuse_other_wave_path(SCRATCH, "the fit scratch")
    problems = W.verify_documents()
    if problems:
        raise W.Refusal("fit REFUSES: the snapshots do not hold (X62): " + "; ".join(problems))
    W.require_part(2)
    got = subprocess.run([sys.executable, "-B", str(W.DECLARE), "check-fit"], capture_output=True,
                         text=True, cwd=W.G0)
    if got.returncode:
        raise W.Refusal("fit REFUSES: W46's declare.py check-fit fails:\n" + (got.stdout + got.stderr)[-2000:])


# ---------------------------------------------------------------------------------------------
# Build
# ---------------------------------------------------------------------------------------------
def write_spec(label: str, overrides: dict, note: str, stage: str, family: str, start: str) -> Path:
    if start not in STARTS:
        raise W.Refusal(f"fit: start {start!r} is not the declared starting point {STARTS}")
    check_overrides(overrides)
    path = G1 / "specs" / f"{label}.json"
    spec = dict(label=label, note=note, stage=stage, family=family, start=start, overrides=overrides)
    if path.exists():
        old = json.loads(path.read_text())
        if old["overrides"] != overrides:
            raise W.Refusal(f"fit: {label} exists with other overrides {old['overrides']}")
        return path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(spec, indent=2) + "\n")
    return path


def builder_env(root: Path) -> dict:
    env = dict(os.environ)
    env["W46_CANDIDATE_ROOT"] = str(W.refuse_other_wave_path(root, "the candidate root"))
    return env


def build(label: str) -> None:
    folder = G1 / "candidates" / label
    if (folder / "candidate.json").exists():
        return
    got = subprocess.run(["pnpm", "exec", "tsx", str(W.BUILDER), str(G1 / "specs" / f"{label}.json")],
                         cwd=CAL, capture_output=True, text=True, env=builder_env(G1 / "candidates"))
    log(dict(label=label, build=now(), exitCode=got.returncode))
    if got.returncode:
        raise W.Refusal(f"build {label}: {(got.stdout + got.stderr)[-800:]}")
    (folder / "identity.json").write_text(json.dumps(identity(label), indent=2) + "\n")


def leaves(node, prefix=""):
    if not isinstance(node, dict):
        return {prefix: node}
    out = {}
    for k, v in node.items():
        out.update(leaves(v, f"{prefix}.{k}" if prefix else k))
    return out


def identity(label: str, folder: Path | None = None, spec: dict | None = None) -> dict:
    """The candidate identity, checked against the SNAPSHOTS (X62): dark endpoints the snapshot's on
    every leaf but the spec's declared overrides; light endpoints patch- and digest-identical (X60)."""
    folder = folder or G1 / "candidates" / label
    spec = spec or json.loads((G1 / "specs" / f"{label}.json").read_text())
    out, ok = {}, True
    for slot in W.SLOTS:
        doc = json.loads((folder / f"{slot}.json").read_text())
        snap = W.document(slot)
        mine, theirs = leaves(doc["patch"]), leaves(snap["patch"])
        moved = sorted(k for k in set(mine) | set(theirs) if mine.get(k) != theirs.get(k))
        want = sorted(spec["overrides"].get(slot, {}))
        undeclared = [k for k in moved if k not in want]
        entry = dict(moved=moved, undeclared=undeclared, digest=doc["resolvedMaterialSha256"],
                     snapshotDigest=snap["resolvedMaterialSha256"],
                     snapshot=W.document_path(slot).name)
        if slot.endswith(".light"):
            entry["patchIdentical"] = doc["patch"] == snap["patch"]
            entry["digestIdentical"] = doc["resolvedMaterialSha256"] == snap["resolvedMaterialSha256"]
            ok &= entry["patchIdentical"] and entry["digestIdentical"]
        ok &= not undeclared
        out[slot] = entry
    if not ok:
        raise W.Refusal(f"identity {label}: {json.dumps(out)}")
    return dict(label=label, holds=True, endpoints=out)


def start(which: str = "d0219") -> str:
    """Build the declared starting point: the four snapshots, no override."""
    if which not in STARTS:
        raise W.Refusal(f"start {which!r} is not one of {STARTS}")
    label = f"start-{which}"
    write_spec(label, {}, "the declared starting point d0219cd684bf (Design \"The moves\")", "start", "start", which)
    build(label)
    return label


# ---------------------------------------------------------------------------------------------
# Render
# ---------------------------------------------------------------------------------------------
def rendered(label: str) -> dict:
    """scale -> the scenes the label's scratch renders hold, over every scope directory."""
    out = {s: set() for s in SCALES}
    root = SCRATCH / label
    for d in sorted(root.glob("*/matrix.json")) if root.exists() else []:
        scale = int(d.parent.name.rsplit("-", 1)[1].rstrip("x"))
        out[scale] |= {r["key"]["sceneId"] for r in json.loads(d.read_bytes())["cells"]}
    return out


def rendered_scopes(label: str) -> dict:
    """scope directory name -> its scenes (the summaries' record of what was read)."""
    root = SCRATCH / label
    return {d.parent.name: sorted(r["key"]["sceneId"] for r in json.loads(d.read_bytes())["cells"])
            for d in sorted(root.glob("*/matrix.json"))} if root.exists() else {}


def wanted(scope: str, scale: int) -> list[str]:
    return scenes_for("fit" if scope in ("fit", "rest-of-fit") else scope, scale)


def covered(label: str, scope: str) -> bool:
    have = rendered(label)
    return all(set(wanted(scope, s)) <= have[s] for s in SCALES)


def compare_argv(candidate: Path, scale: int, scenes: list[str], out: Path) -> list[str]:
    return ["pnpm", "run", "-s", "compare", "--", "--profile", PROFILE[scale], "--renderer", "webgpu",
            "--candidate-document", str(candidate.relative_to(CAL)), "--set", SETS,
            "--scene", ",".join(scenes), "--alpha", "--write-partial", "--out-matrix", str(out / "matrix.json")]


def render(label: str, scope: str) -> int:
    """Both scales of `scope` the label has not rendered, one launch per scale. Exit 0 (complete),
    1 (a partial matrix), 3 (the census or the pin refused before a launch), else the launch's."""
    candidate = W.refuse_other_wave_path(G1 / "candidates" / label / "candidate.json", "the candidate")
    if not candidate.exists():
        raise W.Refusal(f"render: {label} is not built")
    if label in aliases():
        raise W.Refusal(f"render: {label} is measured by {aliases()[label]}; render the twin")
    have = rendered(label)
    worst = 0
    for scale in SCALES:
        scenes = [s for s in wanted(scope, scale) if s not in have[scale]]
        if not scenes:
            continue
        out = W.refuse_other_wave_path(SCRATCH / label / f"{scope}-{scale}x", "the render's scratch")
        if (out / "matrix.json").exists():
            raise W.Refusal(f"render: {out} holds a matrix already; a scope directory is written once")
        out.mkdir(parents=True, exist_ok=True)
        run_label = f"{label}/{scope}-{scale}x"
        argv = compare_argv(candidate, scale, scenes, out)
        env = {k: v for k, v in os.environ.items() if not k.startswith("VITREA_")}
        env.update(VITREA_WEB_CAPTURES=str(out / "web-captures"))
        started = now()
        log(dict(label=run_label, started=started, scenes=len(scenes),
                 argv=[a if a != ",".join(scenes) else f"<{len(scenes)} scenes: {scope}>" for a in argv]))
        (G1 / "logs").mkdir(parents=True, exist_ok=True)
        log_path = G1 / "logs" / f"{label}__{scope}-{scale}x.txt"
        with log_path.open("x") as f:
            result = subprocess.run([str(W.WITH_GPU), f"w46-fit {run_label}", *argv], cwd=CAL, env=env,
                                    stdout=f, stderr=subprocess.STDOUT)
        code = result.returncode
        if code == 1 and census_refused(log_path):
            code = 3
        log(dict(label=run_label, started=started, completed=now(), exitCode=code))
        print(run_label, "exit", code, len(scenes), "cells", flush=True)
        if code not in (0, 1):
            return code
        worst = max(worst, code)
    return worst


def census_refused(log_path: Path) -> bool:
    first = log_path.read_text().splitlines()[:1]
    return bool(first) and first[0].startswith("census ") and ": REFUSES" in first[0]


# ---------------------------------------------------------------------------------------------
# Read
# ---------------------------------------------------------------------------------------------
def read(label: str) -> dict:
    """W46's cuts.py on every scope directory the label has, against the reference; writes cuts.txt,
    cuts.json.gz and summary.json under candidates/<label>/ (a re-read replaces them)."""
    folder = G1 / "candidates" / label
    scopes = rendered_scopes(label)
    if not scopes:
        raise W.Refusal(f"read {label}: nothing rendered")
    merged = SCRATCH / label / "merged-captures"
    merged.mkdir(exist_ok=True)
    for name in scopes:
        tree = SCRATCH / label / name / "web-captures"
        for prof in tree.iterdir() if tree.exists() else []:
            for cell in prof.iterdir():
                (merged / prof.name / cell.name).mkdir(parents=True, exist_ok=True)
                for f in cell.iterdir():
                    link = merged / prof.name / cell.name / f.name
                    if not link.exists():
                        os.link(f, link)
    out_json, out_txt = SCRATCH / label / "cuts.json", SCRATCH / label / "cuts.txt"
    for f in (out_json, out_txt):
        f.unlink(missing_ok=True)
    argv = [sys.executable, "-B", str(W.CUTS / "cuts.py"), "--kind", "candidate",
            "--candidate-document", str((folder / "candidate.json").relative_to(ROOT))]
    for name in scopes:
        argv += ["--bed", str(SCRATCH / label / name / "matrix.json")]
    argv += ["--captures", str(merged), "--out", str(out_json), "--text", str(out_txt)]
    got = subprocess.run(argv, capture_output=True, text=True, cwd=W.CUTS)
    if got.returncode:
        raise W.Refusal(f"read {label}: cuts.py exit {got.returncode}: {got.stderr[-1500:]}")
    result = json.loads(out_json.read_bytes())
    (folder / "cuts.txt").write_text(out_txt.read_text())
    with gzip.open(folder / "cuts.json.gz", "wt") as f:
        json.dump(result, f)
    summary = summarise(label, result, scopes)
    (folder / "summary.json").write_text(json.dumps(summary, indent=1) + "\n")
    return summary


def stage_reading(cells, missing, scope: str) -> dict:
    """A scope's objective, tie and within clause, through W46's rule (both scales pooled)."""
    r = rule()
    clause = r.stage_within(cells, scope, [m for m in missing if m["pose"] == SCOPES[scope]["pose"]])
    return dict(objective=r.stage_objective(cells, scope), tie=stage_tie_of(scope),
                within=clause["verdict"], notWithin=clause["notWithin"], unmeasured=len(clause["unmeasured"]))


def summarise(label, result, scopes) -> dict:
    r = rule()
    t = result["T1"]
    cells = [c for c in t["cells"] if r.in_scope(c)]
    spec = json.loads((G1 / "specs" / f"{label}.json").read_text())
    per_cell = {}
    for c in cells:
        entry = dict(stratum=c["stratum"], pose=c["pose"], span=c["spanClass"], scale=c["scale"], n=c["native"],
                     c=c["reference"], k=c["candidate"], fidelity=c["fidelity"], change=c["change"],
                     growth=c["growth"], B=c["B"])
        if "bands" in c:
            entry["bands"] = {b: {k: c["bands"][b][k] for k in ("native", "reference", "candidate",
                                                                "fidelity", "change", "growth", "B")}
                              for b in ("fine", "low")}
        per_cell[cell_key(c)] = entry
    stages = {scope: stage_reading(t["cells"], [m for m in t.get("missing", ()) if r.in_scope(m)], scope)
              for scope in ALL_SCOPES}
    l1 = result.get("L1", {}).get("webgpu", {})
    return dict(
        label=label, stage=spec["stage"], family=spec["family"], start=spec["start"], overrides=spec["overrides"],
        scopes={k: len(v) for k, v in scopes.items()},
        declarationSha256=sha((G1 / "candidates" / label / "candidate.json").read_bytes()),
        stages=stages, selectionMetric=t["selectionMetric"], rule=t.get("rule", {}).get("verdict"),
        ruleProfiles={p: v["verdict"] for p, v in t.get("rule", {}).get("profiles", {}).items()},
        L1=dict(verdict=l1.get("verdict"), maxError=l1.get("maxError"), maxGrowth=l1.get("maxGrowth"),
                absoluteMisses=[c["cell"] for c in l1.get("absoluteMisses", [])],
                growthMisses=[c["cell"] for c in l1.get("growthMisses", [])]),
        verdicts=result["summary"], cells=per_cell)


def point(label, overrides, stage, family, start_, scope, note="") -> dict:
    """Spec, build, render the scope and read: memoized by label."""
    write_spec(label, overrides, note, stage, family, start_)
    build(label)
    name = measured_label(label)
    code = render(name, scope)
    if code not in (0, 1):
        raise W.Refusal(f"{name}/{scope}: render exit {code}")
    summary = G1 / "candidates" / name / "summary.json"
    if summary.exists():
        s = json.loads(summary.read_text())
        if s["scopes"] == {k: len(v) for k, v in rendered_scopes(name).items()}:
            return s
    return read(name)


def parse_overrides(items) -> dict:
    out = {}
    for item in items:
        key, value = item.split("=")
        leaf, slot = key.split("@")
        out.setdefault(slot, {})[leaf] = float(value) if "." in value or "e" in value else int(value)
    return out


def main(argv) -> int:
    preflight()
    verb = argv[1] if len(argv) > 1 else ""
    opt = lambda name, default=None: argv[argv.index(name) + 1] if name in argv else default  # noqa: E731
    if verb == "start":
        print(start())
        return 0
    if verb == "point":
        label = argv[2]
        rest = [a for a in argv[3:] if "@" in a and "=" in a]
        s = point(label, parse_overrides(rest), opt("--stage"), opt("--family"), "d0219",
                  opt("--scope", "fit"), opt("--note", ""))
        print(json.dumps({k: s[k] for k in ("label", "stages", "selectionMetric", "rule", "L1")}, indent=1))
        return 0
    if verb == "render":
        return render(measured_label(argv[2]), opt("--scope"))
    if verb == "read":
        s = read(measured_label(argv[2]))
        print(json.dumps({k: s[k] for k in ("label", "stages", "selectionMetric", "rule", "L1")}, indent=1))
        return 0
    print(__doc__)
    return 64


if __name__ == "__main__":
    sys.exit(main(sys.argv))
