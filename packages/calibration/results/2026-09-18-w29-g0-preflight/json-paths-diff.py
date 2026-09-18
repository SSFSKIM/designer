#!/usr/bin/env python3
"""Every leaf path at which two JSON documents differ.

Used to say what is left when two `dump-layers` documents agree on every filter
input and still hash differently — so that "not byte-identical" can be reported as
the thing it actually is rather than left as an unexplained negative.
"""
import json
import sys


def leaves(node, prefix="", out=None):
    if out is None:
        out = {}
    if isinstance(node, dict):
        for k, v in node.items():
            leaves(v, f"{prefix}.{k}", out)
    elif isinstance(node, list):
        for i, v in enumerate(node):
            leaves(v, f"{prefix}[{i}]", out)
    else:
        out[prefix] = node
    return out


a = leaves(json.load(open(sys.argv[1])))
b = leaves(json.load(open(sys.argv[2])))
keys = sorted(set(a) | set(b))
diff = [k for k in keys if a.get(k, "<absent>") != b.get(k, "<absent>")]
print(f"{len(diff)} of {len(keys)} leaves differ")
for k in diff[:60]:
    print(f"  {k}: {a.get(k, '<absent>')!r} != {b.get(k, '<absent>')!r}")
