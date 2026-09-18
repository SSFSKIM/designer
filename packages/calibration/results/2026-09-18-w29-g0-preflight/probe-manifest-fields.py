#!/usr/bin/env python3
"""What the committed bundle records per fixture about how it was published.

Prints the distinct key sets fixtures carry and one example of each provenance
field's value, so the bar table is built against the bundle's real shape rather
than against a remembered one.
"""
import json
import sys
from collections import Counter

m = json.load(open(sys.argv[1]))
shapes = Counter()
examples = {}
for p in m["profiles"]:
    for f in p["fixtures"]:
        prov = tuple(sorted(k for k in f if "rovenance" in k or "requenc" in k or "uns" in k))
        shapes[prov] += 1
        for k in prov:
            examples.setdefault(k, json.dumps(f[k], ensure_ascii=False)[:300])

for shape, n in shapes.most_common():
    print(f"{n:5d} fixtures carry {shape or '()'}")
print()
for k, v in sorted(examples.items()):
    print(f"{k} example: {v}")
