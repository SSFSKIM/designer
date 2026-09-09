"""W25 G2 — the three fits and their condition, over one or more rungs read by `read-rung.py`.

WHAT THIS READS. `rung-<name>.json` under the scratch rung directories, and nothing else. It writes
only the text file it is told to. Every number it prints is a function of readings G0's instruments
produced; no law is restated here.

THE THREE OBJECTIVES, each stated before it is run (the W23 lesson).

  share  — the heavy share's thick-end lift. The observable is the WIDTH the reference's
           two-component kernel presents at a given backdrop pitch, so the objective is the mean
           |log(sigma_web / sigma_native)| over reader C's rows that are inside its validated bound
           on BOTH sides (G0 §1: about a quarter of the pitch in device px), on the thick spans of
           the two probe grids. Reader A's share on the canonical `impulse__rrect-md` is reported
           beside it as the direct reading of the quantity, and is a CHECK and not the objective: it
           is a validation row, and X3's discipline is that a fit is made on rows that are not the
           check.

  level  — the body's level above the thickness knee. The observable is the LEVEL RESIDUAL
           native − web in 8-bit codes; the model is `residual = gain · lever(row)` with the lever
           the codes-per-unit `predict.mjs` computes from the tone response itself. The fit is the
           least-squares gain over the rows whose span is above 96, and the condition is reported as
           the spread of the per-row gains those rows imply.

  field  — the rim's along-side slope. The observable is the per-side slope of the rim's peak excess
           in luma per CSS px. Under the factor `1 + slope · sizeThickness · (x/hw)(y/hh)` the rim
           on the top side is `A · (1 − slope · sizeThickness · x/hw)`, so the reference's own slope
           divided by its own rim mean, times the half-extent across the side, is the constant the
           row asks for — one estimate per side per cell, and their spread is the condition.

Usage: fit.py --mode share|level|field --rung r0 [--rung r1 …] [--scratch DIR] [--out FILE]
"""

import argparse
import json
import math
import os
import sys

import numpy as np

SCRATCH_DEFAULT = "/Users/new/.claude/jobs/5c70e47f/tmp/w25/g2"
# G0 `validate.txt`: reader C recovers a true sigma up to about a QUARTER of the backdrop's step
# pitch and reader B up to about an EIGHTH, in device px. Both grids and the canonical 1x bed are
# scale 1, so these are the bounds in device px directly.
PITCH = {"checkerboard-4": 4, "checkerboard-8": 8, "checkerboard": 16, "checkerboard-lc16": 16,
         "checkerboard-32": 32, "checkerboard-64": 64, "hc-text": 16, "hc-text-7": 7,
         "hc-text-28": 28}
HALF_EXTENT = {}   # filled from the component table


def load(rungs, scratch):
    out = {}
    for rung in rungs:
        path = os.path.join(scratch, rung, f"rung-{rung}.json")
        out[rung] = json.load(open(path))
    return out


def bound_c(backdrop):
    p = PITCH.get(backdrop)
    return None if p is None else p / 4.0


def pair(rows, key):
    """Pair native and web readings of the same row."""
    by = {}
    for r in rows:
        k = key(r)
        by.setdefault(k, {})[r["src"]] = r
    return {k: v for k, v in by.items() if "native" in v and "web" in v}


def encode(v):
    v = np.clip(np.asarray(v, dtype=float), 0.0, 1.0)
    return np.where(v <= 0.0031308, v * 12.92, 1.055 * v ** (1 / 2.4) - 0.055)


def codes(a, b):
    return float((encode(a) - encode(b)) * 255.0)


def smoothstep(a, b, x):
    t = min(1.0, max(0.0, (x - a) / max(b - a, 1e-6)))
    return t * t * (3.0 - 2.0 * t)


def do_share(data, out):
    w = out.write
    w("W25 G2 — fit-share: the heavy share's thick-end lift\n")
    w("=" * 100 + "\n\n")
    w("Reader C, the whole-region sigma match, on the two probe grids' structured backdrops.\n")
    w("A row COUNTS toward the objective when both the native and the web sigma are inside\n")
    w("reader C's validated bound for that backdrop's own step pitch (pitch/4 device px, G0 §1),\n")
    w("and the span is above `sizeSpanMin` so the lift can reach it at all.\n\n")
    for rung, d in data.items():
        rows = [r for r in d["widths"] if r["reader"] == "C" and r["bed"] in ("w9", "w21")]
        pairs = pair(rows, lambda r: (r["bed"], r["scene"]))
        w(f"── rung {rung} ─────────────────────────────────────────────────────────────\n")
        w(f"{'bed':5} {'scene':40} {'span':>5} {'pitch':>6} {'bound':>6} "
          f"{'native':>7} {'web':>7} {'ratio':>7}  in-bound\n")
        used = []
        for k in sorted(pairs):
            n, v = pairs[k]["native"], pairs[k]["web"]
            b = bound_c(n["backdrop"])
            sn, sw = n["sigmaDev"], v["sigmaDev"]
            ok = (b is not None and np.isfinite(sn) and np.isfinite(sw)
                  and sn <= b and sw <= b and not n["atCeiling"] and not v["atCeiling"])
            thick = n["span"] > 32
            ratio = sw / sn if np.isfinite(sn) and sn > 0 and np.isfinite(sw) else float("nan")
            if ok and thick:
                used.append((k, ratio, n["span"], n["backdrop"]))
            w(f"{n['bed']:5} {n['scene']:40} {n['span']:5.0f} "
              f"{PITCH.get(n['backdrop'], 0):6.0f} {(b if b else float('nan')):6.1f} "
              f"{sn:7.2f} {sw:7.2f} {ratio:7.3f}  {'yes' if ok else 'no':>3}"
              f"{'' if thick else '   (thin: the lift cannot reach it)'}\n")
        if used:
            logs = np.array([math.log(r) for _, r, _, _ in used if r > 0])
            w(f"\n  objective (mean |log ratio| over {len(logs)} thick in-bound rows): "
              f"{np.mean(np.abs(logs)):.4f}   mean log ratio {np.mean(logs):+.4f}\n")
            for span in sorted({s for _, _, s, _ in used}):
                sub = [r for _, r, s, _ in used if s == span]
                w(f"    span {span:5.0f}: n={len(sub):2d} mean ratio {np.mean(sub):.3f}\n")
        # Reader A's direct share reading, off the fit's own rows.
        a = pair([r for r in d["widths"] if r["reader"] == "A"],
                 lambda r: (r["bed"], r["scene"]))
        w("\n  reader A (the dot's own two components) — the CHECK, on validation rows:\n")
        w(f"  {'bed':12} {'scene':40} {'sharp n/w':>18} {'heavy n/w':>18} {'share n/w':>16}\n")
        for k in sorted(a):
            n, v = a[k]["native"], a[k]["web"]
            w(f"  {n['bed']:12} {n['scene']:40} "
              f"{n['sharpDev']:8.2f} /{v['sharpDev']:8.2f} "
              f"{n['heavyDev']:8.2f} /{v['heavyDev']:8.2f} "
              f"{n['heavyShare']:7.3f} /{v['heavyShare']:7.3f}\n")
        w("\n")


def do_level(data, rungs, analytic, out):
    """The level term, fitted on the EMPIRICAL lever a unit rung measures.

    `rungs[0]` is the baseline (every constant at its default) and `rungs[1]` the unit probe
    (`sizeToneLevelFar` = 1 and nothing else). The lever is then what the renderer actually did —
    `web(unit) - web(baseline)` in 8-bit codes — rather than what the tone response alone predicts,
    which is the difference between a term's effect on the response's TARGET and its effect on the
    composite the response solves inside. The analytic lever from `predict.mjs` is printed beside it
    so the two can be compared; where they disagree, the empirical one is the fit's.
    """
    w = out.write
    base, unit = rungs[0], rungs[1]
    w("W25 G2 - fit-level: the body's level above the thickness knee\n")
    w("=" * 100 + "\n\n")
    w(f"baseline rung {base} (all three constants at 0) against unit rung {unit} "
      f"(`sizeToneLevelFar` = 1)\n\n")
    w("`resid` is native - web at the baseline, in 8-bit codes over the body eroded 6 CSS px.\n")
    w("`lever` is web(unit) - web(baseline) in the same unit: what one unit of the constant\n")
    w("actually moves this row. `gain` is the value of the constant that would close the row's\n")
    w("own residual. Rows at or below span 96 have lever 0 EXACTLY and are the control: the\n")
    w("term cannot reach them at any value, which is what makes the fit safe for the bed.\n\n")
    lb = pair(data[base]["levels"], lambda r: (r["bed"], r["scene"]))
    lu = pair(data[unit]["levels"], lambda r: (r["bed"], r["scene"]))
    w(f"{'bed':12} {'scene':40} {'span':>5} {'native':>8} {'web0':>8} {'web1':>8} "
      f"{'resid':>8} {'lever':>8} {'analytic':>9} {'gain':>8}\n")
    rows, controls = [], []
    for k in sorted(lb):
        n, v0 = lb[k]["native"], lb[k]["web"]
        if n["holdout"] or k not in lu:
            continue
        v1 = lu[k]["web"]
        resid = codes(n["body"], v0["body"])
        lever = codes(v1["body"], v0["body"])
        an = analytic.get(k, float("nan"))
        gain = resid / lever if abs(lever) > 1e-9 else float("nan")
        w(f"{n['bed']:12} {n['scene']:40} {n['span']:5.0f} {n['body']:8.5f} "
          f"{v0['body']:8.5f} {v1['body']:8.5f} {resid:+8.3f} {lever:+8.3f} {an:+9.3f} "
          f"{(f'{gain:+8.3f}' if np.isfinite(gain) else '       -')}\n")
        if n["span"] > 96 and abs(lever) > 1e-9:
            rows.append((resid, lever, gain, n["bed"]))
        elif n["span"] <= 96:
            controls.append(abs(lever))
    w("\n")
    if controls:
        w(f"  CONTROL: {len(controls)} rows at or below span 96, worst |lever| "
          f"{max(controls):.6f} codes per unit - the term is inert there by construction.\n")
    if rows:
        r = np.array([x[0] for x in rows])
        lv = np.array([x[1] for x in rows])
        ls = float((lv @ r) / (lv @ lv))
        w(f"\n  JOINT least-squares gain over {len(rows)} rows above the knee: {ls:+.4f}\n")
        w(f"  residual RMS at that gain {np.sqrt(np.mean((r - ls * lv) ** 2)):.3f} codes, "
          f"at gain 0 {np.sqrt(np.mean(r ** 2)):.3f} codes\n")
        g = np.array([x[2] for x in rows])
        w(f"  per-row gains: median {np.median(g):+.3f}, quartiles "
          f"{np.percentile(g, 25):+.3f} ... {np.percentile(g, 75):+.3f}, sd {np.std(g):.3f}\n")
        w("  by bed (the condition - a constant the beds disagree about is not one constant):\n")
        for bed in sorted({x[3] for x in rows}):
            sub = [x for x in rows if x[3] == bed]
            rr = np.array([x[0] for x in sub])
            ll = np.array([x[1] for x in sub])
            g = float((ll @ rr) / (ll @ ll))
            w(f"    {bed:12}: n={len(sub):3d} least-squares gain {g:+.4f}, "
              f"median per-row {np.median([x[2] for x in sub]):+.3f}, "
              f"RMS {np.sqrt(np.mean(rr ** 2)):.3f} -> "
              f"{np.sqrt(np.mean((rr - g * ll) ** 2)):.3f} codes\n")
    w("\n")


def do_field(data, rungs, out):
    """The along-side slope, fitted on the EMPIRICAL response a unit rung measures.

    `rungs[0]` is the baseline and `rungs[1]` the unit probe (`rimAlongSideSlope` = 1). For each
    straight side of each flat-backdrop thick cell the reference's own slope is the target, the
    baseline web slope is where vitrea starts, and the unit rung's is where one unit of the constant
    takes it - so the row asks for `(native - web0) / (web1 - web0)`. Reading it this way needs no
    model of the rim's amplitude at all: the renderer itself supplies the derivative.
    """
    w = out.write
    base, unit = rungs[0], rungs[1]
    w("W25 G2 - fit-field: the rim's along-side slope\n")
    w("=" * 100 + "\n\n")
    w(f"baseline rung {base} (slope 0) against unit rung {unit} (`rimAlongSideSlope` = 1)\n\n")
    w("The reader is G0's along-side reader, unchanged: the rim's peak excess over the body beside\n")
    w("it, indexed by position along the straight part of a side, on the FLAT solids where a lens\n")
    w("has no gradient to refract. Slopes in luma per CSS px.\n\n")
    sb = pair(data[base]["sides"], lambda r: (r["bed"], r["scene"], r["side"]))
    su = pair(data[unit]["sides"], lambda r: (r["bed"], r["scene"], r["side"]))
    w(f"{'bed':5} {'scene':32} {'side':7} {'span':>5} {'nat slope':>10} {'web0':>10} "
      f"{'web1':>10} {'implied':>8}\n")
    est, thin = [], []
    for k in sorted(sb):
        n, v0 = sb[k]["native"], sb[k]["web"]
        if n["holdout"] or k not in su:
            continue
        v1 = su[k]["web"]
        d = v1["slopePerCss"] - v0["slopePerCss"]
        implied = (n["slopePerCss"] - v0["slopePerCss"]) / d if abs(d) > 1e-9 else float("nan")
        w(f"{n['bed']:5} {n['scene']:32} {n['side']:7} {n['span']:5.0f} "
          f"{n['slopePerCss']:+10.6f} {v0['slopePerCss']:+10.6f} {v1['slopePerCss']:+10.6f} "
          f"{(f'{implied:8.3f}' if np.isfinite(implied) else '       -')}\n")
        if not np.isfinite(implied):
            continue
        (est if n["span"] > 44 else thin).append((implied, abs(d), n["bed"], n["side"]))
    w("\n")
    if thin:
        w(f"  the thin controls (span <= 44): {len(thin)} sides, worst |web1 - web0| "
          f"{max(x[1] for x in thin):.6f} luma per CSS px - the capsule's own 0.0923 of the\n"
          f"  thickness curve, and 0.000000 exactly at span 32.\n")
    if est:
        e = np.array([x[0] for x in est])
        weight = np.array([x[1] for x in est])
        w(f"\n  implied slope over {len(e)} thick sides: median {np.median(e):+.3f}, "
          f"mean {np.mean(e):+.3f}, sd {np.std(e):.3f}\n")
        w(f"  quartiles {np.percentile(e, 25):+.3f} ... {np.percentile(e, 75):+.3f}\n")
        w(f"  lever-weighted mean {float(e @ weight / weight.sum()):+.3f}\n")
        w("  by side (the antisymmetry check - one field, not four constants):\n")
        for side in ("top", "bottom", "left", "right"):
            sub = [x[0] for x in est if x[3] == side]
            if sub:
                w(f"    {side:7}: n={len(sub):3d} median {np.median(sub):+.3f}\n")
        w("  by bed:\n")
        for bed in sorted({x[2] for x in est}):
            sub = [x[0] for x in est if x[2] == bed]
            w(f"    {bed:12}: n={len(sub):3d} median {np.median(sub):+.3f}\n")
    w("\n")


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", required=True, choices=["share", "level", "field"])
    ap.add_argument("--rung", action="append", required=True)
    ap.add_argument("--scratch", default=SCRATCH_DEFAULT)
    ap.add_argument("--levers", default=None, help="levers.json from predict.mjs level")
    ap.add_argument("--out", default=None)
    args = ap.parse_args(argv)

    data = load(args.rung, args.scratch)
    out = open(args.out, "w") if args.out else sys.stdout
    if args.mode == "share":
        do_share(data, out)
    elif args.mode == "level":
        levers = {}
        if args.levers:
            for row in json.load(open(args.levers)):
                levers[(row["bed"], row["scene"])] = row["codesPerUnit"]
        do_level(data, args.rung, levers, out)
    else:
        do_field(data, args.rung, out)
    if args.out:
        out.close()
        print(f"-> {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
