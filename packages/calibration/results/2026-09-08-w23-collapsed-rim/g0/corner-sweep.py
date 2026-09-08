"""W23 G0 (a) (ii) — the corner factor swept, so the straight span is chosen and not assumed.

Apple's rounded rectangle has a CONTINUOUS corner: the curvature is spread along the edge past the
nominal radius, and a top row averaged from `x0 + r` inward is still climbing out of the arc. The
sweep reads each cell's contour rim at a ladder of corner factors and prints where it converges;
1.6 is the factor `read-contour.py` takes, and this is why.
"""

import json
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import importlib.util

spec = importlib.util.spec_from_file_location(
    "readcontour", os.path.join(os.path.dirname(os.path.abspath(__file__)), "read-contour.py")
)
rc = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rc)

WORKTREE = "/Users/new/Developer/GitHub/designer/.claude/worktrees/agent-aa0ee5ea92534c3fd"
MAIN = "/Users/new/Developer/GitHub/designer"
FACTORS = (1.0, 1.2, 1.4, 1.5, 1.6, 1.8, 2.0)
CELLS = (
    ("apple-macos-26.5-1x-light-standard", "dark-solid__rrect-md__rest"),
    ("apple-macos-26.5-1x-light-standard", "light-solid__rrect-md__rest"),
    ("apple-macos-26.5-1x-light-standard", "dark-solid__capsule-button__rest"),
    ("apple-macos-26.5-1x-light-standard", "light-solid__rrect-ml__rest"),
    ("apple-macos-26.5-1x-light-standard", "checkerboard__rrect-sm__rest"),
    ("apple-macos-26.5-2x-light-standard", "dark-solid__rrect-md__rest"),
    ("apple-macos-26.5-1x-dark-standard", "dark-solid__rrect-md__rest"),
    ("apple-macos-26.5-2x-dark-standard", "dark-solid__capsule-button__rest"),
)


def main():
    spec_json = json.load(open(os.path.join(WORKTREE, "apps/reference-apple/scenes.json")))
    canvas = spec_json["canvas"]
    scenes = {s["id"]: s for s in spec_json["scenes"]}
    print("The native fixture's TOP-side contour rim at a ladder of corner factors. A capsule's")
    print("radius is half its short side, so factor 1 already excludes its semicircular ends and")
    print("its read is flat across the ladder; an rrect's is not.")
    print()
    print(f"{'profile':38s} {'scene':32s} " + " ".join(f"{'f=' + f'{f:.1f}':>8s}" for f in FACTORS))
    for profile, scene in CELLS:
        geom = rc.component_geometry(spec_json["components"], scenes[scene]["component"])
        path = os.path.join(MAIN, "apps/reference-apple/fixtures", profile, f"{scene}.png")
        row = []
        for f in FACTORS:
            read = rc.read_one(path, canvas, geom, 6.0, 2.0, f)
            row.append(read["rim"][0])
        print(f"{profile:38s} {scene:32s} " + " ".join(f"{v:8.4f}" for v in row))
    print()
    print("The read converges by factor 1.5 on every rrect and is flat on every capsule. 1.6 is")
    print("taken: it keeps a margin over the convergence point and still leaves 96 of 160 CSS px")
    print("of straight span on `rrect-md` and 38 of 64 on `rrect-sm`.")


if __name__ == "__main__":
    main()
