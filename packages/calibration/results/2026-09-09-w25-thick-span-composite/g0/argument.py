"""W25 G0 deliverable 3 — the size law's argument: what grades the reference's width and level.

WHAT THIS READS, all read-only: the canonical reference fixtures and the canonical web captures
through `widths.json` (written by `widths.py` beside this file), plus the two probe grids' native
fixtures directly — `results/2026-09-02-w9-probe/…-1x-light-standard/` and
`results/2026-09-06-w21-dark-scheme/probe/…-1x-dark-standard/`.

THE QUESTION. `packages/renderer-webgpu/src/instances.ts:204` makes the size law's argument the
SHORT SIDE in CSS px, `spanPx = min(width, height)`, and `sizeThickness` = smoothstep(32, 96, span)
saturates at 96 — so spans 96, 128, 130 and 160 are one number to it, which is why the scatter
ramp grew a third `far` anchor to route around the saturation (`material.ts:847-858`). This asks
what the REFERENCE grades on, over the five thick spans the fixtures carry:

    44   `toolbar-group`'s member (44 x 44,  area 1936,  radius 22)
    96   `rrect-md`             (160 x  96,  area 15360, radius 20)
   128   `rrect-ml`             (224 x 128,  area 28672, radius 27)
   130   `glass-over-glass`'s base (220 x 130, area 28600, radius 24)
   160   `rrect-lg`             (280 x 160,  area 44800, radius 34)

plus the thin controls `rrect-sm` (32) and `capsule-button` (44), and the probe grids' span sweep
over ONE backdrop, which is the only place on disk where span moves with everything else held.

WHY THE PROBE GRIDS MATTER HERE, and not only for coverage. `validate.txt` puts reader C's
identification bound at about a QUARTER of the backdrop's step pitch: 4 device px on the canonical
16 CSS px checkerboard at 1x. The probe grids carry `checkerboard-32` and `checkerboard-64`, whose
pitch is two and four times as coarse, so the same reader identifies widths two and four times as
wide there. A width law for thick surfaces cannot be fitted on a 16 px checkerboard at all; it can
be fitted on a 64 px one.

THE CANDIDATE ARGUMENTS, each scored the same way: the reference's width (and, separately, its
body level) regressed on the candidate across the spans available in one profile and one backdrop,
reported as the correlation and the residual of a straight line in that variable. The candidates
are the short side, the long side, the area, the radius, and the short side through a saturating
smoothstep at the landed knee — the last so that "the current law, unchanged" is one of the rows
being scored and not the assumed baseline.

UNITS. Widths in DEVICE px with the CSS-px value beside them; levels in linear Rec.709 luma.

Usage: argument.py [--out argument.txt]     (reads widths.json if present)
"""

import argparse
import json
import os
import sys

import numpy as np

import w25lib as L

GEOM = {
    "rrect-sm":         (64.0, 32.0, 8.0),
    "capsule-button":   (120.0, 44.0, 22.0),
    "toolbar-group":    (44.0, 44.0, 22.0),
    "rrect-md":         (160.0, 96.0, 20.0),
    "rrect-ml":         (224.0, 128.0, 27.0),
    "glass-over-glass": (220.0, 130.0, 24.0),
    "rrect-lg":         (280.0, 160.0, 34.0),
}
SPAN_ORDER = ["rrect-sm", "capsule-button", "toolbar-group", "rrect-md", "rrect-ml",
              "glass-over-glass", "rrect-lg"]
# The landed law, restated from `packages/calibration/profiles/apple-macos-26.5-1x-light-standard.json`
# and `material.ts:2863-2869`, so "the current argument" is one of the candidates being scored.
SIZE_SPAN_MIN, SIZE_SPAN_MAX = 32.0, 96.0


def size_thickness(span):
    t = np.clip((np.asarray(span, dtype=float) - SIZE_SPAN_MIN)
                / (SIZE_SPAN_MAX - SIZE_SPAN_MIN), 0.0, 1.0)
    return t * t * (3.0 - 2.0 * t)


def candidates(component):
    w, h, r = GEOM[component]
    short, long_ = min(w, h), max(w, h)
    return {
        "short side": short,
        "long side": long_,
        "area": w * h,
        "sqrt(area)": np.sqrt(w * h),
        "radius": r,
        "sizeThickness(short)": float(size_thickness(short)),
    }


def score(xs, ys):
    """A straight line in the candidate: Pearson r, and the fit's RMS as a fraction of ys' spread."""
    xs, ys = np.asarray(xs, float), np.asarray(ys, float)
    ok = np.isfinite(xs) & np.isfinite(ys)
    if ok.sum() < 3 or np.std(xs[ok]) < 1e-12 or np.std(ys[ok]) < 1e-12:
        return float("nan"), float("nan"), int(ok.sum())
    r = float(np.corrcoef(xs[ok], ys[ok])[0, 1])
    a, b = np.polyfit(xs[ok], ys[ok], 1)
    rms = float(np.sqrt(np.mean((a * xs[ok] + b - ys[ok]) ** 2)))
    return r, rms / max(float(np.std(ys[ok])), 1e-12), int(ok.sum())


def read_probe_axis():
    """The span axis on the probe grids: reader C's width and the body level, per backdrop.

    Both grids are 1x, so DEVICE px and CSS px coincide here and the numbers are directly
    comparable with the canonical 1x rows.
    """
    comps = L.load_components()
    rows = []
    for key, (d, scale, scheme, _sc) in L.PROBES.items():
        if not os.path.isdir(d):
            continue
        for f in sorted(os.listdir(d)):
            if not f.endswith(".png"):
                continue
            sid = f[:-4]
            parts = sid.split("__")
            if len(parts) != 3 or parts[2] != "rest" or parts[1] not in GEOM:
                continue
            backdrop, component, _ = parts
            if backdrop.startswith("light-solid") or backdrop.startswith("dark-solid") \
                    or backdrop.startswith("mid-dark-solid"):
                level_only = True
            else:
                level_only = False
            lum = L.luma_of(os.path.join(d, f))
            shape = (int(200 * scale), int(320 * scale))
            if lum.shape != shape:
                continue
            cell = L.Cell(component, comps)
            mask = cell.body_mask(scale, lum.shape, 6.0)
            row = {"grid": key, "scheme": scheme, "scale": scale, "backdrop": backdrop,
                   "component": component, "scene": sid,
                   "pitchCss": L.backdrop_pitch_css(backdrop),
                   "body": float(lum[mask].mean()), "sd": float(lum[mask].std())}
            row.update(candidates(component))
            if not level_only:
                bg = L.probe_background(backdrop, scale, shape)
                m = L.sigma_match(lum, bg, mask, top=64.0, ref_key=("probe", backdrop, scale))
                row["sigmaDev"] = m["sigmaDev"]
                row["sigmaResid"] = m["rmsRel"]
                row["sigmaGain"] = m.get("gain")
                pitch = row["pitchCss"]
                row["bound"] = pitch / 4.0 * scale if pitch else None
                row["flag"] = ("" if row["bound"] is None or not np.isfinite(m["sigmaDev"])
                               or m["sigmaDev"] <= row["bound"] else ">bound")
            rows.append(row)
    return rows


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="argument.txt")
    ap.add_argument("--widths", default="widths.json")
    ap.add_argument("--refresh-probe", action="store_true")
    args = ap.parse_args(argv)

    canon = json.load(open(args.widths)) if os.path.exists(args.widths) else {"widths": [],
                                                                              "levels": []}
    # The probe read is the slow half (one sigma-match per cell over a 145-point grid); it depends
    # only on the committed fixtures, so it is cached and reused unless --refresh-probe is given.
    if os.path.exists("argument-probe.json") and not args.refresh_probe:
        probe = json.load(open("argument-probe.json"))
    else:
        probe = read_probe_axis()
        json.dump(probe, open("argument-probe.json", "w"), indent=1)

    with open(args.out, "w") as fh:
        def w(s=""):
            fh.write(s + "\n")

        w(__doc__.strip())
        w()
        w("=" * 106)
        w("TABLE 1 — the span axis on the PROBE GRIDS, one backdrop at a time, 1x, native only.")
        w("Instrument: reader C (`w25lib.sigma_match`, grid 0..64 device px) and the body mean over")
        w("the declared shape eroded 6 CSS px. `bound` is a quarter of the backdrop's own step")
        w("pitch — reader C's validated identification limit (validate.txt) — and `>bound` marks a")
        w("width past it, which is a lower bound and not a reading.")
        w("=" * 106)
        w(f"{'grid':12} {'backdrop':18} {'component':17} {'short':>6} {'long':>5} {'area':>7} "
          f"{'sigma dev':>10} {'resid':>7} {'bound':>6} {'flag':>7} {'body':>9} {'sd':>8}")
        for r in sorted(probe, key=lambda r: (r["grid"], r["backdrop"],
                                              SPAN_ORDER.index(r["component"]))):
            w(f"{r['grid']:12} {r['backdrop']:18} {r['component']:17} {r['short side']:6.0f} "
              f"{r['long side']:5.0f} {r['area']:7.0f} "
              f"{_f(r.get('sigmaDev'), 10, 2)} {_f(r.get('sigmaResid'), 7, 3)} "
              f"{_f(r.get('bound'), 6, 1)} {r.get('flag', ''):>7} {r['body']:9.5f} {r['sd']:8.4f}")
        w()

        w("=" * 106)
        w("TABLE 2 — which candidate grades the reference. Each row scores ONE candidate against")
        w("the reference's width (and its body level) across the spans available inside one grid")
        w("and one backdrop. `r` is Pearson's correlation, `resid` the straight line's RMS as a")
        w("fraction of the quantity's own spread; n is the number of spans in the group. A group")
        w("with fewer than 3 spans is not scored.")
        w("=" * 106)
        w(f"{'grid':12} {'backdrop':18} {'quantity':7} {'candidate':22} {'n':>3} {'r':>7} "
          f"{'resid':>7}")
        groups = {}
        for r in probe:
            groups.setdefault((r["grid"], r["backdrop"]), []).append(r)
        for k in sorted(groups):
            g = groups[k]
            if len({x["component"] for x in g}) < 3:
                continue
            for qty, getter in (("width", lambda x: x.get("sigmaDev", float("nan"))),
                                ("level", lambda x: x["body"])):
                ys = [getter(x) for x in g]
                if not np.isfinite(ys).any():
                    continue
                for cname in ("short side", "long side", "area", "sqrt(area)", "radius",
                              "sizeThickness(short)"):
                    r_, resid, n = score([x[cname] for x in g], ys)
                    w(f"{k[0]:12} {k[1]:18} {qty:7} {cname:22} {n:3d} {_f(r_, 7, 3)} "
                      f"{_f(resid, 7, 3)}")
                w()
        w()

        w("=" * 106)
        w("TABLE 3 — the knee. Is there a step in the reference's width or level ABOVE span 96,")
        w("where the landed `sizeThickness` is already saturated at exactly 1? The row prints the")
        w("value at each span and the change from the span below it; a law saturating at 96 would")
        w("show no change from 96 upward.")
        w("=" * 106)
        for k in sorted(groups):
            g = sorted(groups[k], key=lambda x: x["short side"])
            if len(g) < 3:
                continue
            w(f"-- {k[0]} / {k[1]}")
            w(f"   {'span':>5} {'sizeThickness':>14} {'sigma dev':>10} {'d sigma':>9} "
              f"{'body':>9} {'d body':>9}")
            prev_s = prev_b = None
            for x in g:
                s, b = x.get("sigmaDev", float("nan")), x["body"]
                w(f"   {x['short side']:5.0f} {x['sizeThickness(short)']:14.4f} "
                  f"{_f(s, 10, 2)} {_f(None if prev_s is None else s - prev_s, 9, 2)} "
                  f"{b:9.5f} {_f(None if prev_b is None else b - prev_b, 9, 5)}")
                prev_s, prev_b = s, b
            w()

        w("=" * 106)
        w("TABLE 4 — the unit. The reference's width at 2x divided by its width at 1x, per cell")
        w("and reader, from the canonical bed (`widths.json`). A ratio of 2 means the width is")
        w("invariant in CSS px; 1 means invariant in DEVICE px; anything else means neither, and")
        w("the value is what a per-scale anchor has to carry. vitrea's column is the same ratio on")
        w("the landed GPU captures.")
        w("=" * 106)
        w(f"{'scene':42} {'R':1} {'nat 1x':>8} {'nat 2x':>8} {'nat 2x/1x':>10} {'gpu 1x':>8} "
          f"{'gpu 2x':>8} {'gpu 2x/1x':>10}")
        byscene = {}
        for r in canon["widths"]:
            byscene.setdefault((r["scene"], r["reader"], r["src"]), {})[r["profileKey"]] = r
        scenes = sorted({(k[0], k[1]) for k in byscene})
        for scene, reader in scenes:
            for schemepair in (("1x-light", "2x-light"), ("1x-dark", "2x-dark")):
                n1 = byscene.get((scene, reader, "native"), {}).get(schemepair[0])
                n2 = byscene.get((scene, reader, "native"), {}).get(schemepair[1])
                g1 = byscene.get((scene, reader, "webgpu"), {}).get(schemepair[0])
                g2 = byscene.get((scene, reader, "webgpu"), {}).get(schemepair[1])
                if not (n1 and n2):
                    continue
                nr = n2["sigmaDev"] / n1["sigmaDev"] if n1["sigmaDev"] else float("nan")
                gr = (g2["sigmaDev"] / g1["sigmaDev"] if g1 and g2 and g1["sigmaDev"]
                      else float("nan"))
                tag = "dark" if "dark" in schemepair[0] else "light"
                w(f"{(scene + ' [' + tag + ']')[:42]:42} {reader:1} {n1['sigmaDev']:8.2f} "
                  f"{n2['sigmaDev']:8.2f} {nr:10.2f} "
                  f"{_f(g1['sigmaDev'] if g1 else None, 8, 2)} "
                  f"{_f(g2['sigmaDev'] if g2 else None, 8, 2)} {_f(gr, 10, 2)}")
        w()

        w("=" * 106)
        w("TABLE 5 — the same axis on the canonical bed: the reference's width and level against")
        w("span, per profile and backdrop, with vitrea's beside them. Levels from `widths.json`.")
        w("=" * 106)
        w(f"{'profile':9} {'backdrop':13} {'component':17} {'span':>5} {'nat sigma':>10} "
          f"{'gpu sigma':>10} {'nat body':>9} {'gpu body':>9} {'d code':>8}")
        lev = {}
        for r in canon["levels"]:
            lev.setdefault((r["profileKey"], r["scene"]), {})[r["src"]] = r
        wid = {}
        for r in canon["widths"]:
            if r["reader"] == "C":
                wid.setdefault((r["profileKey"], r["scene"]), {})[r["src"]] = r
        for k in sorted(lev, key=lambda k: (k[0], k[1])):
            d = lev[k]
            if "native" not in d:
                continue
            comp = d["native"]["component"]
            if comp not in GEOM:
                continue
            wd = wid.get(k, {})
            nat, gpu = d["native"], d.get("webgpu")
            w(f"{k[0]:9} {nat['backdrop']:13} {comp:17} {GEOM[comp][1]:5.0f} "
              f"{_f(wd.get('native', {}).get('sigmaDev'), 10, 2)} "
              f"{_f(wd.get('webgpu', {}).get('sigmaDev'), 10, 2)} "
              f"{nat['body']:9.5f} {_f(gpu['body'] if gpu else None, 9, 5)} "
              f"{_f(L.codes(gpu['body'], nat['body']) if gpu else None, 8, 2)}")
    print(f"-> {args.out}", file=sys.stderr)
    return 0


def _f(v, width=8, p=2):
    return f"{'—':>{width}}" if v is None or not np.isfinite(v) else f"{v:{width}.{p}f}"


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
