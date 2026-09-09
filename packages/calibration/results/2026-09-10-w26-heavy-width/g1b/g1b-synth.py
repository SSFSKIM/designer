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

EXTENT = {1.0: 96.0, 2.0: 96.0}
NODES = 40
CASES = (("rrect-md", 1.0, (16.0, 48.0)), ("rrect-md", 2.0, (16.0, 48.0)),
         ("rrect-lg", 1.0, (16.0, 80.0)), ("rrect-lg", 2.0, (16.0, 80.0)))
LAMBDAS = (1e-5, 1e-4, 3e-4, 1e-3, 3e-3, 1e-2, 3e-2)
SHARP_BAND = (1.0 / 64.0, 1.0 / 8.0)
FULL_BAND = (1.0 / 512.0, 1.0 / 8.0)
SHAPES = ("gauss-8", "two-gauss", "chain", "vitrea", "exponential")


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
        # The QR reduction depends only on the basis columns, which are the real row's; carrying it
        # across saves re-factoring a 60 000 × 41 block for every kernel and every smoothness
        # weight in the sweep.
        out.append({"name": r["name"], "A": r["A"], "y": y,
                    "QR": r.get("QR"), "Q": r.get("Q")})
    return out


def errors(nodes, c, c_true):
    """The three errors every synthetic is scored by, and the band each MTF error was taken on."""
    s_rms, s_worst, _, _, _, s_cov = R.rel_mtf_error(nodes, c, c_true, band=SHARP_BAND)
    h_rms, h_worst, _, _, _, h_cov = R.rel_mtf_error(nodes, c, c_true, band=FULL_BAND)
    wt = E.widths_of_profile(nodes, c_true)
    wr = E.widths_of_profile(nodes, c)
    return {"sharp": s_rms, "sharpCov": s_cov, "full": h_rms, "fullCov": h_cov,
            "hwhm": abs(wr["sigmaHwhm"] / wt["sigmaHwhm"] - 1.0),
            "rms": abs(wr["sigmaRms"] / wt["sigmaRms"] - 1.0),
            "hwhmTrue": wt["sigmaHwhm"], "hwhmRead": wr["sigmaHwhm"],
            "rmsTrue": wt["sigmaRms"], "rmsRead": wr["sigmaRms"]}


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(HERE, "synth.txt"))
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
    e("through the 8-bit sRGB step. So the modulation the reader has to work with is the modulation")
    e("the real file carries.")
    e("")
    e("TWO MTF BANDS, and the second one is the load-bearing one. `S` is the RMS relative error over")
    e("the brief's band, 1/64..1/8 cycles per device px; `F` is the same over 1/512..1/8, which is")
    e("where a kernel tens of device px wide actually carries modulation. Both are taken only at the")
    e("frequencies where the KNOWN kernel's own modulation is at least 1 %, since a relative error")
    e("against a modulation of 10⁻⁵ is a statement about arithmetic and not about a kernel; the")
    e("fraction of each band that leaves is printed beside it as `cov`. On the brief's band alone a")
    e("kernel of σ 13 device px has essentially nothing left to be right or wrong about — which is")
    e("the first thing this reader has to say about how the wave's earlier widths were compared.")
    e("")

    cases = []
    for comp, scale, band in CASES:
        pkey = f"{'1x' if scale == 1 else '2x'}-light"
        profile, _, _ = L.PROFILES[pkey]
        nodes = E.radial_nodes(EXTENT[scale], NODES)
        cell, rows = R.assemble("web", profile, scale, comp, band, nodes, comps)
        if len(rows) < 4:
            e(f"   {comp} {scale:.0f}x: only {len(rows)} rows — skipped")
            continue
        cases.append((comp, scale, band, nodes, rows, known_kernels(nodes, comp, scale, band, m)))

    e("### 1. The smoothness weight, chosen once and frozen")
    e("")
    e(f"   {'lambda':>9} | " + " | ".join(f"{k:>21}" for k in SHAPES))
    e("   " + "-" * 9 + "-+-" + "-+-".join("-" * 21 for _ in SHAPES))
    score = {}
    for lam in LAMBDAS:
        per_shape = {k: [] for k in SHAPES}
        for comp, scale, band, nodes, rows, kernels in cases:
            for label, c_true in kernels.items():
                syn = synth_rows(rows, nodes, c_true)
                fit = E.joint_profile(syn, nodes, lam=lam)
                per_shape[label.split(" ")[0]].append(errors(nodes, fit["c"], c_true))
        cols = []
        allv = []
        for k in SHAPES:
            v = per_shape[k]
            allv.extend(v)
            cols.append(f"F{np.mean([x['full'] for x in v]) * 100:5.1f}%"
                        f" H{np.mean([x['hwhm'] for x in v]) * 100:5.1f}%"
                        f" R{np.mean([x['rms'] for x in v]) * 100:5.1f}%")
        score[lam] = float(np.mean([x["full"] + x["hwhm"] + x["rms"] for x in allv]))
        e(f"   {lam:9.5f} | " + " | ".join(cols))
    best = min(score, key=lambda k: score[k])
    e("")
    e("   `F` is the MTF error over 1/512..1/8, `H` the half-maximum width error, `R` the second")
    e("   moment's. The weight is chosen on their sum, averaged over every shape and every case:")
    e("   " + "  ".join(f"λ {lam}: {score[lam] * 100:.1f}%" for lam in LAMBDAS))
    e("")
    e(f"   CHOSEN: λ = {best}. Frozen from here — the control and the reference are read at it.")

    e("")
    e("### 2. Per case and per shape, at the chosen weight")
    e("")
    e(f"   {'surface':>9} {'sc':>3} {'rows':>4} {'kernel':>26} {'S':>7} {'cov':>5}"
      f" {'F':>7} {'cov':>5} {'HWHM t/r':>15} {'RMSσ t/r':>15}")
    for comp, scale, band, nodes, rows, kernels in cases:
        for label, c_true in kernels.items():
            syn = synth_rows(rows, nodes, c_true)
            fit = E.joint_profile(syn, nodes, lam=best)
            x = errors(nodes, fit["c"], c_true)
            e(f"   {comp:>9} {scale:3.0f} {len(rows):4d} {label:>26}"
              f" {x['sharp'] * 100:6.1f}% {x['sharpCov']:5.2f}"
              f" {x['full'] * 100:6.1f}% {x['fullCov']:5.2f}"
              f" {x['hwhmTrue']:7.3f}/{x['hwhmRead']:7.3f}"
              f" {x['rmsTrue']:7.3f}/{x['rmsRead']:7.3f}")
    e("")
    e(f"CHOSEN LAMBDA = {best}")
    text = "\n".join(lines)
    print(text)
    open(args.out, "w").write(text + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
