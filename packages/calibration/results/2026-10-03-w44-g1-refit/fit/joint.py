#!/usr/bin/env python3.12
"""W44 G1 step 2, the close of the fit: the joint point, the interactions rule and T1's landing
clauses read on the whole fit map (part 2, `interactions`, `landingRule`).

    python3.12 -B joint.py          writes path/joint.json and path/joint.txt (reads only)

The joint point is move 3's landed candidate: it carries move 1's and move 2's landed leaves
(each move's base is the previous move's landed point). Part 2's interactions rule: "a move UNDID
an earlier one when a cell of the earlier move's `cells` that it left within is a miss at the joint
point" — read here for every earlier move's cells, on T1's fidelity output (a T cell's on its
T1-fine, as the landing reads it). The landing rule's T1 clauses (`t1.landing`) are then read on
the joint point's full fit map, against c05, and beside them each earlier landed point's, so the
path's effect on the vetoes is on the record. A fit render in candidate mode draws the same pixels
strict mode draws for the same content (G0 (f)'s control, and this fit's m1-c05 control: 29 of 29
captures byte-identical to the canonical c05 tree), so this reading is the stage's on these cells.
"""
from __future__ import annotations

import gzip
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "cuts"))
import t1  # noqa: E402

PATH = HERE / "path"


def cut_of(label: str) -> dict:
    with gzip.open(HERE / "candidates" / label / "cuts.json.gz", "rt") as f:
        return json.load(f)["T1"]


def fidelity(c) -> str:
    return c["bands"]["fine"]["fidelity"] if c["stratum"] == "T" and "bands" in c else c["fidelity"]


def main() -> int:
    moves = {m: json.loads((PATH / f"{m}.json").read_text())["landed"] for m in ("move1", "move2", "move3")}
    joint = moves["move3"]
    cut = cut_of(joint)
    scope = {c["scene"]: c for c in cut["cells"] if t1.in_landing_scope(c)}
    missing = [m for m in cut["missing"] if t1.in_landing_scope(m)]
    undone = {}
    for m in ("move1", "move2"):
        at_landing = {c["scene"]: c for c in cut_of(moves[m])["cells"] if t1.in_move(c, m)}
        undone[m] = [s for s, c in at_landing.items() if fidelity(c) == "within"
                     and s in scope and fidelity(scope[s]) != "within"]
    landing = {}
    for m, label in moves.items():
        c = cut_of(label)
        landing[f"{m} {label}"] = {k: c["landing"][k] for k in (
            "verdict", "fAggregate", "fAggregateReference", "fNotWithin", "awayBeyondB", "overshoot",
            "unmeasuredInScope", "regressionBudget", "textCells")}
        landing[f"{m} {label}"]["selectionMetric"] = c["selectionMetric"]
        landing[f"{m} {label}"]["cellsInScope"] = sum(1 for x in c["cells"] if t1.in_landing_scope(x))
    result = dict(
        what="W44 G1 step 2: the joint point, part 2's interactions rule and T1's landing clauses on the full fit map",
        landed=moves, joint=joint, cellsInScope=len(scope), unmeasuredInScope=[m["scene"] for m in missing],
        undone=undone,
        interactionsVerdict=("no move undid an earlier one" if not any(undone.values()) else
                             "a move undid an earlier one: refit once on the union of their cells"),
        landing=landing, jointLanding=landing[f"move3 {joint}"])
    (PATH / "joint.json").write_text(json.dumps(result, indent=1) + "\n")
    lines = [f"joint point {joint} (move 1 {moves['move1']}, move 2 {moves['move2']})",
             f"interactions: {result['interactionsVerdict']} {undone}"]
    for k, v in landing.items():
        lines.append(f"{k}: {v['verdict']}; F aggregate {v['fAggregate']:.4f} vs c05 {v['fAggregateReference']:.4f}; "
                     f"{len(v['fNotWithin'])} F not within; away beyond B {v['awayBeyondB']}; overshoot "
                     f"{v['overshoot']}; selection {v['selectionMetric']:.4f}; {v['cellsInScope']} cells in scope")
    (PATH / "joint.txt").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
