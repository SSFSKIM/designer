#!/usr/bin/env python3
"""Settle the compositing order of the label inside the glass, declaration §1.2 item 3.

The label's `CGDrawingLayer` sits in branch 0 of the `glassEffect`'s `SwiftUI.SDFLayer`,
which is *below* the material's branch 1 in paint order. It is not drawn there: the
`SDFPortalLayer @1` in branch 1 names branch 0's root as its `sourceLayer` and carries
`hidesSourceLayer: 1`, so the label is projected into the material stack between the
backdrop `@0` and the highlight `@2`. This checks that address match on every labelled
dump rather than reading it off one, which is what declaration stop S2 asks for.

Writes `order.json` beside itself.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
STRUCT = json.load(open(os.path.join(HERE, "structure.json")))
OUT = os.path.join(HERE, "order.json")

rows = []
for rec in STRUCT["records"]:
    if rec["drawingLayers"] == 0:
        continue
    for stack in rec["stacks"]:
        branches = stack["topLevelOrder"]
        label_branch = branches[stack["labelBranchIndex"]]
        material = stack["materialOrder"]
        # The material branch's own children, in paint order.
        mat = [m for m in material if m["branch"] != stack["labelBranchIndex"]]
        portal = next((m for m in mat if m["class"] == "SDFPortalLayer"), None)
        backdrop = next((m for m in mat if m["class"] == "CABackdropLayer"), None)
        highlight = next((m for m in mat
                          if m["class"] == "CASDFLayer" and m["filterNames"]), None)
        rows.append({
            "scene": rec["scene"],
            "colorScheme": rec["colorScheme"],
            "labelBranchAddress": label_branch["address"],
            "portalName": portal and portal["name"],
            "portalIndex": portal and portal["index"],
            "portalSourceLayer": portal and portal.get("sourceLayer"),
            "portalHidesSourceLayer": portal and portal.get("hidesSourceLayer"),
            "portalMatchesOpacity": portal and portal.get("matchesOpacity"),
            "portalSourceLayerOpacityScale": portal and portal.get("sourceLayerOpacityScale"),
            "portalProjectsTheLabel": bool(
                portal and portal.get("sourceLayer") == label_branch["address"]),
            "backdropIndex": backdrop and backdrop["index"],
            "backdropFilters": backdrop and backdrop["filterNames"],
            "backdropGroupName": backdrop and backdrop.get("groupName"),
            "backdropAllowsFilteredLuma": backdrop and backdrop.get("allowsFilteredLuma"),
            "backdropGroupNamespace": backdrop and backdrop.get("groupNamespace"),
            "highlightIndex": highlight and highlight["index"],
            "highlightOpacity": highlight and highlight["opacity"],
            "highlightEffect": highlight and highlight.get("effect"),
        })

summary = {
    "labelledStacks": len(rows),
    "portalProjectsTheLabel": sum(1 for r in rows if r["portalProjectsTheLabel"]),
    "orderBackdropPortalHighlight": sum(
        1 for r in rows
        if r["backdropIndex"] == 0 and r["portalIndex"] == 1 and r["highlightIndex"] == 2),
    "portalHidesSourceLayer": sorted({r["portalHidesSourceLayer"] for r in rows}),
    "portalMatchesOpacity": sorted({r["portalMatchesOpacity"] for r in rows}),
    "backdropGroupNames": sorted({r["backdropGroupName"] for r in rows}),
    "backdropAllowsFilteredLuma": sorted({r["backdropAllowsFilteredLuma"] for r in rows}),
    "highlightOpacities": sorted({r["highlightOpacity"] for r in rows}),
    "highlightEffects": sorted({r["highlightEffect"] for r in rows}),
}
json.dump({"summary": summary, "rows": rows}, open(OUT, "w"), indent=1, sort_keys=True)
json.dump(summary, sys.stdout, indent=1, sort_keys=True)
print()
