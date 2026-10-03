"""W45 G0 (a): the operator's before/after bytes, compared (charter clause 1, X57; claims §5.205).

`before/` was recorded by `e2e/gpu/w45-share-far.spec.ts`'s recorder on the commit BEFORE the shader
learned the far-curve uniform (the leaf was then unknown and ignored by `withMaterialOverrides`);
`after/` by the same recorder on the operator's commit. Every case whose patch does not name the
leaf, or names it at 0, must be byte-identical across the two; the golden scenes at the renderer
default must be byte-identical; and the cases that name a non-zero delta are listed with whether
they moved (they may, on the 2x scene at a live share, and must not anywhere else).

    python3.12 -B compare.py  →  compare.txt (exit 1 on any identity case that moved)
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
before = json.loads((HERE / "before/cases.json").read_text())
after = json.loads((HERE / "after/cases.json").read_text())
FAR = "sizeHeavySecondShareFar2x"

lines, failures = [], []
for label in before:
    b, a = before[label], after[label]
    same = b["sha256"] == a["sha256"]
    delta = a["patch"].get(FAR, 0)
    live = a["patch"].get("sizeHeavySecondShare", 0) != 0
    two_x = a["scene"] == "w45-span-triple"
    if delta == 0:
        role = "identity (delta absent or 0)"
        if not same:
            failures.append(label)
    elif not live:
        role = "share 0: delta unread"
        if not same:
            failures.append(label)
    elif not two_x:
        role = "dpr 1: delta resolves to 0"
        if not same:
            failures.append(label)
    else:
        role = "ON (2x, live share, delta ≠ 0): may move"
    lines.append(f"{'identical' if same else 'MOVED    '}  {label:28s} {role}  {b['sha256'][:16]} → {a['sha256'][:16]}")

identity = [l for l in lines if "may move" not in l]
lines.append("")
lines.append(f"identity cases byte-identical: {sum(l.startswith('identical') for l in identity)} of {len(identity)}")
lines.append(f"failures: {failures if failures else 'none'}")
(HERE / "compare.txt").write_text("\n".join(lines) + "\n")
print("\n".join(lines))
sys.exit(1 if failures else 0)
