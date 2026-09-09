"""W26 G0 — one rung of the ladder read: reader A's kernel triple, readers B and C's single width.

WHAT THIS READS. The reference fixtures of the two light standard profiles, read-only, and ONE
rung's web captures under the scratch root `g0-rung.sh` wrote. It writes one JSON into that rung's
own scratch directory. Nothing under `fixtures/`, `scenes.json`, the canonical `results/matrix.json`
or the canonical `web-captures/` is touched — X2.

THE INSTRUMENTS ARE W25 G0's, unchanged, as X1 requires: `w25lib.py`'s reader A (the dot's
two-component PSF), reader B (the edge spread) and reader C (the whole-region sigma match). W25
G3's `g3-read.py` is the direct ancestor and the axis is what changes: this child reads the light
bed at both scales only, over the named ladder rows, because a heavy tap is a scheme-independent
mechanism and the question is whether ONE constant moves ONE width.

UNITS. Sigmas in DEVICE px, the unit W25 G0 found the reference invariant in. Levels in linear
Rec.709 luma.

Usage: g0-read.py --rung r0 [--scratch DIR] [--reference]
"""

import argparse
import json
import os
import sys

import numpy as np

W25G0 = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..",
                                     "2026-09-09-w25-thick-span-composite", "g0"))
sys.path.insert(0, W25G0)
import w25lib as L  # noqa: E402

SCRATCH_DEFAULT = "/Users/new/.claude/jobs/5c70e47f/tmp/w26/g0"

IMPULSE = {"impulse"}
EDGE = {"checkerboard", "checkerboard-32", "checkerboard-64"}
STRUCTURED = EDGE | IMPULSE | {"checkerboard-4", "photo"}
PROFILES = ("1x-light", "2x-light")


def read_widths(lum, bg, cell, backdrop, scale, ref_key):
    """W25 G0 `widths.py`'s reader selection, at the row's own scale."""
    out = {}
    mask = cell.body_mask(scale, lum.shape, 6.0)
    if backdrop in IMPULSE:
        rows = L.read_psf_cell(lum, bg, cell, scale, half_css=30.0)
        if rows:
            out["A"] = {
                "sigmaDev": float(np.median([r["sigmaEquivDev"] for r in rows])),
                "sharpDev": float(np.median([r["sharpSigmaDev"] for r in rows])),
                "heavyDev": float(np.median([r["heavySigmaDev"] for r in rows])),
                "heavyShare": float(np.median([r["heavyShare"] for r in rows])),
                "residual": float(np.median([r["rmsRel"] for r in rows])),
                "atCeiling": bool(np.any([r["atCeiling"] for r in rows])),
                "n": len(rows),
            }
    if backdrop in EDGE:
        b = L.read_edge_spread(lum, bg, mask, scale, sigma_ceiling_dev=64.0)
        if b["n"]:
            out["B"] = {"sigmaDev": b["sigmaDev"], "residual": b["residual"], "n": b["n"]}
    if backdrop in STRUCTURED:
        c = L.sigma_match(lum, bg, mask, top=64.0, ref_key=ref_key)
        out["C"] = {"sigmaDev": c["sigmaDev"], "residual": c["rmsRel"], "sd": c["sd"],
                    "atCeiling": c["atCeiling"]}
    return out


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--rung", required=True)
    ap.add_argument("--scratch", default=SCRATCH_DEFAULT)
    ap.add_argument("--tier", default="webgpu")
    # The reference side is the same fixture at every rung, so it is read once — for the baseline
    # — and carried forward. A rung that reads it again wastes a minute and cannot disagree.
    ap.add_argument("--reference", action="store_true")
    # A rung reads only what the rung's question needs. Reader C's sigma-match is a grid of blurs
    # over the whole backdrop and is what makes a full read three minutes; a width ladder that only
    # has to see reader A move asks for `--backdrops impulse` and takes a fifth of that.
    ap.add_argument("--backdrops", default=None)
    args = ap.parse_args(argv)

    keep = None if args.backdrops is None else set(args.backdrops.split(","))
    root = os.path.join(args.scratch, args.rung, "web-captures")
    spec = json.load(open(L.SCENES))
    comps = spec["components"]
    scenes = {s["id"]: s for s in spec["scenes"]}

    widths, levels = [], []
    tasks = []
    for pkey in PROFILES:
        profile, scale, scheme = L.PROFILES[pkey]
        for sid, scene in scenes.items():
            web = os.path.join(root, profile, sid, f"{sid}__{args.tier}.png")
            if not os.path.exists(web):
                continue
            if keep is not None and scene["background"] not in keep:
                continue
            tasks.append((scene["background"], pkey, profile, scale, scheme, sid,
                          scene["component"], L.native_path(profile, sid), web))

    for backdrop, pkey, profile, scale, scheme, sid, component, native, web in sorted(
            tasks, key=lambda t: (t[0], t[1], t[5])):
        shape = (int(200 * scale), int(320 * scale))
        bg = L.background_for(backdrop, scale, shape)
        cell = L.Cell(component, comps)
        mask = cell.body_mask(scale, shape, 6.0)
        sources = [("web", web)]
        if args.reference and os.path.exists(native):
            sources.insert(0, ("native", native))
        for tag, path in sources:
            lum = L.luma_of(path)
            if lum.shape != shape:
                print(f"  SHAPE  {pkey:9} {sid} {tag} {lum.shape}", file=sys.stderr)
                continue
            base = {"profile": pkey, "scheme": scheme, "scale": scale, "scene": sid,
                    "backdrop": backdrop, "component": component, "src": tag,
                    "span": float(cell.short)}
            levels.append({**base, "body": float(lum[mask].mean()), "sd": float(lum[mask].std())})
            for reader, v in read_widths(lum, bg, cell, backdrop, scale,
                                         ("w26g0", backdrop, scale)).items():
                widths.append({**base, "reader": reader, **v})
        print(f"  {pkey:9} {sid:44} read", file=sys.stderr)

    path = os.path.join(args.scratch, args.rung, f"read-{args.rung}.json")
    json.dump({"rung": args.rung, "tier": args.tier, "widths": widths, "levels": levels},
              open(path, "w"), indent=1)
    print(f"{len(widths)} width rows, {len(levels)} level rows -> {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
