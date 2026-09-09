"""W26 G1 §7 — one kernel, two backdrops: is the two-component decomposition identified at all?

THE QUESTION THIS ANSWERS. Reader D reads the same surface on two fixtures and returns two very
different heavy components: on the 1x reference `rrect-lg`, 19.52 device px through the impulse tile
(reader A; reader D agrees where it can read) and 8.42 through `checkerboard-64`. Both readers are
validated to about 1 % on synthetics made at those fixtures' own contrasts, so neither is broken.
A surface has ONE kernel, so either the fit is not identified or the kernel is not two Gaussians.

THE TEST. Fit ONE (sigma_sharp, sigma_heavy, share) JOINTLY across both of a component's backdrops
at once — the impulse tile and `checkerboard-64` — with a per-tile gain and a per-tile polynomial,
since the transmission and the interior's smooth structure are the tile's and the kernel is the
material's. Each tile's residual is normalised by its own signal so neither dominates by contrast.

THE CONTROL IS VITREA, because vitrea's kernel is KNOWN: at the inert default the deep sample is
the chain's own level 4, whose half-maximum sigma is 13.42 device px (`chain-kernel.txt`), mixed
with a body of 1.25 device px. If the joint fit recovers that from the two tiles together, the pair
of instruments is consistent and the reference's disagreement is a statement about APPLE's kernel.
If it does not, the disagreement is the instrument pair's and nothing in W25 or W26 that rests on a
single-fixture heavy sigma is safe.

    g1-joint.py [--scratch DIR] [--out FILE]
"""

import argparse
import math
import os
import sys

import numpy as np
from scipy.ndimage import gaussian_filter
from scipy.optimize import least_squares, nnls

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import w26lib as D  # noqa: E402
import w25lib as L  # noqa: E402

SCRATCH = "/Users/new/.claude/jobs/5c70e47f/tmp/w26/g1"
COMPONENTS = ("rrect-lg", "rrect-ml", "rrect-md")
# The two tiles and the erosion each needs. The impulse tile can be read closer to the rim because
# its structure is local; the checkerboard's model is one field across the whole interior.
TILES = (("impulse", 12.0), ("checkerboard-64", 16.0))


def tile(path, backdrop, erode, comp, scale, comps):
    if not os.path.exists(path):
        return None
    shape = (int(200 * scale), int(320 * scale))
    lum = L.luma_of(path)
    if lum.shape != shape:
        return None
    mask = L.Cell(comp, comps).body_mask(scale, shape, erode)
    if mask.sum() < 2000:
        return None
    bg = L.background_for(backdrop, scale, shape)
    ys, xs = np.nonzero(mask)
    P = D._poly_basis(ys.astype(np.float64), xs.astype(np.float64), shape)
    Q, _ = np.linalg.qr(P)
    y = lum[mask].astype(np.float64)
    yr = y - Q @ (Q.T @ y)
    return {"bg": bg, "mask": mask, "Q": Q, "yr": yr, "sd": float(np.std(yr)) or 1e-12,
            "backdrop": backdrop, "cache": {}}


def column(t, sigma):
    key = round(float(sigma), 4)
    if key not in t["cache"]:
        v = gaussian_filter(t["bg"], key, mode="nearest")[t["mask"]]
        t["cache"][key] = v - t["Q"] @ (t["Q"].T @ v)
    return t["cache"][key]


def solve_tile(t, s1, s2, w):
    """One tile's gain at a shared kernel: linear, so it is solved and not searched."""
    m = (1.0 - w) * column(t, s1) + w * column(t, s2)
    denom = float(m @ m)
    g = float(m @ t["yr"]) / denom if denom > 0 else 0.0
    g = max(g, 0.0)
    return (g * m - t["yr"]) / t["sd"], g


def joint(tiles, seed=(2.0, 13.0, 0.4)):
    """One (sigma_sharp, sigma_heavy, share) over every tile at once."""
    def residual(q):
        s1 = math.exp(q[0])
        s2 = math.exp(q[0]) + math.exp(q[1])
        w = 1.0 / (1.0 + math.exp(-q[2]))
        return np.concatenate([solve_tile(t, s1, s2, w)[0] for t in tiles])

    q0 = [math.log(seed[0]), math.log(max(seed[1] - seed[0], 0.1)),
          math.log(seed[2] / (1 - seed[2]))]
    best = None
    for s2 in (7.0, 13.0, 21.0):
        for w in (0.25, 0.6):
            q = [math.log(seed[0]), math.log(max(s2 - seed[0], 0.1)), math.log(w / (1 - w))]
            try:
                out = least_squares(residual, q, diff_step=0.03, xtol=1e-4)
            except Exception:
                continue
            if best is None or out.cost < best.cost:
                best = out
    if best is None:
        return None
    s1 = math.exp(best.x[0])
    s2 = s1 + math.exp(best.x[1])
    w = 1.0 / (1.0 + math.exp(-best.x[2]))
    per = []
    for t in tiles:
        r, g = solve_tile(t, s1, s2, w)
        per.append({"backdrop": t["backdrop"], "gain": g,
                    "rmsRel": float(np.sqrt(np.mean((r * t["sd"]) ** 2))) / t["sd"]})
    return {"sharp": s1, "heavy": s2, "share": w, "per": per,
            "rmsRel": float(np.sqrt(2.0 * best.cost / sum(len(t["yr"]) for t in tiles)))}


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--scratch", default=SCRATCH)
    ap.add_argument("--out", default=os.path.join(HERE, "joint.txt"))
    args = ap.parse_args(argv)
    comps = L.load_components()
    out = []
    e = out.append
    e("W26 G1 §7 — one kernel fitted jointly across the impulse tile and `checkerboard-64`")
    e("=" * 100)
    e("")
    e("Per-tile gain and per-tile polynomial; ONE sharp sigma, ONE heavy sigma, ONE share. Each")
    e("tile's residual is normalised by its own signal, so the high-contrast checkerboard does not")
    e("outvote the impulse tile by loudness. `separate` repeats each tile's own two-component fit")
    e("beside it, and is quoted from `checker.txt` D and E rather than recomputed here.")
    e("")

    for pkey in ("1x-light",):
        profile, scale, _ = L.PROFILES[pkey]
        for source, root in (("reference", None), ("vitrea r0", os.path.join(args.scratch, "r0",
                                                                            "web-captures"))):
            e(f"### {pkey} — {source}")
            e("")
            e(f"   {'component':>10} | {'JOINT sharp':>11} {'heavy':>7} {'share':>6} "
              f"{'resid':>7} | {'separate: impulse':>24} {'checkerboard-64':>24}")
            for comp in COMPONENTS:
                tiles, sep = [], {}
                for backdrop, erode in TILES:
                    sid = f"{backdrop}__{comp}__rest"
                    path = (L.native_path(profile, sid) if root is None
                            else os.path.join(root, profile, sid, f"{sid}__webgpu.png"))
                    t = tile(path, backdrop, erode, comp, scale, comps)
                    if t is None:
                        continue
                    tiles.append(t)
                if len(tiles) < 2:
                    e(f"   {comp:>10} |  ONE TILE ONLY")
                    continue
                j = joint(tiles)
                fmt = lambda f: (f"{f['sharpSigmaDev']:5.2f}/{f['heavySigmaDev']:6.2f}/"
                                 f"{f['heavyShare']:4.2f} r{f['rmsRel']:.3f}" if f else " " * 24)
                e(f"   {comp:>10} | {j['sharp']:11.2f} {j['heavy']:7.2f} {j['share']:6.3f} "
                  f"{j['rmsRel']:7.4f} | {fmt(sep.get('impulse')):>24} "
                  f"{fmt(sep.get('checkerboard-64')):>24}")
                e(f"   {'':>10} |   per-tile residual at the joint kernel: "
                  + "   ".join(f"{p['backdrop']} {p['rmsRel']:.4f}" for p in j["per"]))
            e("")

    e("Vitrea's r0 rows are the CONTROL and its kernel is known: at the inert default the deep")
    e("sample is the chain's own level 4, half-maximum sigma 13.42 device px, mixed with a body of")
    e("1.25. A joint fit that recovers that from the two tiles together says the instrument pair is")
    e("consistent and the reference's disagreement is Apple's kernel; one that does not says the")
    e("disagreement is the instruments'.")
    text = "\n".join(out)
    print(text)
    open(args.out, "w").write(text + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
