#!/usr/bin/env python3.12
"""W45 G0 (b): the close of the fit, W44 G1's `joint.py` ported for W45 (charter Design "The moves",
"Interactions as W44", Decision Log 4, X56; X58). W44's committed copy is untouched. Reads only;
writes G1's `fit/path/joint.json` and `joint.txt`.

    python3.12 -B joint.py [--stages stage1,stage2-thin,stage2-receded]

**Per lineage** (`c05` and `joint`, X56): the path is the stages' landed points in order, each
stage's base the previous stage's landed point, so the last stage's landed point is that path's
joint point. The interactions rule, as W44's: a stage UNDID an earlier one when a cell of the
earlier stage's scope that its landed point left within is a miss at the path's joint point (T1's
fidelity; a T cell's on T1-fine); the undoing stage is refitted once on the union (recorded here as
the verdict; the refit is `search.py`'s).

**Between the two paths** (X56: "the landed point the better by the selection metric on the gate
population"): T1's selection metric over F u C u P of the 2x light WebGPU gate cells
(`t1.selection_metric`) on each path's joint point, read off its FULL fit map (every gate cell; a
path whose joint point lacks one is UNMEASURED and does not land), a tie within the selection tie
(`t1.selection_tie`) going to the fewer moved leaves. Beside it, each joint point's landing-rule
reading as W45's cuts record it (the cut's `rule` block), never re-derived here.
"""
from __future__ import annotations

import gzip
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import fit  # noqa: E402

PATH = fit.G1 / "path"


def cut_of(label: str) -> dict:
    with gzip.open(fit.G1 / "candidates" / label / "cuts.json.gz", "rt") as f:
        return json.load(f)


def fidelity(c) -> str:
    return c["bands"]["fine"]["fidelity"] if c["stratum"] == "T" and "bands" in c else c["fidelity"]


def moved(label: str) -> int:
    spec = json.loads((fit.G1 / "specs" / f"{label}.json").read_text())
    return sum(len(v) for v in spec["overrides"].values())


def path_of(start: str, stages: list[str]) -> dict:
    _, t1 = fit.cuts()
    landed = {}
    for s in stages:
        f = PATH / start / f"{s}.json"
        if not f.exists():
            raise fit.W.Refusal(f"joint: lineage {start} has no decision for {s} ({f})")
        landed[s] = json.loads(f.read_text())["landed"]
    joint = landed[stages[-1]]
    cut = cut_of(joint)["T1"]
    scope = {c["scene"]: c for c in cut["cells"] if t1.in_landing_scope(c)}
    missing = [m["scene"] for m in cut.get("missing", []) if t1.in_landing_scope(m)]
    gate = set(fit.scenes_for("fit"))
    absent = sorted((gate - set(scope)) | set(missing))
    undone = {}
    for i, s in enumerate(stages[:-1]):
        at_landing = {c["scene"]: c for c in cut_of(landed[s])["T1"]["cells"] if fit.in_scope(c, s)}
        later = stages[i + 1:]
        undone[s] = dict(by=later, cells=[sid for sid, c in at_landing.items() if fidelity(c) == "within"
                                          and sid in scope and fidelity(scope[sid]) != "within"])
    metric = t1.selection_metric(cut["cells"]) if not absent else None
    whole = cut_of(joint)
    return dict(start=start, landed=landed, joint=joint, cellsInScope=len(scope), unmeasured=absent,
                undone=undone, interactions=("no stage undid an earlier one" if not any(v["cells"] for v in undone.values())
                                             else "a stage undid an earlier one: refit once on the union of their cells"),
                selectionMetric=metric, selectionTie=t1.selection_tie(cut["cells"]), movedLeaves=moved(joint),
                rule=cut.get("rule", whole.get("rule")))


def main(argv) -> int:
    stages = (argv[argv.index("--stages") + 1] if "--stages" in argv else "stage1,stage2-thin,stage2-receded").split(",")
    paths = {start: path_of(start, stages) for start in fit.STARTS}
    measured = [p for p in paths.values() if p["selectionMetric"] is not None]
    landed, how = None, "no path's joint point carries its full fit map: UNMEASURED, nothing lands"
    if len(measured) == len(paths):
        best = min(measured, key=lambda p: p["selectionMetric"])
        ties = [p for p in measured if p["selectionMetric"] - best["selectionMetric"] <= best["selectionTie"]]
        landed = min(ties, key=lambda p: (p["movedLeaves"], p["selectionMetric"]))
        how = (f"the smaller selection metric on the gate population, a tie within {best['selectionTie']:.4f} "
               "to the fewer moved leaves")
    result = dict(what="W45 G1: the two paths' joint points, the interactions rule and the selection between them",
                  stages=stages, paths=paths, landed=landed and landed["joint"],
                  landedLineage=landed and landed["start"], how=how)
    PATH.mkdir(parents=True, exist_ok=True)
    (PATH / "joint.json").write_text(json.dumps(result, indent=1) + "\n")
    lines = [f"landed: {result['landed']} (lineage {result['landedLineage']}): {how}"]
    for start, p in paths.items():
        metric = "UNMEASURED" if p["selectionMetric"] is None else f"{p['selectionMetric']:.4f}"
        lines.append(f"{start}: joint {p['joint']} via {p['landed']}; selection {metric}; {p['cellsInScope']} cells; "
                     f"{p['interactions']}; rule {json.dumps(p['rule'])[:300] if p['rule'] else 'not in the cut'}")
    (PATH / "joint.txt").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
