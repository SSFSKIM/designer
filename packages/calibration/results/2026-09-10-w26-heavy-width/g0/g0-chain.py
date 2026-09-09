"""W26 G0 — the backdrop pyramid's own kernel, simulated exactly, level by level.

WHY A SIMULATION AND NOT A CAPTURE. Deliverable 1 asks what filter builds each chain level and how
its effective width compares with a Gaussian. That is a property of `wgsl/backdrop.ts`'s 13-tap
progressive downsample and of the bilinear reconstruction `textureSampleLevel` performs when the
optics pass reads a level — arithmetic, not material, so it is answered exactly here instead of
being inferred from a render. The renders answer the other half of deliverable 1: what the RENDERER
draws at each `sizeScatterGainMax`, which is the reading `g0-gains.py` takes with reader A.

WHAT IS SIMULATED. `WGSL_DOWNSAMPLE_PASS`, verbatim in its arithmetic:

  * the destination texel centre sits at `2j + 1` in SOURCE texel coordinates, so every one of the
    13 taps lands on a half-integer position and is therefore an exact 2x2 box average of the
    source level — that is the "sampled bilinearly so the 13 taps cover a 4x4 footprint" the
    module note describes, stated as arithmetic;
  * the weights are the module's: the four inner taps at (+-1,+-1) carry 0.125 each, the centre
    0.125, the four edge taps 0.0625 and the four corner taps 0.03125, summing to exactly 1;
  * a level is then read back at level-0 resolution by bilinear reconstruction, which is what the
    optics pass's `textureSampleLevel(backdropChain, s, uv, lod)` does at an integer `lod`.

WHAT IS REPORTED per level: the second-moment sigma of the reconstructed point spread in LEVEL-0
texels, the sigma a Gaussian with the same half-width at half maximum would have (the statistic
W25 G0's reader A reduces its two-component kernel by, so the two are directly comparable), the
kurtosis excess against a Gaussian's, and the worst absolute deviation from the best-fitting
Gaussian as a fraction of the peak. `CHAIN_SIGMA_AT_LEVEL_1`, the advisory constant
`pyramid-plan.ts` converts a sigma to a level with, is printed beside the measured level-1 value.
"""

import math
import os
import sys

import numpy as np

N = 1024
LEVELS = 7


def box2x2(a):
    """One bilinear tap at a half-integer position: the 2x2 average centred there.

    Implemented as a shift-and-average so the whole 13-tap pass stays exact rather than resampled.
    """
    return 0.25 * (a + np.roll(a, -1, 0) + np.roll(a, -1, 1) + np.roll(np.roll(a, -1, 0), -1, 1))


TAPS = [
    # (ox, oy, weight) in SOURCE texels, from `WGSL_DOWNSAMPLE_PASS`'s weight algebra.
    (0, 0, 0.125),
    (-1, 1, 0.125), (1, 1, 0.125), (-1, -1, 0.125), (1, -1, 0.125),
    (0, 2, 0.0625), (-2, 0, 0.0625), (2, 0, 0.0625), (0, -2, 0.0625),
    (-2, 2, 0.03125), (2, 2, 0.03125), (-2, -2, 0.03125), (2, -2, 0.03125),
]


def downsample(src):
    """`fs_downsample`, exactly: 13 half-integer taps, then decimate by two."""
    acc = np.zeros_like(src)
    base = box2x2(src)
    for ox, oy, w in TAPS:
        acc += w * np.roll(np.roll(base, -oy, 0), -ox, 1)
    # The destination texel j reads at source position 2j+1; `base` is indexed by the LOW texel of
    # each 2x2, which for that position is 2j. So the decimation takes the even columns and rows.
    return acc[::2, ::2]


def reconstruct(level, factor):
    """Bilinear reconstruction of a level back onto the level-0 grid — `textureSampleLevel`."""
    h, w = level.shape
    out = np.zeros((h * factor, w * factor))
    # Level-0 texel centre (p + 0.5) in level-`n` texel coordinates is (p + 0.5) / factor.
    coord = (np.arange(h * factor) + 0.5) / factor - 0.5
    i0 = np.floor(coord).astype(int)
    t = coord - i0
    i0 = np.clip(i0, 0, h - 1)
    i1 = np.clip(i0 + 1, 0, h - 1)
    rows = (1 - t)[:, None] * level[i0] + t[:, None] * level[i1]
    j0 = np.clip(np.floor(coord).astype(int), 0, w - 1)
    j1 = np.clip(j0 + 1, 0, w - 1)
    tw = coord - np.floor(coord)
    out = (1 - tw)[None, :] * rows[:, j0] + tw[None, :] * rows[:, j1]
    return out


def stats(psf, centre):
    """Second-moment sigma, HWHM-equivalent sigma, kurtosis, and the Gaussian residual."""
    line = psf[centre, :]
    line = line / line.sum()
    x = np.arange(line.size) - centre
    mean = float((line * x).sum())
    var = float((line * (x - mean) ** 2).sum())
    sigma = math.sqrt(max(var, 0.0))
    m4 = float((line * (x - mean) ** 4).sum())
    kurt = m4 / (var * var) - 3.0 if var > 0 else float("nan")
    peak = float(line.max())
    half = np.nonzero(line >= peak / 2.0)[0]
    lo, hi = half[0], half[-1]
    # Sub-texel HWHM by linear interpolation on each flank.
    def cross(a, b):
        return a + (line[a] - peak / 2.0) / (line[a] - line[b]) if line[a] != line[b] else float(a)
    left = cross(lo, lo - 1) if lo > 0 else float(lo)
    right = cross(hi, hi + 1) if hi + 1 < line.size else float(hi)
    hwhm = (right - left) / 2.0
    sigma_hwhm = hwhm / math.sqrt(2.0 * math.log(2.0))
    g = peak * np.exp(-0.5 * ((x - mean) / max(sigma_hwhm, 1e-9)) ** 2)
    worst = float(np.abs(line - g).max() / peak)
    return sigma, sigma_hwhm, kurt, worst


def main():
    delta = np.zeros((N, N))
    delta[N // 2, N // 2] = 1.0
    out = []
    out.append("W26 G0 — the backdrop pyramid's kernel per level, simulated exactly")
    out.append("=" * 100)
    out.append("`wgsl/backdrop.ts`'s 13-tap progressive downsample applied to a level-0 delta, each")
    out.append("level read back at level-0 resolution the way `textureSampleLevel` reads it.")
    out.append("Sigmas in LEVEL-0 texels. sigmaHWHM is the statistic W25 G0's reader A reduces a")
    out.append("kernel by, so it is the column comparable with a reader-A width.")
    out.append("")
    out.append(f"  {'level':>5} {'texel':>6} {'sigmaRMS':>9} {'sigmaHWHM':>10} {'ratio':>7} "
               f"{'kurtosis':>9} {'maxdev':>7}")
    level = delta
    for n in range(1, LEVELS + 1):
        level = downsample(level)
        factor = 2 ** n
        psf = reconstruct(level, factor)
        # The reconstruction's grid is level-0 sized again; the delta sat at N/2, whose image is at
        # the same place to within half a level-`n` texel.
        centre = int(np.argmax(psf.sum(axis=1)))
        s, sh, k, dev = stats(psf, centre)
        out.append(f"  {n:5d} {factor:6d} {s:9.3f} {sh:10.3f} {s / sh:7.3f} {k:9.3f} {dev:7.4f}")
    out.append("")
    out.append("A Gaussian would read kurtosis 0.000 and ratio 1.000; a box would read -1.2.")
    out.append("`CHAIN_SIGMA_AT_LEVEL_1` = 1.2, the advisory constant `pyramid-plan.ts` inverts to")
    out.append("turn a sigma into a level, is to be read against the level-1 row above.")
    text = "\n".join(out)
    print(text)
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "chain-kernel.txt")
    open(path, "w").write(text + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
