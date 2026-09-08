"""W23 G3 — stop S9: the tinted rows' LUMINANCE rim, against Decision Log 2 (c)'s bindings.

The hue clause is the wave's new one and it does not replace the amplitude clause it sits beside:
a rim that reproduces the paint's colour and loses its amount is not the mechanism. So every tinted
side is read on the contour instrument in three columns — the reference, the LANDED 0.11.0 bed and
this gate's dry run — and judged on the two bindings Decision Log 2 (c) wrote:

  * no tinted row worse than landed by more than 0.03;
  * the tinted COLLAPSED cells within 0.05 of the reference.

    tinted-rows.py --landed <label> --after <label> [--out <file>]
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
COLLAPSED = (
    "dark-solid__capsule-button__rest-tint-orange",
    "impulse__capsule-button__rest-tint-orange",
)
WORSE_THAN_LANDED = 0.03
COLLAPSED_BOUND = 0.05


def load(label, profile):
    path = os.path.join(HERE, "reads", f"{label}-{profile}-webgpu.json")
    if not os.path.exists(path):
        return {}
    return {row["scene"]: row for row in json.load(open(path))["rows"]}


def ok(v):
    return v is not None and not (isinstance(v, float) and math.isnan(v))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--landed", default="landed")
    ap.add_argument("--after", default="g3")
    ap.add_argument("--out", default=None)
    args = ap.parse_args()
    lines = []

    def emit(text=""):
        lines.append(text)
        print(text)

    emit("W23 G3 — S9: the tinted rows' luminance rim, reference / landed / this gate")
    emit("=" * 118)
    emit("`d landed` and `d after` are the drawn rim minus the reference's. The bindings are")
    emit("Decision Log 2 (c)'s: no row worse than landed by more than 0.03, and the collapsed")
    emit("painted cells within 0.05.")

    worse, collapsed_miss, worst_worse, worst_collapsed = [], [], 0.0, 0.0
    for profile, label in PROFILES:
        landed, after = load(args.landed, profile), load(args.after, profile)
        if not landed or not after:
            continue
        emit()
        emit(f"=== {label} ===")
        emit(
            f"  {'cell':46s} {'side':7s} {'ref':>9s} {'landed':>9s} {'after':>9s} "
            f"{'d landed':>10s} {'d after':>10s} {'verdict':>10s}"
        )
        for scene in sorted(after):
            row, was = after[scene], landed.get(scene)
            if row.get("tint") is None or was is None or row.get("rimWeb") is None:
                continue
            if was.get("rimWeb") is None:
                continue
            for index, side in enumerate(SIDES):
                n, a, b = row["rimNative"][index], row["rimWeb"][index], was["rimWeb"][index]
                if not ok(n) or not ok(a) or not ok(b):
                    continue
                da, db = a - n, b - n
                verdict = "ok"
                if abs(da) > abs(db) + WORSE_THAN_LANDED:
                    verdict = "S9 WORSE"
                    worse.append((profile, scene, side, db, da))
                    worst_worse = max(worst_worse, abs(da) - abs(db))
                if scene in COLLAPSED:
                    worst_collapsed = max(worst_collapsed, abs(da))
                    if abs(da) > COLLAPSED_BOUND:
                        verdict = "S9 COLLAPSED"
                        collapsed_miss.append((profile, scene, side, da))
                emit(
                    f"  {scene:46s} {side:7s} {n:9.4f} {b:9.4f} {a:9.4f} "
                    f"{db:+10.4f} {da:+10.4f} {verdict:>10s}"
                )
    emit()
    emit(
        f"rows worse than landed by more than {WORSE_THAN_LANDED}: {len(worse)} "
        f"(worst excess {worst_worse:.4f})"
    )
    emit(
        f"collapsed painted sides outside {COLLAPSED_BOUND}: {len(collapsed_miss)} "
        f"(worst {worst_collapsed:.4f})"
    )
    if args.out:
        open(args.out, "w").write("\n".join(lines) + "\n")


main()
