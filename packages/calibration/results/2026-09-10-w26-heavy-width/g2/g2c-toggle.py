"""W26 G2c — the diagnostic rungs read in rings, so the gradient can be attributed to one thing.

`g2c-rings.py` establishes WHAT the eye found; this reads the toggles that say WHY. Each rung
changes one thing against the candidate (`g2c-docs.py`), all of them rendered on the same two probe
rows, and the question per rung is simple: does the depth dependence go away?

The statistic is `g2c-rings.py`'s and is not re-derived — the ring's own light with the backdrop
regressed out, and the ring's transmission of the backdrop's contrast — because a second definition
of "the gradient" would make the toggles unreadable. What this file adds is the SUMMARY per rung:

  * `milk range` — the peak-to-peak of the pane's own light across the rings, in 8-bit codes. This
    is the eye's "milkiest at the edges, blackest at the centre" as one number: a uniformly milky
    pane has a small range whatever its level.
  * `trans range` and `trans mean` — the same for the transmitted contrast, because a pane that
    passes more of the checker at depth than at the edge looks like a gradient even if its own
    light is flat.
  * `vs native` — the range the NATIVE reads on the same rings, which is the only scale on which a
    range is large or small.

    g2c-toggle.py [--rungs d9,t13,flat,nolens,flat13] [--out FILE] [--plot FILE]
"""

import argparse
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(HERE, "..", "..",
                                                "2026-09-09-w25-thick-span-composite", "g0")))
import w25lib as L  # noqa: E402

import importlib.util  # noqa: E402
_spec = importlib.util.spec_from_file_location("g2crings", os.path.join(HERE, "g2c-rings.py"))
R = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(R)

SCRATCH = "/Users/new/.claude/jobs/5c70e47f/tmp/w26/g2c"
CANONICAL = "/Users/new/Developer/GitHub/designer/packages/calibration/web-captures"
ROWS = (
    ("checkerboard-64__rrect-lg__rest", "rrect-lg"),
    ("checkerboard-64__rrect-md__rest", "rrect-md"),
)
PROFILES = (
    ("apple-macos-26.5-1x-dark-standard", 1.0),
    ("apple-macos-26.5-2x-dark-standard", 2.0),
    ("apple-macos-26.5-1x-light-standard", 1.0),
)


def profile_of(root, profile, scene):
    return os.path.join(root, profile, scene, f"{scene}__webgpu.png")


def conditioned(bg, bands, floor=0.35):
    """Which rings can carry a milk/transmission SPLIT at all.

    The split is a two-parameter fit per ring against the backdrop's own luma, so a ring lying
    almost entirely on one checker square has no independent variable and its intercept absorbs the
    whole ring — `checkerboard-64` under a 160 CSS px pane produces two or three such rings and they
    are what a naive peak-to-peak would be measuring. A ring is kept when its own backdrop standard
    deviation is at least `floor` of the deepest ring's, which on this bed keeps every ring that
    straddles an edge of the checker and drops every ring that does not.
    """
    sds = np.array([float(np.std(bg[band])) for _a, _b, band in bands])
    return sds >= floor * sds.max(), sds


def series(path, bg, bands):
    milk, trans = [], []
    lum = R.luma(path)
    for _inner, _outer, band in bands:
        _level, m, gain, _sd, _n = R.read(lum, bg, band)
        milk.append(m * 255)
        trans.append(gain)
    return np.array(milk), np.array(trans)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--rungs", default="d9,t13,flat,nolens,flat13")
    ap.add_argument("--ring", type=float, default=4.0)
    ap.add_argument("--skip", type=float, default=6.0)
    ap.add_argument("--out", default=os.path.join(HERE, "g2c-toggle.txt"))
    ap.add_argument("--plot", default=os.path.join(HERE, "sheets", "g2c-toggle.png"))
    args = ap.parse_args()

    comps = L.load_components()
    rungs = args.rungs.split(",")
    lines = []
    plots = []

    def emit(text=""):
        lines.append(text)
        print(text)

    emit("W26 G2c — the toggles: which one removes the edge→centre gradient")
    emit("=" * 112)
    emit("  `milk` is the pane's own light with the backdrop regressed out, in 8-bit codes; `trans`")
    emit("  is the fraction of the backdrop's contrast it passes. `range` is peak-to-peak over the")
    emit("  rings — the eye's gradient as one number — and the native's range is the scale to read")
    emit("  it on. Every rung is one change against the candidate; `d9` IS the candidate.")

    for profile, scale in PROFILES:
        for scene, component in ROWS:
            native = os.path.join(L.FIXTURES, profile, f"{scene}.png")
            if not os.path.exists(native):
                continue
            shape = (int(200 * scale), int(320 * scale))
            cell = L.Cell(component, comps)
            bands = R.rings(cell, "self", scale, shape, args.ring, args.skip)
            if not bands:
                continue
            bg = R.backdrop(scene, scale, shape)
            depths = [(a + b) / 2 for a, b, _m in bands]
            keep, sds = conditioned(bg, bands)

            emit()
            emit(f"  === {profile} / {scene} ===")
            emit(f"    rings {len(bands)}, of which {int(keep.sum())} carry a split "
                 f"(the ring's own backdrop sd is at least 0.35 of the best ring's)")
            emit(f"    {'column':10s} {'milk mean':>10s} {'milk range':>11s} {'trans mean':>11s} "
                 f"{'trans range':>12s} {'trans edge→deep':>16s}")
            columns = [("native", native), ("0.14.0", profile_of(CANONICAL, profile, scene))]
            columns += [(rung, profile_of(os.path.join(SCRATCH, rung, "web-captures"),
                                          profile, scene)) for rung in rungs]
            for label, path in columns:
                if not os.path.exists(path):
                    emit(f"    {label:10s} (no capture)")
                    continue
                milk, trans = series(path, bg, bands)
                m, t_ = milk[keep], trans[keep]
                emit(f"    {label:10s} {m.mean():10.2f} {np.ptp(m):11.2f} {t_.mean():11.4f} "
                     f"{np.ptp(t_):12.4f} {t_[0]:7.4f} → {t_[-1]:6.4f}")
                plots.append({"profile": profile, "scene": scene, "column": label,
                              "depth": depths, "milk": list(milk), "trans": list(trans)})

    json.dump(plots, open(os.path.join(HERE, "g2c-toggle.json"), "w"), indent=1)
    with open(args.out, "w") as handle:
        handle.write("\n".join(lines) + "\n")
    print(f"\n-> {args.out}")
    plot(plots, args.plot)
    print(f"-> {args.plot}")


def plot(records, path):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    keys = []
    for record in records:
        key = (record["profile"], record["scene"])
        if key not in keys:
            keys.append(key)
    if not keys:
        return
    colour = {"native": "#111111", "0.14.0": "#1f77b4", "d9": "#d62728", "t13": "#2ca02c",
              "flat": "#ff7f0e", "nolens": "#9467bd", "flat13": "#8c564b"}
    fig, axes = plt.subplots(2, len(keys), figsize=(4.4 * len(keys), 7.6), squeeze=False)
    for column, key in enumerate(keys):
        for record in records:
            if (record["profile"], record["scene"]) != key:
                continue
            style = dict(color=colour.get(record["column"], "#777777"), marker="o", markersize=2.5,
                         label=record["column"],
                         linewidth=2.0 if record["column"] in ("native", "d9") else 1.1)
            axes[0][column].plot(record["depth"], record["milk"], **style)
            axes[1][column].plot(record["depth"], record["trans"], **style)
        axes[0][column].set_title(f"{key[1]}\n{key[0].replace('apple-macos-26.5-', '')}", fontsize=8)
        axes[0][column].set_ylabel("the pane's own light (codes)", fontsize=8)
        axes[1][column].set_ylabel("transmission of the backdrop", fontsize=8)
        for row in (0, 1):
            axes[row][column].set_xlabel("depth from the pane's edge (CSS px)", fontsize=8)
            axes[row][column].grid(alpha=0.25)
            axes[row][column].tick_params(labelsize=7)
        axes[0][column].legend(fontsize=6, ncol=2)
    fig.suptitle("W26 G2c — the toggles: one change each against the candidate", fontsize=10)
    fig.tight_layout()
    os.makedirs(os.path.dirname(path), exist_ok=True)
    fig.savefig(path, dpi=140)


if __name__ == "__main__":
    main()
