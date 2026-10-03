#!/usr/bin/env python3.12
"""W44 G1 step 2: the declared search, move by move (part 2 as amended, `searchProcedure`,
`selectionRule`, `moves`, `interactions`).

    python3.12 -B search.py move1
    python3.12 -B search.py move2 --base LABEL      (LABEL: move 1's landed point)
    python3.12 -B search.py move3 --base LABEL      (LABEL: move 2's landed point)
    python3.12 -B search.py full LABEL              (the whole fit map at a point: rest-of-fit)
    python3.12 -B search.py table [MOVE]            (every rung's numbers, from the summaries)

Each point is `fit.point` (spec, build, render the move's cells, read every cut against c05). The
renders run one at a time; each read runs in a worker while the next point renders. A point a
family shares with another (B's sigma 20 is A's floor 1, every other byte equal) is rendered once
and recorded under both. The procedure as part 2 declares it: within a family each leaf's grid in
the order listed, the others held at their current values, the smallest move objective kept, at
most two passes; a full factorial sweep of a family's grids is permitted. Family C's leaves start at
c05's share 0 and width 0, where the tap is off and a share sweep is flat by construction, so C is
swept full factorial (4 x 7). The move objective is t1.move_objective (F u C u P of the move's
cells); the within clause is t1.within_clause.
"""
from __future__ import annotations

import json
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import fit  # noqa: E402

PATH = HERE / "path"


def fmt(v):
    return f"{v:g}"


def run_points(points: list[dict]) -> dict:
    """Render every point in order, reading each in a worker; returns label -> summary."""
    for p in points:
        fit.write_spec(p["label"], p["overrides"], p.get("note", ""), p["move"], p["family"])
        fit.build(p["label"])
    out, futures = {}, {}
    with ThreadPoolExecutor(max_workers=2) as pool:
        for p in points:
            summary = HERE / "candidates" / p["label"] / "summary.json"
            if summary.exists() and fit.covered(p["label"], p["scope"]):
                out[p["label"]] = json.loads(summary.read_text())
                continue
            code = fit.render(p["label"], p["scope"])
            if code == 3:
                raise SystemExit(f"census refused before {p['label']}; nothing after it rendered")
            if code not in (0, 1):
                raise SystemExit(f"{p['label']}: render exit {code}")
            futures[p["label"]] = pool.submit(fit.read, p["label"])
        for label, fut in futures.items():
            out[label] = fut.result()
    return out


def move1() -> dict:
    m = fit.PART2["moves"][0]
    pts = [dict(label="m1-c05", overrides={}, move="move1", family="control", scope="move1",
                note="c05 itself under the scratch key: the control, and A's floor 0.6 point")]
    a = m["families"]["A"]["leaves"]["sizeScatterFloor2x"]["grid"]
    for v in a:
        if v == 0.6:
            continue
        pts.append(dict(label=f"m1a-f{fmt(v)}", overrides={"active.light": {"sizeScatterFloor2x": v}},
                        move="move1", family="A", scope="move1"))
    b = m["families"]["B"]["leaves"]["sizeHeavyTapSigma2x"]["grid"]
    for v in b:
        if v == 20:
            continue   # c05's own heavy width: B at 20 is A's floor 1, byte for byte in the patch
        pts.append(dict(label=f"m1b-s{fmt(v)}", overrides={"active.light": {"sizeScatterFloor2x": 1.0,
                                                                               "sizeHeavyTapSigma2x": v}},
                        move="move1", family="B", scope="move1"))
    c = m["families"]["C"]["leaves"]
    for share in c["sizeHeavySecondShare"]["grid"]:
        for width in c["sizeHeavySecondSigma2x"]["grid"]:
            pts.append(dict(label=f"m1c-{fmt(share)}-{fmt(width)}",
                            overrides={"active.light": {"sizeScatterFloor2x": 1.0, "sizeHeavySecondShare": share,
                                                        "sizeHeavySecondSigma2x": width}},
                            move="move1", family="C", scope="move1"))
    got = run_points(pts)
    return decide("move1", got, families={"A": ["m1-c05"] + [p["label"] for p in pts if p["family"] == "A"],
                                          "B": [p["label"] for p in pts if p["family"] == "B"] + ["m1a-f1"],
                                          "C": [p["label"] for p in pts if p["family"] == "C"]},
                  order=m["familyOrder"])


def base_overrides(label: str) -> dict:
    return json.loads((HERE / "specs" / f"{label}.json").read_text())["overrides"]


def with_leaf(base: dict, slot: str, leaves: dict) -> dict:
    out = json.loads(json.dumps(base))
    out.setdefault(slot, {}).update(leaves)
    return out


def label_of(prefix: str, overrides: dict, base: dict) -> str:
    """A readable label from what a point moves beyond its base."""
    parts = []
    for slot, leaves in sorted(overrides.items()):
        for leaf, v in sorted(leaves.items()):
            if base.get(slot, {}).get(leaf) != v:
                short = {"sizeScatterRampStartThin2x": "t", "sizeScatterRampReach2xPx": "r",
                         "sizeScatterRampStartThick2x": "k", "sizeScatterRampStartFar2x": "f",
                         "sizeHeavyTapSigma2x": "s", "sizeHeavySecondShare": "q"}[leaf]
                parts.append(f"{short}{fmt(round(v, 6))}")
    return prefix + ("-" + "-".join(parts) if parts else "-base")


def same_point(overrides: dict) -> str | None:
    """The label of an existing candidate with exactly these overrides (a point already rendered)."""
    for f in sorted((HERE / "specs").glob("*.json")):
        if json.loads(f.read_text())["overrides"] == overrides:
            return f.stem
    return None


def sweep(prefix: str, base_label: str, move: str, family: str, slot: str, leaves: list, grid: list,
          current: dict, scope: str) -> tuple[dict, list]:
    """One coordinate sweep: `leaves` (a tied pair set together) over `grid`, others held at
    `current`. Returns the point with the smallest move objective and every row."""
    base = base_overrides(base_label)
    pts, labels = [], []
    for v in grid:
        ov = with_leaf(current, slot, {leaf: v for leaf in leaves})
        known = same_point(ov)
        if known is not None:
            labels.append(known)
            continue
        label = label_of(prefix, ov, base)
        pts.append(dict(label=label, overrides=ov, move=move, family=family, scope=scope))
        labels.append(label)
    run_points(pts)
    for lab in labels:
        if not fit.covered(lab, scope):
            fit.render(lab, scope)
            fit.read(lab)
    rows = []
    for lab in labels:
        s = json.loads((HERE / "candidates" / lab / "summary.json").read_text())
        rows.append(dict(label=lab, objective=s["moves"][move]["objective"], within=s["moves"][move]["within"],
                         overrides=s["overrides"]))
    best = min(rows, key=lambda r: r["objective"])
    return best, rows


def move2(base_label: str) -> dict:
    m = fit.PART2["moves"][1]
    current = base_overrides(base_label)
    start = m["families"]["start"]["leaves"]["sizeScatterRampStartThin2x"]["grid"]
    best, rows_start = sweep("m2", base_label, "move2", "start", "active.light", ["sizeScatterRampStartThin2x"],
                             start, current, "move2")
    families = {"start": [r["label"] for r in rows_start]}
    if not any(r["within"] == "WITHIN" for r in rows_start):
        reach = m["families"]["reach"]["leaves"]["sizeScatterRampReach2xPx"]["grid"]
        _, rows_reach = sweep("m2", base_label, "move2", "reach", "active.light", ["sizeScatterRampReach2xPx"],
                              reach, best["overrides"], "move2")
        families["reach"] = [r["label"] for r in rows_reach]
    got = {lab: json.loads((HERE / "candidates" / lab / "summary.json").read_text())
           for fam in families.values() for lab in fam}
    return decide("move2", got, families=families, order=["start", "reach"])


def move3(base_label: str, passes: int = 2) -> dict:
    m = fit.PART2["moves"][2]
    fam = m["families"]["receded"]["leaves"]
    current = base_overrides(base_label)
    active_share = current.get("active.light", {}).get("sizeHeavySecondShare", 0)
    order = [(["sizeScatterRampStartThin2x"], fam["sizeScatterRampStartThin2x"]["grid"]),
             (["sizeScatterRampStartThick2x", "sizeScatterRampStartFar2x"],
              fam["sizeScatterRampStartThick2x+sizeScatterRampStartFar2x"]["grid"]),
             (["sizeHeavyTapSigma2x"], fam["sizeHeavyTapSigma2x"]["grid"])]
    if active_share > 0:
        order.append((["sizeHeavySecondShare"],
                      [round(f * active_share, 6) for f in fam["sizeHeavySecondShare"]["grid"]]))
    labels, history = [], []
    for n in range(passes):
        before = json.dumps(current, sort_keys=True)
        for leaves, grid in order:
            best, rows = sweep("m3", base_label, "move3", "receded", "receded.light", leaves, grid, current, "move3")
            history.append(dict(passNumber=n + 1, leaves=leaves, best=best["label"], objective=best["objective"],
                                rows=[dict(label=r["label"], objective=r["objective"], within=r["within"])
                                      for r in rows]))
            labels += [r["label"] for r in rows]
            current = best["overrides"]
        if json.dumps(current, sort_keys=True) == before:
            break
    got = {lab: json.loads((HERE / "candidates" / lab / "summary.json").read_text()) for lab in set(labels)}
    record = decide("move3", got, families={"receded": sorted(set(labels))}, order=["receded"])
    record["sweeps"] = history
    (PATH / "move3.json").write_text(json.dumps(record, indent=1) + "\n")
    return record


def moved_leaves(summary) -> int:
    return sum(len(v) for v in summary["overrides"].values())


def move_tie(label: str, move: str) -> float:
    """Part 2's selection tie on the move objective's own cells ("the median over the same cells of
    log(1 + bar / native)"): the move's F u C u P cells, read off a point's cut. It depends on the
    cells' natives and bars alone, so every point of the move gives the same value. (Until the
    review of G1 steps 0-2 the decision read each summary's `selectionTie`, which is over every
    cell the point had rendered: the move's cells when the move was decided, the whole fit map once
    the landed point's map was completed afterwards.)"""
    import gzip
    import math
    import statistics
    with gzip.open(HERE / "candidates" / label / "cuts.json.gz", "rt") as f:
        cells = json.load(f)["T1"]["cells"]
    sel = [math.log(1 + c["bar"] / c["native"]) for c in cells
           if fit.t1.in_move(c, move) and c["stratum"] in fit.t1.SELECTION_STRATA and c["native"] > 0]
    return statistics.median(sel)


def decide(move: str, got: dict, families: dict, order: list, write: bool = True) -> dict:
    """Part 2's selection within a move: the first family in order with a searched point that passes
    the move's within clause lands, at its within point with the smallest move objective; if none
    is within, the point with the smallest objective across the families, a tie (within the
    selection tie) to the fewer moved leaves, recorded as not within."""
    rows = {}
    members = [sid for sid in fit.scenes_for(move) if fit.t1.stratum(sid) in fit.t1.SELECTION_STRATA]
    recovered = json.loads((PATH / "recovered.json").read_text())["points"] if (PATH / "recovered.json").exists() else {}
    for fam in order:
        for label in families.get(fam, []):
            s = got.get(label) or json.loads((HERE / "candidates" / label / "summary.json").read_text())
            objective = s["moves"][move]["objective"]
            # The review of G1 steps 0-2 (P2): an objective is the declared statistic only over ALL of
            # the move's F u C u P cells. A point with an UNMEASURED member is ranked on its value
            # recovered through G0's port (recover.py) or not at all.
            if any(sid not in s["cells"] for sid in members):
                if label not in recovered:
                    raise SystemExit(f"decide {move}: {label} has an UNMEASURED objective member and no "
                                     "recovered reading (recover.py); it is not ranked on a partial median")
                objective = recovered[label]["declaredObjective"]
            rows.setdefault(fam, []).append(dict(label=label, objective=objective,
                                                 within=s["moves"][move]["within"], leaves=moved_leaves(s),
                                                 tie=move_tie(label, move)))
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
        how = ("no family has a point within: the smallest move objective across the families, a tie "
               f"within the selection tie ({best['tie']:.4f}) to the fewer moved leaves; recorded as NOT within")
    record = dict(move=move, landed=landed["label"], how=how, families=rows)
    if write:
        PATH.mkdir(exist_ok=True)
        (PATH / f"{move}.json").write_text(json.dumps(record, indent=1) + "\n")
    return record


def table(move: str | None = None) -> str:
    lines = []
    for f in sorted((HERE / "candidates").glob("*/summary.json")):
        s = json.loads(f.read_text())
        if move and s["move"] != move:
            continue
        ov = "; ".join(f"{slot.split('.')[0]} {k}={v:g}" for slot, kv in s["overrides"].items() for k, v in kv.items())
        objs = " ".join(f"{m}={v['objective']:.4f}{'*' if v['within'] == 'WITHIN' else ''}"
                        if v["objective"] is not None else f"{m}=—" for m, v in s["moves"].items())
        lines.append(f"{s['label']:<20} {s['move']}/{s['family']:<8} {objs}  sel={s['selectionMetric'] or 0:.4f}  "
                     f"[{ov}]")
    return "\n".join(lines) + "\n"


def main(argv) -> int:
    fit.preflight()
    verb = argv[1] if len(argv) > 1 else ""
    if verb == "move1":
        print(json.dumps(move1(), indent=1)[:3000])
        return 0
    if verb == "move2":
        print(json.dumps(move2(argv[argv.index("--base") + 1]), indent=1)[:4000])
        return 0
    if verb == "move3":
        print(json.dumps(move3(argv[argv.index("--base") + 1]), indent=1)[:4000])
        return 0
    if verb == "full":
        label = argv[2]
        code = fit.render(label, "rest-of-fit")
        if code not in (0, 1):
            return code
        s = fit.read(label)
        print(json.dumps({k: s[k] for k in ("label", "moves", "selectionMetric", "landing")}, indent=1))
        return 0
    if verb == "table":
        print(table(argv[2] if len(argv) > 2 else None))
        return 0
    print(__doc__)
    return 64


if __name__ == "__main__":
    sys.exit(main(sys.argv))
