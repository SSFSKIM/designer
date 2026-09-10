"""W26 G1c — the ladder read with the family reader, the control at every rung, and the two fits.

THE INSTRUMENT IS G1b's AND IS NOT RE-DERIVED HERE (W26 Decision Log 5 (a)). `w26blib.py` and
`w26brows.py` are imported from `../g1b/` and not edited: the composite `wgsl/optics.ts` computes —
the body vitrea draws, plus `heavyTapPlan`'s kernel for a heavy σ, mixed at a share — fitted to the
PIXELS jointly across every thick untinted backdrop of one surface, with a per-backdrop gain and a
low-order nuisance in depth, at the smoothness weight λ = 0.003 that `g1b-synth.py` chose on
synthetics and froze.

THE ROWS ARE HOLDOUT-FREE, and that is a change from G1b. G1b was a spike and read all eight
backdrops, three of which — `checkerboard__rrect-lg`, `hc-text__rrect-md`, `photo__rrect-lg` — are
holdout scenes. This child FITS two constants, so X3 applies and those three rows are dropped from
every reading here, including the re-reading of the reference. §1 of the findings measures what
dropping them costs.

THE CONTROL IS AT EVERY RUNG, not once. The rung names σ, the pyramid builds `heavyTapPlan(σ)`, and
the reader is asked to give σ back. At dpr 1 and at dpr 2 alike the plan's σ in level-0 texels is
the device-px number the profile names (`heavySigmaCss` = σ/dpr and `texelsPerCss` = dpr), so the
drawn kernel is EXACTLY a member of the fitted family at both scales — which is the difference from
G1b, where the 2x tap was a trilinear blend outside it and the reader read 5–10 % narrow. The bias
per rung is reported, and the mapping from the named constant to the read width is what the
reference's reading is inverted through.

    g1c-read.py [--lam 0.003] [--rungs c0,d8,...] [--out FILE]
"""

import argparse
import importlib.util
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
G1B = os.path.abspath(os.path.join(HERE, "..", "g1b"))
sys.path.insert(0, G1B)
import w26blib as E  # noqa: E402
import w26brows as R  # noqa: E402
import w25lib as L  # noqa: E402

_spec = importlib.util.spec_from_file_location("g1btruth", os.path.join(G1B, "g1b-truth.py"))
TRUTH = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(TRUTH)

SCRATCH = "/Users/new/.claude/jobs/5c70e47f/tmp/w26/g1c"
# The rung the fits below land on; §3 states how it was arrived at.
CANDIDATE = "d9"
EXTENT = 96.0
NODES = 40

# Holdout-free rows, per surface. `checkerboard__rrect-lg`, `hc-text__rrect-md` and
# `photo__rrect-lg` are the three the split puts in the holdout and they are not read here.
ROWS = {
    "rrect-md": ("impulse", "checkerboard-64", "checkerboard-32", "checkerboard",
                 "checkerboard-8", "checkerboard-4", "photo"),
    "rrect-lg": ("impulse", "checkerboard-64", "checkerboard-32",
                 "checkerboard-8", "checkerboard-4", "hc-text"),
}
BANDS = {"rrect-md": (16.0, 48.0), "rrect-lg": (16.0, 80.0)}
# (surface, scale, scheme) — `rrect-lg` has no dark probe fixtures on this bed.
CELLS = (("rrect-md", 1.0, "light"), ("rrect-lg", 1.0, "light"),
         ("rrect-md", 2.0, "light"), ("rrect-lg", 2.0, "light"),
         ("rrect-md", 1.0, "dark"), ("rrect-md", 2.0, "dark"))
# The rungs, and the (1x, 2x) anchors each names.
RUNGS = (("c0", 13.418, 0.0), ("d8", 8.0, 8.0), ("d9", 9.0, 9.0), ("d10", 10.0, 10.0),
         ("d11", 11.0, 11.0), ("x98", 9.0, 8.0), ("x910", 9.0, 10.0), ("z001", 13.418, 0.001))


_TAP = {}
# The σ grid the scan below runs on, in device px. 0.05 is a twentieth of a texel — finer than the
# fit resolves, and fine enough that `heavyTapPlan`'s change of chain level, which moves the SHAPE
# discontinuously while the width stays continuous, is never straddled by more than one step.
SIGMA_GRID = np.round(np.arange(3.0, 30.0001, 0.05), 2)


def tap(sigma, scale, nodes):
    """`heavyTapPlan`'s kernel for a heavy σ, memoised on σ to two decimals."""
    key = (round(float(sigma), 2), float(scale))
    if key not in _TAP:
        _TAP[key] = TRUTH.heavy_tap_profile(key[0], scale, nodes)
    return _TAP[key]


SHARE_GRID = np.round(np.arange(0.0, 1.0001, 0.005), 3)


def row_stats(r, B, T):
    """The five inner products a row needs, with its nuisance projected out of everything.

    Everything below is closed form on these: for a shared share `w` the model column is
    `(1 − w)·B̃ + w·T̃`, its best per-row gain is `⟨m, ỹ⟩ / ⟨m, m⟩`, and the residual follows without
    ever forming a design matrix again.
    """
    Q, _ = np.linalg.qr(r["p"])
    Bt = r["P"] @ B
    Tt = r["P"] @ T
    Bt = Bt - Q @ (Q.T @ Bt)
    Tt = Tt - Q @ (Q.T @ Tt)
    y = r["q"] - Q @ (Q.T @ r["q"])
    return (float(Bt @ Bt), float(Bt @ Tt), float(Tt @ Tt),
            float(Bt @ y), float(Tt @ y), float(y @ y))


def score_at(rows, stats, w):
    """The fit's objective at one share, in units of each row's own quantisation step.

    ONE share across every backdrop, one gain PER backdrop — which is the model, and which the
    first build of this scan got wrong by solving both mixture coefficients per row. Given a share
    that free per-row split lets each backdrop choose its own mixture, and it does: every row runs
    to a share near 1 and the fitted width follows. The share is a property of the material at that
    depth and the gain is a property of the backdrop's own transmission, so exactly one of them is
    allowed to vary by row.
    """
    total = 0.0
    gains = []
    for r, (bb, bt, tt, by, ty, yy) in zip(rows, stats):
        mm = (1 - w) ** 2 * bb + 2 * w * (1 - w) * bt + w * w * tt
        my = (1 - w) * by + w * ty
        g = my / mm if mm > 1e-300 else 0.0
        if g < 0:
            g = 0.0
        sse = yy - 2 * g * my + g * g * mm + r["rho"]
        total += (math.sqrt(max(sse, 0.0) / r["N"]) / (r["noise"] * math.sqrt(12.0))) ** 2
        gains.append(g)
    return math.sqrt(total / len(rows)), gains


def fit_tap_scan(rows, nodes, body, scale, sigmas=SIGMA_GRID):
    """The family fit as a scan over (σ, share), every inner quantity in closed form.

    THE FIT IS SEPARABLE AND WAS BEING SEARCHED AS IF IT WERE NOT. The model is
    `g_b · [(1 − w)·body + w·tap(σ)]` — one kernel, one share, a gain per backdrop. The gain is
    linear, so it is solved rather than searched; only σ and the share are scanned, on grids finer
    than either is resolved to. G1b fitted the same family by Nelder-Mead over both, which is
    correct and about two orders of magnitude slower — slow enough that eight rungs over six cells
    did not finish inside an hour. The answers agree to a twentieth of a device px, and this one
    also returns the residual as a function of σ, which is the curve the ladder's condition is read
    from.
    """
    best = None
    curve = []
    for sigma in sigmas:
        T = tap(float(sigma), scale, nodes)
        stats = [row_stats(r, body, T) for r in rows]
        local = None
        for w in SHARE_GRID:
            score, gains = score_at(rows, stats, float(w))
            if local is None or score < local[0]:
                local = (score, float(w), gains)
        curve.append((float(sigma), local[0], local[1]))
        if best is None or local[0] < best[0]:
            best = (local[0], float(sigma), local[1], local[2])
    score, sigma, share, gains = best
    return {"sigma": sigma, "share": share, "resid": score, "curve": curve, "gains": gains}


def read_cell(source, comp, scale, scheme, nodes, comps, lam, rung=None):
    """One (surface, scale, scheme) read with the family reader. `source` is 'native' or 'web'."""
    pkey = f"{'1x' if scale == 1 else '2x'}-{scheme}"
    profile, _, _ = L.PROFILES[pkey]
    root = os.path.join(SCRATCH, rung, "web-captures") if rung else None
    cell, rows = R.assemble(source, profile, scale, comp, BANDS[comp], nodes, comps,
                            backdrops=ROWS[comp], root=root)
    if len(rows) < 4:
        return None, rows, cell
    E.prepare_rows(rows, nodes)
    out = fit_tap_scan(rows, nodes, TRUTH.body_profile(nodes), scale)
    out["rows"] = rows
    return out, rows, cell


def drawn_share(cell, comp, scale, band, nodes, m):
    """`kScatter` over the band's OWN pixels — the share the material draws there."""
    shape = (int(200 * scale), int(320 * scale))
    d = -L.signed_distance(cell.box, cell.radius, scale, shape, cell.kind)
    u = d[(d >= band[0]) & (d <= band[1])]
    ks = np.array([TRUTH.k_scatter(TRUTH.SPANS[comp], scale, x, m) for x in u])
    return float(ks.mean())


SHARP_GRID = np.round(np.arange(0.6, 4.001, 0.05), 2)
HEAVY_GRID = np.round(np.arange(4.0, 30.001, 0.25), 2)
_GAUSS = {}


def gauss(sigma, nodes):
    key = round(float(sigma), 2)
    if key not in _GAUSS:
        _GAUSS[key] = E.gauss_profile(nodes, key)
    return _GAUSS[key]


def two_gauss_read(rows, nodes):
    """The free two-Gaussian fit to the same pixels, scanned on the same separable argument.

    The share is linear given the two widths, so only the widths are scanned. This is the reader
    the wave's earlier children used, fitted across every backdrop at once instead of one — the
    sharp column is what W26 Decision Log 5 (e) asks to be recorded beside W25's.
    """
    best = None
    for s1 in SHARP_GRID:
        B = gauss(float(s1), nodes)
        for s2 in HEAVY_GRID:
            if s2 <= s1 * 1.5:
                continue
            T = gauss(float(s2), nodes)
            stats = [row_stats(r, B, T) for r in rows]
            local = None
            for w in SHARE_GRID:
                sc, _ = score_at(rows, stats, float(w))
                if local is None or sc < local[0]:
                    local = (sc, float(w))
            score, w = local
            if best is None or score < best[0]:
                best = (score, float(s1), float(s2), w)
    if best is None:
        return None
    score, s1, s2, w = best
    return {"sharp": s1, "heavy": s2, "share": w, "resid": score}


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--lam", type=float, default=0.003)
    ap.add_argument("--rungs", default=None)
    ap.add_argument("--out", default=os.path.join(HERE, "ladder.txt"))
    args = ap.parse_args(argv)
    comps = L.load_components()
    nodes = E.radial_nodes(EXTENT, NODES)
    m = TRUTH.material()
    want = set(args.rungs.split(",")) if args.rungs else None
    rungs = [r for r in RUNGS if want is None or r[0] in want]
    lines = []
    e = lines.append
    e("W26 G1c — the ladder, the control at every rung, and the reference re-read holdout-free")
    e("=" * 100)
    e("")
    e(f"Family reader, λ = {args.lam}, {NODES} radial nodes to {EXTENT:.0f} device px. Widths in")
    e("DEVICE px. Rows are holdout-free: `rrect-md` reads seven backdrops and `rrect-lg` six.")
    e("")

    # ------------------------------------------------------------------ the reference
    e("### 1. The reference, re-read on the holdout-free rows")
    e("")
    e(f"  {'surface':>9} {'sc':>3} {'sch':>6} {'rows':>4} {'σ':>8} {'share':>7} {'resid':>7}"
      f" {'2-gauss sharp/heavy@share':>30} {'G1b σ':>7}")
    G1B_SIGMA = {("rrect-md", 1.0, "light"): 9.11, ("rrect-lg", 1.0, "light"): 8.55,
                 ("rrect-md", 2.0, "light"): 7.92, ("rrect-lg", 2.0, "light"): 8.97,
                 ("rrect-md", 1.0, "dark"): 9.18}
    ref = {}
    for comp, scale, scheme in CELLS:
        out, rows, cell = read_cell("native", comp, scale, scheme, nodes, comps, args.lam)
        if out is None:
            e(f"  {comp:>9} {scale:3.0f} {scheme:>6}  only {len(rows)} rows")
            continue
        ref[(comp, scale, scheme)] = out
        tg = two_gauss_read(rows, nodes)
        prev = G1B_SIGMA.get((comp, scale, scheme))
        e(f"  {comp:>9} {scale:3.0f} {scheme:>6} {len(rows):4d} {out['sigma']:8.3f}"
          f" {out['share']:7.3f} {out['resid']:7.3f}"
          f" {tg['sharp']:9.2f} /{tg['heavy']:7.2f} @{tg['share']:.3f}"
          f" {prev if prev else float('nan'):7.2f}")
    e("")
    e("`G1b σ` is the same surface read over EIGHT backdrops including the three holdout rows")
    e("(claims §5.121 §4). The difference between the two columns is what the holdout was worth.")
    e("")

    # ------------------------------------------------------------------ the ladder
    e("### 2. The ladder, and the control at every rung")
    e("")
    e("`σ named` is the anchor the rung's documents carry at this scale — `heavyTapSigmaAtScale`")
    e("is the 1x anchor at dpr 1 and the 2x anchor at dpr 2. `σ read` is the family reader on the")
    e("rung's own captures and `Δ` is the control: the drawn width read back. `k drawn` is")
    e("`kScatter` over the band's own pixels and `k read` the fitted share.")
    e("")
    e(f"  {'rung':>5} {'surface':>9} {'sc':>3} {'sch':>6} {'σ named':>8} {'σ read':>8} {'Δ':>8}"
      f" {'k drawn':>8} {'k read':>7} {'resid':>7}")
    read = {}
    for name, one, two in rungs:
        for comp, scale, scheme in CELLS:
            named = one if scale == 1 else two
            out, rows, cell = read_cell("web", comp, scale, scheme, nodes, comps, args.lam,
                                        rung=name)
            if out is None:
                continue
            k = drawn_share(cell, comp, scale, BANDS[comp], nodes, m)
            read[(name, comp, scale, scheme)] = (out, named, k)
            d = (out["sigma"] / named - 1.0) if named > 0.5 else float("nan")
            e(f"  {name:>5} {comp:>9} {scale:3.0f} {scheme:>6} {named:8.3f} {out['sigma']:8.3f}"
              f" {d * 100:7.1f}% {k:8.3f} {out['share']:7.3f} {out['resid']:7.3f}")
        e("")
    e("At `c0` the 2x anchor is 0: the pyramid builds no heavy texture there and the pass takes the")
    e("chain tap it has always taken, so `σ named` is not a width and Δ is not defined. At `z001`")
    e("it is 0.001, which does NOT decline the mechanism — the gate is `heavySigmaCss > 0` — and")
    e("builds a heavy texture at chain level 0, making the deep sample the raw backdrop.")
    e("")

    # ------------------------------------------------------------------ the mapping and the fit
    e("### 3. The mapping from the named constant to the read width, and the two fits")
    e("")
    e("One line per (surface, scale, scheme) over the rungs that name a width at that scale, then")
    e("the reference's own reading inverted through it. `slope` is device px of reading per device")
    e("px of constant and is the condition: a slope near 1 is a lever the reader sees one-for-one.")
    e("")
    e(f"  {'surface':>9} {'sc':>3} {'sch':>6} {'rungs':>5} {'slope':>7} {'intercept':>9}"
      f" {'rms':>6} {'σ ref read':>10} {'FITTED':>8}")
    fitted = {}
    for comp, scale, scheme in CELLS:
        xs, ys = [], []
        for name, one, two in rungs:
            named = one if scale == 1 else two
            if named < 0.5 or name == "z001":
                continue
            key = (name, comp, scale, scheme)
            if key in read:
                xs.append(named)
                ys.append(read[key][0]["sigma"])
        if len(xs) < 3 or (comp, scale, scheme) not in ref:
            continue
        a, b = np.polyfit(np.array(xs), np.array(ys), 1)
        rms = float(np.sqrt(np.mean((np.polyval([a, b], xs) - np.array(ys)) ** 2)))
        target = ref[(comp, scale, scheme)]["sigma"]
        value = (target - b) / a if abs(a) > 1e-6 else float("nan")
        fitted[(comp, scale, scheme)] = value
        e(f"  {comp:>9} {scale:3.0f} {scheme:>6} {len(xs):5d} {a:7.3f} {b:9.3f} {rms:6.3f}"
          f" {target:10.3f} {value:8.3f}")
    e("")
    for scale in (1.0, 2.0):
        vals = {k: v for k, v in fitted.items() if k[1] == scale}
        if len(vals) < 2:
            continue
        lo, hi = min(vals.values()), max(vals.values())
        e(f"   dpr {scale:.0f}: " + "  ".join(f"{k[0]} {k[2]} {v:.2f}" for k, v in vals.items())
          + f"   spread {(hi / lo - 1) * 100:.1f} %"
          + ("  — one number serves both spans within 15 %" if hi / lo - 1 <= 0.15
             else "  — WIDER than 15 %: one number does not serve both spans"))
    e("")
    e("### 4. The objective, before and after")
    e("")
    e("The fit's objective is the family reader's width against the reference's, as |log(read /")
    e("reference)| averaged over the cells — a ratio rather than a difference, because a width is a")
    e("scale. `before` is the 0.14.0 control rung `c0`; `after` is the candidate rung. The share is")
    e("carried beside it as the mean |Δ|, unfitted, to show what the width's move costs it.")
    e("")
    e(f"  {'rung':>6} {'surface':>9} {'sc':>3} {'sch':>6} {'σ read':>8} {'σ ref':>8} {'|log|':>7}"
      f" {'k read':>7} {'k ref':>7} {'|Δk|':>6}")
    for name in ("c0", CANDIDATE):
        tot, totk, n = 0.0, 0.0, 0
        for comp, scale, scheme in CELLS:
            key = (name, comp, scale, scheme)
            if key not in read or (comp, scale, scheme) not in ref:
                continue
            got = read[key][0]
            want = ref[(comp, scale, scheme)]
            lg = abs(math.log(got["sigma"] / want["sigma"])) if want["sigma"] > 0 else float("nan")
            dk = abs(got["share"] - want["share"])
            tot += lg
            totk += dk
            n += 1
            e(f"  {name:>6} {comp:>9} {scale:3.0f} {scheme:>6} {got['sigma']:8.3f}"
              f" {want['sigma']:8.3f} {lg:7.4f} {got['share']:7.3f} {want['share']:7.3f}"
              f" {dk:6.3f}")
        if n:
            e(f"  {name:>6} {'MEAN':>9} {'':>3} {'':>6} {'':>8} {'':>8} {tot / n:7.4f}"
              f" {'':>7} {'':>7} {totk / n:6.3f}")
        e("")
    text = "\n".join(lines)
    print(text)
    open(args.out, "w").write(text + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
