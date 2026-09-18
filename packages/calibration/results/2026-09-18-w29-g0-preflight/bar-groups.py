#!/usr/bin/env python3
"""Event coverage against fixture counts, per group of profiles an event names.

`bedProvenance`'s events name profiles in groups (the two 2x standard profiles
together, the two 1x standard profiles together, and four singles) and record one
`cellsPublished` for the group rather than per profile. So the only arithmetic the
bundle supports is at the group's level, and this prints it: how many cells the
group's events say they published, against how many fixtures the group holds and
how many of those already carry a per-cell record.

The shortfall is the number clause 2's "cells it cannot attribute" turns on.
"""
import json
import sys
from collections import defaultdict

m = json.load(open(sys.argv[1]))
events = m.get("bedProvenance") or []
fixtures_by_profile = {p["profileKey"]: p["fixtures"] for p in m["profiles"]}

groups = defaultdict(list)
for e in events:
    groups[tuple(sorted(e.get("profiles", [])))].append(e)

# A profile can appear in more than one group (a pair event and a single event), so
# groups are merged transitively into the closure a cell could have come from.
parent = {p: p for p in fixtures_by_profile}


def find(x):
    while parent[x] != x:
        parent[x] = parent[parent[x]]
        x = parent[x]
    return x


for key in groups:
    for other in key[1:]:
        parent[find(other)] = find(key[0])

closures = defaultdict(list)
for p in fixtures_by_profile:
    closures[find(p)].append(p)

for root, profiles in closures.items():
    profiles = sorted(profiles)
    published = sum(e.get("cellsPublished", 0) for e in events
                    if set(e.get("profiles", [])) & set(profiles))
    runs = sorted({e.get("runs") for e in events
                   if set(e.get("profiles", [])) & set(profiles)})
    n = sum(len(fixtures_by_profile[p]) for p in profiles)
    exact = sum(1 for p in profiles for f in fixtures_by_profile[p] if "stateFrequencies" in f)
    recovered = sum(1 for p in profiles for f in fixtures_by_profile[p]
                    if "recoveredProvenance" in f)
    unrecorded = n - exact - recovered
    print(f"group {', '.join(profiles)}")
    print(f"  fixtures {n}: exact {exact}, recovered {recovered}, unrecorded {unrecorded}")
    print(f"  events at runs {runs} publishing {published} cells")
    print(f"  unrecorded cells the events could cover at all: "
          f"{max(0, published - exact)} of {unrecorded}"
          f"  (shortfall {max(0, unrecorded - max(0, published - exact))})")
