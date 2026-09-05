"""W20 G0: the declaration-conformance readings over the bed, grouped so the defect is legible.

Reads the scratch matrix `g0-conformance-run.sh` writes and prints, per profile and tier, the
conformance rows by COMPONENT — the capsule and the toolbar group on one side, the rounded
rectangles and the stack on the other — because that is the split the defect follows and a
per-scene list of two hundred rows is not a reading of anything.

Cells whose rows are absent are counted and named rather than skipped: absent means the
capture was missing or the tier refused the alpha rule, and both are facts about the
instrument that the table has to carry.

    python3 g0-bed-table.py <matrix.json>
"""
import collections
import json
import sys


def component_of(scene_id: str) -> str:
    return scene_id.split("__")[1]


def value(cell, field):
    shape = cell.get("shape")
    if shape is None:
        return None
    entry = shape.get(field)
    return None if entry is None else entry["value"]


def main() -> None:
    matrix = json.load(open(sys.argv[1]))
    print(f"schemaVersion {matrix['schemaVersion']}, {len(matrix['cells'])} cells\n")

    rows = collections.defaultdict(list)
    absent = collections.defaultdict(list)
    for cell in matrix["cells"]:
        profile = cell["key"]["profileKey"].replace("apple-macos-26.5-", "")
        tier = cell["key"]["web"]["renderer"]
        scene = cell["key"]["sceneId"]
        iou = value(cell, "declaredIoUWeb")
        if iou is None:
            absent[(profile, tier)].append(scene)
            continue
        rows[(profile, tier, component_of(scene))].append(
            (scene, value(cell, "drawnAreaWeb"), value(cell, "componentRegionArea"), iou,
             value(cell, "declaredContourP95Web"), value(cell, "declaredContourMaxWeb"))
        )

    header = (f"{'profile':<28} {'tier':<7} {'component':<18} {'n':>3}  "
              f"{'drawn':>7} {'declared':>8} {'excess':>7}  {'IoU':>7} {'p95':>6} {'max':>6}")
    print(header)
    print("-" * len(header))
    for (profile, tier, component) in sorted(rows):
        entries = rows[(profile, tier, component)]
        drawn = [e[1] for e in entries]
        declared = [e[2] for e in entries]
        ious = [e[3] for e in entries]
        p95 = [e[4] for e in entries]
        mx = [e[5] for e in entries]
        # The extremes, not the means: one cell reading a surface larger than declared is the
        # finding, and a mean over twenty would bury it.
        print(f"{profile:<28} {tier:<7} {component:<18} {len(entries):>3}  "
              f"{min(drawn):7.0f} {min(declared):8.0f} {min(d - c for d, c in zip(drawn, declared)):+7.0f}  "
              f"{min(ious):7.4f} {max(p95):6.2f} {max(mx):6.2f}")

    if absent:
        print("\nrows ABSENT (no conformance capture, or the tier refused the alpha rule):")
        for (profile, tier), scenes in sorted(absent.items()):
            print(f"  {profile:<28} {tier:<7} {len(scenes):>3} cell(s)")


if __name__ == "__main__":
    main()
