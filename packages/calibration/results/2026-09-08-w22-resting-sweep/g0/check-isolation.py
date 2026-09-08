"""W22 G0 (b) — the gate's isolation on the captures: only the LEFT side moved.

The claim the whole wave rests on is that gating the sweep changed the resting band and nothing
else. On the dark bed W21 proved it by rendering the same document at `sweepGain` 0 (claims 5.90
4); here the proof is the gate's own captures against the canonical bed, on every readable cell of
every profile. If any side other than the left moves by more than zero, the gate touched something
it should not have.

Usage: check-isolation.py --reads <canonical-reads dir> [--out <file>]
"""

import argparse
import json
import os

PROFILES = (
    "apple-macos-26.5-1x-light-standard",
    "apple-macos-26.5-2x-light-standard",
    "apple-macos-26.5-1x-dark-standard",
    "apple-macos-26.5-2x-dark-standard",
)
SIDES = ("top", "bottom", "left", "right")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--reads", required=True)
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    lines = []

    def say(text=""):
        lines.append(text)
        print(text)

    say("W22 G0 — the gate's isolation on the captures: which sides moved, and by how much")
    say()
    say("For every cell of every profile the declared reader could read, the per-side rim peak")
    say("before the gate against after. `moved` counts a side whose reading changed at all.")
    say()
    say(f"{'profile':38s} {'cells':>6s} {'top':>6s} {'bottom':>7s} {'left':>6s} {'right':>6s} "
        f"{'worst non-left':>15s} {'worst left':>11s}")
    grand = [0, 0, 0, 0]
    total_cells = 0
    worst_other_all = (0.0, None)
    for profile in PROFILES:
        before = {r["scene"]: r for r in json.load(
            open(os.path.join(args.reads, f"{profile}-webgpu-before.json")))["rows"]}
        after = {r["scene"]: r for r in json.load(
            open(os.path.join(args.reads, f"{profile}-webgpu-after.json")))["rows"]}
        counts = [0, 0, 0, 0]
        cells = 0
        worst_other = (0.0, None)
        worst_left = (0.0, None)
        for scene, row in after.items():
            base = before.get(scene)
            if base is None or "rimWeb" not in row or "rimWeb" not in base:
                continue
            cells += 1
            for i, side in enumerate(SIDES):
                delta = row["rimWeb"][i] - base["rimWeb"][i]
                if delta != 0.0:
                    counts[i] += 1
                if side == "left":
                    if abs(delta) > abs(worst_left[0]):
                        worst_left = (delta, scene)
                elif abs(delta) > abs(worst_other[0]):
                    worst_other = (delta, scene)
        total_cells += cells
        for i in range(4):
            grand[i] += counts[i]
        if abs(worst_other[0]) > abs(worst_other_all[0]):
            worst_other_all = worst_other
        say(f"{profile:38s} {cells:6d} {counts[0]:6d} {counts[1]:7d} {counts[2]:6d} "
            f"{counts[3]:6d} {worst_other[0]:15.10f} {worst_left[0]:11.4f}")
    say()
    say(f"over {total_cells} cells ({total_cells * 4} sides): top {grand[0]}, bottom {grand[1]}, "
        f"left {grand[2]}, right {grand[3]} moved")
    say(f"the largest movement on any side but the left: {worst_other_all[0]:.10f}"
        + (f" ({worst_other_all[1]})" if worst_other_all[1] else ""))
    say()
    say("The body, likewise — the eroded box is six CSS px inside the band, so the sweep should")
    say("reach it only where its blur shoulder does:")
    say(f"{'profile':38s} {'cells moved':>12s} {'worst d body':>13s} {'cell':40s}")
    for profile in PROFILES:
        before = {r["scene"]: r for r in json.load(
            open(os.path.join(args.reads, f"{profile}-webgpu-before.json")))["rows"]}
        after = {r["scene"]: r for r in json.load(
            open(os.path.join(args.reads, f"{profile}-webgpu-after.json")))["rows"]}
        moved, worst = 0, (0.0, "")
        for scene, row in after.items():
            base = before.get(scene)
            if base is None or "bodyWeb" not in row or "bodyWeb" not in base:
                continue
            delta = row["bodyWeb"] - base["bodyWeb"]
            if delta != 0.0:
                moved += 1
            if abs(delta) > abs(worst[0]):
                worst = (delta, scene)
        say(f"{profile:38s} {moved:12d} {worst[0]:13.6f} {worst[1]:40s}")

    if args.out:
        with open(args.out, "w") as fh:
            fh.write("\n".join(lines) + "\n")


if __name__ == "__main__":
    main()
