"""W23 G0 (d) — the rim's law fitted on vitrea's own rendered points, per scheme, per side.

## What is being fitted, and against what

The reference's contour rim, per side, read by `read-contour.py` against each side's OWN base
(`rimLocal`), on the SOLID calibration rows of both schemes. The reference's law is read first —
five candidate forms, least squares on the reference alone, so that the shape is chosen before any
vitrea constant is — and then the chosen form's constants are solved for on vitrea's ladder.

## Why the ladder, and how two constants come out of two captures

The shader's rim is LINEAR in each of its constants:

    rim_drawn = rimWeight(d) × (rimAlpha + rimLevelGain × L + rimEnvGain × E + spec) × present
              + rimWeight(d) × rimCollapsed × toneAdapt

so on a given cell the instrument's reading is `W × rimAlpha + W × L × rimLevelGain` for some cell
constant `W` — the integral of the band weight over the first two CSS px, which no desk calculation
knows because it also carries the tone response, the inner shadow's shoulder and the 8-bit
quantisation. Two captures fix it: the LANDED bed gives `W × rimAlpha` at the shipped `rimAlpha`,
and one rendered point at a named `rimLevelGain` gives `W × L`. Everything after that is a linear
solve, and the confirmation point renders the solved pair so that the answer is a capture and not
an extrapolation.

`present` and `toneAdapt` are complementary, so one ladder document carries a level gain AND a
collapsed rim without the two ever mixing on one cell: the uncollapsed cells move by the first
alone and the collapsed cells by the second alone.

## The rule the answers are held to

W22's S5: a constant whose per-row answers do not agree is not carried. Every per-row answer is
printed, and the spread is the verdict.

Usage: fit-law.py [--out <file>]
"""

import argparse
import json
import math
import os

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
WORKTREE = "/Users/new/Developer/GitHub/designer/.claude/worktrees/agent-aa0ee5ea92534c3fd"
MAIN = "/Users/new/Developer/GitHub/designer"
SCRATCH = "/Users/new/.claude/jobs/5c70e47f/tmp"
SIDES = ("top", "bottom", "left", "right")
# The `optics.regular.rimAlpha` each profile document ships, which is what turns a capture's
# reading into that cell's band weight `W = rim / rimAlpha`. The dark patch's 0.082 is W21 G1's.
SHIPPED_RIM_ALPHA = {"light": 0.18, "dark": 0.082}
LADDER_LEVEL_GAIN = {"light": -0.30, "dark": 0.50}
LADDER_ENV_GAIN = 0.10
LADDER_COLLAPSED = 0.05

BEDS = {
    "light-1x": ("canonical-apple-macos-26.5-1x-light-standard-webgpu", "scenes.json",
                 f"{MAIN}/apps/reference-apple/fixtures/backgrounds", "light"),
    "light-2x": ("canonical-apple-macos-26.5-2x-light-standard-webgpu", "scenes.json",
                 f"{MAIN}/apps/reference-apple/fixtures/backgrounds", "light"),
    "dark-1x": ("canonical-apple-macos-26.5-1x-dark-standard-webgpu", "scenes.json",
                f"{MAIN}/apps/reference-apple/fixtures/backgrounds", "dark"),
    "dark-2x": ("canonical-apple-macos-26.5-2x-dark-standard-webgpu", "scenes.json",
                f"{MAIN}/apps/reference-apple/fixtures/backgrounds", "dark"),
    "probe21-dark": ("probe-w21-dark", "scenes-w21-probe.json",
                     f"{WORKTREE}/packages/calibration/results/2026-09-06-w21-dark-scheme/"
                     "probe/backgrounds", "dark"),
    "probe9-light": ("probe-w9-light", "scenes-w9-probe.json",
                     f"{SCRATCH}/w9-probe-fixtures/backgrounds", "light"),
}
SOLID = ("light-solid", "dark-solid", "mid-dark-solid", "impulse")


def linearise(a):
    a = a / 255.0
    return np.where(a <= 0.04045, a / 12.92, ((a + 0.055) / 1.055) ** 2.4)


_BG = {}


def outside_per_side(bgdir, bg, size, radius, canvas, corner=1.6, depth=4.0):
    """The backdrop's own level just outside each side's straight span, from the BACKGROUND raster.

    The background rather than the fixture, because the fixture's pixels just outside the contour
    carry the material's outer shadow, and the environment term is meant to be what is behind the
    surface and not what the surface did to it.
    """
    key = (bgdir, bg)
    if key not in _BG:
        rgb = np.asarray(Image.open(os.path.join(bgdir, f"{bg}@1x.png")).convert("RGB"),
                         dtype=np.float64)
        c = linearise(rgb)
        _BG[key] = 0.2126 * c[..., 0] + 0.7152 * c[..., 1] + 0.0722 * c[..., 2]
    lum = _BG[key]
    scale = lum.shape[1] / canvas["width"]
    w, h = size
    x0 = (canvas["width"] / 2 - w / 2) * scale
    x1 = (canvas["width"] / 2 + w / 2) * scale
    y0 = (canvas["height"] / 2 - h / 2) * scale
    y1 = (canvas["height"] / 2 + h / 2) * scale
    r = radius * corner * scale
    o = int(round(depth * scale))
    sx = (int(math.ceil(x0 + r)), int(math.floor(x1 - r)))
    sy = (int(math.ceil(y0 + r)), int(math.floor(y1 - r)))
    out = {
        "top": float(lum[max(int(y0) - o, 0):int(y0), sx[0]:sx[1]].mean()),
        "bottom": float(lum[int(math.ceil(y1)):int(math.ceil(y1)) + o, sx[0]:sx[1]].mean()),
    }
    if sy[1] - sy[0] >= 2:
        out["left"] = float(lum[sy[0]:sy[1], max(int(x0) - o, 0):int(x0)].mean())
        out["right"] = float(lum[sy[0]:sy[1], int(math.ceil(x1)):int(math.ceil(x1)) + o].mean())
    else:
        out["left"] = out["right"] = float("nan")
    return out


def side_records():
    """Every (bed, scene, side) the reader could read, with the reference's rim and the backdrop."""
    recs = []
    for bed, (stem, scenes_file, bgdir, scheme) in BEDS.items():
        path = os.path.join(HERE, "reads", f"{stem}.json")
        data = json.load(open(path))
        spec = json.load(open(os.path.join(WORKTREE, "apps/reference-apple", scenes_file)))
        scenes = {s["id"]: s for s in spec["scenes"]}
        for row in data["rows"]:
            if row.get("tint"):
                continue
            scene = scenes[row["scene"]]
            size = spec["components"][scene["component"]]["size"]
            outs = outside_per_side(bgdir, scene["background"], size, row["radius"],
                                    spec["canvas"])
            for i, side in enumerate(SIDES):
                if math.isnan(row["rimLocalNative"][i]):
                    continue
                recs.append({
                    "bed": bed, "scheme": scheme, "scene": row["scene"],
                    "background": scene["background"], "component": scene["component"],
                    "side": side, "set": row["set"],
                    "base": row["baseNative"][i], "rim": row["rimLocalNative"][i],
                    "clip": row["clipNative"][i], "out": outs[side],
                    "rimWeb": row["rimLocalWeb"][i] if "rimLocalWeb" in row else float("nan"),
                    "baseWeb": row["baseWeb"][i] if "baseWeb" in row else float("nan"),
                })
    return recs


def is_collapsed(rec, collapsed_scenes):
    return (rec["bed"], rec["scene"]) in collapsed_scenes


CANONICAL_BEDS = ("light-1x", "light-2x", "dark-1x", "dark-2x")


def collapsed_set(recs):
    """The cells the reference draws its COLLAPSED appearance on.

    Two signatures, both from the pixels, and each used only where it is valid.

    On the four canonical beds, whose captures are the LANDED 0.11.0 material: vitrea's own contour
    rim is 0 on every side, which is `present = 0` seen from the pixels.

    On the probe beds the web column is stale — W9's captures are from a material many waves old and
    W21's probe has no capture in this gate at all — so the web signature is NOT used there and
    would be badly wrong if it were (it would call `dark-solid__rrect-md` collapsed on the W9 grid,
    which is the light law's most important row). What is used instead is the reference's own
    appearance: a body within a code of its own dark backdrop, and a rim inside the band the
    canonical collapsed cells read, 0.012…0.023.
    """
    out = set()
    for r in recs:
        if r["bed"] in CANONICAL_BEDS:
            if not math.isnan(r["rimWeb"]) and abs(r["rimWeb"]) < 0.0005:
                out.add((r["bed"], r["scene"]))
        elif abs(r["base"] - r["out"]) < 0.002 and r["out"] < 0.05 and 0.012 < r["rim"] < 0.023:
            out.add((r["bed"], r["scene"]))
    return out


MODELS = {
    "L1  rim = c                       (additive, W22's form)": lambda r: [1.0],
    "L2  rim = a(1 - base)             (screen, the CSS tier's form)": lambda r: [1.0 - r["base"]],
    "L3  rim = a(1 - base) + k*out     (screen + environment)":
        lambda r: [1.0 - r["base"], r["out"]],
    "L4  rim = c + m*base              (affine in the surface's own level)":
        lambda r: [1.0, r["base"]],
    "L4e rim = c + m*base + k*out      (L4 + environment)":
        lambda r: [1.0, r["base"], r["out"]],
}


def lstsq(rows, basis, target="rim"):
    A = np.array([basis(r) for r in rows])
    y = np.array([r[target] for r in rows])
    coef, *_ = np.linalg.lstsq(A, y, rcond=None)
    pred = A @ coef
    return coef, pred, float(np.abs(pred - y).mean()), float(np.abs(pred - y).max())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=None)
    args = ap.parse_args()
    lines = []

    def say(text=""):
        lines.append(text)
        print(text)

    recs = side_records()
    collapsed = collapsed_set(recs)

    say("W23 G0 (d) — the rim's law: the form chosen on the reference, the constants solved on")
    say("vitrea's ladder")
    say()
    say("Every rim is `rimLocal` — the excess over that side's own neighbouring rows — because the")
    say("structured rows cannot be read against a whole-cell body (see g0/contour-read.txt).")
    say()
    say("The collapsed cells, detected from the pixels and excluded from every material fit:")
    for bed, scene in sorted(collapsed):
        say(f"    {bed:14s} {scene}")
    say()

    # ---------------------------------------------------------------- part 1
    say("=" * 100)
    say("PART 1 — the REFERENCE's own law, fitted on its solid rows before any vitrea constant")
    say("=" * 100)
    say()
    say("Rows: untinted, solid backdrop, not clipped, not collapsed. A clipped row cannot say how")
    say("much brighter it wanted to be and is reported separately.")
    say()
    fits = {}
    for scheme in ("light", "dark"):
        rows = [r for r in recs
                if r["scheme"] == scheme and r["background"] in SOLID and r["clip"] == 0
                and not is_collapsed(r, collapsed)]
        bases = [r["base"] for r in rows]
        say(f"-- {scheme} reference: {len(rows)} sides over {len({(r['bed'], r['scene']) for r in rows})}"
            f" cells, base {min(bases):.4f}..{max(bases):.4f}")
        for name, basis in MODELS.items():
            coef, _pred, mae, mx = lstsq(rows, basis)
            say(f"   {name:62s} coef={np.round(coef, 4)}  mae={mae:.4f}  max={mx:.4f}")
        coef, pred, mae, mx = lstsq(rows, MODELS[
            "L4  rim = c + m*base              (affine in the surface's own level)"])
        fits[scheme] = (float(coef[0]), float(coef[1]))
        say(f"   -> L4 taken: rim = {coef[0]:.4f} + {coef[1]:.4f} x base  (mae {mae:.4f}, "
            f"max {mx:.4f})")
        say()
        say(f"   {'bed':14s} {'scene':32s} {'side':6s} {'base':>7s} {'out':>7s} {'rim':>8s} "
            f"{'L4 pred':>8s} {'d':>8s}")
        for r, p in zip(rows, pred):
            say(f"   {r['bed']:14s} {r['scene']:32s} {r['side']:6s} {r['base']:7.4f} "
                f"{r['out']:7.4f} {r['rim']:8.4f} {p:8.4f} {p - r['rim']:+8.4f}")
        say()

    say("-- the clipped rows, which no fit may be pulled down to")
    say(f"   {'bed':14s} {'scene':32s} {'side':6s} {'base':>7s} {'rim':>8s} {'clip':>5s}")
    for r in recs:
        if r["clip"] > 0 and r["background"] in SOLID:
            say(f"   {r['bed']:14s} {r['scene']:32s} {r['side']:6s} {r['base']:7.4f} "
                f"{r['rim']:8.4f} {r['clip']:5.2f}")
    say()

    say("-- the STRUCTURED and validation rows, checked against each scheme's L4 and NOT fitted")
    say(f"   {'bed':14s} {'scene':32s} {'side':6s} {'base':>7s} {'rim':>8s} {'pred':>8s} "
        f"{'d':>8s}")
    checks = {"light": [], "dark": []}
    for r in recs:
        if r["background"] in SOLID or r["clip"] > 0 or is_collapsed(r, collapsed):
            continue
        c, m = fits[r["scheme"]]
        p = c + m * r["base"]
        checks[r["scheme"]].append(abs(p - r["rim"]))
        say(f"   {r['bed']:14s} {r['scene']:32s} {r['side']:6s} {r['base']:7.4f} "
            f"{r['rim']:8.4f} {p:8.4f} {p - r['rim']:+8.4f}")
    for scheme, errs in checks.items():
        if errs:
            say(f"   {scheme}: {len(errs)} unfitted sides, mean |d| {sum(errs) / len(errs):.4f}, "
                f"max {max(errs):.4f}")
    say()

    # ---------------------------------------------------------------- part 2
    say("=" * 100)
    say("PART 2 — the LADDER: vitrea's leverage per constant, measured on rendered captures")
    say("=" * 100)
    say()
    say("Each point is a pair of captures of the SAME bed: a base at the shipped constants and one")
    say("at a named `rimLevelGain`. `W` is the cell's band weight, `rim_base / rimAlpha`; `W x L` is")
    say("the leverage per unit gain; `L` is the surface luminance the shader saw, recovered as the")
    say("ratio. The pair (`W`, `W x L`) is the row's design matrix, and the reference's own rim is")
    say("the target.")
    say()

    def ladder(label):
        path = os.path.join(HERE, "ladder", f"{label}.json")
        if not os.path.exists(path):
            return None
        return {r["scene"]: r for r in json.load(open(path))["rows"]}

    # (bed, base read, gain read). A canonical bed's base is the LANDED capture already in `recs`;
    # a probe grid has no landed capture and its base is rendered here at the shipped document.
    POINTS = [
        ("light-1x", None, "light-levelgain-1x"),
        ("light-2x", None, "light-levelgain-2x"),
        ("dark-1x", None, "dark-levelgain-1x"),
        ("dark-2x", None, "dark-levelgain-2x"),
        ("probe9-light", "probe9-base", "probe9-levelgain"),
        ("probe21-dark", "probe21-base", "probe21-levelgain"),
    ]

    pooled = {"light": [], "dark": []}
    collapsed_answers = []
    for bed, base_label, gain_label in POINTS:
        gain_rows = ladder(gain_label)
        if gain_rows is None:
            say(f"-- {bed}: no ladder capture ({gain_label}), skipped")
            say()
            continue
        base_rows = ladder(base_label) if base_label else None
        scheme = BEDS[bed][3]
        gain = LADDER_LEVEL_GAIN[scheme]
        alpha0 = SHIPPED_RIM_ALPHA[scheme]
        say(f"-- {bed}: `rimLevelGain` {gain:+.2f}"
            + (f" and `rimCollapsed` {LADDER_COLLAPSED:.2f}" if base_label is None else "")
            + f", shipped rimAlpha {alpha0}")
        say(f"   {'scene':34s} {'side':6s} {'rimBase':>8s} {'rimGain':>8s} {'W':>8s} "
            f"{'WxL':>8s} {'L':>7s} {'target':>8s} {'rowAlpha':>9s} {'rowGain':>9s}")
        used = []
        for r in [x for x in recs if x["bed"] == bed]:
            row = gain_rows.get(r["scene"])
            if row is None or "rimLocalWeb" not in row:
                continue
            i = SIDES.index(r["side"])
            rim_gain = row["rimLocalWeb"][i]
            if base_rows is None:
                rim_base = r["rimWeb"]
            else:
                b = base_rows.get(r["scene"])
                rim_base = b["rimLocalWeb"][i] if b and "rimLocalWeb" in b else float("nan")
            if math.isnan(rim_base) or math.isnan(rim_gain):
                continue
            if is_collapsed(r, collapsed):
                if base_rows is None and rim_gain != 0:
                    collapsed_answers.append(
                        (bed, r, rim_gain, r["rim"] * LADDER_COLLAPSED / rim_gain))
                continue
            if r["background"] not in SOLID or r["clip"] > 0:
                continue
            wl = (rim_gain - rim_base) / gain
            w = rim_base / alpha0
            lweb = wl / w if w else float("nan")
            row_alpha = r["rim"] / w if w else float("nan")
            row_gain = (r["rim"] - rim_base) / wl if wl else float("nan")
            used.append((r, w, wl))
            pooled[scheme].append((bed, r, w, wl))
            say(f"   {r['scene']:34s} {r['side']:6s} {rim_base:8.4f} {rim_gain:8.4f} {w:8.4f} "
                f"{wl:8.4f} {lweb:7.4f} {r['rim']:8.4f} {row_alpha:9.4f} {row_gain:9.4f}")
        if used:
            A = np.array([[w, wl] for _r, w, wl in used])
            y = np.array([r["rim"] for r, _w, _wl in used])
            coef, *_ = np.linalg.lstsq(A, y, rcond=None)
            pred = A @ coef
            say(f"   -> this bed alone: rimAlpha {coef[0]:.4f}, rimLevelGain {coef[1]:.4f}; "
                f"mean |d| {np.abs(pred - y).mean():.4f}, max {np.abs(pred - y).max():.4f}, "
                f"condition {np.linalg.cond(A):.1f}")
        say()

    if collapsed_answers:
        say("-- `rimCollapsed`: what each collapsed row alone would choose")
        say(f"   {'bed':13s} {'scene':34s} {'side':6s} {'drawn at 0.05':>13s} {'target':>8s} "
            f"{'rimCollapsed*':>13s}")
        for bed, r, drawn, want in collapsed_answers:
            say(f"   {bed:13s} {r['scene']:34s} {r['side']:6s} {drawn:13.4f} {r['rim']:8.4f} "
                f"{want:13.4f}")
        wants = sorted(w for _b, _r, _d, w in collapsed_answers)
        say(f"   the per-row answers span {wants[0]:.4f}..{wants[-1]:.4f}, "
            f"median {wants[len(wants) // 2]:.4f}")
        say("   The spread is not noise and it is not the instrument: the reference's collapsed rim")
        say("   is itself +0.0196..0.0204 over `dark-solid` and +0.0149..0.0168 over `impulse`,")
        say("   while one absolute constant draws the same rim on both. What a chosen value costs")
        say("   on every collapsed side:")
        say(f"   {'rimCollapsed':>12s} " + " ".join(f"{'|d| ' + b[:6]:>12s}"
                                                    for b in sorted({x[0] for x in
                                                                     collapsed_answers})))
        for value in (0.035, 0.038, 0.040, 0.041, 0.043, 0.045):
            worst = max(abs(drawn * value / LADDER_COLLAPSED - r["rim"])
                        for _b, r, drawn, _w in collapsed_answers)
            say(f"   {value:12.3f}  worst |d| over every collapsed side {worst:.4f}"
                + ("   (inside clause 1's 0.005)" if worst <= 0.005 else ""))
        say()

    say("-- the POOLED solve per scheme, over every bed's rendered rows")
    say("   This is the answer G1 would land: one pair of constants per scheme, chosen on every")
    say("   solid row that any ladder point renders, with the per-row answers beside it (S5).")
    solved = {}
    for scheme in ("light", "dark"):
        rows = pooled[scheme]
        if not rows:
            continue
        A = np.array([[w, wl] for _b, _r, w, wl in rows])
        y = np.array([r["rim"] for _b, r, _w, _wl in rows])
        coef, *_ = np.linalg.lstsq(A, y, rcond=None)
        pred = A @ coef
        solved[scheme] = (float(coef[0]), float(coef[1]))
        say(f"   {scheme}: {len(rows)} rows over "
            f"{len({(b, r['scene']) for b, r, _w, _wl in rows})} cells -> "
            f"rimAlpha {coef[0]:.4f}, rimLevelGain {coef[1]:.4f}; "
            f"mean |d| {np.abs(pred - y).mean():.4f}, max {np.abs(pred - y).max():.4f}, "
            f"condition {np.linalg.cond(A):.1f}")
        say(f"   {'bed':13s} {'scene':32s} {'side':6s} {'target':>8s} {'pred':>8s} {'d':>8s} "
            f"{'landed':>8s}")
        for (b, r, _w, _wl), pr in zip(rows, pred):
            say(f"   {b:13s} {r['scene']:32s} {r['side']:6s} {r['rim']:8.4f} {pr:8.4f} "
                f"{pr - r['rim']:+8.4f} "
                + (f"{r['rimWeb']:8.4f}" if not math.isnan(r["rimWeb"]) else f"{'-':>8s}"))
        say()

    say("-- what the pooled constants predict on the clipped `light-solid` rows, which no fit was")
    say("   allowed to be pulled down to (parent acceptance 2 asks vitrea to clip where the")
    say("   reference clips):")
    say(f"   {'bed':13s} {'scene':32s} {'side':6s} {'W(landed)':>10s} {'pred rim':>9s} "
        f"{'ref rim':>8s} {'clipRef':>8s}")
    for r in recs:
        if r["clip"] == 0 or r["background"] not in SOLID:
            continue
        if math.isnan(r["rimWeb"]) or r["bed"] not in ("light-1x", "light-2x"):
            continue
        alpha0 = SHIPPED_RIM_ALPHA["light"]
        w = r["rimWeb"] / alpha0
        a, g = solved.get("light", (float("nan"), float("nan")))
        say(f"   {r['bed']:13s} {r['scene']:32s} {r['side']:6s} {w:10.4f} "
            f"{w * (a + g * r['baseWeb']):9.4f} {r['rim']:8.4f} {r['clip']:8.2f}")
    say()
    say("   These rows are already clipped in the landed capture, which is why the environment")
    say("   term could not be measured on them either (below).")
    say()

    # ---------------------------------------------------------------- the environment term
    point = ladder("light-envgain-1x")
    if point is not None:
        say("-- `rimEnvGain` +0.10 on the light bed at 1x — the environment term's own leverage")
        say(f"   {'scene':34s} {'side':6s} {'landed':>8s} {'at k=0.10':>10s} {'d/k':>9s} "
            f"{'out':>7s} {'clipWeb':>8s}")
        for r in recs:
            if r["bed"] != "light-1x" or r["background"] not in SOLID:
                continue
            row = point.get(r["scene"])
            if row is None or "rimLocalWeb" not in row:
                continue
            i = SIDES.index(r["side"])
            rim1 = row["rimLocalWeb"][i]
            if math.isnan(rim1) or math.isnan(r["rimWeb"]):
                continue
            say(f"   {r['scene']:34s} {r['side']:6s} {r['rimWeb']:8.4f} {rim1:10.4f} "
                f"{(rim1 - r['rimWeb']) / LADDER_ENV_GAIN:9.4f} {r['out']:7.4f} "
                f"{row['clipWeb'][i]:8.2f}")
        say()

    # ---------------------------------------------------------------- part 3
    CONFIRM = (("light-fit-1x", "light-1x"), ("light-fit-2x", "light-2x"),
               ("dark-fit-1x", "dark-1x"), ("dark-fit-2x", "dark-2x"),
               ("probe9-fit", "probe9-light"), ("probe21-fit", "probe21-dark"))
    first = True
    for label, bed in CONFIRM:
        point = ladder(label)
        if point is None:
            continue
        if first:
            say("=" * 100)
            say("PART 3 — the CONFIRMATION points: the recommended constants RENDERED, against the")
            say("reference, on every readable cell of every bed")
            say("=" * 100)
            say()
            say("`landed` is the 0.11.0 bed where one exists (the probe grids have none, and their")
            say("`base` column is this gate's own render at the shipped document instead).")
            say()
            first = False
        base_rows = ladder("probe9-base" if bed == "probe9-light" else
                           "probe21-base" if bed == "probe21-dark" else None)
        say(f"-- {label}")
        say(f"   {'scene':34s} {'side':6s} {'set':6s} {'bg':14s} {'target':>8s} {'before':>8s} "
            f"{'fitted':>8s} {'d':>8s} {'improved':>9s}")
        groups = {"solid": ([], []), "structured": ([], []), "collapsed": ([], [])}
        for r in [x for x in recs if x["bed"] == bed]:
            row = point.get(r["scene"])
            if row is None or "rimLocalWeb" not in row:
                continue
            i = SIDES.index(r["side"])
            after = row["rimLocalWeb"][i]
            if base_rows is None:
                before = r["rimWeb"]
            else:
                b = base_rows.get(r["scene"])
                before = b["rimLocalWeb"][i] if b and "rimLocalWeb" in b else float("nan")
            if math.isnan(after) or math.isnan(before):
                continue
            kind = ("collapsed" if is_collapsed(r, collapsed)
                    else "solid" if r["background"] in SOLID else "structured")
            groups[kind][0].append(abs(before - r["rim"]))
            groups[kind][1].append(abs(after - r["rim"]))
            say(f"   {r['scene']:34s} {r['side']:6s} {r['set'][:6]:6s} {r['background']:14s} "
                f"{r['rim']:8.4f} {before:8.4f} {after:8.4f} {after - r['rim']:+8.4f} "
                f"{abs(before - r['rim']) - abs(after - r['rim']):+9.4f}")
        say()
        for kind, (b, a) in groups.items():
            if not b:
                continue
            say(f"   {kind:11s}: {len(b):3d} sides, mean |rim - reference| "
                f"{sum(b) / len(b):.4f} -> {sum(a) / len(a):.4f}, "
                f"worst {max(b):.4f} -> {max(a):.4f}")
        say()

    if args.out:
        with open(args.out, "w") as fh:
            fh.write("\n".join(lines) + "\n")


if __name__ == "__main__":
    main()
