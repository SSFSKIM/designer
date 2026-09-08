"""W22 G1 (1) — the shadow rows, read before and after, because `lightDirection` was declined.

W22 Decision Log 2 (b) declines `lightDirection` on the rim rows and asks for the shadow rows to be
read beside the declaration, because the direction is not inert in the material even when it is
inert on the rim: `platform-web`'s `light.xy` feeds the inner shadow, and the renderer's own outer
shadow sits on the same axis in the matrix. The direction did not move this wave; this is the
reading that says the rows agree.

The matrix's shadow axis carries no field named `shadowPeakDarkening`, `shadowPeakDistance` or
`shadowDecayLength` — those are the charter's words for what schema 5 records as `strengthPeakWeb`,
`strengthPeakDistanceWeb`, `falloffLengthWeb` and `falloffSigmaWeb`, with `meanDepartureWeb` beside
them as the absolute departure the axis reports when a ratio is not identifiable. All five are read
here under their real names.

    shadow-rows.py --before <matrix.json> --after <matrix.json> [--out <file>]
"""

import argparse
import json

ROWS = (
    # The charter's three, under the names schema 5 gives them.
    "strengthPeakWeb",
    "strengthPeakDistanceWeb",
    "falloffLengthWeb",
    # Beside them: the shadow's own shape and, in the second group, the rows a LIGHT DIRECTION
    # would move if it moved — the shadow's offset and its four extents are where the direction
    # lives on this axis, and they are the reading that says the declination cost nothing.
    "falloffSigmaWeb",
    "falloffAmplitudeWeb",
    "meanDepartureWeb",
)
DIRECTION_ROWS = (
    "offsetXWeb",
    "offsetYWeb",
    "centroidOffsetXWeb",
    "centroidOffsetYWeb",
    "extentAboveWeb",
    "extentBelowWeb",
    "extentLeftWeb",
    "extentRightWeb",
)
TOLERANCE = 1e-9


def identity(cell):
    return (
        cell["key"]["profileKey"],
        cell["key"]["sceneId"],
        cell["tier"],
        cell["key"]["web"]["renderer"],
    )


def value(cell, field):
    node = cell.get("shadow")
    if not isinstance(node, dict):
        return None
    entry = node.get(field)
    if isinstance(entry, dict):
        return entry.get("value")
    return entry


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--before", required=True)
    ap.add_argument("--after", required=True)
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    lines = []

    def emit(text=""):
        lines.append(text)
        print(text)

    before = {identity(c): c for c in json.load(open(args.before))["cells"]}
    after = {identity(c): c for c in json.load(open(args.after))["cells"]}

    emit("W22 G1 — the shadow rows, before → after (`lightDirection` declined, read beside it)")
    emit("=" * 100)
    emit("before = the canonical matrix at the 0.10.0 landing; after = this gate's dry run.")
    emit("")

    moved = []
    compared = 0
    for ident, cell in sorted(after.items()):
        base = before.get(ident)
        if base is None:
            continue
        for field in ROWS:
            a, b = value(cell, field), value(base, field)
            if a is None and b is None:
                continue
            compared += 1
            if a is None or b is None or abs(a - b) > TOLERANCE:
                moved.append((ident, field, b, a))

    emit(f"{compared} shadow row(s) compared over {len(after)} cells.")
    per_row = {}
    for (_p, _s, _t, _r), field, b, a in moved:
        if a is None or b is None:
            continue
        entry = per_row.setdefault(field, [0, 0.0])
        entry[0] += 1
        entry[1] = max(entry[1], abs(a - b))
    emit("  per row: cells moved, largest |delta|")
    for field in ROWS:
        count, worst = per_row.get(field, (0, 0.0))
        emit(f"    {field:26s} {count:4d} {worst:12.6f}")
    emit()

    # The direction-carrying rows, separately: `lightDirection` was DECLINED on the rim rows
    # (W22 Decision Log 2 (b)) and the shadow is where it would otherwise be visible.
    emit("the shadow's direction-carrying rows (offset, centroid, the four extents)")
    dir_moved, dir_compared = [], 0
    for ident, cell in sorted(after.items()):
        base = before.get(ident)
        if base is None:
            continue
        for field in DIRECTION_ROWS:
            a, b = value(cell, field), value(base, field)
            if a is None and b is None:
                continue
            dir_compared += 1
            if a is None or b is None or abs(a - b) > TOLERANCE:
                dir_moved.append((ident, field, b, a))
    emit(f"  {dir_compared} compared, {len(dir_moved)} moved.")
    worst_by = {}
    for (profile, scene, tier, _), field, b, a in dir_moved:
        if a is None or b is None:
            continue
        if field not in worst_by or abs(a - b) > abs(worst_by[field][2] - worst_by[field][1]):
            worst_by[field] = (f"{profile} / {scene} / {tier}", b, a)
    for field in DIRECTION_ROWS:
        if field in worst_by:
            where, b, a = worst_by[field]
            emit(f"    {field:22s} worst {b:10.4f} -> {a:10.4f}  {where}")
        else:
            emit(f"    {field:22s} unmoved on every cell")
    emit()
    if not moved:
        emit("NONE moved. Every shadow row is bit-identical to the W21 bed's.")
    else:
        emit(f"{len(moved)} moved:")
        emit(
            f"  {'profile':38s} {'scene':44s} {'tier':8s} {'row':24s} "
            f"{'before':>12s} {'after':>12s} {'delta':>12s}"
        )
        for (profile, scene, tier, _), field, b, a in moved:
            fmt = lambda v: "absent" if v is None else f"{v:12.6f}"  # noqa: E731
            delta = "—" if a is None or b is None else f"{a - b:+12.6f}"
            emit(f"  {profile:38s} {scene:44s} {tier:8s} {field:24s} {fmt(b)} {fmt(a)} {delta:>12s}")

    if args.out is not None:
        with open(args.out, "w") as handle:
            handle.write("\n".join(lines) + "\n")


if __name__ == "__main__":
    main()
