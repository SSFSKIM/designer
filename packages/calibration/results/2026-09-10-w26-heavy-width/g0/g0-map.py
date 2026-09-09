"""W26 G0 deliverable 2 — the three candidates' mapping from the constant to a width.

WHAT THIS DOES. For every rung of `g0-ladder.sh` it puts two numbers side by side:

  * the PREDICTED Gaussian-equivalent width, simulated exactly — the chain level the CPU chose,
    reconstructed the way `textureSampleLevel` reconstructs it, convolved with the discrete 9 x 9
    grid the optics pass actually integrates (one tap-level texel apart, renormalised), reduced by
    half maximum, which is the statistic W25 G0's reader A reduces its two-component kernel by;
  * the READ width, W25 G0's reader A on the rung's own captures, per impulse row and per scale.

The ratio of the two is the mapping's claim, and the acceptance is 10 %. The thin rows' OKLab ΔE
against the inert-default rung is read from the rungs' own scratch matrices beside it, because X5
stops a ladder whose thin cells move by more than 0.001.

Writes `mapping.txt`. Nothing else is written; the canonical matrix and captures are never opened.
"""

import importlib.util
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
SCRATCH = "/Users/new/.claude/jobs/5c70e47f/tmp/w26/g0"

_spec = importlib.util.spec_from_file_location("w26chain", os.path.join(HERE, "g0-chain.py"))
CHAIN = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(CHAIN)

# `pyramid-plan.ts`'s `CHAIN_LEVEL_SIGMA`, and `CHAIN_SIGMA_AT_LEVEL_1` for `bodyChainLod`.
LEVEL_SIGMA = [0.0, 1.542, 3.281, 6.679, 13.418, 26.867]
CHAIN_SIGMA_AT_LEVEL_1 = 1.2
BODY_CHAIN_LOD = 1.0 + math.log2(1.25 / CHAIN_SIGMA_AT_LEVEL_1)
# The gain law, resolved per scale and per span exactly as `renderer.ts` and the optics pass do:
# `rampAtScale` between the 1x and 2x anchors, then the span grading toward the far anchor between
# `sizeSpanMax` and `sizeScatterSpanMax` (W15 G1's re-form, claims §5.70 §4).
GAIN_1X, GAIN_2X, GAIN_FAR_2X = 8.0, 4.8, 9.9
SPAN_MAX, SCATTER_SPAN_MAX = 96.0, 256.0
SPANS = {"impulse__rrect-md__rest": 96.0, "impulse__rrect-ml__rest": 128.0,
         "impulse__rrect-lg__rest": 160.0}


def ramp_at_scale(one, two, dpr):
    t = min(max(dpr - 1.0, 0.0), 1.0)
    return one + (two - one) * t


def gain_eff(span, scale):
    near = ramp_at_scale(GAIN_1X, GAIN_2X, scale)
    far = ramp_at_scale(GAIN_1X, GAIN_FAR_2X, scale)
    t = min(max((span - SPAN_MAX) / (SCATTER_SPAN_MAX - SPAN_MAX), 0.0), 1.0)
    return near + (far - near) * t * t * (3.0 - 2.0 * t)

IMPULSE = ["impulse__rrect-md__rest", "impulse__rrect-ml__rest", "impulse__rrect-lg__rest"]
# X5's rows: every ladder row whose span is at or under 44 CSS px.
THIN = ["impulse__rrect-sm__rest", "checkerboard-32__rrect-sm__rest",
        "checkerboard-64__rrect-sm__rest", "checkerboard__rrect-sm__rest",
        "photo__rrect-sm__rest", "light-solid__rrect-sm__rest",
        "checkerboard-4__capsule-button__rest", "checkerboard-32__capsule-button__rest",
        "checkerboard-64__capsule-button__rest"]

# The plan each scale's backdrop raster produces: level count, and `maxLod` = levelCount - 1.
PLANS = {1.0: (320, 200), 2.0: (640, 400)}


def plan_levels(width, height, min_extent=8):
    levels = [(width, height)]
    while True:
        w, h = levels[-1]
        nxt = (max(1, w >> 1), max(1, h >> 1))
        if min(nxt) < min_extent or nxt == (w, h):
            break
        levels.append(nxt)
    return levels


def max_lod(scale):
    return len(plan_levels(*PLANS[scale])) - 1


def chain_level_sigma(level):
    if level <= 0:
        return 0.0
    if level < len(LEVEL_SIGMA):
        return LEVEL_SIGMA[level]
    return LEVEL_SIGMA[-1] * math.pow(2.0, level - (len(LEVEL_SIGMA) - 1))


def heavy_tap_plan(sigma_texels, levels):
    """`pyramid-plan.ts`'s `heavyTapPlan`, restated."""
    level = 0
    if sigma_texels > 0:
        for i in range(1, levels):
            if chain_level_sigma(i) > sigma_texels:
                break
            level = i
    scale = 2 ** level
    covered = chain_level_sigma(level)
    residual = math.sqrt(max(sigma_texels ** 2 - covered ** 2, 0.0)) / scale
    return level, residual


# ------------------------------------------------------------------ the simulated prediction

_PSF_CACHE = {}


def level_psf(level, n=1024):
    """The chain's level-`level` point spread, reconstructed onto the level-0 grid."""
    if level in _PSF_CACHE:
        return _PSF_CACHE[level]
    img = np.zeros((n, n))
    img[n // 2, n // 2] = 1.0
    for _ in range(level):
        img = CHAIN.downsample(img)
    psf = CHAIN.reconstruct(img, 2 ** level) if level > 0 else img
    _PSF_CACHE[level] = psf
    return psf


def hwhm_sigma(line):
    line = np.asarray(line, dtype=np.float64)
    peak = float(line.max())
    if peak <= 0:
        return float("nan")
    idx = np.nonzero(line >= peak / 2.0)[0]
    lo, hi = int(idx[0]), int(idx[-1])

    def cross(a, b):
        if line[a] == line[b]:
            return float(a)
        return a + (line[a] - peak / 2.0) / (line[a] - line[b])

    left = cross(lo, lo - 1) if lo > 0 else float(lo)
    right = cross(hi, hi + 1) if hi + 1 < line.size else float(hi)
    return ((right - left) / 2.0) / math.sqrt(2.0 * math.log(2.0))


def predict_gaussian_tap(sigma_dev, scale):
    """Candidate (ii)'s delivered width: the chosen level, convolved with the 9 x 9 grid."""
    levels = len(plan_levels(*PLANS[scale]))
    level, residual = heavy_tap_plan(sigma_dev, levels)
    psf = level_psf(level)
    step = 2 ** level
    row = int(np.argmax(psf.sum(axis=1)))
    line = psf[row, :]
    acc = np.zeros_like(line)
    wsum = 0.0
    for k in range(-4, 5):
        w = math.exp(-0.5 * (k / max(residual, 1e-4)) ** 2)
        acc += w * np.roll(line, k * step)
        wsum += w
    # The grid is square, so the horizontal profile of the 2D result is the horizontal profile of
    # the level convolved with the 1D comb — the vertical taps only redistribute rows.
    return hwhm_sigma(acc / wsum), level, residual


def predict_level(lod, scale):
    """Candidate (i)'s and (iii)'s delivered width: a level, or a blend of two, no grid."""
    top = max_lod(scale)
    lod = min(max(lod, 0.0), top)
    lo = int(math.floor(lod))
    hi = min(lo + 1, top)
    frac = lod - lo
    a, b = level_psf(lo), level_psf(hi)
    psf = (1 - frac) * a + frac * b
    row = int(np.argmax(psf.sum(axis=1)))
    return hwhm_sigma(psf[row, :]), lod


def blend_psf(lod):
    lo = int(math.floor(lod))
    frac = lod - lo
    a = level_psf(lo)
    return a if frac <= 1e-9 else (1 - frac) * a + frac * level_psf(lo + 1)


def scatter_lod(span, scale, offset=0.0):
    """`clamp(bodyChainLod + log2(gainEff) + offset, 0, chainMaxLod)` — the pass's own arithmetic."""
    return min(max(BODY_CHAIN_LOD + math.log2(gain_eff(span, scale)) + offset, 0.0), max_lod(scale))


def predict_share(span, share, scale):
    """Candidate (iii): the tap at `scatterLod` mixed toward the tap one level above it."""
    base = scatter_lod(span, scale)
    second = min(base + 1.0, max_lod(scale))
    if abs(second - base) < 1e-9:
        return hwhm_sigma(blend_psf(base)[int(np.argmax(blend_psf(base).sum(axis=1))), :])
    psf = (1 - share) * blend_psf(base) + share * blend_psf(second)
    return hwhm_sigma(psf[int(np.argmax(psf.sum(axis=1))), :])


# ------------------------------------------------------------------ the reads

def read_widths(rung):
    path = os.path.join(SCRATCH, rung, f"read-{rung}.json")
    if not os.path.exists(path):
        return {}
    out = {}
    for w in json.load(open(path))["widths"]:
        if w["reader"] == "A" and w["src"] == "web":
            out[(w["profile"], w["scene"])] = w
    return out


def delta_e(rung):
    path = os.path.join(SCRATCH, rung, "rung.json")
    if not os.path.exists(path):
        return {}
    out = {}
    for cell in json.load(open(path))["cells"]:
        if cell["tier"] != "texture":
            continue
        entry = (cell.get("perceptual") or {}).get("oklabDeltaEMean")
        value = entry.get("value") if isinstance(entry, dict) else entry
        if value is None:
            continue
        out[(cell["key"]["profileKey"], cell["key"]["sceneId"])] = float(value)
    return out


def byte_split(rung, base="r0b"):
    """How many of a rung's captures reproduce the inert default's bytes, per scale."""
    import hashlib
    same = {"1x": 0, "2x": 0}
    diff = {"1x": 0, "2x": 0}
    for pkey, tag in (("apple-macos-26.5-1x-light-standard", "1x"),
                      ("apple-macos-26.5-2x-light-standard", "2x")):
        root = os.path.join(SCRATCH, rung, "web-captures", pkey)
        if not os.path.isdir(root):
            continue
        for scene in sorted(os.listdir(root)):
            a = os.path.join(SCRATCH, base, "web-captures", pkey, scene, f"{scene}__webgpu.png")
            b = os.path.join(root, scene, f"{scene}__webgpu.png")
            if not (os.path.exists(a) and os.path.exists(b)):
                continue
            da = hashlib.sha1(open(a, "rb").read()).digest()
            db = hashlib.sha1(open(b, "rb").read()).digest()
            (same if da == db else diff)[tag] += 1
    return same, diff


def thin_move(base, rung):
    """The worst thin-row ΔE move against the inert default, and where it is."""
    worst, where = 0.0, None
    for key, value in rung.items():
        if key[1] not in THIN or key not in base:
            continue
        d = abs(value - base[key])
        if d > worst:
            worst, where = d, key
    return worst, where


def main():
    out = []
    e = out.append
    e("W26 G0 deliverable 2 — the constant to a Gaussian-equivalent width, per candidate")
    e("=" * 100)
    e("")
    e("`predicted` is the simulation of what the renderer draws: the chain level the CPU chose,")
    e("reconstructed as `textureSampleLevel` reconstructs it, convolved with the discrete grid the")
    e("optics pass integrates, reduced by half maximum. `read` is W25 G0's reader A on the rung's")
    e("own captures, heavy component, DEVICE px. `ratio` is read / predicted.")
    e("")
    base = delta_e("r0b")
    baseline = read_widths("r0b")

    e("CANDIDATE (ii) — the Gaussian at the tap. Constant: `sizeHeavyTapSigma` in device px,")
    e("written to both scale anchors.")
    e("")
    e(f"  {'sigma':>6} {'scale':>5} {'lvl':>4} {'resid':>6} {'predicted':>10} "
      + " ".join(f"{s.split('__')[1]:>10}" for s in IMPULSE) + f" {'median':>8} {'ratio':>6}")
    tap_rungs = [(f"t{s}", float(s)) for s in (10, 13, 16, 19, 22, 25)]
    tap_curve = {1.0: [], 2.0: []}
    for rung, sigma in tap_rungs:
        rows = read_widths(rung)
        for pkey, scale in (("1x-light", 1.0), ("2x-light", 2.0)):
            pred, level, resid = predict_gaussian_tap(sigma, scale)
            reads = [rows.get((pkey, s), {}).get("heavyDev") for s in IMPULSE]
            got = [r for r in reads if r is not None]
            med = float(np.median(got)) if got else float("nan")
            tap_curve[scale].append((sigma, med))
            # Reader A parameterises the heavy component as sharp + delta with delta <= 60 * scale,
            # so a row at 60 * scale + sharp is the READER at its bound and not a width.
            pinned = sum(1 for r in reads if r is not None and r > 59.0 * scale)
            e(f"  {sigma:6.1f} {pkey[:2]:>5} {level:4d} {resid:6.3f} {pred:10.3f} "
              + " ".join(f"{(r if r is not None else float('nan')):10.3f}" for r in reads)
              + f" {med:8.3f} {med / pred:6.3f}"
              + ("" if pinned == 0 else f"   {pinned} row(s) AT THE READER'S BOUND"))
    e("")
    for scale in (1.0, 2.0):
        seq = [m for _, m in tap_curve[scale]]
        rising = all(b >= a - 1e-9 for a, b in zip(seq, seq[1:]))
        e(f"  monotone at {int(scale)}x: {rising}   ({', '.join(f'{v:.2f}' for v in seq)})")
    e("")
    e("  The 1x column stops being a reading of the material at about 17 device px. Reader A's")
    e("  window on `impulse` is half the dot pitch — 30 CSS px, which is 30 device px at 1x and 60")
    e("  at 2x — and its own delta bound is 60 * scale. The DRAWN kernel is the same in device px")
    e("  at both scales at the same σ (the same plan, the same level, the same residual, because")
    e("  `bodySigmaCssFor` divides by the ratio and the raster's texels per CSS px multiplies it")
    e("  back), so the two columns disagreeing IS the instrument: at 2x the reader follows the")
    e("  constant monotonically over the whole 10–25 range at ratio 1.11–1.13 up to 16, and at 1x")
    e("  it saturates at its bound. This is a limit of reader A on a 64 CSS px dot pitch, not of")
    e("  the tap, and it is what clause 1's ladder has to be read through.")
    e("")

    e("CANDIDATE (i) — the fractional pyramid level. Constant: `sizeHeavyLevelOffset`.")
    e(f"  `chainMaxLod` is {max_lod(1.0)} at 1x and {max_lod(2.0)} at 2x; the gain the level is")
    e("  measured from is 8 at dpr 1 and 4.8 rising to 9.9 with the span at dpr 2, so the level the")
    e("  pass draws is per row. `drawn` and `predicted` are quoted for `rrect-md`.")
    e("")
    e(f"  {'offset':>7} {'scale':>5} {'drawn':>7} {'predicted':>10} "
      + " ".join(f"{s.split('__')[1]:>10}" for s in IMPULSE) + f" {'median':>8}")
    off_rungs = [("oM100", -1.0), ("oM050", -0.5), ("r0b", 0.0), ("oP050", 0.5), ("oP100", 1.0)]
    for rung, offset in off_rungs:
        rows = read_widths(rung)
        for pkey, scale in (("1x-light", 1.0), ("2x-light", 2.0)):
            drawn = scatter_lod(SPANS[IMPULSE[0]], scale, offset)
            pred, _ = predict_level(drawn, scale)
            reads = [rows.get((pkey, s), {}).get("heavyDev") for s in IMPULSE]
            got = [r for r in reads if r is not None]
            med = float(np.median(got)) if got else float("nan")
            e(f"  {offset:7.2f} {pkey[:2]:>5} {drawn:7.4f} {pred:10.3f} "
              + " ".join(f"{(r if r is not None else float('nan')):10.3f}" for r in reads)
              + f" {med:8.3f}")
    e("")

    e("CANDIDATE (iii) — the second chain level's share. Constant: `sizeHeavySecondShare`.")
    e("  `predicted` is quoted for `rrect-md`, whose own `scatterLod` the share mixes from.")
    e("")
    e(f"  {'share':>6} {'scale':>5} {'predicted':>10} "
      + " ".join(f"{s.split('__')[1]:>10}" for s in IMPULSE) + f" {'median':>8}")
    share_rungs = [("r0b", 0.0), ("s025", 0.25), ("s050", 0.5), ("s100", 1.0)]
    for rung, share in share_rungs:
        rows = read_widths(rung)
        for pkey, scale in (("1x-light", 1.0), ("2x-light", 2.0)):
            pred = predict_share(SPANS[IMPULSE[0]], share, scale)
            reads = [rows.get((pkey, s), {}).get("heavyDev") for s in IMPULSE]
            got = [r for r in reads if r is not None]
            med = float(np.median(got)) if got else float("nan")
            e(f"  {share:6.2f} {pkey[:2]:>5} {pred:10.3f} "
              + " ".join(f"{(r if r is not None else float('nan')):10.3f}" for r in reads)
              + f" {med:8.3f}")
    e("")
    e("BYTE IDENTITY, which is the sharpest statement of what (i) and (iii) can reach. Against the")
    e("inert-default rung, over the 18 ladder rows per profile, GPU tier:")
    for rung, label in (("oP050", "level offset +0.5"), ("oP100", "level offset +1.0"),
                        ("s025", "second share 0.25"), ("s050", "second share 0.50"),
                        ("s100", "second share 1.00")):
        same, diff = byte_split(rung)
        e(f"  {label:22} 1x: {same['1x']:2d} identical / {diff['1x']:2d} differ    "
          f"2x: {same['2x']:2d} identical / {diff['2x']:2d} differ")
    e("")
    e("  Every 1x row is byte-identical at every value of both constants and every 2x row differs.")
    e("  That is the clamp: at dpr 1 `scatterLod` is already `chainMaxLod`, so a positive offset")
    e("  lands on the same level and the second tap IS the first tap, and the two mechanisms are")
    e("  not approximately inert at 1x — they are inert to the bit.")
    e("")

    e("X5 — the thin rows (span <= 44), OKLab ΔE mean against the inert-default rung, worst move")
    e("per rung. More than 0.001 stops the ladder.")
    e("")
    e(f"  {'rung':>8} {'worst':>9} {'where':>60}")
    for rung, _ in tap_rungs + off_rungs + share_rungs:
        if rung == "r0b":
            continue
        worst, where = thin_move(base, delta_e(rung))
        label = "-" if where is None else f"{where[0][-16:]} {where[1]}"
        e(f"  {rung:>8} {worst:9.5f} {label:>60}")
    e("")
    e("  The sharp component beside it, so a rung that moved the wrong half is visible:")
    e(f"  {'rung':>8} {'scale':>5} " + " ".join(f"{s.split('__')[1]:>10}" for s in IMPULSE))
    for rung, _ in tap_rungs + off_rungs + share_rungs:
        rows = read_widths(rung)
        for pkey in ("1x-light", "2x-light"):
            reads = [rows.get((pkey, s), {}).get("sharpDev") for s in IMPULSE]
            e(f"  {rung:>8} {pkey[:2]:>5} "
              + " ".join(f"{(r if r is not None else float('nan')):10.3f}" for r in reads))

    text = "\n".join(out)
    print(text)
    open(os.path.join(HERE, "mapping.txt"), "w").write(text + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
