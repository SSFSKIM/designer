"""W23 G1 (f) — the rim law's input, per group, on every scene of both beds (Decision Log 2 (f)).

`rim-feed.ts` reads the tone `scene.ts` publishes for each group; this tabulates it and says which
groups carry one and which carry 0. The law's input is the tint shade's quantity by construction —
the material's own composite where the layer covers the pixel, the group's measured backdrop tone
where it does not — so a group with no tone reads the level as 0 in the uncovered part of the pixel,
and the table says how many pixels that can be.

    read-feed.py <feed json...> [--out <file>]
"""

import argparse
import json

ap = argparse.ArgumentParser()
ap.add_argument("files", nargs="+")
ap.add_argument("--out", default=None)
args = ap.parse_args()

lines = []


def emit(text=""):
    lines.append(text)
    print(text)


emit("W23 G1 — the backdrop tone each group is handed, per scene, per bed")
emit("=" * 104)
emit("`level` is the ENCODED-space tone level the collapse's argument is taken from; `linear` is the")
emit("linear mean the rim's law reads where the material's own layer does not cover the pixel.")

for path in args.files:
    document = json.load(open(path))
    a = document["args"]
    emit()
    emit(f"=== {a['colorScheme']} scheme at dpr {a['scale']} ===")
    emit(f"  {'scene':52s} {'background':16s} {'group':16s} {'level':>9s} {'linear':>10s}")
    absent = []
    zero = []
    total = 0
    for row in document["rows"]:
        groups = row.get("groups") or []
        for group in groups:
            total += 1
            tone = group.get("backdropTone")
            if tone is None:
                absent.append((row["scene"], group["id"]))
                emit(f"  {row['scene']:52s} {row['background']:16s} {group['id']:16s} "
                     f"{'ABSENT':>9s} {'ABSENT':>10s}")
                continue
            if abs(tone['linearLuminance']) < 1e-9:
                zero.append((row["scene"], group["id"]))
            emit(f"  {row['scene']:52s} {row['background']:16s} {group['id']:16s} "
                 f"{tone['level']:9.4f} {tone['linearLuminance']:10.5f}")
    emit(f"  groups: {total}; with NO tone at all: {len(absent)}; with a tone of exactly 0: "
         f"{len(zero)}")
    for scene, group in absent:
        emit(f"      absent: {scene} / {group}")
    for scene, group in zero:
        emit(f"      zero:   {scene} / {group}")

if args.out:
    open(args.out, "w").write("\n".join(lines) + "\n")
