"""W26 G1 §7 — reader D on the COARSE CHECKERBOARDS, where the 1x fixture has codes to spare.

WHY THIS EXISTS. §2 measured that the 1x `impulse` fixture cannot carry the heavy component at 8
bits: its interior modulation is about one display code and the heavy component's share of it is a
fraction of one. That is a statement about the impulse tile's CONTRAST, and reader D was never
specific to it — the model is "the backdrop raster itself, convolved with a sharp and a heavy
Gaussian at their own amplitudes", and any periodic raster serves. The coarse checkerboards carry
54-73 codes of interior contrast, and a 64 CSS px pitch's fundamental is still modulated about 16 %
by a 19.5 device px heavy component at 1x — which on those rows is ten codes, not a tenth of one.

W26 G0 §7 retired the coarse checkerboards, and this does not contradict it: what G0 retired was a
SINGLE-Gaussian objective (readers B and C), which is dominated by the kernel's core and answers
about the sharp component at any width (W26 Decision Log 2 (d)). A two-component lattice reader is a
different instrument on the same pixels, and it separates what that objective could not.

WHAT IS READ, in the order a new instrument earns its readings:

  §A the fixtures' own contrast, in display codes, so the claim above is a measurement;
  §B reader D on synthetics made at each fixture's own level and TRANSMISSION — not at its observed
     contrast, because a wider kernel must be allowed to flatten the checkerboard the way it really
     would — through the sRGB 8-bit step, plus the chain's own platykurtic level-4 kernel;
  §C the cross-check against reader A and against reader D on the impulse row where all three are
     conditioned (2x `impulse__rrect-md`);
  §D the reference read at both scales, with the SHARP column as the conditioning statistic;
  §E vitrea's 1x ladder, which is the mapping a fit needs.

Read-only on the fixtures and on this child's scratch capture roots; nothing canonical is written.

    g1-checker.py [--scratch DIR] [--out FILE]
"""

import argparse
import os
import sys

import numpy as np
from scipy.ndimage import gaussian_filter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import w26lib as D  # noqa: E402
import w25lib as L  # noqa: E402

SCRATCH = "/Users/new/.claude/jobs/5c70e47f/tmp/w26/g1"
BACKDROPS = ("checkerboard-64", "checkerboard-32")
COMPONENTS = ("rrect-lg", "rrect-ml", "rrect-md")
# Wider than reader A's 6 CSS px and than §2's 12: this reader fits ONE model across the whole
# interior, and the rim's band, the lens's displacement and the inner shadow are none of them a
# convolution of the backdrop. Sixteen CSS px clears all three on every component read here.
ERODE = 16.0
# The kernels the reader has to tell apart, in device px at scale 1, with the share each carries.
CASES = [(2.0, 10.0, 0.25), (2.0, 13.418, 0.23), (3.0, 19.5, 0.47), (2.5, 25.0, 0.40),
         (2.5, 30.0, 0.40)]
# The rungs of the 1x ladder, and the sigma each names at both anchors. `c1` is 13.418.
LADDER = [("r0", None), ("t10", 10.0), ("c1", 13.418), ("t16", 16.0), ("t19", 19.0),
          ("t22", 22.0), ("t25", 25.0)]


def quantise(a):
    """The 8-bit step through the sRGB OETF, which is where a PNG's quantisation is."""
    return L.linearise(np.round(L.encode(np.clip(a, 0.0, 1.0)) * 255.0))


def contrast_of(lum, mask):
    v = lum[mask]
    lo, hi = float(np.percentile(v, 2)), float(np.percentile(v, 98))
    return lo, hi - lo, abs(L.codes(hi, lo))


def transmission(bg, mask, body, amp, s1=3.0, s2=19.5, share=0.47):
    """The gain one FIXED kernel needs to reproduce the native's observed contrast.

    The whole point of holding it fixed is that a wider kernel then shows LESS contrast, the way it
    really would. Normalising every synthetic to the native's own contrast instead would hand a
    kernel that flattens the checkerboard the codes it has actually destroyed, and would validate an
    instrument that does not exist.
    """
    k = (1 - share) * gaussian_filter(bg, s1, mode="nearest") \
        + share * gaussian_filter(bg, s2, mode="nearest")
    lo, hi = np.percentile(k[mask], 2), np.percentile(k[mask], 98)
    return amp / max(float(hi - lo), 1e-9), float(lo)


def synth(bg, s1, s2, share, body, gain, ref_lo, quant=True):
    k = (1 - share) * gaussian_filter(bg, s1, mode="nearest") \
        + share * gaussian_filter(bg, s2, mode="nearest")
    f = body + gain * (k - ref_lo)
    return quantise(f) if quant else f


def chain_level_psf(level, size=256):
    """`g0-chain.py`'s simulation of the pyramid's own kernel, reduced to the point spread."""
    taps = [(0, 0, 0.125),
            (-1, 1, 0.125), (1, 1, 0.125), (-1, -1, 0.125), (1, -1, 0.125),
            (0, 2, 0.0625), (-2, 0, 0.0625), (2, 0, 0.0625), (0, -2, 0.0625),
            (-2, 2, 0.03125), (2, 2, 0.03125), (-2, -2, 0.03125), (2, -2, 0.03125)]

    def box2x2(a):
        return 0.25 * (a + np.roll(a, -1, 0) + np.roll(a, -1, 1)
                       + np.roll(np.roll(a, -1, 0), -1, 1))

    def down(src):
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
    for _ in range(level):
        a = down(a)
    return reconstruct(a, 2 ** level)


def convolve_psf(img, psf):
    ph, pw = psf.shape
    ih, iw = img.shape
    k = np.zeros_like(img)
    cy, cx = ph // 2, pw // 2
    for dy in range(-min(cy, ih // 2), min(ph - cy, ih // 2)):
        for dx in range(-min(cx, iw // 2), min(pw - cx, iw // 2)):
            k[dy % ih, dx % iw] += psf[cy + dy, cx + dx]
    k /= k.sum()
    return np.real(np.fft.ifft2(np.fft.fft2(img) * np.fft.fft2(k)))


def bed(profile, scale, backdrop, comp, comps):
    """One row's raster, mask and native contrast, or `None` where the fixture is not there."""
    sid = f"{backdrop}__{comp}__rest"
    native = L.native_path(profile, sid)
    if not os.path.exists(native):
        return None
    shape = (int(200 * scale), int(320 * scale))
    lum = L.luma_of(native)
    if lum.shape != shape:
        return None
    bg = L.background_for(backdrop, scale, shape)
    mask = L.Cell(comp, comps).body_mask(scale, shape, ERODE)
    if mask.sum() < 2000:
        return None
    body, amp, codes = contrast_of(lum, mask)
    return {"sid": sid, "bg": bg, "mask": mask, "native": lum, "body": body, "amp": amp,
            "codes": codes, "scale": scale, "shape": shape}


def read_web(root, profile, row):
    path = os.path.join(root, profile, row["sid"], f"{row['sid']}__webgpu.png")
    if not os.path.exists(path):
        return None
    lum = L.luma_of(path)
    if lum.shape != row["shape"]:
        return None
    return D.lattice_fit(lum, row["bg"], row["mask"], row["scale"])


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--scratch", default=SCRATCH)
    ap.add_argument("--out", default=os.path.join(HERE, "checker.txt"))
    args = ap.parse_args(argv)
    comps = L.load_components()
    out = []
    e = out.append
    e("W26 G1 §7 — reader D on the coarse checkerboards")
    e("=" * 100)
    e("")

    # --- A. the fixtures' own contrast -------------------------------------------------------
    e("A. The fixtures' interior contrast, in 8-bit display codes")
    e("")
    e("   p2..p98 of the NATIVE interior (eroded 16 CSS px), expressed through the sRGB OETF at")
    e("   that level. The 1x `impulse` rows of §2 carry 9-14 codes of DOT PEAK and a heavy")
    e("   component of a fraction of one code; these carry the numbers below across the whole tile.")
    e("")
    e(f"   {'profile':>9} {'row':>34} {'n':>7} {'body':>7} {'amp':>7} {'codes':>7}")
    rows = {}
    for pkey in ("1x-light", "2x-light"):
        profile, scale, _ = L.PROFILES[pkey]
        for backdrop in BACKDROPS:
            for comp in COMPONENTS:
                r = bed(profile, scale, backdrop, comp, comps)
                if r is None:
                    continue
                rows[(pkey, backdrop, comp)] = r
                e(f"   {pkey:>9} {r['sid']:>34} {int(r['mask'].sum()):7d} {r['body']:7.4f} "
                  f"{r['amp']:7.4f} {r['codes']:7.1f}")
    e("")

    # --- B. synthetics at those fixtures' own beds --------------------------------------------
    e("B. Reader D on synthetics at each fixture's own level and transmission, through 8 bits")
    e("")
    e("   The transmission is held FIXED across the kernels of one row — calibrated so that a")
    e("   3.0 / 19.5 / 0.47 kernel reproduces that row's observed contrast — so a wider kernel")
    e("   flattens the checkerboard the way it really would instead of being handed back the codes")
    e("   it destroyed. `float` is the same synthetic unquantised, which isolates the 8-bit step.")
    e("")
    worst = 0.0
    for key in sorted(rows):
        pkey, backdrop, comp = key
        if pkey != "1x-light":
            continue
        r = rows[key]
        gain, ref_lo = transmission(r["bg"], r["mask"], r["body"], r["amp"])
        e(f"   {r['sid']} ({r['codes']:.0f} codes)")
        e(f"     {'in':>20} | {'float out':>22} | {'8-bit out':>22} {'err %':>7} {'resid':>7}")
        for s1, s2, share in CASES:
            a, b = s1 * r["scale"], s2 * r["scale"]
            fu = D.lattice_fit(synth(r["bg"], a, b, share, r["body"], gain, ref_lo, quant=False),
                               r["bg"], r["mask"], r["scale"])
            fq = D.lattice_fit(synth(r["bg"], a, b, share, r["body"], gain, ref_lo),
                               r["bg"], r["mask"], r["scale"])
            err = abs(fq["heavySigmaDev"] - b) / b * 100.0
            worst = max(worst, err)
            e(f"     {a:6.2f}/{b:6.2f}/{share:4.2f} | {fu['sharpSigmaDev']:6.2f}/"
              f"{fu['heavySigmaDev']:6.2f}/{fu['heavyShare']:4.2f} | "
              f"{fq['sharpSigmaDev']:6.2f}/{fq['heavySigmaDev']:6.2f}/{fq['heavyShare']:4.2f} "
              f"{err:7.1f} {fq['rmsRel']:7.4f}")
        e("")
    e(f"   Worst 8-bit heavy-width error over every 1x checkerboard row and kernel: {worst:.1f} %.")
    e("")

    e("   The chain's own platykurtic level-4 kernel (half maximum 14.33; `chain-kernel.txt`),")
    e("   on `checkerboard-64__rrect-lg` at 1x, through the same 8-bit step:")
    e("")
    r = rows[("1x-light", "checkerboard-64", "rrect-lg")]
    gain, ref_lo = transmission(r["bg"], r["mask"], r["body"], r["amp"])
    heavy = convolve_psf(r["bg"], chain_level_psf(4, 256))
    e(f"     {'share':>6} {'sharp':>7} {'heavy':>7} {'share out':>10} {'resid':>7}")
    for share in (0.23, 0.5, 1.0):
        k = (1 - share) * gaussian_filter(r["bg"], 2.0, mode="nearest") + share * heavy
        f = quantise(r["body"] + gain * (k - ref_lo))
        fit = D.lattice_fit(f, r["bg"], r["mask"], r["scale"])
        e(f"     {share:6.2f} {fit['sharpSigmaDev']:7.2f} {fit['heavySigmaDev']:7.2f} "
          f"{fit['heavyShare']:10.3f} {fit['rmsRel']:7.4f}")
    e("")

    # --- C. the cross-check on a row where the other readers are conditioned -------------------
    e("C. Cross-check on 2x `impulse__rrect-md`, where reader A, reader D and this are conditioned")
    e("")
    e("   The same rungs read three ways. Reader A and reader D on the impulse row are §5.120 §1's")
    e("   and §2's instruments; the third column is reader D on `checkerboard-64__rrect-md` at 2x,")
    e("   the row this section adds. Agreement here is what lets the checkerboard read the 1x rows")
    e("   that the impulse tile cannot.")
    e("")
    profile2, scale2, _ = L.PROFILES["2x-light"]
    imp_bg = L.background_for("impulse", scale2, (400, 640))
    imp_cell = L.Cell("rrect-md", comps)
    chk = rows.get(("2x-light", "checkerboard-64", "rrect-md"))
    e(f"   {'rung':>6} {'sigma':>7} | {'A imp':>8} {'D imp':>8} {'D chk-64':>9} | "
      f"{'A share':>8} {'D chk share':>12} {'D chk resid':>12}")
    for rung, sigma in [("r0", None), ("t10", 10.0), ("t13", 13.0), ("t16", 16.0)]:
        root = os.path.join(args.scratch, rung, "web-captures")
        p = os.path.join(root, profile2, "impulse__rrect-md__rest",
                         "impulse__rrect-md__rest__webgpu.png")
        if not os.path.exists(p):
            continue
        lum = L.luma_of(p)
        arows = L.read_psf_cell(lum, imp_bg, imp_cell, scale2, half_css=30.0)
        a_h = float(np.median([x["heavySigmaDev"] for x in arows])) if arows else float("nan")
        a_s = float(np.median([x["heavyShare"] for x in arows])) if arows else float("nan")
        d_imp = D.lattice_fit(lum, imp_bg, imp_cell.body_mask(scale2, lum.shape, 12.0), scale2)
        d_chk = read_web(root, profile2, chk) if chk else None
        e(f"   {rung:>6} {('inert' if sigma is None else f'{sigma:.1f}'):>7} | {a_h:8.2f} "
          f"{(d_imp['heavySigmaDev'] if d_imp else float('nan')):8.2f} "
          f"{(d_chk['heavySigmaDev'] if d_chk else float('nan')):9.2f} | {a_s:8.3f} "
          f"{(d_chk['heavyShare'] if d_chk else float('nan')):12.3f} "
          f"{(d_chk['rmsRel'] if d_chk else float('nan')):12.4f}")
    e("")

    # --- D. the reference ----------------------------------------------------------------------
    e("D. The reference read with reader D on the checkerboards, both scales")
    e("")
    e("   The SHARP column is the conditioning statistic (§5.120 §3): a two-component fit whose")
    e("   sharp component comes back at 9-12 device px has split one wide kernel in half. Nothing")
    e("   recorded elsewhere is rewritten; these are new readings on rows nobody has read this way.")
    e("")
    e(f"   {'profile':>9} {'row':>34} {'sharp':>7} {'heavy':>7} {'share':>7} {'resid':>7}")
    reference = {}
    for key in sorted(rows):
        r = rows[key]
        fit = D.lattice_fit(r["native"], r["bg"], r["mask"], r["scale"])
        if fit is None:
            continue
        reference[key] = fit
        e(f"   {key[0]:>9} {r['sid']:>34} {fit['sharpSigmaDev']:7.2f} "
          f"{fit['heavySigmaDev']:7.2f} {fit['heavyShare']:7.3f} {fit['rmsRel']:7.4f}")
    e("")

    # --- E. vitrea's 1x ladder ------------------------------------------------------------------
    e("E. Vitrea's 1x ladder, read on the checkerboards — the mapping a fit needs")
    e("")
    profile1, scale1, _ = L.PROFILES["1x-light"]
    for backdrop in BACKDROPS:
        for comp in COMPONENTS:
            key = ("1x-light", backdrop, comp)
            if key not in rows:
                continue
            r = rows[key]
            ref = reference.get(key)
            e(f"   {r['sid']}   reference: sharp {ref['sharpSigmaDev']:.2f}  heavy "
              f"{ref['heavySigmaDev']:.2f}  share {ref['heavyShare']:.3f}  resid "
              f"{ref['rmsRel']:.4f}")
            e(f"     {'rung':>6} {'sigma':>7} {'sharp':>7} {'heavy':>7} {'share':>7} {'resid':>7}")
            for rung, sigma in LADDER:
                fit = read_web(os.path.join(args.scratch, rung, "web-captures"), profile1, r)
                if fit is None:
                    continue
                e(f"     {rung:>6} {('inert' if sigma is None else f'{sigma:.2f}'):>7} "
                  f"{fit['sharpSigmaDev']:7.2f} {fit['heavySigmaDev']:7.2f} "
                  f"{fit['heavyShare']:7.3f} {fit['rmsRel']:7.4f}")
            e("")

    text = "\n".join(out)
    print(text)
    open(args.out, "w").write(text + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
