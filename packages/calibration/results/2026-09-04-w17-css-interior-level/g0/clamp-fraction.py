#!/usr/bin/env python3
"""W17 G0 (d) — how much of the sharp layer's filtered backdrop the carrier's transfer clips.

Filter Effects 1 clamps a filter primitive's result to the allowed range, so an
`feComponentTransfer` of `type="linear"` cannot emit a negative value however negative its
intercept is. §4's solve returns an intercept of −0.187 to −0.190 against a slope of 1.109 to 1.132,
which puts the transfer's zero crossing at a backdrop level of about 0.17 in linear light: every
pixel of the filtered backdrop below that comes out at 0 instead of at the affine's negative value,
and the tier's body is brighter there than the conversion asked for.

This script measures how large that region is, on the backdrop the probe cells sit over: the
checkerboard, blurred at the sharp layer's own width (W16's measured effective sharp σ, 1.6–1.7
device px at dpr 1) and read in linear light. It is the backdrop rather than the tier's own capture
because the pre-transfer body is not a thing the capture contains — the transfer is inside the
filter — and the backdrop blurred at the sharp width is exactly what the transfer is handed.

Usage: `python3 clamp-fraction.py <fixturesDir>` — the venv's python, which has numpy, scipy and
Pillow; the system python3 has none of them.
"""

import sys
from pathlib import Path

import numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter

# The solves §4 recorded, and the sharp effective σ in device px per scale (claims §5.72 §1: the
# sharp width read 1.60–1.70 device px at dpr 1 against a nominal 1.25, and takes the same
# effective-width ratio at dpr 2).
SOLVES = [
    ("checkerboard__rrect-md__rest", 1.1123, -0.1892),
    ("checkerboard__rrect-ml__rest", 1.1087, -0.1901),
    ("checkerboard__capsule-button__rest", 1.1316, -0.1872),
]
SHARP_SIGMA_DEVICE_PX = {1: 1.7, 2: 2.5}


def linear(encoded):
    e = encoded / 255.0
    return np.where(e <= 0.04045, e / 12.92, ((e + 0.055) / 1.055) ** 2.4)


def main():
    fixtures = Path(sys.argv[1] if len(sys.argv) > 1 else "apps/reference-apple/fixtures")
    for scale, sigma in SHARP_SIGMA_DEVICE_PX.items():
        image = np.asarray(
            Image.open(fixtures / "backgrounds" / f"checkerboard@{scale}x.png").convert("RGB")
        ).astype(float)
        luminance = (
            0.2126 * linear(image[:, :, 0])
            + 0.7152 * linear(image[:, :, 1])
            + 0.0722 * linear(image[:, :, 2])
        )
        blurred = gaussian_filter(luminance, sigma)
        print(f"checkerboard@{scale}x, sharp sigma {sigma} device px: "
              f"blurred mean {blurred.mean():.4f}, std {blurred.std():.4f}")
        for scene, slope, intercept in SOLVES:
            threshold = -intercept / slope
            print(f"  {scene:<36} slope {slope:.4f} intercept {intercept:+.4f} "
                  f"-> clips below {threshold:.4f}, "
                  f"{(blurred < threshold).mean():.3f} of the filtered backdrop")


if __name__ == "__main__":
    main()
