"""W23 G0 (a) — the wave's instrument: the rim read AT THE CONTOUR, per side, on the straight span.

W21's `g0/read.py` reads the rim as a BAND statistic — the declared box's outer 3 CSS px, one peak
per side — and that is the right reader for a body and for a flatness, but it is the wrong reader
for the amplitude of a one-pixel line. Over a dark backdrop a rounded shape leaves the corners'
background inside the rectangle's band, so the peak row's mean is a mixture of rim and backdrop
whose weight differs per side; and a peak is a single row, so a line with an inner shoulder is read
at its brightest row only. W22 G0's `rimAlpha` decline (claims §5.94 §3) was made on that reader
and is not rewritten; this reader is the correction recorded beside it (W23 Decision Log 1 (b)).

## The definition, one place, so every gate of W23 reads the same number

- **body** — W21's, unchanged: the mean linear Rec.709 luminance over the declared box eroded
  `--erode` (6) CSS px on every side. Six px clears the rim band and its blur shoulder. The declared
  box is `scenes.json`'s component size centred on the declared canvas, so it is known exactly in
  the native fixture and in the web capture whatever either one drew.

- **the contour rim, per side** — the rows (top, bottom) or columns (left, right) from the declared
  box's first pixel INSIDE the shape inward, each one's mean over the side's straight span minus
  that capture's own body, summed over the first `--depth` (2) CSS px and divided by the scale. One
  linear number per side, in luminance per CSS px: the excess a one-pixel line of amplitude `a`
  carries is `a` whatever the scale, which is what makes the 1x and the 2x rows comparable and is
  what the injection test in `instrument.txt` proves.

- **the straight span** — the corner arcs are EXCLUDED by the component's declared radius times
  `--corner-factor`: a top/bottom row is averaged over `x ∈ [x0 + fr, x1 − fr)` and a left/right
  column over `y ∈ [y0 + fr, y1 − fr)`. On a capsule the radius is half the short side, so the
  straight span of the left and the right side is empty at any factor ≥ 1 and those two sides are
  reported as `nan` rather than as a number read across a semicircle. This is the one thing that
  separates this reader from the band reader's corner mixture, and it is why `L−R` and `T−B` mean
  here what W22 said they mean.

  The factor is 1.6 and not 1, because Apple's rounded rectangle is a CONTINUOUS corner, not a
  circular arc: the curvature is spread along the edge well past the nominal radius, and the first
  contour row of `dark-solid__rrect-md` at 1x is still climbing (0.60 → 0.74 linear) from
  `x0 + r` = 100 to about `x0 + 1.5r` = 110 before it reaches its plateau. Read at factor 1 the
  cell's rim is 0.2141; at 1.3, 0.2262; at 1.5, 0.2291; at 1.6, 0.2293; at 2.0, 0.2297 — the read
  converges by 1.5 and 1.6 keeps a margin without spending much of the span. A capsule's ends are
  true semicircles and converge at factor 1 (0.0198 → 0.0200), so the same factor costs nothing
  there. `instrument.txt` records the sweep.

- **`row0`** — the first contour row's own excess, undivided: the line's own amplitude before the
  shoulder is summed into it. The pair (`rim`, `row0`) is what says whether two captures that agree
  on the sum agree on the shape (`rimWidth` and the falloff are read on this pair, §5.99).

- **`base` and `rimLocal`** — the same sum taken over the side's OWN neighbouring rows instead of
  over the whole eroded body: `base` is the mean of the rows from `--depth` to `2 × --depth` CSS px
  inward, on the same straight span, and `rimLocal` is the excess over it. Over a solid backdrop
  the two readings agree to a few ten-thousandths and `rim` is the number to quote, because the
  body is the cleaner estimate of the same level. Over a STRUCTURED backdrop they do not: the
  material passes the backdrop's structure, so the level under the top edge is not the level
  averaged over the whole interior, and `rim` then carries that difference as if it were rim. The
  spec asks for the structured cells' contour base to be read from the reference's own neighbouring
  rows before L1 is ruled out (W23 G0 (d)); `rimLocal` is that reading, and it is the one the law
  is fitted and checked on wherever the backdrop is not solid.

- **`clip`** — the fraction of the straight span, in the brightest of the contour rows, that is at
  255 in all three channels. A reference row that clips cannot say how much brighter it wanted to
  be, and a fitted law must be allowed to clip there too rather than being pulled down to the
  clipped value (parent acceptance 2).

Everything is in LINEAR light. Encoded means are not reported here: the rim is a compositing
amplitude and only adds in light.

Usage:

    read-contour.py --scenes <scenes.json> --fixtures <dir> [--profile <key>]
                    [--captures <dir> --tier webgpu] [--sets calibration,validation]
                    [--json <out.json>] [--label <text>]
    read-contour.py --inject <capture.png> --scenes ... --scene <id> --amplitude 0.05
"""

import argparse
import hashlib
import json
import math
import os
import sys

import numpy as np
from PIL import Image

SIDES = ("top", "bottom", "left", "right")


def linearise(a: np.ndarray) -> np.ndarray:
    """sRGB EOTF, the same transfer the runtime decodes a backdrop with."""
    a = a / 255.0
    return np.where(a <= 0.04045, a / 12.92, ((a + 0.055) / 1.055) ** 2.4)


def encode(a: np.ndarray) -> np.ndarray:
    """The sRGB OETF; used only by the injection test, which paints in encoded bytes."""
    return np.where(a <= 0.0031308, a * 12.92, 1.055 * np.maximum(a, 0.0) ** (1 / 2.4) - 0.055)


def rgb_of(path: str) -> np.ndarray:
    """8-bit RGB from a PNG, or unquantised RGB from the injection test's `.npy`.

    The `.npy` form exists only so the exact injection can hand the reader a raster that has NOT
    been through 8 bits; PIL has no 16-bit RGB mode, and rounding the exact test to 8 bits would
    make it measure the bed's quantisation instead of the reader's arithmetic.
    """
    if path.endswith(".npy"):
        return np.load(path)
    return np.asarray(Image.open(path).convert("RGB"), dtype=np.float64)


def luma_of_rgb(rgb: np.ndarray) -> np.ndarray:
    c = linearise(rgb)
    return 0.2126 * c[..., 0] + 0.7152 * c[..., 1] + 0.0722 * c[..., 2]


def component_geometry(components, name):
    """Size and corner radius in CSS px, or None for a composite with no single box.

    `toolbar-group` is three capsules with a gap and `glass-over-glass` is a pane on a pane;
    neither has one box whose interior is one body, so the declared-geometry read has nothing to
    say about them and says so rather than inventing a rectangle.
    """
    c = components.get(name)
    if c is None or "size" not in c:
        return None
    w, h = float(c["size"][0]), float(c["size"][1])
    radius = float(c["radius"]) if c["kind"] == "rrect" else min(w, h) / 2.0
    return w, h, radius


def contour_read(lum, rgb, canvas, geom, scale, erode, depth, corner):
    """Body, and per side the contour excess, the first row's excess and the clip fraction."""
    w, h, radius = geom
    cx, cy = canvas["width"] / 2.0, canvas["height"] / 2.0
    x0, y0 = (cx - w / 2.0) * scale, (cy - h / 2.0) * scale
    x1, y1 = (cx + w / 2.0) * scale, (cy + h / 2.0) * scale
    yy, xx = np.mgrid[0 : lum.shape[0], 0 : lum.shape[1]]
    xx = xx + 0.5
    yy = yy + 0.5
    e = erode * scale
    body_mask = (xx >= x0 + e) & (xx < x1 - e) & (yy >= y0 + e) & (yy < y1 - e)
    body = float(lum[body_mask].mean())

    # The straight span, in device px, with the corner arcs cut off by the declared radius times
    # the corner factor (the continuous corner reaches past the nominal radius; see the module doc).
    r = radius * corner * scale
    span_x = (int(math.ceil(x0 + r)), int(math.floor(x1 - r)))
    span_y = (int(math.ceil(y0 + r)), int(math.floor(y1 - r)))
    rows = int(round(depth * scale))
    white = np.all(rgb >= 254.5, axis=-1)

    out = {}
    for side in SIDES:
        if side in ("top", "bottom"):
            lo, hi = span_x
        else:
            lo, hi = span_y
        if hi - lo < 2:
            out[side] = {"rim": float("nan"), "row0": float("nan"), "base": float("nan"),
                         "rimLocal": float("nan"), "clip": float("nan"), "rows": []}
            continue
        lines = []
        clips = []
        for k in range(rows):
            if side == "top":
                index = int(math.floor(y0)) + k
                strip = lum[index, lo:hi]
                cstrip = white[index, lo:hi]
            elif side == "bottom":
                index = int(math.ceil(y1)) - 1 - k
                strip = lum[index, lo:hi]
                cstrip = white[index, lo:hi]
            elif side == "left":
                index = int(math.floor(x0)) + k
                strip = lum[lo:hi, index]
                cstrip = white[lo:hi, index]
            else:
                index = int(math.ceil(x1)) - 1 - k
                strip = lum[lo:hi, index]
                cstrip = white[lo:hi, index]
            lines.append(float(strip.mean()))
            clips.append(float(cstrip.mean()))
        base_lines = []
        for k in range(rows, 2 * rows):
            if side == "top":
                base_lines.append(float(lum[int(math.floor(y0)) + k, lo:hi].mean()))
            elif side == "bottom":
                base_lines.append(float(lum[int(math.ceil(y1)) - 1 - k, lo:hi].mean()))
            elif side == "left":
                base_lines.append(float(lum[lo:hi, int(math.floor(x0)) + k].mean()))
            else:
                base_lines.append(float(lum[lo:hi, int(math.ceil(x1)) - 1 - k].mean()))
        base = float(np.mean(base_lines))
        excess = [v - body for v in lines]
        peak = int(np.argmax(lines))
        out[side] = {
            "rim": float(sum(excess) / scale),
            "row0": float(excess[0]),
            "base": base,
            "rimLocal": float(sum(v - base for v in lines) / scale),
            "clip": clips[peak],
            "rows": lines,
        }
    return body, out


def read_one(path, canvas, geom, erode, depth, corner=1.6):
    rgb = rgb_of(path)
    lum = luma_of_rgb(rgb)
    scale = lum.shape[1] / canvas["width"]
    body, sides = contour_read(lum, rgb, canvas, geom, scale, erode, depth, corner)
    return {
        "body": body,
        "scale": scale,
        "rim": [sides[s]["rim"] for s in SIDES],
        "row0": [sides[s]["row0"] for s in SIDES],
        "base": [sides[s]["base"] for s in SIDES],
        "rimLocal": [sides[s]["rimLocal"] for s in SIDES],
        "clip": [sides[s]["clip"] for s in SIDES],
        "rows": {s: sides[s]["rows"] for s in SIDES},
        "sha256": hashlib.sha256(open(path, "rb").read()).hexdigest()[:12],
    }


def inject(path, canvas, geom, amplitude, corner, out_path, quantise):
    """Paint a synthetic line of known LINEAR amplitude, ONE CSS PX deep, along every straight span.

    One CSS px and not one device pixel: the reader's unit is luminance per CSS px, so a line one
    CSS px deep of amplitude `a` must read back as `a` at every scale, and that invariance is what
    every table in this wave rests on when it puts a 1x row beside a 2x one. A one-device-pixel line
    at 2x would correctly read back `a / 2` and would be testing nothing but the divisor.

    Two forms, because they answer two different questions:

    - `quantise=False` writes a 16-bit PNG and the reader is exact to float. This is the test of the
      reader's GEOMETRY AND UNITS — the span, the depth, the divisor, the body subtraction — and it
      must return the amplitude to within 1e-6.
    - `quantise=True` re-encodes to the 8 bits a real capture has. What comes back is not the
      reader's error but the BED's own resolution at that body level, and it is reported as such,
      in codes. `instrument.txt` records both.
    """
    rgb = rgb_of(path)
    scale = rgb.shape[1] / canvas["width"]
    w, h, radius = geom
    cx, cy = canvas["width"] / 2.0, canvas["height"] / 2.0
    x0, y0 = (cx - w / 2.0) * scale, (cy - h / 2.0) * scale
    x1, y1 = (cx + w / 2.0) * scale, (cy + h / 2.0) * scale
    r = radius * corner * scale
    lin = linearise(rgb)
    depth = int(round(scale))
    sx = (int(math.ceil(x0 + r)), int(math.floor(x1 - r)))
    sy = (int(math.ceil(y0 + r)), int(math.floor(y1 - r)))
    top, bottom = int(math.floor(y0)), int(math.ceil(y1)) - 1
    left, right = int(math.floor(x0)), int(math.ceil(x1)) - 1
    for k in range(depth):
        lin[top + k, sx[0]:sx[1], :] += amplitude
        lin[bottom - k, sx[0]:sx[1], :] += amplitude
        if sy[1] - sy[0] >= 2:
            lin[sy[0]:sy[1], left + k, :] += amplitude
            lin[sy[0]:sy[1], right - k, :] += amplitude
    encoded = encode(np.clip(lin, 0.0, 1.0)) * 255.0
    if quantise:
        Image.fromarray(np.clip(np.rint(encoded), 0, 255).astype(np.uint8)).save(out_path)
    else:
        np.save(out_path, encoded)
    return out_path


def quantisation_step(level):
    """The linear luminance one 8-bit code is worth at `level` — the bed's resolution there.

    Quoted beside every reading whose error matters, because the instrument cannot be more precise
    than the fixtures: one code near a body of 0.50 linear is worth about 0.006 of luminance and
    near 0.01 about 0.0001, so the same absolute tolerance means very different things on the light
    bed and on the dark one.
    """
    code = float(encode(np.asarray(level))) * 255.0
    hi = float(linearise(np.asarray(min(code + 0.5, 255.0))))
    lo = float(linearise(np.asarray(max(code - 0.5, 0.0))))
    return hi - lo


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--scenes", required=True)
    ap.add_argument("--fixtures", default=None)
    ap.add_argument("--profile", default=None)
    ap.add_argument("--captures", default=None)
    ap.add_argument("--tier", default="webgpu")
    ap.add_argument("--sets", default="calibration,validation,recorded")
    ap.add_argument("--erode", type=float, default=6.0)
    ap.add_argument("--depth", type=float, default=2.0, help="CSS px summed inward (X1: two)")
    ap.add_argument("--corner-factor", type=float, default=1.6,
                    help="radii of corner excluded from the straight span; 1.6 for the "
                         "continuous corner (see the module doc and instrument.txt)")
    ap.add_argument("--json", default=None)
    ap.add_argument("--label", default=None)
    ap.add_argument("--inject", default=None, help="a PNG to paint a synthetic line onto")
    ap.add_argument("--scene", default=None)
    ap.add_argument("--amplitude", type=float, default=0.05)
    ap.add_argument("--inject-out", default=None,
                    help="output stem; -f16.png and -u8.png are written beside it")
    args = ap.parse_args()

    spec = json.load(open(args.scenes))
    canvas = spec["canvas"]
    components = spec["components"]

    if args.inject:
        scene = next(s for s in spec["scenes"] if s["id"] == args.scene)
        geom = component_geometry(components, scene["component"])
        stem = args.inject_out or (args.inject + ".injected")
        print(f"injection on {os.path.basename(args.inject)} ({args.scene}), "
              f"amplitude {args.amplitude:.4f} linear, one CSS px deep")
        for quantise, suffix, bound in ((False, "-exact.npy", 1e-6), (True, "-u8.png", None)):
            out_path = stem + suffix
            inject(args.inject, canvas, geom, args.amplitude, args.corner_factor, out_path,
                   quantise)
            before = read_one(args.inject, canvas, geom, args.erode, args.depth,
                              args.corner_factor)
            after = read_one(out_path, canvas, geom, args.erode, args.depth, args.corner_factor)
            step = quantisation_step(before["body"])
            print(f"  -- {'8-bit (the bed)' if quantise else 'unquantised (exact)'}: body "
                  f"{before['body']:.5f}; one 8-bit code there is {step:.5f} linear")
            print(f"     {'side':8s} {'rim before':>11s} {'rim after':>10s} {'recovered':>10s} "
                  f"{'error':>10s} {'codes':>7s} {'clipAfter':>9s}")
            worst = 0.0
            for i, side in enumerate(SIDES):
                b, a = before["rim"][i], after["rim"][i]
                if math.isnan(b):
                    print(f"     {side:8s} {'nan':>11s} {'nan':>10s} {'-':>10s} {'-':>10s} "
                          f"{'-':>7s} {'-':>9s}  (no straight span: capsule end)")
                    continue
                got = a - b
                err = got - args.amplitude
                clipped = after["clip"][i] > 0.0
                if not clipped:
                    worst = max(worst, abs(err))
                print(f"     {side:8s} {b:11.5f} {a:10.5f} {got:10.5f} {err:10.6f} "
                      f"{err / step:7.2f} {after['clip'][i]:9.2f}"
                      + ("   CLIPPED — excluded" if clipped else ""))
            print("     a clipped side is excluded from the bound: the raster cannot carry "
                  "the line, and\n     that is the instrument's declared limit, not its error "
                  "(the `clip` column exists for it).")
            if bound is None:
                print(f"     worst |error| {worst:.6f} = {worst / step:.2f} codes "
                      "(the bed's resolution, not the reader's)")
            else:
                print(f"     worst |error| {worst:.9f}  bound {bound:g}: "
                      f"{'PASS' if worst < bound else 'FAIL'}")
            print(f"     the eroded body must not move: {after['body'] - before['body']:+.9f}")
        return 0

    profiles = [p["key"] for p in spec["profiles"]]
    profile = args.profile or (profiles[0] if len(profiles) == 1 else None)
    if profile is None:
        raise SystemExit(f"--profile required; the bed declares {profiles}")

    which = {}
    for role in ("calibration", "validation", "holdout", "recorded"):
        for sid in spec.get("split", {}).get(role, []):
            which[sid] = role
    declared = None
    for p in spec["profiles"]:
        if p["key"] == profile:
            declared = p["scenes"]
    scene_ids = [s["id"] for s in spec["scenes"]]
    if isinstance(declared, list):
        scene_ids = [s for s in scene_ids if s in declared]
    wanted = set(args.sets.split(","))
    scene_ids = [s for s in scene_ids if which.get(s, "calibration") in wanted]

    rows = []
    for sid in scene_ids:
        scene = next(s for s in spec["scenes"] if s["id"] == sid)
        geom = component_geometry(components, scene["component"])
        if geom is None:
            print(f"# {sid}: {scene['component']} has no single declared box, skipped",
                  file=sys.stderr)
            continue
        native_png = os.path.join(args.fixtures, profile, f"{sid}.png")
        if not os.path.exists(native_png):
            continue
        nat = read_one(native_png, canvas, geom, args.erode, args.depth,
                       args.corner_factor)
        row = {
            "scene": sid,
            "background": scene["background"],
            "component": scene["component"],
            "tint": scene.get("tint"),
            "set": which.get(sid, "unassigned"),
            "radius": geom[2],
            "scale": nat["scale"],
            "bodyNative": nat["body"],
            "rimNative": nat["rim"],
            "rimLocalNative": nat["rimLocal"],
            "baseNative": nat["base"],
            "row0Native": nat["row0"],
            "clipNative": nat["clip"],
            "shaNative": nat["sha256"],
        }
        if args.captures:
            web_png = os.path.join(args.captures, profile, sid, f"{sid}__{args.tier}.png")
            if os.path.exists(web_png):
                web = read_one(web_png, canvas, geom, args.erode, args.depth,
                               args.corner_factor)
                row["bodyWeb"] = web["body"]
                row["rimWeb"] = web["rim"]
                row["rimLocalWeb"] = web["rimLocal"]
                row["baseWeb"] = web["base"]
                row["row0Web"] = web["row0"]
                row["clipWeb"] = web["clip"]
                row["shaWeb"] = web["sha256"]
        rows.append(row)

    label = args.label or f"{profile} / {args.tier if args.captures else 'native only'}"
    print(f"== {label}  fixtures={args.fixtures} captures={args.captures}")
    print(f"{'scene':44s} {'set':11s} {'bodyN':>7s} {'bodyW':>7s} | "
          f"{'rim native T/B/L/R':>35s} | {'rim web T/B/L/R':>35s} | clipN")
    for r in rows:
        def fmt(vals):
            return " ".join("    -  " if math.isnan(v) else f"{v:+7.4f}" for v in vals)
        bw = f"{r['bodyWeb']:7.4f}" if "bodyWeb" in r else "      -"
        rw = fmt(r["rimWeb"]) if "rimWeb" in r else " " * 35
        clip = " ".join("  -  " if math.isnan(v) else f"{v:5.2f}" for v in r["clipNative"])
        print(f"{r['scene']:44s} {r['set']:11s} {r['bodyNative']:7.4f} {bw} | "
              f"{fmt(r['rimNative'])} | {rw} | {clip}")

    if args.json:
        with open(args.json, "w") as fh:
            json.dump({
                "profile": profile,
                "scenes": os.path.abspath(args.scenes),
                "fixtures": os.path.abspath(args.fixtures),
                "captures": os.path.abspath(args.captures) if args.captures else None,
                "tier": args.tier if args.captures else None,
                "sets": sorted(wanted),
                "erodeCssPx": args.erode,
                "depthCssPx": args.depth,
                "cornerFactor": args.corner_factor,
                "sides": list(SIDES),
                "rows": rows,
            }, fh, indent=2)
        print(f"\n-> {args.json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
