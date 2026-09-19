#!/usr/bin/env python3
"""W29 G3b — the shadow's native delta in one line per 27 profile.

    python3 shadow-per-profile.py > shadow-per-profile.txt

`law-tables.txt` pools the bed; this cuts the same rows by profile, which is the
form the ledger's per-profile sentence and the wave's Tracking Map need. Every
figure is `native-delta.json`'s; nothing is recomputed.

The `moved` column is the instrument's own verdict at the declared bar (beyond
the max of that cell's 27-against-27 pairwise distribution). A row with no bar —
the thirty-two coupled increased-contrast cells, whose raw runs are a sitting the
declared bar does not cover — is counted as unbarred and never as moved.
"""
from __future__ import annotations

import json
import statistics
from pathlib import Path

HERE = Path(__file__).resolve().parent
rows = json.loads((HERE / "native-delta.json").read_text())["rows"]

METRICS = [
    ("shadowMeanDepartureDelta", "shadowMeanDeparture", 5),
    ("shadowFalloffSigmaDeltaPx", "shadowFalloffSigmaPx", 2),
    ("shadowFalloffAmplitudeDelta", "shadowFalloffAmplitude", 4),
    ("shadowExtentBelowDeltaPx", "shadowExtentBelowPx", 1),
    ("shadowOffsetYDeltaPx", "shadowOffsetYPx", 1),
]

profiles = sorted({r["profileKey27"] for r in rows})
for profile in profiles:
    mine = [r for r in rows if r["profileKey27"] == profile and r.get("pose") == "active"]
    print(f"\n── {profile}  ({len(mine)} active pairs) ──")
    for metric, reading, digits in METRICS:
        measured = [r for r in mine if (r.get("metrics") or {}).get(metric) is not None]
        moved = sum(1 for r in measured if (r.get("moved") or {}).get(metric) is True)
        unbarred = sum(1 for r in measured if (r.get("bar") or {}).get(metric) is None)
        pairs = [r["readings"][reading] for r in measured if (r.get("readings") or {}).get(reading)]
        if not pairs:
            print(f"   {metric:<32} {moved}/{len(measured)} moved, no signed reading")
            continue
        before = statistics.median(a for a, _ in pairs)
        after = statistics.median(b for _, b in pairs)
        print(
            f"   {metric:<32} {moved:>3}/{len(measured):<3} moved"
            f"{'' if unbarred == 0 else f' ({unbarred} unbarred)':<16}"
            f"   median {before:>9.{digits}f} -> {after:>9.{digits}f}"
        )
