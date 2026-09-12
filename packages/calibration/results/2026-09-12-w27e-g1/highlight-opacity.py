#!/usr/bin/env python3
"""The surface highlight layer's own opacity, across the probe corpus and G0's.

Read as a control while settling the label's compositing order (declaration §1.2
item 4), and kept because of what it says: the layer §5.136 §5 read the surface
operator off is the `CASDFKeyFillHighlightEffect` layer, and in the probe corpus
that layer's `opacity` is 0 on every cell. §5.128 records that the bright rim goes
to zero in the receded pose in every profile at both scales, and every probe dump
records `isKeyWindow: false`. This walks both corpora and prints the opacity of
every layer carrying a `vibrantColorMatrix`, keyed by the pose the dump records,
so the coincidence is a reading rather than an impression.

Writes `highlight-opacity.json` beside itself.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
RESULTS = os.path.normpath(os.path.join(HERE, ".."))
OUT = os.path.join(HERE, "highlight-opacity.json")

PROBE = os.path.join(RESULTS, "2026-09-11-w27e-probe")
# The five committed layer-dump trees §5.133 §1 counts as 57 dumps. They are found
# by walking the results tree for dumps that carry a `view` and a `vibrantColorMatrix`
# rather than by naming paths, so a tree that moves does not silently drop out.
DRAWING = "CGDrawingLayer"


def subs(n):
    return n.get("sublayers") or []


def walk(n, out, depth=0):
    out.append(n)
    for c in subs(n):
        walk(c, out, depth + 1)
    return out


def occurrences(doc, path):
    root = doc.get("view", {}).get("layer")
    if root is None:
        return []
    rows = []
    for layer in walk(root, []):
        for f in layer.get("filters", []) or []:
            if f.get("name") != "vibrantColorMatrix":
                continue
            cls = layer.get("class", "")
            role = ("content-label" if DRAWING in cls
                    else "surface-highlight" if layer.get("properties", {})
                    .get("effect", {}).get("class") == "CASDFKeyFillHighlightEffect"
                    else "other")
            rows.append({
                "path": path,
                "scene": doc.get("scene"),
                "colorScheme": doc.get("colorScheme"),
                "backingScaleFactor": doc.get("backingScaleFactor"),
                "isKeyWindow": doc.get("isKeyWindow"),
                "layerClass": cls,
                "layerName": layer.get("name"),
                "role": role,
                "opacity": layer.get("opacity"),
                "isHidden": layer.get("isHidden"),
            })
    return rows


rows = []
for dirpath, _dirnames, filenames in os.walk(RESULTS):
    for name in sorted(filenames):
        if not name.endswith(".json"):
            continue
        p = os.path.join(dirpath, name)
        try:
            doc = json.load(open(p))
        except (ValueError, UnicodeDecodeError):
            continue
        if not isinstance(doc, dict) or "view" not in doc:
            continue
        rows.extend(occurrences(doc, os.path.relpath(p, RESULTS)))

buckets = {}
for r in rows:
    key = (f'{r["role"]} / {r["backingScaleFactor"]}x / '
           f'key={r["isKeyWindow"]} / {r["colorScheme"]}')
    b = buckets.setdefault(key, {"n": 0, "opacities": set(), "hidden": set()})
    b["n"] += 1
    b["opacities"].add(r["opacity"])
    b["hidden"].add(r["isHidden"])

summary = {k: {"n": v["n"], "opacities": sorted(v["opacities"]),
               "isHidden": sorted(v["hidden"])}
           for k, v in sorted(buckets.items())}
json.dump({"summary": summary, "occurrences": rows}, open(OUT, "w"),
          indent=1, sort_keys=True)
json.dump(summary, sys.stdout, indent=1, sort_keys=True)
print()
