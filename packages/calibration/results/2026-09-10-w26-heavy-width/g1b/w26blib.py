"""W26 G1b — reader E: the point spread recovered NON-PARAMETRICALLY, jointly over many backdrops.

WHY A FIFTH READER. Every reader this wave has used — W25's reader A, W26 G1's reader D, and the
joint fit of G1 §7.6 — models the transmitted kernel as a SUM OF TWO GAUSSIANS. G1 §7.5 and §7.6
measured what that costs: the same surface's "heavy width" comes back as 18.2 device px read
through the `impulse` tile, 6.0–7.1 through `checkerboard-64` and 11.1–12.4 through both at once,
each already debiased by what the same instrument reads on vitrea's own KNOWN kernel. A factor of
three. A two-Gaussian basis is a two-number projection of a kernel, and which two numbers you get
depends on which frequencies the backdrop you read it through happens to carry. So this reader
assumes no shape at all.

WHAT IT ASSUMES INSTEAD, and why each assumption is safe here.

  * The kernel is RADIALLY SYMMETRIC and is one profile K(r) on a radial grid, non-negative and of
    unit mass. Non-negativity is physical for a scatter kernel; unit mass is only a gauge, since a
    per-backdrop gain is fitted beside it.
  * The interior maps to the backdrop AFFINELY: observed ≈ a_b · (backdrop ⊛ K) + b_b, one gain and
    one offset per backdrop. This is not an approximation of convenience — it is what
    `wgsl/optics.ts` does. The tone response reads `toneColour`, the backdrop SOURCE's own average,
    which is one number per scene and not a per-pixel sample; the tint mix and the size law's level
    are then constants over a band of constant depth. So on vitrea the affine model is exact in the
    deep interior, and on the reference it is the same one-parameter-per-backdrop freedom every
    earlier reader gave itself as a polynomial.
  * The reading is taken on a BAND OF CONSTANT DEPTH. Vitrea's own share is a function of depth —
    `sharpShare = sDeep + max(rampStart − sDeep, 0) · max(1 − depth/reach, 0)` with a reach of 80
    device px at 1x — so a kernel read over a whole interior is a depth average whatever the reader
    does. Reading in bands makes that visible instead of silent, and the band's own spread of the
    known share is reported with every control.

HOW IT IS SOLVED. K = Σ_j c_j Λ_j(r) with Λ_j the hat function at radial node r_j, so K ≥ 0 is
exactly c ≥ 0 and the model is LINEAR in c given the gains: (B ⊛ K) = Σ_j c_j (B ⊛ Λ_j). The
convolutions B ⊛ Λ_j are computed once per backdrop and cached. Gains and profile are then
alternated — c by non-negative least squares on the stacked rows with a second-difference
smoothness penalty, (a_b, b_b) by ordinary least squares — which is the standard alternation for a
bilinear problem and converges in a handful of sweeps because each half is convex and solved
exactly.

THE SMOOTHNESS WEIGHT IS NOT TUNED ON THE ANSWER. λ is chosen once, on SYNTHETICS with known
kernels at the fixtures' own measured levels and contrasts and through the 8-bit step, and then
frozen for the control and for the reference alike. A regulariser fitted to the thing being
measured is not a regulariser.

BOUNDARY. The backdrop raster is the 320 × 200 canvas and nothing else exists on either side: the
web tier's chain samples it clamped to its edge, and the native harness's window is the same
rectangle. Padding is therefore edge-replicate by default, with `pad="wrap"` available as the
sensitivity check the periodic backdrops permit — a kernel of 60 device px reaches outside the
canvas from `rrect-lg`'s interior, and how much that matters is measured rather than assumed.

UNITS. Radii and sigmas in DEVICE px of the image read, W25 G0's unit throughout. Frequencies in
cycles per DEVICE px. This module imports `w25lib` for decoding, geometry and masks and does not
edit it (X1).
"""

import math
import os
import sys

import numpy as np
from scipy.optimize import nnls
from scipy.special import j0

HERE = os.path.dirname(os.path.abspath(__file__))
W25G0 = os.path.abspath(os.path.join(HERE, "..", "..",
                                     "2026-09-09-w25-thick-span-composite", "g0"))
if W25G0 not in sys.path:
    sys.path.insert(0, W25G0)
import w25lib as L  # noqa: E402


# --------------------------------------------------------------------------- the radial basis

def radial_nodes(extent_dev, count=40, power=1.7):
    """Node radii, denser near the core where a sharp component lives.

    `power` > 1 puts the nodes on a curve rather than uniformly: the first spacing is a fraction of
    a texel, which the sharp component needs, and the last is a few texels, which is all the tail
    can be resolved to anyway.
    """
    t = np.arange(count + 1, dtype=np.float64) / count
    return extent_dev * t ** power


def hat_kernels(nodes, oversample=4):
    """The 2D hat basis: one kernel image per node, sampled with `oversample`² sub-pixels.

    Returns (kernels, masses). `masses[j]` is Σ Λ_j over the pixel grid, so a profile c has total
    mass `masses @ c` — the gauge the fit is normalised by.
    """
    extent = float(nodes[-1])
    half = int(math.ceil(extent))
    size = 2 * half + 1
    off = (np.arange(oversample) + 0.5) / oversample - 0.5
    ys = (np.arange(size) - half)[:, None] + off[None, :]
    xs = ys
    yy = ys.reshape(-1)[:, None]
    xx = xs.reshape(-1)[None, :]
    rr = np.hypot(yy, xx)
    ker = np.zeros((nodes.size, size, size))
    for j, r0 in enumerate(nodes):
        lo = nodes[j - 1] if j > 0 else None
        hi = nodes[j + 1] if j + 1 < nodes.size else None
        w = np.zeros_like(rr)
        if lo is None:
            w = np.where(rr <= r0, 1.0, 0.0)
        else:
            m = (rr > lo) & (rr <= r0)
            w[m] = (rr[m] - lo) / max(r0 - lo, 1e-9)
        if hi is not None:
            m = (rr > r0) & (rr < hi)
            w[m] = (hi - rr[m]) / max(hi - r0, 1e-9)
        elif lo is not None:
            w[rr > r0] = 0.0
        block = w.reshape(size, oversample, size, oversample).mean(axis=(1, 3))
        ker[j] = block
    masses = ker.sum(axis=(1, 2))
    return ker, masses


def profile_to_kernel(nodes, c, oversample=4, _cache={}):
    """The 2D image of a radial profile, for MTF and moment statistics on the same footing."""
    key = (float(nodes[-1]), int(nodes.size), oversample)
    if key not in _cache:
        _cache[key] = hat_kernels(nodes, oversample)
    ker, _ = _cache[key]
    return np.tensordot(c, ker, axes=(0, 0))


# --------------------------------------------------------------------------- backdrop columns

def _pad(bg, half, mode):
    if mode == "wrap":
        return np.pad(bg, half, mode="wrap")
    return np.pad(bg, half, mode="edge")


def basis_columns(bg, nodes, oversample=4, pad="edge", _cache={}):
    """`bg ⊛ Λ_j` for every node, as a stack of images the same shape as `bg`.

    One padded rFFT of the backdrop and one per kernel, multiplied and inverted — the same answer
    as `fftconvolve` per node at a fraction of the work, which matters because the driver asks for
    forty nodes over eight backdrops at two scales.
    """
    key = (float(nodes[-1]), int(nodes.size), oversample)
    if key not in _cache:
        _cache[key] = hat_kernels(nodes, oversample)
    ker, _ = _cache[key]
    half = (ker.shape[1] - 1) // 2
    padded = _pad(bg, half, pad)
    h, w = padded.shape
    fh, fw = h + ker.shape[1] - 1, w + ker.shape[2] - 1
    F = np.fft.rfft2(padded, s=(fh, fw))
    out = np.empty((ker.shape[0],) + bg.shape)
    for j in range(ker.shape[0]):
        G = np.fft.rfft2(ker[j], s=(fh, fw))
        full = np.fft.irfft2(F * G, s=(fh, fw))
        # `full` is the linear convolution; the pixel co-located with padded[y, x] sits at
        # [y + half, x + half], and the unpadded image starts at padded[half, half].
        out[j] = full[2 * half:2 * half + bg.shape[0], 2 * half:2 * half + bg.shape[1]]
    return out


# --------------------------------------------------------------------------- the joint fit

def _second_difference(nodes):
    n = nodes.size
    D = np.zeros((max(n - 2, 0), n))
    for i in range(1, n - 1):
        hl = nodes[i] - nodes[i - 1]
        hr = nodes[i + 1] - nodes[i]
        D[i - 1, i - 1] = 2.0 / (hl * (hl + hr))
        D[i - 1, i] = -2.0 / (hl * hr)
        D[i - 1, i + 1] = 2.0 / (hr * (hl + hr))
    return D


def joint_profile(rows, nodes, lam=1e-3, sweeps=12, tol=1e-7):
    """One K over every row at once, with a per-row gain and offset.

    `rows` is a list of dicts with `A` (nodes × pixels, the basis columns already masked) and `y`
    (pixels). Returns the profile, the per-row gains and offsets, and the per-row relative residual.
    """
    D = _second_difference(nodes)
    n = nodes.size
    # Each row is normalised by its own signal so a high-contrast checkerboard cannot outvote a
    # low-contrast one by loudness alone; the gain is what carries the contrast.
    for r in rows:
        r["sd"] = float(np.std(r["y"])) or 1e-12
    gains = []
    for r in rows:
        # A first gain from the row's own best single-scale match to a mid-width column.
        m = r["A"][n // 2]
        gains.append(float(np.std(r["y"]) / (np.std(m) or 1e-12)))
    offs = [float(np.mean(r["y"])) for r in rows]
    c = np.zeros(n)
    c[:] = 1.0 / n
    prev = None
    for _ in range(sweeps):
        # --- c step: stack every row, weighted, with the smoothness rows appended.
        blocks, targets = [], []
        for r, g, b in zip(rows, gains, offs):
            wgt = 1.0 / (r["sd"] * math.sqrt(r["y"].size))
            blocks.append((g * wgt) * r["A"].T)
            targets.append(wgt * (r["y"] - b))
        scale = np.mean([np.linalg.norm(bl) for bl in blocks]) / math.sqrt(n)
        blocks.append(lam * scale * D)
        targets.append(np.zeros(D.shape[0]))
        M = np.vstack(blocks)
        t = np.concatenate(targets)
        c, _ = nnls(M, t, maxiter=8 * n)
        s = float(c.sum())
        if s <= 0:
            break
        # --- gauge: unit mass on the pixel grid, the factor folded into the gains.
        mass = float(_masses(nodes) @ c)
        if mass > 0:
            c = c / mass
            gains = [g * mass for g in gains]
        # --- gain/offset step: ordinary least squares per row, exactly.
        new_g, new_o = [], []
        for r in rows:
            m = c @ r["A"]
            X = np.stack([m, np.ones_like(m)], axis=1)
            sol, *_ = np.linalg.lstsq(X, r["y"], rcond=None)
            new_g.append(float(sol[0]))
            new_o.append(float(sol[1]))
        gains, offs = new_g, new_o
        obj = 0.0
        for r, g, b in zip(rows, gains, offs):
            res = g * (c @ r["A"]) + b - r["y"]
            obj += float(np.mean(res ** 2)) / (r["sd"] ** 2)
        if prev is not None and abs(prev - obj) < tol * max(prev, 1e-12):
            prev = obj
            break
        prev = obj
    per = []
    for r, g, b in zip(rows, gains, offs):
        res = g * (c @ r["A"]) + b - r["y"]
        per.append({"name": r.get("name", "?"), "gain": g, "offset": b,
                    "rmsRel": float(np.sqrt(np.mean(res ** 2))) / r["sd"],
                    "n": int(r["y"].size)})
    return {"c": c, "nodes": nodes, "per": per,
            "rmsRel": float(math.sqrt(prev / len(rows))) if prev is not None else float("nan")}


def _masses(nodes, _cache={}):
    key = (float(nodes[-1]), int(nodes.size))
    if key not in _cache:
        _cache[key] = hat_kernels(nodes)[1]
    return _cache[key]


# --------------------------------------------------------------------------- statistics on a K

def mtf_of_profile(nodes, c, freqs):
    """The radial kernel's modulation transfer, by Hankel transform of the hat basis.

    Exact for the piecewise-linear profile the fit returns: MTF(f) = ∫ K(r) J₀(2πfr) 2πr dr,
    integrated on a fine radial quadrature and normalised by the same integral at f = 0.
    """
    r = np.linspace(0.0, float(nodes[-1]), 4001)
    k = np.interp(r, nodes, c)
    w = k * 2.0 * math.pi * r
    norm = np.trapezoid(w, r)
    out = []
    for f in np.atleast_1d(freqs):
        out.append(float(np.trapezoid(w * j0(2.0 * math.pi * f * r), r) / max(norm, 1e-300)))
    return np.array(out)


def widths_of_profile(nodes, c):
    """Three Gaussian-equivalent widths of one radial profile, each named by how it is taken."""
    r = np.linspace(0.0, float(nodes[-1]), 4001)
    k = np.interp(r, nodes, c)
    w = k * 2.0 * math.pi * r
    mass = np.trapezoid(w, r)
    # Second moment: for a 2D radial kernel, <r²> = 2σ² for a Gaussian.
    m2 = np.trapezoid(w * r * r, r) / max(mass, 1e-300)
    sigma_rms = math.sqrt(max(m2, 0.0) / 2.0)
    # Half maximum of the PROFILE (the statistic reader A reduces its kernels by).
    peak = float(k[0])
    sigma_hwhm = float("nan")
    if peak > 0:
        below = np.nonzero(k <= peak / 2.0)[0]
        if below.size:
            i = int(below[0])
            if i > 0:
                r0, r1 = r[i - 1], r[i]
                k0, k1 = k[i - 1], k[i]
                hw = r0 + (k0 - peak / 2.0) / max(k0 - k1, 1e-300) * (r1 - r0)
            else:
                hw = r[0]
            sigma_hwhm = hw / math.sqrt(2.0 * math.log(2.0))
    return {"sigmaRms": sigma_rms, "sigmaHwhm": sigma_hwhm, "peak": peak, "mass": float(mass)}


MTF_BAND = (1.0 / 64.0, 1.0 / 8.0)


def band_freqs(n=25, band=MTF_BAND):
    return np.exp(np.linspace(math.log(band[0]), math.log(band[1]), n))


def sigma_matching_mtf(nodes, c, band=MTF_BAND, n=25):
    """The Gaussian sigma whose MTF best matches K's over the band, in log-modulation least squares.

    Log rather than linear because the band spans two decades of modulation and a linear fit would
    be decided entirely by its bottom end.
    """
    f = band_freqs(n, band)
    m = np.clip(mtf_of_profile(nodes, c, f), 1e-9, None)
    lm = np.log(m)
    # log MTF of a Gaussian is -2π²σ²f², linear in σ²: one exact least squares, no search.
    x = -2.0 * math.pi ** 2 * f * f
    s2 = float((x @ lm) / (x @ x))
    sigma = math.sqrt(max(s2, 0.0))
    fit = x * s2
    rel = float(np.sqrt(np.mean((np.exp(fit) / m - 1.0) ** 2)))
    return sigma, rel, f, m, np.exp(fit)


def mtf_of_kernel2d(ker, freqs):
    """MTF of an arbitrary 2D kernel, radially averaged, on the same frequency axis."""
    n = 1024
    pad = np.zeros((n, n))
    h, w = ker.shape
    pad[:h, :w] = ker
    F = np.abs(np.fft.fft2(pad))
    F = F / max(F[0, 0], 1e-300)
    fy = np.fft.fftfreq(n)[:, None]
    fx = np.fft.fftfreq(n)[None, :]
    rad = np.hypot(fy, fx)
    out = []
    for f in np.atleast_1d(freqs):
        m = np.abs(rad - f) < (0.6 / n)
        out.append(float(F[m].mean()) if m.any() else float("nan"))
    return np.array(out)


def radial_profile_of_kernel2d(ker, nodes):
    """Bin a 2D kernel onto the same radial nodes, so any kernel can be compared as a profile."""
    h, w = ker.shape
    cy, cx = (h - 1) / 2.0, (w - 1) / 2.0
    yy, xx = np.mgrid[0:h, 0:w]
    rr = np.hypot(yy - cy, xx - cx)
    prof = np.zeros(nodes.size)
    for j, r0 in enumerate(nodes):
        lo = 0.0 if j == 0 else (nodes[j - 1] + r0) / 2.0
        hi = float(nodes[-1]) if j + 1 == nodes.size else (r0 + nodes[j + 1]) / 2.0
        m = (rr >= lo) & (rr < hi)
        prof[j] = float(ker[m].mean()) if m.any() else 0.0
    mass = float(_masses(nodes) @ prof)
    return prof / max(mass, 1e-300)


# --------------------------------------------------------------------------- shape approximations

def gauss_profile(nodes, sigma):
    r = np.asarray(nodes, dtype=np.float64)
    k = np.exp(-0.5 * (r / max(sigma, 1e-9)) ** 2)
    mass = float(_masses(nodes) @ k)
    return k / max(mass, 1e-300)


def fit_two_gaussians(nodes, c):
    """The best two-Gaussian approximation of K, and what it leaves behind.

    Fitted on the MASS-WEIGHTED profile so the comparison is over the kernel's energy rather than
    over its core, which is what a two-Gaussian reader on a real backdrop is doing.
    """
    from scipy.optimize import least_squares
    w = np.sqrt(_masses(nodes))
    target = w * c

    def model(p):
        s1, s2, share = math.exp(p[0]), math.exp(p[0]) + math.exp(p[1]), 1 / (1 + math.exp(-p[2]))
        g = (1 - share) * gauss_profile(nodes, s1) + share * gauss_profile(nodes, s2)
        return w * g

    best = None
    for s2 in (5.0, 10.0, 20.0, 35.0):
        for sh in (0.3, 0.7):
            p0 = [math.log(1.5), math.log(max(s2 - 1.5, 0.2)), math.log(sh / (1 - sh))]
            try:
                out = least_squares(lambda p: model(p) - target, p0, xtol=1e-10)
            except Exception:
                continue
            if best is None or out.cost < best.cost:
                best = out
    if best is None:
        return None
    s1 = math.exp(best.x[0])
    s2 = s1 + math.exp(best.x[1])
    share = 1 / (1 + math.exp(-best.x[2]))
    res = model(best.x) - target
    return {"sharp": s1, "heavy": s2, "share": share,
            "rel": float(np.linalg.norm(res) / max(np.linalg.norm(target), 1e-300))}


def fit_vitrea_mechanism(nodes, c, chain_profiles, band=MTF_BAND):
    """Can a sharp Gaussian plus a CHAIN LEVEL blurred by a Gaussian reproduce K's MTF?

    `chain_profiles` maps a chain level to its radial profile on `nodes`. The search is over the
    level, the residual Gaussian the level is blurred by, the sharp Gaussian and the share — which
    is exactly `wgsl/optics.ts`'s composite once `heavyTapPlan` has chosen a level, so a match
    states the sigma the material would have to name.
    """
    from scipy.optimize import least_squares
    f = band_freqs(31, band)
    target = np.log(np.clip(mtf_of_profile(nodes, c, f), 1e-9, None))
    best = None
    for level, prof in sorted(chain_profiles.items()):
        base = np.log(np.clip(mtf_of_profile(nodes, prof, f), 1e-12, None))

        def model(p):
            blur = math.exp(p[0])
            sharp = math.exp(p[1])
            share = 1 / (1 + math.exp(-p[2]))
            heavy = np.exp(base - 2.0 * math.pi ** 2 * blur * blur * f * f)
            sg = np.exp(-2.0 * math.pi ** 2 * sharp * sharp * f * f)
            return np.log(np.clip((1 - share) * sg + share * heavy, 1e-12, None))

        for blur0 in (0.5, 3.0, 8.0):
            for sh0 in (0.4, 0.8, 0.99):
                p0 = [math.log(blur0), math.log(1.5), math.log(sh0 / (1 - sh0))]
                try:
                    out = least_squares(lambda p: model(p) - target, p0, xtol=1e-10)
                except Exception:
                    continue
                rel = float(np.sqrt(np.mean((np.exp(model(out.x) - target) - 1.0) ** 2)))
                cand = {"level": level, "blur": math.exp(out.x[0]), "sharp": math.exp(out.x[1]),
                        "share": 1 / (1 + math.exp(-out.x[2])), "relMtf": rel}
                if best is None or rel < best["relMtf"]:
                    best = cand
    return best
