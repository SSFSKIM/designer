#!/usr/bin/env python3
"""W18 G1's pre-check tables (Decision Log 3, the gate).

Reads only JSON that `separation.ts`, `spread.ts` and `closed-form.ts` wrote — nothing is
computed here that a reader could not recompute from those files — and prints the five tables
the pre-check owes the parent. G0's own readings are read out of its committed `parts/`
directory so that every row of table 1 sits beside the two configurations it is a move from.

Usage, from `packages/calibration`:
    /Users/new/.claude/jobs/5c70e47f/tmp/venv/bin/python \
      results/2026-09-05-w18-union-contour/g1/tables.py <partsDir> <g0PartsDir>
"""
import json
import sys
from collections import defaultdict

parts, g0parts = sys.argv[1], sys.argv[2]


def load(path):
    with open(path) as handle:
        return json.load(handle)


def by_scene(rows):
    return {row["scene"]: row for row in rows if "skipped" not in row}


def delta(row, mask="declared"):
    return row["whole"][mask]["delta"]


def fmt(value):
    return "—" if value is None else f"{value:+.4f}"


# The bed's scene ids carry the `__rest` state the harness captures under.
SCENES = [
    f"{background}__{component}__rest"
    for background in ("checkerboard", "photo", "light-solid")
    for component in ("capsule-button", "capsule-sm", "toolbar-group-wide", "toolbar-group")
]
STACK = [
    f"{background}__{component}__rest"
    for background in ("checkerboard", "photo")
    for component in ("stack-base", "stack-over", "glass-over-glass")
]

# ---------------------------------------------------------------------------
# 1. The two carriers, beside G0's default and its no-outer-shadow decline.
# ---------------------------------------------------------------------------
print("## 1. CSS − GPU, whole component, declared region, linear luminance\n")
closed = load(f"{g0parts}/closed-form.json")
predicted = defaultdict(float)
weight = defaultdict(float)
for row in closed:
    key = (row["scene"], row["dpr"])
    predicted[key] += row["shadowTermPredicted"] * row.get("pixels", 1)
    weight[key] += row.get("pixels", 1)

for dpr in (1, 2):
    default = by_scene(load(f"{g0parts}/attr-default-{dpr}x.json"))
    declined = by_scene(load(f"{g0parts}/attr-no-outer-shadow-{dpr}x.json"))
    cfg_a = by_scene(load(f"{parts}/sep-cfgA-{dpr}x.json"))
    cfg_ab = by_scene(load(f"{parts}/sep-cfgAB-{dpr}x.json"))
    print(f"### dpr {dpr}\n")
    print("| scene | G0 default | G0 shadow declined | carrier A | A + B | closed form (predicted move) |")
    print("| --- | --- | --- | --- | --- | --- |")
    for scene in SCENES:
        pred = -predicted[(scene, dpr)] / weight[(scene, dpr)] if weight[(scene, dpr)] else None
        cells = [
            fmt(delta(default[scene])) if scene in default else "—",
            fmt(delta(declined[scene])) if scene in declined else "—",
            fmt(delta(cfg_a[scene])) if scene in cfg_a else "—",
            fmt(delta(cfg_ab[scene])) if scene in cfg_ab else "—",
            fmt(pred),
        ]
        print(f"| `{scene}` | " + " | ".join(cells) + " |")
    print()

# ---------------------------------------------------------------------------
# 2. The remainder with the shadow out: the mean and the spread, per tier.
# ---------------------------------------------------------------------------
print("## 2. The remainder on the lone box, with both carriers: mean and spread per tier\n")
print("Declared component region. `keep` is the tier's interior standard deviation over the")
print("backdrop's own under the identical mask — how much of the backdrop's structure survives.\n")
print("| scene | dpr | GPU mean | CSS mean | Δ mean | GPU sd | CSS sd | Δ sd | GPU keep | CSS keep |")
print("| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |")
for dpr in (1, 2):
    rows = by_scene(load(f"{parts}/spread-cfgAB-{dpr}x.json"))
    for scene in SCENES:
        if scene not in rows:
            continue
        if "capsule" not in scene:
            continue
        cell = rows[scene]["whole"]["declared"]
        print(
            f"| `{scene}` | {dpr} | {cell['gpuMean']:.4f} | {cell['cssMean']:.4f} | "
            f"{cell['deltaMean']:+.4f} | {cell['gpuSd']:.4f} | {cell['cssSd']:.4f} | "
            f"{cell['deltaSd']:+.4f} | "
            # `keep` is meaningless where the backdrop has no structure of its own to keep:
            # the denominator is the solid's own quantisation noise, and the ratio would be a
            # number in the thousands standing for "this scene does not measure frosting".
            + (
                f"{cell['gpuKeep']:.3f} | {cell['cssKeep']:.3f} |"
                if cell.get("backdropSd", 0) > 0.005
                else "— | — |"
            )
        )
print()

# ---------------------------------------------------------------------------
# 3. The stack's tier share.
# ---------------------------------------------------------------------------
print("## 3. The stack, with both carriers (S4's restated clause)\n")
print("| scene | dpr | part | GPU | CSS | CSS − GPU | px |")
print("| --- | --- | --- | --- | --- | --- | --- |")
for dpr in (1, 2):
    rows = by_scene(load(f"{parts}/sep-cfgAB-{dpr}x.json"))
    for scene in STACK:
        row = rows.get(scene)
        if row is None:
            continue
        whole = row["whole"]["declared"]
        print(
            f"| `{scene}` | {dpr} | whole | {whole['gpu']:.4f} | {whole['css']:.4f} | "
            f"{whole['delta']:+.4f} | {whole['pixels']} |"
        )
        for surface in row["surfaces"]:
            if row["component"] != "stack":
                continue
            cell = surface["declared"]
            print(
                f"| | {dpr} | {surface['role']} | {cell['gpu']:.4f} | {cell['css']:.4f} | "
                f"{cell['delta']:+.4f} | {cell['pixels']} |"
            )
print()

# ---------------------------------------------------------------------------
# 4. The predicted move of every light cell of the canonical bed (S5).
# ---------------------------------------------------------------------------
print("## 4. The canonical bed's light cells: the closed form's predicted move (S5)\n")
print("The move is `−shadowTermPredicted`, area-weighted over the cell's surfaces — what the")
print("cell's CSS − GPU rises by when the shadow leaves the sampled backdrop. The W17 bed's")
print("reading is beside it where the wave's Grounding Baseline records one.\n")
BASELINE = {
    ("checkerboard__toolbar-group", 1): -0.0122, ("checkerboard__toolbar-group", 2): -0.0040,
    ("photo__toolbar-group", 1): -0.0150, ("photo__toolbar-group", 2): -0.0101,
    ("photo__glass-over-glass", 1): -0.0119, ("photo__glass-over-glass", 2): -0.0126,
    ("checkerboard__glass-over-glass", 1): -0.0042, ("checkerboard__glass-over-glass", 2): -0.0012,
    ("checkerboard__capsule-button", 1): -0.0005, ("checkerboard__capsule-button", 2): +0.0095,
    ("photo__capsule-button", 1): +0.0005, ("photo__capsule-button", 2): +0.0016,
}
LIGHT_BACKGROUNDS = ("checkerboard", "photo", "light-solid", "impulse", "hc-text", "mid-dark-solid")
bed = load(f"{parts}/closed-form-bed.json")
move = defaultdict(float)
area = defaultdict(float)
for row in bed:
    key = (row["scene"], row["dpr"])
    move[key] += -row["shadowTermPredicted"] * row["pixels"]
    area[key] += row["pixels"]
print("| cell | dpr | predicted move | W17 bed CSS − GPU | predicted after | leaves 0.01? |")
print("| --- | --- | --- | --- | --- | --- |")
for (scene, dpr) in sorted(move, key=lambda key: (key[0], key[1])):
    if not scene.startswith(LIGHT_BACKGROUNDS):
        continue
    predicted_move = move[(scene, dpr)] / area[(scene, dpr)]
    base = BASELINE.get((scene.removesuffix("__rest"), dpr))
    after = None if base is None else base + predicted_move
    leaves = "" if after is None else ("**yes**" if abs(after) > 0.01 else "no")
    print(
        f"| `{scene}` | {dpr} | {predicted_move:+.4f} | {fmt(base)} | {fmt(after)} | {leaves} |"
    )
print()

# ---------------------------------------------------------------------------
# 4a. S5's clause: the MEASURED move against the closed form's, per scratch twin.
# ---------------------------------------------------------------------------
print("## 4a. S5's clause on the twins: measured move against the closed form's (bound 0.0015)\n")
print("| scene | dpr | measured move | closed form | miss | inside 0.0015 |")
print("| --- | --- | --- | --- | --- | --- |")
for dpr in (1, 2):
    default = by_scene(load(f"{g0parts}/attr-default-{dpr}x.json"))
    cfg_ab = by_scene(load(f"{parts}/sep-cfgAB-{dpr}x.json"))
    for scene in SCENES + STACK:
        if scene not in default or scene not in cfg_ab:
            continue
        measured = delta(cfg_ab[scene]) - delta(default[scene])
        pred = -predicted[(scene, dpr)] / weight[(scene, dpr)] if weight[(scene, dpr)] else None
        miss = None if pred is None else measured - pred
        inside = "" if miss is None else ("yes" if abs(miss) <= 0.0015 else "**no**")
        print(
            f"| `{scene}` | {dpr} | {measured:+.4f} | {fmt(pred)} | {fmt(miss)} | {inside} |"
        )
print()

# ---------------------------------------------------------------------------
# 6. S8's cost check.
# ---------------------------------------------------------------------------
print("## 6. The cost knee, W16 G0's harness, with and without carrier B (S8)\n")
print("Every surface is in a group of three, so every surface gets a caster and every third host")
print("a clipped container — the most carrier B can cost. The knee is the count at which the")
print("median leaves the display's 16.7 ms cadence.\n")
print("| form | dpr | n | median ms | p90 ms |")
print("| --- | --- | --- | --- | --- |")
for row in load(f"{parts}/cost.json"):
    print(
        f"| `{row['form']}` | {row['dpr']} | {row['n']} | {row['medianMs']:.1f} | {row['p90Ms']:.1f} |"
    )
print()
