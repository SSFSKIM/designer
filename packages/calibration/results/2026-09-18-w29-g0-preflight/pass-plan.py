#!/usr/bin/env python3
"""The 27 bed's passes, priced from G0's own measured seconds per cell.

    pass-plan.py <scenes.json> <manifest.json> <seconds-per-cell> [--markdown]

A pass is one scale, one accessibility mode and one pose — the unit `run-sitting.sh`
takes, because the accessibility mode is read-only and set in System Settings and
the pose is a launch-time property of the process. The declaration fixes the cells:
a profile's `scenes` list intersected with the pose's states (`rest` and `pressed`
for an active pass, `inactive` for the recede).

Priced at the seven-run bar clause 2 declares, at the seconds per cell G0 measured
on 27 rather than the 9.5 s the 26.5 record quotes, and with the W27 sitting's own
attempt-loss multiplier (1.3–2.5x) carried rather than dropped — a pass is refused
at its opening idle gate often enough that the multiplier is part of the price.
"""
import json
import sys

spec = json.load(open(sys.argv[1]))
manifest = json.load(open(sys.argv[2]))
per_cell = float(sys.argv[3])
markdown = "--markdown" in sys.argv

state_of = {s["id"]: s.get("state") for s in spec["scenes"]}
published = {p["profileKey"]: {f["sceneId"] for f in p["fixtures"]} for p in manifest["profiles"]}

POSES = {"active": {"rest", "pressed"}, "inactive": {"inactive"}}

passes = {}
for p in spec["profiles"]:
    key = p["key"]
    scale = 2 if "-2x-" in key else 1
    a11y = p["a11y"]
    for pose, states in POSES.items():
        ids = [i for i in p["scenes"] if state_of.get(i) in states]
        if not ids:
            continue
        passes.setdefault((scale, a11y, pose), {"cells": 0, "profiles": [], "published": 0})
        entry = passes[(scale, a11y, pose)]
        entry["cells"] += len(ids)
        entry["profiles"].append(key)
        entry["published"] += len(published.get(key, set()) & set(ids))

total_cells = sum(e["cells"] for e in passes.values())
total_published = sum(e["published"] for e in passes.values())

if markdown:
    print("| pass (scale x a11y x pose) | profiles | declared cells | 26.5 published | "
          "one run | seven runs | with 1.3-2.5x attempt loss |")
    print("| --- | --- | ---: | ---: | ---: | ---: | --- |")
for (scale, a11y, pose), e in sorted(passes.items()):
    one = e["cells"] * per_cell
    seven = one * 7
    lo, hi = seven * 1.3, seven * 2.5
    name = f"{scale}x x {a11y} x {pose}"
    if markdown:
        print(f"| {name} | {', '.join(sorted(e['profiles']))} | {e['cells']} | {e['published']} | "
              f"{one / 60:.1f} min | {seven / 3600:.2f} h | {lo / 3600:.2f}-{hi / 3600:.2f} h |")
    else:
        print(f"{name}: cells={e['cells']} published26.5={e['published']} "
              f"one-run={one / 60:.1f}min seven={seven / 3600:.2f}h "
              f"loss-adjusted={lo / 3600:.2f}-{hi / 3600:.2f}h")

one = total_cells * per_cell
seven = one * 7
print(f"\n{len(passes)} passes, {total_cells} declared cells "
      f"({total_published} of them published on 26.5), at {per_cell:.2f} s/cell:")
print(f"  one round over every pass: {one / 60:.1f} min")
print(f"  seven runs: {seven / 3600:.2f} h")
print(f"  with the W27 record's 1.3-2.5x attempt loss: {seven * 1.3 / 3600:.1f}-{seven * 2.5 / 3600:.1f} h")
