#!/usr/bin/env python3.12
"""W46 G0 (a): the close of the fit, W45 G0's `joint.py` (`results/2026-10-03-w45-g0-operator/fit/joint.py`)
ported for W46 (charter Design "The moves", Interactions; clause 1). W45's committed copy is
untouched. Reads only; writes G1's `fit/path/joint.json` and `joint.txt`.

    python3.12 -B joint.py [--stages stage1,stage2]

**What W46 changes.** One lineage (`d0219`, Design "The moves": one starting point), so there is no
selection between paths: the joint point is the last stage's landed point. Cells are read at both
scales (keyed `<scale>x <scene>`), and the landing reading is W46's rule as the point's cut records it
(per profile) as the point's composed summary records it (each scale read off the renderer that
measures it; `fit.compose`), quoted, never re-derived here.

W45's text, unchanged where it applies: the path is part 2's stages' landed points in order, read
from the records `search.py stage` writes, each stage's base the previous stage's landed point; a
stage UNDID another when a cell of the other stage's cells that its landed point left within is a
miss at the final point (T1's fidelity; a T cell's on T1-fine); the undoing stage is refitted once on
the union of the two stages' cells (recorded here as the verdict; the refit is `search.py`'s). A path
whose stage records do not chain refuses.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import fit  # noqa: E402

PATH = fit.G1 / "path"


def summary_of(label: str) -> dict:
    """A point's composed summary (since scale-separable rendering a point has no single cut: its
    scales' cuts live with the renderers that measure it, `fit.compose`)."""
    return json.loads((fit.G1 / "candidates" / label / "summary.json").read_text())


def fidelity(c) -> str:
    return c["bands"]["fine"]["fidelity"] if c["stratum"] == "T" and "bands" in c else c["fidelity"]


def moved(label: str) -> int:
    spec = json.loads((fit.G1 / "specs" / f"{label}.json").read_text())
    return sum(len(v) for v in spec["overrides"].values())


def path_of(start: str, stages: list[str]) -> dict:
    r = fit.rule()
    landed, components = {}, {}
    for s in stages:
        f = PATH / start / f"{s}.json"
        if not f.exists():
            raise fit.W.Refusal(f"joint: lineage {start} has no decision for {s} ({f})")
        record = json.loads(f.read_text())
        if record.get("start") != start or record.get("stage") != s:
            raise fit.W.Refusal(f"joint: {f} is not lineage {start}'s {s} record")
        if landed and record.get("base") != landed[stages[stages.index(s) - 1]]:
            raise fit.W.Refusal(f"joint: {start} {s} starts from {record.get('base')}, not the previous stage's "
                                f"landed {landed[stages[stages.index(s) - 1]]}")
        landed[s] = record["landed"]
        components[s] = record.get("components", [])
    joint = landed[stages[-1]]
    whole = summary_of(joint)
    scope = {fit.cell_key(c): c for c in whole["t1Cells"]}
    missing = [fit.cell_key(m) for m in whole["t1Missing"]]
    gate = {f"{sc}x {sid}" for sc in fit.SCALES for sid in fit.scenes_for("fit", sc)
            if fit.cuts()[0].SCENES.by_id[sid]["background"] in fit.cuts()[1].T1_BACKDROPS}
    absent = sorted((gate - set(scope)) | set(missing))
    undone = {}
    for i, s in enumerate(stages[:-1]):
        at_landing = {fit.cell_key(c): c for c in summary_of(landed[s])["t1Cells"] if fit.in_scope(c, s)}
        undone[s] = dict(by=stages[i + 1:], cells=[k for k, c in at_landing.items() if fidelity(c) == "within"
                                                   and k in scope and fidelity(scope[k]) != "within"])
    return dict(start=start, landed=landed, components={s: [dict(family=c["family"], best=c["best"]) for c in v]
                                                        for s, v in components.items()},
                joint=joint, cellsInScope=len(scope), unmeasured=absent, undone=undone,
                interactions=("no stage undid an earlier one" if not any(v["cells"] for v in undone.values())
                              else "a stage undid an earlier one: refit once on the union of their cells"),
                selectionMetric=None if absent else r.selection_metric(whole["t1Cells"]), movedLeaves=moved(joint),
                rule=whole["rule"], ruleProfiles=whole["ruleProfiles"], L1=whole["L1"])


def main(argv) -> int:
    stages = (argv[argv.index("--stages") + 1] if "--stages" in argv else "stage1,stage2").split(",")
    p = path_of(fit.STARTS[0], stages)
    result = dict(what="W46 G1: the joint point of the one lineage and the interactions rule", stages=stages,
                  path=p, landed=None if p["unmeasured"] else p["joint"],
                  how=("the last stage's landed point (one starting point, Design \"The moves\")" if not p["unmeasured"]
                       else "the joint point lacks a fit cell's reading: UNMEASURED, nothing lands"))
    PATH.mkdir(parents=True, exist_ok=True)
    (PATH / "joint.json").write_text(json.dumps(result, indent=1) + "\n")
    lines = [f"landed: {result['landed']}: {result['how']}",
             f"{p['start']}: joint {p['joint']} via {p['landed']}; {p['cellsInScope']} cells; {p['interactions']}; "
             f"rule {p['rule']} {p['ruleProfiles']}; L1 {p['L1']}"]
    (PATH / "joint.txt").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
