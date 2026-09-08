#!/usr/bin/env python3
"""W22 G1 — the goldens' attribution: the delta is the rim's specular and nothing else.

W15 G2's `attribute-goldens.py` gives the count, the magnitude and the bounding box. This adds the
two things W22's delta has to satisfy to be the specular term and not something travelling with it,
and it can be stated exactly because THIS wave's delta IS expressible through the profile seam: both
directories are renders of the SAME tree, differing only in `optics.regular.specularGain` (0.55 in
`before`, the fitted 0 in `after`), so nothing but that constant can be in the difference.

  * **The change is a BAND.** The rim is drawn within `rimWidth` of the contour, so every moved pixel
    must be near an unmoved one. Reported as the largest distance from a moved pixel to the nearest
    unmoved pixel — a band's half-thickness in device px.
  * **The change is LIT FROM ABOVE.** `lightDirection` is [−0.3714, −0.9285] and the specular factor
    is `clamp(n · l)^specularPower`, so it can only reach contour points whose outward normal has an
    upward component. Reported as the share of the moved luminance sitting in the upper half of the
    moved region's own bounding box.

    attribute-w22-goldens.py <before dir> <after dir> [--out <file>]
"""

import argparse
import glob
import hashlib
import os

import numpy as np
from PIL import Image
from scipy import ndimage


def load(path):
    return np.asarray(Image.open(path).convert("RGBA")).astype(int)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("before")
    ap.add_argument("after")
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    lines = []

    def emit(text=""):
        lines.append(text)
        print(text)

    names = sorted(
        {os.path.basename(p).split("__")[0] for p in glob.glob(f"{args.before}/*__declined.png")}
    )
    emit("W22 G1 — the goldens, attributed to `optics.regular.specularGain` 0.55 -> 0")
    emit("=" * 112)
    emit("Both directories are the SAME tree; `before` renders the constant at 0.55 through the")
    emit("profile seam. The declined column is the isolation proof's named profile.")
    emit("")
    emit(
        f"  {'scene':26s} {'render':9s} {'px moved':>9s} {'of':>7s} {'max|d|rgb':>10s} "
        f"{'max|d|a':>8s} {'band px':>8s} {'upper share':>12s}  hash (declined)"
    )
    for name in names:
        for tag in ("declined", "default"):
            before = load(f"{args.before}/{name}__{tag}.png")
            after = load(f"{args.after}/{name}__{tag}.png")
            delta = np.abs(before - after)
            moved = delta.max(axis=2) > 0
            if not moved.any():
                emit(
                    f"  {name:26s} {tag:9s} {0:>9d} {moved.size:>7d} {0:>10d} {0:>8d} "
                    f"{'—':>8s} {'—':>12s}  "
                    + (hashlib.sha256(after.astype(np.uint8).tobytes()).hexdigest()[:32]
                       if tag == "declined" else "")
                )
                continue
            # The band's half-thickness: how far a moved pixel can be from an unmoved one.
            band = ndimage.distance_transform_edt(moved)[moved].max()
            ys, xs = np.nonzero(moved)
            y0, y1 = ys.min(), ys.max()
            weight = delta[..., :3].sum(axis=2)[moved].astype(float)
            upper = weight[(ys - y0) <= (y1 - y0) / 2].sum() / weight.sum()
            emit(
                f"  {name:26s} {tag:9s} {int(moved.sum()):>9d} {moved.size:>7d} "
                f"{int(delta[..., :3].max()):>10d} {int(delta[..., 3].max()):>8d} "
                f"{band:>8.2f} {upper:>12.3f}  "
                + (hashlib.sha256(after.astype(np.uint8).tobytes()).hexdigest()[:32]
                   if tag == "declined" else "")
            )
    emit()
    emit("`band px` is the largest distance from a moved pixel to the nearest unmoved one, so a")
    emit("value near 1-2 device px says the change is a rim band and not an interior. `upper share`")
    emit("is the fraction of the moved luminance in the upper half of the moved region — the")
    emit("signature of a light direction with a −0.93 y-component.")

    if args.out is not None:
        with open(args.out, "w") as handle:
            handle.write("\n".join(lines) + "\n")


if __name__ == "__main__":
    main()
