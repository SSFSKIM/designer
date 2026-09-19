#!/usr/bin/env python3
"""W29 G3b — the shadow axis of the native delta, per profile and per cell.

    python3 shadow-delta.py [--pose active|inactive] [--profile <27 key substring>]

`native-delta.ts tables` prints one line per metric pooled over the bed, which is
what a per-law verdict needs. A REFIT needs the other cut: the 26.5 and the 27
readings of one cell side by side, so the direction and the size of the move can
be read where the constant it names is identified. That is all this does; the
verdicts and the bar are the instrument's.

Every figure is `native-delta.json`'s. Nothing is recomputed here — a second
opinion about a committed reading is exactly what this project's rules forbid.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent

READINGS = [
    ("shadowMeanDeparture", 5),
    ("shadowFalloffAmplitude", 4),
    ("shadowFalloffSigmaPx", 2),
    ("shadowFalloffLengthPx", 2),
    ("shadowExtentBelowPx", 1),
    ("shadowOffsetYPx", 1),
    ("shadowStrengthPeak", 4),
    ("shadowBackdropSupport", 3),
]

pose = "active"
profile_filter = None
argv = sys.argv[1:]
if "--pose" in argv:
    pose = argv[argv.index("--pose") + 1]
if "--profile" in argv:
    profile_filter = argv[argv.index("--profile") + 1]

rows = json.loads((HERE / "native-delta.json").read_text())["rows"]

selected = [
    r
    for r in rows
    if r.get("pose") == pose
    and (profile_filter is None or profile_filter in r["profileKey27"])
    and any(r.get("readings", {}).get(name) for name, _ in READINGS)
]
selected.sort(key=lambda r: (r["profileKey27"], r["sceneId"]))

header = f"{'27 profile':<50}{'scene':<44}"
for name, _ in READINGS:
    header += f"{name.replace('shadow', ''):>28}"
print(header)
print(f"{'':<94}" + "".join(f"{'26.5    ->      27':>28}" for _ in READINGS))

for r in selected:
    line = f"{r['profileKey27'].replace('apple-macos-27.0-', ''):<50}{r['sceneId']:<44}"
    for name, digits in READINGS:
        pair = r.get("readings", {}).get(name)
        if not pair:
            line += f"{'—':>28}"
            continue
        line += f"{pair[0]:>13.{digits}f}{pair[1]:>15.{digits}f}"
    print(line)

print()
for name, digits in READINGS:
    pairs = [r["readings"][name] for r in selected if r.get("readings", {}).get(name)]
    if not pairs:
        continue
    moves = [b - a for a, b in pairs]
    moves.sort()
    ratios = [b / a for a, b in pairs if a not in (0, None) and abs(a) > 1e-9]
    ratios.sort()
    print(
        f"{name:<28} n={len(pairs):<4} median 26.5 {sorted(a for a, _ in pairs)[len(pairs) // 2]:>12.{digits}f}"
        f"   median 27 {sorted(b for _, b in pairs)[len(pairs) // 2]:>12.{digits}f}"
        f"   median Δ {moves[len(moves) // 2]:>+12.{digits}f}"
        + (f"   median 27/26.5 {ratios[len(ratios) // 2]:>8.3f}" if ratios else "")
    )
