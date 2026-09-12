#!/usr/bin/env python3
"""Read the labelled probe dumps' complete layer and filter configuration.

W27e G1, declaration §1.2. §5.136 §4 read the label's `vibrantColorMatrix` and its
four inputs; this reads everything around it that decides what the operator *means*:
the whole `filters` array, the absence of `compositingFilter` and `backgroundFilters`
(`Sources/LayerDump.swift` emits both when non-nil, so absence is a measured negative),
the sublayer order inside the `glassEffect`'s `SwiftUI.SDFLayer` — which is CoreAnimation
paint order, snapshotted unmodified by `describeLayer` — the portal layers' source and
`hidesSourceLayer`, and the backdrop layer's group properties.

Writes `structure.json` beside itself. Reads only committed dumps; captures nothing.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
CORPUS = os.path.normpath(os.path.join(HERE, "..", "2026-09-11-w27e-probe"))
OUT = os.path.join(HERE, "structure.json")

SDF_CONTAINER = "SwiftUI.SDFLayer"
DRAWING = "CGDrawingLayer"
PORTAL = "SDFPortalLayer"
BACKDROP = "CABackdropLayer"


def short(cls):
    """A dump's class strings carry Swift's mangled private-name prefixes; the tail
    after the mangling is the readable name and is what the record prints."""
    for marker in (DRAWING, PORTAL):
        if marker in cls:
            return marker
    return cls


def subs(node):
    return node.get("sublayers") or []


def find(node, pred, out):
    if pred(node):
        out.append(node)
    for c in subs(node):
        find(c, pred, out)
    return out


def matrix_of(filt):
    m = filt.get("inputs", {}).get("inputColorMatrix")
    return m.get("float32") if isinstance(m, dict) else None


def describe_filter(filt):
    ins = filt.get("inputs", {})
    return {
        "name": filt.get("name"),
        "type": filt.get("type"),
        "matrix": matrix_of(filt),
        "inputBackdropAware": ins.get("inputBackdropAware"),
        "inputClamp": ins.get("inputClamp"),
        "inputClampPreserveHue": ins.get("inputClampPreserveHue"),
        "declaredInputKeys": filt.get("properties", {}).get("inputKeys"),
        "enabled": filt.get("properties", {}).get("enabled"),
    }


def layer_row(node, index):
    """One sublayer of the glass container, in paint order."""
    row = {
        "index": index,
        "class": short(node.get("class", "")),
        "name": node.get("name"),
        "opacity": node.get("opacity"),
        "isHidden": node.get("isHidden"),
        "masksToBounds": node.get("masksToBounds"),
        "frame": node.get("frame"),
        "bounds": node.get("bounds"),
        "address": (node.get("description") or "").rsplit(" ", 1)[-1].rstrip(">"),
        "filterNames": [f.get("name") for f in node.get("filters", [])],
        "hasCompositingFilter": "compositingFilter" in node,
        "hasBackgroundFilters": "backgroundFilters" in node,
    }
    props = node.get("properties") or {}
    for key in ("hidesSourceLayer", "matchesOpacity", "matchesTransform",
                "sourceLayerOpacityScale", "allowsBackdropGroups"):
        if key in props:
            row[key] = props[key]
    src = props.get("sourceLayer")
    if isinstance(src, dict):
        row["sourceLayer"] = (src.get("description") or "").rsplit(" ", 1)[-1].rstrip(">")
    for key in ("allowsFilteredLuma", "groupName", "groupNamespace", "lumaUpdateRate",
                "allowsInPlaceFiltering", "allowsSubstituteColor"):
        if key in props:
            row[key] = props[key]
    effect = props.get("effect")
    if isinstance(effect, dict):
        row["effect"] = effect.get("class")
    return row


def descends_from(node, target_address):
    """Is `target_address` the address of `node` or of anything under it?"""
    addr = (node.get("description") or "").rsplit(" ", 1)[-1].rstrip(">")
    if addr == target_address:
        return True
    return any(descends_from(c, target_address) for c in subs(node))


def read_dump(path, scheme, scene):
    doc = json.load(open(path))
    root = doc["view"]["layer"]
    containers = find(root, lambda n: n.get("class") == SDF_CONTAINER, [])
    drawings = find(root, lambda n: DRAWING in n.get("class", ""), [])

    rec = {
        "scene": doc.get("scene"),
        "colorScheme": doc.get("colorScheme"),
        "background": doc.get("background"),
        "component": doc.get("component"),
        "backingScaleFactor": doc.get("backingScaleFactor"),
        "isKeyWindow": doc.get("isKeyWindow"),
        "tint": doc.get("tint"),
        "label": doc.get("label"),
        "glassContainers": len(containers),
        "drawingLayers": len(drawings),
    }

    labels = []
    for d in drawings:
        filters = d.get("filters", [])
        labels.append({
            "address": (d.get("description") or "").rsplit(" ", 1)[-1].rstrip(">"),
            "frame": d.get("frame"),
            "opacity": d.get("opacity"),
            "contentsScale": d.get("contentsScale"),
            "filterCount": len(filters),
            "filters": [describe_filter(f) for f in filters],
            "hasCompositingFilter": "compositingFilter" in d,
            "hasBackgroundFilters": "backgroundFilters" in d,
            "emittedKeys": sorted(k for k in d.keys() if k != "sublayers"),
        })
    rec["labelLayers"] = labels

    stacks = []
    for c in containers:
        order = [layer_row(n, i) for i, n in enumerate(subs(c))]
        # Which branch of the container holds the label's drawing layer, and which
        # holds the material. The portal's `sourceLayer` address is matched against
        # the branch that actually contains the drawing layer, so "the label is
        # projected above the material" is read rather than inferred from indices.
        branch_of_label = None
        for i, n in enumerate(subs(c)):
            if find(n, lambda x: DRAWING in x.get("class", ""), []):
                branch_of_label = i
                break
        material = []
        for i, n in enumerate(subs(c)):
            for j, m in enumerate(subs(n)):
                material.append(layer_row(m, j) | {"branch": i})
        stacks.append({
            "containerFrame": c.get("frame"),
            "topLevelOrder": order,
            "labelBranchIndex": branch_of_label,
            "materialOrder": material,
        })
    rec["stacks"] = stacks
    return rec


def main():
    records = []
    for scheme in ("light", "dark"):
        d = os.path.join(CORPUS, scheme)
        for name in sorted(os.listdir(d)):
            if not name.endswith(".json"):
                continue
            records.append(read_dump(os.path.join(d, name), scheme, name[:-5]))

    labelled = [r for r in records if r["drawingLayers"] > 0]
    with_matrix = [r for r in labelled
                   if any(l["filterCount"] > 0 for l in r["labelLayers"])]

    summary = {
        "dumps": len(records),
        "labelled": len(labelled),
        "labelledCarryingAMatrix": len(with_matrix),
        "labelLayersWithACompositingFilter": sum(
            1 for r in labelled for l in r["labelLayers"] if l["hasCompositingFilter"]),
        "labelLayersWithBackgroundFilters": sum(
            1 for r in labelled for l in r["labelLayers"] if l["hasBackgroundFilters"]),
        "labelFilterCounts": sorted({l["filterCount"]
                                     for r in labelled for l in r["labelLayers"]}),
        "labelBranchIndices": sorted({s["labelBranchIndex"]
                                      for r in labelled for s in r["stacks"]
                                      if s["labelBranchIndex"] is not None}),
        "distinctLabelMatrices": sorted({json.dumps(f["matrix"])
                                         for r in labelled for l in r["labelLayers"]
                                         for f in l["filters"] if f["matrix"]}),
    }
    json.dump({"summary": summary, "records": records}, open(OUT, "w"),
              indent=1, sort_keys=True)
    json.dump(summary, sys.stdout, indent=1, sort_keys=True)
    print()


if __name__ == "__main__":
    main()
