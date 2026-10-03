#!/usr/bin/env python3.12
"""W45 G0 (b): the cuts port, tested on c05 before use (charter clause 2, X58).

W44 G1 cut the published c05 generation against itself (`results/2026-10-03-w44-g1-refit/
references/c05-cuts.json`). W45's port cut the same generation, against the same reference and the
same canonical capture tree (`c05-cuts.json.gz` beside this file). Every field the two have in common
must be equal; the only differences allowed are the ones the port adds by name: `what`,
`cutsSource` (W45's files), T1's `rule` and `stages`, and the summary's W45 line. One more field
differs and is not the port's: `ownerTest.sha256`, the hash of `adopted-thresholds.test.ts`, which
moved after W44 G1 cut c05 (W44 G2 adopted T1 there; W45 G0 (a) added the clause (b) exception).
What the cuts READ from that file — the adopted rows' bounds, parsed into `tables` — is compared
like every other field and must be equal.

    python3.12 -B port-proof.py   →  port-proof.txt; exit 1 on any other difference
"""
import gzip
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
RESULTS = HERE.parents[1]
w44 = json.loads((RESULTS / "2026-10-03-w44-g1-refit/references/c05-cuts.json").read_text())
w45 = json.loads(gzip.open(HERE / "c05-cuts.json.gz").read())
ADDED = {("what",), ("cutsSource",), ("T1", "rule"), ("T1", "stages"),
         ("summary", "W45 rule (T1, 2x light WebGPU)")}
MOVED_SINCE = {("ownerTest", "sha256")}

diffs, moved, compared = [], [], [0]


def walk(a, b, path):
    if path in ADDED:
        return
    if path in MOVED_SINCE:
        moved.append(f"{'/'.join(path)}: W44 {a!r}, W45 {b!r} (the owner test moved since W44 G1)")
        return
    if isinstance(a, dict) and isinstance(b, dict):
        for k in sorted(set(a) | set(b)):
            if (*path, k) in ADDED:
                continue
            if k not in a or k not in b:
                diffs.append(f"{'/'.join(path + (k,))}: only in {'W45' if k in b else 'W44'}")
                continue
            walk(a[k], b[k], path + (k,))
    elif isinstance(a, list) and isinstance(b, list):
        if len(a) != len(b):
            diffs.append(f"{'/'.join(path)}: {len(a)} items in W44, {len(b)} in W45")
            return
        for i, (x, y) in enumerate(zip(a, b)):
            walk(x, y, path + (str(i),))
    else:
        compared[0] += 1
        if a != b and not (isinstance(a, float) and isinstance(b, float) and a != a and b != b):
            diffs.append(f"{'/'.join(path)}: W44 {a!r}, W45 {b!r}")


walk(w44, w45, ())
lines = [f"leaves compared: {compared[0]}", f"differences outside the port's named additions: {len(diffs)}"]
lines += [f"  {d}" for d in diffs[:50]]
lines += [f"named, not the port's: {m}" for m in moved]
lines.append(f"W44 cutsSource: {w44['cutsSource']}")
lines.append(f"W45 cutsSource: {w45['cutsSource']}")
lines.append(f"W45 rule on c05 against itself: {w45['T1']['rule']['verdict']}")
(HERE / "port-proof.txt").write_text("\n".join(lines) + "\n")
print("\n".join(lines))
sys.exit(1 if diffs else 0)
