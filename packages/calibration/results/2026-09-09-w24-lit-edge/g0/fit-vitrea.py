"""W24 G0 (c) — the lit edge fitted on VITREA's own pixels, and the straight spans checked.

Three questions, in order, all of them on captures the real pipeline produced at a named constant:

1. **Does the shader draw the factor the arithmetic says it draws?** The rendered bins at exponent
   1 and 2, divided by the landed bed's own bins at exponent 0, must equal the SAME binned mean of
   `(√2 · |cos(θ − 135°)|)^p` that `fit-law.py` fits the reference with. If they do, the ladder has
   two rendered points and the exponent can be interpolated in closed form between them instead of
   being swept — which is what makes a short ladder enough for a non-linear constant.

2. **What exponent do vitrea's own rows want?** Per row, the exponent minimising the summed square
   of (vitrea's bin − the reference's bin) over the CORNER AND ARC bins of the solid rows — the
   bins the straight-span readers of three waves could not see. Fitted on the calibration rows,
   checked on the validation rows and on the structured rows' arcs, and reported per row, because a
   constant whose rows do not agree is not carried (C9a §6.2, S5).

3. **Do the straight spans hold?** W23's own `read-contour.py`, unmodified, on every solid side of
   every ladder point against the landed bed. The wave's clause 4 and W23's clause 2 want them
   within 0.005, and the mechanism's `√2` normalisation says they should be within the capture's
   own noise at every exponent.

Usage: fit-vitrea.py [--json <out.json>]
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

WORKTREE = os.path.abspath(os.path.join(HERE, "..", "..", "..", "..", ".."))
SCENES = os.path.join(WORKTREE, "apps", "reference-apple", "scenes.json")
COMPASS = RA.COMPASS
NBINS = RA.NBINS
SOLID = ("dark-solid", "mid-dark-solid", "light-solid")
# The four bins whose normal is horizontal or vertical. The factor is 1 on them by construction, so
# they are the CONTROL: they must not move at any exponent, and they are excluded from the fit.
STRAIGHT = (0, 4, 8, 12)
ARCS = tuple(k for k in range(NBINS) if k not in STRAIGHT)
AXIS_DEG = 135.0

BEDS = [("light", "1x"), ("light", "2x"), ("dark", "1x"), ("dark", "2x")]


def factor(scene_id, scale, exponent):
    """The binned mean of `(√2 |cos(θ − 135°)|)^p` over this cell's own boundary samples."""
    spec = json.load(open(SCENES))
    scene = next(s for s in spec["scenes"] if s["id"] == scene_id)
    geom = RA.component_geometry(spec["components"], scene["component"])
    box = RA.declared_box(spec["canvas"], geom, scale)
    pts = RA.boundary_points(box, 0.25, 720)
    theta = np.asarray([RA.normal_angle(nx, ny) for (_x, _y, nx, ny, _s) in pts])
    value = np.maximum(np.abs(np.cos(np.radians(theta - AXIS_DEG))) * math.sqrt(2.0), 1e-6)
    value = value ** exponent
    b = RA.bin_of(theta)
    return np.asarray([value[b == k].mean() if (b == k).any() else np.nan for k in range(NBINS)])


def load(path):
    return json.load(open(path)) if os.path.exists(path) else None


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", default=None)
    args = ap.parse_args()

    landed = {}
    for scheme, scale in BEDS:
        key = f"apple-macos-26.5-{scale}-{scheme}-standard"
        landed[(scheme, scale)] = load(os.path.join(HERE, "reads", f"{key}__webgpu.json"))
    ladder = {}
    for point in ("lit1", "lit2"):
        for scheme, scale in BEDS:
            ladder[(point, scheme, scale)] = load(
                os.path.join(HERE, "ladder", f"{scheme}-{point}-{scale}.json"))

    print("== 1. the shader against the arithmetic")
    print("   For every solid untinted row: vitrea's RENDERED bin at the exponent against the")
    print("   landed bed's own bin times the binned mean of (sqrt2 |cos(theta - 135)|)^p, in")
    print("   absolute linear luminance. The identity is only expected where the rim is the whole")
    print("   of the near-contour excess: over `light-solid` the material's body sits at 0.93 and")
    print("   the rim runs into the encoding's ceiling, so the peak the reader returns is not the")
    print("   rim's own amplitude and those rows are printed but not summed into the bound.")
    print(f"{'row':52s} {'p':>4s} {'max |rendered - landed x factor|':>32s} {'straight moved':>15s}")
    worst_arith, worst_straight = 0.0, 0.0
    for point, exponent in (("lit1", 1.0), ("lit2", 2.0)):
        for scheme, scale in BEDS:
            d = ladder[(point, scheme, scale)]
            base = landed[(scheme, scale)]
            if d is None or base is None:
                continue
            base_rows = {r["scene"]: r for r in base["rows"]}
            for r in d["rows"]:
                if r["background"] not in SOLID or r.get("tint") or "web" not in r:
                    continue
                b0 = base_rows.get(r["scene"])
                if b0 is None or "web" not in b0:
                    continue
                y1 = np.asarray([np.nan if v is None else v for v in r["web"]["bins"]])
                y0 = np.asarray([np.nan if v is None else v for v in b0["web"]["bins"]])
                f = factor(r["scene"], r["web"]["scale"], exponent)
                err = float(np.nanmax(np.abs(y1 - y0 * f)))
                moved = float(np.nanmax(np.abs(y1[list(STRAIGHT)] - y0[list(STRAIGHT)])))
                compressed = r["web"]["body"] + float(np.nanmax(y0)) > 0.97
                if not compressed:
                    worst_arith = max(worst_arith, err)
                worst_straight = max(worst_straight, moved)
                print(f"{scheme}-{scale}/{r['scene']:<40s} {exponent:4.1f} {err:32.5f} "
                      f"{moved:15.5f}" + ("   at the ceiling — printed, not summed"
                                          if compressed else ""))
    print(f"   worst |rendered - landed x factor| over the unclipped rows and both points: "
          f"{worst_arith:.5f}")
    print(f"   worst movement on a straight bin: {worst_straight:.5f} of linear luminance")

    print("\n== 2. the exponent vitrea's own rows want, per row")
    print("   The bins are interpolated in closed form between the rendered points, which section 1")
    print("   licenses: bin(p) = bin(0) x factor(p). The objective is the summed square of")
    print("   (vitrea - reference) over the twelve ARC bins; the four straight bins are the control.")
    exponents = np.round(np.arange(0.0, 3.001, 0.05), 3)
    print(f"{'row':56s} {'set':11s} {'p*':>5s} {'arc err at 0':>12s} {'arc err at p*':>13s}")
    rows_out = []
    for scheme, scale in BEDS:
        base = landed[(scheme, scale)]
        if base is None:
            continue
        for r in base["rows"]:
            if r.get("tint") or "web" not in r:
                continue
            structured = r["background"] not in SOLID
            y0 = np.asarray([np.nan if v is None else v for v in r["web"]["bins"]])
            ref = np.asarray([np.nan if v is None else v for v in r["native"]["bins"]])
            clip = np.asarray([0.0 if v is None else v for v in r["native"]["clipFraction"]])
            out = np.asarray([0.0 if v is None else v for v in r["native"]["outsideFraction"]])
            mask = np.zeros(NBINS, dtype=bool)
            for k in ARCS:
                mask[k] = np.isfinite(y0[k]) and np.isfinite(ref[k]) and clip[k] <= 0.02 \
                    and out[k] <= 0.20
            if mask.sum() < 6:
                continue
            best, best_p = None, None
            for p in exponents:
                f = factor(r["scene"], r["web"]["scale"], float(p))
                err = float(np.nansum((y0[mask] * f[mask] - ref[mask]) ** 2))
                if best is None or err < best:
                    best, best_p = err, float(p)
            at0 = math.sqrt(float(np.nansum((y0[mask] - ref[mask]) ** 2)) / mask.sum())
            atp = math.sqrt(best / mask.sum())
            label = f"{scheme}-{scale}/{r['scene']}" + ("  [structured]" if structured else "")
            print(f"{label[:56]:56s} {r['set']:11s} {best_p:5.2f} {at0:12.4f} {atp:13.4f}")
            rows_out.append({"row": label, "set": r["set"], "scheme": scheme, "scale": scale,
                             "structured": structured, "p": best_p, "rmsAt0": at0, "rmsAtP": atp})
    for scheme in ("light", "dark"):
        for group, keep in (("solid calibration", lambda r: not r["structured"]
                             and r["set"] == "calibration"),
                            ("solid validation", lambda r: not r["structured"]
                             and r["set"] == "validation"),
                            ("structured", lambda r: r["structured"])):
            sub = [r["p"] for r in rows_out if r["scheme"] == scheme and keep(r)]
            if sub:
                print(f"   {scheme} / {group}: p* mean {np.mean(sub):.2f} +/- {np.std(sub):.2f} "
                      f"(min {min(sub):.2f} max {max(sub):.2f}, {len(sub)} rows)")

    print("\n== 3. the straight spans, W23's own contour reader, ladder against the landed bed")
    print("   `rim` per side in luminance per CSS px; solid untinted rows; the bound is 0.005.")
    print(f"{'row':46s} {'point':6s} {'side':7s} {'landed':>8s} {'ladder':>8s} {'delta':>8s}")
    worst_span, worst_where = 0.0, None
    base_contour = {}
    for scheme, scale in BEDS:
        key = f"apple-macos-26.5-{scale}-{scheme}-standard"
        base_contour[(scheme, scale)] = load(os.path.join(HERE, "reads",
                                                          f"contour-{key}.json"))
    for point in ("lit1", "lit2"):
        for scheme, scale in BEDS:
            lad = load(os.path.join(HERE, "ladder", f"{scheme}-{point}-{scale}-contour.json"))
            base = base_contour[(scheme, scale)]
            if lad is None or base is None:
                continue
            base_rows = {r["scene"]: r for r in base["rows"]}
            for r in lad["rows"]:
                if r["background"] not in SOLID or r.get("tint") or "rimWeb" not in r:
                    continue
                b = base_rows.get(r["scene"])
                if b is None or "rimWeb" not in b:
                    continue
                for i, side in enumerate(("top", "bottom", "left", "right")):
                    a, c = b["rimWeb"][i], r["rimWeb"][i]
                    if not (math.isfinite(a) and math.isfinite(c)):
                        continue
                    delta = c - a
                    if abs(delta) > worst_span:
                        worst_span = abs(delta)
                        worst_where = f"{scheme}-{scale}/{r['scene']}/{side} at {point}"
                    if abs(delta) > 0.0005:
                        print(f"{scheme}-{scale}/{r['scene']:<32s} {point:6s} {side:7s} "
                              f"{a:8.4f} {c:8.4f} {delta:+8.4f}")
    print(f"   worst |delta| on any solid straight span, over both ladder points: "
          f"{worst_span:.5f} at {worst_where}   bound 0.005: "
          f"{'PASS' if worst_span < 0.005 else 'FAIL'}")

    print("\n== 4. the prediction against parent acceptance clause 1, at three candidate exponents")
    print("   Clause 1 asks, on every untinted SOLID cell of both beds at both scales: the")
    print("   brightest/dimmest bin ratio within 20 % of the reference's wherever the reference's")
    print("   exceeds 2, and every bin within 0.005 (dark) / 0.03 (light) of the reference's. The")
    print("   bins are interpolated from the landed capture by the factor, which section 1")
    print("   licenses; a rendered dry run at the declared constant is G2's.")
    print("   `maxBin@0` is the same worst bin error on the LANDED bed, so the mechanism's own")
    print("   contribution is legible against what W23's amplitude already leaves.")
    print(f"{'row':46s} {'p':>5s} {'refRatio':>9s} {'ours':>8s} {'d%':>6s} {'maxBin@0':>9s} "
          f"{'maxBin':>8s} {'bound':>6s} {'verdict':>8s}")
    clause = []
    for candidate in (1.00, 1.15, 1.30, 1.45):
        met = failed = 0
        for scheme, scale in BEDS:
            base = landed[(scheme, scale)]
            if base is None:
                continue
            for r in base["rows"]:
                if r.get("tint") or "web" not in r or r["background"] not in SOLID:
                    continue
                y0 = np.asarray([np.nan if v is None else v for v in r["web"]["bins"]])
                ref = np.asarray([np.nan if v is None else v for v in r["native"]["bins"]])
                clip = np.asarray([0.0 if v is None else v for v in r["native"]["clipFraction"]])
                out = np.asarray([0.0 if v is None else v for v in r["native"]["outsideFraction"]])
                mask = np.isfinite(y0) & np.isfinite(ref) & (clip <= 0.02) & (out <= 0.20)
                if mask.sum() < 8:
                    continue
                f = factor(r["scene"], r["web"]["scale"], candidate)
                ours = y0 * f
                ref_ratio = float(np.nanmax(ref[mask]) / max(np.nanmin(ref[mask]), 1e-6))
                our_ratio = float(np.nanmax(ours[mask]) / max(np.nanmin(ours[mask]), 1e-6))
                bound = 0.005 if scheme == "dark" else 0.03
                max_bin = float(np.nanmax(np.abs(ours[mask] - ref[mask])))
                max_bin0 = float(np.nanmax(np.abs(y0[mask] - ref[mask])))
                ratio_ok = ref_ratio <= 2.0 or abs(our_ratio - ref_ratio) <= 0.2 * ref_ratio
                ok = ratio_ok and max_bin <= bound
                met += 1 if ok else 0
                failed += 0 if ok else 1
                print(f"{scheme}-{scale}/{r['scene'][:36]:<36s} {candidate:5.2f} "
                      f"{ref_ratio:9.2f} {our_ratio:8.2f} "
                      f"{100 * (our_ratio - ref_ratio) / max(ref_ratio, 1e-6):6.0f} "
                      f"{max_bin0:9.4f} {max_bin:8.4f} {bound:6.3f} "
                      f"{'MET' if ok else 'missed':>8s}")
        print(f"   exponent {candidate:.2f}: {met} of {met + failed} solid rows meet clause 1 "
              f"on both halves")
        clause.append({"exponent": candidate, "met": met, "rows": met + failed})

    if args.json:
        with open(args.json, "w") as fh:
            json.dump({"rows": rows_out, "worstArithmetic": worst_arith,
                       "worstStraightBin": worst_straight, "worstStraightSpan": worst_span,
                       "clauseOne": clause}, fh, indent=2)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
