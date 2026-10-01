"""W43 G2 (1): what the declared bar says on pairs whose true slider change is zero.

Reads the two measured rehearsal files ``slider-delta pairs`` wrote (``rehearsal/``):
- ``null-pairs-measured.json``: G1a's 0.5 bridge captures (side bundle) against their 0.5 fixtures;
- ``w29-state-pairs-measured.json``: W29's own minority states against their 0.5 fixtures.

Per metric: pairs measured, pairs the declared bar calls moved, and the largest value; per cell, the
metrics that moved. Every "moved" on these pairs is a misreading the bar would make on a cell whose
slider change is zero, so the per-law rule (``verdicts.py``) is also run over them.

    python3.12 -B rehearse.py   # writes rehearsal/rehearse.txt
"""

from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
R = HERE / "rehearsal"


def summarise(path: Path, title: str, out: list[str]) -> None:
    doc = json.loads(path.read_text())
    rows = doc["rows"]
    metrics = doc["metrics"]
    out.append(f"## {title}: {len(rows)} pairs ({path.name})")
    out.append("")
    groups = defaultdict(list)
    for row in rows:
        groups[row["label"].split(":")[0]].append(row)
    for group, subset in sorted(groups.items()):
        cells_moved = [r for r in subset if any(r["moved"].values())]
        out.append(f"### {group}: {len(subset)} pairs; pairs with any metric moved: {len(cells_moved)}")
        out.append(f"{'metric':<36} {'moved/measured':>15} {'max value':>11} {'max value/bar':>14}")
        for metric in metrics:
            measured = [r for r in subset if r["metrics"].get(metric) is not None and metric in r["bar"]]
            if not measured:
                continue
            moved = [r for r in measured if r["moved"].get(metric)]
            top = max(r["metrics"][metric] for r in measured)
            ratio = max(
                (r["metrics"][metric] / r["bar"][metric]) if r["bar"][metric] > 0 else (float("inf") if r["metrics"][metric] > 0 else 0.0)
                for r in measured
            )
            if moved or top > 0:
                out.append(f"{metric:<36} {f'{len(moved)}/{len(measured)}':>15} {top:>11.3e} {ratio:>14.3e}")
        out.append("")
        out.append("Per pair with any metric moved (label: the metrics moved):")
        per_cell = Counter()
        for r in cells_moved:
            names = sorted(m for m, v in r["moved"].items() if v)
            per_cell[(r["profileKey"].replace("-glass0.25", ""), r["sceneId"])] += 1
            out.append(f"  {r['label']}  [{len(names)}] {', '.join(names)}")
        out.append("")
        if per_cell:
            out.append("Distinct cells among them: " + ", ".join(f"{p.split('27.0-')[1]}/{s} x{n}" for (p, s), n in sorted(per_cell.items())))
            out.append("")


def main() -> None:
    out: list[str] = ["# The declared bar on pairs whose slider change is zero (W43 G2, bar-declaration.md §6)", ""]
    summarise(R / "null-pairs-measured.json", "(b) the bridge null: side bundle at 0.5 against the 0.5 fixtures", out)
    summarise(R / "w29-state-pairs-measured.json", "(c) the positive control: W29's minority states against their fixtures", out)
    (R / "rehearse.txt").write_text("\n".join(out) + "\n")
    print("\n".join(out))


if __name__ == "__main__":
    main()
