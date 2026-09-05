"""W20 G0 contract X4: inject a known dilation into a real conformance capture.

The unit test `packages/calibration/test/declared-conformance.test.ts` recovers a dilation
from a synthetic mask, which proves the metric. This proves the PIPELINE: it takes the
declaration-conformance capture the driver actually wrote, dilates its alpha by a stated
number of device pixels with a Euclidean structuring element, and writes it back into a copy
of the capture tree under the same filename — so `compare --skip-capture --alpha` re-measures
it as if the renderer had drawn it that way, through every step the bed's own rows came
through.

The dilation is applied to the thresholded coverage, not to the alpha ramp: the instrument
reads {alpha >= 0.5}, so growing that set by exactly d is the injection whose answer is known.
Everything below the threshold is left alone, which keeps the shadow band where it was and
makes the recovered figure attributable to the injection rather than to a rescaling.

    python3 g0-x4-dilate.py <capture-tree> <scene> <tier> <dilate-device-px>
"""
import os
import sys

import numpy as np
from PIL import Image
from scipy import ndimage

THRESHOLD = 0.5


def main() -> None:
    tree, scene, tier, radius = sys.argv[1], sys.argv[2], sys.argv[3], float(sys.argv[4])
    path = os.path.join(tree, scene, f"{scene}__{tier}__alpha.png")
    image = Image.open(path).convert("RGBA")
    data = np.asarray(image, dtype=np.uint8).copy()
    alpha = data[..., 3] / 255.0

    covered = alpha >= THRESHOLD
    # A Euclidean ball, not a square: a square structuring element dilates the diagonal by
    # d*sqrt(2) and the contour metric would report that instead of the injected d.
    size = int(np.ceil(radius)) * 2 + 1
    yy, xx = np.mgrid[0:size, 0:size] - (size // 2)
    ball = (xx * xx + yy * yy) <= radius * radius
    grown = ndimage.binary_dilation(covered, structure=ball)

    added = grown & ~covered
    data[..., 3][added] = 255
    # The colour under an injected pixel is white, the same value the tier's own coverage
    # carries here, so the file stays readable by eye. Nothing downstream reads the colour —
    # the instrument is an alpha rule — but an image that looked like noise would be one
    # nobody could check.
    for channel in range(3):
        plane = data[..., channel]
        plane[added] = 255

    Image.fromarray(data, "RGBA").save(path)
    print(
        f"{scene} [{tier}]: coverage {int(covered.sum())} -> {int(grown.sum())} px "
        f"(+{int(added.sum())}) at a {radius:g} device-px Euclidean dilation; wrote {path}"
    )


if __name__ == "__main__":
    main()
