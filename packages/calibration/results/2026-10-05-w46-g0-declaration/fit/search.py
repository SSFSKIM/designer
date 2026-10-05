#!/usr/bin/env python3.12
"""W46 G0 (a): the declared search, stage by stage, W45 G0's (`results/2026-10-03-w45-g0-operator/fit/
search.py`) ported for W46 (charter Design "The moves", MARKED; clause 1; X64). W45's committed copy
is untouched.

    python3.12 -B search.py stage <stage> --base LABEL [--passes 2]
    python3.12 -B search.py full LABEL              (the whole fit map at a point: rest-of-fit)
    python3.12 -B search.py table [SCOPE]           (every point's numbers, from the summaries)

**What W46 changes, each closing a tracker entry W45 G1 left for the next port:**
- **The declared tie rule** (the tracker's "a coordinate sweep on a median objective decides a
  plateau by grid order"; Design "The moves": "the point nearest the start wins an
  indistinguishable pair, so a plateau is never decided by grid order"). Within a step, every
  candidate whose objective is within the stage tie of the step's minimum is INDISTINGUISHABLE; among
  them the point nearest the step's start wins — distance the sum, over the step's keys, of
  |v − v0| / (domain hi − lo) — then the fewer moved leaves, then grid order. `decide` applies the
  same rule to the stage's points, the distance measured from the stage's base over every declared
  leaf a point moves. The tie is `rule.stage_tie` over the stage's DECLARED cells, computed once from
  the published reference rows (`fit.stage_tie_of`), never from what a point rendered.
- **One label grammar** (`labels.json`): a receded leaf is marked lower-case `r`, which the builder's
  pattern admits (the tracker's "upper-case R" entry), and `label_of` refuses to name a point whose
  label the builder would refuse.
- **`full` renders the twin that measures a point** (the tracker's "`search.py full` renders an
  alias" entry): it resolves `fit.measured_label` first, as the runner does.
- **X64 in stage 2.** A move whose part-2 body names `materialiseX64: <slot>` starts from its base
  with every X64 key of that slot stated at its inherited value (for the receded document, the
  stage-1 active's resolved values): an unchanged start (digest-neutral), from which each is held or
  moved on its own (Design "The moves", Interactions).
- **One lineage** (`d0219`), so W45's two-path machinery has one path; labels carry `d-`.

W45's procedure is otherwise unchanged: a family's coordinate sweeps in the order its leaves are
listed, at most two passes; `factorial: true` sweeps the family's whole grid product as one step and
`factorialGroups` sweep their keys' product as ONE coordinate step on the lineages they name; a grid
point outside a declared joint domain is not a candidate; a leaf key `a+b` is a tied pair; a leaf with
`domainRelativeTo` takes its grid as fractions of the active value; a family's `fixed` leaves are
held. A stage's families are sequential components in `familyOrder`, each on its own scope from the
point the previous left; the composed point is read on the stage and the stage is decided there.
Candidates of one content render once (a twin MEASURES a point and never replaces its overrides). A
partial objective is never ranked: it is the recovered value (`recover.py`) or a refusal.
"""
from __future__ import annotations

import json
import re
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import fit  # noqa: E402

PATH = fit.G1 / "path"
LABELS = fit.LABELS
SHORT = LABELS["short"]
SLOTS = fit.W.SLOTS


def fmt(v):
    return f"{v:g}"


def move_of(stage_id: str) -> dict:
    for m in fit.part2()["moves"]:
        if m["id"] == stage_id:
            return m
    raise fit.W.Refusal(f"part 2 declares no stage {stage_id!r}")


def spec_of(label: str) -> dict:
    return json.loads((fit.G1 / "specs" / f"{label}.json").read_text())


def base_overrides(label: str) -> dict:
    return spec_of(label)["overrides"]


def with_leaf(base: dict, slot: str, leaves: dict) -> dict:
    out = json.loads(json.dumps(base))
    out.setdefault(slot, {}).update(leaves)
    return out


def merged(a: dict, b: dict) -> dict:
    out = json.loads(json.dumps(a))
    for slot, leaves in b.items():
        out.setdefault(slot, {}).update(leaves)
    return out


def fixed_of(fbody: dict) -> dict:
    out = {}
    for leaf, spec in fbody.get("fixed", {}).items():
        out.setdefault(spec["slot"], {})[leaf] = spec["value"]
    return out


def label_of(start: str, stage_id: str, overrides: dict, base: dict) -> str:
    """A readable label from what a point moves beyond `base`, prefixed by its lineage and stage, in
    `labels.json`'s grammar; a label the builder's pattern would refuse is refused here first."""
    parts = []
    for slot, leaves in sorted(overrides.items()):
        for leaf, v in sorted(leaves.items()):
            if base.get(slot, {}).get(leaf) != v:
                if leaf not in SHORT:
                    raise fit.W.Refusal(f"labels.json has no short name for {leaf}")
                parts.append(f"{LABELS['slotMark'][slot]}{SHORT[leaf]}{fmt(round(v, 6))}")
    label = f"{LABELS['lineage'][start]}-{LABELS['stage'].get(stage_id, stage_id)}" + (
        "-" + "-".join(parts) if parts else "-base")
    if not re.fullmatch(LABELS["pattern"], label):
        raise fit.W.Refusal(f"label {label!r} does not match labels.json's pattern {LABELS['pattern']}")
    return label


def grid_of(spec: dict, current: dict, leaf: str) -> list:
    if spec.get("domainRelativeTo"):
        active = fit.active_value(current, leaf)
        return sorted({round(f * active, 6) for f in spec["grid"]})
    return list(spec["grid"])


def sweep_candidates(fbody: dict, key: str, current: dict) -> list[dict]:
    spec = fbody["leaves"][key]
    grid = grid_of(spec, current, key.split("+")[0])
    points = [with_leaf(current, spec["slot"], {leaf: v for leaf in key.split("+")}) for v in grid]
    return [p for p in points if fit.in_joint_domain(p)]


def steps_of(fbody: dict, start: str) -> list[list[str]]:
    keys = list(fbody.get("leaves", {}))
    groups = [g for g in fbody.get("factorialGroups", []) if start in g["starts"]]
    for g in groups:
        missing = [k for k in g["keys"] if k not in keys]
        if missing:
            raise fit.W.Refusal(f"a factorial group names {missing}, which the family does not search")
    grouped = {k: g for g in groups for k in g["keys"]}
    steps = []
    for k in keys:
        g = grouped.get(k)
        if g is None:
            steps.append([k])
        elif k == next(x for x in keys if x in g["keys"]):
            steps.append([x for x in keys if x in g["keys"]])
    return steps


def step_candidates(fbody: dict, step: list[str], current: dict) -> list[dict]:
    cands = [current]
    for k in step:
        cands = [c for point in cands for c in sweep_candidates(fbody, k, point)]
    return cands


# ---------------------------------------------------------------------------------------------
# The tie rule
# ---------------------------------------------------------------------------------------------
def distance(point: dict, origin: dict, keys) -> float:
    """sum over `keys` ((slot, leaf, domain)) of |v − v0| / (hi − lo), each value resolved."""
    total = 0.0
    for slot, leaf, (lo, hi) in keys:
        v, v0 = fit.resolved_value(point, slot, leaf), fit.resolved_value(origin, slot, leaf)
        total += abs(v - v0) / ((hi - lo) or 1)
    return total


def step_keys(fbody: dict, step: list[str], current: dict) -> list:
    out = []
    for key in step:
        spec = fbody["leaves"][key]
        leaf = key.split("+")[0]
        out.append((spec["slot"], leaf, fit.domain_of(spec, current, leaf)))
    return out


def moved_count(overrides: dict, origin: dict) -> int:
    return sum(1 for slot, leaves in overrides.items() for leaf, v in leaves.items()
               if fit.resolved_value(origin, slot, leaf) != v)


def choose(names: list[str], objective, tie: float, origin: dict, keys, overrides) -> str:
    """The declared tie rule: the points within `tie` of the minimum are indistinguishable; the one
    nearest `origin` wins, then the fewer moved leaves, then grid (list) order."""
    values = {n: objective(n) for n in names}
    best = min(values.values())
    close = [n for n in names if values[n] - best <= tie]
    order = {n: i for i, n in enumerate(dict.fromkeys(names))}
    return min(close, key=lambda n: (distance(overrides(n), origin, keys), moved_count(overrides(n), origin), order[n]))


# ---------------------------------------------------------------------------------------------
# The real runner
# ---------------------------------------------------------------------------------------------
def same_point(overrides: dict, start: str) -> str | None:
    for f in sorted((fit.G1 / "specs").glob("*.json")) if (fit.G1 / "specs").exists() else []:
        spec = json.loads(f.read_text())
        if spec["overrides"] == overrides and spec.get("start") == start:
            return f.stem
    return None


def content_of(label: str) -> tuple:
    folder = fit.G1 / "candidates" / label
    return tuple(json.loads((folder / f"{slot}.json").read_text())["resolvedMaterialSha256"] for slot in SLOTS)


def content_twin(label: str, start: str, pending: dict) -> str | None:
    mine = content_of(label)
    table = fit.aliases()
    for f in sorted((fit.G1 / "candidates").glob("*/summary.json")):
        other = f.parent.name
        if other == label or other in table or not (fit.G1 / "specs" / f"{other}.json").exists():
            continue
        if spec_of(other).get("start") == start and content_of(other) == mine:
            return other
    twin = pending.get(mine)
    return twin if twin != label else None


def summary_of(label: str) -> dict:
    return json.loads((fit.G1 / "candidates" / label / "summary.json").read_text())


def read_current(label: str) -> bool:
    path = fit.G1 / "candidates" / label / "summary.json"
    if not path.exists():
        return False
    return json.loads(path.read_text())["scopes"] == {k: len(v) for k, v in fit.rendered_scopes(label).items()}


def recovered_points() -> dict:
    path = PATH / "recovered.json"
    return json.loads(path.read_text())["points"] if path.exists() else {}


def scope_objective(label: str, scope: str) -> float:
    """A point's objective on `scope` (both scales), read off the label that measures it: the
    recorded value when every F u C u P member has a reading, else the value `recover.py` recovered,
    else a refusal."""
    measured = fit.measured_label(label)
    s = summary_of(measured)
    if all(key in s["cells"] for key in fit.selection_members(scope)):
        return s["stages"][scope]["objective"]
    got = recovered_points().get(measured, {}).get(scope)
    if got is None:
        raise fit.W.Refusal(f"{label} (measured by {measured}) has an UNMEASURED {scope} objective member and no "
                            "recovered reading: run recover.py, then the search again; a partial median is "
                            "never ranked")
    return got["declaredObjective"]


class Runner:
    """Builds, renders (once per content) and reads points; the tests hand `compose` a runner that
    renders nothing. A point keeps its OWN label and overrides whatever measures it."""

    def points(self, cands: list[dict], labels: list[str], stage_id: str, family: str, start: str,
               scope: str) -> list[str]:
        named, pending = [], {}
        for ov, label in zip(cands, labels):
            known = same_point(ov, start)
            if known is None:
                fit.write_spec(label, ov, "", stage_id, family, start)
                fit.build(label)
                known = label
            if known not in fit.aliases() and not (fit.G1 / "candidates" / known / "summary.json").exists():
                twin = content_twin(known, start, pending)
                if twin is not None:
                    fit.record_alias(known, twin)
                    fit.log(dict(label=known, measuredBy=twin, scope=scope, at=fit.now()))
                else:
                    pending.setdefault(content_of(known), known)
            named.append(known)
        with ThreadPoolExecutor(max_workers=2) as pool:
            futures = []
            for name in dict.fromkeys(fit.measured_label(n) for n in named):
                if not fit.covered(name, scope):
                    code = fit.render(name, scope)
                    if code == 3:
                        raise fit.W.Refusal(f"census refused before {name}; nothing after it rendered")
                    if code not in (0, 1):
                        raise fit.W.Refusal(f"{name}: render exit {code}")
                if not read_current(name):
                    futures.append(pool.submit(fit.read, name))
            for fut in futures:
                fut.result()
        return named

    def objective(self, label: str, scope: str) -> float:
        return scope_objective(label, scope)

    def overrides(self, label: str) -> dict:
        return base_overrides(label)

    def tie(self, scope: str) -> float:
        return fit.stage_tie_of(scope)


# ---------------------------------------------------------------------------------------------
# The procedure
# ---------------------------------------------------------------------------------------------
def sweep_family(move: dict, family: str, start: str, base: dict, current: dict, passes: int,
                 runner: Runner) -> tuple[dict, list[str], str | None]:
    fbody = move["families"][family]
    scope = fit.scope_of(move, family)
    fixed = fixed_of(fbody)
    current = merged(current, fixed)
    label_base = merged(base, fixed)
    keys = list(fbody.get("leaves", {}))
    labels, best = [], None
    tie = runner.tie(scope)

    def run(cands: list[dict]) -> list[str]:
        names = runner.points(cands, [label_of(start, move["id"], ov, label_base) for ov in cands],
                              move["id"], family, start, scope)
        labels.extend(names)
        return names

    if fbody.get("factorial"):
        names = run(step_candidates(fbody, keys, current))
        best = choose(names, lambda n: runner.objective(n, scope), tie, current,
                      step_keys(fbody, keys, current), runner.overrides)
        return runner.overrides(best), labels, best
    for _ in range(passes):
        before = json.dumps(current, sort_keys=True)
        for step in steps_of(fbody, start):
            cands = step_candidates(fbody, step, current)
            if not cands:
                raise fit.W.Refusal(f"{move['id']}/{family}: the step {step} offers no point inside the declared "
                                    f"domains from {json.dumps(current, sort_keys=True)}")
            names = run(cands)
            best = choose(names, lambda n: runner.objective(n, scope), tie, current,
                          step_keys(fbody, step, current), runner.overrides)
            current = runner.overrides(best)
        if json.dumps(current, sort_keys=True) == before:
            break
    return current, labels, best


def stage_scope(move: dict) -> str:
    """The scope a stage is decided on: the stage's own (its id), which every family of it shares."""
    scopes = {fit.scope_of(move, f) for f in move["families"]}
    if move["id"] in fit.SCOPES and scopes <= {move["id"]}:
        return move["id"]
    raise fit.W.Refusal(f"part 2 {move['id']}: its families' scopes {sorted(scopes)} are not the stage's own")


def stage_base(move: dict, base: dict) -> dict:
    """The stage's starting overrides: `base`, with every X64 key of `materialiseX64`'s slot stated
    at its inherited value when part 2 asks for it (an unchanged, digest-neutral start)."""
    slot = move.get("materialiseX64")
    if slot is None:
        return base
    if slot not in fit.W.X64:
        raise fit.W.Refusal(f"part 2 {move['id']}: materialiseX64 names {slot!r}, not a slot X64 lists")
    return fit.materialise_x64(base, slot)


def compose(stage_id: str, start: str, base: dict, passes: int, runner: Runner) -> dict:
    move = move_of(stage_id)
    order = move.get("familyOrder") or list(move["families"])
    base = stage_base(move, base)
    current, components = base, []
    for family in order:
        start_point = current
        current, labels, best = sweep_family(move, family, start, base, current, passes, runner)
        components.append(dict(family=family, scope=fit.scope_of(move, family), from_=start_point, best=best,
                               bestOverrides=current, points=list(dict.fromkeys(labels))))
    return dict(stage=stage_id, start=start, base=base, components=components, composed=current)


def stage(stage_id: str, base_label: str, passes: int = 2, runner: Runner | None = None,
          start: str = "d0219") -> dict:
    runner = runner or Runner()
    if spec_of(base_label)["start"] != start:
        raise fit.W.Refusal(f"stage {stage_id}: base {base_label} is of lineage {spec_of(base_label)['start']}, "
                            f"not {start}")
    move = move_of(stage_id)
    path = compose(stage_id, start, base_overrides(base_label), passes, runner)
    base = path["base"]
    if len(path["components"]) == 1:
        candidates = path["components"][0]["points"]
    else:
        composed_base = base
        for c in path["components"]:
            composed_base = merged(composed_base, fixed_of(move["families"][c["family"]]))
        candidates = runner.points([path["composed"]], [label_of(start, stage_id, path["composed"], composed_base)],
                                   stage_id, "composed", start, stage_scope(move))
    record = decide(move, start, candidates, base, runner)
    record.update(base=base_label, baseOverrides=base,
                  components=[{("from" if k == "from_" else k): v for k, v in c.items()} for c in path["components"]],
                  composed=path["composed"])
    (PATH / start).mkdir(parents=True, exist_ok=True)
    (PATH / start / f"{stage_id}.json").write_text(json.dumps(record, indent=1) + "\n")
    return record


def declared_keys(origin: dict) -> list:
    """(slot, leaf, domain) for every searched leaf part 2 declares: `decide`'s distance axes."""
    out = []
    for (slot, leaf), spec in sorted(fit.declared().items()):
        if not spec.get("fixedOnly"):
            out.append((slot, leaf, fit.domain_of(spec, origin, leaf)))
    return out


def decide(move: dict, start: str, labels: list[str], origin: dict | None = None, runner: Runner | None = None) -> dict:
    """Part 2's selection within a stage: among the points with a passing within clause (else all),
    the declared tie rule on the stage objective, the distance from the stage's base."""
    runner = runner or Runner()
    stage_id = move["id"]
    scope = stage_scope(move)
    origin = origin if origin is not None else {}
    tie = runner.tie(scope)
    rows = []
    for label in dict.fromkeys(labels):
        measured = fit.measured_label(label)
        reading = summary_of(measured)["stages"][scope]
        try:
            objective = scope_objective(label, scope)
        except fit.W.Refusal as err:
            raise fit.W.Refusal(f"decide {stage_id}: {err}") from None
        rows.append(dict(label=label, measuredBy=measured, objective=objective, within=reading["within"],
                         notWithin=reading["notWithin"], leaves=moved_count(base_overrides(label), origin)))
    inside = [r for r in rows if r["within"] == "WITHIN"]
    pool = inside or rows
    by = {r["label"]: r for r in pool}
    landed = by[choose(list(by), lambda n: by[n]["objective"], tie, origin, declared_keys(origin), base_overrides)]
    how = (("the stage's points with a passing within clause" if inside else
            "no point within: every point of the stage, recorded as NOT within")
           + f"; the smallest stage objective, a tie within {tie:.4f} to the point nearest the stage's base, "
             "then the fewer moved leaves")
    return dict(stage=stage_id, start=start, landed=landed["label"], within=landed["within"], how=how,
                tie=tie, points=rows)


def table(scope: str | None = None) -> str:
    lines = []
    for f in sorted((fit.G1 / "candidates").glob("*/summary.json")):
        s = json.loads(f.read_text())
        ov = "; ".join(f"{slot.split('.')[0]} {k}={v:g}" for slot, kv in s["overrides"].items() for k, v in kv.items())
        objs = " ".join(f"{m}={v['objective']:.4f}{'*' if v['within'] == 'WITHIN' else ''}"
                        if v["objective"] is not None else f"{m}=—" for m, v in s["stages"].items()
                        if scope is None or m == scope)
        lines.append(f"{s['label']:<28} {s['stage']}/{s['family']:<8} {objs}  "
                     f"sel={s['selectionMetric'] or 0:.4f}  L1 {s['L1']['verdict']}  [{ov}]")
    return "\n".join(lines) + "\n"


def full(label: str) -> dict:
    """The whole fit map at a point, rendered on the twin that measures it (the tracker's entry)."""
    name = fit.measured_label(label)
    code = fit.render(name, "rest-of-fit")
    if code not in (0, 1):
        raise fit.W.Refusal(f"full {label}: render exit {code} on {name}")
    return fit.read(name)


def main(argv) -> int:
    fit.preflight()
    verb = argv[1] if len(argv) > 1 else ""
    opt = lambda name, default=None: argv[argv.index(name) + 1] if name in argv else default  # noqa: E731
    if verb == "stage":
        record = stage(argv[2], opt("--base"), int(opt("--passes", 2)))
        print(json.dumps({k: v for k, v in record.items() if k != "points"}, indent=1)[:4000])
        return 0
    if verb == "full":
        s = full(argv[2])
        print(json.dumps({k: s[k] for k in ("label", "stages", "selectionMetric", "rule", "L1")}, indent=1))
        return 0
    if verb == "table":
        print(table(argv[2] if len(argv) > 2 else None))
        return 0
    print(__doc__)
    return 64


if __name__ == "__main__":
    sys.exit(main(sys.argv))
