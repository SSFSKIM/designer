"""W26 G1b — vitrea's OWN kernel at the 0.14.0 material, derived from the arithmetic that draws it.

WHY THIS EXISTS. A reader that has not been shown a kernel it already knows has nothing to say
about one it does not. This module states, exactly, what `wgsl/optics.ts` convolves the backdrop
with at a given surface, scale and depth on the frozen bed, so `g1b-control.py` can hold reader E's
answer against it rather than against another reader.

THE COMPOSITE, from `wgsl/optics.ts` verbatim:

    backdrop = mix(bodySample, scatterSample, kScatter)

`bodySample` is the level-0 backdrop blurred separably by `blurSigma` — a Gaussian of 1.25 device
px at both scales, since `bodySigmaCssFor` divides by the ratio and the raster multiplies it back.
`scatterSample` is `textureSampleLevel(backdropChain, uv, scatterLod)`, whose point spread is the
13-tap chain's own level kernel, reconstructed onto the level-0 grid, trilinearly blended between
the two neighbouring integer levels where `scatterLod` is fractional. It is NOT a Gaussian: W26 G0
measured kurtosis −0.23 and a worst deviation of 12 % of the peak from the best-fitting Gaussian at
every level from 2 up.

    scatterLod = clamp(bodyChainLod + log2(gainEff), 0, chainMaxLod)

with `bodyChainLod` = 1 + log2(1.25 / 1.2) = 1.0589 and `chainMaxLod` the pyramid's last level: 4
on the 1x 320 × 200 raster and 5 on the 2x 640 × 400 one, because `planPyramid` stops when the
shorter side would fall below `MIN_LEVEL_EXTENT` = 8. At 1x the clamp has been holding since the
material was fitted (W26 G0, claims §5.116 §2), so every 1x row draws level 4 exactly.

    kScatter = kDeep − max(rampStart − (1 − kDeep), 0) · max(1 − depth / rampReach, 0)

`kDeep` is the span curve — floor + (1 − floor) · smoothstep(sizeSpanMin, sizeScatterSpanMax, span)
— and the floor is 0.4 at 1x and 1 at 2x, so at dpr 2 the deep interior is PURELY the chain tap and
the control there has no share to be wrong about. `rampReach` is 80 device px at 1x and 100 at 2x,
divided by the ratio before it reaches the shader, so it is 80 and 50 CSS px: at 1x the ramp does
not run out inside `rrect-md` at all. That is why reader E reads in bands of depth and why every
control states the band's own spread of `kScatter`.
"""

import importlib.util
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
G0 = os.path.abspath(os.path.join(HERE, "..", "g0"))
_spec = importlib.util.spec_from_file_location("w26chain", os.path.join(G0, "g0-chain.py"))
CHAIN = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(CHAIN)

sys.path.insert(0, HERE)
import w26blib as E  # noqa: E402

# The resolved light-standard material, dumped by `resolve.mjs` from `withMaterialOverrides` over
# the committed profile document. Every constant below is read from it rather than transcribed.
MATERIAL_JSON = os.environ.get(
    "W26_MATERIAL_JSON", "/Users/new/.claude/jobs/5c70e47f/tmp/w26/g1b/material.json")
# Transcribed fallback (the committed 1x light patch), used only where the dump is unavailable.
FALLBACK = {
    "blurSigma": 1.25, "sizeSpanMin": 32.0, "sizeSpanMax": 96.0,
    "sizeScatterSpanMax": 256.0, "sizeScatterGainMax": 8.0, "sizeScatterGainMax2x": 4.8,
    "sizeScatterGainFar2x": 9.9, "sizeScatterFloor": 0.4, "sizeScatterFloor2x": 1.0,
    "sizeScatterRampStartThin1x": 0.72, "sizeScatterRampStartThick1x": 0.52,
    "sizeScatterRampStartFar1x": 0.2, "sizeScatterRampStartThin2x": 0.46,
    "sizeScatterRampStartThick2x": 0.21, "sizeScatterRampStartFar2x": 0.21,
    "sizeScatterRampReach1xPx": 80.0, "sizeScatterRampReach2xPx": 100.0,
    "sizeScatterHeavyShareThick1x": 0.0, "sizeScatterHeavyShareThick2x": 0.0,
}
CHAIN_SIGMA_AT_LEVEL_1 = 1.2
PLANS = {1.0: (320, 200), 2.0: (640, 400)}
SPANS = {"rrect-sm": 32.0, "rrect-md": 96.0, "rrect-ml": 128.0, "rrect-lg": 160.0}


def material(profile="apple-macos-26.5-1x-light-standard"):
    if os.path.exists(MATERIAL_JSON):
        try:
            return json.load(open(MATERIAL_JSON))[profile]
        except Exception:
            pass
    return dict(FALLBACK)


def ramp_at_scale(one, two, dpr):
    t = min(max(dpr - 1.0, 0.0), 1.0)
    return one + (two - one) * t


def smoothstep(t):
    t = min(max(t, 0.0), 1.0)
    return t * t * (3.0 - 2.0 * t)


def max_lod(scale):
    w, h = PLANS[scale]
    n = 0
    while min(w >> 1, h >> 1) >= 8:
        w, h = w >> 1, h >> 1
        n += 1
    return n


def scatter_lod(span, scale, m):
    body = 1.0 + math.log2(m["blurSigma"] / CHAIN_SIGMA_AT_LEVEL_1)
    near = ramp_at_scale(m["sizeScatterGainMax"], m["sizeScatterGainMax2x"], scale)
    far = ramp_at_scale(m["sizeScatterGainMax"], m["sizeScatterGainFar2x"], scale)
    far_s = smoothstep((span - m["sizeSpanMax"]) / (m["sizeScatterSpanMax"] - m["sizeSpanMax"]))
    gain = near + (far - near) * far_s
    return min(max(body + math.log2(max(gain, 1e-4)), 0.0), float(max_lod(scale)))


def k_scatter(span, scale, depth_css, m):
    """`kScatter` at one depth, in the shader's own arithmetic. `depth_css` is CSS px inside."""
    floor = ramp_at_scale(m["sizeScatterFloor"], m["sizeScatterFloor2x"], scale)
    deep_t = smoothstep((span - m["sizeSpanMin"]) / (m["sizeScatterSpanMax"] - m["sizeSpanMin"]))
    thick = smoothstep((span - m["sizeSpanMin"]) / (m["sizeSpanMax"] - m["sizeSpanMin"]))
    lift = ramp_at_scale(m["sizeScatterHeavyShareThick1x"], m["sizeScatterHeavyShareThick2x"],
                         scale)
    k_deep = min(max(floor + (1.0 - floor) * deep_t + lift * thick, 0.0), 1.0)
    s_deep = 1.0 - k_deep
    far_s = smoothstep((span - m["sizeSpanMax"]) / (m["sizeScatterSpanMax"] - m["sizeSpanMax"]))
    thin = ramp_at_scale(m["sizeScatterRampStartThin1x"], m["sizeScatterRampStartThin2x"], scale)
    thk = ramp_at_scale(m["sizeScatterRampStartThick1x"], m["sizeScatterRampStartThick2x"], scale)
    farv = ramp_at_scale(m["sizeScatterRampStartFar1x"], m["sizeScatterRampStartFar2x"], scale)
    ramp_start = thin + (thk - thin) * thick + (farv - thk) * far_s
    reach_dev = ramp_at_scale(m["sizeScatterRampReach1xPx"], m["sizeScatterRampReach2xPx"], scale)
    reach_css = reach_dev / scale
    ramp_t = max(1.0 - max(depth_css, 0.0) / max(reach_css, 1e-6), 0.0)
    sharp = min(max(s_deep + max(ramp_start - s_deep, 0.0) * ramp_t, 0.0), 1.0)
    return 1.0 - sharp


_LEVEL = {}


def level_psf(level, n=1024):
    if level in _LEVEL:
        return _LEVEL[level]
    img = np.zeros((n, n))
    img[n // 2, n // 2] = 1.0
    for _ in range(level):
        img = CHAIN.downsample(img)
    psf = CHAIN.reconstruct(img, 2 ** level) if level > 0 else img
    r = int(np.argmax(psf.sum(axis=1)))
    c = int(np.argmax(psf.sum(axis=0)))
    half = 200
    _LEVEL[level] = psf[r - half:r + half + 1, c - half:c + half + 1]
    return _LEVEL[level]


def chain_profile(level, nodes):
    """The chain's level kernel as a radial profile on reader E's own nodes."""
    return E.radial_profile_of_kernel2d(level_psf(level), nodes)


def truth_profile(span, scale, depths_css, nodes, m=None):
    """The kernel vitrea draws, averaged over a band of depths — the control's target.

    The average is over the band's pixels because that is what a single kernel fitted on the band
    can possibly be: `kScatter` varies with depth by construction, so the band's own spread is
    returned beside the profile and is what a 10 % acceptance has to be read against.
    """
    m = m or material()
    lod = scatter_lod(span, scale, m)
    lo = int(math.floor(lod))
    frac = lod - lo
    heavy = chain_profile(lo, nodes)
    if frac > 1e-9:
        heavy = (1 - frac) * heavy + frac * chain_profile(lo + 1, nodes)
    sharp = E.gauss_profile(nodes, m["blurSigma"])
    ks = np.array([k_scatter(span, scale, d, m) for d in np.atleast_1d(depths_css)])
    kbar = float(ks.mean())
    prof = (1 - kbar) * sharp + kbar * heavy
    return {"c": prof, "kMean": kbar, "kMin": float(ks.min()), "kMax": float(ks.max()),
            "lod": lod, "sharpSigma": m["blurSigma"]}


def main():
    m = material()
    nodes = E.radial_nodes(64.0, 40)
    lines = []
    e = lines.append
    e("W26 G1b — vitrea's own kernel at the 0.14.0 material, from the arithmetic that draws it")
    e("=" * 100)
    e("")
    e(f"  chainMaxLod: 1x {max_lod(1.0)}   2x {max_lod(2.0)}     blurSigma {m['blurSigma']}"
      f"   bodyChainLod {1 + math.log2(m['blurSigma'] / CHAIN_SIGMA_AT_LEVEL_1):.4f}")
    e("")
    e(f"  {'surface':>9} {'scale':>5} {'span':>5} {'scatterLod':>10} {'level sigma':>12}"
      f" {'kScatter @ depth (CSS px)':>44}")
    for comp in ("rrect-md", "rrect-lg"):
        span = SPANS[comp]
        for scale in (1.0, 2.0):
            lod = scatter_lod(span, scale, m)
            lo = int(math.floor(lod))
            frac = lod - lo
            ls = [0.0, 1.542, 3.281, 6.679, 13.418, 26.867]
            sig = (1 - frac) * ls[lo] + frac * ls[min(lo + 1, 5)]
            ks = "  ".join(f"{d:.0f}:{k_scatter(span, scale, d, m):.3f}"
                          for d in (8, 16, 24, 32, 48, 80))
            e(f"  {comp:>9} {scale:5.0f} {span:5.0f} {lod:10.4f} {sig:12.3f}  {ks}")
    e("")
    e("`level sigma` is the linear blend of the two neighbouring chain levels' half-maximum sigmas")
    e("in level-0 texels (= device px), quoted for orientation only: the control's target is the")
    e("blended PSF itself, not a sigma of it.")
    e("")
    e("The truth kernel on each control band, reduced by reader E's own statistics:")
    e("")
    e(f"  {'surface':>9} {'scale':>5} {'band CSS':>10} {'kScatter':>18} {'sigmaHWHM':>10}"
      f" {'sigmaRMS':>9} {'sigmaMTF':>9} {'MTF-fit':>8}")
    for comp in ("rrect-md", "rrect-lg"):
        span = SPANS[comp]
        for scale in (1.0, 2.0):
            for band in ((16.0, 24.0), (24.0, 40.0), (16.0, span / 2)):
                depths = np.linspace(band[0], min(band[1], span / 2), 33)
                t = truth_profile(span, scale, depths, nodes, m)
                w = E.widths_of_profile(nodes, t["c"])
                s, rel, *_ = E.sigma_matching_mtf(nodes, t["c"])
                e(f"  {comp:>9} {scale:5.0f} {band[0]:4.0f}-{band[1]:<5.0f}"
                  f" {t['kMean']:.3f} [{t['kMin']:.3f},{t['kMax']:.3f}]"
                  f" {w['sigmaHwhm']:10.3f} {w['sigmaRms']:9.3f} {s:9.3f} {rel * 100:7.2f}%")
    text = "\n".join(lines)
    print(text)
    open(os.path.join(HERE, "truth.txt"), "w").write(text + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
