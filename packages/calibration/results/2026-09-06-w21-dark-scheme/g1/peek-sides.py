"""W21 G1 scratch reader — the four sides, raw, for whatever cells are asked for.

Kept beside the fit because the first rim read produced a surprise the fit script had no column
for: with `specularGain` 0 the four sides still spread by 0.11–0.15, so the two-light term is not
the only thing that distinguishes them. This prints the peaks themselves rather than their mean.

    peek-sides.py <read.json> [<scene substring>]
"""

import json
import sys

path = sys.argv[1]
needle = sys.argv[2] if len(sys.argv) > 2 else ""
rows = json.load(open(path))["rows"]
print(f"{'scene':40s} {'body':>8s} | {'native T/B/L/R':>31s} | {'web T/B/L/R':>31s}")
for row in rows:
    if needle not in row["scene"] or "bodyWeb" not in row:
        continue
    native = " ".join(f"{value:7.4f}" for value in row["rimNative"])
    web = " ".join(f"{value:7.4f}" for value in row["rimWeb"])
    print(f"{row['scene']:40s} {row['bodyWeb']:8.4f} | {native} | {web}")
