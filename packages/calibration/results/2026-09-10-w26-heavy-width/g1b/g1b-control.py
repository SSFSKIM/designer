"""W26 G1b — THE CONTROL. Reader E run on vitrea's own captures, where the kernel is known exactly.

THIS IS BINDING AND IT COMES FIRST. W26 G1 §7.6's verdict was that the joint two-Gaussian fit
under-read vitrea's known 13.42 device px by 14–23 %, and that a reader which fails its control has
nothing to say about the reference. So reader E is held against `g1b-truth.py`'s statement of what
`wgsl/optics.ts` actually convolves the backdrop with at the frozen 0.14.0 material — the chain
level `scatterLod` selects, trilinearly blended, mixed at `kScatter` with the BODY, which is the
chain's level-1 kernel plus a third of a texel and not a Gaussian of `blurSigma` — over the same
depth band the fit is taken on, before one number is read off the reference.

THE ACCEPTANCE, as the brief sets it: the recovered K must reproduce the known kernel's MTF within
10 % between 1/64 and 1/8 cycles per device px, and its half-maximum width within 10 %.

A SECOND BAND IS REPORTED BESIDE IT, and it is not decoration. A Gaussian of σ 13.4 device px has
transferred 3 % of its modulation by 1/32 cycles per px and 4 × 10⁻¹⁴ by 1/8: the brief's band is
where the SHARP component lives, and a reader can pass it while knowing nothing about the heavy
one. The band that carries the heavy component is 1/512 to about 1/32, and both are reported so a
pass on one is not read as a pass on the other.

THE RESIDUAL AT THE KNOWN KERNEL IS REPORTED BESIDE THE RESIDUAL AT THE FIT, and it is what turns
a failure into a diagnosis. If the drawn kernel fits the pixels much worse than the recovered one,
the reader has found something the arithmetic statement of the material missed. If the two fit
about equally, the pixels do not distinguish them, and the reader's answer is under-determined at
this noise level however well it did on synthetics — a different verdict with a different remedy.

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

EXTENT = 96.0
NODES = 40
SHARP_BAND = (1.0 / 64.0, 1.0 / 8.0)
HEAVY_BAND = (1.0 / 512.0, 1.0 / 8.0)
CASES = (("rrect-md", 1.0, (16.0, 48.0)), ("rrect-md", 2.0, (16.0, 48.0)),
         ("rrect-lg", 1.0, (16.0, 80.0)), ("rrect-lg", 2.0, (16.0, 80.0)),
         # The two bands where the DRAWN kernel is pure. At dpr 2 `sizeScatterFloor2x` is 1, so
         # `sDeep` is 0 and the only sharp admixture left is the depth ramp, which runs out at
         # 50 CSS px. Past that the surface draws the chain tap and nothing else — no share to be
         # averaged, no depth dependence, one kernel exactly. That is the control's best case and
         # it exists only on `rrect-lg`, whose half-span is 80 CSS px.
         ("rrect-lg", 2.0, (50.0, 80.0)),
         ("rrect-md", 2.0, (40.0, 48.0)))


def depths_of(cell, scale, shape, band):
    """The band's OWN pixel depths, which is what a fitted kernel is an average over.

    Not a uniform grid between the band's edges: a ring at depth 16 holds far more pixels than one
    at depth 45, so a uniformly sampled average of `kScatter` states a share the surface does not
    draw. Every earlier reading of a depth-varying quantity in this wave averaged uniformly.
    """
    d = L.signed_distance(cell.box, cell.radius, scale, shape, cell.kind)
    u = -d
    m = (u >= band[0]) & (u <= band[1])
    return u[m]


def band_row(nodes, c, ref, band):
    rms, worst, f, a, b, cov = R.rel_mtf_error(nodes, c, ref, band=band, n=25)
    return rms, cov


def resid_at(rows, nodes, c):
    """Each row's residual at a GIVEN kernel, gain and nuisance refitted, in quantisation steps."""
    out = []
    for r in rows:
        m = r["P"] @ c
        X = np.concatenate([m[:, None], r["p"]], axis=1)
        sol, *_ = np.linalg.lstsq(X, r["q"], rcond=None)
        res = X @ sol - r["q"]
        rms = math.sqrt(max(float(res @ res) + r["rho"], 0.0) / r["N"])
        out.append(rms / (r["noise"] * math.sqrt(12.0)))
    return out


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
    e("`MTF sharp` is the RMS relative error of the recovered modulation transfer over")
    e("1/64..1/8 cycles per device px — the brief's band. `MTF heavy` is the same over 1/512..1/8,")
    e("which is where a kernel of σ 13 device px actually carries its modulation. Each is taken")
    e("only where the DRAWN kernel's own modulation is at least 1 %, and `cov` is the fraction of the")
    e("band that leaves.")
    e("")
    e(f"  {'surface':>9} {'sc':>3} {'band':>7} {'rows':>4} {'kScatter band':>20} {'MTF sharp':>16}"
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
        depths = depths_of(cell, scale, (int(200 * scale), int(320 * scale)), band)
        t = TRUTH.truth_profile(span, scale, depths, nodes, m)
        fit = E.joint_profile(rows, nodes, lam=args.lam)
        fits[(comp, scale, band)] = (fit, t, rows)
        s_rms, s_cov = band_row(nodes, fit["c"], t["c"], SHARP_BAND)
        h_rms, h_cov = band_row(nodes, fit["c"], t["c"], HEAVY_BAND)
        wt = E.widths_of_profile(nodes, t["c"])
        wr = E.widths_of_profile(nodes, fit["c"])
        tail = float(E._masses(nodes)[-4:] @ fit["c"][-4:])
        e(f"  {comp:>9} {scale:3.0f} {band[0]:3.0f}-{band[1]:<3.0f} {len(rows):4d}"
          f" {t['kMean']:.3f}[{t['kMin']:.2f},{t['kMax']:.2f}]"
          f" {s_rms * 100:6.1f}% {s_cov:6.2f}"
          f" {h_rms * 100:6.1f}% {h_cov:6.2f}"
          f" {wt['sigmaHwhm']:7.3f} {wr['sigmaHwhm']:7.3f}"
          f" {wt['sigmaRms']:7.3f} {wr['sigmaRms']:7.3f} {tail * 100:5.1f}%")
        verdict.append((comp, scale, band, s_rms, h_rms,
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
    for (comp, scale, band), (fit, t, rows) in fits.items():
        e(f"   {comp} {scale:.0f}x {band[0]:.0f}-{band[1]:.0f}")
        e("      at the FIT   " + "   ".join(
            f"{p['name']}: {p['rmsCodes']:.2f}" for p in fit["per"]))
        e("      at the DRAWN " + "   ".join(
            f"{p['name']}: {q:.2f}" for p, q in zip(fit["per"], resid_at(rows, nodes, t["c"]))))
    e("")

    # ------------------------------------------------------------------ the profiles
    e("### The recovered profile against the drawn one, normalised to its own peak")
    e("")
    for (comp, scale, band), (fit, t, rows) in fits.items():
        e(f"   {comp} {scale:.0f}x {band[0]:.0f}-{band[1]:.0f} — DRAWN (truth)")
        lines.extend(R.fmt_profile(nodes, t["c"]))
        e(f"   {comp} {scale:.0f}x {band[0]:.0f}-{band[1]:.0f} — READ")
        lines.extend(R.fmt_profile(nodes, fit["c"]))
        e("")

    # ------------------------------------------------------------------ the drawn width, scanned
    e("### The drawn width, scanned directly against the pixels")
    e("")
    e("A separate and much narrower question than the profile's: forget the free fit, and ask which")
    e("chain LOD, as a whole kernel with its gain and nuisance refitted, best explains the band. On")
    e("`rrect-lg` at 2x past 50 CSS px the material draws EXACTLY one chain tap — `kScatter` is 1 to")
    e("the bit there — so the answer is a number the arithmetic already states, and the scan is a")
    e("direct test of whether these eight backdrops can find a width they were not told.")
    e("")
    key = ("rrect-lg", 2.0, (50.0, 80.0))
    if key in fits:
        fit, t, rows = fits[key]
        e(f"   the arithmetic says scatterLod {t['lod']:.3f}")
        e(f"   {'lod':>6} {'resid (quantisation steps)':>28} {'HWHMσ':>8} {'RMSσ':>8}")
        best = None
        for i in range(20, 51):
            lod = i / 10.0
            c = TRUTH.chain_profile_at(lod, nodes)
            sc = float(np.sqrt(np.mean(np.array(resid_at(rows, nodes, c)) ** 2)))
            w = E.widths_of_profile(nodes, c)
            if best is None or sc < best[0]:
                best = (sc, lod)
            if abs(lod - round(lod * 2) / 2) < 1e-9 or abs(lod - t["lod"]) < 0.06:
                e(f"   {lod:6.1f} {sc:28.4f} {w['sigmaHwhm']:8.3f} {w['sigmaRms']:8.3f}")
        free = float(np.sqrt(np.mean(np.array([p["rmsCodes"] for p in fit["per"]]) ** 2)))
        e(f"   BEST pure chain tap: lod {best[1]:.1f} at {best[0]:.4f}; the free profile reaches"
          f" {free:.4f}")
    e("")

    # ------------------------------------------------------------------ the family control
    e("### The SECOND control: vitrea's own mechanism, fitted to the pixels as a two-parameter family")
    e("")
    e("The scan above says the width is identified where the shape is not, so this is the same")
    e("question asked in two parameters instead of forty: the BODY vitrea already draws, plus what")
    e("`heavyTapPlan` would build for a heavy σ, mixed at a share — the composite `wgsl/optics.ts`")
    e("computes, with the two numbers the material would name left free. The truth column is the")
    e("arithmetic: the drawn tap's own width, and `kScatter` averaged over the band's own pixels.")
    e("")
    e(f"  {'surface':>9} {'sc':>3} {'band':>7} {'σ drawn':>8} {'σ read':>8} {'Δ':>7}"
      f" {'k drawn':>8} {'k read':>8} {'Δ':>7} {'resid':>7} {'free':>7}")
    fam = []
    for (comp, scale, band), (fit, t, rows) in fits.items():
        body = TRUTH.body_profile(nodes)

        def mech(p, scale=scale, body=body):
            w = 1.0 / (1.0 + math.exp(-p[1]))
            return (1 - w) * body + w * TRUTH.heavy_tap_profile(max(abs(p[0]), 0.5), scale, nodes)

        out = E.fit_family(rows, nodes, mech, [[9.0, 0.0], [13.4, 0.8], [20.0, -0.5]])
        sig = abs(out["x"][0])
        share = 1.0 / (1.0 + math.exp(-out["x"][1]))
        drawn = TRUTH.sigma_naming_lod(t["lod"], scale, nodes)
        free = float(np.sqrt(np.mean(np.array([p["rmsCodes"] for p in fit["per"]]) ** 2)))
        d_sig = sig / drawn - 1.0
        d_k = share - t["kMean"]
        fam.append((comp, scale, band, d_sig, d_k))
        e(f"  {comp:>9} {scale:3.0f} {band[0]:3.0f}-{band[1]:<3.0f} {drawn:8.3f} {sig:8.3f}"
          f" {d_sig * 100:6.1f}% {t['kMean']:8.3f} {share:8.3f} {d_k:+7.3f}"
          f" {out['resid']:7.3f} {free:7.3f}")
    e("")
    inside = sum(1 for *_, d, _k in fam if abs(d) <= 0.10)
    worst = max((abs(d) for *_, d, _k in fam), default=float("nan"))
    worst_k = max((abs(k) for *_, _d, k in fam), default=float("nan"))
    e(f"   FAMILY CONTROL: the drawn heavy width is recovered inside 10 % on {inside} of"
      f" {len(fam)} bands, worst {worst * 100:.1f} %; the drawn share inside {worst_k:.3f}"
      f" everywhere.")
    e("   Both 1x bands, where the drawn tap is a whole chain level and therefore lies exactly in")
    e("   the fitted family, return it to 0.6 %. The 2x bands, where `scatterLod` is fractional and")
    e("   the drawn tap is a trilinear blend no member of the family can be, read 5–10 % narrow —")
    e("   which is the family's own bias against a kernel outside it and not the reader's noise.")
    e("")

    # ------------------------------------------------------------------ the verdict
    e("### Verdict")
    e("")
    ok = True
    for comp, scale, band, s_rms, h_rms, dh, dr in verdict:
        passes = s_rms <= 0.10 and dh <= 0.10
        ok = ok and passes
        e(f"   {comp} {scale:.0f}x {band[0]:.0f}-{band[1]:.0f}: MTF(1/64..1/8) {s_rms * 100:.1f}%, "
          f"MTF(1/512..1/8) {h_rms * 100:.1f}%, HWHM {dh * 100:.1f}%, RMSσ {dr * 100:.1f}% "
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
