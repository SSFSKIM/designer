#!/usr/bin/env python3
"""What the 26.5 bed recorded about the machine and the display it was captured on.

G0 (a) asks whether the BetterDisplay screen came back after the OS update as the
same screen. The only durable record of what it was is the committed manifest, so
this prints that record rather than re-deriving it: the hardware block, and every
distinct `display` block across the six profiles with the profile keys that carry it.
"""
import json
import sys
from collections import defaultdict

manifest = json.load(open(sys.argv[1]))
print("== hardware ==")
print(json.dumps(manifest.get("hardware"), indent=2, ensure_ascii=False))

print("\n== profiles ==")
by_display = defaultdict(list)
for p in manifest["profiles"]:
    d = json.dumps(p.get("display"), sort_keys=True, ensure_ascii=False)
    by_display[d].append(p["profileKey"])
for d, keys in by_display.items():
    print(f"\n{len(keys)} profile(s): {', '.join(sorted(keys))}")
    print(json.dumps(json.loads(d), indent=2, ensure_ascii=False))

print("\n== bedProvenance ==")
prov = manifest.get("bedProvenance")
print(json.dumps(prov, indent=2, ensure_ascii=False)[:6000])
