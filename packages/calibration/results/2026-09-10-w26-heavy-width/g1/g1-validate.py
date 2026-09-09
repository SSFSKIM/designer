"""W26 G1 — reader D validated, before it is used to fit anything.

Two validations, in the order the parent's ruling states them (W26 Decision Log 2 (f), G1 (b)):

  1. **On synthetic kernels.** The impulse backdrop convolved with a known pair at a known share,
     scaled and offset the way a glass interior is, quantised to 8 bit the way a capture is, and
     read back. Including the chain's OWN kernel at level 4 — the platykurtic shape `chain-kernel.txt`
     simulated, which is neither a Gaussian nor a box — because that is what the renderer draws
     wherever the heavy width is left to the pyramid, and a two-Gaussian reader has to say something
     defensible about it.
  2. **Against reader A**, on the 2x rows where W26 G0 measured reader A monotone (σ 10 → 16). The
     acceptance is agreement within 10 %.

Nothing here is fitted and nothing is written outside this directory.

    g1-validate.py [--scratch DIR] [--ladder DIR]
"""

import argparse
import math
import os
import sys

import numpy as np
from scipy.ndimage import gaussian_filter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import w26lib as D  # noqa: E402
import w25lib as L  # noqa: E402

SCRATCH = "/Users/new/.claude/jobs/5c70e47f/tmp/w26/g1"
G0_SCRATCH = "/Users/new/.claude/jobs/5c70e47f/tmp/w26/g0"


def quantise(a):
    """The 8-bit step a capture is written through — through the sRGB OETF, which is where it is.

    A PNG is quantised in the ENCODED domain, so the step in the linear luma the readers work in is
    a function of the level: at the impulse fixtures' interior level of 0.45 one code is 0.0059 of
    linear luma, which is larger than the whole interior modulation the reader has to fit. Quantising
    linearly instead would flatter the reader by about a third.
    """
    return L.linearise(np.round(L.encode(np.clip(a, 0.0, 1.0)) * 255.0))


BODY = 0.4529   # the native 1x `impulse__rrect-lg` interior's own level
PEAK = 0.058    # and its own dot peak above that level


def synth(bg, s1, s2, share, body=BODY, peak=PEAK, quant=True):
    """One synthetic interior at the fixtures' own level and dot amplitude.

    Both matter: the reader's whole difficulty is that the signal is about one display code, so a
    synthetic at a comfortable contrast would validate an instrument that does not exist.
    """
    k = (1.0 - share) * gaussian_filter(bg, s1, mode="nearest") \
        + share * gaussian_filter(bg, s2, mode="nearest")
    gain = peak / max(float(k.max()), 1e-9)
    field = body + gain * k
    return quantise(field) if quant else field


def chain_level_psf(level, size=256):
    """The pyramid's own kernel at `level`, as a separable-free 2D array on the level-0 grid.

    `g0-chain.py`'s simulation, reduced to the one thing this file needs: the reconstructed point
    spread, so a synthetic tile can be convolved with what the renderer's chain actually draws
    rather than with a Gaussian standing in for it.
    """
    taps = [(0, 0, 0.125),
            (-1, 1, 0.125), (1, 1, 0.125), (-1, -1, 0.125), (1, -1, 0.125),
            (0, 2, 0.0625), (-2, 0, 0.0625), (2, 0, 0.0625), (0, -2, 0.0625),
            (-2, 2, 0.03125), (2, 2, 0.03125), (-2, -2, 0.03125), (2, -2, 0.03125)]

    def box2x2(a):
        return 0.25 * (a + np.roll(a, -1, 0) + np.roll(a, -1, 1)
                       + np.roll(np.roll(a, -1, 0), -1, 1))

    def downsample(src):
        base = box2x2(src)
        acc = np.zeros_like(src)
        for ox, oy, w in taps:
            acc += w * np.roll(np.roll(base, -oy, 0), -ox, 1)
        return acc[::2, ::2]

    def reconstruct(lv, factor):
        h, w = lv.shape
        coord = (np.arange(h * factor) + 0.5) / factor - 0.5
        i0 = np.clip(np.floor(coord).astype(int), 0, h - 1)
        i1 = np.clip(i0 + 1, 0, h - 1)
        t = coord - np.floor(coord)
        rows = (1 - t)[:, None] * lv[i0] + t[:, None] * lv[i1]
        j0 = np.clip(np.floor(coord).astype(int), 0, w - 1)
        j1 = np.clip(j0 + 1, 0, w - 1)
        tw = coord - np.floor(coord)
        return (1 - tw)[None, :] * rows[:, j0] + tw[None, :] * rows[:, j1]

    a = np.zeros((size, size))
    a[size // 2, size // 2] = 1.0
    for n in range(1, level + 1):
        a = downsample(a)
    return reconstruct(a, 2 ** level)


def convolve_psf(img, psf):
    """Circular convolution through the FFT — the backdrop lattice is periodic anyway."""
    ph, pw = psf.shape
    k = np.zeros_like(img)
    ih, iw = img.shape
    cy, cx = ph // 2, pw // 2
    for dy in range(-min(cy, ih // 2), min(ph - cy, ih // 2)):
        for dx in range(-min(cx, iw // 2), min(pw - cx, iw // 2)):
            k[dy % ih, dx % iw] += psf[cy + dy, cx + dx]
    k /= k.sum()
    return np.real(np.fft.ifft2(np.fft.fft2(img) * np.fft.fft2(k)))


ROWS = (("1x-light", 1.0, "rrect-lg"), ("1x-light", 1.0, "rrect-md"),
        ("2x-light", 2.0, "rrect-lg"), ("2x-light", 2.0, "rrect-md"))
# The pairs the fit has to tell apart, in device px at scale 1, with the share each carries.
CASES = [(2.0, 10.0, 0.25), (2.0, 13.42, 0.23), (3.0, 19.5, 0.47), (2.0, 11.3, 0.69),
         (2.5, 25.0, 0.40), (2.5, 30.0, 0.40)]


def contrast_of(profile, sid, scale, comps):
    """One row's own interior level and dot peak, so a synthetic is made at the fixture's own
    contrast rather than at a comfortable one."""
    native = L.native_path(profile, sid)
    if not os.path.exists(native):
        return None
    lum = L.luma_of(native)
    shape = (int(200 * scale), int(320 * scale))
    if lum.shape != shape:
        return None
    mask = L.Cell(sid.split("__")[1], comps).body_mask(scale, shape, 12.0)
    v = lum[mask]
    body = float(np.percentile(v, 5))
    return body, float(v.max() - body), float(np.std(v))


def heavy_codes(bg, s1, s2, share, body, peak):
    """The heavy component's own peak, in 8-bit display codes at the interior's level."""
    k = (1 - share) * gaussian_filter(bg, s1, mode="nearest") \
        + share * gaussian_filter(bg, s2, mode="nearest")
    gain = peak / max(float(k.max()), 1e-9)
    h = share * gaussian_filter(bg, s2, mode="nearest")
    return abs(L.codes(body + gain * float(h.max()), body))


def synthetic(out):
    comps = L.load_components()

    out.append("## 1. Reader D on the model it fits — exact, and that is the easy half")
    out.append("")
    out.append("The impulse backdrop convolved with a known pair at a known share, read over")
    out.append("`rrect-lg`'s eroded interior, with NO quantisation. If the fit or the model were")
    out.append("wrong this is where it would show.")
    out.append("")
    scale, shape = 1.0, (200, 320)
    bg = L.background_for("impulse", scale, shape)
    mask = L.Cell("rrect-lg", comps).body_mask(scale, shape, 12.0)
    out.append(f"  {'sigS in':>7} {'sigH in':>7} {'w in':>6} | {'sigS out':>8} {'sigH out':>8} "
               f"{'w out':>6} {'err %':>7}")
    for s1, s2, w in CASES:
        lum = synth(bg, s1, s2, w, quant=False)
        f = D.lattice_fit(lum, bg, mask, scale)
        out.append(f"  {s1:7.2f} {s2:7.2f} {w:6.2f} | {f['sharpSigmaDev']:8.2f} "
                   f"{f['heavySigmaDev']:8.2f} {f['heavyShare']:6.2f} "
                   f"{abs(f['heavySigmaDev'] - s2) / s2 * 100:7.2f}")
    out.append("")

    out.append("## 2. The same synthetics through the 8-bit step — the fixture's own limit")
    out.append("")
    out.append("Each row is made at that fixture's own interior level and dot peak, measured from")
    out.append("the native, and quantised through the sRGB OETF, which is where a PNG's")
    out.append("quantisation actually is.")
    out.append("")
    out.append(f"  {'row':>18} {'body':>7} {'peak':>7} {'peak/code':>10} {'sd':>7}")
    contrasts = {}
    for pkey, sc, comp in ROWS:
        profile = L.PROFILES[pkey][0]
        sid = f"impulse__{comp}__rest"
        c = contrast_of(profile, sid, sc, comps)
        if c is None:
            continue
        contrasts[(pkey, comp)] = c
        body, peak, sd = c
        code = float(L.linearise(np.array([L.encode(body) * 255.0 + 1.0]))[0]) - body
        out.append(f"  {pkey + ' ' + comp:>18} {body:7.4f} {peak:7.4f} {peak / code:10.1f} "
                   f"{sd:7.4f}")
    out.append("")
    out.append("`peak/code` is the dot peak in 8-bit display codes at that level. The heavy")
    out.append("component's own share of that peak is what reader D has to see, and the last")
    out.append("column of each table below says how many codes that is.")
    out.append("")
    for pkey, sc, comp in ROWS:
        if (pkey, comp) not in contrasts:
            continue
        body, peak, _ = contrasts[(pkey, comp)]
        shape = (int(200 * sc), int(320 * sc))
        bg = L.background_for("impulse", sc, shape)
        mask = L.Cell(comp, comps).body_mask(sc, shape, 12.0)
        out.append(f"### {pkey} {comp} (body {body:.4f}, peak {peak:.4f})")
        out.append("")
        out.append(f"  {'sigS in':>7} {'sigH in':>7} {'w in':>6} | {'sigS out':>8} "
                   f"{'sigH out':>8} {'w out':>6} {'err %':>7} {'heavy codes':>12}")
        for s1, s2, w in CASES:
            a, b = s1 * sc, s2 * sc
            lum = synth(bg, a, b, w, body=body, peak=peak)
            f = D.lattice_fit(lum, bg, mask, sc)
            out.append(f"  {a:7.2f} {b:7.2f} {w:6.2f} | {f['sharpSigmaDev']:8.2f} "
                       f"{f['heavySigmaDev']:8.2f} {f['heavyShare']:6.2f} "
                       f"{abs(f['heavySigmaDev'] - b) / b * 100:7.1f} "
                       f"{heavy_codes(bg, a, b, w, body, peak):12.2f}")
        out.append("")

    out.append("### The two kernels the 1x raster cannot tell apart")
    out.append("")
    out.append("The decisive statement, and it is about the FIXTURE and not about any reader: a")
    out.append("heavy component of 13.42 device px and one of 25.0 device px, each at its own")
    out.append("share, land in the same 8-bit tile.")
    out.append("")
    scale, shape = 1.0, (200, 320)
    bg = L.background_for("impulse", scale, shape)
    body, peak, _ = contrasts[("1x-light", "rrect-lg")]
    mask = L.Cell("rrect-lg", comps).body_mask(scale, shape, 12.0)
    a1 = synth(bg, 2.0, 13.42, 0.23, body=body, peak=peak)
    a2 = synth(bg, 2.5, 25.0, 0.40, body=body, peak=peak)
    u1 = synth(bg, 2.0, 13.42, 0.23, body=body, peak=peak, quant=False)
    u2 = synth(bg, 2.5, 25.0, 0.40, body=body, peak=peak, quant=False)
    dq = np.abs(a1 - a2)[mask]
    du = np.abs(u1 - u2)[mask]
    out.append(f"  before quantisation: max |d| {du.max():.5f} linear "
               f"({L.codes(body + du.max(), body):.2f} codes), mean {du.mean():.5f}")
    out.append(f"  after  quantisation: max |d| {dq.max():.5f} linear "
               f"({L.codes(body + dq.max(), body):.2f} codes), "
               f"identical pixels {100.0 * float(np.mean(dq == 0)):.1f} %")
    out.append("")

    out.append("### The low-pass that was tried and did not help")
    out.append("")
    out.append("Both the image and every model column through one matched Gaussian, scanned over")
    out.append("its width, on the 1x `rrect-lg` contrast. It quiets the staircase and collapses")
    out.append("the sharp component into the heavy one, and no setting reads the drawn width.")
    out.append("")
    header = f"  {'low-pass':>9} "
    for a, b, _ in CASES[:4]:
        header += "| %13s " % ("in %.1f/%.2f" % (a, b))
    out.append(header)
    for lp in (0.0, 1.0, 2.0, 4.0):
        line = f"  {lp:9.1f} "
        for s1, s2, w in CASES[:4]:
            lum = synth(bg, s1, s2, w, body=body, peak=peak)
            f = D.lattice_fit(lum, bg, mask, scale, smooth=lp)
            line += f"| {f['sharpSigmaDev']:5.2f}/{f['heavySigmaDev']:7.2f} "
        out.append(line)
    out.append("")

    out.append("### The chain's own level-4 kernel, which is not a Gaussian")
    out.append("")
    out.append("`chain-kernel.txt` reads level 4 at sigma 13.660 by second moment and 14.327 by")
    out.append("half maximum, kurtosis -0.23. Reader A reduces a kernel by HALF MAXIMUM, so 14.33")
    out.append("is the number reader D should be held to on this shape. Read WITHOUT quantisation,")
    out.append("which is the only condition under which reader D reads anything on this bed.")
    out.append("")
    psf = chain_level_psf(4, 256)
    heavy = convolve_psf(bg, psf)
    out.append(f"  {'share':>6} {'sigS out':>8} {'sigH out':>8} {'w out':>6} {'resid':>7}")
    for share in (0.23, 0.5, 1.0):
        k = (1 - share) * gaussian_filter(bg, 2.0, mode="nearest") + share * heavy
        lum = body + (peak / max(float(k.max()), 1e-9)) * k
        f = D.lattice_fit(lum, bg, mask, scale)
        out.append(f"  {share:6.2f} {f['sharpSigmaDev']:8.2f} {f['heavySigmaDev']:8.2f} "
                   f"{f['heavyShare']:6.2f} {f['rmsRel']:7.4f}")
    out.append("")


IMPULSE_ROWS = ("impulse__rrect-md__rest", "impulse__rrect-ml__rest", "impulse__rrect-lg__rest")


def read_pair(root, profile, scale, sid, comps):
    web = os.path.join(root, profile, sid, f"{sid}__webgpu.png")
    if not os.path.exists(web):
        return None
    shape = (int(200 * scale), int(320 * scale))
    lum = L.luma_of(web)
    if lum.shape != shape:
        return None
    bg = L.background_for("impulse", scale, shape)
    scene_component = sid.split("__")[1]
    cell = L.Cell(scene_component, comps)
    a_rows = L.read_psf_cell(lum, bg, cell, scale, half_css=30.0)
    a = None
    if a_rows:
        a = {
            "sharp": float(np.median([r["sharpSigmaDev"] for r in a_rows])),
            "heavy": float(np.median([r["heavySigmaDev"] for r in a_rows])),
            "share": float(np.median([r["heavyShare"] for r in a_rows])),
            "ceiling": bool(np.any([r["atCeiling"] for r in a_rows])),
        }
    d = D.read_lattice_cell(lum, bg, cell, scale)
    return a, d


def against_reader_a(out, ladder):
    out.append("## 2. Reader D against reader A, on the 2x rows where reader A is monotone")
    out.append("")
    out.append("W26 G0 measured reader A monotone at 2x over σ 10 → 16 and drifting above it")
    out.append("(claims §5.119 §2). The acceptance is agreement within 10 % on that range.")
    out.append("")
    comps = L.load_components()
    profile, scale = "apple-macos-26.5-2x-light-standard", 2.0
    out.append(f"  {'rung':>6} {'row':>10} | {'A heavy':>8} {'D heavy':>8} {'Δ %':>7} | "
               f"{'A share':>8} {'D share':>8} | {'A sharp':>8} {'D sharp':>8}")
    diffs = []
    for rung in ("t10", "t13", "t16", "t19", "t22", "t25"):
        root = os.path.join(ladder, rung, "web-captures")
        for sid in IMPULSE_ROWS:
            pair = read_pair(root, profile, scale, sid, comps)
            if pair is None:
                continue
            a, d = pair
            if a is None or d is None:
                continue
            delta = (d["heavySigmaDev"] - a["heavy"]) / a["heavy"] * 100.0
            if rung in ("t10", "t13", "t16"):
                diffs.append(abs(delta))
            out.append(f"  {rung:>6} {sid.split('__')[1]:>10} | {a['heavy']:8.2f} "
                       f"{d['heavySigmaDev']:8.2f} {delta:7.1f} | {a['share']:8.3f} "
                       f"{d['heavyShare']:8.3f} | {a['sharp']:8.2f} {d['sharpSigmaDev']:8.2f}")
    out.append("")
    if diffs:
        out.append(f"Median |Δ| over σ 10 / 13 / 16: **{np.median(diffs):.1f} %**, "
                   f"worst {max(diffs):.1f} %.")
    out.append("")


def reference(out):
    out.append("## 3. The reference read with reader D, beside W25's reader-A numbers")
    out.append("")
    out.append("W25 §5.113 §2 read the reference's heavy component at 19.52 device px at 1x and")
    out.append("11.29 at 2x with reader A. Those numbers are not rewritten; this is the same")
    out.append("fixtures read with the new instrument, recorded beside them.")
    out.append("")
    comps = L.load_components()
    out.append(f"  {'profile':>9} {'row':>10} | {'A heavy':>8} {'A share':>8} {'A ceil':>7} | "
               f"{'D heavy':>8} {'D share':>8} {'D sharp':>8} {'D mod':>6} {'D resid':>8}")
    for pkey in ("1x-light", "2x-light"):
        profile, scale, _ = L.PROFILES[pkey]
        for sid in IMPULSE_ROWS + ("impulse__rrect-sm__rest",):
            native = L.native_path(profile, sid)
            if not os.path.exists(native):
                continue
            shape = (int(200 * scale), int(320 * scale))
            lum = L.luma_of(native)
            if lum.shape != shape:
                continue
            bg = L.background_for("impulse", scale, shape)
            cell = L.Cell(sid.split("__")[1], comps)
            a_rows = L.read_psf_cell(lum, bg, cell, scale, half_css=30.0)
            ah = np.median([r["heavySigmaDev"] for r in a_rows]) if a_rows else float("nan")
            ash = np.median([r["heavyShare"] for r in a_rows]) if a_rows else float("nan")
            ac = bool(np.any([r["atCeiling"] for r in a_rows])) if a_rows else False
            d = D.read_lattice_cell(lum, bg, cell, scale)
            if d is None:
                out.append(f"  {pkey:>9} {sid.split('__')[1]:>10} | {ah:8.2f} {ash:8.3f} "
                           f"{str(ac):>7} |  NO FIT")
                continue
            out.append(f"  {pkey:>9} {sid.split('__')[1]:>10} | {ah:8.2f} {ash:8.3f} "
                       f"{str(ac):>7} | {d['heavySigmaDev']:8.2f} {d['heavyShare']:8.3f} "
                       f"{d['sharpSigmaDev']:8.2f} {d['heavyMod']:6.3f} {d['rmsRel']:8.4f}")
    out.append("")


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--ladder", default=G0_SCRATCH)
    ap.add_argument("--out", default=os.path.join(HERE, "reader-d.txt"))
    ap.add_argument("--skip", default="")
    args = ap.parse_args(argv)
    skip = set(args.skip.split(",")) if args.skip else set()

    out = ["# W26 G1 — reader D (the lattice reader), validated", ""]
    if "synthetic" not in skip:
        synthetic(out)
    if "readera" not in skip:
        against_reader_a(out, args.ladder)
    if "reference" not in skip:
        reference(out)
    text = "\n".join(out)
    print(text)
    open(args.out, "w").write(text + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
