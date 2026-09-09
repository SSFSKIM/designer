"""W25 G0 deliverables 2 — the width and the level on every thick cell, reference and vitrea.

WHAT THIS READS, all read-only:
  - the reference fixtures `apps/reference-apple/fixtures/<profile>/<scene>.png`;
  - the canonical web captures `packages/calibration/web-captures/<profile>/<scene>/
    <scene>__{webgpu,css}.png` (the 0.13.0 bed);
  - the backdrop rasters `apps/reference-apple/fixtures/backgrounds/<bg>@{1,2}x.png`.
Nothing under `fixtures/`, `scenes.json`, `results/matrix.json` or `web-captures/` is written.

THE CELLS. Every thick component of the bed — `rrect-md` (span 96), `rrect-ml` (128), `rrect-lg`
(160), `toolbar-group` (three 44 px members) and `glass-over-glass` (the nested base, span 130,
read on the W22 stack geometry: the base box eroded 6 CSS px with the overlay's box dilated 6 px cut
out of it) — on every backdrop that carries it, in every profile that carries it, at both scales.
`capsule-button` (44) and `rrect-sm` (32) ride along as the thin controls.

THE READERS. `w25lib`'s three, each applied only where its backdrop can answer, and each carrying
the bound `validate.txt` measured for it:
  A the dot PSF        — `impulse` only.        Identifies to 16 device px at both scales.
  B the edge spread    — `checkerboard`, `hc-text`. Identifies to about an eighth of the backdrop's
                         step pitch: 2 device px at 1x and 4 at 2x on the 16 CSS px checkerboard.
  C the sigma match    — any structured backdrop. Identifies to about a quarter of the pitch on the
                         checkerboard (4 device px at 1x, 8 at 2x) and to 16 on the impulse.
A row past its reader's validated bound is printed with a `>bound` flag and is a LOWER BOUND, not a
reading. Where two readers agree inside their residuals the width is a reading; where they do not,
the disagreement is tabled as the finding.

UNITS. Every sigma is DEVICE px with the CSS-px value beside it (sigma / scale). Levels are linear
Rec.709 luma with the web-minus-native difference also given in 8-bit display codes.

Usage: widths.py [--out-prefix .]     (writes widths.txt and levels.txt beside itself)
"""

import argparse
import json
import os
import sys

import numpy as np

import w25lib as L

THICK = ["rrect-md", "rrect-ml", "rrect-lg", "toolbar-group", "glass-over-glass"]
THIN = ["capsule-button", "rrect-sm"]
SPAN = {"capsule-button": 44.0, "rrect-sm": 32.0, "rrect-md": 96.0, "rrect-ml": 128.0,
        "rrect-lg": 160.0, "toolbar-group": 44.0, "glass-over-glass": 130.0}
# The validated identification bound per reader and backdrop, in DEVICE px, from validate.txt.
BOUND = {
    ("A", "impulse"): {1.0: 16.0, 2.0: 16.0},
    ("B", "checkerboard"): {1.0: 2.0, 2.0: 4.0},
    ("B", "hc-text"): {1.0: 2.0, 2.0: 4.0},
    ("C", "checkerboard"): {1.0: 4.0, 2.0: 8.0},
    ("C", "hc-text"): {1.0: 4.0, 2.0: 8.0},
    ("C", "photo"): {1.0: 4.0, 2.0: 8.0},
    ("C", "impulse"): {1.0: 16.0, 2.0: 16.0},
}
STRUCTURED = {"checkerboard", "photo", "impulse", "hc-text"}
FLAT = {"light-solid", "dark-solid", "mid-dark-solid"}


def scenes_on_disk(profile_dir):
    if not os.path.isdir(profile_dir):
        return []
    return sorted(f[:-4] for f in os.listdir(profile_dir) if f.endswith(".png"))


def parse_scene(sid):
    parts = sid.split("__")
    if len(parts) < 3:
        return None
    return parts[0], parts[1], "__".join(parts[2:])


def read_widths(lum, bg, cell, scale, backdrop, ref_key=None):
    """The three readers on one image, each only where its backdrop can answer."""
    out = {}
    mask = cell.body_mask(scale, lum.shape, 6.0)
    if backdrop == "impulse":
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
    if backdrop in ("checkerboard", "hc-text"):
        b = L.read_edge_spread(lum, bg, mask, scale, sigma_ceiling_dev=64.0)
        if b["n"]:
            out["B"] = {"sigmaDev": b["sigmaDev"], "residual": b["residual"], "n": b["n"],
                        "iqr": b.get("sigmaIqr", float("nan")),
                        "halfWindowDev": b.get("halfWindowDev", float("nan"))}
    if backdrop in STRUCTURED:
        c = L.sigma_match(lum, bg, mask, top=64.0, ref_key=ref_key)
        out["C"] = {"sigmaDev": c["sigmaDev"], "residual": c["rmsRel"], "gain": c.get("gain"),
                    "sd": c["sd"], "atCeiling": c["atCeiling"], "reason": c["reason"]}
    return out


def flag(reader, backdrop, scale, sigma):
    b = BOUND.get((reader, backdrop), {}).get(scale)
    if b is None or not np.isfinite(sigma):
        return ""
    return ">bound" if sigma > b else ""


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-prefix", default=".")
    args = ap.parse_args(argv)

    comps = L.load_components()
    cells = {n: L.Cell(n, comps) for n in THICK + THIN}

    rows = []
    levels = []
    # Ordered by (scale, backdrop) rather than by profile: reader C's blurred-reference cache holds
    # one (backdrop, scale) at a time, so walking the bed in that order turns 145 blurs per source
    # into 145 blurs per backdrop and scale.
    tasks = []
    for key, (profile, scale, scheme) in L.PROFILES.items():
        pdir = os.path.join(L.FIXTURES, profile)
        for sid in scenes_on_disk(pdir):
            p = parse_scene(sid)
            if p is None:
                continue
            backdrop, component, state = p
            if component not in cells or state != "rest":
                continue
            tasks.append((scale, backdrop, key, profile, scheme, sid, component))
    for (scale, backdrop, key, profile, scheme, sid, component) in sorted(
            tasks, key=lambda t: (t[0], t[1], t[2], t[5])):
        cell = cells[component]
        shape = (int(200 * scale), int(320 * scale))
        bg = L.background_for(backdrop, scale, shape)
        sources = [("native", L.native_path(profile, sid))]
        for tier in ("webgpu", "css"):
            wp = L.web_path(profile, sid, tier)
            if os.path.exists(wp):
                sources.append((tier, wp))
        for tag, path in sources:
            if not os.path.exists(path):
                continue
            lum = L.luma_of(path)
            if lum.shape != shape:
                continue
            mask = cell.body_mask(scale, lum.shape, 6.0)
            levels.append({
                "profileKey": key, "profile": profile, "scale": scale, "scheme": scheme,
                "scene": sid, "backdrop": backdrop, "component": component, "src": tag,
                "span": SPAN[component],
                "body": float(lum[mask].mean()), "sd": float(lum[mask].std()),
                "n": int(mask.sum()),
            })
            if backdrop in FLAT:
                continue
            w = read_widths(lum, bg, cell, scale, backdrop, ref_key=(backdrop, scale))
            for reader, v in w.items():
                rows.append({
                    "profileKey": key, "scale": scale, "scheme": scheme, "scene": sid,
                    "backdrop": backdrop, "component": component, "span": SPAN[component],
                    "src": tag, "reader": reader, **v,
                    "sigmaCss": v["sigmaDev"] / scale if np.isfinite(v["sigmaDev"]) else
                                float("nan"),
                    "flag": flag(reader, backdrop, scale, v["sigmaDev"]),
                })
                print(f"  {key:9} {sid:44} {tag:7} {reader} "
                      f"sigma {v['sigmaDev']:7.2f} dev  resid {v['residual']:8.4f}",
                      file=sys.stderr)

    json.dump({"widths": rows, "levels": levels},
              open(os.path.join(args.out_prefix, "widths.json"), "w"), indent=1)
    write_widths(rows, os.path.join(args.out_prefix, "widths.txt"))
    write_levels(levels, os.path.join(args.out_prefix, "levels.txt"))
    return 0


def fnum(v, w=8, p=2):
    return f"{'—':>{w}}" if v is None or not np.isfinite(v) else f"{v:{w}.{p}f}"


def write_widths(rows, path):
    with open(path, "w") as fh:
        def w(s=""):
            fh.write(s + "\n")

        w(__doc__.strip())
        w()
        w("=" * 100)
        w("TABLE 1 — every width read, by cell. Instrument: w25lib readers A / B / C.")
        w("Units: sigma in DEVICE px (sigma css = sigma / scale). `resid` is each reader's own")
        w("residual — A: fit RMS as a fraction of the dot's peak excess; B: fit RMS as a fraction")
        w("of the profile's own step height (`report.ts:391-397`: large means not identifiable);")
        w("C: match RMS as a fraction of the region's own standard deviation.")
        w("`>bound` marks a value past the reader's validated identification bound (validate.txt):")
        w("a LOWER BOUND, not a reading.")
        w("=" * 100)
        hdr = (f"{'profile':9} {'scene':42} {'src':7} {'R':1} {'span':>5} {'sigma dev':>10} "
               f"{'sigma css':>10} {'resid':>9} {'extra':>26} flag")
        w(hdr)
        for r in sorted(rows, key=lambda r: (r["component"], r["backdrop"], r["profileKey"],
                                             r["src"], r["reader"])):
            extra = ""
            if r["reader"] == "A":
                extra = (f"sharp {r['sharpDev']:.2f} heavy {r['heavyDev']:.2f} "
                         f"hs {r['heavyShare']:.2f}")
            elif r["reader"] == "B":
                extra = f"n {r['n']} iqr {r['iqr']:.2f}"
            elif r["reader"] == "C":
                extra = f"gain {r['gain']:.3f} sd {r['sd']:.4f}" if r.get("gain") else r["reason"][:26]
            w(f"{r['profileKey']:9} {r['scene']:42} {r['src']:7} {r['reader']:1} "
              f"{r['span']:5.0f} {fnum(r['sigmaDev'], 10)} {fnum(r['sigmaCss'], 10)} "
              f"{fnum(r['residual'], 9, 4)} {extra:>26} {r['flag']}")
        w()
        w("=" * 100)
        w("TABLE 2 — reference against vitrea, per cell and reader. `ratio` is web / native.")
        w("=" * 100)
        w(f"{'profile':9} {'scene':42} {'R':1} {'native dev':>11} {'gpu dev':>9} {'css dev':>9} "
          f"{'gpu/nat':>8} {'css/nat':>8} {'nat resid':>10} {'gpu resid':>10}")
        by = {}
        for r in rows:
            by.setdefault((r["profileKey"], r["scene"], r["reader"]), {})[r["src"]] = r
        for k in sorted(by, key=lambda k: (k[1], k[0], k[2])):
            d = by[k]
            nat, gpu, css = d.get("native"), d.get("webgpu"), d.get("css")
            if nat is None:
                continue
            gn = gpu["sigmaDev"] / nat["sigmaDev"] if gpu and nat["sigmaDev"] else float("nan")
            cn = css["sigmaDev"] / nat["sigmaDev"] if css and nat["sigmaDev"] else float("nan")
            w(f"{k[0]:9} {k[1]:42} {k[2]:1} {fnum(nat['sigmaDev'], 11)} "
              f"{fnum(gpu['sigmaDev'] if gpu else None, 9)} "
              f"{fnum(css['sigmaDev'] if css else None, 9)} {fnum(gn, 8)} {fnum(cn, 8)} "
              f"{fnum(nat['residual'], 10, 4)} "
              f"{fnum(gpu['residual'] if gpu else None, 10, 4)}")
        w()
        w("=" * 100)
        w("TABLE 3 — where two readers meet, and where they do not.")
        w("A width is a READING when two readers on the same image are within 15 % of each other")
        w("and both are inside their validated bounds; otherwise the row is a DISAGREEMENT and the")
        w("numbers stand beside each other.")
        w("=" * 100)
        w(f"{'profile':9} {'scene':42} {'src':7} {'pair':5} {'a dev':>8} {'b dev':>8} "
          f"{'spread %':>9}  verdict")
        by2 = {}
        for r in rows:
            by2.setdefault((r["profileKey"], r["scene"], r["src"]), {})[r["reader"]] = r
        for k in sorted(by2, key=lambda k: (k[1], k[0], k[2])):
            d = by2[k]
            for a, b in (("A", "C"), ("B", "C"), ("A", "B")):
                if a not in d or b not in d:
                    continue
                sa, sb = d[a]["sigmaDev"], d[b]["sigmaDev"]
                if not (np.isfinite(sa) and np.isfinite(sb)):
                    verdict = "one reader returned no width"
                    spread = float("nan")
                else:
                    spread = abs(sa - sb) / max(min(sa, sb), 1e-9) * 100.0
                    inside = not d[a]["flag"] and not d[b]["flag"]
                    verdict = ("READING" if spread <= 15.0 and inside else
                               "DISAGREEMENT" + ("" if inside else " (one past its bound)"))
                w(f"{k[0]:9} {k[1]:42} {k[2]:7} {a}+{b:3} {fnum(sa, 8)} {fnum(sb, 8)} "
                  f"{fnum(spread, 9, 1)}  {verdict}")
    print(f"-> {path}", file=sys.stderr)


def write_levels(levels, path):
    with open(path, "w") as fh:
        def w(s=""):
            fh.write(s + "\n")

        w("W25 G0 deliverable 2 (levels) — the body level on every thick cell, reference vs vitrea.")
        w()
        w("Instrument: the declared shape eroded 6 CSS px (the stack's base on W22's geometry),")
        w("mean linear Rec.709 luma over that mask. `dcode` is the web-minus-native difference")
        w("expressed in 8-bit display codes at that level (the sRGB OETF applied to each side),")
        w("which is the unit W23 and W24 recorded the thick body's miss in.")
        w("Sources: the reference fixtures and the canonical 0.13.0 web captures, read-only.")
        w()
        w(f"{'profile':9} {'scene':42} {'span':>5} {'native':>9} {'gpu':>9} {'css':>9} "
          f"{'gpu-nat':>9} {'dcode gpu':>10} {'css-nat':>9} {'dcode css':>10} "
          f"{'nat sd':>8} {'gpu sd':>8}")
        by = {}
        for r in levels:
            by.setdefault((r["profileKey"], r["scene"]), {})[r["src"]] = r
        for k in sorted(by, key=lambda k: (k[1], k[0])):
            d = by[k]
            nat = d.get("native")
            if nat is None:
                continue
            gpu, css = d.get("webgpu"), d.get("css")
            gd = gpu["body"] - nat["body"] if gpu else None
            cd = css["body"] - nat["body"] if css else None
            w(f"{k[0]:9} {k[1]:42} {nat['span']:5.0f} {nat['body']:9.5f} "
              f"{fnum(gpu['body'] if gpu else None, 9, 5)} {fnum(css['body'] if css else None, 9, 5)} "
              f"{fnum(gd, 9, 5)} "
              f"{fnum(L.codes(gpu['body'], nat['body']) if gpu else None, 10, 2)} "
              f"{fnum(cd, 9, 5)} "
              f"{fnum(L.codes(css['body'], nat['body']) if css else None, 10, 2)} "
              f"{nat['sd']:8.4f} {fnum(gpu['sd'] if gpu else None, 8, 4)}")
    print(f"-> {path}", file=sys.stderr)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
