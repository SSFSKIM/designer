"""W26 G1b — THE CONTROL. Reader E run on vitrea's own captures, where the kernel is known exactly.

THIS IS BINDING AND IT COMES FIRST. W26 G1 §7.6's verdict was that the joint two-Gaussian fit
under-read vitrea's known 13.42 device px by 14–23 %, and that a reader which fails its control has
nothing to say about the reference. So reader E is held against `g1b-truth.py`'s statement of what
`wgsl/optics.ts` actually convolves the backdrop with at the frozen 0.14.0 material — the chain
level `scatterLod` selects, trilinearly blended, mixed with the body's 1.25 device px Gaussian at
`kScatter` — over the same depth band the fit is taken on, before one number is read off the
reference.

THE ACCEPTANCE, as the brief sets it: the recovered K must reproduce the known kernel's MTF within
10 % between 1/64 and 1/8 cycles per device px, and its half-maximum width within 10 %.

A SECOND BAND IS REPORTED BESIDE IT, and it is not decoration. A Gaussian of σ 13.4 device px has
transferred 3 % of its modulation by 1/32 cycles per px and 4 × 10⁻¹⁴ by 1/8: the brief's band is
where the SHARP component lives, and a reader can pass it while knowing nothing about the heavy
one. The band that carries the heavy component is 1/256 to 1/32, and both are reported so a pass on
one is not read as a pass on the other.

The canonical `web-captures/` are the frozen 0.14.0 bed and are opened READ-ONLY; W26 G1 §1
measured every re-rendered bed row byte-identical to them, so no capture is taken here.
"""

import argparse
import importlib.util
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import w26blib as E  # noqa: E402
import w26brows as R  # noqa: E402
import w25lib as L  # noqa: E402

_spec = importlib.util.spec_from_file_location("g1btruth", os.path.join(HERE, "g1b-truth.py"))
TRUTH = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(TRUTH)
_ss = importlib.util.spec_from_file_location("g1bsynth", os.path.join(HERE, "g1b-synth.py"))
SYNTH = importlib.util.module_from_spec(_ss)
_ss.loader.exec_module(SYNTH)

EXTENT = 64.0
NODES = 40
SHARP_BAND = (1.0 / 64.0, 1.0 / 8.0)
HEAVY_BAND = (1.0 / 256.0, 1.0 / 32.0)
CASES = (("rrect-md", 1.0, (16.0, 48.0)), ("rrect-md", 2.0, (16.0, 48.0)),
         ("rrect-lg", 1.0, (16.0, 80.0)), ("rrect-lg", 2.0, (16.0, 80.0)))


def band_row(nodes, c, ref, band):
    rms, worst, f, a, b = R.rel_mtf_error(nodes, c, ref, band=band, n=25)
    return rms, worst


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--lam", type=float, required=True,
                    help="the smoothness weight chosen on synthetics by `g1b-synth.py`")
    ap.add_argument("--out", default=os.path.join(HERE, "control.txt"))
    args = ap.parse_args(argv)
    comps = L.load_components()
    m = TRUTH.material()
    nodes = E.radial_nodes(EXTENT, NODES)
    lines = []
    e = lines.append
    e("W26 G1b — THE CONTROL: reader E on vitrea's own captures, against the kernel vitrea draws")
    e("=" * 100)
    e("")
    e(f"Smoothness weight λ = {args.lam}, chosen on synthetics in `synth.txt` and frozen. Radial")
    e(f"grid: {NODES} hat nodes out to {EXTENT:.0f} device px. Rows: every thick untinted backdrop")
    e("the surface has, at the canonical 0.14.0 web captures, read over the stated band of depth.")
    e("")
    e("`MTF sharp` is the RMS and worst relative error of the recovered modulation transfer over")
    e("1/64..1/8 cycles per device px — the brief's band. `MTF heavy` is the same over 1/256..1/32,")
    e("which is where a kernel of σ 13 device px actually carries its modulation.")
    e("")
    e(f"  {'surface':>9} {'sc':>3} {'rows':>4} {'kScatter band':>20} {'MTF sharp':>16}"
      f" {'MTF heavy':>16} {'HWHM t/r':>16} {'RMSσ t/r':>16} {'tail':>6}")
    verdict = []
    fits = {}
    for comp, scale, band in CASES:
        pkey = f"{'1x' if scale == 1 else '2x'}-light"
        profile, _, _ = L.PROFILES[pkey]
        cell, rows = R.assemble("web", profile, scale, comp, band, nodes, comps)
        if len(rows) < 4:
            e(f"  {comp:>9} {scale:3.0f}  only {len(rows)} rows — not read")
            continue
        span = TRUTH.SPANS[comp]
        depths = np.linspace(band[0], min(band[1], span / 2), 65)
        t = TRUTH.truth_profile(span, scale, depths, nodes, m)
        fit = E.joint_profile(rows, nodes, lam=args.lam)
        fits[(comp, scale)] = (fit, t, rows)
        s_rms, s_worst = band_row(nodes, fit["c"], t["c"], SHARP_BAND)
        h_rms, h_worst = band_row(nodes, fit["c"], t["c"], HEAVY_BAND)
        wt = E.widths_of_profile(nodes, t["c"])
        wr = E.widths_of_profile(nodes, fit["c"])
        tail = float(E._masses(nodes)[-4:] @ fit["c"][-4:])
        e(f"  {comp:>9} {scale:3.0f} {len(rows):4d}"
          f" {t['kMean']:.3f}[{t['kMin']:.2f},{t['kMax']:.2f}]"
          f" {s_rms * 100:6.1f}% {s_worst * 100:6.1f}%"
          f" {h_rms * 100:6.1f}% {h_worst * 100:6.1f}%"
          f" {wt['sigmaHwhm']:7.3f} {wr['sigmaHwhm']:7.3f}"
          f" {wt['sigmaRms']:7.3f} {wr['sigmaRms']:7.3f} {tail * 100:5.1f}%")
        verdict.append((comp, scale, s_rms, h_rms,
                        abs(wr["sigmaHwhm"] / wt["sigmaHwhm"] - 1.0),
                        abs(wr["sigmaRms"] / wt["sigmaRms"] - 1.0)))
    e("")
    e("`tail` is the fraction of the recovered kernel's mass in the outermost four nodes — the")
    e("reader saying whether its own radial extent was wide enough for what it found.")
    e("")

    # ------------------------------------------------------------------ per-row residuals
    e("### Per-row fit residual, in units of the row's own quantisation step")
    e("")
    e("A row whose residual is about one quantisation step is fitted as well as the file allows; a")
    e("row far above it is a row the single shared kernel does not describe.")
    e("")
    for (comp, scale), (fit, t, rows) in fits.items():
        e(f"   {comp} {scale:.0f}x   " + "   ".join(
            f"{p['name']}: {p['rmsCodes']:.2f}" for p in fit["per"]))
    e("")

    # ------------------------------------------------------------------ the profiles
    e("### The recovered profile against the drawn one, normalised to its own peak")
    e("")
    for (comp, scale), (fit, t, rows) in fits.items():
        e(f"   {comp} {scale:.0f}x — DRAWN (truth)")
        lines.extend(R.fmt_profile(nodes, t["c"]))
        e(f"   {comp} {scale:.0f}x — READ")
        lines.extend(R.fmt_profile(nodes, fit["c"]))
        e("")

    # ------------------------------------------------------------------ the verdict
    e("### Verdict")
    e("")
    ok = True
    for comp, scale, s_rms, h_rms, dh, dr in verdict:
        passes = s_rms <= 0.10 and dh <= 0.10
        ok = ok and passes
        e(f"   {comp} {scale:.0f}x: MTF(1/64..1/8) {s_rms * 100:.1f}%, "
          f"MTF(1/256..1/32) {h_rms * 100:.1f}%, HWHM {dh * 100:.1f}%, RMSσ {dr * 100:.1f}% "
          f"— {'PASS' if passes else 'FAIL'}")
    e("")
    e(f"   CONTROL: {'PASSED' if ok else 'FAILED'} on the brief's acceptance "
      f"(10 % on MTF over 1/64..1/8 and on the half-maximum width).")
    text = "\n".join(lines)
    print(text)
    open(args.out, "w").write(text + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
