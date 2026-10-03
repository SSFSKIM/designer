#!/usr/bin/env python3.12
"""W45 G0 (b): the declared search, stage by stage, W44 G1's (`results/2026-10-03-w44-g1-refit/fit/
search.py`) ported for W45 (charter Design "The moves", Decision Log 4, X56, X58). W44's committed
copy is untouched.

    python3.12 -B search.py stage <stage> --start c05|joint --base LABEL [--passes 2]
    python3.12 -B search.py full LABEL              (the whole fit map at a point: rest-of-fit)
    python3.12 -B search.py table [SCOPE]           (every point's numbers, from the summaries)

**Part 2, as hashed** (`fit-declaration.json`): `stage1` {families: `deep`} and `stage2`
{familyOrder [`thin`, `receded`], `thin` on scope `stage2-thin`, `receded` on `stage2-receded`}. A
family's cell scope is its `scope`, else the stage's `scope`, else the stage id (`fit.scope_of`); a
leaf key `a+b` is a tied pair set together; a leaf with `domainRelativeTo` takes its grid as
fractions of the ACTIVE light value of the same leaf at the current point (the receded share and
the receded operator delta); a family's `fixed` leaves are held at their declared values in every
point it sweeps.

**The procedure** (part 2's `searchProcedure`): within a stage each leaf's grid is swept in the order
listed, the others held at their current values, keeping the grid point with the smallest objective;
at most two passes; a full factorial sweep is permitted (`factorial: true`) and not required. A
stage's families are SEQUENTIAL COMPONENTS of that one procedure, in `familyOrder`: each family is
swept on its own scope from the point the previous one left (stage 2: `thin` from the stage-1 point,
then `receded` from `thin`'s best), so the stage's point carries every component's overrides. The
point the components compose is then rendered on the rest of the STAGE's cells (the union of its
parts) and the stage is decided there.

**Candidates of one content render once** (part 2's `searchProcedure`; W44 G1's tracker note): a
point is labelled by what it moves beyond its base — the stage's base point with the family's fixed
leaves folded in, so a fixed value is never a label difference — and, once built, a point whose four
resolved digests equal an already-rendered (or earlier same-batch) point's of the same lineage is
MEASURED by that twin and not rendered again (`fit.record_alias`; logged in `runs.jsonl`). It keeps
its own label and overrides: equal digests are not equal search states (the identity table drops
both second-tap widths while the share is 0), so a sweep that chooses a point carries THAT point's
overrides forward, and readers follow `fit.measured_label` to its measurements.

**A partial objective is never ranked** (`scope_objective`), in a sweep or in a decision: a point
whose scope lacks an F u C u P member's reading is ranked on the value `recover.py` recovered for
it, or the search refuses until it is recovered.

**From two starting points** (X56): `--start` names the lineage, `--base` the point the stage starts
from (`start-c05`, `start-joint`, or the previous stage's landed point of the same lineage); every
label carries the lineage (`c-` or `j-`), and each stage's decision is written to G1's
`fit/path/<start>/<stage>.json` with its components, so the two paths never share a record.

**The decision** (part 2's `selectionRule.withinAStage` and `ifNotWithin`): among the stage's points
read on the whole stage — every swept point of a one-family stage; the composed point of a stage of
several components — the point with a passing within clause and the smallest stage objective lands;
if none is within, the smallest stage objective, a tie within the stage tie (`rule.stage_tie`)
going to the fewer moved leaves, recorded as not within. A point with an UNMEASURED objective member
is ranked only on its value recovered through W44 G0's port (`recover.py`), never on a partial
median.
"""
from __future__ import annotations

import json
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import fit  # noqa: E402

PATH = fit.G1 / "path"
SHORT = {"sizeScatterFloor2x": "fl", "sizeScatterSpanMax2x": "top", "sizeHeavySecondShare": "q",
         "sizeHeavySecondSigma2x": "w", "sizeHeavySecondSigma": "w1x", "sizeHeavySecondShareFar2x": "d",
         "sizeScatterRampStartThin2x": "t", "sizeScatterRampStartThick2x": "k", "sizeScatterRampStartFar2x": "f",
         "sizeScatterRampReach2xPx": "r", "sizeHeavyTapSigma2x": "s"}
STAGE_SHORT = {"stage1": "s1", "stage2": "s2"}
SLOTS = ("active.light", "active.dark", "receded.light", "receded.dark")


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
    """A family's fixed leaves as overrides {slot: {leaf: value}}."""
    out = {}
    for leaf, spec in fbody.get("fixed", {}).items():
        out.setdefault(spec["slot"], {})[leaf] = spec["value"]
    return out


def label_of(start: str, stage_id: str, overrides: dict, base: dict) -> str:
    """A readable label from what a point moves beyond `base` (the stage's base with the family's
    fixed leaves folded in), prefixed by its lineage and stage."""
    parts = []
    for slot, leaves in sorted(overrides.items()):
        for leaf, v in sorted(leaves.items()):
            if base.get(slot, {}).get(leaf) != v:
                parts.append(f"{'R' if slot == 'receded.light' else ''}{SHORT[leaf]}{fmt(round(v, 6))}")
    return f"{start[0]}-{STAGE_SHORT.get(stage_id, stage_id)}" + ("-" + "-".join(parts) if parts else "-base")


def grid_of(spec: dict, current: dict, leaf: str) -> list:
    if spec.get("domainRelativeTo"):
        active = fit.active_value(current, leaf)
        return sorted({round(f * active, 6) for f in spec["grid"]})
    return list(spec["grid"])


def sweep_candidates(fbody: dict, key: str, current: dict) -> list[dict]:
    """The points one leaf's (or tied pair's) grid gives from `current`, the others held."""
    spec = fbody["leaves"][key]
    grid = grid_of(spec, current, key.split("+")[0])
    return [with_leaf(current, spec["slot"], {leaf: v for leaf in key.split("+")}) for v in grid]


# ---------------------------------------------------------------------------------------------
# The real runner: build, render once per content, read
# ---------------------------------------------------------------------------------------------
def same_point(overrides: dict, start: str) -> str | None:
    """An existing candidate of the same lineage with exactly these overrides."""
    for f in sorted((fit.G1 / "specs").glob("*.json")):
        spec = json.loads(f.read_text())
        if spec["overrides"] == overrides and spec.get("start") == start:
            return f.stem
    return None


def content_of(label: str) -> tuple:
    folder = fit.G1 / "candidates" / label
    return tuple(json.loads((folder / f"{slot}.json").read_text())["resolvedMaterialSha256"] for slot in SLOTS)


def content_twin(label: str, start: str, pending: dict) -> str | None:
    """A point of the same lineage and content that is (or is about to be) rendered, other than
    `label`: a rendered point first, else one named earlier in the same batch (`pending`,
    content -> label). Aliases are never twins of each other: a twin is a point that renders."""
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
    """Whether the label's summary reads every scope it has rendered."""
    path = fit.G1 / "candidates" / label / "summary.json"
    if not path.exists():
        return False
    rendered = {k: len(v) for k, v in fit.rendered_scopes(label).items() if k != "x48"}
    return json.loads(path.read_text())["scopes"] == rendered


def recovered_points() -> dict:
    path = PATH / "recovered.json"
    return json.loads(path.read_text())["points"] if path.exists() else {}


def scope_objective(label: str, scope: str) -> float:
    """A point's objective on `scope`, read off the label that measures it: the recorded value when
    every F u C u P member of the scope has a reading, else the value `recover.py` recovered for it,
    else a refusal — a partial median is never ranked, in a sweep or in a decision."""
    _, t1 = fit.cuts()
    measured = fit.measured_label(label)
    s = summary_of(measured)
    members = [sid for sid in fit.scenes_for(scope) if t1.stratum(sid) in t1.SELECTION_STRATA]
    if all(sid in s["cells"] for sid in members):
        return s["stages"][scope]["objective"]
    got = recovered_points().get(measured, {}).get(scope)
    if got is None:
        raise fit.W.Refusal(f"{label} (measured by {measured}) has an UNMEASURED {scope} objective member and no "
                            "recovered reading: run recover.py, then the search again; a partial median is "
                            "never ranked")
    return got["declaredObjective"]


class Runner:
    """Builds, renders (once per content) and reads points; the tests hand `compose` a runner that
    renders nothing.

    A point keeps its OWN label and overrides whatever measures it. Equal resolved digests draw
    equal pixels, so a point whose content an already-rendered (or earlier, same-batch) point of its
    lineage has is MEASURED by that twin (`fit.record_alias`) rather than rendered again — but equal
    digests are not equal search states: the identity table drops both second-tap widths while the
    share is 0, so every width of a zero-share sweep shares one content, and the width the sweep
    chooses must survive into the next sweep (the review of W45 G0's closure, P1)."""

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


# ---------------------------------------------------------------------------------------------
# The procedure
# ---------------------------------------------------------------------------------------------
def sweep_family(move: dict, family: str, start: str, base: dict, current: dict, passes: int,
                 runner: Runner) -> tuple[dict, list[str], str | None]:
    """One component: the family's coordinate sweeps (or its full factorial) on its own scope from
    `current`, with its fixed leaves held. Returns (the best point's overrides, every label, best)."""
    fbody = move["families"][family]
    scope = fit.scope_of(move, family)
    fixed = fixed_of(fbody)
    current = merged(current, fixed)
    label_base = merged(base, fixed)
    keys = list(fbody.get("leaves", {}))
    labels, best = [], None

    def run(cands: list[dict]) -> list[str]:
        names = runner.points(cands, [label_of(start, move["id"], ov, label_base) for ov in cands],
                              move["id"], family, start, scope)
        labels.extend(names)
        return names

    if fbody.get("factorial"):
        cands = [current]
        for k in keys:
            cands = [c for point in cands for c in sweep_candidates(fbody, k, point)]
        names = run(cands)
        best = min(names, key=lambda n: runner.objective(n, scope))
        return runner.overrides(best), labels, best
    for _ in range(passes):
        before = json.dumps(current, sort_keys=True)
        for k in keys:
            names = run(sweep_candidates(fbody, k, current))
            best = min(names, key=lambda n: runner.objective(n, scope))
            current = runner.overrides(best)
        if json.dumps(current, sort_keys=True) == before:
            break
    return current, labels, best


def compose(stage_id: str, start: str, base: dict, passes: int, runner: Runner) -> dict:
    """The stage's components in `familyOrder`, each swept on its scope from the point the previous
    one left; `composed` is the point that carries them all."""
    move = move_of(stage_id)
    order = move.get("familyOrder") or list(move["families"])
    current, components = base, []
    for family in order:
        start_point = current
        current, labels, best = sweep_family(move, family, start, base, current, passes, runner)
        components.append(dict(family=family, scope=fit.scope_of(move, family), from_=start_point, best=best,
                               bestOverrides=current, points=list(dict.fromkeys(labels))))
    return dict(stage=stage_id, start=start, components=components, composed=current)


def stage(stage_id: str, start: str, base_label: str, passes: int = 2, runner: Runner | None = None) -> dict:
    runner = runner or Runner()
    if spec_of(base_label)["start"] != start:
        raise fit.W.Refusal(f"stage {stage_id}: base {base_label} is of lineage {spec_of(base_label)['start']}, "
                            f"not {start}")
    move = move_of(stage_id)
    base = base_overrides(base_label)
    path = compose(stage_id, start, base, passes, runner)
    if len(path["components"]) == 1:
        candidates = path["components"][0]["points"]
    else:
        # The composed point, read on the rest of the stage's union (its components each rendered one part).
        composed_base = base
        for c in path["components"]:
            composed_base = merged(composed_base, fixed_of(move["families"][c["family"]]))
        candidates = runner.points([path["composed"]], [label_of(start, stage_id, path["composed"], composed_base)],
                                   stage_id, "composed", start, stage_id)
    record = decide(move, start, candidates)
    record.update(base=base_label, components=[{("from" if k == "from_" else k): v for k, v in c.items()}
                                               for c in path["components"]], composed=path["composed"])
    (PATH / start).mkdir(parents=True, exist_ok=True)
    (PATH / start / f"{stage_id}.json").write_text(json.dumps(record, indent=1) + "\n")
    return record


def moved_leaves(summary) -> int:
    return sum(len(v) for v in summary["overrides"].values())


def decide(move: dict, start: str, labels: list[str]) -> dict:
    """Part 2's selection within a stage, on the stage's own cells (`rule.stage_*`)."""
    stage_id = move["id"]
    rows = []
    for label in dict.fromkeys(labels):
        measured = fit.measured_label(label)
        reading = summary_of(measured)["stages"][stage_id]
        try:
            objective = scope_objective(label, stage_id)
        except fit.W.Refusal as err:
            raise fit.W.Refusal(f"decide {stage_id}: {err}") from None
        rows.append(dict(label=label, measuredBy=measured, objective=objective, within=reading["within"],
                         notWithin=reading["notWithin"], leaves=moved_leaves(dict(overrides=base_overrides(label))),
                         tie=reading["tie"]))
    inside = [r for r in rows if r["within"] == "WITHIN"]
    if inside:
        landed = min(inside, key=lambda r: r["objective"])
        how = "the stage's point with a passing within clause and the smallest stage objective"
    else:
        best = min(rows, key=lambda r: r["objective"])
        ties = [r for r in rows if r["objective"] - best["objective"] <= best["tie"]]
        landed = min(ties, key=lambda r: (r["leaves"], r["objective"]))
        how = ("no point within: the smallest stage objective, a tie within the stage tie "
               f"({best['tie']:.4f}) to the fewer moved leaves; recorded as NOT within")
    return dict(stage=stage_id, start=start, landed=landed["label"], within=landed["within"], how=how,
                points=rows)


def table(scope: str | None = None) -> str:
    lines = []
    for f in sorted((fit.G1 / "candidates").glob("*/summary.json")):
        s = json.loads(f.read_text())
        ov = "; ".join(f"{slot.split('.')[0]} {k}={v:g}" for slot, kv in s["overrides"].items() for k, v in kv.items())
        objs = " ".join(f"{m}={v['objective']:.4f}{'*' if v['within'] == 'WITHIN' else ''}"
                        if v["objective"] is not None else f"{m}=—" for m, v in s["stages"].items()
                        if scope is None or m == scope)
        lines.append(f"{s['label']:<28} {s['start']:<5} {s['stage']}/{s['family']:<8} {objs}  "
                     f"sel={s['selectionMetric'] or 0:.4f}  [{ov}]")
    return "\n".join(lines) + "\n"


def main(argv) -> int:
    fit.preflight()
    verb = argv[1] if len(argv) > 1 else ""
    opt = lambda name, default=None: argv[argv.index(name) + 1] if name in argv else default  # noqa: E731
    if verb == "stage":
        record = stage(argv[2], opt("--start"), opt("--base"), int(opt("--passes", 2)))
        print(json.dumps({k: v for k, v in record.items() if k != "points"}, indent=1)[:4000])
        return 0
    if verb == "full":
        label = argv[2]
        code = fit.render(label, "rest-of-fit")
        if code not in (0, 1):
            return code
        s = fit.read(label)
        print(json.dumps({k: s[k] for k in ("label", "stages", "selectionMetric", "rule")}, indent=1))
        return 0
    if verb == "table":
        print(table(argv[2] if len(argv) > 2 else None))
        return 0
    print(__doc__)
    return 64


if __name__ == "__main__":
    sys.exit(main(sys.argv))
