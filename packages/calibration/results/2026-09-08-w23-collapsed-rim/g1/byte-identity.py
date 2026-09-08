"""W23 G1 — every capture of the dry run against the canonical W22 bed, byte for byte.

The parent's clause 8 says the CSS tier derives from the same profile and that every CSS mover is
explained. The rim's law reaches that tier twice — through the border's own alpha
(`adaptedSourceOptics` → `borderAlphaPerRimAlpha`) and through the derived interior level
(`interiorBandLight`) — so its captures are expected to move, and each mover has to be named rather
than assumed.

Every capture on both tiers is compared. The GPU tier's movers are the law; the CSS tier's are the
law's amplitude, the re-based conversion and the collapsed rims' floor.

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

    emit("W22 G1 — the dry run's captures against the canonical W21 bed, byte for byte")
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
