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
THICK = ["rrect-md", "rrect-ml", "rrect-lg"]
# The renderer's own size law: `sizeThickness = smoothstep(sizeSpanMin, sizeSpanMax, span)` with
# the landed 32 / 96, and `backdropToneResponse` smoothsteps the two anchor rows in that thickness.
SPAN = {"rrect-sm": 32, "capsule-button": 44, "rrect-md": 96, "rrect-ml": 128, "rrect-lg": 160}
SIZE_SPAN_MIN, SIZE_SPAN_MAX = 32.0, 96.0
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
    lines.append("row is rrect-sm (span 32, thickness 0); the thick row is rrect-md / ml / lg pooled")
    lines.append("(spans 96 / 128 / 160, thickness 1 for all three because the size law saturates at")
    lines.append("96). Every level below is a MEASUREMENT of the dark reference under the declared")
    lines.append("box eroded 6 CSS px; sigma is the run-to-run standard deviation across the attested")
    lines.append("probe runs. Nothing is fitted.")
    lines.append("")
    lines.append(f"{'anchor':16s} {'encodedMean':>12s} {'linearMean':>11s} | "
                 f"{'thin (sm)':>10s} {'sigma':>7s} | {'md':>8s} {'ml':>8s} {'lg':>8s} "
                 f"{'thick mean':>11s} {'spread':>8s} {'sigma':>7s}")
    anchor_x, thin_y, thick_y = [], [], []
    for bg in SOLIDS:
        sm = cell(bg, THIN)
        thick = [cell(bg, c) for c in THICK]
        thick = [t for t in thick if t is not None]
        if sm is None or not thick:
            lines.append(f"{bg:16s}  (not read)")
            continue
        vals = [t["bodyNative"] for t in thick]
        mean = sum(vals) / len(vals)
        spread = max(vals) - min(vals)
        sigma_thick = max((t.get("sigmaBody", float("nan")) for t in thick), default=float("nan"))
        anchor_x.append(sm["backdropEncodedMean"])
        thin_y.append(sm["bodyNative"])
        thick_y.append(mean)
        per = {t["component"]: t["bodyNative"] for t in thick}
        lines.append(
            f"{bg:16s} {sm['backdropEncodedMean']:12.4f} {sm['backdropLinearMean']:11.4f} | "
            f"{sm['bodyNative']:10.4f} {sig(sm, 'sigmaBody'):>7s} | "
            + " ".join(f"{per.get(c, float('nan')):8.4f}" for c in THICK)
            + f" {mean:11.4f} {spread:8.4f} {sigma_thick:7.4f}"
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
                f"{pred:10.4f} {pred - r['bodyNative']:+8.4f} {sig(r, 'sigmaBody'):>7s}"
            )
    write(args.out, "anchors.txt", lines)

    # ---- 2. the passthrough --------------------------------------------------
    lines = ["W21 G0 table 3 — the passthrough: body sd against backdrop pitch, per component", ""]
    lines.append("The alpha's evidence. Under a LERP toward a constant tint the passed structure is")
    lines.append("independent of the body level; under a MULTIPLY it scales with it. The two columns")
    lines.append("that decide it are `sd` and `sd/body`: a flat `sd/body` across a pitch sweep whose")
    lines.append("body level moves is a multiply, a flat `sd` is a lerp.")
    lines.append("")
    head = f"{'component':16s} {'background':18s} {'pitch':>6s} {'body':>8s} {'sd':>8s} {'sd/body':>8s} {'sigma':>7s}"
    for label in webs:
        head += f" | {label + ' sd':>12s} {label + ' sd/body':>14s}"
    lines.append(head)
    for comp in ["rrect-sm", "capsule-button", "rrect-md", "rrect-ml", "rrect-lg"]:
        for bg in sorted(PITCH, key=lambda b: (b.split("-")[0], PITCH[b])):
            r = cell(bg, comp)
            if r is None:
                continue
            line = (f"{comp:16s} {bg:18s} {PITCH[bg]:6d} {r['bodyNative']:8.4f} {r['sdNative']:8.4f} "
                    f"{r['sdNative'] / max(r['bodyNative'], 1e-9):8.4f} {sig(r, 'sigmaBody'):>7s}")
            for label, wrows in webs.items():
                w = wrows.get(r["scene"])
                if w and "bodyWeb" in w:
                    line += f" | {w['sdWeb']:12.4f} {w['sdWeb'] / max(w['bodyWeb'], 1e-9):14.4f}"
                else:
                    line += f" | {'-':>12s} {'-':>14s}"
            lines.append(line)
        lines.append("")
    write(args.out, "passthrough.txt", lines)

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
                f"{sig(r, 'sigmaRim'):>7s}")
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
                f"{r['sdNative']:7.4f} {sig(r, 'sigmaBody'):>7s} | "
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
                lines.append(f"   worst |body d|: {worst[0][1]} at {worst[0][0]:.4f}; "
                             f"mean |body d| {sum(w for w, _ in worst) / len(worst):.4f} over "
                             f"{len(worst)} cells")
            lines.append("")
        write(args.out, "candidate.txt", lines)


def write(out_dir, name, lines):
    path = os.path.join(out_dir, name)
    with open(path, "w") as fh:
        fh.write("\n".join(lines) + "\n")
    print(f"-> {path}")


if __name__ == "__main__":
    main()
