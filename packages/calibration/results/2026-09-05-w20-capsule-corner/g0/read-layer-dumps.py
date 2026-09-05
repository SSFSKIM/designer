"""W20 G0 — what Core Animation says the corner is, per probe scene.

`dump-layers` walks the layer tree SwiftUI commits and records every layer's geometry by runtime
reflection. The shape a `glassEffect` draws is carried on the SDF element layer at the bottom of the
backdrop's tree, so this pulls `cornerRadius` and `cornerCurve` off it for every scene. That is the
reference implementation's own declaration of the corner and it goes first in the findings: a
statement beats an inference from pixels wherever one is available.

Usage: read-layer-dumps.py <layerDumpsDir>
"""

import glob
import json
import os
import sys


def walk(node, out):
    if "SDFElement" in node.get("class", ""):
        out.append(node)
    for child in node.get("sublayers") or []:
        walk(child, out)


def main():
    rows = []
    for path in sorted(glob.glob(os.path.join(sys.argv[1], "*.json"))):
        doc = json.load(open(path))
        elements = []
        walk(doc["view"]["layer"], elements)
        for e in elements:
            rows.append(
                {
                    "scene": doc["scene"],
                    "component": doc["component"],
                    "layer": e["class"],
                    "bounds": [e["frame"]["width"], e["frame"]["height"]],
                    "cornerRadius": e.get("cornerRadius"),
                    "cornerCurve": e.get("cornerCurve"),
                    "mode": e.get("properties", {}).get("mode"),
                    "settleSeconds": doc["settleSeconds"],
                    "isKeyWindow": doc["isKeyWindow"],
                }
            )
    print(json.dumps(rows, indent=1))


if __name__ == "__main__":
    main()
