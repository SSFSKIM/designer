"""W23 G3 — the tinted rows' HUE, native against web, before and after (Decision Log 3 (h)).

The reference's rim on a painted surface is the paint's own colour lifted; vitrea's is white added
over the paint. The luminance clauses cannot see the difference and the eye can, so this prints the
contour ROW's straight-span mean colour per tinted row — encoded sRGB for reading and OKLab (a, b)
for the clause — beside the row's base colour, which is what the rim is a lift OF.

    chroma-table.py --label <label> [--label <label> ...] [--tier webgpu] [--out <file>]
"""

import argparse
import json
import math
import os

HERE = os.path.dirname(os.path.abspath(__file__))
SIDES = ("top", "bottom", "left", "right")
PROFILES = (
    ("apple-macos-26.5-1x-light-standard", "light 1x"),
    ("apple-macos-26.5-2x-light-standard", "light 2x"),
    ("apple-macos-26.5-1x-dark-standard", "dark 1x"),
    ("apple-macos-26.5-2x-dark-standard", "dark 2x"),
)


def load(label, profile, tier):
    path = os.path.join(HERE, "reads", f"{label}-{profile}-{tier}.json")
    if not os.path.exists(path):
        return {}
    return {row["scene"]: row for row in json.load(open(path))["rows"]}


def ok(v):
    return v is not None and not (isinstance(v, float) and math.isnan(v))


def rgb(triple):
    if triple is None or any(not ok(v) for v in triple):
        return "     —      "
    return "(%3.0f,%3.0f,%3.0f)" % tuple(triple)


def ab(triple):
    if triple is None or any(not ok(v) for v in triple):
        return "    —        "
    return "%+.3f/%+.3f" % (triple[1], triple[2])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--label", action="append", required=True)
    ap.add_argument("--tier", default="webgpu")
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    lines = []

    def emit(text=""):
        lines.append(text)
        print(text)

    emit(f"W23 G3 — the tinted rows' contour-row colour, {args.tier} tier")
    emit("=" * 118)
    emit("`base` is the side's own base 2-4 CSS px in — the paint as the surface draws it — and")
    emit("`row0` is the contour row. `dOKLab` is the row's (a, b) minus the reference row's (a, b);")
    emit("the clause is |da| and |db| within 0.02.")

    worst = 0.0
    for profile, label in PROFILES:
        columns = [(name, load(name, profile, args.tier)) for name in args.label]
        native = columns[0][1]
        if not native:
            continue
        emit()
        emit(f"=== {label} ===")
        header = (
            f"  {'cell':46s} {'side':7s} {'base native':13s} {'row0 native':13s} "
            f"{'ref a/b':13s}"
        )
        for name, _ in columns:
            header += f" | {name + ' row0':13s} {name + ' a/b':13s} {'dOKLab':13s}"
        emit(header)
        for scene in sorted(native):
            row = native[scene]
            if row.get("tint") is None or row.get("row0RgbNative") is None:
                continue
            for side in SIDES:
                nat_rgb = row["row0RgbNative"].get(side)
                nat_ab = row["row0OklabNative"].get(side)
                if nat_rgb is None or any(not ok(v) for v in nat_rgb):
                    continue
                line = (
                    f"  {scene:46s} {side:7s} {rgb(row['baseRgbNative'].get(side)):13s} "
                    f"{rgb(nat_rgb):13s} {ab(nat_ab):13s}"
                )
                for name, table in columns:
                    web = table.get(scene)
                    if web is None or web.get("row0RgbWeb") is None:
                        line += f" | {'—':13s} {'—':13s} {'—':13s}"
                        continue
                    w_rgb = web["row0RgbWeb"].get(side)
                    w_ab = web["row0OklabWeb"].get(side)
                    if w_rgb is None or any(not ok(v) for v in w_rgb):
                        line += f" | {'—':13s} {'—':13s} {'—':13s}"
                        continue
                    d = (w_ab[1] - nat_ab[1], w_ab[2] - nat_ab[2])
                    worst = max(worst, abs(d[0]), abs(d[1]))
                    line += (
                        f" | {rgb(w_rgb):13s} {ab(w_ab):13s} "
                        f"{'%+.3f/%+.3f' % d:13s}"
                    )
                emit(line)
    emit()
    emit(f"worst |da| or |db| over every tinted side and every column: {worst:.4f} against 0.02")
    if args.out:
        open(args.out, "w").write("\n".join(lines) + "\n")


main()
