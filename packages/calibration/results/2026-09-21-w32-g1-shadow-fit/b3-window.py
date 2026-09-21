#!/usr/bin/env python3
"""W32 G1 — B3's own statistic, read over the admitted bands instead of the whole exterior.

    python3 b3-window.py <label>=<exterior-cut.json> [<label>=<...> ...]

**This adopts nothing and re-states nothing** (X4). B3 stays what W30 Decision
Log 3 (a) declared: `|meanDepartureWeb − meanDepartureNative|`, arithmetic mean
over the calibration + validation cells of all six profiles, WebGPU tier,
≤ 0.00035, over the WHOLE exterior. `departure-stat.py` is that reading and this
file does not touch it.

What this file computes is the SAME functional over the SAME 166 cells with the
pixels restricted to the admitted bands — the window `T` and the anchor solve are
taken over — so that "B3 broke" can be said with the decomposition beside it
rather than as a verdict on the fit. It is the evidence a re-statement of B3
would need and it is a reading, not a bound: the number has no bar, and the
Decision Log draft that carries it is the parent's to rule.

The quantity per cell is `exterior-cut.py`'s `window_departure`, read out of a
cut rather than recomputed, and the aggregate is the arithmetic mean of its
absolute difference — B3's own aggregation, cell for cell.

The two poses are printed apart, because Apple's inactive exterior is the `0-3`
band alone (claims §5.166 §7) and pooling a pose whose whole exterior is a rim
with one whose exterior is a shadow is exactly what the decomposition is for.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from statistics import mean

SETS = ("calibration", "validation")


def main(argv) -> int:
    if not argv:
        raise SystemExit(__doc__)
    print("W32 G1 — B3's statistic over the whole exterior and over the admitted bands")
    print("=" * 112)
    print("  the same 166 cells, the same aggregation, two pixel sets. Nothing here is a bound.")
    print()
    print(f"  {'round':<10}{'pose':<10}{'n':>5}{'whole |Δ|':>12}{'window |Δ|':>13}"
          f"{'whole web':>12}{'whole nat':>12}{'win web':>11}{'win nat':>11}")
    for spec in argv:
        label, _, path = spec.partition("=")
        rows = [r for r in json.loads(Path(path).read_text())["rows"]
                if r["tier"] == "webgpu" and r["set"] in SETS
                and r["departure"]["native"] is not None
                and r["departure"]["window"]["native"] is not None]
        for pose, keep in (("active", lambda r: r["state"] != "inactive"),
                           ("inactive", lambda r: r["state"] == "inactive"),
                           ("pooled", lambda r: True)):
            here = [r for r in rows if keep(r)]
            if not here:
                continue
            print(f"  {label:<10}{pose:<10}{len(here):>5}"
                  f"{mean(abs(r['departure']['web'] - r['departure']['native']) for r in here):>12.5f}"
                  f"{mean(abs(r['departure']['window']['difference']) for r in here):>13.5f}"
                  f"{mean(r['departure']['web'] for r in here):>12.5f}"
                  f"{mean(r['departure']['native'] for r in here):>12.5f}"
                  f"{mean(r['departure']['window']['web'] for r in here):>11.5f}"
                  f"{mean(r['departure']['window']['native'] for r in here):>11.5f}")
        print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
