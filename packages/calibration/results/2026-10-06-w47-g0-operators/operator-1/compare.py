"""W47 G0 (a): operator 1's before/after bytes, compared (charter clause 1, Decision Log 2, X57, X65;
claims §5.211). W45's `compare.py` (`results/2026-10-03-w45-g0-operator/operator/`), ported.

`before/cases.json` was recorded by `e2e/gpu/w47-alpha-far.spec.ts`'s recorder on a clean checkout
of 2d0016af2, the commit BEFORE the shader learned the uniform (the two leaves were then unknown
and ignored by `withMaterialOverrides`), twice, byte-identical; `after/cases.json` by the same
recorder on b1b16a3f3, twice, byte-identical. Hashes are SHA-256 over the raw RGBA readback.

- Every case whose far delta RESOLVES to 0 at its own scale (leaf absent, both anchors 0, a
  2x-only delta at dpr 1, a 1x-only delta at dpr 2) and every golden scene must be byte-identical.
- Every case whose delta resolves to non-zero must MOVE (the operator is live), and inside it the
  members at and below the knee (spans 56 and 96) and every pixel outside the four members must be
  byte-identical to the same scene's identity render at the same endpoint; the 128 and 160
  members must move. Read off `after/png/`, which holds every after raster.

    python3.12 -B compare.py  →  compare.txt (exit 1 on any failure)
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

from PIL import Image

HERE = Path(__file__).resolve().parent
before = json.loads((HERE / "before/cases.json").read_text())
after = json.loads((HERE / "after/cases.json").read_text())

# The members' boxes in CSS px (x0, x1, y0, y1), widened by 4 px as the spec widens them.
MEMBERS = {
    "span56": (16, 114, 68, 132), "span96": (131, 279, 48, 152),
    "span128": (301, 459, 32, 168), "span160": (486, 674, 16, 184),
}


def resolved_delta(label: str, patch: dict) -> float:
    if label.startswith("golden/"):
        return 0.0
    return float(patch.get("tintAlphaFar2x" if label.startswith("2x/") else "tintAlphaFar1x", 0))


def png(label: str) -> Image.Image:
    return Image.open(HERE / "after/png" / f"{label.replace('/', '__')}.png").convert("RGBA")


def region_deltas(a: Image.Image, b: Image.Image, dpr: int) -> dict[str, int]:
    pa, pb, (w, h) = a.load(), b.load(), a.size
    worst = {name: 0 for name in [*MEMBERS, "outside"]}
    for y in range(h):
        for x in range(w):
            if pa[x, y] == pb[x, y]:
                continue
            d = max(abs(c1 - c2) for c1, c2 in zip(pa[x, y], pb[x, y]))
            where = next((n for n, (x0, x1, y0, y1) in MEMBERS.items()
                          if x0 * dpr <= x < x1 * dpr and y0 * dpr <= y < y1 * dpr), "outside")
            worst[where] = max(worst[where], d)
    return worst


lines, failures = [], []
for label in before:
    b, a = before[label], after[label]
    same = b["sha256"] == a["sha256"]
    delta = resolved_delta(label, a["patch"])
    if delta == 0:
        role = "identity (delta resolves to 0 at this scale)"
        if not same:
            failures.append(label)
        lines.append(f"{'identical' if same else 'MOVED    '}  {label:44s} {role}  "
                     f"{b['sha256'][:16]} → {a['sha256'][:16]}")
        continue
    # ON: the base is the same scene's identity render at the same endpoint.
    tag, form, endpoint = label.split("/")[:3]
    base = f"{tag}/{form}/{endpoint}"
    worst = region_deltas(png(base), png(label), 2 if tag == "2x" else 1)
    ok = (not same and worst["span56"] == 0 and worst["span96"] == 0 and worst["outside"] == 0
          and worst["span128"] > 0 and worst["span160"] > 0)
    if not ok:
        failures.append(label)
    lines.append(f"{'MOVED    ' if not same else 'identical'}  {label:44s} ON (delta {delta:g}): "
                 f"max channel Δ vs {base}: span56 {worst['span56']}, span96 {worst['span96']}, "
                 f"span128 {worst['span128']}, span160 {worst['span160']}, outside {worst['outside']}"
                 f"{'' if ok else '  FAIL'}")

identity = [line for line in lines if " ON (" not in line]
on = [line for line in lines if " ON (" in line]
lines.append("")
lines.append(f"identity cases byte-identical: {sum(l.startswith('identical') for l in identity)} of {len(identity)}")
lines.append(f"ON cases moved above the knee only: {sum(not l.endswith('FAIL') for l in on)} of {len(on)}")
lines.append(f"failures: {failures if failures else 'none'}")
(HERE / "compare.txt").write_text("\n".join(lines) + "\n")
print("\n".join(lines))
sys.exit(1 if failures else 0)
