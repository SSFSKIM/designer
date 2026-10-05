#!/usr/bin/env python3.12
"""W46 G0 (a): the fit's measuring loop, W45 G0's (`results/2026-10-03-w45-g0-operator/fit/fit.py`)
ported for W46 (charter clauses 1 and 5; Design "The moves"; X60, X62, X64). W45's committed copy is
untouched. G1 runs it; G0 commits it, tested, before part 2 exists.

    python3.12 -B fit.py start                     build the declared starting point (`start-d0219`)
    python3.12 -B fit.py point <label> --stage S --family F [--scope S] [--note N] leaf@slot=value ...
    python3.12 -B fit.py render <label> --scope S  (one more scope of a built point, on its renderers)
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
- **Both scales, every point, rendered SCALE-SEPARABLY** (the parent's ruling for stage 1's factorial
  over 1x and 2x leaves). The targets are read at 1x and 2x (Decision Log 3, per profile), but a leaf
  acts at one scale or both (`labels.json` "scales"; `rampAtScale` anchors every 1x/2x pair), so a
  point's render at scale s is the render of its SCALE TWIN — the candidate of its overrides
  restricted to the leaves acting at s, non-moves dropped — and twins of one lineage whose four
  resolved digests are equal share that scale's render (`scale-aliases.json`, keyed `<twin> <s>x`).
  Each renderer is read at its scale (`read_scale`: W46's cuts on its own matrices, its own candidate
  document), and a point's summary is COMPOSED from its two scales' readings, wherever they were
  rendered (`compose`): its stages, objective and W46's rule are evaluated on the union. A 1x lever ×
  2x lever factorial thus renders (#1x values) + (#2x values) scale contents, not their product. The
  decision is exact only under the scale anchoring, which W46's ladders verify by rendering every
  lever at both scales (the scale a lever does not act at byte-identical to the control's). Every
  launch is one dark profile, `--alpha --write-partial`, through `../with-gpu.sh` (the GPU lock, the
  classifying census and the browser pin), into `~/vitrea-w46/g1-scratch/fit/<renderer>/<scope>-<s>x/`.
  W45's label-level content aliasing (`aliases.json`) is replaced by the per-scale one; W45's `x48`
  scope is gone: X60 is read by evidence on every candidate (`identity`: the light endpoints patch-
  and digest-identical to the light snapshots) and by render at the gate, which is G1's stage.
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
the machine. A renderer MEASURES a point's scale and never replaces its overrides; a render of a
scope draws only the cells the renderer has not rendered; a census refusal is told apart from a
partial matrix (exit 3).
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


def measured_label(label: str) -> str:
    """Kept for the readers' interface: since scale-separable rendering every point has its own
    summary, composed from the renders that measure it per scale (`renderer_of`)."""
    return label


# ---------------------------------------------------------------------------------------------
# Scale-separable rendering (the parent's ruling for W46's stage-1 factorial)
# ---------------------------------------------------------------------------------------------
# A leaf acts at 1x, at 2x or at both (`labels.json` "scales"): the renderer's `rampAtScale`
# anchors every `…1x`/`…2x` pair and every 2x-only leaf (`sizeScatterFloor2x`, `sizeHeavyTapSigma2x`,
# `sizeHeavySecondShareFar2x`, …) to its scale, so a 1x-anchored leaf moves no 2x pixel and a
# 2x-anchored leaf no 1x pixel (W45's X48: every W45 rung's 1x captures pixel-identical to its
# control's). A point's render at scale s is therefore the render of its SCALE TWIN, the candidate
# built from the point's overrides restricted to the leaves acting at s (a leaf at the snapshot's
# resolved value, an X64 key at its inherited value included, is not a move and is dropped). Scale
# twins of one lineage whose four resolved digests are equal draw equal pixels at that scale and
# share one render (`scale-aliases.json`, keyed `<twin> <s>x`). The decision is exact only under the
# scale anchoring, which W46's ladders verify by rendering every lever at both scales: the scale a
# lever does not act at must be byte-identical to the control's. A factorial of a 1x lever by a 2x
# lever then renders (#1x values) + (#2x values) scale contents, not their product.
def scales_of() -> dict:
    return LABELS["scales"]


def leaf_scale(leaf: str) -> str:
    got = scales_of().get(leaf)
    if got not in ("1x", "2x", "both"):
        raise W.Refusal(f"labels.json states no scale for {leaf}; a leaf with no scale is never rendered "
                        "scale-separably (and never searched)")
    return got


def acts_at(leaf: str, scale: int) -> bool:
    return leaf_scale(leaf) in ("both", f"{scale}x")


def scale_overrides(overrides: dict, scale: int) -> dict:
    """The point's overrides restricted to the leaves acting at `scale`, non-moves dropped."""
    out = {}
    for slot, leaves in overrides.items():
        for leaf, value in leaves.items():
            if not acts_at(leaf, scale) or resolved_value({}, slot, leaf) == value:
                continue
            out.setdefault(slot, {})[leaf] = value
    return out


def label_parts(overrides: dict, base: dict) -> list[str]:
    """The label grammar's parts (`labels.json`) for what `overrides` moves beyond `base`."""
    parts = []
    for slot, leaves in sorted(overrides.items()):
        for leaf, v in sorted(leaves.items()):
            if base.get(slot, {}).get(leaf) != v:
                if leaf not in LABELS["short"]:
                    raise W.Refusal(f"labels.json has no short name for {leaf}")
                parts.append(f"{LABELS['slotMark'][slot]}{LABELS['short'][leaf]}{round(v, 6):g}")
    return parts


def twin_label(start: str, scale: int, twin: dict) -> str:
    label = f"{LABELS['lineage'][start]}-x{scale}-" + ("-".join(label_parts(twin, {})) or "base")
    if not __import__("re").fullmatch(LABELS["pattern"], label):
        raise W.Refusal(f"scale twin label {label!r} is outside labels.json's pattern")
    return label


def scale_aliases() -> dict:
    path = G1 / "scale-aliases.json"
    return json.loads(path.read_text()) if path.exists() else {}


def record_scale_alias(twin: str, scale: int, renderer: str) -> None:
    table = scale_aliases()
    key = f"{twin} {scale}x"
    if table.get(key, renderer) != renderer:
        raise W.Refusal(f"{key} is rendered by {table[key]} already, not {renderer}")
    if f"{renderer} {scale}x" in table:
        raise W.Refusal(f"{renderer} is itself rendered by another at {scale}x; an alias names a renderer")
    table[key] = renderer
    G1.mkdir(parents=True, exist_ok=True)
    (G1 / "scale-aliases.json").write_text(json.dumps(dict(sorted(table.items())), indent=1) + "\n")


def content_of(label: str) -> tuple:
    folder = G1 / "candidates" / label
    return tuple(json.loads((folder / f"{slot}.json").read_text())["resolvedMaterialSha256"] for slot in W.SLOTS)


def is_renderer(label: str, scale: int) -> bool:
    """A scale twin that renders its own scale (it has a scale directory, or a scale summary)."""
    return ((SCRATCH / label).exists() and any((SCRATCH / label).glob(f"*-{scale}x/matrix.json"))) or \
        (G1 / "candidates" / label / f"scale-{scale}x.json").exists()


def scale_twin(label: str, scale: int, pending: dict | None = None) -> str:
    """The scale twin of a point, written and built (cheap), and the renderer that measures it at
    `scale`: itself, or an earlier twin of the lineage with equal resolved digests (rendered, or
    named earlier in the same batch through `pending`, scale content -> renderer)."""
    spec = json.loads((G1 / "specs" / f"{label}.json").read_text())
    twin = scale_overrides(spec["overrides"], scale)
    name = twin_label(spec["start"], scale, twin)
    path = G1 / "specs" / f"{name}.json"
    if path.exists():
        if json.loads(path.read_text())["overrides"] != twin:
            raise W.Refusal(f"scale twin {name} exists with other overrides")
    else:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(dict(label=name, note=f"the {scale}x scale twin", stage="scale-twin",
                                        family=f"{scale}x", start=spec["start"], scale=scale, overrides=twin),
                                   indent=2) + "\n")
    build(name)
    table = scale_aliases()
    key = f"{name} {scale}x"
    if key in table:
        return table[key]
    if is_renderer(name, scale):
        return name
    mine = content_of(name)
    for other in sorted((G1 / "specs").glob("*.json")):
        o = json.loads(other.read_text())
        if (o.get("stage") == "scale-twin" and o.get("scale") == scale and o["start"] == spec["start"]
                and o["label"] != name and is_renderer(o["label"], scale) and content_of(o["label"]) == mine):
            record_scale_alias(name, scale, o["label"])
            log(dict(label=name, scale=scale, renderedBy=o["label"], at=now()))
            return o["label"]
    if pending is not None:
        first = pending.setdefault((scale, mine), name)
        if first != name:
            record_scale_alias(name, scale, first)
            log(dict(label=name, scale=scale, renderedBy=first, at=now()))
            return first
    return name


def renderer_of(label: str, scale: int) -> str:
    """The renderer of a point's `scale`: its scale twin's renderer (built on demand)."""
    return scale_twin(label, scale)

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
# Render (per scale, on the renderer that measures a point's scale)
# ---------------------------------------------------------------------------------------------
def rendered(label: str) -> dict:
    """scale -> the scenes a RENDERER's scratch holds at that scale, over every scope directory."""
    out = {s: set() for s in SCALES}
    root = SCRATCH / label
    for d in sorted(root.glob("*/matrix.json")) if root.exists() else []:
        scale = int(d.parent.name.rsplit("-", 1)[1].rstrip("x"))
        out[scale] |= {r["key"]["sceneId"] for r in json.loads(d.read_bytes())["cells"]}
    return out


def rendered_scopes(label: str, scale: int | None = None) -> dict:
    """A renderer's scope directory name -> its scenes (at `scale`, or every scale)."""
    root = SCRATCH / label
    return {d.parent.name: sorted(r["key"]["sceneId"] for r in json.loads(d.read_bytes())["cells"])
            for d in sorted(root.glob("*/matrix.json"))
            if scale is None or d.parent.name.endswith(f"-{scale}x")} if root.exists() else {}


def wanted(scope: str, scale: int) -> list[str]:
    return scenes_for("fit" if scope in ("fit", "rest-of-fit") else scope, scale)


def covered(label: str, scope: str) -> bool:
    """Whether every scale of a POINT holds the scope's cells, on whichever renders measure it."""
    return all(set(wanted(scope, s)) <= rendered(renderer_of(label, s))[s] for s in SCALES)


def compare_argv(candidate: Path, scale: int, scenes: list[str], out: Path) -> list[str]:
    return ["pnpm", "run", "-s", "compare", "--", "--profile", PROFILE[scale], "--renderer", "webgpu",
            "--candidate-document", str(candidate.relative_to(CAL)), "--set", SETS,
            "--scene", ",".join(scenes), "--alpha", "--write-partial", "--out-matrix", str(out / "matrix.json")]


def render_scale(renderer: str, scope: str, scale: int) -> int:
    """One launch at `scale` of the scope's cells the renderer has not rendered. Exit 0 (complete or
    nothing to do), 1 (a partial matrix), 3 (the census or the pin refused before the launch)."""
    candidate = W.refuse_other_wave_path(G1 / "candidates" / renderer / "candidate.json", "the candidate")
    if not candidate.exists():
        raise W.Refusal(f"render: {renderer} is not built")
    spec = json.loads((G1 / "specs" / f"{renderer}.json").read_text())
    if spec.get("stage") != "scale-twin" or spec.get("scale") != scale:
        raise W.Refusal(f"render: {renderer} is not a {scale}x scale twin; a point renders through its twins")
    if f"{renderer} {scale}x" in scale_aliases():
        raise W.Refusal(f"render: {renderer} is rendered by {scale_aliases()[f'{renderer} {scale}x']} at {scale}x")
    scenes = [s for s in wanted(scope, scale) if s not in rendered(renderer)[scale]]
    if not scenes:
        return 0
    out = W.refuse_other_wave_path(SCRATCH / renderer / f"{scope}-{scale}x", "the render's scratch")
    if (out / "matrix.json").exists():
        raise W.Refusal(f"render: {out} holds a matrix already; a scope directory is written once")
    out.mkdir(parents=True, exist_ok=True)
    run_label = f"{renderer}/{scope}-{scale}x"
    argv = compare_argv(candidate, scale, scenes, out)
    env = {k: v for k, v in os.environ.items() if not k.startswith("VITREA_")}
    env.update(VITREA_WEB_CAPTURES=str(out / "web-captures"))
    started = now()
    log(dict(label=run_label, started=started, scenes=len(scenes),
             argv=[a if a != ",".join(scenes) else f"<{len(scenes)} scenes: {scope}>" for a in argv]))
    (G1 / "logs").mkdir(parents=True, exist_ok=True)
    log_path = G1 / "logs" / f"{renderer}__{scope}-{scale}x.txt"
    with log_path.open("x") as f:
        result = subprocess.run([str(W.WITH_GPU), f"w46-fit {run_label}", *argv], cwd=CAL, env=env,
                                stdout=f, stderr=subprocess.STDOUT)
    code = result.returncode
    if code == 1 and census_refused(log_path):
        code = 3
    log(dict(label=run_label, started=started, completed=now(), exitCode=code))
    print(run_label, "exit", code, len(scenes), "cells", flush=True)
    return code


def render(label: str, scope: str) -> int:
    """Both scales of a POINT, each on the renderer that measures it at that scale."""
    worst = 0
    for scale in SCALES:
        code = render_scale(renderer_of(label, scale), scope, scale)
        if code not in (0, 1):
            return code
        worst = max(worst, code)
    return worst


def census_refused(log_path: Path) -> bool:
    first = log_path.read_text().splitlines()[:1]
    return bool(first) and first[0].startswith("census ") and ": REFUSES" in first[0]


# ---------------------------------------------------------------------------------------------
# Read (per scale on the renderer, then composed per point)
# ---------------------------------------------------------------------------------------------
def scale_summary_path(renderer: str, scale: int) -> Path:
    return G1 / "candidates" / renderer / f"scale-{scale}x.json"


def scale_current(renderer: str, scale: int) -> bool:
    path = scale_summary_path(renderer, scale)
    return path.exists() and json.loads(path.read_text())["scopes"] == {
        k: len(v) for k, v in rendered_scopes(renderer, scale).items()}


def read_scale(renderer: str, scale: int) -> dict:
    """W46's cuts.py on a renderer's matrices at `scale` (its own candidate document), against the
    reference; keeps that scale's rule-scope T1 cells, their missing members and its L1 rows, and
    writes `cuts-<s>x.json.gz`, `cuts-<s>x.txt` and `scale-<s>x.json` under candidates/<renderer>/."""
    folder = G1 / "candidates" / renderer
    scopes = rendered_scopes(renderer, scale)
    if not scopes:
        raise W.Refusal(f"read {renderer} {scale}x: nothing rendered")
    merged = SCRATCH / renderer / f"merged-captures-{scale}x"
    merged.mkdir(exist_ok=True)
    for name in scopes:
        tree = SCRATCH / renderer / name / "web-captures"
        for prof in tree.iterdir() if tree.exists() else []:
            for cell in prof.iterdir():
                (merged / prof.name / cell.name).mkdir(parents=True, exist_ok=True)
                for f in cell.iterdir():
                    link = merged / prof.name / cell.name / f.name
                    if not link.exists():
                        os.link(f, link)
    out_json, out_txt = SCRATCH / renderer / f"cuts-{scale}x.json", SCRATCH / renderer / f"cuts-{scale}x.txt"
    for f in (out_json, out_txt):
        f.unlink(missing_ok=True)
    argv = [sys.executable, "-B", str(W.CUTS / "cuts.py"), "--kind", "candidate",
            "--candidate-document", str((folder / "candidate.json").relative_to(ROOT))]
    for name in scopes:
        argv += ["--bed", str(SCRATCH / renderer / name / "matrix.json")]
    argv += ["--captures", str(merged), "--out", str(out_json), "--text", str(out_txt)]
    got = subprocess.run(argv, capture_output=True, text=True, cwd=W.CUTS)
    if got.returncode:
        raise W.Refusal(f"read {renderer} {scale}x: cuts.py exit {got.returncode}: {got.stderr[-1500:]}")
    result = json.loads(out_json.read_bytes())
    (folder / f"cuts-{scale}x.txt").write_text(out_txt.read_text())
    with gzip.open(folder / f"cuts-{scale}x.json.gz", "wt") as f:
        json.dump(result, f)
    profile = PROFILE[scale]
    r = rule()
    t = result["T1"]
    l1 = result.get("L1", {}).get("webgpu", {})
    mine = lambda c: c["cell"].startswith(profile + "/") or c["cell"].startswith(profile + " ")  # noqa: E731
    body = dict(renderer=renderer, scale=scale, profile=profile, scopes={k: len(v) for k, v in scopes.items()},
                declarationSha256=sha((folder / "candidate.json").read_bytes()),
                cells=[c for c in t["cells"] if r.in_scope(c) and c["profile"] == profile],
                missing=[m for m in t.get("missing", ()) if r.in_scope(m) and m["profile"] == profile],
                L1=dict(absoluteMisses=[c["cell"] for c in l1.get("absoluteMisses", []) if mine(c)],
                        growthMisses=[c["cell"] for c in l1.get("growthMisses", []) if mine(c)],
                        unmeasured=[c for c in l1.get("unmeasured", []) if c.startswith(profile)]),
                verdicts={k: v for k, v in result["summary"].items()})
    scale_summary_path(renderer, scale).write_text(json.dumps(body, indent=1) + "\n")
    return body


def stage_reading(cells, missing, scope: str) -> dict:
    """A scope's objective, tie and within clause, through W46's rule (both scales pooled)."""
    r = rule()
    clause = r.stage_within(cells, scope, [m for m in missing if m["pose"] == SCOPES[scope]["pose"]])
    return dict(objective=r.stage_objective(cells, scope), tie=stage_tie_of(scope),
                within=clause["verdict"], notWithin=clause["notWithin"], unmeasured=len(clause["unmeasured"]))


def compose(label: str) -> dict:
    """A point's summary from its two scales' readings, wherever they were rendered: the T1 cells of
    each scale off that scale's renderer, the stages and W46's rule evaluated on their union."""
    r = rule()
    spec = json.loads((G1 / "specs" / f"{label}.json").read_text())
    per = {}
    for scale in SCALES:
        renderer = renderer_of(label, scale)
        path = scale_summary_path(renderer, scale)
        if not path.exists():
            raise W.Refusal(f"compose {label}: {renderer} has no {scale}x reading")
        per[scale] = dict(renderer=renderer, body=json.loads(path.read_text()), sha=sha(path.read_bytes()))
    cells = [c for s in SCALES for c in per[s]["body"]["cells"]]
    missing = [m for s in SCALES for m in per[s]["body"]["missing"]]
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
    ruled = r.evaluate(cells, missing)
    return dict(
        label=label, stage=spec["stage"], family=spec["family"], start=spec["start"], overrides=spec["overrides"],
        renderers={f"{s}x": dict(label=per[s]["renderer"], scaleSummarySha256=per[s]["sha"],
                                 scopes=per[s]["body"]["scopes"]) for s in SCALES},
        declarationSha256=sha((G1 / "candidates" / label / "candidate.json").read_bytes()),
        stages={scope: stage_reading(cells, missing, scope) for scope in ALL_SCOPES},
        selectionMetric=r.selection_metric(cells), rule=ruled["verdict"],
        ruleProfiles={p: v["verdict"] for p, v in ruled["profiles"].items()},
        L1={f"{s}x": per[s]["body"]["L1"] for s in SCALES},
        verdicts={f"{s}x": per[s]["body"]["verdicts"] for s in SCALES},
        cells=per_cell, t1Cells=cells, t1Missing=missing)


def summary_current(label: str) -> bool:
    path = G1 / "candidates" / label / "summary.json"
    if not path.exists():
        return False
    s = json.loads(path.read_text())
    for scale in SCALES:
        renderer = renderer_of(label, scale)
        got = s.get("renderers", {}).get(f"{scale}x", {})
        p = scale_summary_path(renderer, scale)
        if got.get("label") != renderer or not scale_current(renderer, scale) or \
                got.get("scaleSummarySha256") != sha(p.read_bytes()):
            return False
    return True


def read(label: str) -> dict:
    """A point's reading: each scale's renderer read if its reading is stale, then composed."""
    for scale in SCALES:
        renderer = renderer_of(label, scale)
        if not scale_current(renderer, scale):
            read_scale(renderer, scale)
    summary = compose(label)
    (G1 / "candidates" / label / "summary.json").write_text(json.dumps(summary, indent=1) + "\n")
    return summary


def point(label, overrides, stage, family, start_, scope, note="") -> dict:
    """Spec, build, render the scope on each scale's renderer, and read: memoized by label."""
    write_spec(label, overrides, note, stage, family, start_)
    build(label)
    code = render(label, scope)
    if code not in (0, 1):
        raise W.Refusal(f"{label}/{scope}: render exit {code}")
    if summary_current(label):
        return json.loads((G1 / "candidates" / label / "summary.json").read_text())
    return read(label)



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
        return render(argv[2], opt("--scope"))
    if verb == "read":
        s = read(argv[2])
        print(json.dumps({k: s[k] for k in ("label", "stages", "selectionMetric", "rule", "L1")}, indent=1))
        return 0
    print(__doc__)
    return 64


if __name__ == "__main__":
    sys.exit(main(sys.argv))
