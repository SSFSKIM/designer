#!/usr/bin/env python3.12
"""W45 G0 (b): the fit's measuring loop, W44 G1's (`results/2026-10-03-w44-g1-refit/fit/fit.py`) ported
for W45 (charter clauses 2 and 5, Decision Logs 2 and 4, X56, X58). W44's committed copy is
untouched. G1 runs it; G0 commits it, tested, before part 2 exists.

Build a candidate (W45's `build-candidate.ts`), render it on the fit cells, read T1 and every cut
against the c05 reference (W45's `cuts/cuts.py`). Every candidate's documents, identity check and
cuts are committed under G1's `fit/candidates/<label>/`; every launch is logged in G1's
`fit/runs.jsonl` with its compare log under `fit/logs/`; matrices and PNGs stay on the machine
under `~/vitrea-w45/g1-scratch/fit/<label>/<scope>/`.

    python3.12 -B fit.py start c05|joint            build a declared starting point (Decision Log 4)
    python3.12 -B fit.py point <label> --stage S --family F --start c05|joint [--scope S] [--note N] leaf@slot=value ...
    python3.12 -B fit.py render <label> --scope S   (one more scope of a built candidate)
    python3.12 -B fit.py read <label>

**What W45 changes from W44's driver, each a refusal rather than a convention:**
- **W45's part 2, by W45's hash.** The declared leaves, domains and grids are read from W45's
  `fit-declaration.json`, and nothing runs until it is hashed (`fit-declaration.sha256`'s last
  line), the file on disk is those bytes, it names W45's charter, and W45's `declare.py check-fit`
  passes. A W44 part hash is refused wherever W45's is expected (`bindings`).
- **The operator's key and the span top.** `check_overrides` admits exactly the (slot, leaf) pairs
  part 2 declares — `sizeHeavySecondShareFar2x` in `active.light` and in `receded.light`,
  `sizeScatterSpanMax2x` in `active.light` among them where part 2 declares them — inside their
  domains; never a dark slot, never an undeclared leaf.
- **Two starting points** (Decision Log 4, X56). `start c05` builds c05 itself under the scratch key
  (`start-c05`, no override); `start joint` builds W44's joint point (`start-joint`) from W44 G1's
  committed spec, admitted only when W44's committed `candidate.json` hashes to the declared
  `66bf5a01…` and W45's builder reproduces each of its four endpoint patches. Every point records
  its lineage (`start`), and a point's spec names its stage and family.
- **The scopes are the charter's stages** (Design "The moves"): `stage1` the rest mid and thick
  cells (span 96 and 128-160), `stage2-thin` the rest thin cells, `stage2-receded` every inactive
  cell (W44's moves 2 and 3), `fit` all of them, `rest-of-fit` and `x48` (the 1x light T1 gate
  cells, for X48's byte identity). Each is the gate partition of the 2x light WebGPU T1 cells: no
  referee, no holdout, and every probe scene in the planner's pre-gate whitelist.
- **Every fit render passes `--alpha`** (clause 5: a fit row equals a stage row; W44 G1's tracker
  note), and runs through `with-gpu.sh` (the GPU lock and the classifying census, §5.201 §21).
- **W44's evidence, scratch and stage are refused** as a place to read a render from or write to.

Unchanged from W44: the candidate identity (dark endpoints patch- and digest-identical to c05's,
light endpoints c05's on every leaf but the declared overrides, the 1x second width at 0); the
objective (T1's selection metric over the scope's F u C u P cells); the within clauses (stage 1:
every F and pitch-16 cell of the scope; stage 2: every F, C and P cell of the scope).
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
sys.path.insert(0, str(HERE))
import bindings as W  # noqa: E402

CAL, ROOT, G1 = W.CAL, W.ROOT, W.G1_FIT
SCRATCH = W.FIT_SCRATCH
PROFILE = W.PROFILE
SETS = "calibration,validation,recorded,probe"
SLOTS = ("active.light", "receded.light")
# The charter's stages as cell scopes (Design "The moves"): pose and span classes.
SCOPES = {"stage1": dict(pose="rest", spans=("mid", "thick"), within="F+pitch16"),
          "stage2-thin": dict(pose="rest", spans=("thin",), within="FCP"),
          "stage2-receded": dict(pose="inactive", spans=None, within="FCP")}
STARTS = ("c05", "joint")

_part2 = None
_declared = None


def now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def sha(data: bytes) -> str:
    return W.sha(data)


def log(row):
    G1.mkdir(parents=True, exist_ok=True)
    with (G1 / "runs.jsonl").open("a") as f:
        f.write(json.dumps(row, sort_keys=True) + "\n")


def cuts():
    return W.load_cuts()


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


def check_overrides(overrides: dict, table: dict | None = None) -> None:
    """Refuse an override part 2 does not declare, or a value outside its declared domain."""
    table = declared() if table is None else table
    for slot, leaves in overrides.items():
        if slot not in SLOTS:
            raise W.Refusal(f"fit: {slot} is not a slot part 2 moves (the dark endpoints never move; X48)")
        for leaf, value in leaves.items():
            spec = table.get((slot, leaf))
            if spec is None:
                raise W.Refusal(f"fit: {slot} {leaf} is not a leaf part 2 declares (clause 5)")
            if spec.get("fixedOnly"):
                if value != spec["value"]:
                    raise W.Refusal(f"fit: {slot} {leaf} is held at {spec['value']} by part 2, not {value}")
                continue
            lo, hi = spec["domain"]
            if spec.get("domainRelativeTo"):
                active = overrides.get("active.light", {}).get(leaf, 0)
                lo, hi = sorted((lo * active, hi * active))
            if not lo <= value <= hi or (spec.get("domainOpenAt") is not None and value == spec["domainOpenAt"]):
                raise W.Refusal(f"fit: {slot} {leaf} {value} is outside its declared domain [{lo}, {hi}]")


def scope_of(move: dict, family: str) -> str:
    """The cell scope a part-2 family is searched on: the family's `scope`, else the move's, else
    the move id; one of `SCOPES`."""
    fbody = move["families"][family]
    scope = fbody.get("scope") or move.get("scope") or move["id"]
    if scope not in SCOPES:
        raise W.Refusal(f"part 2 {move['id']}/{family}: scope {scope!r} is not one of {sorted(SCOPES)}")
    return scope


def in_scope(c, scope: str) -> bool:
    _, t1 = cuts()
    s = SCOPES[scope]
    return (t1.in_landing_scope(c) and c["pose"] == s["pose"]
            and (s["spans"] is None or c["spanClass"] in s["spans"]))


def scenes_for(scope: str, scale: int = 2) -> list[str]:
    """The fit cells of `scope` at `scale`: light T1 gate cells (never a referee or holdout), every
    probe scene among them inside the planner's pre-gate whitelist."""
    B, t1 = cuts()
    plan = W.referee_plan()
    held = plan.referee_cells(plan.load_manifest())
    pregate = set(plan.lists()["pregateProbe"]["scenes"])
    profile = PROFILE[scale]
    out = []
    for p, sid in t1.population([profile]):
        if t1.partition(p, sid, held) != "gate":
            continue
        if scope in SCOPES:
            s = SCOPES[scope]
            if t1.pose(sid) != s["pose"] or (s["spans"] is not None and t1.span_class(sid) not in s["spans"]):
                continue
        elif scope not in ("fit", "x48", "rest-of-fit"):
            raise W.Refusal(f"scope {scope!r} is not one of {sorted(SCOPES) + ['fit', 'rest-of-fit', 'x48']}")
        if B.SCENES.role[sid] == "probe" and sid not in pregate:
            raise W.Refusal(f"{sid}: a probe scene outside the planner's pre-gate whitelist")
        out.append(sid)
    return sorted(out)


def preflight() -> None:
    W.require_shared()
    W.refuse_w44_path(G1, "G1's evidence")
    W.refuse_w44_path(SCRATCH, "the fit scratch")
    W.require_part(2)
    got = subprocess.run([sys.executable, "-B", str(W.DECLARE), "check-fit"], capture_output=True,
                         text=True, cwd=W.G0)
    if got.returncode:
        raise W.Refusal("fit REFUSES: W45's declare.py check-fit fails:\n" + (got.stdout + got.stderr)[-2000:])


# ---------------------------------------------------------------------------------------------
# Build
# ---------------------------------------------------------------------------------------------
def write_spec(label: str, overrides: dict, note: str, stage: str, family: str, start: str) -> Path:
    if start not in STARTS:
        raise W.Refusal(f"fit: start {start!r} is not a declared starting point {STARTS}")
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
    env["W45_CANDIDATE_ROOT"] = str(W.refuse_w44_path(root, "the candidate root"))
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
    """The candidate identity, checked: dark endpoints patch- and digest-identical to c05's; light
    endpoints c05's on every leaf but the spec's declared overrides; the 1x second width at 0."""
    folder = folder or G1 / "candidates" / label
    spec = spec or json.loads((G1 / "specs" / f"{label}.json").read_text())
    out, ok = {}, True
    for slot in ("active.light", "active.dark", "receded.light", "receded.dark"):
        pose, scheme = slot.split(".")
        doc = json.loads((folder / f"{slot}.json").read_text())
        c05 = json.loads((CAL / "profiles" / f"apple-macos-27.0-1x-{scheme}-standard-glass0.25"
                          f"{'-receded' if pose == 'receded' else ''}.json").read_text())
        mine, theirs = leaves(doc["patch"]), leaves(c05["patch"])
        moved = sorted(k for k in set(mine) | set(theirs) if mine.get(k) != theirs.get(k))
        want = sorted(spec["overrides"].get(slot, {}))
        undeclared = [k for k in moved if k not in want]
        entry = dict(moved=moved, undeclared=undeclared, digest=doc["resolvedMaterialSha256"],
                     c05Digest=c05["resolvedMaterialSha256"])
        if scheme == "dark":
            entry["patchIdentical"] = doc["patch"] == c05["patch"]
            entry["digestIdentical"] = doc["resolvedMaterialSha256"] == c05["resolvedMaterialSha256"]
            ok &= entry["patchIdentical"] and entry["digestIdentical"]
        entry["secondTap1xWidth"] = mine.get("sizeHeavySecondSigma", 0)
        ok &= not undeclared and entry["secondTap1xWidth"] == 0
        out[slot] = entry
    if not ok:
        raise W.Refusal(f"identity {label}: {json.dumps(out)}")
    return dict(label=label, holds=True, endpoints=out)


def joint_overrides() -> dict:
    """W44's joint point (Decision Log 4, X56): its committed spec's overrides, admitted only when
    W44's committed declaration hashes to the declared `66bf5a01…`."""
    got = sha(W.JOINT["candidate"].read_bytes())
    if got != W.JOINT["declarationSha256"]:
        raise W.Refusal(f"the joint point's declaration hashes to {got[:12]}, not the declared "
                        f"{W.JOINT['declarationSha256'][:12]}")
    return json.loads(W.JOINT["spec"].read_text())["overrides"]


def start(which: str) -> str:
    """Build a declared starting point; `start-joint` must reproduce W44's four endpoint patches."""
    if which not in STARTS:
        raise W.Refusal(f"start {which!r} is not one of {STARTS}")
    label = f"start-{which}"
    overrides = {} if which == "c05" else joint_overrides()
    write_spec(label, overrides, f"the declared starting point {which} (Decision Log 4, X56)",
               "start", "start", which)
    build(label)
    if which == "joint":
        w44 = W.JOINT["candidate"].parent
        for slot in ("active.light", "active.dark", "receded.light", "receded.dark"):
            mine = json.loads((G1 / "candidates" / label / f"{slot}.json").read_text())
            theirs = json.loads((w44 / f"{slot}.json").read_text())
            if mine["patch"] != theirs["patch"] or mine["resolvedMaterialSha256"] != theirs["resolvedMaterialSha256"]:
                raise W.Refusal(f"start-joint {slot}: W45's build is not W44's joint point "
                                f"(digest {mine['resolvedMaterialSha256']} vs {theirs['resolvedMaterialSha256']})")
    return label


# ---------------------------------------------------------------------------------------------
# Render
# ---------------------------------------------------------------------------------------------
def rendered_scopes(label: str) -> dict:
    out = {}
    root = SCRATCH / label
    for d in sorted(root.glob("*/matrix.json")) if root.exists() else []:
        out[d.parent.name] = {r["key"]["sceneId"] for r in json.loads(d.read_bytes())["cells"]}
    return out


def covered(label: str, scope: str) -> bool:
    """Whether the label's rendered 2x scopes already hold every fit cell of `scope`."""
    have = rendered_scopes(label)
    if scope == "x48":
        return "x48" in have
    done = set().union(*[v for k, v in have.items() if k != "x48"]) if have else set()
    want = scenes_for("fit" if scope in ("fit", "rest-of-fit") else scope)
    return set(want) <= done


def compare_argv(candidate: Path, scale: int, scenes: list[str], out: Path) -> list[str]:
    return ["pnpm", "run", "-s", "compare", "--", "--profile", PROFILE[scale], "--renderer", "webgpu",
            "--candidate-document", str(candidate.relative_to(CAL)), "--set", SETS,
            "--scene", ",".join(scenes), "--alpha", "--write-partial", "--out-matrix", str(out / "matrix.json")]


def render(label: str, scope: str) -> int:
    candidate = W.refuse_w44_path(G1 / "candidates" / label / "candidate.json", "the candidate")
    if not candidate.exists():
        raise W.Refusal(f"render: {label} is not built")
    scale = 1 if scope == "x48" else 2
    have = rendered_scopes(label)
    if scope in have or covered(label, scope):
        return 0
    done = set().union(*[v for k, v in have.items() if k != "x48"]) if have else set()
    if scope == "rest-of-fit":
        scenes = [s for s in scenes_for("fit") if s not in done]
    else:
        scenes = scenes_for("fit" if scope in ("fit", "x48") else scope, scale)
        if scale == 2 and done & set(scenes):
            raise W.Refusal(f"render {label} {scope}: overlaps a rendered scope; use rest-of-fit")
    if not scenes:
        return 0
    out = W.refuse_w44_path(SCRATCH / label / scope, "the render's scratch")
    out.mkdir(parents=True, exist_ok=True)
    run_label = f"{label}/{scope}"
    argv = compare_argv(candidate, scale, scenes, out)
    env = {k: v for k, v in os.environ.items() if not k.startswith("VITREA_")}
    env.update(VITREA_WEB_CAPTURES=str(out / "web-captures"))
    started = now()
    log(dict(label=run_label, started=started, scenes=len(scenes),
             argv=[a if a != ",".join(scenes) else f"<{len(scenes)} scenes: {scope}>" for a in argv]))
    (G1 / "logs").mkdir(exist_ok=True)
    log_path = G1 / "logs" / f"{label}__{scope}.txt"
    with log_path.open("x") as f:
        result = subprocess.run([str(W.G0 / "with-gpu.sh"), f"w45-fit {run_label}", *argv], cwd=CAL, env=env,
                                stdout=f, stderr=subprocess.STDOUT)
    code = result.returncode
    if code == 1 and census_refused(log_path):
        code = 3      # the census refused before the launch: nothing rendered (with-gpu.sh exits 1)
    log(dict(label=run_label, started=started, completed=now(), exitCode=code))
    print(run_label, "exit", code, len(scenes), "cells", flush=True)
    return code


def census_refused(log_path: Path) -> bool:
    """`with-gpu.sh` exits 1 both on a census refusal and when compare wrote a partial matrix; the
    census gate's first line says which (`census <label>: REFUSES ...`)."""
    first = log_path.read_text().splitlines()[:1]
    return bool(first) and first[0].startswith("census ") and ": REFUSES" in first[0]


# ---------------------------------------------------------------------------------------------
# Read
# ---------------------------------------------------------------------------------------------
def read(label: str) -> dict:
    """W45's cuts.py on every 2x scope the label has, against c05; writes cuts.txt, cuts.json.gz and
    summary.json under candidates/<label>/ (a re-read replaces them: they derive from the scratch)."""
    folder = G1 / "candidates" / label
    scopes = {k: v for k, v in rendered_scopes(label).items() if k != "x48"}
    if not scopes:
        raise W.Refusal(f"read {label}: nothing rendered")
    merged = SCRATCH / label / "merged-captures"
    merged.mkdir(exist_ok=True)
    for tree in [SCRATCH / label / s / "web-captures" for s in scopes]:
        for prof in tree.iterdir():
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
    for s in scopes:
        argv += ["--bed", str(SCRATCH / label / s / "matrix.json")]
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


def within_clause(cells, scope: str, missing=()) -> dict:
    """The scope's within clause on T1's fidelity output: stage 1, every F and every pitch-16
    (`checkerboard`) cell of the scope; stage 2, every F, C and P cell. A T cell is never required
    within; a member with no reading makes the clause UNMEASURED."""
    B, t1 = cuts()

    def member(c) -> bool:
        if c["stratum"] not in t1.SELECTION_STRATA:
            return False
        if SCOPES[scope]["within"] == "F+pitch16":
            return c["stratum"] == "F" or B.SCENES.by_id[c["scene"]]["background"] == "checkerboard"
        return True

    members = [c for c in cells if in_scope(c, scope) and member(c)]
    s = SCOPES[scope]
    absent = [m for m in missing if t1.in_landing_scope(m) and m["pose"] == s["pose"]
              and (s["spans"] is None or t1.span_class(m["scene"]) in s["spans"]) and member(m)]
    not_within = [f"{c['scene']} {c['scale']}x" for c in members if c["fidelity"] != "within"]
    return dict(scope=scope, members=len(members), notWithin=not_within,
                unmeasured=[f"{m['scene']} {m['scale']}x" for m in absent],
                verdict="UNMEASURED" if absent or not members else "WITHIN" if not not_within else "NOT WITHIN")


def summarise(label, result, scopes) -> dict:
    _, t1 = cuts()
    t = result["T1"]
    cells = [c for c in t["cells"] if t1.in_landing_scope(c)]
    spec = json.loads((G1 / "specs" / f"{label}.json").read_text())
    per_cell = {}
    for c in cells:
        entry = dict(stratum=c["stratum"], pose=c["pose"], span=c["spanClass"], n=c["native"],
                     c=c["reference"], k=c["candidate"], fidelity=c["fidelity"], change=c["change"],
                     growth=c["growth"], B=c["B"])
        if "bands" in c:
            entry["bands"] = {b: {k: c["bands"][b][k] for k in ("native", "reference", "candidate",
                                                                "fidelity", "change", "growth", "B")}
                              for b in t1.BANDS}
        per_cell[c["scene"]] = entry
    stages = {}
    for scope in SCOPES:
        clause = within_clause(t["cells"], scope, t.get("missing", ()))
        stages[scope] = dict(objective=t1.selection_metric(t["cells"], where=lambda c, s=scope: in_scope(c, s)),
                             within=clause["verdict"], notWithin=clause["notWithin"],
                             unmeasured=len(clause["unmeasured"]))
    return dict(
        label=label, stage=spec["stage"], family=spec["family"], start=spec["start"], overrides=spec["overrides"],
        scopes={k: len(v) for k, v in scopes.items()},
        declarationSha256=sha((G1 / "candidates" / label / "candidate.json").read_bytes()),
        stages=stages, selectionMetric=t["selectionMetric"], selectionTie=t["selectionTie"],
        rule=t.get("rule", result.get("rule")),
        verdicts=result["summary"], cells=per_cell)


def point(label, overrides, stage, family, start_, scope, note="") -> dict:
    """Spec, build, render the scope and read: memoized by label."""
    write_spec(label, overrides, note, stage, family, start_)
    build(label)
    code = render(label, scope)
    if code not in (0, 1):
        raise W.Refusal(f"{label}/{scope}: render exit {code}")
    summary = G1 / "candidates" / label / "summary.json"
    if summary.exists():
        s = json.loads(summary.read_text())
        if s["scopes"] == {k: len(v) for k, v in rendered_scopes(label).items() if k != "x48"}:
            return s
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
        print(start(argv[2]))
        return 0
    if verb == "point":
        label = argv[2]
        rest = [a for a in argv[3:] if "@" in a and "=" in a]
        s = point(label, parse_overrides(rest), opt("--stage"), opt("--family"), opt("--start"),
                  opt("--scope", "fit"), opt("--note", ""))
        print(json.dumps({k: s[k] for k in ("label", "stages", "selectionMetric", "rule")}, indent=1))
        return 0
    if verb == "render":
        return render(argv[2], opt("--scope"))
    if verb == "read":
        s = read(argv[2])
        print(json.dumps({k: s[k] for k in ("label", "stages", "selectionMetric", "rule")}, indent=1))
        return 0
    print(__doc__)
    return 64


if __name__ == "__main__":
    sys.exit(main(sys.argv))
