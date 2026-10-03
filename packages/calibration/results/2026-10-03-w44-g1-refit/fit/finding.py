#!/usr/bin/env python3.12
"""W44 G1 step 2, the finding: the joint point's T1 map, and where in the searched space the
landing rule's vetoes come from (reads only; writes path/finding.json and path/finding.txt).

The landing rule (Decision Log 4) needs, besides an F aggregate at most half of c05's, no cell
`away` with error growth g > B and no cell `overshoot` over F u T u C u P (a T cell's away read on
T1-low, its overshoot on T1-fine). For each cell that vetoes at the joint point, this reads the same
cell at every searched point that rendered it, so the record says whether any declared point the fit
searched kept that cell clear, and at what cost elsewhere. It also writes the joint point's full
per-cell T1 table (2x light WebGPU, the 94 fit cells) beside c05's.
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


def cells_of(label):
    with gzip.open(HERE / "candidates" / label / "cuts.json.gz", "rt") as f:
        cut = json.load(f)["T1"]
    return {c["scene"]: c for c in cut["cells"] if t1.in_landing_scope(c)}


def veto(c):
    r = t1.landing_reads(c)
    if r is None:
        return None
    if r["change"] == "overshoot":
        return "overshoot"
    if r["awayChange"] == "away" and r["awayGrowth"] > r["awayB"]:
        return "away>B"
    return None


def main() -> int:
    joint = json.loads((PATH / "joint.json").read_text())["joint"]
    J = cells_of(joint)
    labels = sorted(p.parent.name for p in (HERE / "candidates").glob("*/cuts.json.gz"))
    every = {lab: cells_of(lab) for lab in labels}
    vetoes = {s: veto(c) for s, c in J.items() if veto(c)}
    per_cell = {}
    for s in vetoes:
        seen = []
        for lab, cells in every.items():
            c = cells.get(s)
            if c is None:
                continue
            seen.append(dict(label=lab, ratio=c["candidate"] / c["native"], fidelity=c["fidelity"],
                             change=c["change"], growth=c["growth"], B=c["B"], veto=veto(c)))
        clear = [x["label"] for x in seen if x["veto"] is None and x["label"] != "m1-c05"]
        per_cell[s] = dict(atJoint=vetoes[s], native=J[s]["native"], c05=J[s]["reference"],
                           joint=J[s]["candidate"], B=J[s]["B"], pointsRead=len(seen),
                           pointsClearOtherThanC05=clear, readings=seen)
    table = []
    for s, c in sorted(J.items(), key=lambda kv: (kv[1]["stratum"], kv[1]["pose"], kv[1]["spanClass"], kv[0])):
        row = dict(scene=s, stratum=c["stratum"], pose=c["pose"], span=c["spanClass"], native=c["native"],
                   c05=c["reference"], joint=c["candidate"], fidelity=c["fidelity"], change=c["change"],
                   growth=c["growth"], B=c["B"], veto=veto(c))
        if "bands" in c:
            row["bands"] = {b: {k: c["bands"][b][k] for k in ("native", "reference", "candidate", "fidelity",
                                                              "change", "growth", "B")} for b in t1.BANDS}
        table.append(row)
    result = dict(what="W44 G1 step 2: the joint point's T1 map and the landing rule's vetoes across the search",
                  joint=joint, vetoes=per_cell, table=table)
    (PATH / "finding.json").write_text(json.dumps(result, indent=1) + "\n")
    lines = [f"joint point {joint}: {len(vetoes)} vetoing cells"]
    for s, v in per_cell.items():
        lines.append(f"  {v['atJoint']:<9} {s:<46} n {v['native']:.4f} c05 {v['c05']:.4f} joint {v['joint']:.4f} "
                     f"B {v['B']:.4f}; read at {v['pointsRead']} points, clear (besides c05) at "
                     f"{len(v['pointsClearOtherThanC05'])}: {', '.join(v['pointsClearOtherThanC05'][:8])}")
    lines.append("")
    lines.append(f"{'scene':<48} {'str':<3} {'pose':<8} {'span':<5} {'n':>7} {'c05':>7} {'joint':>7} "
                 f"{'c/n':>5} {'k/n':>5}  state")
    for r in table:
        lines.append(f"{r['scene']:<48} {r['stratum']:<3} {r['pose']:<8} {r['span']:<5} {r['native']:7.4f} "
                     f"{r['c05']:7.4f} {r['joint']:7.4f} {r['c05'] / r['native']:5.2f} {r['joint'] / r['native']:5.2f}"
                     f"  {r['fidelity']}/{r['change']}{'  VETO ' + r['veto'] if r['veto'] else ''}"
                     + (f"  fine {r['bands']['fine']['fidelity']}/{r['bands']['fine']['change']} low "
                        f"{r['bands']['low']['fidelity']}/{r['bands']['low']['change']}" if 'bands' in r and r['stratum'] == 'T' else ""))
    (PATH / "finding.txt").write_text("\n".join(lines) + "\n")
    print("\n".join(lines[:14]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
