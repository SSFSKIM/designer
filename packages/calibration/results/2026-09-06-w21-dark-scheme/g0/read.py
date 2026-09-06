"""W21 G0 — the wave's instrument: body and rim under the DECLARED geometry (W21 X2).

Generalised from the finding's `dark-read.py` (claims §5.87) so that it reads any scene bed —
the canonical one or the W21 probe — from any fixtures directory, with or without a web capture
beside it, and with the run-to-run noise floor measured from the probe's own attested runs.

The silhouette extractor is not used and cannot be. Over the dark solids the reference's body sits
within the extractor's 0.02 threshold of its own backdrop, so the silhouette it returns is the rim
ring in fragments and every statistic taken over it is a rim reading (claims §5.87). The declared
geometry has no such failure mode: `scenes.json` states the component's size, the harness centres it
on the canvas, and the box is therefore known exactly, in both the native fixture and the web
capture, whatever either one drew.

Definitions, one place, so every gate in this wave reads the same numbers:

- **body** — mean and sd of linear luminance (Rec.709) over the declared box eroded `--erode` CSS px
  on every side. Six px clears the rim band and its blur shoulder.
- **rim peak per side** — the declared box's outer `--band` CSS px is the rim band; a side's peak is
  the largest mean over the band's rows (top, bottom) or columns (left, right). A peak rather than a
  mean because the rim is a thin bright line inside a band that also holds body pixels.
- **backdrop linear / encoded mean** — measured from the RENDERED background raster under the
  declared box, never assumed from the background's parameters (W9's input definition, claims
  §5.30: the canvas does not divide evenly at every pitch). The encoded mean is
  `Σ encode(l) / n` — the input W9's P3 named — reported as an encoded value; the linear mean is
  `Σ l / n`.
- **σ body / σ rim** — the run-to-run standard deviation of the body mean and of the four rim peaks
  (the largest of the four sides' σ) across the attested runs given by `--runs`. This is the noise
  floor every anchor and every rim reading is quoted against, and the only reason to keep the runs
  after materialisation.

Usage:

    read.py --scenes <scenes.json> --fixtures <dir> [--profile <key>]
            [--captures <dir> --tier webgpu] [--runs <runDir> ...] [--json <out.json>]

`--fixtures` is a materialised bed: `<dir>/<profile>/<scene>.png` plus `<dir>/backgrounds/<bg>@1x.png`.
`--captures` is a web-capture tree: `<dir>/<profile>/<scene>/<scene>__<tier>.png`.
Scale is inferred per fixture from the raster against the declared canvas, so the same invocation
reads a 1x probe and a 2x canonical profile.
"""

import argparse
import json
import os
import sys

import numpy as np
from PIL import Image


def linearise(a: np.ndarray) -> np.ndarray:
    """sRGB EOTF, the same transfer the runtime decodes a backdrop with."""
    a = a / 255.0
    return np.where(a <= 0.04045, a / 12.92, ((a + 0.055) / 1.055) ** 2.4)


def encode(a: np.ndarray) -> np.ndarray:
    """The sRGB OETF — W9's encoded-space input is taken in this space, not in light."""
    return np.where(a <= 0.0031308, a * 12.92, 1.055 * np.maximum(a, 0.0) ** (1 / 2.4) - 0.055)


def luma_of(path: str) -> np.ndarray:
    rgb = np.asarray(Image.open(path).convert("RGB"), dtype=np.float64)
    c = linearise(rgb)
    return 0.2126 * c[..., 0] + 0.7152 * c[..., 1] + 0.0722 * c[..., 2]


def component_size(components, name):
    """The declared box, or None for a composite component that does not have one.

    `toolbar-group` is three capsules with a gap between them and `glass-over-glass` is a pane on a
    pane; neither has a single box whose interior is one body, so the declared-geometry read has
    nothing to say about them and reports that rather than inventing a rectangle. Both are outside
    this wave's clauses (the nested pane is W21 Deferred, the toolbar group is not a dark cell).
    """
    c = components[name]
    if "size" in c:
        return float(c["size"][0]), float(c["size"][1])
    if "width" in c:
        return float(c["width"]), float(c["height"])
    return None


def masks(canvas, size, scale, shape, erode, band):
    """The declared box, its eroded body, and the four sides of its rim band, in device px."""
    w, h = size
    cx, cy = canvas["width"] / 2.0, canvas["height"] / 2.0
    x0, y0 = (cx - w / 2.0) * scale, (cy - h / 2.0) * scale
    x1, y1 = (cx + w / 2.0) * scale, (cy + h / 2.0) * scale
    yy, xx = np.mgrid[0 : shape[0], 0 : shape[1]]
    xx = xx + 0.5
    yy = yy + 0.5

    def inside(e):
        return (xx >= x0 + e * scale) & (xx < x1 - e * scale) & (yy >= y0 + e * scale) & (yy < y1 - e * scale)

    box = inside(0)
    body = inside(erode)
    ring = box & ~inside(band)
    sides = {
        "top": ring & (yy < y0 + band * scale),
        "bottom": ring & (yy >= y1 - band * scale),
        "left": ring & (xx < x0 + band * scale),
        "right": ring & (xx >= x1 - band * scale),
    }
    return box, body, sides


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


def read_one(path, canvas, size, erode, band):
    lum = luma_of(path)
    scale = lum.shape[1] / canvas["width"]
    _box, body, sides = masks(canvas, size, scale, lum.shape, erode, band)
    return {
        "body": float(lum[body].mean()),
        "sd": float(lum[body].std()),
        "rim": rim_peaks(lum, sides),
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--scenes", required=True)
    ap.add_argument("--fixtures", required=True)
    ap.add_argument("--profile", default=None, help="defaults to the bed's single profile")
    ap.add_argument("--captures", default=None)
    ap.add_argument("--tier", default="webgpu")
    ap.add_argument("--runs", nargs="*", default=[])
    ap.add_argument("--backgrounds", default=None, help="defaults to <fixtures>/backgrounds")
    ap.add_argument(
        "--sets",
        default="calibration,validation,recorded",
        help="split roles to read at all; a cell outside them is skipped before its file is opened, "
        "which is how a gate leaves a holdout genuinely unread",
    )
    ap.add_argument("--erode", type=float, default=6.0)
    ap.add_argument("--band", type=float, default=3.0)
    ap.add_argument("--json", default=None)
    args = ap.parse_args()

    spec = json.load(open(args.scenes))
    canvas = spec["canvas"]
    components = spec["components"]
    profiles = [p["key"] for p in spec["profiles"]]
    profile = args.profile or (profiles[0] if len(profiles) == 1 else None)
    if profile is None:
        raise SystemExit(f"--profile required; the bed declares {profiles}")
    bg_dir = args.backgrounds or os.path.join(args.fixtures, "backgrounds")

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
    if spec.get("split"):
        wanted = set(args.sets.split(","))
        scene_ids = [s for s in scene_ids if which.get(s, "calibration") in wanted]

    # Attested runs, for the noise floor. A run contributes a cell only when that cell passed its
    # own audit in that run: `presentedActive` (the window was key — Liquid Glass draws a flat
    # inactive appearance otherwise), `deterministic`, `materialRendered`.
    run_cells = []
    for run_dir in args.runs:
        try:
            manifest = json.load(open(os.path.join(run_dir, "manifest.json")))
        except FileNotFoundError:
            print(f"# no manifest in {run_dir}, skipped", file=sys.stderr)
            continue
        ok = set()
        for prof in manifest["profiles"]:
            if prof.get("profileKey", prof.get("key")) != profile:
                continue
            for f in prof["fixtures"]:
                if f.get("presentedActive") and f.get("deterministic") and f.get("materialRendered"):
                    ok.add(f["sceneId"])
        run_cells.append((os.path.basename(run_dir), run_dir, ok))

    rows = []
    for sid in scene_ids:
        scene = next(s for s in spec["scenes"] if s["id"] == sid)
        size = component_size(components, scene["component"])
        if size is None:
            print(f"# {sid}: {scene['component']} has no single declared box, skipped", file=sys.stderr)
            continue
        native_png = os.path.join(args.fixtures, profile, f"{sid}.png")
        if not os.path.exists(native_png):
            continue
        nat = read_one(native_png, canvas, size, args.erode, args.band)

        bg_png = os.path.join(bg_dir, f"{scene['background']}@1x.png")
        bg = luma_of(bg_png)
        scale = bg.shape[1] / canvas["width"]
        box, _body, _sides = masks(canvas, size, scale, bg.shape, args.erode, args.band)
        bg_linear = float(bg[box].mean())
        bg_encoded = float(encode(bg[box]).mean())

        row = {
            "scene": sid,
            "background": scene["background"],
            "component": scene["component"],
            "tint": scene.get("tint"),
            "set": which.get(sid, "unassigned"),
            "bodyNative": nat["body"],
            "sdNative": nat["sd"],
            "rimNative": nat["rim"],
            "backdropLinearMean": bg_linear,
            "backdropEncodedMean": bg_encoded,
        }

        bodies, rims = [], []
        for name, run_dir, ok in run_cells:
            png = os.path.join(run_dir, profile, f"{sid}.png")
            if sid not in ok or not os.path.exists(png):
                continue
            r = read_one(png, canvas, size, args.erode, args.band)
            bodies.append(r["body"])
            rims.append(r["rim"])
        if bodies:
            row["runs"] = len(bodies)
            row["sigmaBody"] = float(np.std(bodies))
            row["sigmaRim"] = float(np.max(np.std(np.asarray(rims), axis=0)))

        if args.captures:
            web_png = os.path.join(args.captures, profile, sid, f"{sid}__{args.tier}.png")
            if os.path.exists(web_png):
                web = read_one(web_png, canvas, size, args.erode, args.band)
                row["bodyWeb"] = web["body"]
                row["sdWeb"] = web["sd"]
                row["rimWeb"] = web["rim"]
        rows.append(row)

    head = (
        f"{'scene':46s} {'set':11s} {'bgLin':>7s} {'bgEnc':>7s} "
        f"{'body':>8s} {'sd':>7s} {'sigB':>7s} {'sigR':>7s} | rim T/B/L/R"
    )
    print(f"== {profile}  ({args.fixtures})")
    print(head)
    for r in rows:
        sig_b = f"{r['sigmaBody']:7.4f}" if "sigmaBody" in r else "      -"
        sig_r = f"{r['sigmaRim']:7.4f}" if "sigmaRim" in r else "      -"
        line = (
            f"{r['scene']:46s} {r['set']:11s} {r['backdropLinearMean']:7.4f} "
            f"{r['backdropEncodedMean']:7.4f} {r['bodyNative']:8.4f} {r['sdNative']:7.4f} "
            f"{sig_b} {sig_r} | " + " ".join(f"{v:.3f}" for v in r["rimNative"])
        )
        if "bodyWeb" in r:
            line += (
                f"  ||web {r['bodyWeb']:.4f} {r['sdWeb']:.4f} | "
                + " ".join(f"{v:.3f}" for v in r["rimWeb"])
            )
        print(line)

    if args.json:
        with open(args.json, "w") as fh:
            json.dump(
                {
                    "profile": profile,
                    "fixtures": os.path.abspath(args.fixtures),
                    "captures": os.path.abspath(args.captures) if args.captures else None,
                    "tier": args.tier if args.captures else None,
                    "sets": args.sets.split(","),
                    "erodeCssPx": args.erode,
                    "rimBandCssPx": args.band,
                    "runs": [name for name, _d, _ok in run_cells],
                    "rows": rows,
                },
                fh,
                indent=2,
            )
        print(f"\n-> {args.json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
