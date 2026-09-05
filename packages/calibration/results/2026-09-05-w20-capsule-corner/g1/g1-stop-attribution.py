"""W20 G1: what moved on the cells whose SSIM fell — read off the pixels, not the axes.

Four capsule cells worsened on `ssimMean` in the dry run and two on `oklabDeltaEMean`, which is
the wave's declared stop. This reads the same captures the matrix read and splits the surface
into three regions built from `scenes.json`'s own geometry:

  shoulders  the crescents between the declared stadium and the shape the clamp drew — the region
             the fix removes, and the only region whose PIXELS the fix touches by design;
  rim        a two-CSS-px band inside the declared contour, which is where the tier's rim sits and
             where SSIM's band term is computed;
  body       the stadium eroded four CSS px, inside the rim.

For each it prints the mean |ΔL| in linear luminance against Apple's own capture, before (the
canonical W19 capture) and after (the dry run's). A fix that improves the pixels everywhere while
SSIM falls is a structural reading, not a level one, and this table is what says which.

The canonical `web-captures/` is gitignored and lives beside the main checkout rather than in a
worktree, so both reference roots are arguments with the repository's own layout as the default.

    python3 g1-stop-attribution.py <after-captures-root> [<canonical-captures-root>] [<fixtures>]
"""
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", "..", ".."))
FIXTURES = os.path.join(ROOT, "apps", "reference-apple", "fixtures")
CANONICAL = os.path.join(ROOT, "packages", "calibration", "web-captures")
APPLE_REACH = 1.52866495

# (profile, scale, scene, capsule centres in CSS px, box size in CSS px)
CELLS = [
    ("apple-macos-26.5-1x-light-increased-contrast", 1,
     "photo__capsule-button__rest-tint-orange", [160], (120, 44)),
    ("apple-macos-26.5-1x-light-increased-contrast", 1,
     "checkerboard__capsule-button__rest-tint-orange", [160], (120, 44)),
    ("apple-macos-26.5-1x-light-increased-contrast", 1,
     "photo__capsule-button__rest", [160], (120, 44)),
    ("apple-macos-26.5-2x-light-standard", 2, "dark-solid__capsule-button__rest", [160], (120, 44)),
    ("apple-macos-26.5-2x-dark-standard", 2, "dark-solid__capsule-button__rest", [160], (120, 44)),
    # two controls that improved on both metrics, for the same three regions
    ("apple-macos-26.5-1x-light-standard", 1, "photo__capsule-button__rest", [160], (120, 44)),
    ("apple-macos-26.5-1x-light-standard", 1, "photo__toolbar-group__rest", [104, 160, 216], (44, 44)),
]


def linear(a):
    a = a / 255.0
    return np.where(a <= 0.04045, a / 12.92, ((a + 0.055) / 1.055) ** 2.4)


def luma(img):
    c = linear(np.asarray(img.convert("RGB"), dtype=np.float64))
    return 0.2126 * c[..., 0] + 0.7152 * c[..., 1] + 0.0722 * c[..., 2]


def rrect_mask(shape, radius, cx, cy, half, scale, inset=0.0):
    """Coverage of a circular rounded rectangle, in device px, at `scale`."""
    h, w = shape
    ys, xs = np.mgrid[0:h, 0:w]
    x = (xs + 0.5) / scale - cx
    y = (ys + 0.5) / scale - cy
    qx = np.abs(x) - (half[0] - radius)
    qy = np.abs(y) - (half[1] - radius)
    d = np.hypot(np.maximum(qx, 0), np.maximum(qy, 0)) + np.minimum(np.maximum(qx, qy), 0) - radius
    return d <= -inset


def maybe(path):
    return Image.open(path) if os.path.exists(path) else None


def main():
    global CANONICAL, FIXTURES
    after_root = sys.argv[1]
    if len(sys.argv) > 2:
        CANONICAL = sys.argv[2]
    if len(sys.argv) > 3:
        FIXTURES = sys.argv[3]
    header = (f"{'profile':<28} {'scene':<44} "
              f"{'shoulders b':>11} {'shoulders a':>11}  {'rim b':>7} {'rim a':>7}  "
              f"{'body b':>7} {'body a':>7}")
    print("mean |ΔL| against Apple's capture, linear luminance, GPU tier\n")
    print(header)
    print("-" * len(header))
    for profile, scale, scene, centres, size in CELLS:
        native = maybe(os.path.join(FIXTURES, profile, f"{scene}.png"))
        before = maybe(os.path.join(CANONICAL, profile, scene, f"{scene}__webgpu.png"))
        after = maybe(os.path.join(after_root, profile, scene, f"{scene}__webgpu.png"))
        if native is None or before is None or after is None:
            print(f"{profile:<28} {scene:<44}  a capture is missing — skipped")
            continue
        ln, lb, la = luma(native), luma(before), luma(after)
        half = (size[0] / 2, size[1] / 2)
        declared = min(half)
        clamped = declared / APPLE_REACH
        shoulders = np.zeros(ln.shape, bool)
        rim = np.zeros(ln.shape, bool)
        body = np.zeros(ln.shape, bool)
        for cx in centres:
            stadium = rrect_mask(ln.shape, declared, cx, 100, half, scale)
            drawn = rrect_mask(ln.shape, clamped, cx, 100, half, scale)
            shoulders |= drawn & ~stadium
            body |= rrect_mask(ln.shape, declared, cx, 100, half, scale, inset=4)
            rim |= stadium & ~rrect_mask(ln.shape, declared, cx, 100, half, scale, inset=2)
        rows = []
        for mask in (shoulders, rim, body):
            n = int(mask.sum())
            rows.append((np.abs(lb - ln)[mask].mean() if n else float("nan"),
                         np.abs(la - ln)[mask].mean() if n else float("nan")))
        short = profile.replace("apple-macos-26.5-", "")
        print(f"{short:<28} {scene:<44} "
              + "  ".join(f"{b:11.4f} {a:11.4f}" if i == 0 else f"{b:7.4f} {a:7.4f}"
                          for i, (b, a) in enumerate(rows)))


if __name__ == "__main__":
    main()
