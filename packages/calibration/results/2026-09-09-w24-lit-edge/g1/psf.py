"""W24 G1 (b) — the kernel the dot arrives through, native and vitrea, at both scales.

The dot's FWHM is a summary and this is the shape behind it. The background's dot is a 4 CSS px
square, so the transmitted profile through the body is that box convolved with whatever kernel the
material transmits through; fitting the box's convolution with a sharp and a heavy Gaussian
recovers the material's own two-component blur in DEVICE px, which is the unit a kernel lives in
and the one a CSS-px FWHM hides.

This exists because the wave's design named the possibility explicitly: "if the dot's FWHM (8 at
1x, 4 at 2x — a width that does not double with the scale) asks for a different kernel, that is a
finding, not a fit". It does, and the finding is here.

Usage: psf.py <label>=<png>:<scale> ...
"""

import importlib.util
import os
import sys

import numpy as np
from scipy.optimize import least_squares
from scipy.special import erf

_here = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location("read_impulse", os.path.join(_here,
                                                                           "read-impulse.py"))
ri = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(ri)

DOT_CSS = 4.0
CENTRE_CSS = (160.0, 104.0)


def box_gauss(x, w, sigma):
    s = max(abs(sigma), 1e-6)
    return 0.5 * (erf((x + w / 2) / (s * np.sqrt(2))) - erf((x - w / 2) / (s * np.sqrt(2))))


def fit(path, scale):
    lum = ri.luma_of(path)
    offs, vals = ri.profile_along(lum, CENTRE_CSS[0] * scale, CENTRE_CSS[1] * scale, "x",
                                  20 * scale, 1 * scale)
    body = float(vals[np.abs(offs) >= 14 * scale].mean())
    y = vals - body
    w = DOT_CSS * scale

    def residual(q):
        return q[0] * box_gauss(offs, w, q[1]) + q[2] * box_gauss(offs, w, q[3]) + q[4] - y

    # Bounded, and the bounds are what make the two components mean something: both amplitudes
    # non-negative and the heavy component at least four times the sharp one's floor. Unbounded,
    # the pair is free to fit any profile as a large positive and a large negative Gaussian of the
    # same width, which is a perfect fit and no reading at all — it did exactly that on the 1x
    # rows before this bound existed.
    seed = [max(y.max(), 1e-5), 2.0 * scale, max(y.max(), 1e-5) * 0.05, 8.0 * scale, 0.0]
    r = least_squares(
        residual,
        seed,
        bounds=(
            [0.0, 0.05 * scale, 0.0, 4.0 * scale, -0.01],
            [np.inf, 4.0 * scale, np.inf, 30.0 * scale, 0.01],
        ),
    )
    a1, s1, a2, s2 = r.x[0], abs(r.x[1]), r.x[2], abs(r.x[3])
    return {
        "body": body, "sharpA": a1, "sharpSigma": s1, "heavyA": a2, "heavySigma": s2,
        "rms": float(np.sqrt((r.fun ** 2).mean())), "integral": float(y.sum() / scale),
    }


def main(argv):
    print(f"{'label':22}{'scale':>6}{'body':>9}{'sharp A':>10}{'sharp σ dev':>13}"
          f"{'σ css':>8}{'heavy A':>10}{'heavy σ dev':>13}{'rms':>10}{'∫ css':>9}")
    for spec in argv:
        label, rest = spec.split("=", 1)
        path, scale_s = rest.rsplit(":", 1)
        scale = float(scale_s)
        f = fit(path, scale)
        print(f"{label:22}{scale:6.0f}{f['body']:9.5f}{f['sharpA']:10.5f}"
              f"{f['sharpSigma']:13.2f}{f['sharpSigma'] / scale:8.2f}{f['heavyA']:10.5f}"
              f"{f['heavySigma']:13.2f}{f['rms']:10.5f}{f['integral']:9.4f}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
