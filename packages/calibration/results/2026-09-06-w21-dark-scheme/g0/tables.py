"""W21 G0 — the findings' tables, written from `read.py`'s JSON rather than by hand.

Five tables, each one a file under `g0/` that `g0-probe.md` quotes verbatim:

  anchors.txt      the response surface's six anchors, plus the law's interpolation checked on the
                   two components that have no anchor cells of their own;
  passthrough.txt  body sd against backdrop pitch per component — the alpha's evidence, and the
                   lerp-versus-multiply discriminator;
  rim.txt          the rim peak per side against backdrop and size, its excess over the backdrop on
                   the solids, and its flatness across sides;
  tints.txt        the tinted capsules, descriptive (the tint pathway is a stop this wave);
  candidate.txt    a residual table for a web reading against the native probe, per cell.

Nothing here fits anything. The anchors are read, the law is evaluated FROM those anchors with no
free parameter, and everything else is arithmetic on the reader's output.

    tables.py --native <read.json> [--web <label>=<read.json> ...] --out <dir>

Every table is restricted to the cells present in the given JSON, so a run that left the probe's
holdout unread produces tables that do not mention it.
"""

import argparse
import json
import os

SOLIDS = ["dark-solid", "mid-dark-solid", "light-solid"]
THIN = "rrect-sm"
# The thick row's pool over the solids. W9's grid runs three components over each solid — sm, md and
# lg — so rrect-ml, thick though it is, has no solid cell to contribute and is an interpolation
# check instead.
THICK = ["rrect-md", "rrect-lg"]
# The renderer's own size law: `sizeThickness = smoothstep(sizeSpanMin, sizeSpanMax, span)` with
# the landed 32 / 96, and `backdropToneResponse` smoothsteps the two anchor rows in that thickness.
SPAN = {"rrect-sm": 32, "capsule-button": 44, "rrect-md": 96, "rrect-ml": 128, "rrect-lg": 160}
SIZE_SPAN_MIN, SIZE_SPAN_MAX = 32.0, 96.0
# The one cell where the dark reference draws the material's LIGHT appearance rather than a level on
# a response curve; every summary reports it apart from the rest (see anchors.txt).
SWITCH_CELL = "light-solid__rrect-sm__rest"
PITCH = {
    "checkerboard-4": 4, "checkerboard-8": 8, "checkerboard": 16, "checkerboard-32": 32,
    "checkerboard-64": 64, "checkerboard-lc16": 16, "hc-text-7": 7, "hc-text": 14, "hc-text-28": 28,
}


def smoothstep(a, b, x):
    t = min(1.0, max(0.0, (x - a) / (b - a)))
    return t * t * (3 - 2 * t)


def thickness(component):
    return smoothstep(SIZE_SPAN_MIN, SIZE_SPAN_MAX, SPAN[component])


def pchip3(xs, ys):
    """The renderer's own three-anchor monotone interpolant, clamped — `backdropToneResponse`."""
    def f(x):
        x = min(xs[2], max(xs[0], x))
        h0, h1 = xs[1] - xs[0], xs[2] - xs[1]
        d0, d1 = (ys[1] - ys[0]) / h0, (ys[2] - ys[1]) / h1
        m1 = 0.0 if d0 * d1 <= 0 else (2 * d0 * d1) / (d0 + d1)
        if x <= xs[1]:
            h, t, y0, y1, s0, s1 = h0, (x - xs[0]) / h0, ys[0], ys[1], d0, m1
        else:
            h, t, y0, y1, s0, s1 = h1, (x - xs[1]) / h1, ys[1], ys[2], m1, d1
        return (y0 * (1 + 2 * t) * (1 - t) ** 2 + s0 * h * t * (1 - t) ** 2
                + y1 * t * t * (3 - 2 * t) + s1 * h * t * t * (t - 1))
    return f


def sig(row, key):
    return f"{row[key]:.4f}" if key in row else "  -   "


def shares(row):
    """The cell's byte-state shares as `4/3`, or a bare count when the cell drew one state."""
    st = row.get("states")
    return "/".join(str(s["runs"]) for s in st) if st else "-"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--native", required=True)
    ap.add_argument("--web", action="append", default=[], metavar="LABEL=JSON")
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    native = json.load(open(args.native))
    rows = {r["scene"]: r for r in native["rows"]}
    webs = {}
    for spec in args.web:
        label, path = spec.split("=", 1)
        webs[label] = {r["scene"]: r for r in json.load(open(path))["rows"]}
    os.makedirs(args.out, exist_ok=True)

    def cell(bg, comp, tint=None):
        sid = f"{bg}__{comp}__rest" + ("-tint-orange" if tint else "")
        return rows.get(sid)

    # ---- 1. the anchors ------------------------------------------------------
    lines = []
    lines.append("W21 G0 table 1 — the response surface's anchors, read from the dark probe")
    lines.append("")
    lines.append("The law is `R(encodedMean, thickness)` (material.ts backdropToneResponse): three")
    lines.append("anchors in the backdrop's ENCODED-space mean, a thin row and a thick row, and a")
    lines.append("smoothstep between the rows in `sizeThickness = smoothstep(32, 96, span)`. The thin")
    lines.append("row is rrect-sm (span 32, thickness 0); the thick row is the rrect-md and rrect-lg")
    lines.append("cells pooled (spans 96 and 160, thickness 1 for both because the size law saturates")
    lines.append("at 96). rrect-ml belongs to the thick row by thickness but W9's grid puts no rrect-ml")
    lines.append("over a solid, so it cannot join the pool and appears below as an interpolation check")
    lines.append("instead. Every level is a MEASUREMENT of the dark reference under the declared box")
    lines.append("eroded 6 CSS px. Nothing is fitted.")
    lines.append("")
    lines.append("Two sigmas per level, because they answer different questions. `sigma` runs over")
    lines.append("every attested run including a state flip; `sigmaMaj` runs only over the runs holding")
    lines.append("the published byte state and is the noise floor of the quoted number. `states` gives")
    lines.append("the byte-state shares. A cell where the two sigmas differ by orders of magnitude is")
    lines.append("bistable and the anchor rests on its majority draw — say so wherever it is quoted.")
    lines.append("")
    lines.append(f"{'anchor':16s} {'encodedMean':>12s} {'linearMean':>11s} | "
                 f"{'thin (sm)':>10s} {'sigma':>8s} {'sigmaMaj':>9s} {'states':>7s} | "
                 f"{'md':>8s} {'lg':>8s} {'thick mean':>11s} {'spread':>8s} {'sigmaMaj':>9s} "
                 f"{'states':>7s}")
    anchor_x, thin_y, thick_y = [], [], []
    for bg in SOLIDS:
        sm = cell(bg, THIN)
        thick = [t for t in (cell(bg, c) for c in THICK) if t is not None]
        if sm is None or not thick:
            lines.append(f"{bg:16s}  (not read)")
            continue
        vals = [t["bodyNative"] for t in thick]
        mean = sum(vals) / len(vals)
        spread = max(vals) - min(vals)
        sigma_thick = max((t.get("sigmaBodyMajority", 0.0) for t in thick), default=0.0)
        anchor_x.append(sm["backdropEncodedMean"])
        thin_y.append(sm["bodyNative"])
        thick_y.append(mean)
        per = {t["component"]: t["bodyNative"] for t in thick}
        lines.append(
            f"{bg:16s} {sm['backdropEncodedMean']:12.4f} {sm['backdropLinearMean']:11.4f} | "
            f"{sm['bodyNative']:10.4f} {sig(sm, 'sigmaBody'):>8s} "
            f"{sig(sm, 'sigmaBodyMajority'):>9s} {shares(sm):>7s} | "
            + " ".join(f"{per[c]:8.4f}" for c in THICK if c in per)
            + f" {mean:11.4f} {spread:8.4f} {sigma_thick:9.4f} "
            + "/".join(shares(t) for t in thick)
        )
    lines.append("")
    if len(anchor_x) == 3:
        lines.append(f"backdropToneAnchorX          [{anchor_x[0]:.4f}, {anchor_x[1]:.4f}, {anchor_x[2]:.4f}]")
        lines.append(f"backdropToneResponseThin     [{thin_y[0]:.4f}, {thin_y[1]:.4f}, {thin_y[2]:.4f}]")
        lines.append(f"backdropToneResponseThick    [{thick_y[0]:.4f}, {thick_y[1]:.4f}, {thick_y[2]:.4f}]")
        lines.append("")
        lines.append("Interpolation check — the two components with no anchor cells of their own")
        lines.append("(capsule-button at span 44, rrect-ml at span 128) predicted by the law FROM the")
        lines.append("six anchors above, with no free parameter, against what the reference drew over")
        lines.append("every structured backdrop the grid carries. A miss here is the law's form, not")
        lines.append("its anchors.")
        lines.append("")
        lines.append(f"{'scene':46s} {'encIn':>7s} {'thick':>6s} {'measured':>9s} "
                     f"{'predicted':>10s} {'resid':>8s} {'sigma':>7s}")
        thin_f = pchip3(anchor_x, thin_y)
        thick_f = pchip3(anchor_x, thick_y)
        for sid, r in sorted(rows.items()):
            if r["tint"] is not None or r["component"] not in ("capsule-button", "rrect-ml"):
                continue
            f = smoothstep(0.0, 1.0, thickness(r["component"]))
            pred = thin_f(r["backdropEncodedMean"]) * (1 - f) + thick_f(r["backdropEncodedMean"]) * f
            lines.append(
                f"{sid:46s} {r['backdropEncodedMean']:7.4f} {f:6.3f} {r['bodyNative']:9.4f} "
                f"{pred:10.4f} {pred - r['bodyNative']:+8.4f} {sig(r, 'sigmaBodyMajority'):>7s}"
            )
    write(args.out, "anchors.txt", lines)

    # The anchors as data, so the candidate profile documents are DERIVED from the reading rather
    # than typed from it. Two readings of the thin row's top anchor, because the probe offers two
    # and they disagree by 0.81: `light-solid__rrect-sm` is the whole scene bright and the material
    # draws its light appearance; `checkerboard-64__rrect-sm` has a footprint entirely inside one
    # white checker cell — the same uniform bright input at the footprint, a dark scene around it —
    # and the material stays dark. A monotone curve over a footprint statistic can carry one of them.
    if len(anchor_x) == 3:
        uniform_white = cell("checkerboard-64", THIN)
        variants = {
            "anchors-measured": {
                "anchorX": [round(x, 4) for x in anchor_x],
                "thin": [round(y, 4) for y in thin_y],
                "thick": [round(y, 4) for y in thick_y],
                "note": "The thin row's top anchor is light-solid__rrect-sm as measured, 0.9666 — "
                "the material's LIGHT appearance, drawn on a scene that is bright everywhere.",
            },
        }
        if uniform_white is not None:
            variants["anchors-footprint-top"] = {
                "anchorX": [round(x, 4) for x in anchor_x],
                "thin": [round(thin_y[0], 4), round(thin_y[1], 4),
                         round(uniform_white["bodyNative"], 4)],
                "thick": [round(y, 4) for y in thick_y],
                "note": "The thin row's top anchor is checkerboard-64__rrect-sm, "
                f"{uniform_white['bodyNative']:.4f} — a footprint entirely inside one white checker "
                "cell (encoded mean 1.0000, placed at the light-solid anchor's 0.9505), which is "
                "the brightest UNIFORM FOOTPRINT the grid offers that does not also make the whole "
                "scene bright.",
            }
        for name, payload in variants.items():
            path = os.path.join(args.out, f"{name}.json")
            with open(path, "w") as fh:
                json.dump(payload, fh, indent=2)
                fh.write("\n")
            print(f"-> {path}")

    # ---- 2. the passthrough --------------------------------------------------
    lines = ["W21 G0 table 3 — the passthrough: body sd against backdrop pitch, per component", ""]
    lines.append("The alpha's evidence, and the lerp-versus-multiply discriminator.")
    lines.append("")
    lines.append("`bgSd` is the backdrop's own sd under the declared box — the structure on offer.")
    lines.append("`pass` is `sd / bgSd`, the fraction of it the material let through, which is the")
    lines.append("quantity a lerp's alpha sets directly. `sd/body` is the passed structure relative to")
    lines.append("the level. Under a LERP toward a constant tint the passed structure is a function of")
    lines.append("the alpha alone, so `pass` is flat while `sd/body` tracks 1/body; under a MULTIPLY")
    lines.append("the passed structure scales with the level, so `sd/body` is flat while `pass` tracks")
    lines.append("the body. Read the two columns against each other down a column of constant body and")
    lines.append("across rows whose body differs.")
    lines.append("")
    head = (f"{'component':16s} {'background':18s} {'pitch':>6s} {'body':>8s} {'sd':>8s} "
            f"{'bgSd':>8s} {'pass':>7s} {'sd/body':>8s} {'sigmaMaj':>9s}")
    for label in webs:
        head += f" | {label + ' sd':>13s} {label + ' pass':>15s}"
    lines.append(head)
    for comp in ["rrect-sm", "capsule-button", "rrect-md", "rrect-ml", "rrect-lg"]:
        for bg in sorted(PITCH, key=lambda b: (b.split("-")[0], PITCH[b])):
            r = cell(bg, comp)
            if r is None:
                continue
            bgsd = r.get("backdropSd", float("nan"))
            # A footprint that lies inside one uniform checker cell offers no structure at all, so
            # the passed FRACTION is undefined there rather than enormous. The row still belongs in
            # the table — it is the strongest datum in the whole probe (see anchors.txt) — but its
            # pass column has to say "no structure on offer" and not a number.
            passed = f"{r['sdNative'] / bgsd:7.4f}" if bgsd > 1e-4 else f"{'-':>7s}"
            line = (f"{comp:16s} {bg:18s} {PITCH[bg]:6d} {r['bodyNative']:8.4f} "
                    f"{r['sdNative']:8.4f} {bgsd:8.4f} {passed} "
                    f"{r['sdNative'] / max(r['bodyNative'], 1e-9):8.4f} "
                    f"{sig(r, 'sigmaBodyMajority'):>9s}")
            for label, wrows in webs.items():
                w = wrows.get(r["scene"])
                if w and "bodyWeb" in w:
                    wp = f"{w['sdWeb'] / bgsd:15.4f}" if bgsd > 1e-4 else f"{'-':>15s}"
                    line += f" | {w['sdWeb']:13.4f} {wp}"
                else:
                    line += f" | {'-':>13s} {'-':>15s}"
            lines.append(line)
        lines.append("")

    lines.append("The discriminator, stated as two predictions. The equal-mean pair is one pitch (16)")
    lines.append("and one component at a time, with the body level differing by a factor of about 1.4")
    lines.append("and the backdrop's own structure by a factor of 0.568. A MULTIPLY composite predicts")
    lines.append("the passed sd scales with BOTH — `sd_lc / sd_full = (body_lc / body_full) x (bgSd_lc")
    lines.append("/ bgSd_full)`. A LERP predicts it scales with the backdrop's structure ALONE.")
    lines.append("")
    lines.append(f"{'component':16s} {'sd full':>9s} {'sd lc16':>9s} {'multiply pred':>14s} "
                 f"{'lerp pred':>10s} {'closer':>8s}")
    for comp in ["rrect-sm", "capsule-button", "rrect-md", "rrect-ml"]:
        full, lc = cell("checkerboard", comp), cell("checkerboard-lc16", comp)
        if full is None or lc is None:
            continue
        ratio_bg = lc["backdropSd"] / full["backdropSd"]
        ratio_body = lc["bodyNative"] / full["bodyNative"]
        mult = full["sdNative"] * ratio_bg * ratio_body
        lerp = full["sdNative"] * ratio_bg
        closer = "lerp" if abs(lerp - lc["sdNative"]) < abs(mult - lc["sdNative"]) else "multiply"
        lines.append(f"{comp:16s} {full['sdNative']:9.4f} {lc['sdNative']:9.4f} {mult:14.4f} "
                     f"{lerp:10.4f} {closer:>8s}")
    write(args.out, "passthrough.txt", lines)

    # ---- 2b. the equal-mean pair ---------------------------------------------
    lines = ["W21 G0 table 2c — the equal-mean pair in the dark scheme (W9's H4 discriminator)", ""]
    lines.append("`checkerboard` (16, black and white) and `checkerboard-lc16` (16, 128 and 229) are")
    lines.append("built to have the same LINEAR mean — 0.5000 against 0.4997 — and very different")
    lines.append("ENCODED means, 0.5000 against 0.7000. No luminance-only model can separate them at")
    lines.append("all; an encoded-mean model predicts a gap and its direction. W9's declared rule is")
    lines.append("that a contrast term survives only if the residual after the best luminance-only")
    lines.append("model exceeds three times the pooled run-to-run sigma of the pair.")
    lines.append("")
    lines.append(f"{'component':16s} {'full (enc .50)':>15s} {'lc16 (enc .70)':>15s} "
                 f"{'gap lc16-full':>14s} {'pooled sigmaMaj':>16s} {'3 sigma':>9s} {'verdict':>10s}")
    for comp in ["rrect-sm", "capsule-button", "rrect-md", "rrect-ml", "rrect-lg"]:
        full, lc = cell("checkerboard", comp), cell("checkerboard-lc16", comp)
        if full is None or lc is None:
            lines.append(f"{comp:16s}  (pair incomplete — one side is holdout at G0)")
            continue
        gap = lc["bodyNative"] - full["bodyNative"]
        pooled = (
            (full.get("sigmaBodyMajority", 0.0) ** 2 + lc.get("sigmaBodyMajority", 0.0) ** 2) / 2
        ) ** 0.5
        lines.append(
            f"{comp:16s} {full['bodyNative']:15.4f} {lc['bodyNative']:15.4f} {gap:+14.4f} "
            f"{pooled:16.4f} {3 * pooled:9.4f} "
            f"{'separated' if abs(gap) > 3 * pooled else 'within noise':>10s}"
        )
    lines.append("")
    lines.append("The gap is what the encoded-mean law predicts the sign of; whether the law also")
    lines.append("predicts its SIZE is probe-score.ts's question, not this table's.")
    write(args.out, "equal-mean-pair.txt", lines)

    # ---- 3. the rim ----------------------------------------------------------
    lines = ["W21 G0 table 4 — the rim peak per side, against backdrop and size", ""]
    lines.append("Sides are top / bottom / left / right, each the largest row (top, bottom) or column")
    lines.append("(left, right) mean inside the declared box's outer 3 CSS px. `excess` is the peak")
    lines.append("minus the cell's own body level — over a solid backdrop that is the rim's whole")
    lines.append("amplitude, because the band carries no backdrop structure. `flat` is max side minus")
    lines.append("min side: the wave's clause 4 asks vitrea to reproduce it within 0.03.")
    lines.append("")
    head = (f"{'scene':46s} {'body':>8s} | {'top':>7s} {'bottom':>7s} {'left':>7s} {'right':>7s} "
            f"| {'excess':>7s} {'flat':>6s} {'sigma':>7s}")
    for label in webs:
        head += f" | {label + ' T/B/L/R':>34s} {'flat':>6s}"
    lines.append(head)
    for sid, r in sorted(rows.items()):
        if r["tint"] is not None:
            continue
        rim = r["rimNative"]
        line = (f"{sid:46s} {r['bodyNative']:8.4f} | " + " ".join(f"{v:7.3f}" for v in rim)
                + f" | {max(rim) - r['bodyNative']:7.3f} {max(rim) - min(rim):6.3f} "
                f"{sig(r, 'sigmaRimMajority'):>7s}")
        for label, wrows in webs.items():
            w = wrows.get(sid)
            if w and "rimWeb" in w:
                wr = w["rimWeb"]
                line += " | " + " ".join(f"{v:7.3f}" for v in wr) + f"  {max(wr) - min(wr):6.3f}"
            else:
                line += f" | {'-':>34s} {'-':>6s}"
        lines.append(line)
    write(args.out, "rim.txt", lines)

    # ---- 4. the tints --------------------------------------------------------
    lines = ["W21 G0 table 5 — the tinted capsules, descriptive", ""]
    lines.append("The dark tint pathway is a stop this wave (W21 S2: no tinted dark cell may move by")
    lines.append("more than 0.001). These rows are read so that G1 and G2 have a before-picture, and")
    lines.append("for no other purpose: nothing is fitted on them and no bound is proposed from them.")
    lines.append("")
    head = f"{'scene':50s} {'encIn':>7s} {'body':>8s} {'sd':>7s} {'sigma':>7s} | rim T/B/L/R"
    for label in webs:
        head += f" | {label + ' body':>12s}"
    lines.append(head)
    for sid, r in sorted(rows.items()):
        if r["tint"] is None:
            continue
        line = (f"{sid:50s} {r['backdropEncodedMean']:7.4f} {r['bodyNative']:8.4f} "
                f"{r['sdNative']:7.4f} {sig(r, 'sigmaBodyMajority'):>7s} | "
                + " ".join(f"{v:.3f}" for v in r["rimNative"]))
        for label, wrows in webs.items():
            w = wrows.get(sid)
            line += f" | {w['bodyWeb']:12.4f}" if w and "bodyWeb" in w else f" | {'-':>12s}"
        lines.append(line)
    write(args.out, "tints.txt", lines)

    # ---- 5. the residuals ----------------------------------------------------
    if webs:
        lines = ["W21 G0 table 6 — vitrea against the dark probe, per cell", ""]
        lines.append("Residual is web minus native. `rim d` is the largest per-side difference. These")
        lines.append("are diagnostics, not a fit: G1 fits, on the probe's calibration split.")
        lines.append("")
        for label, wrows in webs.items():
            lines.append(f"== {label}")
            lines.append(f"{'scene':46s} {'set':11s} {'body d':>8s} {'sd d':>8s} {'rim d':>8s}")
            worst = []
            for sid, r in sorted(rows.items()):
                w = wrows.get(sid)
                if not w or "bodyWeb" not in w:
                    continue
                db = w["bodyWeb"] - r["bodyNative"]
                ds = w["sdWeb"] - r["sdNative"]
                dr = max(abs(a - b) for a, b in zip(w["rimWeb"], r["rimNative"]))
                worst.append((abs(db), sid))
                lines.append(f"{sid:46s} {r['set']:11s} {db:+8.4f} {ds:+8.4f} {dr:8.3f}")
            if worst:
                worst.sort(reverse=True)

                def mean(vals):
                    return sum(vals) / len(vals) if vals else float("nan")

                allv = [w for w, _s in worst]
                # `light-solid__rrect-sm` is the one cell where the reference draws the material's
                # LIGHT appearance (0.9666 against a dark-scheme body of 0.08 everywhere else). No
                # setting of a monotone response curve reproduces an appearance switch, so it is
                # reported separately rather than allowed to dominate a mean over 46 cells.
                switch = [w for w, s in worst if s == SWITCH_CELL]
                rest = [w for w, s in worst if s != SWITCH_CELL]
                thin = [w for w, s in worst
                        if s != SWITCH_CELL and SPAN.get(rows[s]["component"], 0) < 96]
                thick = [w for w, s in worst
                         if s != SWITCH_CELL and SPAN.get(rows[s]["component"], 0) >= 96]
                lines.append(f"   worst |body d|: {worst[0][1]} at {worst[0][0]:.4f}")
                lines.append(f"   mean |body d|  all {mean(allv):.4f} ({len(allv)} cells) | "
                             f"without the appearance switch {mean(rest):.4f} ({len(rest)}) | "
                             f"thin rows {mean(thin):.4f} ({len(thin)}) | "
                             f"thick rows {mean(thick):.4f} ({len(thick)})")
                if switch:
                    lines.append(f"   the appearance switch ({SWITCH_CELL}) alone: {switch[0]:.4f}")
            lines.append("")
        write(args.out, "candidate.txt", lines)


def write(out_dir, name, lines):
    path = os.path.join(out_dir, name)
    with open(path, "w") as fh:
        fh.write("\n".join(lines) + "\n")
    print(f"-> {path}")


if __name__ == "__main__":
    main()
