#!/usr/bin/env python3
"""The 26.5 bar per cell, re-derived — W29 acceptance clause 2's table, verified.

    verify-bar-table.py <fixtures/manifest.json>

Clause 2 asks G1 to commit "a table of the 26.5 bar per cell where the manifest's
`bedProvenance` can attribute it … and names the cells it cannot attribute as
such". G0 drafted that table (`results/2026-09-18-w29-g0-preflight/bar-table.md`)
and G1's instruction is to VERIFY it rather than copy it, so this is an
independent derivation: it reads the same committed manifest, counts the same
three kinds of record from scratch, and prints what it found beside what G0
published so the two can be compared line by line.

The three kinds of per-cell record, and only three:

  * `stateFrequencies` — the exact run total for that cell, as the sum of each
    byte-state's `runs`. A cell decided by counting knows how many draws it saw.
  * `recoveredProvenance` with `runsPerCell: 1` — the 2026-08-30 tree re-adopted
    at one run. A bar of one is a bar.
  * neither — nothing per cell.

`bedProvenance` records a publication EVENT's run count and how many cells it
published, but not WHICH cells (except `frequencySettledCells`, which are already
in the first kind). So an unrecorded fixture inherits a bar from an event only
where that inheritance is unambiguous, and the arithmetic that decides it is at
the level of the profile GROUP an event names, not the individual profile.
"""
import json
import sys
from collections import defaultdict

manifest = json.load(open(sys.argv[1]))

PROFILES = [p for p in manifest["profiles"] if p["profileKey"].startswith("apple-macos-26.5-")]

kind = {}            # profileKey/sceneId -> "exact" | "recovered" | "unrecorded"
exact_bar = {}       # profileKey/sceneId -> run total
per_profile = defaultdict(lambda: {"exact": 0, "recovered": 0, "unrecorded": 0, "bars": set()})

for profile in PROFILES:
    key = profile["profileKey"]
    for fixture in profile["fixtures"]:
        cell = key + "/" + fixture["sceneId"]
        freqs = fixture.get("stateFrequencies")
        if freqs:
            total = sum(state["runs"] for state in freqs)
            kind[cell] = "exact"
            exact_bar[cell] = total
            per_profile[key]["exact"] += 1
            per_profile[key]["bars"].add(total)
        elif (fixture.get("recoveredProvenance") or {}).get("runsPerCell") is not None:
            kind[cell] = "recovered"
            per_profile[key]["recovered"] += 1
        else:
            kind[cell] = "unrecorded"
            per_profile[key]["unrecorded"] += 1

events = manifest.get("bedProvenance") or []

print("## Per-cell records over the six 26.5 profiles")
print()
counts = defaultdict(int)
for v in kind.values():
    counts[v] += 1
print("fixtures         %d" % len(kind))
print("exact bar        %d  (stateFrequencies)" % counts["exact"])
print("recovered @1     %d  (recoveredProvenance)" % counts["recovered"])
print("no per-cell bar  %d" % counts["unrecorded"])
print("with a bar       %d" % (counts["exact"] + counts["recovered"]))
print()
print("distinct exact bars seen: %s" % sorted(set(exact_bar.values())))
print()

print("## Per profile")
print()
print("| profile | fixtures | exact | bars seen | recovered @1 | unrecorded |")
print("| --- | ---: | ---: | --- | ---: | ---: |")
for profile in PROFILES:
    key = profile["profileKey"]
    row = per_profile[key]
    print("| %s | %d | %d | %s | %d | %d |" % (
        key, len(profile["fixtures"]), row["exact"],
        ", ".join(str(b) for b in sorted(row["bars"])) or "—",
        row["recovered"], row["unrecorded"]))
print()

print("## Publication events, and the groups of profiles they name")
print()
print("| # | profiles | runs | cells published | frequency-settled cells named |")
print("| ---: | --- | ---: | ---: | ---: |")
for i, e in enumerate(events):
    print("| %d | %s | %s | %s | %d |" % (
        i, " + ".join(p.replace("apple-macos-26.5-", "") for p in e.get("profiles", [])),
        e.get("runs"), e.get("cellsPublished"), len(e.get("frequencySettledCells") or [])))
print()

print("## Where the arithmetic closes, and where it does not")
print()
# The unit of the arithmetic is the CLOSURE of profiles that events link, not the
# profile and not the event's own profile tuple. An event records one
# `cellsPublished` for every profile it names, so a pair event cannot be split
# between its two profiles; and a profile named by both a pair event and a single
# event ties the two together, so an unrecorded cell in either could have come
# from either. Grouping by the event's tuple instead would count one fixture in
# two groups and put more cells in the table than the bed holds.
parent = {p["profileKey"]: p["profileKey"] for p in PROFILES}


def find(x):
    while parent[x] != x:
        parent[x] = parent[parent[x]]
        x = parent[x]
    return x


for e in events:
    named = [p for p in e.get("profiles", []) if p in parent]
    for other in named[1:]:
        parent[find(other)] = find(named[0])

closures = defaultdict(list)
for p in parent:
    closures[find(p)].append(p)

print("| group | fixtures | exact | recovered | unrecorded | event run counts | event cells published | verdict for the unrecorded |")
print("| --- | ---: | ---: | ---: | ---: | --- | ---: | --- |")
attributable_seven = 0
no_bar = 0
for _, members in sorted(closures.items()):
    members = sorted(members)
    touching = [e for e in events if set(e.get("profiles", [])) & set(members)]
    published = sum(e.get("cellsPublished") or 0 for e in touching)
    bars = sorted({e.get("runs") for e in touching})
    fixtures = sum(len(p["fixtures"]) for p in PROFILES if p["profileKey"] in members)
    ex = sum(per_profile[k]["exact"] for k in members)
    rec = sum(per_profile[k]["recovered"] for k in members)
    un = sum(per_profile[k]["unrecorded"] for k in members)
    # `recoveredProvenance` cells are NOT subtracted from what the events
    # published: they were recovered from the 2026-08-30 tree, which predates
    # every event here, so the cells an event published are drawn from the exact
    # ones and the unrecorded ones alone.
    covered = min(un, max(0, published - ex))
    if len(bars) == 1:
        # Every event that touched this group ran at one bar, so an unrecorded
        # cell the events can account for carries that bar as a GROUP statement —
        # "published by one of the events that ran at seven", not "seen seven
        # times", because the event does not name it. Cells beyond what the events
        # say they published at all carry nothing.
        attributable_seven += covered
        no_bar += un - covered
        verdict = "%d of %d attributable at %d as a group statement; **%d short**" % (
            covered, un, bars[0], un - covered)
    else:
        no_bar += un
        verdict = "%d of %d, but at **%d different bars** — nothing chooses" % (
            covered, un, len(bars))
    print("| %s | %d | %d | %d | %d | %s | %d | %s |" % (
        " + ".join(m.replace("apple-macos-26.5-", "") for m in members),
        fixtures, ex, rec, un, ", ".join(str(b) for b in bars), published, verdict))
print()
print("attributable at seven as a group statement: %d" % attributable_seven)
print("no attributable bar at all:                 %d" % no_bar)
print()
print("## G0's published figures, for comparison")
print()
G0 = {"fixtures": 619, "exact": 103, "recovered": 121, "unrecorded": 395,
      "withBar": 224, "groupSeven": 159, "noBar": 236}
mine = {"fixtures": len(kind), "exact": counts["exact"], "recovered": counts["recovered"],
        "unrecorded": counts["unrecorded"],
        "withBar": counts["exact"] + counts["recovered"],
        "groupSeven": attributable_seven, "noBar": no_bar}
print("| figure | G0 | re-derived | agrees |")
print("| --- | ---: | ---: | --- |")
agree = True
for name in G0:
    same = G0[name] == mine[name]
    agree = agree and same
    print("| %s | %d | %d | %s |" % (name, G0[name], mine[name], "yes" if same else "**NO**"))
print()
print("VERDICT: " + ("G0's bar table is confirmed on every figure."
                    if agree else "G0's bar table DISAGREES with this derivation."))
sys.exit(0 if agree else 1)
