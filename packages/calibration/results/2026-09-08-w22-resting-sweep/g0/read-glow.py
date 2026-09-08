"""W22 G0 (e1) — the dark `impulse` capsule under both instruments, with the centre glow isolated.

The wave's Surprises record the discrepancy this script measures: on the native `impulse` capsule
the declared body reads 0.0066 and the silhouette interior 0.0210, a factor of three, and the eye
read the difference as glass. The reason is spatial, so the reading has to be spatial:

- **body (declared)** — the declared box eroded 6 CSS px, W21's instrument. It averages the whole
  capsule, so the centre square's glow is one part of it against a large dark remainder.
- **glow (centre)** — the mean over the box's central 16 x 16 CSS px, which is where the `impulse`
  background's own bright square sits, against **surround**, the mean over the rest of the eroded
  box. Their difference is the glow the material passes, isolated from the level it sits at. This
  is the number the eye was reading.
- **rim per side** — W21's peak per side, unchanged.

The silhouette interior is NOT recomputed here: it is read from the matrix's own
`interiorMeanNative` / `interiorMeanWeb` rows and printed beside, because the whole point of the
discrepancy is that two DIFFERENT instruments disagree, and re-implementing one of them here would
make the comparison a comparison of this file with itself.

The same read runs over every dark cell for the `backdropToneMax` 0 prediction, so what
un-collapsing the dark material costs and buys is a table rather than an argument.

Usage:
    read-glow.py --scenes <scenes.json> --fixtures <dir> --profile <key>
                 --web <label>=<capturesDir> ... [--matrix <matrix.json>] [--out <file>]
"""

import argparse
import json
import os

import numpy as np
from PIL import Image

SIDES = ("top", "bottom", "left", "right")


def linearise(a):
    a = a / 255.0
    return np.where(a <= 0.04045, a / 12.92, ((a + 0.055) / 1.055) ** 2.4)


def luma_of(path):
    rgb = np.asarray(Image.open(path).convert("RGB"), dtype=np.float64)
    c = linearise(rgb)
    return 0.2126 * c[..., 0] + 0.7152 * c[..., 1] + 0.0722 * c[..., 2]


def component_size(components, name):
    c = components[name]
    if "size" in c:
        return float(c["size"][0]), float(c["size"][1])
    return None


def masks(canvas, size, scale, shape, erode, band, centre_css):
    w, h = size
    cx, cy = canvas["width"] / 2.0, canvas["height"] / 2.0
    x0, y0 = (cx - w / 2.0) * scale, (cy - h / 2.0) * scale
    x1, y1 = (cx + w / 2.0) * scale, (cy + h / 2.0) * scale
    yy, xx = np.mgrid[0 : shape[0], 0 : shape[1]]
    xx = xx + 0.5
    yy = yy + 0.5

    def inside(e):
        return ((xx >= x0 + e * scale) & (xx < x1 - e * scale)
                & (yy >= y0 + e * scale) & (yy < y1 - e * scale))

    body = inside(erode)
    ring = inside(0) & ~inside(band)
    sides = {
        "top": ring & (yy < y0 + band * scale),
        "bottom": ring & (yy >= y1 - band * scale),
        "left": ring & (xx < x0 + band * scale),
        "right": ring & (xx >= x1 - band * scale),
    }
    half = centre_css / 2.0 * scale
    centre = ((xx >= cx * scale - half) & (xx < cx * scale + half)
              & (yy >= cy * scale - half) & (yy < cy * scale + half))
    return body, sides, body & centre, body & ~centre


def rim_peaks(lum, sides):
    out = []
    for key in SIDES:
        m = sides[key]
        if key in ("top", "bottom"):
            means = [lum[r][m[r]].mean() for r in range(lum.shape[0]) if m[r].any()]
        else:
            means = [lum[:, c][m[:, c]].mean() for c in range(lum.shape[1]) if m[:, c].any()]
        out.append(float(max(means)) if means else float("nan"))
    return out


def read_one(path, canvas, size, erode, band, centre_css):
    lum = luma_of(path)
    scale = lum.shape[1] / canvas["width"]
    body, sides, centre, surround = masks(canvas, size, scale, lum.shape, erode, band, centre_css)
    return {
        "body": float(lum[body].mean()),
        "sd": float(lum[body].std()),
        "centre": float(lum[centre].mean()),
        "surround": float(lum[surround].mean()),
        "glow": float(lum[centre].mean() - lum[surround].mean()),
        "rim": rim_peaks(lum, sides),
    }


def matrix_rows(path, profile):
    if path is None or not os.path.exists(path):
        return {}
    out = {}
    for cell in json.load(open(path))["cells"]:
        if cell["key"]["profileKey"] != profile or cell["key"]["web"]["renderer"] != "webgpu":
            continue
        material = cell.get("material") or {}
        out[cell["key"]["sceneId"]] = {
            k: (material.get(k) or {}).get("value")
            for k in ("interiorMeanNative", "interiorMeanWeb", "luminanceSlopeNative",
                      "luminanceSlopeWeb")
        }
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--scenes", required=True)
    ap.add_argument("--fixtures", required=True)
    ap.add_argument("--profile", required=True)
    ap.add_argument("--web", nargs="*", default=[], help="<label>=<capturesDir>")
    ap.add_argument("--matrix", default=None)
    ap.add_argument("--erode", type=float, default=6.0)
    ap.add_argument("--band", type=float, default=3.0)
    ap.add_argument("--centre", type=float, default=16.0)
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    spec = json.load(open(args.scenes))
    canvas, components = spec["canvas"], spec["components"]
    declared = None
    for p in spec["profiles"]:
        if p["key"] == args.profile:
            declared = p.get("scenes")
    which = {}
    for role in ("calibration", "validation", "holdout", "recorded"):
        for sid in spec.get("split", {}).get(role, []):
            which[sid] = role
    rows_matrix = matrix_rows(args.matrix, args.profile)

    webs = [(label, path) for label, path in (e.split("=", 1) for e in args.web)]

    lines = []

    def say(text=""):
        lines.append(text)
        print(text)

    say(f"W22 G0 (e1) — the declared body, the centre {args.centre:.0f} x {args.centre:.0f} CSS px "
        f"glow and the rim per side")
    say(f"== {args.profile}")
    say()
    say("`glow` is the centre square's mean minus the mean over the rest of the eroded box: the")
    say("structure the material passes, isolated from the level it sits at. `intN` / `intW` are the")
    say("matrix's own SILHOUETTE interior means, printed beside so the two instruments' "
        "disagreement stays visible.")
    say()
    header = (f"{'scene':40s} {'which':22s} {'body':>8s} {'sd':>7s} {'centre':>8s} "
              f"{'surround':>9s} {'glow':>9s} | rim T/B/L/R")
    say(header)
    out_rows = []
    for scene in spec["scenes"]:
        sid = scene["id"]
        if isinstance(declared, list) and sid not in declared:
            continue
        if which.get(sid, "calibration") == "holdout":
            continue
        size = component_size(components, scene["component"])
        if size is None:
            continue
        native_png = os.path.join(args.fixtures, args.profile, f"{sid}.png")
        if not os.path.exists(native_png):
            continue
        entry = {"scene": sid, "set": which.get(sid, "unassigned"),
                 "native": read_one(native_png, canvas, size, args.erode, args.band, args.centre)}
        for label, root in webs:
            png = os.path.join(root, args.profile, sid, f"{sid}__webgpu.png")
            if os.path.exists(png):
                entry[label] = read_one(png, canvas, size, args.erode, args.band, args.centre)
        entry["matrix"] = rows_matrix.get(sid, {})
        out_rows.append(entry)

        for label in ["native"] + [l for l, _p in webs]:
            d = entry.get(label)
            if d is None:
                continue
            say(f"{sid:40s} {label:22s} {d['body']:8.4f} {d['sd']:7.4f} {d['centre']:8.4f} "
                f"{d['surround']:9.4f} {d['glow']:+9.4f} | "
                + " ".join(f"{v:.4f}" for v in d["rim"]))
        m = entry["matrix"]
        if m.get("interiorMeanNative") is not None:
            say(f"{sid:40s} {'matrix silhouette':22s} "
                f"intN {m['interiorMeanNative']:.4f}  intW "
                f"{m.get('interiorMeanWeb') if m.get('interiorMeanWeb') is None else format(m['interiorMeanWeb'], '.4f')}"
                f"  slopeN {m.get('luminanceSlopeNative')}  slopeW {m.get('luminanceSlopeWeb')}")

    if len(webs) >= 2:
        say()
        say("== what the second column costs and buys against the first, per cell")
        say(f"{'scene':40s} {'d body':>9s} {'d glow':>9s} {'d rim T':>9s} {'d rim B':>9s} "
            f"{'d rim L':>9s} {'d rim R':>9s} {'|body-nat| a':>13s} {'|body-nat| b':>13s}")
        first, second = webs[0][0], webs[1][0]
        for entry in out_rows:
            if first not in entry or second not in entry:
                continue
            a, b, n = entry[first], entry[second], entry["native"]
            say(f"{entry['scene']:40s} {b['body'] - a['body']:+9.4f} "
                f"{b['glow'] - a['glow']:+9.4f} "
                + " ".join(f"{b['rim'][i] - a['rim'][i]:+9.4f}" for i in range(4))
                + f" {abs(a['body'] - n['body']):13.4f} {abs(b['body'] - n['body']):13.4f}")

    if args.out:
        with open(args.out, "w") as fh:
            fh.write("\n".join(lines) + "\n")
        with open(args.out.replace(".txt", ".json"), "w") as fh:
            json.dump({"profile": args.profile, "centreCssPx": args.centre, "rows": out_rows}, fh,
                      indent=2)


if __name__ == "__main__":
    main()
