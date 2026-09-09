"""W26 G0 deliverable 1 — how the heavy sample is taken today, measured.

Reads the five gain rungs `g0-rung.sh` captured at dpr 1 (`sizeScatterGainMax` 4 / 8 / 10.3 / 16 /
32, everything else the 0.14.0 material) through W25 G0's reader A, and states beside them the
arithmetic the renderer actually performs: `bodyChainLod`, the level `log2(gain)` asks for, and the
level `clamp(..., 0, chainMaxLod)` delivers. The chain's own kernel per level comes from
`chain-kernel.txt`, which simulates `WGSL_DOWNSAMPLE_PASS` exactly.

Writes `tap-today.txt`. Nothing else is written.
"""

import json
import math
import os
import sys

RUNGS = [("gain4", 4.0), ("gain8", 8.0), ("gain103", 10.3), ("gain16", 16.0), ("gain32", 32.0)]
SCRATCH = "/Users/new/.claude/jobs/5c70e47f/tmp/w26/g0"
SCENES = ["impulse__rrect-md__rest", "impulse__rrect-ml__rest", "impulse__rrect-lg__rest"]

# The bed's own numbers, restated here so the table is readable without opening four files.
BLUR_SIGMA_DEV = 1.25          # `optics.regular.blurSigma`, a DEVICE-px quantity (W12 G3)
CHAIN_SIGMA_AT_LEVEL_1 = 1.2   # `pyramid-plan.ts`, advisory
# `chain-kernel.txt`'s measured second-moment sigmas, divided by the shape's constant ratio of
# second-moment to half-maximum sigma (1.018) — `pyramid-plan.ts`'s `CHAIN_LEVEL_SIGMA`.
LEVEL_SIGMA = [0.0, 1.542, 3.281, 6.679, 13.418, 26.867]
CANVAS = (320, 200)


def chain_lod_for_sigma(sigma_texels):
    if sigma_texels <= 0:
        return 0.0
    if sigma_texels <= CHAIN_SIGMA_AT_LEVEL_1:
        return sigma_texels / CHAIN_SIGMA_AT_LEVEL_1
    return 1.0 + math.log2(sigma_texels / CHAIN_SIGMA_AT_LEVEL_1)


def plan_levels(width, height, min_extent=8):
    levels = [(width, height)]
    while True:
        w, h = levels[-1]
        nxt = (max(1, w >> 1), max(1, h >> 1))
        if min(nxt) < min_extent or nxt == (w, h):
            break
        levels.append(nxt)
    return levels


def level_sigma(lod):
    """The chain's measured half-maximum sigma at a continuous level, in level-0 texels."""
    if lod <= 0:
        return 0.0
    lo = int(math.floor(lod))
    hi = min(lo + 1, len(LEVEL_SIGMA) - 1)
    a, b = LEVEL_SIGMA[min(lo, len(LEVEL_SIGMA) - 1)], LEVEL_SIGMA[hi]
    if a <= 0:
        return b * lod
    # Trilinear between two mips is linear in the SAMPLES, which for a self-similar kernel reads
    # as geometric interpolation between the two widths; that is what the renders confirm.
    return a * math.pow(b / a, lod - lo)


def read(rung):
    path = os.path.join(SCRATCH, rung, f"read-{rung}.json")
    return json.load(open(path))["widths"]


def main():
    out = []
    e = out.append
    e("W26 G0 deliverable 1 — how the heavy sample is taken today")
    e("=" * 100)
    e("")
    e("THE ARITHMETIC. `wgsl/optics.ts` takes the body's deep sample as")
    e("")
    e("    gainEff    = size.x + (shadowSize.w - size.x) * farS      (one number at dpr 1)")
    e("    scatterLod = clamp(size.w + log2(gainEff), 0, lens.w)")
    e("")
    e("`size.w` is `bodyChainLod` = `chainLodForSigma(bodySigmaTexels)` and `lens.w` is the")
    e("pyramid plan's `maxLod`. On the bed at dpr 1:")
    e("")
    sigma_css = BLUR_SIGMA_DEV / 1.0
    sigma_texels = sigma_css * 1.0
    body_lod = chain_lod_for_sigma(sigma_texels)
    levels = plan_levels(*CANVAS)
    e(f"  blurSigma              {BLUR_SIGMA_DEV} device px, and `bodySigmaCssFor` divides by the")
    e(f"                         ratio, so {sigma_css:.4f} CSS px at dpr 1")
    e(f"  texels per CSS px      1.0 — the backdrop raster is {CANVAS[0]}x{CANVAS[1]} for a")
    e(f"                         {CANVAS[0]}x{CANVAS[1]} CSS canvas, and the plan does not downscale it")
    e(f"  bodySigmaTexels        {sigma_texels:.4f}")
    e(f"  bodyChainLod           {body_lod:.4f}   (= 1 + log2(sigma / {CHAIN_SIGMA_AT_LEVEL_1}))")
    e(f"  the chain              {len(levels)} levels " + " -> ".join(f"{w}x{h}" for w, h in levels))
    e(f"                         the next would be {levels[-1][0] // 2}x{levels[-1][1] // 2}, whose")
    e(f"                         shorter side is under MIN_LEVEL_EXTENT = 8, so the chain stops")
    e(f"  chainMaxLod            {len(levels) - 1}")
    e("")
    e(f"  {'gain':>6} {'log2(gain)':>11} {'asked lod':>10} {'drawn lod':>10} {'clamped':>8} "
      f"{'level sigma':>12}")
    for _, gain in RUNGS:
        asked = body_lod + math.log2(gain)
        drawn = min(max(asked, 0.0), len(levels) - 1)
        e(f"  {gain:6.1f} {math.log2(gain):11.4f} {asked:10.4f} {drawn:10.4f} "
          f"{str(asked > drawn + 1e-9):>8} {level_sigma(drawn):12.3f}")
    e("")
    e("  `level sigma` is the chain's OWN kernel at the drawn level, in level-0 texels (= device")
    e("  px here), by half maximum, from `chain-kernel.txt`'s exact simulation of the 13-tap")
    e("  downsample. It is not a Gaussian: kurtosis -0.23 at every level from 2 on, and the worst")
    e("  deviation from the best-fitting Gaussian is 12% of the peak. Level n's width is")
    e(f"  {LEVEL_SIGMA[1:]} at levels 1..5, NOT the advisory")
    e(f"  CHAIN_SIGMA_AT_LEVEL_1 = {CHAIN_SIGMA_AT_LEVEL_1} the plan inverts, which under-states level 1 by 24%.")
    e("")
    e("THE READING. W25 G0's reader A on the three impulse rows at dpr 1, light standard.")
    e("Sigmas in DEVICE px; `native` is the reference fixture and is the same at every rung.")
    e("")
    e(f"  {'scene':28} {'gain':>6} {'src':>7} {'sharp':>7} {'heavy':>8} {'share':>6} {'sigmaEq':>8}")
    native_done = set()
    for rung, gain in RUNGS:
        rows = {(w["scene"], w["src"]): w for w in read(rung)
                if w["reader"] == "A" and w["profile"] == "1x-light"}
        for scene in SCENES:
            n = rows.get((scene, "native"))
            if n is not None and scene not in native_done:
                e(f"  {scene:28} {'-':>6} {'native':>7} {n['sharpDev']:7.3f} "
                  f"{n['heavyDev']:8.3f} {n['heavyShare']:6.3f} {n['sigmaDev']:8.3f}")
                native_done.add(scene)
        for scene in SCENES:
            w = rows.get((scene, "web"))
            if w is None:
                continue
            e(f"  {scene:28} {gain:6.1f} {'web':>7} {w['sharpDev']:7.3f} {w['heavyDev']:8.3f} "
              f"{w['heavyShare']:6.3f} {w['sigmaDev']:8.3f}")
        e("")
    e("WHY THE WIDTH SATURATES. `bodyChainLod + log2(8)` is "
      f"{body_lod + 3:.4f} and `chainMaxLod` is {len(levels) - 1}, so the")
    e("clamp has been holding since the material was fitted: gains 8, 10.3, 16 and 32 all draw")
    e("level 4 and the three rows read the same three widths at every one of them, to the")
    e("last digit. Gain 4 asks for level 3.06, which the chain has, and it is the ONLY rung")
    e("that moves. The cause is not the material and not the reader: it is that")
    e("`planPyramid` stops the chain when the shorter side would fall below MIN_LEVEL_EXTENT,")
    e("so a 320x200 backdrop has no level above 4, and the pyramid's widths are octaves — the")
    e("gain can only ask for a level that exists.")
    text = "\n".join(out)
    print(text)
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tap-today.txt")
    open(path, "w").write(text + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
