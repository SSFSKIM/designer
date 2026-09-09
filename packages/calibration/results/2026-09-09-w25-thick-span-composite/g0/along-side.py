"""W25 G0 deliverable 4 — the along-side reader: the rim's excess as a function of POSITION.

WHAT THIS READS. The reference fixtures and the canonical web captures, read-only, plus the
backdrop rasters. Nothing is written outside this directory.

THE IDEA. W24's angular reader bins the rim's peak excess by the NORMAL's direction, which is what
made the along-side variation visible at all ("2x dark `dark-solid__rrect-md`, top edge
0.0442 -> 0.0158", claims 5.108 section 1) and is also what hides it: on a straight side every
point has the same normal, so a whole side is one bin and the variation inside it is an average.
This reader keeps the same quantity — the rim's peak excess over the body along the inward normal —
and indexes it by POSITION along the side instead.

  - The side's straight part only: the corner arcs are excluded by dropping `radius` CSS px from
    each end, so nothing here is a corner reading.
  - At each position `u` (CSS px from the side's midpoint, signed), the inward profile is read at
    depths 0.5, 1.5, ... CSS px inside the declared contour.
  - `excess(u)` = max over depth in [0, RIM_CSS] of profile(u, d) minus `body(u)`, and `body(u)` is
    the mean of the same profile over depths [BODY_LO, BODY_HI] CSS px — the body BESIDE that point,
    never the shape's global mean, so a lens or a backdrop gradient under the surface is divided out
    of the level and left only in the rim.

THE VERDICT this is built to reach. Three signatures, and they separate:
  (a) a THICKNESS term — the grading's size scales with the span, and is absent on the flat controls
      (`capsule-button` 44 and `rrect-sm` 32);
  (b) the LENS — the grading follows the backdrop's own luminance gradient under the surface, so it
      vanishes on a FLAT backdrop (`dark-solid`, `light-solid`) and follows the structure on
      `checkerboard`;
  (c) neither — the grading is a fixed asymmetry of the capture (a light direction, a window
      shadow), in which case it is the same shape on every component at a given scale.
`dark-solid` is the discriminating backdrop and is read first wherever it exists: a grading there
cannot be the lens refracting a gradient that is not present.

UNITS. `u` in CSS px along the side. Excess in linear Rec.709 luma. Depths in CSS px.

Usage: along-side.py [--out along-side.txt]
"""

import argparse
import json
import os
import sys

import numpy as np

import w25lib as L

RIM_CSS = 6.0        # the rim band, W22's and W24's erosion depth
BODY_LO, BODY_HI = 10.0, 20.0
BINS = 16
# The four thick shapes the wave names, plus W24's two flat controls.
ORDER = ["capsule-button", "rrect-sm", "rrect-md", "rrect-ml", "rrect-lg", "glass-over-glass"]
SPAN = {"capsule-button": 44.0, "rrect-sm": 32.0, "rrect-md": 96.0, "rrect-ml": 128.0,
        "rrect-lg": 160.0, "glass-over-glass": 130.0}


def side_profiles(lum, box, radius, kind, scale, side):
    """Per position along one straight side, the inward profile in CSS-px depth bins.

    Returns (u_css, excess, body, backdrop_u) with `u` measured from the side's midpoint.
    """
    h, w = lum.shape
    r = (box["height"] / 2.0 if kind == "capsule" else radius)
    r = min(r, box["width"] / 2.0, box["height"] / 2.0)
    depths = np.arange(0.5, BODY_HI + 1.0, 1.0 / scale)   # CSS px, one device px apart
    if side in ("top", "bottom"):
        span_len = box["width"]
        u0, u1 = box["left"] + r, box["left"] + box["width"] - r
        edge = box["top"] if side == "top" else box["top"] + box["height"]
        sgn = 1.0 if side == "top" else -1.0
        us = np.arange(u0 + 0.5 / scale, u1, 1.0 / scale)
        cols = np.round(us * scale - 0.5).astype(int)
        rowsets = [np.round((edge + sgn * d) * scale - 0.5).astype(int) for d in depths]
        prof = np.full((len(us), len(depths)), np.nan)
        for j, rr in enumerate(rowsets):
            if 0 <= rr < h:
                ok = (cols >= 0) & (cols < w)
                prof[ok, j] = lum[rr, cols[ok]]
        centre = box["left"] + box["width"] / 2.0
    else:
        span_len = box["height"]
        u0, u1 = box["top"] + r, box["top"] + box["height"] - r
        edge = box["left"] if side == "left" else box["left"] + box["width"]
        sgn = 1.0 if side == "left" else -1.0
        us = np.arange(u0 + 0.5 / scale, u1, 1.0 / scale)
        rows = np.round(us * scale - 0.5).astype(int)
        colsets = [np.round((edge + sgn * d) * scale - 0.5).astype(int) for d in depths]
        prof = np.full((len(us), len(depths)), np.nan)
        for j, cc in enumerate(colsets):
            if 0 <= cc < w:
                ok = (rows >= 0) & (rows < h)
                prof[ok, j] = lum[rows[ok], cc]
        centre = box["top"] + box["height"] / 2.0
    rim = prof[:, depths <= RIM_CSS]
    bodyband = prof[:, (depths >= BODY_LO) & (depths <= BODY_HI)]
    body = np.nanmean(bodyband, axis=1)
    excess = np.nanmax(rim, axis=1) - body
    return us - centre, excess, body, span_len


def summarise(u, excess, bins=BINS):
    """The along-side profile reduced to `bins` equal buckets, plus the grading statistics."""
    ok = np.isfinite(excess)
    if ok.sum() < bins:
        return None
    u, excess = u[ok], excess[ok]
    edges = np.linspace(u.min(), u.max(), bins + 1)
    idx = np.clip(np.digitize(u, edges) - 1, 0, bins - 1)
    means = np.array([excess[idx == b].mean() if (idx == b).any() else np.nan
                      for b in range(bins)])
    mid = (edges[:-1] + edges[1:]) / 2.0
    good = np.isfinite(means)
    if good.sum() < 3:
        return None
    slope = np.polyfit(mid[good], means[good], 1)[0]
    return {
        "bins": means.tolist(), "mid": mid.tolist(),
        "mean": float(np.nanmean(means)), "min": float(np.nanmin(means)),
        "max": float(np.nanmax(means)), "range": float(np.nanmax(means) - np.nanmin(means)),
        "rangeRel": float((np.nanmax(means) - np.nanmin(means)) / max(abs(np.nanmean(means)), 1e-9)),
        "slopePerCss": float(slope),
        "lengthCss": float(u.max() - u.min()),
    }


def cell_boxes(cell):
    if cell.kind == "stack":
        return [("base", *cell.base)]
    if cell.kind == "group":
        return [(f"m{i}", *m) for i, m in enumerate(cell.members)]
    return [("", cell.box, cell.radius, cell.kind)]


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="along-side.txt")
    args = ap.parse_args(argv)

    comps = L.load_components()
    out = []
    # The canonical bed first, then the two probe grids. A probe row is marked by its profile key
    # (`w9-1x-light`, `w21-1x-dark`) and carries no web side: the grids were captured natively by
    # wave-local scripts and vitrea has never been rendered against them.
    beds = [(key, os.path.join(L.FIXTURES, profile), scale, scheme, True)
            for key, (profile, scale, scheme) in L.PROFILES.items()]
    beds += [(key, d, scale, scheme, False) for key, (d, scale, scheme, _sc) in L.PROBES.items()]
    for key, pdir, scale, scheme, canonical in beds:
        profile = L.PROFILES[key][0] if canonical else None
        if not os.path.isdir(pdir):
            continue
        for f in sorted(os.listdir(pdir)):
            if not f.endswith(".png"):
                continue
            sid = f[:-4]
            parts = sid.split("__")
            if len(parts) != 3 or parts[2] != "rest":
                continue
            backdrop, component, _ = parts
            if component not in ORDER:
                continue
            cell = L.Cell(component, comps)
            shape = (int(200 * scale), int(320 * scale))
            bg = (L.background_for(backdrop, scale, shape) if canonical
                  else L.probe_background(backdrop, scale, shape))
            srcs = [("native", os.path.join(pdir, f))]
            if canonical:
                for tier in ("webgpu", "css"):
                    wp = L.web_path(profile, sid, tier)
                    if os.path.exists(wp):
                        srcs.append((tier, wp))
            for tag, path in srcs:
                if not os.path.exists(path):
                    continue
                lum = L.luma_of(path)
                if lum.shape != shape:
                    continue
                for label, box, rad, kind in cell_boxes(cell):
                    for side in ("top", "bottom", "left", "right"):
                        u, ex, body, _ = side_profiles(lum, box, rad, kind, scale, side)
                        s = summarise(u, ex)
                        if s is None:
                            continue
                        ub, exb, _, _ = side_profiles(bg, box, rad, kind, scale, side)
                        sb = summarise(ub, exb)
                        # The backdrop's own level along the same side, at the body's depth: the
                        # quantity the lens would be refracting.
                        _, _, bgbody, _ = side_profiles(bg, box, rad, kind, scale, side)
                        okb = np.isfinite(bgbody) & np.isfinite(ex)
                        corr = (float(np.corrcoef(bgbody[okb], ex[okb])[0, 1])
                                if okb.sum() > 8 and np.std(bgbody[okb]) > 1e-9 else float("nan"))
                        out.append({
                            "profileKey": key, "scale": scale, "scheme": scheme, "scene": sid,
                            "backdrop": backdrop, "component": component, "sub": label,
                            "side": side, "src": tag, "span": SPAN[component],
                            "backdropSdAlongSide": float(np.nanstd(bgbody)),
                            "corrWithBackdrop": corr, **s,
                        })
    json.dump(out, open("along-side.json", "w"), indent=1)
    write(out, args.out)
    return 0


def fnum(v, w=8, p=4):
    return f"{'—':>{w}}" if v is None or not np.isfinite(v) else f"{v:{w}.{p}f}"


def write(rows, path):
    with open(path, "w") as fh:
        def w(s=""):
            fh.write(s + "\n")

        w(__doc__.strip())
        w()
        w("=" * 108)
        w("TABLE 1 — the along-side profile per side, in 16 equal buckets from one end of the")
        w("straight part to the other. Instrument: this file's `side_profiles`. Unit: linear")
        w("Rec.709 luma, the rim's peak excess over the body BESIDE it.")
        w("`range/mean` is the grading's size relative to the rim's own height; `slope` is the")
        w("least-squares gradient in luma per CSS px along the side; `corr` is the correlation of")
        w("excess(u) with the BACKDROP's own level under the body at the same u — the lens's")
        w("signature — and is blank where the backdrop is flat along that side (sd < 1e-9).")
        w("=" * 108)
        w(f"{'profile':9} {'scene':40} {'src':7} {'side':6} {'span':>5} {'mean':>9} {'min':>9} "
          f"{'max':>9} {'range':>9} {'r/mean':>8} {'slope':>10} {'bgSd':>8} {'corr':>7}")
        for r in sorted(rows, key=lambda r: (ORDER.index(r["component"]), r["backdrop"],
                                             r["profileKey"], r["src"], r["side"])):
            w(f"{r['profileKey']:9} {r['scene'][:40]:40} {r['src']:7} {r['side']:6} "
              f"{r['span']:5.0f} {fnum(r['mean'], 9)} {fnum(r['min'], 9)} {fnum(r['max'], 9)} "
              f"{fnum(r['range'], 9)} {fnum(r['rangeRel'], 8, 3)} "
              f"{fnum(r['slopePerCss'], 10, 6)} {fnum(r['backdropSdAlongSide'], 8)} "
              f"{fnum(r['corrWithBackdrop'], 7, 3)}")
        w()
        w("=" * 108)
        w("TABLE 2 — the discriminator. Grading size against span, on the FLAT backdrops only")
        w("(`dark-solid`, `light-solid`), where a lens has no gradient to refract, so any grading")
        w("is the surface's own. Native side. Each row is the median over that cell's four sides.")
        w("=" * 108)
        w(f"{'profile':9} {'component':17} {'backdrop':13} {'span':>5} {'mean':>9} {'range':>9} "
          f"{'r/mean':>8} {'|slope|':>10}")
        flat = [r for r in rows if r["src"] == "native" and r["backdrop"] in
                ("dark-solid", "light-solid", "mid-dark-solid")]
        by = {}
        for r in flat:
            by.setdefault((r["profileKey"], r["component"], r["backdrop"]), []).append(r)
        for k in sorted(by, key=lambda k: (k[0], ORDER.index(k[1]), k[2])):
            g = by[k]
            w(f"{k[0]:9} {k[1]:17} {k[2]:13} {g[0]['span']:5.0f} "
              f"{fnum(np.median([x['mean'] for x in g]), 9)} "
              f"{fnum(np.median([x['range'] for x in g]), 9)} "
              f"{fnum(np.median([x['rangeRel'] for x in g]), 8, 3)} "
              f"{fnum(np.median([abs(x['slopePerCss']) for x in g]), 10, 6)}")
        w()
        w("=" * 108)
        w("TABLE 3 — the same on the STRUCTURED backdrops (`checkerboard`), where the lens has a")
        w("gradient to refract. If the grading is the lens, `corr` is large here and the grading")
        w("collapses in Table 2; if it is a thickness term, Table 2 grades with span and `corr` is")
        w("incidental.")
        w("=" * 108)
        w(f"{'profile':9} {'component':17} {'span':>5} {'mean':>9} {'range':>9} {'r/mean':>8} "
          f"{'|corr| med':>11}")
        ck = [r for r in rows if r["src"] == "native" and r["backdrop"] == "checkerboard"]
        by = {}
        for r in ck:
            by.setdefault((r["profileKey"], r["component"]), []).append(r)
        for k in sorted(by, key=lambda k: (k[0], ORDER.index(k[1]))):
            g = by[k]
            cs = [abs(x["corrWithBackdrop"]) for x in g if np.isfinite(x["corrWithBackdrop"])]
            w(f"{k[0]:9} {k[1]:17} {g[0]['span']:5.0f} "
              f"{fnum(np.median([x['mean'] for x in g]), 9)} "
              f"{fnum(np.median([x['range'] for x in g]), 9)} "
              f"{fnum(np.median([x['rangeRel'] for x in g]), 8, 3)} "
              f"{fnum(np.median(cs) if cs else None, 11, 3)}")
        w()
        w("=" * 108)
        w("TABLE 4 — vitrea against the reference on the same sides. vitrea's lit-edge factor is")
        w("`pow(|dot(n, axis)| * sqrt(2), p)`, exactly 1 on every straight side, so vitrea's rim is")
        w("constant along a straight side BY CONSTRUCTION and this table's `range` on the web rows")
        w("is the reader's own floor plus whatever the backdrop puts there.")
        w("=" * 108)
        w(f"{'profile':9} {'scene':40} {'side':6} {'nat mean':>9} {'nat range':>10} "
          f"{'gpu mean':>9} {'gpu range':>10} {'css mean':>9} {'css range':>10}")
        by = {}
        for r in rows:
            by.setdefault((r["profileKey"], r["scene"], r["sub"], r["side"]), {})[r["src"]] = r
        for k in sorted(by, key=lambda k: (k[1], k[0], k[3])):
            d = by[k]
            if "native" not in d or ("webgpu" not in d and "css" not in d):
                continue
            n, g, c = d["native"], d.get("webgpu"), d.get("css")
            w(f"{k[0]:9} {k[1][:40]:40} {k[3]:6} {fnum(n['mean'], 9)} {fnum(n['range'], 10)} "
              f"{fnum(g['mean'] if g else None, 9)} {fnum(g['range'] if g else None, 10)} "
              f"{fnum(c['mean'] if c else None, 9)} {fnum(c['range'] if c else None, 10)}")
    print(f"-> {path}", file=sys.stderr)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
