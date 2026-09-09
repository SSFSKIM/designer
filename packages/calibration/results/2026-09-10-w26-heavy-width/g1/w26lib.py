"""W26 G1 — reader D: the impulse tile as a lattice, fitted over the WHOLE tile.

WHY A FOURTH READER. W25 G0's reader A fits one dot's profile, and W26 G0 measured the consequence
(claims §5.119 §3, W26 Decision Log 2 (c)): its window is half the 64 CSS px dot pitch, which is 30
device px at dpr 1, and a heavy component of 19.5 device px does not fit in a 30 device px
half-window. The 1x ladder therefore parks on the reader's own bound above σ ≈ 17 while the 2x
ladder over the same constant — the SAME drawn kernel, because the plan divides by the ratio and
the raster multiplies it back — is monotone over the whole range. The instrument, not the material.

WHAT READER D DOES DIFFERENTLY. It never windows. The impulse backdrop is a periodic lattice of
4 CSS px squares 64 CSS px apart, so the whole transmitted tile is one measurement of the kernel:
the model is the backdrop raster itself convolved with a sharp Gaussian and a heavy Gaussian at
their own amplitudes, fitted over every pixel of the eroded interior at once. A kernel wider than
the pitch is then not out of the window — it is a kernel that has flattened the lattice, and the
depth of what modulation survives is exactly what identifies it.

WHAT IT CAN AND CANNOT RESOLVE, stated before it is used. A Gaussian's modulation transfer at the
lattice's fundamental (pitch p, σ in the same units) is exp(−2π²σ²/p²): at the 1x pitch of 64
device px that is 16 % at σ 19.5 and 5 % at σ 25. The heavy component carries only its share of
that, so past about σ 25 at 1x the heavy component's whole signature is inside the raster's own
8-bit step and reader D is reading its bound rather than a width. Every reading here reports
`atCeiling` and the modulation depth it had to work with, so that cannot be discovered later.

THE FIT'S SHAPE, and why it is only two-dimensional. The model is LINEAR in the two amplitudes
given the two widths — reader A's structure — so the amplitudes are solved exactly at every
candidate pair by non-negative least squares and only (σ_sharp, σ_heavy) are searched. The
non-negativity is reader A's bound and is here for reader A's reason: without it the fit can spend a
large positive and a large negative Gaussian of similar width on any profile.

WHAT ELSE IS IN THE MODEL, and why. A low-order polynomial in the pixel coordinates (constant,
linear, quadratic) is fitted beside the two blurs and projected out before the amplitudes are
solved. The interior of a glass surface is not a pure convolution of its backdrop: the tone
response, the tint and the size law's own level all vary smoothly across it, and a reader that did
not absorb them would spend heavy amplitude on the gradient. The polynomial cannot imitate the
lattice, whose period is far shorter than anything it can bend.

THE ONE THING THAT HAD TO BE ENGINEERED AROUND, measured before it was: **the 8-bit step**. On the
1x `impulse` fixtures the whole surviving interior modulation is about one display code — the
native `impulse__rrect-lg` interior reads a standard deviation of 0.0055 in linear luma at a level
of 0.453, where one 8-bit sRGB code IS 0.0059 — and the heavy component's share of it is a fraction
of that. Quantisation is then not noise but a deterministic staircase of the field, concentrated
where the field is steepest, which is at the dot cores; fitted naively, a spurious NARROW second
component fits that staircase better than the true wide one does. The first build of this reader
returned 4.3 device px for a drawn 10.0 on exactly that.

A matched low-pass was the obvious answer and it is here, as `SMOOTH_SIGMA` — the image and every
model column put through one Gaussian, computed as a normalised convolution against the cell's own
mask so the rim outside it cannot leak in and so the operator applied to the data is EXACTLY the
operator applied to the model. It is exact on the model (a Gaussian of a Gaussian is a Gaussian).
**It does not work, and the default is 0 because it does not**: `g1-validate.py` scans it over
0 → 4 device px on synthetics at the fixtures' own contrast and every setting reads a drawn 10.0 as
between 3.8 and 4.9, because the low-pass that quiets the staircase also collapses the sharp
component into the heavy one. The scan is kept in the record; the finding it produced is §2 of
`reader-d.txt`, and it is a finding about the FIXTURE rather than about any reader.

UNITS. Sigmas in DEVICE px, W25 G0's unit throughout. This module imports `w25lib` and does not
edit it (X1): reader A stays exactly the instrument the ledger's numbers were read with.
"""

import math
import os
import sys

import numpy as np
from scipy.ndimage import gaussian_filter
from scipy.optimize import least_squares, nnls

HERE = os.path.dirname(os.path.abspath(__file__))
W25G0 = os.path.abspath(os.path.join(HERE, "..", "..",
                                     "2026-09-09-w25-thick-span-composite", "g0"))
if W25G0 not in sys.path:
    sys.path.insert(0, W25G0)
import w25lib as L  # noqa: E402

# The search's own bounds, in DEVICE px. The floor is under one texel, so a kernel narrower than the
# raster is representable rather than clamped; the ceiling is 60 * scale, which is reader A's own
# ceiling on its heavy component, so a reading that hits it is comparable with reader A hitting its.
SHARP_MIN = 0.3
SHARP_MAX = 16.0
HEAVY_MAX = 60.0
# The polynomial the interior's own smooth structure is absorbed into (see the note above).
POLY_ORDER = 2
# The matched low-pass, in device px at scale 1, applied identically to the image and to every
# model column. Zero: it was measured and it does not help (see the note on the 8-bit step above).
SMOOTH_SIGMA = 0.0


def _poly_basis(ys, xs, shape):
    """Normalised polynomial terms up to `POLY_ORDER` on the mask's own coordinates."""
    h, w = shape
    u = (xs / max(w - 1, 1)) * 2.0 - 1.0
    v = (ys / max(h - 1, 1)) * 2.0 - 1.0
    cols = [np.ones_like(u)]
    if POLY_ORDER >= 1:
        cols += [u, v]
    if POLY_ORDER >= 2:
        cols += [u * u, v * v, u * v]
    return np.stack(cols, axis=1)


def _sigma_grid(scale):
    """The two search grids, geometric so the resolution is proportional to the width."""
    sharp = np.exp(np.linspace(math.log(SHARP_MIN * scale), math.log(SHARP_MAX * scale), 40))
    heavy = np.exp(np.linspace(math.log(1.0 * scale), math.log(HEAVY_MAX * scale), 56))
    return sharp, heavy


def _smoother(mask, sigma):
    """A normalised convolution against `mask`: the matched low-pass, edge-exact by construction.

    Smoothing the raw image would pull the rim, the lens's turn and the outer shadow into the
    interior; dividing by the smoothed mask instead averages only what is inside it. The same
    operator is applied to every model column, so whatever it does to the data it does to the
    model.
    """
    if not (sigma > 1e-6):
        return lambda field: field[mask]
    weight = gaussian_filter(mask.astype(np.float64), sigma, mode="constant", cval=0.0)
    safe = np.where(weight > 1e-6, weight, 1.0)

    def op(field):
        num = gaussian_filter(np.where(mask, field, 0.0), sigma, mode="constant", cval=0.0)
        return (num / safe)[mask]

    return op


def lattice_fit(lum, bg, mask, scale, seed=None, smooth=None):
    """Reader D on one cell. `lum` and `bg` are device-px luma; `mask` selects the interior.

    Returns sigmas in DEVICE px, the heavy component's amplitude share, the fit's relative residual,
    and the lattice modulation the fit had to work with.
    """
    ys, xs = np.nonzero(mask)
    if ys.size < 400:
        return None
    lp = SMOOTH_SIGMA * scale if smooth is None else smooth
    op = _smoother(mask, lp)
    y = op(lum.astype(np.float64))
    P = _poly_basis(ys.astype(np.float64), xs.astype(np.float64), lum.shape)
    # Orthonormalise the polynomial subspace once and project everything through it, so the two
    # amplitudes below are solved on what the smooth terms cannot explain.
    Q, _ = np.linalg.qr(P)
    def project(v):
        return v - Q @ (Q.T @ v)
    yr = project(y)
    signal = float(np.std(yr)) or 1e-12

    cache = {}
    def column(sigma):
        key = round(float(sigma), 4)
        if key not in cache:
            cache[key] = project(op(gaussian_filter(bg, key, mode="nearest")))
        return cache[key]

    def solve(s1, s2):
        A = np.stack([column(s1), column(s2)], axis=1)
        try:
            coef, _ = nnls(A, yr)
        except Exception:
            return float("inf"), (0.0, 0.0)
        resid = float(np.sqrt(np.mean((A @ coef - yr) ** 2)))
        return resid, (float(coef[0]), float(coef[1]))

    sharp_grid, heavy_grid = _sigma_grid(scale)
    best = (float("inf"), SHARP_MIN * scale, 2.0 * scale, (0.0, 0.0))
    for s1 in sharp_grid:
        for s2 in heavy_grid:
            if s2 <= s1 * 1.15:
                continue
            r, coef = solve(s1, s2)
            if r < best[0]:
                best = (r, float(s1), float(s2), coef)
    if seed is not None:
        r, coef = solve(*seed)
        if r < best[0]:
            best = (r, float(seed[0]), float(seed[1]), coef)

    # Continuous refinement in log width, from the grid's minimum. The amplitudes stay solved
    # exactly at every step, so the refinement is over two numbers however wide the pair is.
    lo = [math.log(SHARP_MIN * scale), math.log(0.5 * scale)]
    hi = [math.log(SHARP_MAX * scale), math.log(HEAVY_MAX * scale)]
    def residual_vec(q):
        s1, s2 = math.exp(q[0]), math.exp(max(q[1], q[0] + 1e-3))
        A = np.stack([column(s1), column(s2)], axis=1)
        try:
            coef, _ = nnls(A, yr)
        except Exception:
            return np.full(yr.size, 1e3)
        return A @ coef - yr
    q0 = [min(max(math.log(best[1]), lo[0]), hi[0]), min(max(math.log(best[2]), lo[1]), hi[1])]
    try:
        out = least_squares(residual_vec, q0, bounds=(lo, hi), diff_step=0.02, xtol=1e-4)
        s1, s2 = math.exp(out.x[0]), math.exp(max(out.x[1], out.x[0] + 1e-3))
        r, coef = solve(s1, s2)
        if r <= best[0]:
            best = (r, s1, s2, coef)
    except Exception:
        pass

    resid, s1, s2, (a1, a2) = best
    total = a1 + a2
    # What the lattice still carried at the fitted heavy width, so a reading at the instrument's
    # own limit is visible as one. `L.backdrop_pitch_css` has no entry for `impulse`; the pitch is
    # the scene's own 64 CSS px.
    pitch = 64.0 * scale
    mtf_heavy = math.exp(-2.0 * math.pi ** 2 * s2 * s2 / (pitch * pitch))
    return {
        "sharpSigmaDev": s1,
        "heavySigmaDev": s2,
        "sharpA": a1,
        "heavyA": a2,
        "heavyShare": float(a2 / total) if total > 0 else float("nan"),
        "rmsRel": resid / signal,
        "n": int(ys.size),
        "signal": signal,
        "heavyMtf": mtf_heavy,
        "heavyMod": mtf_heavy * (float(a2 / total) if total > 0 else 0.0),
        "atCeiling": bool(s2 > HEAVY_MAX * scale * 0.995 or s1 > SHARP_MAX * scale * 0.995),
        "sigmaEquivDev": L.kernel_sigma_equiv(a1, s1, a2, s2),
    }


def read_lattice_cell(lum, bg, cell, scale, erode=12.0):
    """Reader D over one impulse cell's whole eroded interior.

    The erosion is wider than reader A's 6 CSS px on purpose: reader A subtracts a local body level
    per dot and can afford to sit closer to the rim, while reader D fits one model across the whole
    interior and the rim's own band, the lens's displacement and the inner shadow are none of them
    a convolution of the backdrop. Twelve CSS px clears the rim band and the lens's turn on every
    component this wave reads.
    """
    mask = cell.body_mask(scale, lum.shape, erode)
    return lattice_fit(lum, bg, mask, scale)
