"""W26 G1b — reader E on synthetics: the smoothness weight chosen, and the reader's own bias measured.

WHAT THIS IS FOR, in order.

  1. **λ is chosen here and nowhere else.** The fit's only free knob is the second-difference
     penalty. Choosing it on the thing being measured would make it part of the answer, so it is
     chosen on synthetics whose kernel is known and then frozen for the control and the reference.
  2. **The reader's bias is measured on shapes it was not built around.** A Gaussian, a
     two-Gaussian mixture, the chain's own platykurtic level-4 kernel, vitrea's real composite and
     an exponential (heavy-tailed, which no Gaussian basis can imitate) are each recovered from the
     same eight backdrops at each fixture's OWN measured level and contrast, through the 8-bit sRGB
     step. A reader that recovers all five is not preferring a shape.

THE SYNTHETIC IS THE REAL BACKDROP, NOT A MODEL OF IT. Each row is the fixture's own backdrop
raster convolved with the known kernel, then put through a gain and offset chosen so the row
reproduces the level and the p2..p98 amplitude the REAL capture of that row has, then quantised the
way a capture is. So the modulation the reader has to work with is the modulation the real file
carries — which is the whole of W26 G1 §2's finding about the 1x `impulse` tile, reproduced here
rather than assumed away.
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

EXTENT = {1.0: 64.0, 2.0: 64.0}
NODES = 40
CASES = (("rrect-md", 1.0, (16.0, 48.0)), ("rrect-md", 2.0, (16.0, 48.0)),
         ("rrect-lg", 1.0, (16.0, 80.0)), ("rrect-lg", 2.0, (16.0, 80.0)))
LAMBDAS = (0.0, 1e-4, 3e-4, 1e-3, 3e-3, 1e-2, 3e-2, 1e-1)


def exp_profile(nodes, scale_len):
    k = np.exp(-np.asarray(nodes, dtype=np.float64) / scale_len)
    mass = float(E._masses(nodes) @ k)
    return k / mass


def known_kernels(nodes, comp, scale, band, m):
    depths = np.linspace(band[0], min(band[1], TRUTH.SPANS[comp] / 2), 33)
    t = TRUTH.truth_profile(TRUTH.SPANS[comp], scale, depths, nodes, m)
    two = (1 - 0.47) * E.gauss_profile(nodes, 2.0) + 0.47 * E.gauss_profile(nodes, 19.5)
    return {
        "gauss-8": E.gauss_profile(nodes, 8.0),
        "two-gauss 2.0/19.5 @0.47": two,
        "chain level 4": TRUTH.chain_profile(4, nodes),
        f"vitrea {comp} {scale:.0f}x (k={t['kMean']:.3f})": t["c"],
        "exponential L=8": exp_profile(nodes, 8.0),
    }


def synth_rows(real_rows, nodes, c_true, seed=0):
    """Each real row's backdrop convolved with `c_true`, matched to its level and contrast, 8-bit."""
    out = []
    for r in real_rows:
        m = c_true @ r["A"]
        amp = float(np.percentile(m, 98) - np.percentile(m, 2))
        a = (r["amp"] / amp) if amp > 1e-12 else 0.0
        b = r["level"] - a * float(m.mean())
        y = a * m + b
        # The 8-bit sRGB step, applied where a capture applies it: on the display signal.
        y = L.linearise(np.round(np.clip(L.encode(y), 0.0, 1.0) * 255.0))
        out.append({"name": r["name"], "A": r["A"], "y": y})
    return out


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(HERE, "synth.txt"))
    ap.add_argument("--profile", default="1x-light")
    args = ap.parse_args(argv)
    comps = L.load_components()
    m = TRUTH.material()
    lines = []
    e = lines.append
    e("W26 G1b — reader E on synthetics: the smoothness weight, and the reader's bias by shape")
    e("=" * 100)
    e("")
    e("Every row is the fixture's OWN backdrop raster convolved with the named kernel, gained and")
    e("offset to the level and p2..p98 amplitude the real capture of that row carries, and put")
    e("through the 8-bit sRGB step. Errors are against the known kernel: `MTF` is the RMS relative")
    e("error of the recovered modulation transfer over 1/64..1/8 cycles per device px, `HWHM` and")
    e("`RMS` the two width statistics. The acceptance the brief sets is 10 % on MTF and on HWHM.")
    e("")

    # ---------------------------------------------------------------- the lambda sweep
    e("### 1. The smoothness weight, chosen once")
    e("")
    e(f"   {'lambda':>8} | " + " | ".join(f"{k:>26}" for k in
                                          ("gauss-8", "two-gauss", "chain L4", "vitrea", "exp")))
    e("   " + "-" * 96)
    tally = {lam: [] for lam in LAMBDAS}
    detail = {lam: {} for lam in LAMBDAS}
    for comp, scale, band in CASES:
        pkey = f"{'1x' if scale == 1 else '2x'}-light"
        profile, _, _ = L.PROFILES[pkey]
        nodes = E.radial_nodes(EXTENT[scale], NODES)
        cell, rows = R.assemble("web", profile, scale, comp, band, nodes, comps)
        if len(rows) < 4:
            e(f"   {comp} {scale:.0f}x: only {len(rows)} rows — skipped")
            continue
        kernels = known_kernels(nodes, comp, scale, band, m)
        for lam in LAMBDAS:
            for label, c_true in kernels.items():
                syn = synth_rows(rows, nodes, c_true)
                fit = E.joint_profile(syn, nodes, lam=lam)
                rms, worst, *_ = R.rel_mtf_error(nodes, fit["c"], c_true)
                wt = E.widths_of_profile(nodes, c_true)
                wr = E.widths_of_profile(nodes, fit["c"])
                dh = abs(wr["sigmaHwhm"] / wt["sigmaHwhm"] - 1.0)
                dr = abs(wr["sigmaRms"] / wt["sigmaRms"] - 1.0)
                tally[lam].append((rms, dh, dr))
                detail[lam].setdefault(label.split(" ")[0], []).append((rms, dh, dr))
    for lam in LAMBDAS:
        if not tally[lam]:
            continue
        cols = []
        for key in ("gauss-8", "two-gauss", "chain", "vitrea", "exponential"):
            v = detail[lam].get(key)
            cols.append(f"MTF {np.mean([x[0] for x in v]) * 100:5.1f}% HWHM "
                        f"{np.mean([x[1] for x in v]) * 100:5.1f}%" if v else " " * 26)
        e(f"   {lam:8.4f} | " + " | ".join(cols))
    best = min((lam for lam in LAMBDAS if tally[lam]),
               key=lambda lam: np.mean([x[0] + x[1] for x in tally[lam]]))
    e("")
    e(f"   CHOSEN: lambda = {best}, on the mean of MTF + HWHM error over every shape and every")
    e("   case above. Frozen from here: the control and the reference are read at this value.")

    # ---------------------------------------------------------------- per case at the chosen lambda
    e("")
    e("### 2. Per case, at the chosen weight")
    e("")
    e(f"   {'surface':>9} {'sc':>3} {'rows':>4} {'kernel':>28} {'MTF':>7} {'worst':>7}"
      f" {'HWHM true':>9} {'read':>7} {'RMS true':>9} {'read':>7}")
    for comp, scale, band in CASES:
        pkey = f"{'1x' if scale == 1 else '2x'}-light"
        profile, _, _ = L.PROFILES[pkey]
        nodes = E.radial_nodes(EXTENT[scale], NODES)
        cell, rows = R.assemble("web", profile, scale, comp, band, nodes, comps)
        if len(rows) < 4:
            continue
        for label, c_true in known_kernels(nodes, comp, scale, band, m).items():
            syn = synth_rows(rows, nodes, c_true)
            fit = E.joint_profile(syn, nodes, lam=best)
            rms, worst, *_ = R.rel_mtf_error(nodes, fit["c"], c_true)
            wt = E.widths_of_profile(nodes, c_true)
            wr = E.widths_of_profile(nodes, fit["c"])
            e(f"   {comp:>9} {scale:3.0f} {len(rows):4d} {label:>28} {rms * 100:6.1f}%"
              f" {worst * 100:6.1f}% {wt['sigmaHwhm']:9.3f} {wr['sigmaHwhm']:7.3f}"
              f" {wt['sigmaRms']:9.3f} {wr['sigmaRms']:7.3f}")
    e("")
    e(f"CHOSEN LAMBDA = {best}")
    text = "\n".join(lines)
    print(text)
    open(args.out, "w").write(text + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
