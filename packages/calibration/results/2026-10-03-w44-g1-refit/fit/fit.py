#!/usr/bin/env python3.12
"""W44 G1 step 2: the fit's measuring loop, in scratch (charter clause 5; part 2 as amended).

W43 G3 (i)'s loop and G0's ladder driver carried to part 2: build a candidate
(`build-candidate.ts`), render it on the fit cells, read T1 and every cut against the c05
reference. Every candidate's documents, its identity check and its cuts are committed under
`candidates/<label>/`; every launch is logged in `runs.jsonl` (census, start, completion) with its
compare log under `logs/`; the matrices and PNGs stay on the machine under
`~/vitrea-w44/g1-scratch/fit/<label>/<scope>/`.

    python3.12 -B fit.py point <label> --move M --family F [--scope S] [--note N] leaf@slot=value ...
    python3.12 -B fit.py render <label> --scope S       (one more scope of a built candidate)
    python3.12 -B fit.py read <label>

What every candidate is, each a refusal rather than a convention (clause 5; part 2's
`candidateIdentity`):
  - a complete four-endpoint declaration built from c05, moved ONLY on leaves part 2 declares for
    the moves (or holds fixed for a family), at values inside the declared domain, never a 1x leaf
    or a dark leaf (`check_overrides`);
  - its dark endpoints patch- and digest-identical to c05's, its light endpoints c05's on every leaf
    but those (`identity`, written beside it as `identity.json`);
  - rendered on the fit cells only: the 2x light T1 cells of the gate partition, named by a
    positive `--scene` whitelist drawn from `scenes.json` through `t1.population` and the referee
    manifest (never a referee, never a holdout scene), under `--set calibration,validation,
    recorded,probe`; the cut loader refuses a referee or holdout row besides.
Scopes partition the fit cells, so a candidate's scopes never overlap: `move1`, `move2`, `move3`
(each move's cells), `fit` (all 94), `rest-of-fit` (the fit cells outside the scopes already
rendered for that label), and `x48` (the 1x light T1 gate cells, for the byte-identity check).

Before the first launch of each process: part 2 hashed at `c04227e9…` (the amended hash) and
`declare.py check-fit` consistent, and the classifying web census (W43 G3 (ii)'s `census.py`)
before every launch: it refuses on Reduce Transparency, Increase Contrast or a real capture
process and annotates the user's own Chrome and a browserless Playwright relay.
"""
from __future__ import annotations

import datetime
import gzip
import hashlib
import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
EVIDENCE = HERE.parent
CAL = EVIDENCE.parents[1]
ROOT = CAL.parent.parent
G0 = CAL / "results" / "2026-10-03-w44-g0-declaration"
SCRATCH = Path.home() / "vitrea-w44" / "g1-scratch" / "fit"
PART2_SHA = "c04227e9240a0f1e890aef5c6529db412783864305b7ddbc125a00923c771175"
PROFILE = {2: "apple-macos-27.0-2x-light-standard-glass0.25", 1: "apple-macos-27.0-1x-light-standard-glass0.25"}
SETS = "calibration,validation,recorded,probe"
sys.path.insert(0, str(EVIDENCE / "cuts"))
import bed as B  # noqa: E402
import t1  # noqa: E402

_spec = importlib.util.spec_from_file_location("w43_census", CAL / "results/2026-10-02-w43-g3-refit/stage/census.py")
census = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(census)

PART2 = json.loads((G0 / "fit-declaration.json").read_text())
HELD = B.referee_plan.referee_cells(B.referee_plan.load_manifest())


def now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def log(row):
    with (HERE / "runs.jsonl").open("a") as f:
        f.write(json.dumps(row, sort_keys=True) + "\n")


# ---------------------------------------------------------------------------------------------
# What part 2 declares
# ---------------------------------------------------------------------------------------------
def declared_leaves() -> dict:
    """(slot, leaf) -> spec for every leaf part 2 lets a move change: the searched leaves (a tied
    pair as both) and the families' fixed values."""
    out = {}
    for move in PART2["moves"]:
        for fam, body in move["families"].items():
            for key, spec in body.get("leaves", {}).items():
                for leaf in key.split("+"):
                    out[(spec["slot"], leaf)] = dict(spec, move=move["id"], family=fam)
            for leaf, spec in body.get("fixed", {}).items():
                out.setdefault((spec["slot"], leaf), dict(spec, move=move["id"], family=fam, fixedOnly=True))
    return out


DECLARED = declared_leaves()


def check_overrides(overrides: dict) -> None:
    """Refuse an override part 2 does not declare, or a value outside its declared domain."""
    for slot, leaves in overrides.items():
        if slot not in ("active.light", "receded.light"):
            raise SystemExit(f"fit: {slot} is not a slot part 2 moves (the dark endpoints never move)")
        for leaf, value in leaves.items():
            spec = DECLARED.get((slot, leaf))
            if spec is None:
                raise SystemExit(f"fit: {slot} {leaf} is not a leaf part 2 declares (clause 5)")
            if spec.get("fixedOnly"):
                if value != spec["value"]:
                    raise SystemExit(f"fit: {slot} {leaf} is held at {spec['value']} by part 2, not {value}")
                continue
            lo, hi = spec["domain"]
            if spec.get("domainRelativeTo"):
                active = overrides.get("active.light", {}).get(leaf, 0)
                lo, hi = lo * active, hi * active
            if not lo <= value <= hi or (spec.get("domainOpenAt") is not None and value == spec["domainOpenAt"]):
                raise SystemExit(f"fit: {slot} {leaf} {value} is outside its declared domain [{lo}, {hi}]")


def scenes_for(scope: str, scale: int = 2) -> list[str]:
    """The fit cells of `scope` at `scale`: 2x light T1 gate cells (never a referee or holdout)."""
    profile = PROFILE[scale]
    out = []
    for p, sid in t1.population([profile]):
        if t1.partition(p, sid, HELD) != "gate":
            continue
        cell = dict(pose=t1.pose(sid), spanClass=t1.span_class(sid))
        if scope.startswith("move"):
            m = t1.MOVES[scope]
            if cell["pose"] != m["pose"] or (m["spans"] is not None and cell["spanClass"] not in m["spans"]):
                continue
        out.append(sid)
    return sorted(out)


def preflight() -> None:
    raw = (G0 / "fit-declaration.json").read_bytes()
    if sha(raw) != PART2_SHA:
        raise SystemExit(f"fit REFUSES: part 2 hashes to {sha(raw)[:12]}, not the amended {PART2_SHA[:12]}")
    got = subprocess.run([sys.executable, "-B", str(G0 / "declare.py"), "check-fit"], capture_output=True,
                         text=True, cwd=G0)
    if got.returncode:
        raise SystemExit("fit REFUSES: declare.py check-fit fails:\n" + got.stdout[-2000:])


# ---------------------------------------------------------------------------------------------
# Build
# ---------------------------------------------------------------------------------------------
def write_spec(label: str, overrides: dict, note: str, move: str, family: str) -> Path:
    check_overrides(overrides)
    path = HERE / "specs" / f"{label}.json"
    spec = dict(label=label, note=note, move=move, family=family, overrides=overrides)
    if path.exists():
        old = json.loads(path.read_text())
        if old["overrides"] != overrides:
            raise SystemExit(f"fit: {label} exists with other overrides {old['overrides']}")
        return path
    path.parent.mkdir(exist_ok=True)
    path.write_text(json.dumps(spec, indent=2) + "\n")
    return path


def build(label: str) -> None:
    folder = HERE / "candidates" / label
    if (folder / "candidate.json").exists():
        return
    got = subprocess.run(["npx", "tsx", str(HERE / "build-candidate.ts"), str(HERE / "specs" / f"{label}.json")],
                         cwd=CAL, capture_output=True, text=True)
    log(dict(label=label, build=now(), exitCode=got.returncode))
    if got.returncode:
        raise SystemExit(f"build {label}: {got.stderr[-800:]}")
    (folder / "identity.json").write_text(json.dumps(identity(label), indent=2) + "\n")


def leaves(node, prefix=""):
    if not isinstance(node, dict):
        return {prefix: node}
    out = {}
    for k, v in node.items():
        out.update(leaves(v, f"{prefix}.{k}" if prefix else k))
    return out


def identity(label: str) -> dict:
    """Part 2's candidateIdentity, checked: dark endpoints patch- and digest-identical to c05's;
    light endpoints c05's on every leaf but the spec's declared overrides."""
    folder = HERE / "candidates" / label
    spec = json.loads((HERE / "specs" / f"{label}.json").read_text())
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
        # The 1x width of the second tap stays at its inert 0 (L3's proof; X48), wherever it is read.
        entry["secondTap1xWidth"] = mine.get("sizeHeavySecondSigma", 0)
        ok &= not undeclared and entry["secondTap1xWidth"] == 0
        out[slot] = entry
    if not ok:
        raise SystemExit(f"identity {label}: {json.dumps(out)}")
    return dict(label=label, holds=True, endpoints=out)


# ---------------------------------------------------------------------------------------------
# Render
# ---------------------------------------------------------------------------------------------
def rendered_scopes(label: str) -> dict:
    out = {}
    for d in sorted((SCRATCH / label).glob("*/matrix.json")) if (SCRATCH / label).exists() else []:
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


def render(label: str, scope: str) -> int:
    candidate = HERE / "candidates" / label / "candidate.json"
    if not candidate.exists():
        raise SystemExit(f"render: {label} is not built")
    scale = 1 if scope == "x48" else 2
    have = rendered_scopes(label)
    if scope in have or covered(label, scope):
        return 0
    if scope == "rest-of-fit":
        done = set().union(*[v for k, v in have.items() if k != "x48"]) if have else set()
        scenes = [s for s in scenes_for("fit") if s not in done]
    else:
        scenes = scenes_for("fit" if scope in ("fit", "x48") else scope, scale)
        done = set().union(*[v for k, v in have.items() if k != "x48"]) if have else set()
        if scale == 2 and done & set(scenes):
            raise SystemExit(f"render {label} {scope}: overlaps a rendered scope; use rest-of-fit")
    if not scenes:
        return 0
    for sid in scenes:
        if (PROFILE[scale], sid) in HELD or B.SCENES.role[sid] == "holdout":
            raise SystemExit(f"render REFUSES: {sid} is a referee or a holdout scene")
    out = SCRATCH / label / scope
    run_label = f"{label}/{scope}"
    observation = census.observe()
    log(dict(label=run_label, at=observation["recordedAt"], census=dict(
        refusals=observation["refusals"], refuse=observation["refuse"],
        annotate=sorted({a["why"] for a in observation["annotate"]}), x6=observation["x6"])))
    if not observation["passes"]:
        print("CENSUS REFUSED", run_label, observation["refusals"], observation["refuse"][:3], flush=True)
        return 3
    out.mkdir(parents=True, exist_ok=True)
    argv = ["pnpm", "run", "-s", "compare", "--", "--profile", PROFILE[scale], "--renderer", "webgpu",
            "--candidate-document", str(candidate.relative_to(CAL)), "--set", SETS,
            "--scene", ",".join(scenes), "--write-partial", "--out-matrix", str(out / "matrix.json")]
    env = {k: v for k, v in os.environ.items() if not k.startswith("VITREA_")}
    env.update(VITREA_WEB_CAPTURES=str(out / "web-captures"))
    started = now()
    log(dict(label=run_label, started=started, scenes=len(scenes),
             argv=[a if a != ",".join(scenes) else f"<{len(scenes)} scenes: {scope}>" for a in argv]))
    (HERE / "logs").mkdir(exist_ok=True)
    with (HERE / "logs" / f"{label}__{scope}.txt").open("x") as f:
        result = subprocess.run(argv, cwd=CAL, env=env, stdout=f, stderr=subprocess.STDOUT)
    log(dict(label=run_label, started=started, completed=now(), exitCode=result.returncode))
    print(run_label, "exit", result.returncode, len(scenes), "cells", flush=True)
    return result.returncode


# ---------------------------------------------------------------------------------------------
# Read
# ---------------------------------------------------------------------------------------------
def read(label: str) -> dict:
    """cuts.py on every 2x scope the label has, against c05; writes cuts.txt, cuts.json.gz and
    summary.json under candidates/<label>/ (a re-read replaces them: they derive from the scratch)."""
    folder = HERE / "candidates" / label
    scopes = {k: v for k, v in rendered_scopes(label).items() if k != "x48"}
    if not scopes:
        raise SystemExit(f"read {label}: nothing rendered")
    trees = [SCRATCH / label / s / "web-captures" for s in scopes]
    merged = SCRATCH / label / "merged-captures"
    merged.mkdir(exist_ok=True)
    for tree in trees:    # one capture root for the cuts: real folders of hard links, never copies
        for prof in tree.iterdir():
            for cell in prof.iterdir():
                (merged / prof.name / cell.name).mkdir(parents=True, exist_ok=True)
                for f in cell.iterdir():
                    link = merged / prof.name / cell.name / f.name
                    if not link.exists():
                        os.link(f, link)
    out_json = SCRATCH / label / "cuts.json"
    out_txt = SCRATCH / label / "cuts.txt"
    for f in (out_json, out_txt):
        f.unlink(missing_ok=True)
    argv = [sys.executable, "-B", str(EVIDENCE / "cuts" / "cuts.py"), "--kind", "candidate",
            "--candidate-document", str((folder / "candidate.json").relative_to(ROOT))]
    for s in scopes:
        argv += ["--bed", str(SCRATCH / label / s / "matrix.json")]
    argv += ["--captures", str(merged), "--out", str(out_json), "--text", str(out_txt)]
    got = subprocess.run(argv, capture_output=True, text=True, cwd=EVIDENCE / "cuts")
    if got.returncode:
        raise SystemExit(f"read {label}: cuts.py exit {got.returncode}: {got.stderr[-1500:]}")
    result = json.loads(out_json.read_bytes())
    (folder / "cuts.txt").write_text(out_txt.read_text())
    with gzip.open(folder / "cuts.json.gz", "wt") as f:
        json.dump(result, f)
    summary = summarise(label, result, scopes)
    (folder / "summary.json").write_text(json.dumps(summary, indent=1) + "\n")
    return summary


def summarise(label, result, scopes) -> dict:
    t = result["T1"]
    cells = [c for c in t["cells"] if t1.in_landing_scope(c)]
    spec = json.loads((HERE / "specs" / f"{label}.json").read_text())
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
    return dict(
        label=label, move=spec["move"], family=spec["family"], overrides=spec["overrides"],
        scopes={k: len(v) for k, v in scopes.items()},
        declarationSha256=sha((HERE / "candidates" / label / "candidate.json").read_bytes()),
        moves={m: dict(objective=v["objective"], within=v["within"]["verdict"],
                       notWithin=v["within"]["notWithin"], unmeasured=len(v["within"]["unmeasured"]))
               for m, v in t["moves"].items()},
        selectionMetric=t["selectionMetric"], selectionTie=t["selectionTie"],
        landing={k: t["landing"][k] for k in ("verdict", "fAggregate", "fAggregateReference", "fNotWithin",
                                              "awayBeyondB", "overshoot", "unmeasuredInScope")},
        verdicts=result["summary"], cells=per_cell)


def point(label, overrides, move, family, scope, note="") -> dict:
    """Spec, build, render the scope and read: memoized by label."""
    write_spec(label, overrides, note, move, family)
    build(label)
    code = render(label, scope)
    if code not in (0, 1):
        raise SystemExit(f"{label}/{scope}: render exit {code}")
    summary = HERE / "candidates" / label / "summary.json"
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
        out.setdefault(slot, {})[leaf] = float(value) if "." in value else int(value)
    return out


def main(argv) -> int:
    preflight()
    verb = argv[1] if len(argv) > 1 else ""
    opt = lambda name, default=None: argv[argv.index(name) + 1] if name in argv else default  # noqa: E731
    if verb == "point":
        label = argv[2]
        rest = [a for i, a in enumerate(argv[3:], 3) if "@" in a and "=" in a]
        s = point(label, parse_overrides(rest), opt("--move"), opt("--family"), opt("--scope", "fit"),
                  opt("--note", ""))
        print(json.dumps({k: s[k] for k in ("label", "moves", "selectionMetric", "landing")}, indent=1))
        return 0
    if verb == "render":
        return render(argv[2], opt("--scope"))
    if verb == "read":
        s = read(argv[2])
        print(json.dumps({k: s[k] for k in ("label", "moves", "selectionMetric", "landing")}, indent=1))
        return 0
    print(__doc__)
    return 64


if __name__ == "__main__":
    sys.exit(main(sys.argv))
