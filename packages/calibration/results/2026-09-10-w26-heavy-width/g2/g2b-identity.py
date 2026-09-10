"""W26 G2b — the CSS tier's captures against the 0.14.0 bed, byte for byte, at the LANDED documents.

The parent's ruling declines clause 7, so the claim this file tests is the sharpest one the wave can
make about the CSS tier: **at the profile documents W26 lands — which now NAME `sizeHeavyTapSigma`
and `sizeHeavyTapSigma2x` — every CSS capture is byte-identical to the 0.14.0 bed.** It is not an
argument from the code: `sourceSize()` no longer mirrors those two keys, so a patch that carries them
resolves to the same `MaterialSourceSize` it did before, and the way to know that is to render it.

Two comparisons, and the difference between them matters:

  * the canonical committed `web-captures/` in the shared checkout, which is the 0.14.0 bed itself —
    read-only, and the column every claim in this wave is stated against;
  * G1c's `c0b` rung where it overlaps, which is that same material captured on THIS machine in this
    session, so a difference against the canonical column and not against `c0b` is a session or a
    machine difference rather than a material one.

A capture that differs is reported with the size of the difference in 8-bit codes and the count of
moved pixels, because "not byte-identical" and "moved by one code on seventeen pixels" are different
findings and the bed has produced the second one before (W25 G3 §8's `photo__toolbar-group` cell, on
its fifth sighting).

    g2b-identity.py --after <captures dir> --canonical <captures dir> [--session <captures dir>]
                    [--tier css] [--out FILE]
"""

import argparse
import hashlib
import os

import numpy as np
from PIL import Image


def digest(path):
    with open(path, "rb") as handle:
        return hashlib.sha256(handle.read()).hexdigest()


def walk(root, tier):
    """Every capture of one tier under a capture root, keyed by its path below the root."""
    out = {}
    for base, _dirs, files in os.walk(root):
        for name in files:
            if not name.endswith(".png") or f"__{tier}" not in name:
                continue
            full = os.path.join(base, name)
            out[os.path.relpath(full, root)] = full
    return out


def difference(a, b):
    """The largest 8-bit channel delta and the count of moved pixels between two captures."""
    left = np.asarray(Image.open(a).convert("RGBA"), dtype=np.int16)
    right = np.asarray(Image.open(b).convert("RGBA"), dtype=np.int16)
    if left.shape != right.shape:
        return None, None
    delta = np.abs(left - right)
    moved = int(np.count_nonzero(delta.max(axis=2)))
    return int(delta.max()), moved


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--after", required=True)
    ap.add_argument("--canonical", required=True)
    ap.add_argument("--session", default=None)
    ap.add_argument("--tier", default="css")
    # The reference column is not always the 0.14.0 bed: the GPU invariance proof compares
    # against W26 G2's own dry run, and a header that said otherwise would be a false record.
    ap.add_argument("--label", default="the 0.14.0 bed")
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    lines = []

    def emit(text=""):
        lines.append(text)
        print(text)

    after = walk(args.after, args.tier)
    canonical = walk(args.canonical, args.tier)
    session = walk(args.session, args.tier) if args.session else {}

    emit(f"W26 G2b — the {args.tier} tier at the landed documents, against {args.label}")
    emit("=" * 104)
    emit(f"  after     {args.after}")
    emit(f"  canonical {args.canonical}")
    if args.session:
        emit(f"  session   {args.session}")
    shared = sorted(set(after) & set(canonical))
    emit(f"  captures: after {len(after)}, canonical {len(canonical)}, compared {len(shared)}")
    emit()

    identical = 0
    movers = []
    for key in shared:
        if digest(after[key]) == digest(canonical[key]):
            identical += 1
            continue
        worst, moved = difference(after[key], canonical[key])
        against_session = None
        if key in session:
            against_session = ("identical" if digest(after[key]) == digest(session[key])
                               else "differs")
        movers.append((key, worst, moved, against_session))

    emit(f"  BYTE-IDENTICAL to {args.label}: {identical} of {len(shared)}")
    if movers:
        emit(f"  moved: {len(movers)}")
        emit(f"    {'capture':78s} {'codes':>6s} {'pixels':>8s}  vs this session's own 0.14.0")
        for key, worst, moved, against_session in movers:
            emit(f"    {key:78s} {worst:6d} {moved:8d}  {against_session or '—'}")
        emit()
        emit("  A capture that differs from the REFERENCE column but is identical to this session's")
        emit("  own 0.14.0 capture is a session or machine difference and not a material one; a")
        emit("  capture that differs from both is the material and has to be explained.")
    else:
        emit("  moved: none")

    with open(args.out, "w") as handle:
        handle.write("\n".join(lines) + "\n")
    print(f"\n-> {args.out}")


if __name__ == "__main__":
    main()
