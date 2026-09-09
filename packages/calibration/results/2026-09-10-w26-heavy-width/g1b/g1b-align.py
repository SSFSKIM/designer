"""W26 G1b — is the committed backdrop raster the pixels the fixture was actually captured over?

WHY THIS IS ASKED BEFORE ANY KERNEL IS FITTED. Reader E's whole model is `observed ≈ a·(backdrop ⊛
K) + b`. If the raster on disk is displaced from the raster the harness drew by even one device px,
the fit absorbs the mismatch by widening K, and it widens it most on the backdrops whose pitch is
finest — which is exactly the direction that would fake the disagreement W26 G1 §7.5 recorded. The
check is cheap and settles it.

HOW. On the `rrect-sm` scenes, which leave most of the 320 × 200 canvas untouched, the fixture's
own free background is compared with the committed raster over every pixel more than 56 CSS px
outside the surface's contour — clear of the outer shadow's reach. The comparison scans integer
shifts and reports the best one, the residual there in 8-bit display codes, and the gain and offset
the free background needed, which for an unmodified background should be 1 and 0.
"""

import argparse
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import w26brows as R  # noqa: E402
import w25lib as L  # noqa: E402

SHIFTS = range(-3, 4)


def check(profile, scale, backdrop, comps, clear_css=56.0):
    sid = f"{backdrop}__rrect-sm__rest"
    path = L.native_path(profile, sid)
    if not os.path.exists(path):
        return None
    shape = (int(200 * scale), int(320 * scale))
    lum = L.luma_of(path)
    if lum.shape != shape:
        return None
    cell = L.Cell("rrect-sm", comps)
    d = L.signed_distance(cell.box, cell.radius, scale, shape, cell.kind)
    free = d > clear_css
    # Keep clear of the canvas edge too: the window's own border is not the backdrop.
    edge = np.ones(shape, dtype=bool)
    k = int(round(2 * scale))
    edge[:k, :] = edge[-k:, :] = edge[:, :k] = edge[:, -k:] = False
    free = free & edge
    if free.sum() < 2000:
        return None
    bg = L.background_for(backdrop, scale, shape)
    best = None
    for dy in SHIFTS:
        for dx in SHIFTS:
            s = np.roll(np.roll(bg, dy, axis=0), dx, axis=1)
            X = np.stack([s[free], np.ones(int(free.sum()))], axis=1)
            sol, *_ = np.linalg.lstsq(X, lum[free], rcond=None)
            res = X @ sol - lum[free]
            rms = float(np.sqrt(np.mean(res ** 2)))
            if best is None or rms < best[0]:
                best = (rms, dy, dx, float(sol[0]), float(sol[1]))
    rms, dy, dx, gain, off = best
    level = float(lum[free].mean())
    return {"backdrop": backdrop, "rms": rms, "dy": dy, "dx": dx, "gain": gain, "offset": off,
            "codes": rms / (L.linearise(np.array([min(L.encode(level) * 255 + 1, 255)]))[0] - level),
            "n": int(free.sum())}


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(HERE, "align.txt"))
    args = ap.parse_args(argv)
    comps = L.load_components()
    lines = []
    e = lines.append
    e("W26 G1b — the committed backdrop rasters against the fixtures' own free background")
    e("=" * 100)
    e("")
    e("`rrect-sm` scenes, every pixel more than 56 CSS px outside the contour and 2 CSS px inside")
    e("the canvas edge. A gain of 1 and an offset of 0 mean the harness drew the raster unmodified;")
    e("a shift of (0, 0) means it drew it where the raster says. `codes` is the residual in 8-bit")
    e("display codes at the region's own level.")
    e("")
    e(f"  {'profile':>8} {'backdrop':>18} {'dy':>3} {'dx':>3} {'gain':>8} {'offset':>9}"
      f" {'codes':>7} {'px':>7}")
    for pkey in ("1x-light", "2x-light", "1x-dark"):
        profile, scale, _ = L.PROFILES[pkey]
        for backdrop in R.BACKDROPS:
            out = check(profile, scale, backdrop, comps)
            if out is None:
                continue
            e(f"  {pkey:>8} {backdrop:>18} {out['dy']:3d} {out['dx']:3d} {out['gain']:8.4f}"
              f" {out['offset']:9.5f} {out['codes']:7.2f} {out['n']:7d}")
    text = "\n".join(lines)
    print(text)
    open(args.out, "w").write(text + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
