"""W23 G1 — the two mechanisms Decision Log 2 handed this gate, fitted on the ladder's captures.

`rimTintKeep` (Decision Log 2 (c)) and `rimWidth2x` (Decision Log 2 (d)) are each linear in the
constant over the rows they reach, so one rendered point beside the base fixes the leverage per side
and every row's own answer is a division. The two do not mix: the width term is inert at dpr 1 by
construction and the tint gate moves only a collapsed surface the author painted.

Reads the ladder's `.json` files, which are `read-contour.py`'s output — the wave's instrument (X1),
`rimLocal` for the fit and `rim` beside it, per side, linear, per CSS px.

Usage: `python fit-mechanisms.py`
"""

import json
import math
import os

HERE = os.path.dirname(os.path.abspath(__file__))
SIDES = ("top", "bottom", "left", "right")


def load(label):
    with open(os.path.join(HERE, "ladder", label + ".json")) as handle:
        return {row["scene"]: row for row in json.load(handle)["rows"]}


def finite(values):
    return [v for v in values if v is not None and not math.isnan(v)]


def per_side(base, point, native, only=None, skip=None):
    """Every side of every scene both points carry, as (scene, side, native, base, point)."""
    out = []
    for scene, brow in base.items():
        if only is not None and not only(brow):
            continue
        if skip is not None and skip(brow):
            continue
        prow = point.get(scene)
        if prow is None or "rimWeb" not in prow or "rimWeb" not in brow:
            continue
        for index, side in enumerate(SIDES):
            n, b, p = brow[native][index], brow["rimWeb"][index], prow["rimWeb"][index]
            if any(x is None or math.isnan(x) for x in (n, b, p)):
                continue
            out.append((scene, side, n, b, p))
    return out


def report(title, rows, constant_at_point):
    print(f"\n== {title} — one rendered point at {constant_at_point}")
    print(f"{'scene':<48}{'side':<8}{'ref':>9}{'base':>9}{'point':>9}{'leverage':>10}{'answer':>9}")
    answers = []
    for scene, side, n, b, p in rows:
        lever = p - b
        answer = (n - b) / lever * constant_at_point if abs(lever) > 1e-9 else float("nan")
        if not math.isnan(answer):
            answers.append(answer)
        print(f"{scene:<48}{side:<8}{n:>9.4f}{b:>9.4f}{p:>9.4f}{lever:>10.4f}{answer:>9.4f}")
    if answers:
        print(f"  answers: n={len(answers)} min={min(answers):.4f} max={max(answers):.4f} "
              f"mean={sum(answers) / len(answers):.4f}")
    return answers


def sweep(rows, constant_at_point, candidates):
    """Worst and mean |drawn − reference| at a candidate value, by the term's own linearity."""
    print(f"{'value':>8}{'mean|d|':>10}{'worst|d|':>10}")
    for value in candidates:
        deltas = []
        for _scene, _side, n, b, p in rows:
            drawn = b + (p - b) * (value / constant_at_point)
            deltas.append(abs(drawn - n))
        print(f"{value:>8.3f}{sum(deltas) / len(deltas):>10.4f}{max(deltas):>10.4f}")


def is_tinted(row):
    return row["tint"] is not None


def collapsed(base_row):
    """A cell whose landed rim before this wave was exactly 0 on every side — G0's definition,
    re-read here as 'the base point draws the collapsed constant', which is the same set."""
    return all(abs(v) < 0.025 for v in finite(base_row["rimWeb"]))


print("=" * 100)
print("(c) rimTintKeep — the collapsed rim a PAINTED surface keeps (Decision Log 2 (c))")
print("=" * 100)
for bed, base_label, point_label in (
    ("light 1x", "base-light-1x", "tk1-light-1x"),
    ("dark 1x", "base-dark-1x", "tk1-dark-1x"),
):
    base, point = load(base_label), load(point_label)
    moved = [
        (scene, side, n, b, p)
        for scene, side, n, b, p in per_side(base, point, "rimNative", only=is_tinted)
        if abs(p - b) > 1e-6
    ]
    answers = report(f"{bed}: the tinted rows the gate moves", moved, 1.0)
    print("  sweep over the candidate:")
    sweep(moved, 1.0, [0.0, 0.25, 0.3, 0.4, 0.5, 0.534, 0.6, 0.75, 1.0])
    unmoved = [
        (scene, side)
        for scene, side, n, b, p in per_side(base, point, "rimNative")
        if abs(p - b) > 1e-6 and base[scene]["tint"] is None
    ]
    print(f"  untinted sides moved by the gate: {len(unmoved)}")

print()
print("=" * 100)
print("(d) rimWidth2x — the band's second anchor (Decision Log 2 (d))")
print("=" * 100)
for bed, base_label, point_label in (
    ("light 2x", "base-light-2x", "w2x12-light-2x"),
    ("dark 2x", "base-dark-2x", "w2x12-dark-2x"),
):
    base, point = load(base_label), load(point_label)
    solid = lambda row: row["tint"] is None and row["background"].endswith("solid")
    rows = [
        (scene, side, n, b, p)
        for scene, side, n, b, p in per_side(base, point, "rimLocalNative", only=solid)
        if not collapsed(base[scene]) and max(finite(base[scene]["clipNative"]) or [0]) < 0.5
    ]
    report(f"{bed}: the untinted solid, unclipped, uncollapsed sides", rows, 1.2)
    print("  sweep over the candidate (1.5 is the 1x width, unmoved):")
    sweep(rows, 1.2, [1.5, 1.4, 1.3, 1.25, 1.2, 1.15, 1.1, 1.0])
