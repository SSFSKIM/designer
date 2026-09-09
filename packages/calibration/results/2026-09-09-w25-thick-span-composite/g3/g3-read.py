"""W25 G3 — one rung of the probe set read: the kernel's triple, the body levels, the along-side rim.

WHAT THIS READS. The reference fixtures of the four standard profiles
(`apps/reference-apple/fixtures/apple-macos-26.5-{1x,2x}-{light,dark}-standard/`), read-only, and
ONE rung's web captures under the scratch root that `g3-probe-run.sh` wrote. It writes one JSON
into that rung's own scratch directory. Nothing under `fixtures/`, `scenes.json`, the canonical
`results/matrix.json` or the canonical `web-captures/` is touched — X2.

THE INSTRUMENTS ARE G0's, unchanged, as X1 requires: `w25lib.py`'s reader A (the dot's
two-component PSF), reader B (the edge spread) and reader C (the whole-region sigma match), plus
`along-side.py`'s position reader. G2's `read-rung.py` is the direct ancestor; what changes here is
the axis. G2 read four 1x beds because that was every fixture on disk; this child reads the probe
set at BOTH scales in BOTH schemes, which is the fixture G1's sitting produced and the only one
that identifies the 2x thick material (Decision Log 3 (e)).

WHY THE SETS ARE READ WHOLE. Every probe scene is read on both sides. The probe set is not a gated
set — the gate ignores it by name — so no holdout reservation applies to it and X3's one-read rule
is about the canonical holdout, which this file never opens.

UNITS. Sigmas in DEVICE px, so a 2x row's sigma is twice its CSS-px value and the two scales are
directly comparable in the unit G0 found the reference invariant in (§3 of `g0-findings.md`:
each component halves in device px between the scales). Levels in linear Rec.709 luma. Along-side
slopes in luma per CSS px, which is the unit G0's table quotes.

Usage: g3-read.py --rung r0 [--scratch DIR]
"""

import argparse
import importlib.util
import json
import os
import sys

import numpy as np

G0 = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "g0")
sys.path.insert(0, G0)
import w25lib as L  # noqa: E402


def _load(name, filename):
    spec = importlib.util.spec_from_file_location(name, os.path.join(G0, filename))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


ALONG = _load("w25_along_side", "along-side.py")

SCRATCH_DEFAULT = "/Users/new/.claude/jobs/5c70e47f/tmp/w25/g3"

# Which reader answers on which backdrop. Reader A needs a transmitted dot; readers B and C need a
# resolvable step, and B additionally needs the step to be a single edge it can window.
IMPULSE = {"impulse"}
EDGE = {"checkerboard", "checkerboard-32", "checkerboard-64", "checkerboard-lc16", "hc-text",
        "hc-text-7", "hc-text-28"}
STRUCTURED = EDGE | IMPULSE | {"checkerboard-4", "checkerboard-8", "photo"}
FLAT = {"light-solid", "dark-solid", "mid-dark-solid"}

PROFILES = ("1x-light", "2x-light", "1x-dark", "2x-dark")


def cell_for(component, comps):
    """G0's `Cell`, with a displaced component put where the harness draws it.

    `w25lib.Cell` places a plain rrect or capsule at the canvas centre, because when G0 wrote it
    every component on the bed was centred and only the stack and the group carried offsets. G1's
    sitting added one that is not: `rrect-md-clear20` is `rrect-md` displaced 32 points down, which
    is the fixture that separates span from canvas clearance (Decision Log 3 (d), answered at
    Decision Log 5 (d)). The library is G0's committed instrument and is left alone (X1); the
    offset is applied here, where it is visible, and it moves the body mask and the four sides
    together so a level and an along-side slope are read at the same place.
    """
    cell = L.Cell(component, comps)
    offset = comps[component].get("offset")
    if offset and cell.kind not in ("stack", "group"):
        cell.box = L.place(comps[component]["size"], offset)
    return cell


def read_widths(lum, bg, cell, backdrop, scale, ref_key):
    """G0 `widths.py`'s reader selection, at the row's own scale."""
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
                "n": len(rows),
            }
    if backdrop in EDGE:
        b = L.read_edge_spread(lum, bg, mask, scale, sigma_ceiling_dev=64.0)
        if b["n"]:
            out["B"] = {"sigmaDev": b["sigmaDev"], "residual": b["residual"], "n": b["n"]}
    if backdrop in STRUCTURED:
        c = L.sigma_match(lum, bg, mask, top=64.0, ref_key=ref_key)
        out["C"] = {"sigmaDev": c["sigmaDev"], "residual": c["rmsRel"], "gain": c.get("gain"),
                    "sd": c["sd"], "atCeiling": c["atCeiling"]}
    return out


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--rung", required=True)
    ap.add_argument("--scratch", default=SCRATCH_DEFAULT)
    ap.add_argument("--tier", default="webgpu")
    # A ladder rung reads only what the rung can move. `--fast` keeps the backdrops that identify
    # the kernel's triple (the impulse rows for reader A and the two coarse checkerboards for
    # reader C) and drops the fine and textured ones, whose readers saturate on this material
    # anyway (G0 §1); `--web-only` drops the reference side, which is the same fixture at every
    # rung and is carried forward from the baseline read. Both are omitted for the baseline and
    # the confirmation, which read everything.
    ap.add_argument("--fast", action="store_true")
    ap.add_argument("--web-only", action="store_true")
    args = ap.parse_args(argv)
    fast_backdrops = {"impulse", "checkerboard-32", "checkerboard-64"}

    root = os.path.join(args.scratch, args.rung, "web-captures")
    matrix = json.load(open(L.SCENES))
    comps = matrix["components"]
    probe = set(matrix["split"]["probe"])
    scenes = {s["id"]: s for s in matrix["scenes"] if s["id"] in probe}

    widths, levels, sides = [], [], []
    tasks = []
    for pkey in PROFILES:
        profile, scale, scheme = L.PROFILES[pkey]
        for sid, scene in scenes.items():
            if scene.get("state") != "rest" or "tint" in scene:
                continue
            native = L.native_path(profile, sid)
            web = os.path.join(root, profile, sid, f"{sid}__{args.tier}.png")
            if not (os.path.exists(native) and os.path.exists(web)):
                print(f"  MISSING {pkey:9} {sid}", file=sys.stderr)
                continue
            tasks.append((scene["background"], pkey, profile, scale, scheme, sid,
                          scene["component"], native, web))

    # Ordered by (backdrop, profile): reader C's blurred-reference cache holds one at a time.
    for backdrop, pkey, profile, scale, scheme, sid, component, native, web in sorted(
            tasks, key=lambda t: (t[0], t[1], t[5])):
        shape = (int(200 * scale), int(320 * scale))
        bg = L.background_for(backdrop, scale, shape)
        cell = cell_for(component, comps)
        mask = cell.body_mask(scale, shape, 6.0)
        sources = (("web", web),) if args.web_only else (("native", native), ("web", web))
        for tag, path in sources:
            lum = L.luma_of(path)
            if lum.shape != shape:
                print(f"  SHAPE  {pkey:9} {sid} {tag} {lum.shape}", file=sys.stderr)
                continue
            base = {"profile": pkey, "scheme": scheme, "scale": scale, "scene": sid,
                    "backdrop": backdrop, "component": component, "src": tag,
                    "span": float(cell.short)}
            levels.append({**base, "body": float(lum[mask].mean()),
                           "sd": float(lum[mask].std()), "n": int(mask.sum())})
            if backdrop not in FLAT and not (args.fast and backdrop not in fast_backdrops):
                for reader, v in read_widths(lum, bg, cell, backdrop, scale,
                                             ("canonical", backdrop, scale)).items():
                    widths.append({**base, "reader": reader, **v})
            if backdrop in FLAT and cell.kind not in ("stack", "group"):
                for side in ("top", "bottom", "left", "right"):
                    u, excess, _b, _l = ALONG.side_profiles(
                        lum, cell.box, cell.radius, cell.kind, scale, side)
                    s = ALONG.summarise(u, excess)
                    if s is None:
                        continue
                    sides.append({**base, "side": side, "mean": s["mean"], "range": s["range"],
                                  "slopePerCss": s["slopePerCss"], "lengthCss": s["lengthCss"]})
        print(f"  {pkey:9} {sid:44} read", file=sys.stderr)

    path = os.path.join(args.scratch, args.rung, f"read-{args.rung}.json")
    json.dump({"rung": args.rung, "tier": args.tier, "widths": widths, "levels": levels,
               "sides": sides}, open(path, "w"), indent=1)
    print(f"{len(widths)} width rows, {len(levels)} level rows, {len(sides)} side rows -> {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
