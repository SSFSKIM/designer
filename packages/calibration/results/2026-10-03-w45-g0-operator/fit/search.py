#!/usr/bin/env python3.12
"""W45 G0 (b): the declared search, stage by stage, W44 G1's (`results/2026-10-03-w44-g1-refit/fit/
search.py`) ported for W45 (charter Design "The moves", Decision Log 4, X56, X58). W44's committed
copy is untouched.

    python3.12 -B search.py stage <move-id> --start c05|joint --base LABEL [--passes 2]
    python3.12 -B search.py full LABEL              (the whole fit map at a point: rest-of-fit)
    python3.12 -B search.py table [SCOPE]           (every point's numbers, from the summaries)

**What part 2 must say for this to run** (the interface W45's part 2 is written to): each entry
of `moves` has an `id`, its `families` (each with `leaves`, optional `fixed`, optional `scope`,
optional `from: "previous"`, optional `factorial: true`) and an optional `familyOrder`; a family's
cell scope is its `scope`, else the move's `scope`, else the move id, one of `fit.SCOPES`
(`stage1`, `stage2-thin`, `stage2-receded`). A leaf key `a+b` is a tied pair set together; a leaf
with `domainRelativeTo` takes its grid as fractions of the current active light value of the same
leaf (W44's receded share).

**The procedure, as W44's** (part 2's `searchProcedure`): within a family each leaf's grid in the
order listed, the others held at their current values, the smallest scope objective kept, at most
two passes; a full factorial sweep of a family's grids is permitted (`factorial: true`). A family
starts from the stage's base unless it says `from: "previous"` (W44's move 2 `reach` after
`start`). **From two starting points** (X56): `--start` names the lineage, `--base` the point the
stage starts from (`start-c05`, `start-joint`, or a previous stage's landed point of the same
lineage); every label carries the lineage (`c-` or `j-`), and each stage's decision is written to
G1's `fit/path/<start>/<move-id>.json`, so the two paths never share a record.

**The decision, as W44's** (`decide`): the first family in order with a searched point within the
scope's clause lands, at its within point with the smallest objective; if none is within, the
smallest objective across the families, a tie within the selection tie (the median over the
scope's F u C u P cells of log(1 + bar / native)) going to the fewer moved leaves. A point with an
UNMEASURED objective member is ranked only on its value recovered through W44 G0's port
(`recover.py`), never on a partial median.
"""
from __future__ import annotations

import gzip
import itertools
import json
import math
import statistics
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import fit  # noqa: E402

PATH = fit.G1 / "path"
SHORT = {"sizeScatterFloor2x": "fl", "sizeScatterSpanMax2x": "top", "sizeHeavySecondShare": "q",
         "sizeHeavySecondSigma2x": "w", "sizeHeavySecondShareFar2x": "d", "sizeScatterRampStartThin2x": "t",
         "sizeScatterRampStartThick2x": "k", "sizeScatterRampStartFar2x": "f", "sizeScatterRampReach2xPx": "r",
         "sizeHeavyTapSigma2x": "s"}
MOVE_SHORT = {"stage1": "s1", "stage2-thin": "s2t", "stage2-receded": "s2r"}


def fmt(v):
    return f"{v:g}"


def move_of(move_id: str) -> dict:
    for m in fit.part2()["moves"]:
        if m["id"] == move_id:
            return m
    raise fit.W.Refusal(f"part 2 declares no move {move_id!r}")


def base_overrides(label: str) -> dict:
    return json.loads((fit.G1 / "specs" / f"{label}.json").read_text())["overrides"]


def lineage(label: str) -> str:
    return json.loads((fit.G1 / "specs" / f"{label}.json").read_text())["start"]


def with_leaf(base: dict, slot: str, leaves: dict) -> dict:
    out = json.loads(json.dumps(base))
    out.setdefault(slot, {}).update(leaves)
    return out


def label_of(start: str, move_id: str, overrides: dict, base: dict) -> str:
    """A readable label from what a point moves beyond its base, prefixed by its lineage."""
    parts = []
    for slot, leaves in sorted(overrides.items()):
        for leaf, v in sorted(leaves.items()):
            if base.get(slot, {}).get(leaf) != v:
                parts.append(f"{'R' if slot == 'receded.light' else ''}{SHORT[leaf]}{fmt(round(v, 6))}")
    return f"{start[0]}-{MOVE_SHORT.get(move_id, move_id)}" + ("-" + "-".join(parts) if parts else "-base")


def same_point(overrides: dict, start: str) -> str | None:
    """An existing candidate of the same lineage with exactly these overrides."""
    for f in sorted((fit.G1 / "specs").glob("*.json")):
        spec = json.loads(f.read_text())
        if spec["overrides"] == overrides and spec.get("start") == start:
            return f.stem
    return None


def run_points(points: list[dict]) -> dict:
    """Render every point in order, reading each in a worker; returns label -> summary."""
    for p in points:
        fit.write_spec(p["label"], p["overrides"], p.get("note", ""), p["stage"], p["family"], p["start"])
        fit.build(p["label"])
    out, futures = {}, {}
    with ThreadPoolExecutor(max_workers=2) as pool:
        for p in points:
            summary = fit.G1 / "candidates" / p["label"] / "summary.json"
            if summary.exists() and fit.covered(p["label"], p["scope"]):
                out[p["label"]] = json.loads(summary.read_text())
                continue
            code = fit.render(p["label"], p["scope"])
            if code == 3:
                raise fit.W.Refusal(f"census refused before {p['label']}; nothing after it rendered")
            if code not in (0, 1):
                raise fit.W.Refusal(f"{p['label']}: render exit {code}")
            futures[p["label"]] = pool.submit(fit.read, p["label"])
        for label, fut in futures.items():
            out[label] = fut.result()
    return out


def grid_of(spec: dict, current: dict, leaf: str) -> list:
    if spec.get("domainRelativeTo"):
        active = current.get("active.light", {}).get(leaf, 0)
        return sorted({round(f * active, 6) for f in spec["grid"]})
    return list(spec["grid"])


def summary_of(label: str) -> dict:
    return json.loads((fit.G1 / "candidates" / label / "summary.json").read_text())


def sweep_family(move: dict, family: str, start: str, base_label: str, current: dict, passes: int) -> tuple:
    """One family's coordinate sweeps (or its full factorial): returns (best overrides, labels)."""
    fbody = move["families"][family]
    scope = fit.scope_of(move, family)
    fixed = {}
    for leaf, spec in fbody.get("fixed", {}).items():
        fixed.setdefault(spec["slot"], {})[leaf] = spec["value"]
    for slot, leaves in fixed.items():
        current = with_leaf(current, slot, leaves)
    base = base_overrides(base_label)
    labels = []

    def points_for(candidates: list[dict]) -> list[str]:
        pts, names = [], []
        for ov in candidates:
            known = same_point(ov, start)
            if known is not None:
                names.append(known)
                continue
            name = label_of(start, move["id"], ov, base)
            pts.append(dict(label=name, overrides=ov, stage=move["id"], family=family, start=start, scope=scope))
            names.append(name)
        run_points(pts)
        for name in names:
            if not fit.covered(name, scope):
                code = fit.render(name, scope)
                if code not in (0, 1):
                    raise fit.W.Refusal(f"{name}: render exit {code}")
                fit.read(name)
        return names

    def objective(name: str) -> float:
        return summary_of(name)["stages"][scope]["objective"]

    keys = list(fbody.get("leaves", {}))
    if fbody.get("factorial"):
        grids = [(k, fbody["leaves"][k]) for k in keys]
        combos = itertools.product(*[grid_of(spec, current, k.split("+")[0]) for k, spec in grids])
        cands = []
        for values in combos:
            ov = current
            for (k, spec), v in zip(grids, values):
                ov = with_leaf(ov, spec["slot"], {leaf: v for leaf in k.split("+")})
            cands.append(ov)
        names = points_for(cands)
        labels += names
        best = min(names, key=objective)
        return base_overrides(best), labels
    for _ in range(passes):
        before = json.dumps(current, sort_keys=True)
        for k in keys:
            spec = fbody["leaves"][k]
            grid = grid_of(spec, current, k.split("+")[0])
            cands = [with_leaf(current, spec["slot"], {leaf: v for leaf in k.split("+")}) for v in grid]
            names = points_for(cands)
            labels += names
            current = base_overrides(min(names, key=objective))
        if json.dumps(current, sort_keys=True) == before:
            break
    return current, labels


def stage(move_id: str, start: str, base_label: str, passes: int = 2) -> dict:
    if lineage(base_label) != start:
        raise fit.W.Refusal(f"stage {move_id}: base {base_label} is of lineage {lineage(base_label)}, not {start}")
    move = move_of(move_id)
    order = move.get("familyOrder") or list(move["families"])
    families, previous = {}, None
    base = base_overrides(base_label)
    for family in order:
        fbody = move["families"][family]
        current = previous if fbody.get("from") == "previous" and previous is not None else base
        previous, labels = sweep_family(move, family, start, base_label, current, passes)
        families[family] = sorted(set(labels))
    return decide(move, start, families, order)


def scope_tie(label: str, scope: str) -> float:
    """The selection tie on the scope's own cells: the median of log(1 + bar / native) over the
    scope's F u C u P cells, read off a point's cut (it depends on natives and bars alone)."""
    _, t1 = fit.cuts()
    with gzip.open(fit.G1 / "candidates" / label / "cuts.json.gz", "rt") as f:
        cells = json.load(f)["T1"]["cells"]
    sel = [math.log(1 + c["bar"] / c["native"]) for c in cells
           if fit.in_scope(c, scope) and c["stratum"] in t1.SELECTION_STRATA and c["native"] > 0]
    return statistics.median(sel)


def moved_leaves(summary) -> int:
    return sum(len(v) for v in summary["overrides"].values())


def decide(move: dict, start: str, families: dict, order: list, write: bool = True) -> dict:
    """Part 2's selection within a stage (W44's `decide`, on the family's scope)."""
    _, t1 = fit.cuts()
    recovered = {}
    if (PATH / "recovered.json").exists():
        recovered = json.loads((PATH / "recovered.json").read_text())["points"]
    rows = {}
    for fam in order:
        scope = fit.scope_of(move, fam)
        members = [sid for sid in fit.scenes_for(scope) if t1.stratum(sid) in t1.SELECTION_STRATA]
        for label in families.get(fam, []):
            s = summary_of(label)
            objective = s["stages"][scope]["objective"]
            if any(sid not in s["cells"] for sid in members):
                got = recovered.get(label, {}).get(scope)
                if got is None:
                    raise fit.W.Refusal(f"decide {move['id']}: {label} has an UNMEASURED objective member and no "
                                        "recovered reading (recover.py); it is not ranked on a partial median")
                objective = got["declaredObjective"]
            rows.setdefault(fam, []).append(dict(label=label, scope=scope, objective=objective,
                                                 within=s["stages"][scope]["within"], leaves=moved_leaves(s),
                                                 tie=scope_tie(label, scope)))
    landed, how = None, None
    for fam in order:
        inside = [r for r in rows.get(fam, []) if r["within"] == "WITHIN"]
        if inside:
            landed = min(inside, key=lambda r: r["objective"])
            how = f"family {fam} is the first with a point within; its within point with the smallest objective"
            break
    if landed is None:
        every = [r for fam in order for r in rows.get(fam, [])]
        best = min(every, key=lambda r: r["objective"])
        ties = [r for r in every if r["objective"] - best["objective"] <= best["tie"]]
        landed = min(ties, key=lambda r: (r["leaves"], r["objective"]))
        how = ("no family has a point within: the smallest objective across the families, a tie within the "
               f"selection tie ({best['tie']:.4f}) to the fewer moved leaves; recorded as NOT within")
    record = dict(move=move["id"], start=start, landed=landed["label"], how=how, families=rows)
    if write:
        (PATH / start).mkdir(parents=True, exist_ok=True)
        (PATH / start / f"{move['id']}.json").write_text(json.dumps(record, indent=1) + "\n")
    return record


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
        print(json.dumps(record, indent=1)[:4000])
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
