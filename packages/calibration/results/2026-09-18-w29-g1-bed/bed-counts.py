#!/usr/bin/env python3
"""The 27 bed's counts against the 26.5 bed's, cell by cell — W29 clause 2.

Clause 2: "The per-profile count equals the 26.5 count or the shortfall is named
cell by cell." This reads the published bundle and says, per profile: what the
declaration asked for, what 27 filed, what 26.5 holds, and every id that is in one
bed and not the other. A 27 cell with no 26.5 counterpart is a cell G2 reports
rather than diffs; a 26.5 cell with no 27 counterpart would be a shortfall.

It also checks the two things a count alone cannot: that every PNG on disk has a
manifest entry and every entry a PNG, and that every published cell's `file` field
points at the bytes beside it.
"""
import json
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
FIX = os.path.join(ROOT, "apps/reference-apple/fixtures")
SCENES = os.path.join(ROOT, "apps/reference-apple/scenes.json")

spec = json.load(open(SCENES))
declared = {p["key"]: set(p["scenes"]) for p in spec["profiles"]}
m = json.load(open(os.path.join(FIX, "manifest.json")))
held = {p["profileKey"]: {f["sceneId"] for f in p["fixtures"]} for p in m["profiles"]}

print("| 27 profile | declared | 27 filed | 26.5 held | shortfall | only on 27 |")
print("| --- | ---: | ---: | ---: | ---: | ---: |")
short_total, extra_total = 0, 0
shortfalls, extras = {}, {}
for key in sorted(k for k in held if k.startswith("apple-macos-27.0-")):
    src = key.replace("apple-macos-27.0-", "apple-macos-26.5-").replace("-glass0.5", "")
    d, mine, theirs = declared[key], held[key], held.get(src, set())
    short = sorted(theirs - mine)
    extra = sorted(mine - theirs)
    undeclared = sorted(mine - d)
    missing_declared = sorted(d - mine)
    shortfalls[key], extras[key] = short, extra
    short_total += len(short)
    extra_total += len(extra)
    print("| %s | %d | %d | %d | %d | %d |"
          % (key.replace("apple-macos-27.0-", "").replace("-glass0.5", ""),
             len(d), len(mine), len(theirs), len(short), len(extra)))
    if undeclared:
        print("|   UNDECLARED CELLS FILED: %s |||||" % ", ".join(undeclared))
    if missing_declared:
        print("|   DECLARED BUT NOT FILED: %s |||||" % ", ".join(missing_declared))

print()
print("26.5 cells with no 27 counterpart (the shortfall clause 2 asks to be named): %d" % short_total)
for key, ids in shortfalls.items():
    for i in ids:
        print("  SHORTFALL %s/%s" % (key, i))
print()
print("27 cells with no 26.5 counterpart (G2 reports these rather than diffing them): %d" % extra_total)
for key, ids in extras.items():
    for i in ids:
        print("  ONLY-ON-27 %s/%s" % (key, i))

print()
totals_27 = sum(len(v) for k, v in held.items() if k.startswith("apple-macos-27.0-"))
totals_265 = sum(len(v) for k, v in held.items() if k.startswith("apple-macos-26.5-"))
print("total cells: 27 bed %d, 26.5 bed %d" % (totals_27, totals_265))

# Disk against record, both directions.
problems = []
for p in m["profiles"]:
    key = p["profileKey"]
    d = os.path.join(FIX, key)
    on_disk = {f[:-4] for f in os.listdir(d)} if os.path.isdir(d) else set()
    recorded = {f["sceneId"] for f in p["fixtures"]}
    for i in sorted(on_disk - recorded):
        problems.append("%s/%s: a PNG the manifest does not describe" % (key, i))
    for i in sorted(recorded - on_disk):
        problems.append("%s/%s: a manifest entry with no PNG" % (key, i))
    for f in p["fixtures"]:
        if f.get("file") != "%s/%s.png" % (key, f["sceneId"]):
            problems.append("%s/%s: file field reads %r" % (key, f["sceneId"], f.get("file")))
print()
print("disk-against-record problems: %d" % len(problems))
for x in problems[:20]:
    print("  ! " + x)
sys.exit(1 if problems or short_total else 0)
