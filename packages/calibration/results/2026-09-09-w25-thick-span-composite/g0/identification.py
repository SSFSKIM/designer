"""W25 G0 deliverable 6 — the identification table: which rows separate which thick constant.

THIS IS A DESIGN ANALYSIS, NOT A MEASUREMENT, and every entry in it is a stated rule rather than a
reading. What it computes is the condition of the fit each bed shape would offer: for a set of rows
and a set of constants, the design matrix's singular values say whether the rows can tell the
constants apart at all. A zero singular value is exact collinearity — two constants the rows cannot
separate however good the instrument is — and that verdict is structural, so it does not depend on
the magnitudes chosen for the non-zero entries.

WHAT THIS READS: `apps/reference-apple/scenes.json` (the declared split, so the bed's shape is read
and never assumed), the two probe grids' fixture directories (to enumerate the rows a harness set
would carry), and `widths.json` / `argument-probe.json` beside this file, for the measured widths
that decide which rows are INSIDE their reader's identification bound.

THE FIVE CONSTANTS a thick-span law would carry, from the wave's Design:
  s1  the sharp sigma at 1x            s2  the sharp sigma at 2x
  hs  the heavy share                  kn  the knee / the size law's argument
  lv  the body's level term            cb  the collapsed body's level

THE SENSITIVITY RULES, each stated with what it is derived from. A row's entry for a constant is
how much that row's observable moves when the constant moves; zero means the row says nothing
about it.

  s1 / s2 — a row informs a width only if its reader can IDENTIFY a width there. `validate.txt`
      puts reader C's bound at about a quarter of the backdrop's step pitch and reader A's at 16
      device px on the impulse. So: 1 where the reference's own width at that cell is inside the
      row's bound, 0 where it is not. The scale selects which of the two constants the row loads.
  hs  — the heavy component is separable only where the backdrop has structure at a pitch WIDER
      than the heavy width itself; the reference's heavy sigma is 11-29 device px
      (dossier section 2b), so a 16 CSS px checkerboard cannot separate it from a level shift at
      either scale. 1 on `impulse` (dots 64 CSS px apart), 1 on `checkerboard-64`, 0.5 on
      `checkerboard-32`, 0 otherwise.
  kn  — the derivative of the LANDED law with respect to the knee, evaluated at the row's span:
      d/d(sizeSpanMax) of `scatterRampStart`'s span term (material.ts:3140-3188), which is
      `thin + (thick-thin)*smoothstep(sizeSpanMin, sizeSpanMax, span)
             + (far-thick)*smoothstep(sizeSpanMax, sizeScatterSpanMax(dpr), span)`.
      This is the one entry that is not a judgement: it is the current law differentiated. It is
      exactly 0 AT span 96 (a smoothstep's derivative vanishes at its own edge) and 0.002 above it,
      through the `far` decline alone — the anchor `material.ts:847-858` records as the workaround
      for the saturation.
  lv  — every row with a body reading carries the level: 1 everywhere.
  cb  — the collapsed body's level is carried only by rows that are actually collapsed. The tone
      response's argument is `backdropLuminance + 0.09*sizeThickness(span)` against a smoothstep
      down with edges 0.14 / 0.02 (`scenes.json:50-68`), so the row's own backdrop luminance and
      span decide it; the entry is that smoothstep's value, i.e. how collapsed the row is.

WHAT IS COMPARED. Five bed shapes — the three the wave's Design names, plus two variants the
readings made necessary:
  (i)    the current bed — the calibration and validation rows of `scenes.json`'s split;
  (ii)   the same plus `rrect-lg` and `glass-over-glass`'s cells moved from holdout to calibration;
  (iii)  the same as (i) plus the two probe grids declared as a harness set with their structured
         backdrops (`checkerboard-{4,8,16,32,64}`, `hc-text{,-7,-28}`, `photo`) over
         `rrect-sm`/`-md`/`-ml`/`-lg`, keeping `rrect-lg` and the stack as holdout — AS THE GRIDS
         STAND ON DISK, which is 1x only;
  (iii+) the same grids captured at BOTH scales, which is the variant the 2x column forces;
  (iv)   the grids whole, their solid backdrops included, at both scales — the shape that also
         carries the collapsed body's level.

Usage: identification.py [--out identification.txt]
"""

import argparse
import json
import os
import sys

import numpy as np

import w25lib as L

SIZE_SPAN_MIN, SIZE_SPAN_MAX = 32.0, 96.0
SCATTER_SPAN_MAX = {1.0: 256.0, 2.0: 256.0}
RAMP = {1.0: (0.72, 0.52, 0.20), 2.0: (0.46, 0.21, 0.21)}   # thin, thick, far — the landed patch
CONSTANTS = ["s1", "s2", "hs", "kn", "lv", "cb"]
SPAN = {"rrect-sm": 32.0, "capsule-button": 44.0, "toolbar-group": 44.0, "rrect-md": 96.0,
        "rrect-ml": 128.0, "glass-over-glass": 130.0, "rrect-lg": 160.0}
# Each committed backdrop's linear-light mean, as W21's probe scene file measured them
# (`scenes-w21-probe.json`, the mid-dark-solid comment): the same rule the runtime samples with.
BACKDROP_LUMA = {"impulse": 0.003750, "dark-solid": 0.011711, "mid-dark-solid": 0.059511,
                 "photo": 0.214065, "checkerboard": 0.500000, "hc-text": 0.740031,
                 "light-solid": 0.891800}


def smoothstep(a, b, x):
    if b == a:
        return 0.0 if x < a else 1.0
    t = min(max((x - a) / (b - a), 0.0), 1.0)
    return t * t * (3.0 - 2.0 * t)


def d_smoothstep_d_edge1(a, b, x):
    """d/db of smoothstep(a, b, x) — the knee is the UPPER edge of `sizeThickness`."""
    if b <= a or x <= a or x >= b:
        return 0.0
    t = (x - a) / (b - a)
    return 6.0 * t * (1.0 - t) * (-(x - a) / (b - a) ** 2)


def d_smoothstep_d_edge0(a, b, x):
    """d/da of smoothstep(a, b, x) — the knee is also the LOWER edge of the `far` decline."""
    if b <= a or x <= a or x >= b:
        return 0.0
    t = (x - a) / (b - a)
    return 6.0 * t * (1.0 - t) * ((x - b) / (b - a) ** 2)


def knee_lever(span, dpr):
    """d(scatterRampStart)/d(sizeSpanMax) at this span and scale, from the landed constants."""
    thin, thick, far = RAMP[dpr]
    return abs((thick - thin) * d_smoothstep_d_edge1(SIZE_SPAN_MIN, SIZE_SPAN_MAX, span)
               + (far - thick) * d_smoothstep_d_edge0(SIZE_SPAN_MAX, SCATTER_SPAN_MAX[dpr], span))


def collapse_lever(backdrop, span):
    """How collapsed the row is: the tone response evaluated at its own backdrop and span."""
    lum = BACKDROP_LUMA.get(backdrop.split("-")[0] if backdrop.startswith("checkerboard-")
                            else backdrop)
    if lum is None:
        lum = BACKDROP_LUMA.get("checkerboard" if backdrop.startswith("checkerboard")
                                else "hc-text" if backdrop.startswith("hc-text") else None)
    if lum is None:
        return 0.0
    x = lum + 0.09 * smoothstep(SIZE_SPAN_MIN, SIZE_SPAN_MAX, span)
    return 1.0 - smoothstep(0.02, 0.14, x)


def heavy_lever(backdrop):
    if backdrop == "impulse":
        return 1.0
    if backdrop == "checkerboard-64":
        return 1.0
    if backdrop == "checkerboard-32":
        return 0.5
    return 0.0


def width_lever(backdrop, scale, measured):
    """1 where the reference's own width at this cell is inside the row's identification bound."""
    pitch = L.backdrop_pitch_css(backdrop)
    if backdrop == "impulse":
        bound = 16.0
    elif pitch is None:
        return 0.0          # a solid backdrop identifies no width at all
    else:
        bound = pitch / 4.0 * scale
    if measured is None or not np.isfinite(measured):
        # No reading on this row: treat it as informative only if the bound is generous enough to
        # have carried the reference's widest recorded thick width (4.84 device px, dossier 2a).
        return 1.0 if bound >= 4.84 else 0.0
    return 1.0 if measured <= bound else 0.0


def build_rows(bed, measured):
    """The design matrix for one bed shape. `bed` is a list of (backdrop, component, scale)."""
    A, labels = [], []
    for backdrop, component, scale in bed:
        span = SPAN.get(component)
        if span is None:
            continue
        m = measured.get((backdrop, component, scale))
        wl = width_lever(backdrop, scale, m)
        row = {
            "s1": wl if scale == 1.0 else 0.0,
            "s2": wl if scale == 2.0 else 0.0,
            "hs": heavy_lever(backdrop) * (1.0 if wl else 0.3),
            "kn": knee_lever(span, scale),
            "lv": 1.0,
            "cb": collapse_lever(backdrop, span),
        }
        A.append([row[c] for c in CONSTANTS])
        labels.append(f"{backdrop}__{component} @{scale:g}x")
    return np.array(A, dtype=float), labels


def analyse(A):
    """Column-normalised singular values, the condition number, and the PER-CONSTANT separation.

    The condition number is a property of the whole matrix and it hides which constant is the
    trouble. `sep` is the per-constant statement: the fraction of a constant's own column that
    survives projecting out every OTHER column. sep = 1 means the rows see that constant and
    nothing else the same way; sep = 0 means the rows cannot tell it apart from a combination of
    the others at all, whatever the instrument's precision. It is the quantity the W23 lesson
    ("the condition before the fit") asks for, one number per constant.
    """
    if A.size == 0:
        return None
    norms = np.linalg.norm(A, axis=0)
    dead = [CONSTANTS[i] for i, n in enumerate(norms) if n < 1e-12]
    keep = [i for i, n in enumerate(norms) if n >= 1e-12]
    if not keep:
        return {"dead": dead, "sv": [], "cond": float("inf"), "kept": [], "sep": {},
                "n": A.shape[0]}
    B = A[:, keep] / norms[keep]
    sv = np.linalg.svd(B, compute_uv=False)
    cond = float(sv[0] / sv[-1]) if sv[-1] > 1e-12 else float("inf")
    sep = {}
    for j, i in enumerate(keep):
        a = B[:, j]
        others = np.delete(B, j, axis=1)
        if others.shape[1] == 0:
            sep[CONSTANTS[i]] = 1.0
            continue
        coef, *_ = np.linalg.lstsq(others, a, rcond=None)
        resid = a - others @ coef
        sep[CONSTANTS[i]] = float(np.linalg.norm(resid) / max(np.linalg.norm(a), 1e-12))
    for c in dead:
        sep[c] = 0.0
    return {"dead": dead, "sv": sv.tolist(), "cond": cond,
            "kept": [CONSTANTS[i] for i in keep], "sep": sep, "n": A.shape[0]}


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="identification.txt")
    args = ap.parse_args(argv)

    spec = json.load(open(L.SCENES))
    split = spec["split"]

    # The reference's own measured widths, keyed by (backdrop, component, scale), reader C on the
    # canonical bed and on the probe grids. Used only to decide the width levers.
    # Only the four STANDARD profiles: reduced transparency and increased contrast change the
    # material itself (the reduced-transparency body is flat, so reader C refuses it), and a width
    # read there says nothing about whether a row identifies the standard material's width. Where
    # several standard profiles share a (backdrop, component, scale) the median is taken.
    acc = {}
    if os.path.exists("widths.json"):
        for r in json.load(open("widths.json"))["widths"]:
            if (r["src"] == "native" and r["reader"] == "C"
                    and r["profileKey"] in ("1x-light", "2x-light", "1x-dark", "2x-dark")
                    and np.isfinite(r["sigmaDev"])):
                acc.setdefault((r["backdrop"], r["component"], r["scale"]), []).append(
                    r["sigmaDev"])
    if os.path.exists("argument-probe.json"):
        for r in json.load(open("argument-probe.json")):
            if "sigmaDev" in r and np.isfinite(r["sigmaDev"]):
                acc.setdefault((r["backdrop"], r["component"], r["scale"]), []).append(
                    r["sigmaDev"])
    measured = {k: float(np.median(v)) for k, v in acc.items()}

    def cells(ids, scales):
        out = []
        for sid in ids:
            parts = sid.split("__")
            if len(parts) != 3 or parts[2] != "rest":
                continue
            for s in scales:
                out.append((parts[0], parts[1], s))
        return out

    fittable = split["calibration"] + split["validation"]
    bed_i = cells(fittable, (1.0, 2.0))
    bed_ii = bed_i + cells(split["holdout"], (1.0, 2.0))
    probe_structured, probe_solid = [], []
    for key, (d, scale, scheme, _sc) in L.PROBES.items():
        if not os.path.isdir(d):
            continue
        for f in sorted(os.listdir(d)):
            if not f.endswith(".png"):
                continue
            parts = f[:-4].split("__")
            if len(parts) != 3 or parts[2] != "rest" or parts[1] not in SPAN:
                continue
            if parts[0] in ("light-solid", "dark-solid", "mid-dark-solid"):
                probe_solid.append((parts[0], parts[1], scale))
            else:
                probe_structured.append((parts[0], parts[1], scale))
    bed_iii = bed_i + probe_structured
    # The grids exist at 1x only. Shape (iii) as the fixtures stand therefore adds nothing at 2x,
    # which is the amendment's sharpest constraint, so the 2x variant is scored beside it.
    bed_iii2x = bed_i + probe_structured + [(b, c, 2.0) for (b, c, _s) in probe_structured]
    bed_iv = bed_iii2x + probe_solid + [(b, c, 2.0) for (b, c, _s) in probe_solid]

    beds = [("(i)    the current bed", bed_i),
            ("(ii)   + rrect-lg and glass-over-glass into calibration", bed_ii),
            ("(iii)  + the probe grids as a structured harness set, AS CAPTURED (1x only)",
             bed_iii),
            ("(iii+) the same grids captured at BOTH scales", bed_iii2x),
            ("(iv)   the grids whole, structured and solid, at both scales", bed_iv)]

    with open(args.out, "w") as fh:
        def w(s=""):
            fh.write(s + "\n")

        w(__doc__.strip())
        w()
        w("=" * 100)
        w("TABLE 1 — the per-row sensitivity, for the rows that carry a thick span. Every entry is")
        w("the rule stated in the header, evaluated at the row. `kn` is the landed law's own")
        w("derivative and is the only entry that is not a judgement.")
        w("=" * 100)
        w(f"{'row':46} {'span':>5} " + " ".join(f"{c:>6}" for c in CONSTANTS))
        seen = set()
        for _name, bed in beds:
            for (bd, comp, sc) in bed:
                if SPAN.get(comp, 0) < 96 or (bd, comp, sc) in seen:
                    continue
                seen.add((bd, comp, sc))
                A, _ = build_rows([(bd, comp, sc)], measured)
                w(f"{bd + '__' + comp + ' @' + format(sc, 'g') + 'x':46} {SPAN[comp]:5.0f} "
                  + " ".join(f"{v:6.3f}" for v in A[0]))
        w()
        w("READING TABLE 1. `kn` is exactly 0.000 at span 96 — `sizeThickness` saturates there and")
        w("a smoothstep's derivative vanishes at its own edge — and 0.002 at 128, 130 and 160,")
        w("where the only sensitivity left is the `far` decline's shallow lower edge, the")
        w("workaround `material.ts:847-858` records. So the knee is not strictly collinear on the")
        w("thick spans; its lever there is three orders of magnitude below the width levers, and")
        w("it comes entirely through the anchor that exists because the knee saturates. Spans")
        w("BETWEEN 32 and 96 carry the same 0.002 and no thick span carries more, which is the")
        w("bed's real limit: nothing on any of the three shapes moves the knee's own edge.")
        w()
        w("A CAVEAT THAT BOUNDS TABLE 2. The `kn` column is a derivative in share-per-CSS-px and")
        w("the width columns are 0/1 indicators, so they are not in the same unit and the")
        w("condition number and `sep` below inherit that choice of scale. What does NOT depend on")
        w("it is which entries are ZERO — which rows say nothing about a constant — and every")
        w("verdict this file offers is read off those.")
        w()
        w("=" * 100)
        w("TABLE 2 — the three bed shapes, scored. `cond` is the condition number of the")
        w("column-normalised design matrix over the constants the bed carries at all; `dead` lists")
        w("the constants no row in that bed touches, which is the strongest verdict available —")
        w("those are not ill-conditioned, they are absent.")
        w("=" * 100)
        for name, bed in beds:
            A, labels = build_rows(bed, measured)
            res = analyse(A)
            w(f"-- {name}")
            w(f"   rows {res['n']}   carried {res['kept']}   DEAD {res['dead'] or 'none'}")
            w(f"   singular values (normalised): "
              + " ".join(f"{v:.4f}" for v in res["sv"]))
            w(f"   condition number: {res['cond']:.1f}"
              if np.isfinite(res["cond"]) else "   condition number: infinite (collinear)")
            w(f"     {'const':6} {'rows':>5} {'max entry':>10} {'sep':>7}   "
              f"separated by rows at spans")
            for c in CONSTANTS:
                col = A[:, CONSTANTS.index(c)]
                spans = sorted({SPAN[lab.split('__')[1].split(' @')[0]]
                                for lab, v in zip(labels, col) if v > 1e-9})
                w(f"     {c:6} {int((col > 1e-9).sum()):5d} {col.max():10.3f} "
                  f"{res['sep'].get(c, 0.0):7.3f}   {spans or 'none'}")
            w()
        w("=" * 100)
        w("TABLE 3 — per constant, the rows that separate it, in each bed.")
        w("=" * 100)
        for c in CONSTANTS:
            w(f"-- {c}")
            for name, bed in beds:
                A, labels = build_rows(bed, measured)
                j = CONSTANTS.index(c)
                hit = [(labels[i], A[i, j]) for i in range(len(labels)) if A[i, j] > 1e-9]
                distinct_spans = sorted({SPAN[l.split("__")[1].split(" @")[0]] for l, _ in hit}) \
                    if hit else []
                w(f"   {name:52} {len(hit):3d} row(s), spans {distinct_spans or 'none'}")
                if hit and len(hit) <= 12:
                    for lab, v in hit:
                        w(f"        {lab:50} {v:.3f}")
                elif hit:
                    for lab, v in hit[:6]:
                        w(f"        {lab:50} {v:.3f}")
                    w(f"        … and {len(hit) - 6} more")
            w()
    print(f"-> {args.out}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
