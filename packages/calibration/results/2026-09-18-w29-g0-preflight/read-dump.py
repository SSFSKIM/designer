#!/usr/bin/env python3
"""Pull the `glassBackground` filter's declared inputs out of a `dump-layers` JSON.

`dump-layers` walks SwiftUI's Core Animation layer tree and records every filter's
inputs by its own `inputKeys` (README, claims §5.50). The reference implementation's
numbers therefore sit somewhere inside a nested `view` tree whose shape is the layer
tree's, not a flat record — so a reading that wants to compare two dumps has to find
the filter rather than index into it.

Usage:
    read-dump.py <dump.json> [<dump.json> ...]        # print each dump's inputs
    read-dump.py --diff <a.json> <b.json>             # only the inputs that differ
"""
import json
import sys


def filters(node, out=None):
    """Every filter dict in the tree, in walk order, keyed by its recorded type."""
    if out is None:
        out = []
    if isinstance(node, dict):
        if "type" in node and "inputs" in node:
            out.append(node)
        for v in node.values():
            filters(v, out)
    elif isinstance(node, list):
        for v in node:
            filters(v, out)
    return out


def glass_inputs(path):
    d = json.load(open(path))
    found = {}
    for f in filters(d):
        found.setdefault(f.get("type", "?"), {}).update(f.get("inputs") or {})
    return d, found


def flatten(found):
    flat = {}
    for ftype, inputs in found.items():
        for k, v in inputs.items():
            flat[f"{ftype}.{k}"] = v
    return flat


if __name__ == "__main__":
    args = sys.argv[1:]
    if args and args[0] == "--diff":
        a, b = args[1], args[2]
        _, fa = glass_inputs(a)
        _, fb = glass_inputs(b)
        ka, kb = flatten(fa), flatten(fb)
        keys = sorted(set(ka) | set(kb))
        differing = [k for k in keys if ka.get(k, "<absent>") != kb.get(k, "<absent>")]
        print(f"{a}\n{b}\n{len(differing)} of {len(keys)} inputs differ")
        for k in differing:
            print(f"  {k}: {ka.get(k, '<absent>')!r} -> {kb.get(k, '<absent>')!r}")
        sys.exit(0)
    for path in args:
        d, found = glass_inputs(path)
        print(f"== {path}")
        print(f"   os={d.get('os')} scheme={d.get('colorScheme')} scale={d.get('backingScaleFactor')} "
              f"key={d.get('isKeyWindow')} active={d.get('appIsActive')}")
        for k, v in sorted(flatten(found).items()):
            print(f"   {k} = {v}")
