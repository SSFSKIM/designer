#!/usr/bin/env python3
"""Cells the declaration carries that the 26.5 bed never published.

    declared-not-published.py <scenes.json> <manifest.json>

Clause 2 asks for the per-profile count to equal the 26.5 count "or the shortfall
named cell by cell". The shortfall exists already, in the other direction: the
declaration carries 624 cells and 619 were ever published, so five cells the 27
bed will attempt have no 26.5 counterpart to be read against. Naming them here
means G2 does not discover them as absences in a diff.
"""
import json
import sys

spec = json.load(open(sys.argv[1]))
manifest = json.load(open(sys.argv[2]))
published = {p["profileKey"]: {f["sceneId"] for f in p["fixtures"]} for p in manifest["profiles"]}

total_declared = 0
missing = []
for p in spec["profiles"]:
    declared = set(p["scenes"])
    total_declared += len(declared)
    have = published.get(p["key"], set())
    for scene in sorted(declared - have):
        missing.append(f"{p['key']}/{scene}")
    for scene in sorted(have - declared):
        missing.append(f"{p['key']}/{scene}  (PUBLISHED BUT NOT DECLARED)")

print(f"declared {total_declared}; published {sum(len(v) for v in published.values())}")
print(f"declared and never published: {len(missing)}")
for m in missing:
    print(f"  {m}")
