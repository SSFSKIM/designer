"""W26 G1b — the reference's point spread, recovered without a shape assumption, per surface per scale.

RUN ONLY AFTER THE CONTROL PASSES. `g1b-control.py` holds reader E against the kernel vitrea itself
draws; this script reads Apple's. Both use the same rows, the same band, the same radial grid and
the same frozen smoothness weight, so the only difference between the two answers is the material.

WHAT IS REPORTED per surface and scale, and why each is here rather than a single width.

  * **The radial profile**, as text. It is the answer; everything below is a reduction of it.
  * **The MTF** at named frequencies from 1/512 to 1/4 cycles per device px. A kernel IS its
    modulation transfer as far as any backdrop can tell, and the frequencies a backdrop carries are
    exactly the frequencies at which its width was ever identified.
  * **Three Gaussian-equivalent widths** — the second moment, the half maximum, and the σ whose MTF
    best matches K's over a band — together with how badly that last Gaussian misses. W26 G1 §7.5
    found the same surface reading 8.4 and 19.5 device px through two backdrops; if a single
    Gaussian misses K's MTF by tens of per cent then those two numbers were never the same
    statistic and the disagreement needs no further explanation.
  * **The best two-Gaussian approximation and its residual**, which is what every earlier reader in
    this wave was fitting, measured against what is actually there.
  * **Whether vitrea's own mechanism can match K**: a sharp Gaussian plus a chain level blurred by a
    Gaussian, which is `wgsl/optics.ts`'s composite once `heavyTapPlan` has chosen a level. If it
    can, the σ it needs is the constant the material would name.
  * **Vitrea's own K at the same rows**, read the same way, so the gap is one comparison of two
    profiles rather than of two projections onto different bases.

SENSITIVITY IS PART OF THE READING, not an appendix. The depth band, the backdrop's continuation
outside the 320 × 200 canvas and the presence of the two rows most likely to break the affine model
(`photo`, which is not neutral, and `impulse`, whose 1x modulation is about one display code) are
each varied and the answer re-reported. A width that moves under any of them is a width the bed
cannot carry.
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

EXTENT = 96.0
NODES = 40
FREQS = np.array([1 / 512, 1 / 256, 1 / 192, 1 / 128, 1 / 96, 1 / 64, 1 / 48, 1 / 32,
                  1 / 24, 1 / 16, 1 / 12, 1 / 8, 1 / 6, 1 / 4])
FULL_BAND = (1.0 / 512.0, 1.0 / 8.0)
CASES = (("rrect-md", 1.0, (16.0, 48.0)), ("rrect-md", 2.0, (16.0, 48.0)),
         ("rrect-lg", 1.0, (16.0, 80.0)), ("rrect-lg", 2.0, (16.0, 80.0)))


def chain_profiles(nodes):
    return {lv: TRUTH.chain_profile(lv, nodes) for lv in (2, 3, 4, 5)}


def read(source, profile, scale, comp, band, nodes, comps, lam, backdrops=R.BACKDROPS,
         pad="edge"):
    cell, rows = R.assemble(source, profile, scale, comp, band, nodes, comps,
                            backdrops=backdrops, pad=pad)
    if len(rows) < 4:
        return None, rows
    return E.joint_profile(rows, nodes, lam=lam), rows


def describe(nodes, c, cp):
    w = E.widths_of_profile(nodes, c)
    s_mtf, rel_mtf, *_ = E.sigma_matching_mtf(nodes, c, band=FULL_BAND, n=31)
    two = E.fit_two_gaussians(nodes, c)
    mech = E.fit_vitrea_mechanism(nodes, c, cp, band=FULL_BAND)
    tail = float(E._masses(nodes)[-4:] @ c[-4:])
    return {"w": w, "sMtf": s_mtf, "relMtf": rel_mtf, "two": two, "mech": mech, "tail": tail}


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--lam", type=float, required=True)
    ap.add_argument("--out", default=os.path.join(HERE, "reference.txt"))
    ap.add_argument("--dark", action="store_true", help="also read the dark standard on rrect-md")
    args = ap.parse_args(argv)
    comps = L.load_components()
    nodes = E.radial_nodes(EXTENT, NODES)
    cp = chain_profiles(nodes)
    lines = []
    e = lines.append
    e("W26 G1b — Apple's point spread, recovered non-parametrically, per surface per scale")
    e("=" * 100)
    e("")
    e(f"Smoothness weight λ = {args.lam}, chosen on synthetics and frozen. Radial grid: {NODES} hat")
    e(f"nodes out to {EXTENT:.0f} device px. Widths in DEVICE px, frequencies in cycles per device px.")
    e("")

    jobs = [(c, s, b, "light") for c, s, b in CASES]
    if args.dark:
        jobs.append(("rrect-md", 1.0, (16.0, 48.0), "dark"))
    store = {}

    e("### 1. The widths, reference and vitrea side by side")
    e("")
    e(f"  {'surface':>9} {'sc':>3} {'sch':>5} {'src':>9} {'rows':>4} {'RMSσ':>7} {'HWHMσ':>7}"
      f" {'MTFσ':>7} {'MTF miss':>9} {'2-gauss sharp/heavy@share':>27} {'resid':>7} {'tail':>6}")
    for comp, scale, band, scheme in jobs:
        pkey = f"{'1x' if scale == 1 else '2x'}-{scheme}"
        profile, _, _ = L.PROFILES[pkey]
        for source, label in (("native", "reference"), ("web", "vitrea")):
            fit, rows = read(source, profile, scale, comp, band, nodes, comps, args.lam)
            if fit is None:
                e(f"  {comp:>9} {scale:3.0f} {scheme:>5} {label:>9}  only {len(rows)} rows")
                continue
            d = describe(nodes, fit["c"], cp)
            store[(comp, scale, scheme, source)] = (fit, rows, d)
            t = d["two"]
            e(f"  {comp:>9} {scale:3.0f} {scheme:>5} {label:>9} {len(rows):4d}"
              f" {d['w']['sigmaRms']:7.3f} {d['w']['sigmaHwhm']:7.3f} {d['sMtf']:7.3f}"
              f" {d['relMtf'] * 100:8.1f}%"
              f" {t['sharp']:9.3f} /{t['heavy']:8.3f} @{t['share']:.3f}"
              f" {t['rel'] * 100:6.1f}% {d['tail'] * 100:5.1f}%")
    e("")
    e("`MTFσ` is the Gaussian whose modulation transfer best matches K's over 1/512..1/8; `MTF miss`")
    e("is how far that best single Gaussian still is from K, in RMS relative modulation. A large")
    e("miss means K has no Gaussian-equivalent width at all, and that two readings of it taken")
    e("through different backdrops were never measuring the same quantity.")
    e("")

    # ------------------------------------------------------------------ the MTF tables
    e("### 2. The modulation transfer, reference against vitrea")
    e("")
    e("   " + " ".join(f"{'1/' + str(int(round(1 / f))):>8}" for f in FREQS))
    for comp, scale, band, scheme in jobs:
        for source in ("native", "web"):
            key = (comp, scale, scheme, source)
            if key not in store:
                continue
            fit = store[key][0]
            mt = E.mtf_of_profile(nodes, fit["c"], FREQS)
            e(f"   {comp} {scale:.0f}x {scheme} {'reference' if source == 'native' else 'vitrea':>9}")
            e("   " + " ".join(f"{v:8.4f}" for v in mt))
    e("")

    # ------------------------------------------------------------------ the mechanism
    e("### 3. Can vitrea's mechanism draw K? A sharp Gaussian plus a chain level blurred to width")
    e("")
    e(f"  {'surface':>9} {'sc':>3} {'src':>9} {'level':>5} {'blur σ':>8} {'sharp σ':>8}"
      f" {'share':>6} {'MTF miss':>9}")
    for comp, scale, band, scheme in jobs:
        for source in ("native", "web"):
            key = (comp, scale, scheme, source)
            if key not in store:
                continue
            mech = store[key][2]["mech"]
            e(f"  {comp:>9} {scale:3.0f} {'reference' if source == 'native' else 'vitrea':>9}"
              f" {mech['level']:5d} {mech['blur']:8.3f} {mech['sharp']:8.3f}"
              f" {mech['share']:6.3f} {mech['relMtf'] * 100:8.1f}%")
    e("")
    e("`blur σ` is the residual Gaussian the chosen chain level would have to be blurred by — which")
    e("is exactly what `sizeHeavyTapSigma` names once `heavyTapPlan` has chosen the level. A miss")
    e("under about 10 % means the mechanism can carry K; the σ column is then the constant.")
    e("")

    # ------------------------------------------------------------------ families on the pixels
    e("### 3b. Four kernel FAMILIES, each fitted to the pixels, judged in quantisation steps")
    e("")
    e("The control's finding is that the free forty-parameter profile reaches a lower residual than")
    e("the kernel the material actually draws while getting its shape wrong, and that a scan over ONE")
    e("width does not: on the band where the drawn kernel is known the residual falls to a single")
    e("minimum at the LOD the material draws. So the families below are fitted to the PIXELS rather")
    e("than to a recovered profile, and the question each answers is how much of the file a shape")
    e("can explain — not how close it comes to a curve that was itself inferred.")
    e("")
    e("`resid` is the RMS over rows of each row's residual in units of its own 8-bit step. `free` is")
    e("the forty-parameter profile on the same rows and is a lower bound no shape can beat; the gap")
    e("between a family and `free` is what that family cannot describe.")
    e("")
    e(f"  {'surface':>9} {'sc':>3} {'src':>9} {'family':>28} {'parameters':>34} {'resid':>7}")
    for comp, scale, band, scheme in jobs:
        pkey = f"{'1x' if scale == 1 else '2x'}-{scheme}"
        profile, _, _ = L.PROFILES[pkey]
        for source in ("native", "web"):
            key = (comp, scale, scheme, source)
            if key not in store:
                continue
            fit, rows, _ = store[key]
            E.prepare_rows(rows, nodes)
            lab = "reference" if source == "native" else "vitrea"
            body = TRUTH.body_profile(nodes)

            def one_gauss(p):
                return E.gauss_profile(nodes, max(abs(p[0]), 0.05))

            def two_gauss(p):
                s1, s2 = max(abs(p[0]), 0.05), max(abs(p[1]), 0.05)
                w = 1.0 / (1.0 + math.exp(-p[2]))
                return (1 - w) * E.gauss_profile(nodes, s1) + w * E.gauss_profile(nodes, s2)

            def body_plus_gauss(p):
                """Vitrea's own composite: the BODY it already draws plus one Gaussian at a share."""
                s = max(abs(p[0]), 0.05)
                w = 1.0 / (1.0 + math.exp(-p[1]))
                return (1 - w) * body + w * E.gauss_profile(nodes, s)

            def body_plus_chain(p):
                """Vitrea's MECHANISM: the body plus a chain level blurred to σ, at a share.

                `heavyTapPlan` picks the level from σ and the residual Gaussian carries the rest, so
                the σ this returns is exactly what `sizeHeavyTapSigma` would have to name.
                """
                s = max(abs(p[0]), 0.5)
                w = 1.0 / (1.0 + math.exp(-p[1]))
                return (1 - w) * body + w * TRUTH.heavy_tap_profile(s, scale, nodes)

            fams = (
                ("one Gaussian", one_gauss, [[6.0], [14.0], [22.0]], lambda x: f"σ {abs(x[0]):.2f}"),
                ("two Gaussians", two_gauss,
                 [[2.0, 10.0, 0.0], [2.0, 20.0, 0.8], [4.0, 30.0, -0.8]],
                 lambda x: (f"sharp {abs(x[0]):.2f} heavy {abs(x[1]):.2f} "
                            f"@{1 / (1 + math.exp(-x[2])):.3f}")),
                ("vitrea body + Gaussian", body_plus_gauss,
                 [[10.0, 0.0], [20.0, 0.8], [30.0, -0.5]],
                 lambda x: (f"heavy σ {abs(x[0]):.2f} @{1 / (1 + math.exp(-x[1])):.3f}")),
                ("vitrea body + chain tap", body_plus_chain,
                 [[10.0, 0.0], [20.0, 0.8], [30.0, -0.5]],
                 lambda x: (f"sizeHeavyTapSigma {abs(x[0]):.2f} @{1 / (1 + math.exp(-x[1])):.3f}")),
            )
            for name, build, starts, fmt in fams:
                out = E.fit_family(rows, nodes, build, starts)
                if out is None:
                    continue
                e(f"  {comp:>9} {scale:3.0f} {lab:>9} {name:>28} {fmt(out['x']):>34}"
                  f" {out['resid']:7.3f}")
                store.setdefault("fam", {})[(comp, scale, scheme, source, name)] = out
            free, _ = E.profile_residual(rows, fit["c"])
            e(f"  {comp:>9} {scale:3.0f} {lab:>9} {'free profile (40 nodes)':>28} {'':>34}"
              f" {free:7.3f}")
    e("")

    # ------------------------------------------------------------------ per-row residuals
    e("### 4. Per-row residual, in units of the row's own quantisation step")
    e("")
    for comp, scale, band, scheme in jobs:
        for source in ("native", "web"):
            key = (comp, scale, scheme, source)
            if key not in store:
                continue
            fit = store[key][0]
            e(f"   {comp} {scale:.0f}x {scheme} {'reference' if source == 'native' else 'vitrea'}")
            e("      " + "   ".join(f"{p['name']}: {p['rmsCodes']:.2f}" for p in fit["per"]))
    e("")

    # ------------------------------------------------------------------ sensitivity
    e("### 5. Sensitivity — the same reading under the choices that could have made it")
    e("")
    e("The instrument here is the one that PASSED the control — vitrea's own mechanism family fitted")
    e("to the pixels — not the free profile, whose shape the control showed is not determined.")
    e("`σ` is `sizeHeavyTapSigma`, `share` the heavy component's weight, `resid` the fit in")
    e("quantisation steps, and `freeRMSσ` the free profile's second moment on the same rows.")
    e("")
    e(f"  {'surface':>9} {'sc':>3} {'variant':>28} {'rows':>4} {'σ':>8} {'share':>7} {'resid':>7}"
      f" {'freeRMSσ':>8}")
    variants = [
        ("as read", dict()),
        ("band 24..: deeper", dict(band_lo=24.0)),
        ("band 32..: deeper still", dict(band_lo=32.0)),
        ("backdrop tiled outside canvas", dict(pad="wrap")),
        ("without photo", dict(drop=("photo",))),
        ("without impulse", dict(drop=("impulse",))),
        ("without the fine checkerboards", dict(drop=("checkerboard-4", "checkerboard-8"))),
        ("checkerboards only", dict(keep=("checkerboard-64", "checkerboard-32", "checkerboard",
                                          "checkerboard-8", "checkerboard-4"))),
    ]
    for comp, scale, band, scheme in jobs:
        if scheme != "light":
            continue
        pkey = f"{'1x' if scale == 1 else '2x'}-{scheme}"
        profile, _, _ = L.PROFILES[pkey]
        for name, opt in variants:
            bd = opt.get("keep") or tuple(b for b in R.BACKDROPS if b not in opt.get("drop", ()))
            bb = (opt.get("band_lo", band[0]), band[1])
            cell, rows = R.assemble("native", profile, scale, comp, bb, nodes, comps,
                                    backdrops=bd, pad=opt.get("pad", "edge"))
            if len(rows) < 4:
                e(f"  {comp:>9} {scale:3.0f} {name:>28}  only {len(rows)} rows")
                continue
            E.prepare_rows(rows, nodes)
            body = TRUTH.body_profile(nodes)

            def mech(p, scale=scale, body=body):
                w = 1.0 / (1.0 + math.exp(-p[1]))
                return (1 - w) * body + w * TRUTH.heavy_tap_profile(max(abs(p[0]), 0.5), scale,
                                                                   nodes)

            out = E.fit_family(rows, nodes, mech, [[9.0, 0.0], [14.0, 0.8], [20.0, -0.5]])
            fit = E.joint_profile(rows, nodes, lam=args.lam)
            w = E.widths_of_profile(nodes, fit["c"])
            e(f"  {comp:>9} {scale:3.0f} {name:>28} {len(rows):4d}"
              f" {abs(out['x'][0]):8.2f} {1 / (1 + math.exp(-out['x'][1])):7.3f}"
              f" {out['resid']:7.3f} {w['sigmaRms']:8.2f}")
    e("")

    # ------------------------------------------------------------------ the profiles
    e("### 6. The profiles, normalised to their own peak")
    e("")
    for comp, scale, band, scheme in jobs:
        for source in ("native", "web"):
            key = (comp, scale, scheme, source)
            if key not in store:
                continue
            e(f"   {comp} {scale:.0f}x {scheme} — "
              f"{'REFERENCE' if source == 'native' else 'vitrea 0.14.0'}")
            lines.extend(R.fmt_profile(nodes, store[key][0]["c"]))
            e("")
    text = "\n".join(lines)
    print(text)
    open(args.out, "w").write(text + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
