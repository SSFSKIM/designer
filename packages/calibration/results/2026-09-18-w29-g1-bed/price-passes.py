#!/usr/bin/env python3
"""The eight passes of the 27 bed, priced from the declaration and from G0's clock.

    price-passes.py <scenes.json> <fixtures/manifest.json>

G0's `pass-plan.py` priced the passes before the 27 profile keys existed, off the
26.5 declaration; this re-prices them off the 27 keys G1 committed, so the plan
and the file a pass actually reads cannot disagree. The seconds per cell are
G0's measurement on 27 and are not re-measured here (`plan.md`, `timing.py`: 10.09
s/cell over 22 attested scratch runs, against 9.5 s on 26.5).

A PASS is one scale, one accessibility mode and one pose. A CELL is one profile ×
one scene: the unique id count is what `--scenes` carries and the cell count is
what the machine spends, and for the standard passes the two differ because the
light and dark profiles declare overlapping lists.
"""
import json
import sys

SECONDS_PER_CELL = 10.09
LAUNCH_SECONDS = 0.4
RUNS = 7
LOSS = (1.3, 2.5)

spec = json.load(open(sys.argv[1]))
manifest = json.load(open(sys.argv[2]))

state = {s["id"]: s["state"] for s in spec["scenes"]}
REACHABLE = {"active": {"rest", "pressed"}, "inactive": {"inactive"}}
published = {
    p["profileKey"]: {f["sceneId"] for f in p["fixtures"]} for p in manifest["profiles"]
}

profiles27 = [p for p in spec["profiles"] if p["key"].startswith("apple-macos-27.0-")]
by_pass = {}
for pose in ("active", "inactive"):
    for a11y in ("standard", "increased-contrast", "reduced-transparency"):
        members = [p for p in profiles27 if p["a11y"] == a11y]
        for scale in ("1x", "2x"):
            at_scale = [p for p in members if "-%s-" % scale in p["key"]]
            if not at_scale:
                continue
            cells, ids, published_265 = 0, set(), 0
            for p in at_scale:
                declared = list(state) if p["scenes"] == "all" else p["scenes"]
                mine = [i for i in declared if state.get(i) in REACHABLE[pose]]
                cells += len(mine)
                ids.update(mine)
                source = p["key"].replace("apple-macos-27.0-", "apple-macos-26.5-") \
                                 .replace("-glass0.5", "")
                published_265 += len(set(mine) & published.get(source, set()))
            if cells:
                by_pass[(scale, a11y, pose)] = {
                    "profiles": [p["key"] for p in at_scale],
                    "cells": cells, "ids": len(ids), "published265": published_265,
                }

print("| pass (scale x a11y x pose) | profiles | --scenes ids | declared cells | 26.5 published | one run | seven runs | with 1.3-2.5x loss |")
print("| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |")
total_cells = 0
order = [("2x", "standard", "active"), ("2x", "standard", "inactive"),
         ("1x", "standard", "active"), ("1x", "standard", "inactive"),
         ("1x", "increased-contrast", "active"), ("1x", "increased-contrast", "inactive"),
         ("1x", "reduced-transparency", "active"), ("1x", "reduced-transparency", "inactive")]
for key in order:
    row = by_pass[key]
    total_cells += row["cells"]
    one = LAUNCH_SECONDS + SECONDS_PER_CELL * row["cells"]
    seven = one * RUNS / 3600
    print("| %s x %s x %s | %d | %d | %d | %d | %.1f min | %.2f h | %.2f-%.2f h |" % (
        key[0], key[1], key[2], len(row["profiles"]), row["ids"], row["cells"],
        row["published265"], one / 60, seven, seven * LOSS[0], seven * LOSS[1]))

one_round = sum(LAUNCH_SECONDS + SECONDS_PER_CELL * by_pass[k]["cells"] for k in order)
print()
print("passes: %d   declared cells: %d" % (len(order), total_cells))
print("one round over every pass: %.1f min" % (one_round / 60))
print("seven runs:                %.2f h" % (one_round * RUNS / 3600))
print("with 1.3-2.5x attempt loss: %.1f-%.1f h" % (
    one_round * RUNS / 3600 * LOSS[0], one_round * RUNS / 3600 * LOSS[1]))
print()
standard = [k for k in order if k[1] == "standard"]
s_round = sum(LAUNCH_SECONDS + SECONDS_PER_CELL * by_pass[k]["cells"] for k in standard)
print("standard-first (four passes): %.2f h at the bar, %.1f-%.1f h with loss" % (
    s_round * RUNS / 3600, s_round * RUNS / 3600 * LOSS[0], s_round * RUNS / 3600 * LOSS[1]))
a11y = [k for k in order if k[1] != "standard"]
a_round = sum(LAUNCH_SECONDS + SECONDS_PER_CELL * by_pass[k]["cells"] for k in a11y)
print("then the four a11y passes:    %.2f h at the bar, %.1f-%.1f h with loss" % (
    a_round * RUNS / 3600, a_round * RUNS / 3600 * LOSS[0], a_round * RUNS / 3600 * LOSS[1]))
print()
print("declared by a 27 profile and never published on 26.5:")
for key in order:
    row = by_pass[key]
    if row["cells"] != row["published265"]:
        print("  %s x %s x %s: %d declared, %d published on 26.5" % (
            key[0], key[1], key[2], row["cells"], row["published265"]))
