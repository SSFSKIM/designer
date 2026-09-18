#!/usr/bin/env python3
"""Seconds per cell, measured on 27, from the probe's own runs.

    timing.py <run-dir> [<run-dir> ...]

The 26.5 record prices a pass at 9.5 s per cell and the charter asks G0 to price
the 27 passes from its own captures rather than from that figure. Two readings are
printed, because they answer different questions:

  * **dwell** — the span from the first cell's `capturedAt` to the last, divided by
    (cells - 1). This is the per-cell cost inside a run: the settle loop, the
    capture, the repeat for the determinism check, and the reset interstitial.
  * **wall** — the run's own measured wall clock (written by the sweep script)
    divided by cells, which also carries the launch, the window presentation and
    the manifest write, and is what a pass actually costs.

A plan priced on dwell alone under-counts by the launch; a plan priced on wall
from a two-cell run over-counts, because the launch is amortised over more cells in
a real pass. Both are printed with the cell count beside them so the fit below can
be read rather than trusted.
"""
import json
import os
import sys
from datetime import datetime

rows = []
for d in sys.argv[1:]:
    path = os.path.join(d, "manifest.json")
    if not os.path.exists(path):
        continue
    m = json.load(open(path))
    times = sorted(datetime.fromisoformat(f["capturedAt"].replace("Z", "+00:00"))
                   for p in m["profiles"] for f in p["fixtures"])
    n = len(times)
    if n < 2:
        continue
    dwell = (times[-1] - times[0]).total_seconds() / (n - 1)
    secs_path = d.rstrip("/") + "/seconds"
    wall = float(open(secs_path).read().strip()) if os.path.exists(secs_path) else None
    rows.append((d, n, dwell, wall))
    print(f"{d}: cells={n} dwell={dwell:.2f}s/cell "
          + (f"wall={wall}s ({wall / n:.2f}s/cell)" if wall else ""))

if rows:
    # A two-point fit of wall = launch + perCell * n over the run sizes present,
    # which is what separates the fixed cost of a run from the per-cell cost.
    sized = {}
    for _, n, _, wall in rows:
        if wall is not None:
            sized.setdefault(n, []).append(wall)
    means = {n: sum(v) / len(v) for n, v in sized.items()}
    print("\nmean wall by cell count:", {n: round(v, 1) for n, v in sorted(means.items())})
    if len(means) >= 2:
        ns = sorted(means)
        lo, hi = ns[0], ns[-1]
        per = (means[hi] - means[lo]) / (hi - lo)
        launch = means[lo] - per * lo
        print(f"fit: wall = {launch:.1f}s + {per:.2f}s x cells   (over n={lo} and n={hi})")
    dwells = [d for _, _, d, _ in rows]
    print(f"dwell per cell: min {min(dwells):.2f} mean {sum(dwells) / len(dwells):.2f} max {max(dwells):.2f}")
