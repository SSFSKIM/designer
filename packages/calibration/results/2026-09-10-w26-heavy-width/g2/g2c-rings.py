"""W26 G2c — the interior read in RINGS from the pane's own edge, for the eye's gradient.

The user's eye found something on the dark `checkerboard-64` rrects and the dark nested pane that no
metric in this wave reports: at the candidate the pane looks MILKIEST AT ITS EDGES AND BLACKEST AT
ITS CENTRE, where Apple's pane and the 0.14.0 material are both uniformly milky. Every reader this
wave used takes a statistic over the whole interior — a mean, a standard deviation, an OKLab ΔE — and
a mean is exactly the statistic a radial gradient can hide in. This file reads the same interiors as
a function of distance from the contour instead.

TWO QUANTITIES PER RING, and the pair is the point: a gradient in the MEAN and a gradient in the
MODULATION are different mechanisms and the eye sees their sum.

  * **milk** — the ring's own light with the BACKDROP REGRESSED OUT: fit `interior ≈ milk + trans·bg`
    over the ring's pixels and take the intercept, in 8-bit display codes. The raw ring mean is
    useless on its own here, and the first draft of this file learned it the hard way: a 64 CSS px
    checker under a 160 CSS px pane puts a dark square at the centre and bright ones at the edges,
    so EVERY column including the native's shows a large "gradient" that is the backdrop's phase and
    not the pane's. The intercept is what the pane adds whatever is under it.
  * **transmission** — the same fit's slope, `cov(interior, bg) / var(bg)`: the fraction of the
    checkerboard's contrast the pane still passes at that depth, which is what a blur's width and a
    mix's share both act on, and which is scale-free in a way a standard deviation is not.

The raw ring mean is printed beside them because it is what the eye actually sees, but every VERDICT
here is read off the intercept and the slope.

The rings are `--ring` CSS px wide and are taken from the signed distance to the pane's own contour,
so a rounded rectangle's rings follow its corners rather than a bounding box. The first ring is
dropped by `--skip` CSS px because the rim and its shoulder are not the body (W23's reader uses 6).

The nested pane is read on its BASE with the overlay's box cut out, which is W22's geometry and the
one every other reader in this wave uses on that cell — and separately on the OVERLAY alone, because
the eye named that pane too.

Nothing is written outside this directory and the captures are read-only.

    g2c-rings.py --native <fixtures> --before <captures> --after <captures> [--ring 4] [--skip 6]
                 [--out FILE] [--plot FILE]
"""

import argparse
import json
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(HERE, "..", "..",
                                                "2026-09-09-w25-thick-span-composite", "g0")))
import w25lib as L  # noqa: E402

# (scene, component, part) — `part` names which shape of a stack the rings follow.
ROWS = (
    ("checkerboard-64__rrect-lg__rest", "rrect-lg", "self"),
    ("checkerboard-64__rrect-md__rest", "rrect-md", "self"),
    ("checkerboard__glass-over-glass__rest", "glass-over-glass", "base"),
    ("checkerboard__glass-over-glass__rest", "glass-over-glass", "over"),
)
PROFILES = (
    ("apple-macos-26.5-1x-dark-standard", 1.0, "dark"),
    ("apple-macos-26.5-2x-dark-standard", 2.0, "dark"),
    ("apple-macos-26.5-1x-light-standard", 1.0, "light"),
    ("apple-macos-26.5-2x-light-standard", 2.0, "light"),
)


def luma(path):
    rgb = np.asarray(Image.open(path).convert("RGB"), dtype=np.float64) / 255.0
    lin = np.where(rgb <= 0.04045, rgb / 12.92, ((rgb + 0.055) / 1.055) ** 2.4)
    return lin[..., 0] * 0.2126 + lin[..., 1] * 0.7152 + lin[..., 2] * 0.0722


def backdrop(scene, scale, shape):
    return L.background_for(scene.split("__")[0], scale, shape)


def geometry(cell, part):
    """The box, radius and kind whose contour the rings follow, and the shape to cut out."""
    if cell.kind == "stack":
        box, radius, kind = cell.base if part == "base" else cell.over
        cut = cell.over if part == "base" else None
        return (box, radius, kind), cut
    return (cell.box, cell.radius, cell.kind), None


def rings(cell, part, scale, shape, ring, skip):
    """A list of (inner, outer, mask) in CSS px of depth, from the contour inward."""
    (box, radius, kind), cut = geometry(cell, part)
    depth = -L.signed_distance(box, radius, scale, shape, kind)
    inside = depth > 0
    if cut is not None:
        cbox, cradius, ckind = cut
        # The overlay's own box DILATED by `skip`, so the base's rings never touch the pane above.
        inside &= L.signed_distance(cbox, cradius, scale, shape, ckind) > skip
    out = []
    reach = float(depth[inside].max()) if inside.any() else 0.0
    edge = skip
    while edge < reach:
        band = inside & (depth >= edge) & (depth < edge + ring)
        if band.sum() >= 64:
            out.append((edge, edge + ring, band))
        edge += ring
    return out


def read(lum, bg, band):
    """The ring's raw mean, its own light with the backdrop regressed out, and its transmission."""
    y = lum[band]
    x = bg[band]
    var = float(np.var(x))
    gain = float(np.cov(x, y, bias=True)[0, 1] / var) if var > 1e-12 else float("nan")
    milk = float(np.mean(y) - gain * np.mean(x)) if var > 1e-12 else float(np.mean(y))
    # The ring's OWN backdrop contrast, which is what conditions the split. A ring that lies
    # almost entirely on one checker square has nothing for the slope to be fitted on and the
    # intercept absorbs the whole ring — so a `milk` read there is not a reading, and the callers
    # drop it rather than average it in.
    return float(np.mean(y)), milk, gain, float(np.sqrt(var)), int(band.sum())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--native", default=L.FIXTURES)
    ap.add_argument("--before", required=True)
    ap.add_argument("--after", required=True)
    ap.add_argument("--ring", type=float, default=4.0)
    ap.add_argument("--skip", type=float, default=6.0)
    ap.add_argument("--tier", default="webgpu")
    ap.add_argument("--out", default=os.path.join(HERE, "g2c-rings.txt"))
    ap.add_argument("--plot", default=os.path.join(HERE, "sheets", "g2c-rings.png"))
    ap.add_argument("--json", default=os.path.join(HERE, "g2c-rings.json"))
    args = ap.parse_args()

    comps = L.load_components()
    lines = []

    def emit(text=""):
        lines.append(text)
        print(text)

    emit("W26 G2c — the interior in rings from the pane's edge: level and transmission")
    emit("=" * 118)
    emit(f"  rings {args.ring:.0f} CSS px wide, the first {args.skip:.0f} CSS px skipped (the rim and")
    emit("  its shoulder are not the body). `level` is the ring's mean luminance in 8-bit display")
    emit("  codes; `trans` is the ring's regression gain onto the BACKDROP's own luma — the fraction")
    emit("  of the checkerboard's contrast the pane still passes at that depth.")
    emit()
    emit("  A GRADIENT is the difference between the first ring and the deepest: `Δlevel` and")
    emit("  `Δtrans`, edge minus centre. A uniformly milky pane reads about 0 for both.")

    records = []
    for profile, scale, scheme in PROFILES:
        for scene, component, part in ROWS:
            native_path = os.path.join(args.native, profile, f"{scene}.png")
            if not os.path.exists(native_path):
                continue
            shape = (int(200 * scale), int(320 * scale))
            cell = L.Cell(component, comps)
            bands = rings(cell, part, scale, shape, args.ring, args.skip)
            if not bands:
                continue
            bg = backdrop(scene, scale, shape)
            columns = {"native": native_path}
            for label, root in (("0.14.0", args.before), ("candidate", args.after)):
                path = os.path.join(root, profile, scene, f"{scene}__{args.tier}.png")
                if os.path.exists(path):
                    columns[label] = path
            if len(columns) < 3:
                emit(f"\n  {profile} / {scene} / {part}: missing a column, skipped")
                continue

            emit()
            emit(f"  === {profile} / {scene} / {part} ({scheme}, dpr {scale:.0f}) ===")
            head = f"    {'depth CSS px':>14s}"
            for label in ("native", "0.14.0", "candidate"):
                head += (f" | {label[:4] + ' raw':>9s} {label[:4] + ' milk':>10s} "
                         f"{label[:4] + ' trans':>11s}")
            emit(head + f" {'px':>7s}")
            series = {label: {"depth": [], "level": [], "milk": [], "trans": []}
                      for label in columns}
            planes = {label: luma(path) for label, path in columns.items()}
            for inner, outer, band in bands:
                row = f"    {inner:6.0f} … {outer:5.0f}"
                for label in ("native", "0.14.0", "candidate"):
                    level, milk, gain, _sd, n = read(planes[label], bg, band)
                    series[label]["depth"].append((inner + outer) / 2.0)
                    series[label]["level"].append(level)
                    series[label]["milk"].append(milk)
                    series[label]["trans"].append(gain)
                    row += f" | {level * 255:9.2f} {milk * 255:10.2f} {gain:11.4f}"
                row += f" {n:7d}"
                emit(row)
            emit("    GRADIENT, edge ring minus deepest ring — a uniformly milky pane reads ~0:")
            for label in ("native", "0.14.0", "candidate"):
                lv, mk, tr = (series[label][k] for k in ("level", "milk", "trans"))
                d_level = (lv[0] - lv[-1]) * 255
                d_milk = (mk[0] - mk[-1]) * 255
                d_trans = tr[0] - tr[-1]
                emit(f"      {label:10s} Δraw {d_level:+7.2f}   Δmilk {d_milk:+7.2f} codes   "
                     f"Δtrans {d_trans:+8.4f}")
                records.append({
                    "profile": profile, "scene": scene, "part": part, "scale": scale,
                    "scheme": scheme, "source": label,
                    "depth": series[label]["depth"],
                    "levelCodes": [v * 255 for v in lv],
                    "milkCodes": [v * 255 for v in mk],
                    "trans": tr,
                    "deltaLevelCodes": d_level, "deltaMilkCodes": d_milk, "deltaTrans": d_trans,
                })
            # The two vitrea columns differenced per ring over the SAME backdrop, which needs no
            # model at all: if the candidate carries a radial gradient the 0.14.0 material does not,
            # it is in this line and nowhere else.
            emit("    candidate − 0.14.0 per ring, milk in codes (same backdrop under both):")
            drow = "      "
            for index, depth in enumerate(series["candidate"]["depth"]):
                delta = (series["candidate"]["milk"][index]
                         - series["0.14.0"]["milk"][index]) * 255
                drow += f"{depth:5.0f}:{delta:+6.2f} "
                if len(drow) > 104:
                    emit(drow)
                    drow = "      "
            if drow.strip():
                emit(drow)

    json.dump(records, open(args.json, "w"), indent=1)
    with open(args.out, "w") as handle:
        handle.write("\n".join(lines) + "\n")
    print(f"\n-> {args.out}")

    plot(records, args.plot)
    print(f"-> {args.plot}")


def plot(records, path):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    keys = []
    for record in records:
        key = (record["profile"], record["scene"], record["part"])
        if key not in keys:
            keys.append(key)
    if not keys:
        return
    fig, axes = plt.subplots(2, len(keys), figsize=(4.2 * len(keys), 7.4), squeeze=False)
    colour = {"native": "#111111", "0.14.0": "#1f77b4", "candidate": "#d62728"}
    for column, key in enumerate(keys):
        for record in records:
            if (record["profile"], record["scene"], record["part"]) != key:
                continue
            style = dict(color=colour[record["source"]], marker="o", markersize=3,
                         label=record["source"])
            axes[0][column].plot(record["depth"], record["milkCodes"], **style)
            axes[1][column].plot(record["depth"], record["trans"], **style)
        title = f"{key[1]}\n{key[0].replace('apple-macos-26.5-', '')} / {key[2]}"
        axes[0][column].set_title(title, fontsize=8)
        axes[0][column].set_ylabel("the pane's own light (codes, backdrop out)", fontsize=8)
        axes[1][column].set_ylabel("transmission (gain onto backdrop)", fontsize=8)
        for row in (0, 1):
            axes[row][column].set_xlabel("depth from the pane's edge (CSS px)", fontsize=8)
            axes[row][column].grid(alpha=0.25)
            axes[row][column].tick_params(labelsize=7)
        axes[0][column].legend(fontsize=7)
    fig.suptitle("W26 G2c — the interior in rings: a flat line is a uniformly milky pane", fontsize=10)
    fig.tight_layout()
    os.makedirs(os.path.dirname(path), exist_ok=True)
    fig.savefig(path, dpi=140)


if __name__ == "__main__":
    main()
