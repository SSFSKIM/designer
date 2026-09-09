"""W25 G3 — every capture of the dry run against the canonical 0.13.0 bed (the W24 landing), byte for byte.

This is stop S10 read on the bed: no cell the one landed mechanism cannot reach may move at all.
The along-side field multiplies the rim's amplitude on the GPU tier, so every GPU cell that draws a
rim on a surface of span above 32 is expected to move; and it reaches the CSS tier NOWHERE, because
its integral around the contour is exactly zero and `interiorBandLight` integrates that band — so
**every CSS capture is expected to be byte-identical**, which is a much sharper statement than the
last wave could make and is the one this run is here to test.

Every capture on both tiers is compared, and each mover is named rather than assumed.

    byte-identity.py --before <captures dir> --after <captures dir> [--out <file>]
"""

import argparse
import hashlib
import os


def digest(path):
    with open(path, "rb") as handle:
        return hashlib.sha256(handle.read()).hexdigest()


def walk(root):
    found = {}
    for base, _, files in os.walk(root):
        for name in files:
            if not name.endswith(".png"):
                continue
            path = os.path.join(base, name)
            found[os.path.relpath(path, root)] = path
    return found


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

    before, after = walk(args.before), walk(args.after)
    shared = sorted(set(before) & set(after))

    emit("W25 G3 — the dry run's captures against the canonical 0.13.0 bed (the W24 landing), byte for byte")
    emit("=" * 100)
    emit(f"before {args.before}")
    emit(f"after  {args.after}")
    emit("")

    identical, moved = [], []
    for relative in shared:
        (identical if digest(before[relative]) == digest(after[relative]) else moved).append(
            relative
        )

    emit(f"{len(shared)} captures in both beds: {len(identical)} identical, {len(moved)} moved.")
    only_before = sorted(set(before) - set(after))
    only_after = sorted(set(after) - set(before))
    if only_before:
        emit(f"  in the canonical bed only: {len(only_before)}")
        for relative in only_before:
            emit(f"    {relative}")
    if only_after:
        emit(f"  in the dry run only: {len(only_after)}")
        for relative in only_after:
            emit(f"    {relative}")

    # Two captures per cell per tier: the render, and `__alpha` — the declaration-conformance
    # capture `--alpha` takes. Both are compared, and both are named, because the alpha capture is
    # a row of the matrix as much as the render is.
    groups = [
        (f"{tier} tier, {kind}", suffix)
        for tier in ("webgpu", "css")
        for kind, suffix in (("render", f"__{tier}.png"), ("alpha", f"__{tier}__alpha.png"))
    ]
    for label, suffix in groups:
        rows = [r for r in moved if r.endswith(suffix)]
        held = [r for r in identical if r.endswith(suffix)]
        emit()
        emit(f"=== the {label}: {len(rows)} moved, {len(held)} identical ===")
        for relative in rows:
            emit(f"  moved      {relative}")
        for relative in held:
            emit(f"  identical  {relative}")

    if args.out is not None:
        with open(args.out, "w") as handle:
            handle.write("\n".join(lines) + "\n")


if __name__ == "__main__":
    main()
