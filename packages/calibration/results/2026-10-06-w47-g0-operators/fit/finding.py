#!/usr/bin/env python3.12
"""W47 G0 (c): W46 G0's `finding.py` (`results/2026-10-05-w46-g0-declaration/fit/finding.py`), ported by
copy for W47 (charter clause 2, Design "The landing rule"; Decision Log 5): it reads W47's G1 through
W47's `fit.py` and W46's binding of the rule, carried verbatim. W46's committed copy is untouched.
W46's text follows, unchanged; where it says W46 it is W47.

W46 G0 (a): the finding, W45 G0's `finding.py` (`results/2026-10-03-w45-g0-operator/fit/finding.py`)
ported for W46's binding of the landing rule (Decision Log 3; clause 1). W45's committed copy is
untouched. Reads only; writes G1's `fit/path/finding.json` and `finding.txt`.

    python3.12 -B finding.py [LABEL]        (default: joint.py's landed point)

**What W46 changes.** The budget is PER PROFILE (Decision Log 3: "over the whole gated population per
profile"), so a cell spends its own profile's budget and the counts are reported per scale; cells are
keyed `<scale>x <scene>`; the reference column is `d0219cd684bf`'s. The verdict is W46's rule's as the
point's cut records it, per profile, quoted, never re-derived here.

W45's text, unchanged where it applies: a cell spends the budget when it is `away` with g > B (at most
three such cells, none past 3B); under the growth-only partition `away` with g > B is exactly g > B, so
this reads each cell's growth off its cut directly: T1's for F, C and P, a T cell's T1-low's. For every
cell that spends the budget at the point, it reads the same cell at every searched point that rendered
it, so the record says whether any declared point kept that cell within B, and it writes the point's
full per-cell T1 table beside the reference's.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import fit  # noqa: E402

PATH = fit.G1 / "path"
COUNT, CEILING = 3, 3.0


def summary_of(label):
    """A point's composed summary (its scales' cells read off the renderers that measure it)."""
    return json.loads((fit.G1 / "candidates" / label / "summary.json").read_text())


def cells_of(label):
    return {fit.cell_key(c): c for c in summary_of(label)["t1Cells"]}


def growth(c) -> tuple[float, float] | None:
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
    labels = sorted(p.parent.name for p in (fit.G1 / "candidates").glob("*/summary.json"))
    every = {lab: cells_of(lab) for lab in labels}
    spending = {k: spend(c) for k, c in J.items() if spend(c)}
    per_cell = {}
    for k in spending:
        seen = []
        for lab, cells in every.items():
            c = cells.get(k)
            if c is None:
                continue
            g, b = growth(c)
            seen.append(dict(label=lab, ratio=c["candidate"] / c["native"], fidelity=c["fidelity"],
                             growthInB=g / b, spends=spend(c)))
        g, b = growth(J[k])
        per_cell[k] = dict(atPoint=spending[k], growthInB=g / b, native=J[k]["native"], reference=J[k]["reference"],
                           point=J[k]["candidate"], pointsRead=len(seen),
                           pointsWithinB=[x["label"] for x in seen if x["spends"] is None
                                          and not x["label"].startswith("start-")],
                           readings=seen)
    budget = {}
    for scale in fit.SCALES:
        past_b = [k for k in spending if k.startswith(f"{scale}x ")]
        past_3b = [k for k in past_b if spending[k] == "past 3B"]
        budget[f"{scale}x"] = dict(pastB=past_b, past3B=past_3b, withinBudget=len(past_b) <= COUNT and not past_3b)
    table = []
    for k, c in sorted(J.items(), key=lambda kv: (kv[1]["scale"], kv[1]["stratum"], kv[1]["pose"], kv[1]["spanClass"], kv[0])):
        gb = growth(c)
        table.append(dict(cell=k, stratum=c["stratum"], pose=c["pose"], span=c["spanClass"], native=c["native"],
                          reference=c["reference"], point=c["candidate"], fidelity=c["fidelity"],
                          growthInB=None if gb is None else gb[0] / gb[1], spends=spend(c)))
    whole = summary_of(label)
    result = dict(what="W47 G1: the point's T1 map and the growth budget per profile across the search",
                  point=label, budget=dict(count=COUNT, ceilingInB=CEILING, perScale=budget),
                  rule=whole["rule"], ruleProfiles=whole["ruleProfiles"],
                  cells=per_cell, table=table)
    PATH.mkdir(parents=True, exist_ok=True)
    (PATH / "finding.json").write_text(json.dumps(result, indent=1) + "\n")
    lines = [f"point {label}: rule {result['rule']}"]
    for scale, b in budget.items():
        lines.append(f"  {scale}: {len(b['pastB'])} cells past B (count {COUNT}), {len(b['past3B'])} past 3B; "
                     f"budget {'holds' if b['withinBudget'] else 'BROKEN'}")
    for k, v in per_cell.items():
        lines.append(f"  {v['atPoint']:<8} {k:<50} g {v['growthInB']:.2f} B; n {v['native']:.4f} ref {v['reference']:.4f} "
                     f"point {v['point']:.4f}; within B at {len(v['pointsWithinB'])} of {v['pointsRead']} points read")
    lines.append("")
    lines.append(f"{'cell':<52} {'str':<3} {'pose':<8} {'span':<5} {'n':>7} {'ref':>7} {'point':>7} {'g/B':>6}")
    for row in table:
        g = "—" if row["growthInB"] is None else f"{row['growthInB']:6.2f}"
        lines.append(f"{row['cell']:<52} {row['stratum']:<3} {row['pose']:<8} {row['span']:<5} {row['native']:7.4f} "
                     f"{row['reference']:7.4f} {row['point']:7.4f} {g:>6}  {row['fidelity']}"
                     f"{'  ' + row['spends'] if row['spends'] else ''}")
    (PATH / "finding.txt").write_text("\n".join(lines) + "\n")
    print("\n".join(lines[:16]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
