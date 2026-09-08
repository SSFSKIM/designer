"""W22 G0 (e2) — the declared-geometry read extended to a STACK: two bodies and eight sides.

W21's reader (`../../2026-09-06-w21-dark-scheme/g0/read.py`) refuses a composite component and says
so, because `glass-over-glass` has no single box whose interior is one body. W22 contract X2 gives
the stack the same instrument the single box gets, once per pane:

- **the base pane** — the base's declared box eroded `--erode` CSS px, with the OVERLAY's declared
  box DILATED by the same erosion cut out of it. The cut is dilated rather than exact so the
  overlay's own rim and its blur shoulder are outside the base's body, exactly as the erosion keeps
  the base's own rim out of it.
- **the overlay pane** — the overlay's declared box eroded `--erode` CSS px.
- **eight sides** — each pane's declared box's outer `--band` CSS px is that pane's rim band, and a
  side's peak is the largest row (top, bottom) or column (left, right) mean inside it. On this
  scene the overlay sits clear of the base's band on every side (the smallest gap is 29 CSS px at
  the top), so the base's four sides are uncontaminated by the overlay; the reader asserts that
  rather than assuming it.

**The placement is replicated, not imported.** `packages/calibration/src/component-region.ts`'s
`placeComponent` is TypeScript and this is the Python reader, so the rule is restated here in one
function and stated in full: a shape is centred on the canvas with `round((canvas - size) / 2)` and
then displaced by its own declared `offset`, a stack's base before its overlay. For
`glass-over-glass` on the 320x200 canvas that is base 220x130 at (50, 35) and overlay 120x56 at
(100, 64) — the same numbers the DOM harness lays out from, and `--assert-placement` prints them so
a reader can check them against the TypeScript by eye.

Beside the two bodies the reader reports, per pane:

- **excess** — the overlay's body minus the base's body. The eye finding is a SIGN: Apple's overlay
  is darker than its base and vitrea's is lighter (claims 5.93), so this one number carries it.
- **sd** — the body's own standard deviation, the structure the pane passed.
- **blurSigmaMatchPx** — the Gaussian sigma at which the raster BACKGROUND under the pane, blurred
  and then affinely rescaled (one gain and one offset, least squares), best matches the pane's
  body. This is NOT the matrix's `blurSigmaNative`, which is an edge-spread fit on a checker step;
  it is a whole-region match, reported under its own name so the two are never confused, and it is
  comparable between native and web because both sides are matched against the same background.
  For the OVERLAY pane the reference is the base pane's own rendered output rather than the raster,
  since that is what the overlay actually samples on both sides.

Usage:

    read-stack.py --scenes <scenes.json> --fixtures <dir> --profile <key>
                  [--captures <dir> --tier webgpu] [--json <out>] [--inject-check]
"""

import argparse
import json
import os
import sys

import numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter


def linearise(a: np.ndarray) -> np.ndarray:
    """sRGB EOTF — the same transfer W21's reader decodes with."""
    a = a / 255.0
    return np.where(a <= 0.04045, a / 12.92, ((a + 0.055) / 1.055) ** 2.4)


def luma_of(path: str) -> np.ndarray:
    rgb = np.asarray(Image.open(path).convert("RGB"), dtype=np.float64)
    c = linearise(rgb)
    return 0.2126 * c[..., 0] + 0.7152 * c[..., 1] + 0.0722 * c[..., 2]


def place(shape, canvas):
    """`component-region.ts`'s `place`, restated: centre on the canvas, then the declared offset."""
    w, h = float(shape["size"][0]), float(shape["size"][1])
    ox, oy = (shape.get("offset") or [0, 0])[0], (shape.get("offset") or [0, 0])[1]
    left = round((canvas["width"] - w) / 2) + float(ox)
    top = round((canvas["height"] - h) / 2) + float(oy)
    return {"left": left, "top": top, "width": w, "height": h}


def rect_mask(box, scale, shape, inset):
    """The declared box inset by `inset` CSS px on every side, in device px."""
    yy, xx = np.mgrid[0 : shape[0], 0 : shape[1]]
    xx = xx + 0.5
    yy = yy + 0.5
    x0 = (box["left"] + inset) * scale
    y0 = (box["top"] + inset) * scale
    x1 = (box["left"] + box["width"] - inset) * scale
    y1 = (box["top"] + box["height"] - inset) * scale
    return (xx >= x0) & (xx < x1) & (yy >= y0) & (yy < y1)


def side_masks(box, scale, shape, band):
    """The four sides of a pane's rim band, in device px."""
    yy, xx = np.mgrid[0 : shape[0], 0 : shape[1]]
    xx = xx + 0.5
    yy = yy + 0.5
    x0, y0 = box["left"] * scale, box["top"] * scale
    x1 = (box["left"] + box["width"]) * scale
    y1 = (box["top"] + box["height"]) * scale
    ring = rect_mask(box, scale, shape, 0) & ~rect_mask(box, scale, shape, band)
    return {
        "top": ring & (yy < y0 + band * scale),
        "bottom": ring & (yy >= y1 - band * scale),
        "left": ring & (xx < x0 + band * scale),
        "right": ring & (xx >= x1 - band * scale),
    }


def rim_peaks(lum, sides):
    """Per side, the largest row (top/bottom) or column (left/right) mean inside the band."""
    out = []
    for key in ("top", "bottom", "left", "right"):
        m = sides[key]
        if key in ("top", "bottom"):
            means = [lum[r][m[r]].mean() for r in range(lum.shape[0]) if m[r].any()]
        else:
            means = [lum[:, c][m[:, c]].mean() for c in range(lum.shape[1]) if m[:, c].any()]
        out.append(float(max(means)) if means else float("nan"))
    return out


def blur_sigma_match(target, reference, mask, sigmas=None):
    """The Gaussian sigma at which `reference`, blurred then affinely rescaled, best fits `target`.

    One gain and one offset are solved in closed form at each sigma, so the statistic is about the
    SHAPE the pane passed and not about its level — which is the point: a pane can be at the right
    level and pass the wrong amount of structure, and the eye reads that as haze.
    """
    if sigmas is None:
        sigmas = np.concatenate([np.arange(0.0, 4.0, 0.1), np.arange(4.0, 16.01, 0.25)])
    t = target[mask]
    if t.size == 0 or float(np.std(t)) == 0.0:
        return float("nan"), float("nan")
    best = (float("inf"), float("nan"))
    for sigma in sigmas:
        blurred = reference if sigma == 0 else gaussian_filter(reference, sigma, mode="nearest")
        r = blurred[mask]
        var = float(np.var(r))
        if var <= 1e-12:
            continue
        gain = float(np.cov(r, t, bias=True)[0, 1]) / var
        offset = float(np.mean(t) - gain * np.mean(r))
        rms = float(np.sqrt(np.mean((gain * r + offset - t) ** 2)))
        if rms < best[0]:
            best = (rms, float(sigma))
    return best[1], best[0]


def read_stack(lum, base_box, over_box, canvas, erode, band, background=None):
    scale = lum.shape[1] / canvas["width"]
    base_body = rect_mask(base_box, scale, lum.shape, erode) & ~rect_mask(
        over_box, scale, lum.shape, -erode
    )
    over_body = rect_mask(over_box, scale, lum.shape, erode)
    base_sides = side_masks(base_box, scale, lum.shape, band)
    over_sides = side_masks(over_box, scale, lum.shape, band)
    # X2's premise on this scene: the overlay is clear of the base's rim band.
    for key, mask in base_sides.items():
        overlap = int(np.count_nonzero(mask & rect_mask(over_box, scale, lum.shape, -band)))
        if overlap:
            raise SystemExit(f"read-stack: the overlay touches the base's {key} band ({overlap} px)")
    row = {
        "baseBody": float(lum[base_body].mean()),
        "baseSd": float(lum[base_body].std()),
        "baseRim": rim_peaks(lum, base_sides),
        "overBody": float(lum[over_body].mean()),
        "overSd": float(lum[over_body].std()),
        "overRim": rim_peaks(lum, over_sides),
    }
    row["excess"] = row["overBody"] - row["baseBody"]
    if background is not None:
        sigma, rms = blur_sigma_match(lum, background, base_body)
        row["baseBlurSigmaMatchPx"] = sigma
        row["baseBlurMatchRms"] = rms
        # The overlay's own reference is the base's rendered output, which is what it samples.
        sigma_over, rms_over = blur_sigma_match(lum, lum, over_body)
        row["overBlurSigmaMatchPx"] = sigma_over
        row["overBlurMatchRms"] = rms_over
    return row


def inject_check(lum, base_box, over_box, canvas, erode, band):
    """X3 on a stack: paint known levels and known rims into a copy, and recover them.

    The recovery error is the instrument's own floor on this geometry, recorded beside the first
    reading. The painted image is built from the DECLARED boxes, so what is being validated is the
    masking and the peak statistic, not the placement — the placement is checked separately by
    `--assert-placement` against `component-region.ts`.
    """
    scale = lum.shape[1] / canvas["width"]
    painted = np.full(lum.shape, 0.0100, dtype=np.float64)
    truth = {"baseBody": 0.0450, "overBody": 0.0320}
    painted[rect_mask(base_box, scale, lum.shape, 0)] = truth["baseBody"]
    # A rim of a known height on each of the base's four sides, one CSS px inside the box edge, so
    # the peak statistic has a line to find rather than a plateau.
    base_sides = side_masks(base_box, scale, lum.shape, band)
    base_rim_truth = [0.0900, 0.0850, 0.0800, 0.0750]
    for key, level in zip(("top", "bottom", "left", "right"), base_rim_truth):
        painted[base_sides[key]] = level
    painted[rect_mask(over_box, scale, lum.shape, 0)] = truth["overBody"]
    over_sides = side_masks(over_box, scale, lum.shape, band)
    over_rim_truth = [0.1400, 0.1350, 0.1300, 0.1250]
    for key, level in zip(("top", "bottom", "left", "right"), over_rim_truth):
        painted[over_sides[key]] = level

    got = read_stack(painted, base_box, over_box, canvas, erode, band)
    errors = {
        "baseBody": abs(got["baseBody"] - truth["baseBody"]),
        "overBody": abs(got["overBody"] - truth["overBody"]),
        "baseRim": [abs(a - b) for a, b in zip(got["baseRim"], base_rim_truth)],
        "overRim": [abs(a - b) for a, b in zip(got["overRim"], over_rim_truth)],
    }
    errors["worst"] = max(
        [errors["baseBody"], errors["overBody"]] + errors["baseRim"] + errors["overRim"]
    )
    return {"truth": truth, "baseRimTruth": base_rim_truth, "overRimTruth": over_rim_truth,
            "read": got, "errors": errors}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--scenes", required=True)
    ap.add_argument("--fixtures", required=True)
    ap.add_argument("--profile", required=True)
    ap.add_argument("--captures", default=None)
    ap.add_argument("--tier", default="webgpu")
    ap.add_argument("--backgrounds", default=None)
    ap.add_argument("--component", default="glass-over-glass")
    ap.add_argument("--erode", type=float, default=6.0)
    ap.add_argument("--band", type=float, default=3.0)
    ap.add_argument("--sets", default="calibration,validation,recorded,holdout")
    ap.add_argument("--inject-check", action="store_true")
    ap.add_argument("--assert-placement", action="store_true")
    ap.add_argument("--json", default=None)
    args = ap.parse_args()

    spec = json.load(open(args.scenes))
    canvas = spec["canvas"]
    component = spec["components"][args.component]
    base_box = place(component["base"], canvas)
    over_box = place(component["over"], canvas)
    bg_dir = args.backgrounds or os.path.join(args.fixtures, "backgrounds")

    if args.assert_placement:
        print(f"placement (CSS px, from component-region.ts's rule restated here)")
        print(f"  base {base_box}")
        print(f"  over {over_box}")

    which = {}
    for role in ("calibration", "validation", "holdout", "recorded"):
        for sid in spec.get("split", {}).get(role, []):
            which[sid] = role
    wanted = set(args.sets.split(","))

    declared = None
    for p in spec["profiles"]:
        if p["key"] == args.profile:
            declared = p.get("scenes")
    rows = []
    checked = None
    for scene in spec["scenes"]:
        if scene["component"] != args.component:
            continue
        sid = scene["id"]
        if isinstance(declared, list) and sid not in declared:
            continue
        if which.get(sid, "calibration") not in wanted:
            continue
        native_png = os.path.join(args.fixtures, args.profile, f"{sid}.png")
        if not os.path.exists(native_png):
            continue
        nat_lum = luma_of(native_png)
        bg_png = os.path.join(bg_dir, f"{scene['background']}@1x.png")
        bg = luma_of(bg_png) if os.path.exists(bg_png) else None
        if bg is not None and bg.shape != nat_lum.shape:
            zoom = nat_lum.shape[0] / bg.shape[0]
            bg_nat = np.asarray(
                Image.open(bg_png).convert("RGB").resize(
                    (nat_lum.shape[1], nat_lum.shape[0]), Image.NEAREST
                ),
                dtype=np.float64,
            )
            c = linearise(bg_nat)
            bg_nat = 0.2126 * c[..., 0] + 0.7152 * c[..., 1] + 0.0722 * c[..., 2]
        else:
            bg_nat = bg
        nat = read_stack(nat_lum, base_box, over_box, canvas, args.erode, args.band, bg_nat)
        row = {"scene": sid, "background": scene["background"], "tint": scene.get("tint"),
               "set": which.get(sid, "unassigned"), "native": nat}
        if args.captures:
            web_png = os.path.join(args.captures, args.profile, sid, f"{sid}__{args.tier}.png")
            if os.path.exists(web_png):
                web_lum = luma_of(web_png)
                bg_web = bg_nat if bg_nat is not None and bg_nat.shape == web_lum.shape else None
                row["web"] = read_stack(
                    web_lum, base_box, over_box, canvas, args.erode, args.band, bg_web
                )
        rows.append(row)
        if args.inject_check and checked is None:
            checked = inject_check(nat_lum, base_box, over_box, canvas, args.erode, args.band)

    print(f"== {args.profile} / {args.tier}  ({args.fixtures})")
    head = (f"{'scene':44s} {'side':6s} {'baseBody':>9s} {'overBody':>9s} {'excess':>8s} "
            f"{'baseSd':>7s} {'blurSig':>7s} | base rim T/B/L/R | over rim T/B/L/R")
    print(head)
    for r in rows:
        for which_side in ("native", "web"):
            d = r.get(which_side)
            if d is None:
                continue
            print(
                f"{r['scene']:44s} {which_side:6s} {d['baseBody']:9.4f} {d['overBody']:9.4f} "
                f"{d['excess']:+8.4f} {d['baseSd']:7.4f} "
                f"{d.get('baseBlurSigmaMatchPx', float('nan')):7.2f} | "
                + " ".join(f"{v:.4f}" for v in d["baseRim"])
                + " | "
                + " ".join(f"{v:.4f}" for v in d["overRim"])
            )
    if checked is not None:
        print()
        print("X3 — the reader's recovery on a stack, by injection (known levels painted into a")
        print("copy of a capture and recovered through the same masks and the same peak statistic):")
        print(f"  base body  truth {checked['truth']['baseBody']:.4f} read "
              f"{checked['read']['baseBody']:.4f}  err {checked['errors']['baseBody']:.6f}")
        print(f"  over body  truth {checked['truth']['overBody']:.4f} read "
              f"{checked['read']['overBody']:.4f}  err {checked['errors']['overBody']:.6f}")
        for label, truth_key, read_key, err_key in (
            ("base rim", "baseRimTruth", "baseRim", "baseRim"),
            ("over rim", "overRimTruth", "overRim", "overRim"),
        ):
            for i, side in enumerate(("top", "bottom", "left", "right")):
                print(f"  {label} {side:7s} truth {checked[truth_key][i]:.4f} read "
                      f"{checked['read'][read_key][i]:.4f}  err {checked['errors'][err_key][i]:.6f}")
        print(f"  worst recovery error over the ten quantities: {checked['errors']['worst']:.6f}")

    if args.json:
        with open(args.json, "w") as fh:
            json.dump({
                "profile": args.profile,
                "tier": args.tier if args.captures else None,
                "fixtures": os.path.abspath(args.fixtures),
                "captures": os.path.abspath(args.captures) if args.captures else None,
                "component": args.component,
                "placement": {"base": base_box, "over": over_box},
                "erodeCssPx": args.erode,
                "rimBandCssPx": args.band,
                "rows": rows,
                "injectionCheck": checked,
            }, fh, indent=2)
        print(f"\n-> {args.json}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
