"""W23 G3 — the painted rim's colour, fitted on the ladder's own captures.

`rimTintChroma` gates the rim's colour by `chroma × tintStrength`, so it is linear in the constant
on every painted pixel and reaches no other row. Two rendered points per bed — the base at 0 and one
at 1 — give each tinted side its own answer in OKLab (a, b), and the value is chosen on the pooled
rows rather than on any one cell.

The objective is the CHROMATICITY: |da| and |db| of the contour row's straight-span mean colour
against the reference's, which is the clause Decision Log 3 (h) binds. The luminance rim is printed
beside it, because a colour that reproduces the hue and loses the amount is not the mechanism.

    fit-chroma.py [--out <file>]
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


def load(label, profile):
    path = os.path.join(HERE, "reads", f"{label}-{profile}-webgpu.json")
    if not os.path.exists(path):
        return {}
    return {row["scene"]: row for row in json.load(open(path))["rows"]}


def ok(v):
    return v is not None and not (isinstance(v, float) and math.isnan(v))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=None)
    args = ap.parse_args()
    lines = []

    def emit(text=""):
        lines.append(text)
        print(text)

    emit("W23 G3 — rimTintChroma, per tinted side, from two rendered points")
    emit("=" * 118)
    emit("`da` / `db` are the drawn row's OKLab (a, b) minus the reference row's; the clause is")
    emit("0.02 on each. `answer` is the value at which the pooled |da| + |db| of that side is least,")
    emit("by the term's own linearity between the two points.")

    rows = []
    for profile, label in PROFILES:
        base, point = load("g3base", profile), load("g3chroma1", profile)
        if not base or not point:
            continue
        emit()
        emit(f"=== {label} ===")
        emit(
            f"  {'cell':46s} {'side':7s} {'ref a/b':15s} {'at 0 a/b':15s} {'at 1 a/b':15s} "
            f"{'answer':>8s} {'rim 0':>8s} {'rim 1':>8s} {'ref rim':>8s}"
        )
        for scene in sorted(base):
            b, p = base[scene], point.get(scene)
            if p is None or b.get("tint") is None or b.get("row0OklabWeb") is None:
                continue
            if p.get("row0OklabWeb") is None:
                continue
            for index, side in enumerate(SIDES):
                nat = b["row0OklabNative"].get(side)
                at0 = b["row0OklabWeb"].get(side)
                at1 = p["row0OklabWeb"].get(side)
                if any(x is None or any(not ok(v) for v in x) for x in (nat, at0, at1)):
                    continue
                d0 = (at0[1] - nat[1], at0[2] - nat[2])
                d1 = (at1[1] - nat[1], at1[2] - nat[2])
                # Least squares in (a, b) along the segment from the point at 0 to the point at 1.
                dx = (d1[0] - d0[0], d1[1] - d0[1])
                denom = dx[0] * dx[0] + dx[1] * dx[1]
                answer = float("nan") if denom < 1e-12 else -(d0[0] * dx[0] + d0[1] * dx[1]) / denom
                rims = (b["rimWeb"][index], p["rimWeb"][index], b["rimNative"][index])
                rows.append((profile, scene, side, d0, d1, answer))
                emit(
                    f"  {scene:46s} {side:7s} "
                    f"{'%+.3f/%+.3f' % (nat[1], nat[2]):15s} "
                    f"{'%+.3f/%+.3f' % d0:15s} {'%+.3f/%+.3f' % d1:15s} "
                    f"{answer:8.3f} {rims[0]:8.4f} {rims[1]:8.4f} {rims[2]:8.4f}"
                )

    if not rows:
        emit("no rows")
        return
    answers = [r[5] for r in rows if not math.isnan(r[5])]
    emit()
    emit(
        f"the per-side answers: n={len(answers)} min={min(answers):.3f} max={max(answers):.3f} "
        f"mean={sum(answers) / len(answers):.3f}"
    )
    emit()
    emit("=== the sweep: worst and mean |da|, |db| over every tinted side at a candidate ===")
    emit(f"{'value':>8}{'mean|da|':>10}{'mean|db|':>10}{'worst|da|':>11}{'worst|db|':>11}{'sides over 0.02':>17}")
    for value in [0.0, 0.25, 0.4, 0.5, 0.6, 0.7, 0.75, 0.8, 0.9, 1.0]:
        das, dbs = [], []
        for _profile, _scene, _side, d0, d1, _answer in rows:
            das.append(abs(d0[0] + (d1[0] - d0[0]) * value))
            dbs.append(abs(d0[1] + (d1[1] - d0[1]) * value))
        over = sum(1 for a, b in zip(das, dbs) if a > 0.02 or b > 0.02)
        emit(
            f"{value:>8.2f}{sum(das) / len(das):>10.4f}{sum(dbs) / len(dbs):>10.4f}"
            f"{max(das):>11.4f}{max(dbs):>11.4f}{over:>17d}"
        )
    if args.out:
        open(args.out, "w").write("\n".join(lines) + "\n")


main()
