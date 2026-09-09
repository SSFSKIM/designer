"""W26 G1 — the fits, per scale, on the impulse rows: the width, then the share.

Each fit is printed with its ROWS, its CONDITION (the spread of the regressor and the range over
which the read is monotone), its residual before and after, and its decline where it declines. The
reference's own readings are reader A's from claims §5.113 §2 and are not rewritten here.

    g1-fit.py [--scratch DIR] [--out FILE]
"""

import argparse
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import w26lib as D  # noqa: E402
import w25lib as L  # noqa: E402

SCRATCH = "/Users/new/.claude/jobs/5c70e47f/tmp/w26/g1"
SPANS = ("rrect-md", "rrect-ml", "rrect-lg")
# Reader A on the REFERENCE fixtures, read by this file so the numbers are this run's own; the
# ledger's are §5.113 §2 and stand beside them.
WIDTH_RUNGS = [("r0", 0.0), ("t10", 10.0), ("t103", 10.3), ("t11", 11.0), ("t113", 11.3), ("t12", 12.0), ("t13", 13.0),
               ("t16", 16.0), ("t19", 19.0), ("t22", 22.0), ("t25", 25.0)]
FLOOR_RUNGS = [("r0", -1.0), ("c1", 1.00), ("c1f85", 0.85), ("c1f75", 0.75), ("c1f65", 0.65), ("c1f55", 0.55)]
LIFT_RUNGS = [("r0", -1.0), ("c1", 0.00), ("c1l15", 0.15), ("c1l25", 0.25), ("c1l35", 0.35), ("c1l45", 0.45)]


def reader_a(root, profile, scale, comp, comps):
    sid = f"impulse__{comp}__rest"
    web = os.path.join(root, profile, sid, f"{sid}__webgpu.png")
    if not os.path.exists(web):
        return None
    shape = (int(200 * scale), int(320 * scale))
    lum = L.luma_of(web)
    if lum.shape != shape:
        return None
    bg = L.background_for("impulse", scale, shape)
    rows = L.read_psf_cell(lum, bg, L.Cell(comp, comps), scale, half_css=30.0)
    if not rows:
        return None
    return {
        "heavy": float(np.median([r["heavySigmaDev"] for r in rows])),
        "share": float(np.median([r["heavyShare"] for r in rows])),
        "sharp": float(np.median([r["sharpSigmaDev"] for r in rows])),
    }


def reference(profile, scale, comp, comps):
    sid = f"impulse__{comp}__rest"
    native = L.native_path(profile, sid)
    if not os.path.exists(native):
        return None
    shape = (int(200 * scale), int(320 * scale))
    lum = L.luma_of(native)
    if lum.shape != shape:
        return None
    bg = L.background_for("impulse", scale, shape)
    rows = L.read_psf_cell(lum, bg, L.Cell(comp, comps), scale, half_css=30.0)
    if not rows:
        return None
    return {
        "heavy": float(np.median([r["heavySigmaDev"] for r in rows])),
        "share": float(np.median([r["heavyShare"] for r in rows])),
        "sharp": float(np.median([r["sharpSigmaDev"] for r in rows])),
    }


def objective(reads, refs, key):
    """Mean |log(web/native)| over the rows that have both — scale-free and symmetric."""
    vals = []
    for comp in reads:
        if comp not in refs:
            continue
        a, b = reads[comp].get(key), refs[comp].get(key)
        if a is None or b is None or a <= 0 or b <= 0:
            continue
        vals.append(abs(np.log(a / b)))
    return float(np.mean(vals)) if vals else float("nan")


def share_objective(reads, refs):
    vals = [abs(reads[c]["share"] - refs[c]["share"]) for c in reads if c in refs]
    return float(np.mean(vals)) if vals else float("nan")


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--scratch", default=SCRATCH)
    ap.add_argument("--out", default=os.path.join(HERE, "fits.txt"))
    args = ap.parse_args(argv)
    comps = L.load_components()
    out = []
    e = out.append
    e("W26 G1 — the fits, per scale, on the impulse rows")
    e("=" * 100)
    e("")

    refs = {}
    for pkey in ("1x-light", "2x-light"):
        profile, scale, _ = L.PROFILES[pkey]
        refs[pkey] = {c: reference(profile, scale, c, comps) for c in SPANS}
        refs[pkey] = {c: v for c, v in refs[pkey].items() if v is not None}
    e("0. The reference, reader A, this run's own reading")
    e("")
    e(f"   {'profile':>9} {'row':>10} {'heavy':>8} {'share':>8} {'sharp':>8}")
    for pkey, rows in refs.items():
        for c, v in rows.items():
            e(f"   {pkey:>9} {c:>10} {v['heavy']:8.2f} {v['share']:8.3f} {v['sharp']:8.2f}")
    e("")

    # 1. The 2x width.
    e("1. `sizeHeavyTapSigma2x` on the three 2x impulse rows, reader A's heavy sigma")
    e("")
    e("   Condition: the read moves 11.0 -> 52.2 device px over sigma 10 -> 25, and is monotone")
    e("   over the whole range (claims 5.119 section 2). The objective is mean |log(web/native)|")
    e("   over the three rows; `md+ml` drops `-lg`, whose reference reads 16.92 against `-md`'s")
    e("   11.29 — a span grading one width per source cannot follow.")
    e("")
    profile, scale, _ = L.PROFILES["2x-light"]
    e(f"   {'rung':>6} {'sigma':>6} " + " ".join(f"{c:>10}" for c in SPANS)
      + f" | {'all 3':>7} {'md+ml':>7}")
    best = (None, float("inf"))
    for rung, sigma in WIDTH_RUNGS:
        root = os.path.join(args.scratch, rung, "web-captures")
        reads = {c: reader_a(root, profile, scale, c, comps) for c in SPANS}
        reads = {c: v for c, v in reads.items() if v is not None}
        if not reads:
            continue
        o3 = objective(reads, refs["2x-light"], "heavy")
        o2 = objective({c: reads[c] for c in reads if c != "rrect-lg"},
                       refs["2x-light"], "heavy")
        e(f"   {rung:>6} {sigma:6.1f} " + " ".join(f"{reads[c]['heavy']:10.2f}" for c in SPANS
                                                   if c in reads)
          + f" | {o3:7.4f} {o2:7.4f}")
        if o2 < best[1]:
            best = (sigma, o2)
    e("")
    e(f"   Minimum on `md+ml`: sigma2x = {best[0]}, objective {best[1]:.4f}.")
    e("")

    # 2. The 1x width — declined, with the reading that declines it.
    e("2. `sizeHeavyTapSigma` at 1x — DECLINED, and the reading that declines it")
    e("")
    profile1, scale1, _ = L.PROFILES["1x-light"]
    e(f"   {'rung':>6} {'sigma':>6} " + " ".join(f"{c:>10}" for c in SPANS) + f" {'median':>8}")
    for rung, sigma in WIDTH_RUNGS:
        root = os.path.join(args.scratch, rung, "web-captures")
        reads = {c: reader_a(root, profile1, scale1, c, comps) for c in SPANS}
        reads = {c: v for c, v in reads.items() if v is not None}
        if not reads:
            continue
        med = float(np.median([reads[c]["heavy"] for c in reads]))
        e(f"   {rung:>6} {sigma:6.1f} " + " ".join(f"{reads[c]['heavy']:10.2f}" for c in SPANS
                                                   if c in reads) + f" {med:8.2f}")
    e("")
    e("   Reader A's 1x median is FLAT over sigma 10 -> 13 and garbage above it; reader D cannot")
    e("   read these rows at all (`reader-d.txt`). No 1x fit is taken — see g1-findings.md.")
    e("")

    # 3. The share, per scale.
    e("3. The share, per scale, on the same rows — reader A's own share")
    e("")
    e("   The two scales want the lever in OPPOSITE directions, which is why they take different")
    e("   constants. The objective is the mean absolute share difference against the reference.")
    e("")
    e("   3a. 2x: `sizeScatterFloor2x` off 1")
    e("")
    e(f"   {'rung':>6} {'floor':>6} " + " ".join(f"{c:>10}" for c in SPANS) + f" | {'mean |d|':>9}")
    for rung, floor in FLOOR_RUNGS:
        root = os.path.join(args.scratch, rung, "web-captures")
        reads = {c: reader_a(root, profile, scale, c, comps) for c in SPANS}
        reads = {c: v for c, v in reads.items() if v is not None}
        if not reads:
            continue
        e(f"   {rung:>6} {floor:6.2f} " + " ".join(f"{reads[c]['share']:10.3f}" for c in SPANS
                                                   if c in reads)
          + f" | {share_objective(reads, refs['2x-light']):9.4f}")
    e("")
    e("   3b. 1x: `sizeScatterHeavyShareThick1x`, the lift on `kDeep`")
    e("")
    e(f"   {'rung':>6} {'lift':>6} " + " ".join(f"{c:>10}" for c in SPANS) + f" | {'mean |d|':>9}")
    for rung, lift in LIFT_RUNGS:
        root = os.path.join(args.scratch, rung, "web-captures")
        reads = {c: reader_a(root, profile1, scale1, c, comps) for c in SPANS}
        reads = {c: v for c, v in reads.items() if v is not None}
        if not reads:
            continue
        e(f"   {rung:>6} {lift:6.2f} " + " ".join(f"{reads[c]['share']:10.3f}" for c in SPANS
                                                  if c in reads)
          + f" | {share_objective(reads, refs['1x-light']):9.4f}")
    e("")

    # 4. The off-row check: `impulse__rrect-sm`, at both scales.
    e("4. The share's off-row check — `impulse__rrect-sm`, which no fit above reads")
    e("")
    e("   Decision Log 2 (d) retired the coarse checkerboards' single-width objective as this")
    e("   check: it is dominated by the kernel's CORE and answers about the SHARP component. The")
    e("   off-row check is therefore a fourth impulse span, read the same way.")
    e("")
    for pkey, rungs in (("2x-light", FLOOR_RUNGS), ("1x-light", LIFT_RUNGS)):
        p, sc, _ = L.PROFILES[pkey]
        ref = reference(p, sc, "rrect-sm", comps)
        e(f"   {pkey}: reference heavy {ref['heavy']:.2f}, share {ref['share']:.3f}"
          if ref else f"   {pkey}: reference NOT READ")
        e(f"   {'rung':>6} {'value':>6} {'heavy':>8} {'share':>8} {'sharp':>8}")
        for rung, value in rungs:
            root = os.path.join(args.scratch, rung, "web-captures")
            v = reader_a(root, p, sc, "rrect-sm", comps)
            if v is None:
                continue
            e(f"   {rung:>6} {value:6.2f} {v['heavy']:8.2f} {v['share']:8.3f} {v['sharp']:8.2f}")
        e("")

    # 5. The sharp sigma, read at every rung and not fitted.
    e("5. The sharp sigma, read at every rung and NOT fitted (Decision Log 2 (d))")
    e("")
    for pkey, rungs in (("2x-light", WIDTH_RUNGS + FLOOR_RUNGS),
                        ("1x-light", WIDTH_RUNGS + LIFT_RUNGS)):
        p, sc, _ = L.PROFILES[pkey]
        ref = {c: reference(p, sc, c, comps) for c in SPANS}
        e(f"   {pkey}  reference sharp: "
          + " ".join(f"{c}={ref[c]['sharp']:.2f}" for c in SPANS if ref[c]))
        e(f"   {'rung':>6} " + " ".join(f"{c:>10}" for c in SPANS))
        for rung, _value in rungs:
            root = os.path.join(args.scratch, rung, "web-captures")
            reads = {c: reader_a(root, p, sc, c, comps) for c in SPANS}
            reads = {c: v for c, v in reads.items() if v is not None}
            if not reads:
                continue
            e(f"   {rung:>6} " + " ".join(f"{reads[c]['sharp']:10.2f}" for c in SPANS
                                          if c in reads))
        e("")

    text = "\n".join(out)
    print(text)
    open(args.out, "w").write(text + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
