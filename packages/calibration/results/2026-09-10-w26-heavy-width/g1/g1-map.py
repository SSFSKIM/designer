"""W26 G1 — the structural tap's ladder read: reader A and reader D per rung, per scale, with X5.

WHAT THIS READS. One rung's web captures under this child's own scratch root, and the rungs'
scratch matrices for X5's OKLab ΔE. The reference fixtures are read read-only. Nothing under
`fixtures/`, `scenes.json`, the canonical `results/matrix.json` or the canonical `web-captures/` is
written — X2.

WHAT IT PRINTS, in the order the fits are taken:

  1. **The structural tap against the grid.** G0's 9 × 9 in-shader grid read 12.22 / 11.95 / 12.04
     device px on the three 2x impulse rows at σ2x 11.3. Part (a)'s acceptance is that the third
     pyramid texture lands within 5 % of that at the same constant, which is a statement about
     captures rather than about arithmetic, because the two mechanisms integrate the same Gaussian
     by different means.
  2. **The 2x ladder**, reader A's heavy σ and share against the constant.
  3. **The 1x ladder**, reader A and reader D side by side.
  4. **X5** — the worst thin-row (span ≤ 44) OKLab ΔE move against the inert rung, at every rung.
  5. **The inert rung's byte identity** against the canonical 0.14.0 captures.

    g1-map.py [--scratch DIR] [--out FILE]
"""

import argparse
import hashlib
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import w26lib as D  # noqa: E402
import w25lib as L  # noqa: E402

SCRATCH = "/Users/new/.claude/jobs/5c70e47f/tmp/w26/g1"
IMPULSE = ("impulse__rrect-md__rest", "impulse__rrect-ml__rest", "impulse__rrect-lg__rest",
           "impulse__rrect-sm__rest")
# The rungs, and the nominal σ each one names at BOTH scale anchors.
LADDER = [("t113", 11.3), ("t11", 11.0), ("t12", 12.0), ("t10", 10.0), ("t13", 13.0),
          ("t16", 16.0), ("t19", 19.0), ("t22", 22.0), ("t25", 25.0)]
# G0's own reading of the 9 x 9 grid at σ2x 11.3, from `mapping.txt` / the findings §4.
GRID_AT_113 = {"rrect-md": 12.22, "rrect-ml": 11.95, "rrect-lg": 12.04}
# The reference's own reader-A heavy component (claims §5.113 §2), quoted with G0 §6's caveat at 1x.
REFERENCE = {"1x": {"rrect-md": 19.52}, "2x": {"rrect-md": 11.29, "rrect-ml": 12.03,
                                               "rrect-lg": 16.92}}
THIN_SPAN = 44.0


def cells_of(rung, scratch):
    path = os.path.join(scratch, rung, "rung.json")
    if not os.path.exists(path):
        return {}
    out = {}
    for cell in json.load(open(path))["cells"]:
        if cell["tier"] != "texture":
            continue
        entry = (cell.get("perceptual") or {}).get("oklabDeltaEMean")
        value = entry.get("value") if isinstance(entry, dict) else entry
        if value is None:
            continue
        out[(cell["key"]["profileKey"], cell["key"]["sceneId"])] = float(value)
    return out


def read_row(root, profile, scale, sid, comps, want_d=True):
    web = os.path.join(root, profile, sid, f"{sid}__webgpu.png")
    if not os.path.exists(web):
        return None
    shape = (int(200 * scale), int(320 * scale))
    lum = L.luma_of(web)
    if lum.shape != shape:
        return None
    bg = L.background_for("impulse", scale, shape)
    cell = L.Cell(sid.split("__")[1], comps)
    rows = L.read_psf_cell(lum, bg, cell, scale, half_css=30.0)
    a = None
    if rows:
        a = {
            "sharp": float(np.median([r["sharpSigmaDev"] for r in rows])),
            "heavy": float(np.median([r["heavySigmaDev"] for r in rows])),
            "share": float(np.median([r["heavyShare"] for r in rows])),
            "ceiling": bool(np.any([r["atCeiling"] for r in rows])),
        }
    d = D.read_lattice_cell(lum, bg, cell, scale) if want_d else None
    return a, d


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--scratch", default=SCRATCH)
    ap.add_argument("--out", default=os.path.join(HERE, "mapping.txt"))
    ap.add_argument("--no-reader-d", action="store_true")
    args = ap.parse_args(argv)
    comps = L.load_components()
    out = []
    e = out.append
    e("W26 G1 — the structural heavy blur's ladder")
    e("=" * 100)
    e("")

    # 1. The structural tap against G0's grid, at the constant G0 read it at.
    e("1. The third pyramid texture against G0's 9 x 9 in-shader grid, at sigma2x 11.3")
    e("   (part (a)'s acceptance: within 5 %; the grid's reading is claims 5.119 section 4)")
    e("")
    e(f"   {'row':>10} {'grid':>8} {'texture':>8} {'delta %':>8}   {'reference':>10}")
    root = os.path.join(args.scratch, "t113", "web-captures")
    for sid in IMPULSE[:3]:
        name = sid.split("__")[1]
        pair = read_row(root, "apple-macos-26.5-2x-light-standard", 2.0, sid, comps, want_d=False)
        if pair is None or pair[0] is None:
            e(f"   {name:>10}  NOT READ")
            continue
        got = pair[0]["heavy"]
        grid = GRID_AT_113[name]
        e(f"   {name:>10} {grid:8.2f} {got:8.2f} {(got - grid) / grid * 100:8.1f}   "
          f"{REFERENCE['2x'].get(name, float('nan')):10.2f}")
    e("")

    # 2 and 3. The ladders.
    for pkey, scale, tag in (("apple-macos-26.5-2x-light-standard", 2.0, "2x"),
                             ("apple-macos-26.5-1x-light-standard", 1.0, "1x")):
        e(f"{'2' if tag == '2x' else '3'}. The {tag} ladder — reader A, and reader D beside it")
        e("")
        head = (f"   {'rung':>6} {'sigma':>6} {'row':>10} | {'A heavy':>8} {'A share':>8} "
                f"{'A sharp':>8} {'ceil':>5}")
        if not args.no_reader_d:
            head += f" | {'D heavy':>8} {'D share':>8} {'D sharp':>8} {'D mod':>6}"
        e(head)
        for rung, sigma in LADDER:
            root = os.path.join(args.scratch, rung, "web-captures")
            for sid in IMPULSE[:3]:
                pair = read_row(root, pkey, scale, sid, comps, want_d=not args.no_reader_d)
                if pair is None:
                    continue
                a, d = pair
                if a is None:
                    continue
                line = (f"   {rung:>6} {sigma:6.1f} {sid.split('__')[1]:>10} | {a['heavy']:8.2f} "
                        f"{a['share']:8.3f} {a['sharp']:8.2f} {str(a['ceiling']):>5}")
                if d is not None:
                    line += (f" | {d['heavySigmaDev']:8.2f} {d['heavyShare']:8.3f} "
                             f"{d['sharpSigmaDev']:8.2f} {d['heavyMod']:6.3f}")
                e(line)
            e("")
        e("")

    # 4. X5.
    e("4. X5 — the thin rows (span <= 44), OKLab dE mean against the inert rung, worst move")
    e("")
    base = cells_of("r0", args.scratch)
    thin = {sid for sid in {k[1] for k in base}
            if min(comps[sid.split("__")[1]].get("size", [999, 999])) <= THIN_SPAN}
    e(f"   {'rung':>6} {'sigma':>6} {'worst dE':>9}   where")
    for rung, sigma in LADDER:
        rows = cells_of(rung, args.scratch)
        worst, where = 0.0, None
        for key, value in rows.items():
            if key[1] not in thin or key not in base:
                continue
            d = abs(value - base[key])
            if d > worst:
                worst, where = d, key
        e(f"   {rung:>6} {sigma:6.1f} {worst:9.5f}   {where}")
    e("")

    # 5. The inert rung's bytes.
    e("5. The inert rung against the canonical 0.14.0 captures, per scale")
    e("")
    for pkey in ("apple-macos-26.5-1x-light-standard", "apple-macos-26.5-2x-light-standard"):
        root = os.path.join(args.scratch, "r0", "web-captures", pkey)
        same = diff = missing = 0
        if os.path.isdir(root):
            for scene in sorted(os.listdir(root)):
                a = os.path.join(L.CAPTURES, pkey, scene, f"{scene}__webgpu.png")
                b = os.path.join(root, scene, f"{scene}__webgpu.png")
                if not (os.path.exists(a) and os.path.exists(b)):
                    missing += 1
                    continue
                da = hashlib.sha1(open(a, "rb").read()).digest()
                db = hashlib.sha1(open(b, "rb").read()).digest()
                if da == db:
                    same += 1
                else:
                    diff += 1
                    print(f"  DIFFER {pkey} {scene}", file=sys.stderr)
        e(f"   {pkey:44} {same:3d} identical, {diff:3d} differing, {missing:3d} missing")
    e("")

    text = "\n".join(out)
    print(text)
    open(args.out, "w").write(text + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
