"""W26 G3 — the per-group OKLab dE mean, the 0.14.0 bed beside the landed one.

The gate reads bounds and floors per CELL; this is the same bed read per GROUP, which is where a
change that is small everywhere and one that is large somewhere look different. It is G2b's
`g2b-delta-e.txt` over the CANONICAL matrices rather than over a rung's, so the landing reproduces
the declaring child's table on the bytes that ship. Probe rows are dropped: they are gated by
nothing (W25 Decision Log 3 (e)).

    g3-delta-e.py <before matrix.json> <after matrix.json> > g3-delta-e.txt
"""

import json
import sys
from collections import defaultdict


def groups(path):
    out = defaultdict(list)
    for cell in json.load(open(path))["cells"]:
        if cell["fixtureSet"] == "probe":
            continue
        entry = (cell.get("perceptual") or {}).get("oklabDeltaEMean")
        if isinstance(entry, dict):
            out[(cell["key"]["profileKey"], cell["key"]["web"]["renderer"],
                 cell["fixtureSet"])].append(entry["value"])
    return {k: (sum(v) / len(v), len(v)) for k, v in out.items()}


def main():
    before, after = groups(sys.argv[1]), groups(sys.argv[2])
    print("W26 G3 — the per-group OKLab dE mean, the 0.14.0 bed -> the landed bed")
    print("=" * 108)
    print(f"{'profile / renderer / set':70s} {'n':>4s} {'0.14.0':>9s} {'landed':>9s} {'delta':>9s}")
    worst = None
    for key in sorted(set(before) | set(after)):
        mb, _ = before.get(key, (float("nan"), 0))
        ma, na = after.get(key, (float("nan"), 0))
        print(f"{' / '.join(key):70s} {na:4d} {mb:9.5f} {ma:9.5f} {ma - mb:+9.5f}")
        if worst is None or ma - mb > worst[1]:
            worst = (key, ma - mb)
    print()
    print(f"worst group rise: {' / '.join(worst[0])}  {worst[1]:+.5f}")


if __name__ == "__main__":
    main()
