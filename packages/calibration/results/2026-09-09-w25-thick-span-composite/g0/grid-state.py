"""W25 G0 deliverable 5 — the dark grid read for a state flip, and what a re-capture would settle.

WHAT THIS READS, all read-only: the two probe grids' native fixtures
(`results/2026-09-02-w9-probe/apple-macos-26.5-1x-light-standard/` — W9's grid under the LIGHT
scheme; `results/2026-09-06-w21-dark-scheme/probe/apple-macos-26.5-1x-dark-standard/` — the same
grid verbatim under the DARK scheme), the canonical reference fixtures, and the probe backdrops.

THE QUESTION. `tech-debt-tracker.md:874-882`: in the dark probe grid `dark-solid__rrect-sm` (span
32) and `dark-solid__rrect-lg` (160) both draw the COLLAPSED appearance while `dark-solid__rrect-md`
(96) between them does not — "a size law that collapses the small and the large surface and not the
middle one is not a size law". Either the fixture carries a state flip (the bistability of claims
5.17) or the reference keys the collapse on something other than span. This reads the grids for the
flip's signature.

THE SIGNATURES this looks for, in the order they settle the question.

  1. BYTE IDENTITY ACROSS SCHEMES. A light-scheme capture and a dark-scheme capture of the same
     scene are the same file only if the material's appearance does not depend on the scheme at
     all — which is what a FULLY collapsed surface does, since a collapsed body has stopped
     following the scheme's own tint — or if the fixture was not re-captured. Either way the
     identity is the strongest statement the fixtures make about the state, and it is checkable
     without any model.
  2. THE BODY AND THE RIM against the scheme's two poles. A cell is read against the same scene's
     light-scheme twin: a collapsed cell sits on the dark pole in both schemes, an uncollapsed one
     moves between them. `k` here is where the cell's body falls between the two, 1 = it did not
     move (collapsed), 0 = it moved the whole way.
  3. THE ORDER ALONG THE SPAN AXIS. With `rrect-sm`, `-md`, `-ml` and `-lg` all over one backdrop,
     a size-keyed collapse is MONOTONE in span. A non-monotone order is not a size law and is what
     a state flip looks like.

Units: linear Rec.709 luma; bodies over the declared shape eroded 6 CSS px; the rim is the peak
excess over the body in the outer 6 CSS px, as in `along-side.py`.

Usage: grid-state.py [--out grid-state.txt]
"""

import argparse
import hashlib
import os
import sys

import numpy as np

import w25lib as L

SPAN = {"rrect-sm": 32.0, "capsule-button": 44.0, "rrect-md": 96.0, "rrect-ml": 128.0,
        "rrect-lg": 160.0}
ORDER = ["rrect-sm", "capsule-button", "rrect-md", "rrect-ml", "rrect-lg"]


def sha(path):
    return hashlib.sha1(open(path, "rb").read()).hexdigest()


def body_and_rim(lum, cell, scale):
    body_mask = cell.body_mask(scale, lum.shape, 6.0)
    outer = cell.body_mask(scale, lum.shape, 0.0)
    rim_band = outer & ~body_mask
    body = float(lum[body_mask].mean())
    rim = float(np.percentile(lum[rim_band], 99.0)) - body if rim_band.any() else float("nan")
    return body, rim, float(lum[body_mask].std())


def read_dir(d, scale, comps):
    rows = {}
    if not os.path.isdir(d):
        return rows
    for f in sorted(os.listdir(d)):
        if not f.endswith(".png"):
            continue
        sid = f[:-4]
        parts = sid.split("__")
        if len(parts) != 3 or parts[2] != "rest" or parts[1] not in SPAN:
            continue
        lum = L.luma_of(os.path.join(d, f))
        if lum.shape != (int(200 * scale), int(320 * scale)):
            continue
        cell = L.Cell(parts[1], comps)
        b, r, sd = body_and_rim(lum, cell, scale)
        rows[sid] = {"backdrop": parts[0], "component": parts[1], "span": SPAN[parts[1]],
                     "body": b, "rim": r, "sd": sd, "sha": sha(os.path.join(d, f)),
                     "path": os.path.join(d, f)}
    return rows


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="grid-state.txt")
    args = ap.parse_args(argv)
    comps = L.load_components()

    light = read_dir(L.PROBES["w9-1x-light"][0], 1.0, comps)
    dark = read_dir(L.PROBES["w21-1x-dark"][0], 1.0, comps)
    canon = {k: read_dir(os.path.join(L.FIXTURES, p), s, comps)
             for k, (p, s, _sch) in L.PROFILES.items()}

    with open(args.out, "w") as fh:
        def w(s=""):
            fh.write(s + "\n")

        w(__doc__.strip())
        w()
        w("=" * 104)
        w("TABLE 1 — signature 1: the scenes whose LIGHT-scheme and DARK-scheme captures are the")
        w("SAME FILE. Instrument: SHA-1 over the PNG bytes. Left column: the two probe grids")
        w("(W9 light against W21 dark, the same scene ids). Right block: the canonical bed's two")
        w("1x profiles.")
        w("=" * 104)
        w(f"{'source':14} {'scene':40} {'span':>5} {'identical':>10} {'light body':>11} "
          f"{'dark body':>10} {'light rim':>10} {'dark rim':>9}")
        for sid in sorted(set(light) & set(dark), key=lambda s: (ORDER.index(light[s]["component"]),
                                                                light[s]["backdrop"])):
            a, b = light[sid], dark[sid]
            w(f"{'probe grids':14} {sid[:40]:40} {a['span']:5.0f} "
              f"{'YES' if a['sha'] == b['sha'] else 'no':>10} {a['body']:11.5f} {b['body']:10.5f} "
              f"{a['rim']:10.5f} {b['rim']:9.5f}")
        w()
        cl, cd = canon.get("1x-light", {}), canon.get("1x-dark", {})
        for sid in sorted(set(cl) & set(cd)):
            a, b = cl[sid], cd[sid]
            w(f"{'canonical 1x':14} {sid[:40]:40} {a['span']:5.0f} "
              f"{'YES' if a['sha'] == b['sha'] else 'no':>10} {a['body']:11.5f} {b['body']:10.5f} "
              f"{a['rim']:10.5f} {b['rim']:9.5f}")
        w()
        cl2, cd2 = canon.get("2x-light", {}), canon.get("2x-dark", {})
        for sid in sorted(set(cl2) & set(cd2)):
            a, b = cl2[sid], cd2[sid]
            w(f"{'canonical 2x':14} {sid[:40]:40} {a['span']:5.0f} "
              f"{'YES' if a['sha'] == b['sha'] else 'no':>10} {a['body']:11.5f} {b['body']:10.5f} "
              f"{a['rim']:10.5f} {b['rim']:9.5f}")
        w()

        w("=" * 104)
        w("TABLE 2 — signature 2: how far the DARK capture moved from its LIGHT twin, per scene.")
        w("`k` = 1 means the dark capture is the light one (the surface stopped following the")
        w("scheme — the collapsed state); `k` = 0 means it moved the whole way to the scheme's own")
        w("appearance. The denominator is the largest move any cell over that backdrop made, so")
        w("`k` is comparable within a backdrop column and not across them.")
        w("=" * 104)
        w(f"{'backdrop':16} {'component':16} {'span':>5} {'light body':>11} {'dark body':>10} "
          f"{'|move|':>9} {'k':>7} {'light rim':>10} {'dark rim':>9} {'same file':>10}")
        for bd in sorted({r["backdrop"] for r in light.values()}):
            ids = [s for s in set(light) & set(dark) if light[s]["backdrop"] == bd]
            if not ids:
                continue
            moves = {s: abs(dark[s]["body"] - light[s]["body"]) for s in ids}
            biggest = max(moves.values()) or 1.0
            for s in sorted(ids, key=lambda s: SPAN[light[s]["component"]]):
                a, b = light[s], dark[s]
                w(f"{bd:16} {a['component']:16} {a['span']:5.0f} {a['body']:11.5f} "
                  f"{b['body']:10.5f} {moves[s]:9.5f} {1 - moves[s] / biggest:7.3f} "
                  f"{a['rim']:10.5f} {b['rim']:9.5f} "
                  f"{'YES' if a['sha'] == b['sha'] else 'no':>10}")
            w()

        w("=" * 104)
        w("TABLE 3 — signature 3: the span axis inside ONE grid and one backdrop. A size-keyed")
        w("collapse is monotone in span. `monotone` says whether body and rim move one way across")
        w("the spans present.")
        w("=" * 104)
        for name, grid in (("W21 dark probe grid", dark), ("W9 light probe grid", light)):
            w(f"-- {name}")
            w(f"   {'backdrop':16} " + " ".join(f"{c:>17}" for c in ORDER))
            for bd in sorted({r["backdrop"] for r in grid.values()}):
                cells = {grid[s]["component"]: grid[s] for s in grid if grid[s]["backdrop"] == bd}
                if len(cells) < 2:
                    continue
                bodies = [cells[c]["body"] if c in cells else None for c in ORDER]
                rims = [cells[c]["rim"] if c in cells else None for c in ORDER]
                seq = [v for v in bodies if v is not None]
                mono = (all(x <= y + 1e-9 for x, y in zip(seq, seq[1:]))
                        or all(x >= y - 1e-9 for x, y in zip(seq, seq[1:])))
                w(f"   {bd:16} " + " ".join("      —          " if v is None
                                            else f"{v:9.5f}/{r:+8.5f}"
                                            for v, r in zip(bodies, rims))
                  + f"   body monotone: {'yes' if mono else 'NO'}")
            w()

        w("=" * 104)
        w("TABLE 4 — signature 1 again, from the grid's OWN record. The W21 probe grid's")
        w("`manifest.json` was materialised by the majority byte-state per cell over seven attested")
        w("runs at one sitting (`probe/provenance.json`: rule = 'majority byte-state per cell")
        w("across the attested runs (frequency-settled, claims 5.30); shares recorded per cell'),")
        w("and it records `observedStates` and the share of each state. Every cell that observed")
        w("MORE THAN ONE byte-state is listed. This is the bistability of claims 5.17, counted.")
        w("=" * 104)
        man = os.path.join(os.path.dirname(L.PROBES["w21-1x-dark"][0]), "manifest.json")
        total = flips = 0
        if os.path.exists(man):
            import json as _json
            m = _json.load(open(man))
            w(f"{'scene':44} {'states':>7} {'shares':>22} {'settled':>8}")
            for prof in m["profiles"]:
                for f in prof["fixtures"]:
                    total += 1
                    if f.get("observedStates", 1) > 1:
                        flips += 1
                        sh = ", ".join(f"{s['share']:.4f}" for s in f.get("stateFrequencies", []))
                        w(f"{f['sceneId']:44} {f['observedStates']:7d} {sh:>22} "
                          f"{str(f.get('frequencySettled')):>8}")
            w()
            w(f"{flips} of {total} cells observed two byte-states across the seven attested runs.")
        w()

        w("=" * 104)
        w("TABLE 5 — the collapse read where it is keyed: `dark-solid`, both grids, against the")
        w("backdrop's own level. A collapsed body sits AT the backdrop (delta near zero and the")
        w("body's sd exactly 0); an uncollapsed one sits far above it. `margin` is the shape's")
        w("clearance to the canvas edge in CSS px on its short axis — the quantity that moves with")
        w("span on this 320x200 canvas and is therefore confounded with it.")
        w("=" * 104)
        w(f"{'grid':12} {'component':12} {'span':>5} {'margin':>7} {'body':>10} {'backdrop':>10} "
          f"{'delta':>10} {'sd':>9} {'state':>13}")
        for gname, grid, gdir in (("w9-1x-light", light, L.PROBES["w9-1x-light"][0]),
                                  ("w21-1x-dark", dark, L.PROBES["w21-1x-dark"][0])):
            bg = L.probe_background("dark-solid", 1.0, (200, 320))
            for comp in ("rrect-sm", "rrect-md", "rrect-lg"):
                sid = f"dark-solid__{comp}__rest"
                if sid not in grid:
                    continue
                cell = L.Cell(comp, comps)
                lum = L.luma_of(grid[sid]["path"])
                mask = cell.body_mask(1.0, lum.shape, 6.0)
                body, back = float(lum[mask].mean()), float(bg[mask].mean())
                short = min(cell.box["width"], cell.box["height"])
                margin = (200.0 - short) / 2.0
                state = "COLLAPSED" if abs(body - back) < 0.002 else "not collapsed"
                w(f"{gname:12} {comp:12} {short:5.0f} {margin:7.1f} {body:10.6f} {back:10.6f} "
                  f"{body - back:+10.6f} {float(lum[mask].std()):9.6f} {state:>13}")
        w()
    print(f"-> {args.out}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
