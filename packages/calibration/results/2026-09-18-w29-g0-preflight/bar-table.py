#!/usr/bin/env python3
"""The 26.5 bar per cell, as far as the committed manifest can attribute one.

    bar-table.py <manifest.json> [--markdown]

Clause 2 asks G1 to commit a table of the 26.5 bar per cell "where the manifest's
`bedProvenance` can attribute it … and names the cells it cannot attribute as
such". This derives that table from the bundle rather than asserting it, and the
bundle has exactly three kinds of record, measured rather than assumed (see
`probe-manifest-fields.py`, which prints the key sets):

  * **exact** — a fixture carrying `stateFrequencies`, a list of byte-states with
    the number of runs each was seen in. Its bar is the sum of those runs, per
    cell, with no inference at all.
  * **recovered** — a fixture carrying `recoveredProvenance`, the 2026-08-30 tree
    re-adopted at `runsPerCell` (1). A bar of one is a bar; it is not no bar.
  * **unrecorded** — a fixture carrying neither. Its bar can only be inherited
    from a publication event in `bedProvenance`, and an event records COUNTS and
    not ids (except the frequency-settled ones, which are the `stateFrequencies`
    cells). So an unrecorded fixture can be attributed a bar only when every event
    touching its profile ran at the same count, and even then only as far as those
    events' `cellsPublished` reach — which is the arithmetic printed below the
    table, because for four of the six profiles the events run at two different
    counts and the attribution is not unique.

Nothing here is rewritten to what it "should" be: where the arithmetic does not
close, the shortfall is printed as a shortfall.
"""
import json
import sys
from collections import defaultdict

manifest = json.load(open(sys.argv[1]))
markdown = "--markdown" in sys.argv
events = manifest.get("bedProvenance") or []

events_by_profile = defaultdict(list)
for e in events:
    for p in e.get("profiles", []):
        events_by_profile[p].append(e)

rows = []
unattributable = []
for p in manifest["profiles"]:
    key = p["profileKey"]
    exact_bars, recovered, unrecorded = [], 0, []
    for f in p["fixtures"]:
        if "stateFrequencies" in f:
            exact_bars.append(sum(s["runs"] for s in f["stateFrequencies"]))
        elif "recoveredProvenance" in f:
            recovered += 1
        else:
            unrecorded.append(f["sceneId"])
    runs = sorted({e.get("runs") for e in events_by_profile.get(key, [])})
    published = sum(e.get("cellsPublished", 0) for e in events_by_profile.get(key, []))
    unique = len(runs) == 1
    if not unique:
        unattributable.extend(f"{key}/{s}" for s in unrecorded)
    rows.append({
        "profile": key,
        "fixtures": len(p["fixtures"]),
        "exact": len(exact_bars),
        "exactBars": sorted(set(exact_bars)),
        "recovered": recovered,
        "unrecorded": len(unrecorded),
        "eventRunCounts": runs,
        "eventCellsPublished": published,
        "unrecordedAttributable": unique,
    })

if markdown:
    print("| profile | fixtures | exact bar | bars seen | recovered @1 | unrecorded | "
          "event run counts | event cells published |")
    print("| --- | ---: | ---: | --- | ---: | ---: | --- | ---: |")
    for r in rows:
        print(f"| {r['profile']} | {r['fixtures']} | {r['exact']} | "
              f"{', '.join(str(b) for b in r['exactBars']) or '—'} | {r['recovered']} | "
              f"{r['unrecorded']} | {', '.join(str(c) for c in r['eventRunCounts']) or '—'} | "
              f"{r['eventCellsPublished']} |")
else:
    for r in rows:
        print(json.dumps(r, ensure_ascii=False))

print()
print(f"totals: {sum(r['fixtures'] for r in rows)} fixtures — "
      f"exact {sum(r['exact'] for r in rows)}, recovered {sum(r['recovered'] for r in rows)}, "
      f"unrecorded {sum(r['unrecorded'] for r in rows)}")
print(f"publication events: {len(events)}; cells published across them "
      f"{sum(e.get('cellsPublished', 0) for e in events)} "
      f"(an event naming two profiles counts its cells once, across both)")
print(f"profiles whose unrecorded fixtures CAN inherit one run count: "
      f"{[r['profile'] for r in rows if r['unrecordedAttributable']]}")
print(f"unrecorded fixtures in profiles with two event run counts, and therefore "
      f"attributable to no bar: {len(unattributable)}")
if "--list" in sys.argv:
    for c in unattributable:
        print(f"  {c}")
