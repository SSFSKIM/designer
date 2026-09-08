"""W24 G0 (c) — the lit edge's law fitted on the REFERENCE's own angular bins.

The form the wave chartered, with the axis fitted rather than assumed:

    rim(theta) = A_cell * ( a + (1 - a) * |cos(theta - phi)|^p )

`A_cell` is the cell's own amplitude and is the W23 law's business, so it is solved per cell and
never carried; the three constants this gate is fitting are the AXIS `phi`, the EXPONENT `p` and the
AMBIENT FRACTION `a`, and they are shared across every row of a scheme. Two rival forms are fitted
on exactly the same rows and reported beside it:

- the ONE-SIDED Lambert `max(cos(theta - phi), 0)^p`, which is the shape W22's `spec` term drew and
  fitted to 0 — if the reference's top-left and bottom-right corners are equally bright, this form
  cannot reach one of them and must lose;
- the FLAT rim `a = 1`, which is what vitrea draws today and is the null hypothesis the wave exists
  to reject.

The basis is binned exactly as the read is: `f_k` is the mean of the directional factor over the
BOUNDARY SAMPLES that fall in bin k, not the factor at the bin's centre angle. `|cos|` has a kink at
its zero, so over the 22.5 deg of the dimmest bin its mean stands well above its centre value, and a
fit against centre values would push `a` up by a third to absorb the difference.

Rows: the untinted cells over a SOLID backdrop (`dark-solid`, `mid-dark-solid`, `light-solid`) of
both canonical beds at both scales and of both probe grids. Over a structured backdrop the rim read
is the backdrop's structure (the reads show ratios of 10 to 240 with the brightest bin wherever the
checkerboard's bright square happens to meet the contour), so those cells cannot separate a
directional law and are reported as a CHECK, never fitted. Bins whose peak pixel clips to white, and
bins whose peak ran to the end of the search window, are excluded per bin with their counts printed.

Usage:  fit-law.py --reads <dir> [--scheme light|dark|both] [--json <out.json>]
"""

import argparse
import importlib.util
import json
import math
import os

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location("read_angular", os.path.join(HERE, "read-angular.py"))
RA = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(RA)

SOLID = ("dark-solid", "mid-dark-solid", "light-solid")
NBINS = RA.NBINS
COMPASS = RA.COMPASS


def basis(scenes_path, scene_id, scale, phis, ps):
    """`f_k(phi, p)` for one cell: the bin-mean of |cos(theta - phi)|^p over its boundary samples."""
    spec = json.load(open(scenes_path))
    scene = next(s for s in spec["scenes"] if s["id"] == scene_id)
    geom = RA.component_geometry(spec["components"], scene["component"])
    box = RA.declared_box(spec["canvas"], geom, scale)
    pts = RA.boundary_points(box, 0.25, 720)
    theta = np.asarray([RA.normal_angle(nx, ny) for (_x, _y, nx, ny, _s) in pts])
    b = RA.bin_of(theta)
    # (phi, p, bin)
    c = np.abs(np.cos(np.radians(theta[None, :] - np.asarray(phis)[:, None])))
    out = np.zeros((len(phis), len(ps), NBINS))
    one = np.zeros((len(phis), len(ps), NBINS))
    csigned = np.cos(np.radians(theta[None, :] - np.asarray(phis)[:, None]))
    for j, p in enumerate(ps):
        cp = c ** p
        op = np.maximum(csigned, 0.0) ** p
        for k in range(NBINS):
            m = b == k
            out[:, j, k] = cp[:, m].mean(axis=1)
            one[:, j, k] = op[:, m].mean(axis=1)
    return out, one


# The cells the reference COLLAPSES — its material has taken the backdrop's tone and draws nothing
# but the collapsed rim. W23 G0 §1 identified them by the body sitting within one code of the
# backdrop, and their light and dark fixtures are byte-identical. They are read here to answer
# whether the collapsed rim carries the same directional profile as the appearance's own, and they
# are reported apart rather than mixed into the fit's rows.
COLLAPSED = ("dark-solid__capsule-button__rest", "impulse__capsule-button__rest",
             "dark-solid__rrect-sm__rest", "dark-solid__rrect-lg__rest")


def collect(reads_dir, scenes_of, want_schemes, clip_bound=0.02, trunc_bound=0.05,
            outside_bound=0.2):
    """Every fittable reference row: the bins, the mask, the scheme, the scale, the cell's identity.

    A fixture is taken ONCE. Both standard profiles declare the collapsed cells and their fixtures
    are byte-identical (W23 G0 §3), so keying the rows on the fixture's own digest is what keeps one
    capture from weighing twice in a fit that is already only 27 cells wide.
    """
    rows = []
    seen = {}
    for fname in sorted(os.listdir(reads_dir)):
        # `reads/` also holds W23's contour reads of the landed bed, which the straight-span
        # check needs and this fit has no use for.
        if not fname.endswith(".json") or fname.startswith("contour-"):
            continue
        d = json.load(open(os.path.join(reads_dir, fname)))
        if d.get("tier") not in (None, "webgpu"):
            continue                       # the CSS tier is context, never fitting ground
        profile = d["profile"]
        scheme = "dark" if "-dark-" in profile else "light"
        if scheme not in want_schemes:
            continue
        bed = "probe" if "probe" in fname else "canonical"
        for r in d["rows"]:
            if r.get("tint"):
                continue
            if r["background"] not in SOLID:
                continue
            v = r["native"]
            bins = np.asarray([np.nan if b is None else b for b in v["bins"]])
            clip = np.asarray([0.0 if c is None else c for c in v["clipFraction"]])
            trunc = np.asarray([0.0 if t is None else t for t in v["truncatedFraction"]])
            out = np.asarray([0.0 if o is None else o for o in v["outsideFraction"]])
            mask = (np.isfinite(bins) & (clip <= clip_bound) & (trunc <= trunc_bound)
                    & (out <= outside_bound))
            if mask.sum() < 8:
                continue
            # A row whose rim rides into the display's own ceiling cannot carry a SHAPE: its bins
            # are compressed toward each other by the encoding, not by the material. The light
            # scheme's `light-solid` rows sit at a body of 0.93 with a rim of 0.06, within a
            # hundredth of white, and they read a ratio of 1.15 where the same material over a dark
            # backdrop reads 7.7. They are excluded from the fit and reported in the read.
            if v["body"] + np.nanmax(bins) > 0.97:
                continue
            if v["sha256"] in seen:
                seen[v["sha256"]].append(f"{bed}/{profile}")
                continue
            seen[v["sha256"]] = [f"{bed}/{profile}"]
            rows.append({
                "key": f"{bed}/{profile}/{r['scene']}",
                "scenes": scenes_of[fname],
                "scene": r["scene"], "scheme": scheme, "bed": bed, "profile": profile,
                "scale": v["scale"], "background": r["background"], "component": r["component"],
                "bins": bins, "mask": mask, "web": r.get("web"),
                "clipped": int((clip > clip_bound).sum()),
                "truncated": int((trunc > trunc_bound).sum()),
                "outside": int((out > outside_bound).sum()),
                "collapsed": r["scene"] in COLLAPSED,
                "sha256": v["sha256"],
            })
    for r in rows:
        r["alsoIn"] = [k for k in seen[r["sha256"]] if not r["key"].startswith(k)]
    return rows


def fit(rows, phis, ps, ambients, symmetric=True, flat=False):
    """The shared (phi, p, a) that minimises the summed squared residual of the NORMALISED bins.

    Normalised by each cell's own brightest bin, so a light row whose rim is 0.28 and a dark row
    whose rim is 0.04 weigh the same: the constants are a SHAPE, and a fit in absolute luminance
    would be a fit to the light bed alone.
    """
    total = np.zeros((len(phis), len(ps), len(ambients)))
    per_cell = {}
    a = np.asarray(ambients)[None, None, :]
    for r in rows:
        y = r["bins"][r["mask"]] / np.nanmax(r["bins"])
        # `g = a + (1 - a) f` is never materialised over the whole (phi, p, a, bin) grid: the two
        # sums the solve needs are polynomials in `a` with coefficients that depend only on (phi, p).
        if flat:
            s1 = np.full(total.shape, y.sum())
            s2 = np.full(total.shape, float(y.size))
        else:
            sym, one = r["_basis"]
            f = (sym if symmetric else one)[:, :, r["mask"]]
            y0, n = float(y.sum()), float(y.size)
            y1 = (f * y).sum(axis=-1)[:, :, None]
            f1 = f.sum(axis=-1)[:, :, None]
            f2 = (f * f).sum(axis=-1)[:, :, None]
            s1 = a * y0 + (1.0 - a) * y1
            s2 = a * a * n + 2.0 * a * (1.0 - a) * f1 + (1.0 - a) ** 2 * f2
        resid = (y * y).sum() - s1 * s1 / np.maximum(s2, 1e-12)
        per_cell[r["key"]] = resid
        total = total + resid
    idx = np.unravel_index(np.argmin(total), total.shape)
    n = sum(int(r["mask"].sum()) for r in rows)
    return {
        "phi": float(phis[idx[0]]) if not flat else float("nan"),
        "p": float(ps[idx[1]]) if not flat else float("nan"),
        "a": float(ambients[idx[2]]) if not flat else 1.0,
        "rms": float(math.sqrt(total[idx] / n)),
        "n": n,
        "perCell": {k: float(math.sqrt(v[idx] / max(1, 1))) for k, v in per_cell.items()},
        "grid": total,
        "index": idx,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--reads", default=os.path.join(HERE, "reads"))
    ap.add_argument("--json", default=None)
    args = ap.parse_args()

    worktree = os.path.abspath(os.path.join(HERE, "..", "..", "..", "..", ".."))
    scenes_of = {}
    for fname in os.listdir(args.reads):
        if fname.startswith("probe9"):
            scenes_of[fname] = os.path.join(worktree, "apps/reference-apple/scenes-w9-probe.json")
        elif fname.startswith("probe21"):
            scenes_of[fname] = os.path.join(worktree, "apps/reference-apple/scenes-w21-probe.json")
        else:
            scenes_of[fname] = os.path.join(worktree, "apps/reference-apple/scenes.json")

    phis = np.arange(0.0, 180.0, 0.5)
    ps = np.round(np.arange(0.30, 3.001, 0.05), 3)
    ambients = np.round(np.arange(0.0, 0.601, 0.005), 4)
    phis_one = np.arange(0.0, 360.0, 1.0)

    rows = collect(args.reads, scenes_of, {"light", "dark"})
    print(f"== the rows: {len(rows)} untinted solid reference cells "
          f"({sum(1 for r in rows if r['scheme'] == 'light')} light, "
          f"{sum(1 for r in rows if r['scheme'] == 'dark')} dark; "
          f"{sum(1 for r in rows if r['bed'] == 'canonical')} canonical, "
          f"{sum(1 for r in rows if r['bed'] == 'probe')} probe)")
    print(f"{'cell':64s} {'scale':>5s} {'peak':>8s} {'floor':>8s} {'ratio':>7s} {'bright':>6s} "
          f"{'clip':>4s} {'trunc':>5s} {'outsd':>5s} {'coll':>4s}")
    for r in sorted(rows, key=lambda r: r["key"]):
        peak = float(np.nanmax(r["bins"][r["mask"]]))
        floor = float(np.nanmin(r["bins"][r["mask"]]))
        bright = COMPASS[int(np.arange(NBINS)[r["mask"]][np.argmax(r["bins"][r["mask"]])])]
        print(f"{r['key']:64s} {r['scale']:5.1f} {peak:8.4f} {floor:8.4f} "
              f"{peak / max(floor, 1e-6):7.2f} {bright:>6s} {r['clipped']:4d} {r['truncated']:5d} "
              f"{r['outside']:5d} {'yes' if r['collapsed'] else '-':>4s}"
              + (f"   (= {', '.join(r['alsoIn'])})" if r["alsoIn"] else ""))

    for r in rows:
        r["_basis"] = basis(r["scenes"], r["scene"], r["scale"], phis, ps)
        r["_basis_one"] = basis(r["scenes"], r["scene"], r["scale"], phis_one, ps)

    print("\n== the forms, fitted on the same rows (RMS of the normalised bin residual)")
    print(f"{'rows':22s} {'form':28s} {'phi':>7s} {'p':>6s} {'a':>6s} {'rms':>8s} {'n':>5s}")
    results = {}
    groups = [("both schemes", rows),
              ("light", [r for r in rows if r["scheme"] == "light"]),
              ("dark", [r for r in rows if r["scheme"] == "dark"]),
              ("uncollapsed", [r for r in rows if not r["collapsed"]]),
              ("collapsed", [r for r in rows if r["collapsed"]]),
              ("light 1x", [r for r in rows if r["scheme"] == "light" and r["scale"] == 1.0]),
              ("light 2x", [r for r in rows if r["scheme"] == "light" and r["scale"] == 2.0]),
              ("dark 1x", [r for r in rows if r["scheme"] == "dark" and r["scale"] == 1.0]),
              ("dark 2x", [r for r in rows if r["scheme"] == "dark" and r["scale"] == 2.0]),
              ("canonical", [r for r in rows if r["bed"] == "canonical"]),
              ("probe", [r for r in rows if r["bed"] == "probe"])]
    for name, group in groups:
        if not group:
            continue
        sym = fit(group, phis, ps, ambients, symmetric=True)
        results[name] = {k: sym[k] for k in ("phi", "p", "a", "rms", "n")}
        print(f"{name:22s} {'symmetric |cos(t-phi)|^p':28s} {sym['phi']:7.1f} {sym['p']:6.2f} "
              f"{sym['a']:6.3f} {sym['rms']:8.5f} {sym['n']:5d}")
        for r in group:
            r["_basis"], r["_keep"] = r["_basis_one"], r["_basis"]
        one = fit(group, phis_one, ps, ambients, symmetric=False)
        for r in group:
            r["_basis"] = r["_keep"]
        print(f"{'':22s} {'one-sided max(cos,0)^p':28s} {one['phi']:7.1f} {one['p']:6.2f} "
              f"{one['a']:6.3f} {one['rms']:8.5f} {one['n']:5d}")
        results[name]["oneSided"] = {k: one[k] for k in ("phi", "p", "a", "rms")}
        flatfit = fit(group, phis, ps, ambients, flat=True)
        print(f"{'':22s} {'flat (what vitrea draws)':28s} {'-':>7s} {'-':>6s} {'-':>6s} "
              f"{flatfit['rms']:8.5f} {flatfit['n']:5d}")
        results[name]["flat"] = {"rms": flatfit["rms"]}

    print("\n== per cell, fitted alone (S5: do the rows agree on the constants?)")
    print(f"{'cell':64s} {'phi':>7s} {'p':>6s} {'a':>6s} {'rms':>8s}")
    per = []
    for r in sorted(rows, key=lambda r: r["key"]):
        f1 = fit([r], phis, ps, ambients, symmetric=True)
        per.append((r, f1))
        print(f"{r['key']:64s} {f1['phi']:7.1f} {f1['p']:6.2f} {f1['a']:6.3f} {f1['rms']:8.5f}")
    for scheme in ("light", "dark"):
        sub = [(r, f1) for r, f1 in per if r["scheme"] == scheme]
        if not sub:
            continue
        ph = np.asarray([f1["phi"] for _r, f1 in sub])
        pp = np.asarray([f1["p"] for _r, f1 in sub])
        aa = np.asarray([f1["a"] for _r, f1 in sub])
        print(f"  {scheme}: phi {ph.mean():.1f} +/- {ph.std():.1f} (min {ph.min():.1f} max "
              f"{ph.max():.1f}); p {pp.mean():.2f} +/- {pp.std():.2f}; "
              f"a {aa.mean():.3f} +/- {aa.std():.3f}")
        results[f"{scheme} per-cell"] = {
            "phi": [float(ph.mean()), float(ph.std())],
            "p": [float(pp.mean()), float(pp.std())],
            "a": [float(aa.mean()), float(aa.std())]}

    print("\n== the prediction, bin by bin, at the constants each scheme's rows chose")
    print("   `want` is the reference's bin; `law` is A_cell x (a + (1 - a) |cos(theta - phi)|^p)")
    print("   with A_cell the least-squares amplitude for that cell alone.")
    for scheme in ("light", "dark"):
        group = [r for r in rows if r["scheme"] == scheme]
        if not group:
            continue
        f = results[scheme]
        phi, p, a = f["phi"], f["p"], f["a"]
        pi = int(np.argmin(np.abs(phis - phi)))
        pj = int(np.argmin(np.abs(ps - p)))
        print(f"\n-- {scheme}: phi {phi}, p {p}, a {a}")
        print(f"{'cell':58s} {'src':5s} " + " ".join(f"{c:>7s}" for c in COMPASS)
              + f" {'maxErr':>8s}")
        worst_all = 0.0
        for r in sorted(group, key=lambda r: r["key"]):
            sym, _one = r["_basis"]
            g = a + (1.0 - a) * sym[pi, pj, :]
            y = r["bins"]
            m = r["mask"]
            amp = float((g[m] * y[m]).sum() / (g[m] * g[m]).sum())
            law = amp * g
            err = np.where(m, np.abs(law - y), np.nan)
            worst = float(np.nanmax(err))
            worst_all = max(worst_all, worst)
            print(f"{r['key'][-58:]:58s} {'want':5s} "
                  + " ".join(f"{v:7.4f}" for v in y) + f" {'':8s}")
            print(f"{'':58s} {'law':5s} "
                  + " ".join(("  excl " if not mm else f"{v:7.4f}") for v, mm in zip(law, m))
                  + f" {worst:8.4f}")
        print(f"   worst absolute bin error over the scheme's rows: {worst_all:.4f}")

    if args.json:
        with open(args.json, "w") as fh:
            json.dump(results, fh, indent=2)
        print(f"\n-> {args.json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
