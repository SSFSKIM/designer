"""W20 G0: does an alpha coverage rule separate a tier's material from its own shadow?

The declaration-conformance reading is `{alpha >= 0.5}` over a transparent-page capture, and
that rule is only honest if the tier's fill sits above the threshold and everything it draws
outside its contour sits below. This measures both, per tier, rather than assuming either:
the alpha profiled by SIGNED DISTANCE to the declared contour, so the fill, the antialiased
boundary band, the rim and the outer shadow are separated by where they are rather than by
what they are called.

Distances are analytic, from the scene matrix's declaration — the same rounded-rectangle
signed distance `packages/calibration/src/component-region.ts` uses — so nothing here depends
on an extractor whose behaviour is what is in question.

    python3 g0-alpha-separation.py <capture-tree> <tier> [scene ...]

Prints, per scene: the alpha histogram by one-pixel distance shells from -8 to +12, the
interior median at four CSS px of depth (the level the instrument conditions on), and the
extracted area at three thresholds beside the declared and the clamped-contour areas.
"""
import os
import sys

import numpy as np
from PIL import Image

CANVAS = (320, 200)
APPLE_REACH = 1.52866495

# Every component of the bed this is run over, as `apps/reference-apple/scenes.json` declares
# it: size in points, declared radius (None for a capsule, whose radius is half its short
# side), and the x centres of its members.
COMPONENTS = {
    "capsule-button": ((120, 44), None, [160]),
    "rrect-sm": ((64, 32), 8, [160]),
    "rrect-md": ((160, 96), 20, [160]),
    "rrect-ml": ((224, 128), 27, [160]),
    "rrect-lg": ((280, 160), 34, [160]),
    "toolbar-group": ((44, 44), None, [104, 160, 216]),
}


def signed_distance(size, radius, centres, shape, scale):
    """Nearest signed distance to any member's contour, device px, negative inside."""
    height, width = shape
    yy, xx = np.mgrid[0:height, 0:width]
    x = (xx + 0.5) / scale
    y = (yy + 0.5) / scale
    half_w, half_h = size[0] / 2, size[1] / 2
    nearest = np.full(shape, np.inf)
    for cx in centres:
        qx = np.abs(x - cx) - (half_w - radius)
        qy = np.abs(y - CANVAS[1] / 2) - (half_h - radius)
        d = np.hypot(np.maximum(qx, 0), np.maximum(qy, 0)) + np.minimum(np.maximum(qx, qy), 0) - radius
        nearest = np.minimum(nearest, d)
    return nearest * scale


def main() -> None:
    tree, tier = sys.argv[1], sys.argv[2]
    scenes = sys.argv[3:]
    for scene in scenes:
        path = os.path.join(tree, scene, f"{scene}__{tier}__alpha.png")
        if not os.path.exists(path):
            print(f"{scene} [{tier}]: no conformance capture at {path}")
            continue
        alpha = np.asarray(Image.open(path).convert("RGBA"), dtype=np.float64)[..., 3] / 255.0
        component = scene.split("__")[1]
        size, declared, centres = COMPONENTS[component]
        scale = alpha.shape[1] / CANVAS[0]
        radius = declared if declared is not None else min(size) / 2
        clamped = min(radius, (min(size) / 2) / APPLE_REACH)

        d_declared = signed_distance(size, radius, centres, alpha.shape, scale)
        d_clamped = signed_distance(size, clamped, centres, alpha.shape, scale)
        deep = alpha[d_declared <= -4 * scale]
        print(f"--- {scene} [{tier}] at {scale:g}x: declared r {radius:g}, clamped r {clamped:.4f} ---")
        print(f"  interior alpha at 4 CSS px depth: median {np.median(deep):.4f} "
              f"min {deep.min():.4f} max {deep.max():.4f}  (n={deep.size})")
        for lo in range(-8, 13):
            shell = (d_declared >= lo) & (d_declared < lo + 1)
            if not shell.any():
                continue
            print(f"  d [{lo:3d},{lo + 1:3d})  n={shell.sum():5d}  min {alpha[shell].min():.4f}"
                  f"  mean {alpha[shell].mean():.4f}  max {alpha[shell].max():.4f}")
        declared_area = int((d_declared <= 0).sum())
        clamped_area = int((d_clamped <= 0).sum())
        for threshold in (0.3, 0.5, 0.7):
            print(f"    alpha >= {threshold}: area {int((alpha >= threshold).sum()):6d}"
                  f"   declared {declared_area}   clamped-contour {clamped_area}")


if __name__ == "__main__":
    main()
