#!/usr/bin/env python3
"""Which profiles of `scenes.json` declare each named scene id.

A `capture` run files a cell for every (profile, scene) pair the declaration
carries and the machine's scale and accessibility mode allow, so the cell count of
a probe run is a property of the declaration rather than of the id list — which is
what decides how long a probe arm takes and what it is a probe OF.
"""
import json
import sys

spec = json.load(open(sys.argv[1]))
ids = sys.argv[2].split(",")
for i in ids:
    holders = [p["key"] for p in spec["profiles"] if i in p["scenes"]]
    print(f"{i}: {len(holders)} profile(s)")
    for h in holders:
        print(f"    {h}")
