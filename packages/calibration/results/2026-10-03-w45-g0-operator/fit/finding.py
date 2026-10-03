#!/usr/bin/env python3.12
"""W45 G0 (b): the finding, W44 G1's `finding.py` ported for W45's landing rule (charter Design "The
landing rule", Decision Log 3, X54; X58). W44's committed copy is untouched. Reads only; writes G1's
`fit/path/finding.json` and `finding.txt`.

    python3.12 -B finding.py [LABEL]        (default: joint.py's landed point)

W45's per-cell clause is error GROWTH alone (X54): a cell spends the budget when it is `away` with
g > B, at most three such cells over the whole population and none past 3B. Under the growth-only
partition `away` with g > B is exactly g > B (g > B >= 2 bar implies |k - c| > bar and g > 0), so
this reads each cell's growth off its cut directly: T1's for F, C and P, a T cell's T1-low's
(W44 Decision Log 7, kept by W45). For every cell that spends the budget at the point, it reads the
same cell at every searched point that rendered it, so the record says whether any declared point
kept that cell within B and at what cost elsewhere; and it writes the point's full per-cell T1
table (2x light WebGPU, the gate cells) beside c05's. The verdict itself is W45's cuts' (`rule`),
quoted, never re-derived here.
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
COUNT, CEILING = 3, 3.0


def cut_of(label):
    """A point's cut, read off its content twin where it is measured by one (`fit.measured_label`)."""
    with gzip.open(fit.G1 / "candidates" / fit.measured_label(label) / "cuts.json.gz", "rt") as f:
        return json.load(f)


def cells_of(label):
    _, t1 = fit.cuts()
    return {c["scene"]: c for c in cut_of(label)["T1"]["cells"] if t1.in_landing_scope(c)}


def growth(c) -> tuple[float, float] | None:
    """(g, B) the budget reads: T1's, or a T cell's T1-low's; None for a T cell with no bands."""
    if c["stratum"] == "T":
        if "bands" not in c:
            return None
        low = c["bands"]["low"]
        return low["growth"], low["B"]
    return c["growth"], c["B"]


def spend(c) -> str | None:
    gb = growth(c)
    if gb is None:
        return None
    g, b = gb
    return "past 3B" if g > CEILING * b else "past B" if g > b else None


def main(argv) -> int:
    label = argv[1] if len(argv) > 1 else json.loads((PATH / "joint.json").read_text())["landed"]
    if label is None:
        raise fit.W.Refusal("finding: joint.py landed nothing; name a point")
    J = cells_of(label)
    labels = sorted(p.parent.name for p in (fit.G1 / "candidates").glob("*/cuts.json.gz"))
    every = {lab: cells_of(lab) for lab in labels}
    spending = {s: spend(c) for s, c in J.items() if spend(c)}
    per_cell = {}
    for s in spending:
        seen = []
        for lab, cells in every.items():
            c = cells.get(s)
            if c is None:
                continue
            g, b = growth(c)
            seen.append(dict(label=lab, ratio=c["candidate"] / c["native"], fidelity=c["fidelity"],
                             growthInB=g / b, spends=spend(c)))
        g, b = growth(J[s])
        per_cell[s] = dict(atPoint=spending[s], growthInB=g / b, native=J[s]["native"], c05=J[s]["reference"],
                           point=J[s]["candidate"], pointsRead=len(seen),
                           pointsWithinB=[x["label"] for x in seen if x["spends"] is None
                                          and not x["label"].startswith("start-")],
                           readings=seen)
    past_b = [s for s, v in spending.items()]
    past_3b = [s for s, v in spending.items() if v == "past 3B"]
    table = []
    for s, c in sorted(J.items(), key=lambda kv: (kv[1]["stratum"], kv[1]["pose"], kv[1]["spanClass"], kv[0])):
        gb = growth(c)
        table.append(dict(scene=s, stratum=c["stratum"], pose=c["pose"], span=c["spanClass"], native=c["native"],
                          c05=c["reference"], point=c["candidate"], fidelity=c["fidelity"],
                          growthInB=None if gb is None else gb[0] / gb[1], spends=spend(c)))
    whole = cut_of(label)
    result = dict(what="W45 G1: the point's T1 map and the growth budget across the search",
                  point=label, budget=dict(count=COUNT, ceilingInB=CEILING, pastB=past_b, past3B=past_3b,
                                           withinBudget=len(past_b) <= COUNT and not past_3b),
                  rule=whole["T1"].get("rule", whole.get("rule")), cells=per_cell, table=table)
    PATH.mkdir(parents=True, exist_ok=True)
    (PATH / "finding.json").write_text(json.dumps(result, indent=1) + "\n")
    lines = [f"point {label}: {len(past_b)} cells past B (count {COUNT}), {len(past_3b)} past 3B (ceiling); "
             f"budget {'holds' if result['budget']['withinBudget'] else 'BROKEN'}"]
    for s, v in per_cell.items():
        lines.append(f"  {v['atPoint']:<8} {s:<46} g {v['growthInB']:.2f} B; n {v['native']:.4f} c05 {v['c05']:.4f} "
                     f"point {v['point']:.4f}; within B at {len(v['pointsWithinB'])} of {v['pointsRead']} points read")
    lines.append("")
    lines.append(f"{'scene':<48} {'str':<3} {'pose':<8} {'span':<5} {'n':>7} {'c05':>7} {'point':>7} {'g/B':>6}")
    for r in table:
        g = "—" if r["growthInB"] is None else f"{r['growthInB']:6.2f}"
        lines.append(f"{r['scene']:<48} {r['stratum']:<3} {r['pose']:<8} {r['span']:<5} {r['native']:7.4f} "
                     f"{r['c05']:7.4f} {r['point']:7.4f} {g:>6}  {r['fidelity']}{'  ' + r['spends'] if r['spends'] else ''}")
    (PATH / "finding.txt").write_text("\n".join(lines) + "\n")
    print("\n".join(lines[:14]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
