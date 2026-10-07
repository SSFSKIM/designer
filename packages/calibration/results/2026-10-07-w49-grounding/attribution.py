#!/usr/bin/env python3
"""W49 G0 grounding (charter `2026-10-07-w49-authorised-list-repair.md`, Grounding): attribute each of
the seventeen cells `T1_DARK_AUTHORISED_REGRESSIONS` names to the leaf that caused it, from evidence that
already exists. Renders nothing; reads only committed files and the W48 fit-summaries archive.

    python3 -B attribution.py <root of the extracted w48-fit-summaries-archive> > attribution.txt

The archive is GitHub release `w48-fit-summaries-archive` (claims §5.214 §14), asset
`g1-candidate-summaries.tar.gz`, SHA-256 bd610da5c9ca44a54b0ad363254e6a75a1e361d7e691d08c2fdf86a93d413f9d,
extracted into an empty directory (its entries are repository-relative). Writes `attribution.json`
beside this file. Four readings:

1. the landed cells: native, `d0219cd684bf`, `b2d074d2df24`, growth in B, from W48's exposure cut;
2. the authority check: for every cell stage 2 of W48's fit read, the number of distinct values over
   all of its rendered points (a cell with ONE value was outside every receded leaf's reach);
3. W46's point A (receded tintAlpha 0.8, no far delta, over the d0219 active) on the same cells,
   from W46's gate cut — the receded scatter WITHOUT the opaque body;
4. stage 1's isolation of the active rest cells: the span top, the far delta, the scale gain;
5. the shader's arithmetic on the bed's spans (alphaBase, kDeep, farS, the 2x heavy gain), both
   generations, both poses, both scales, from the documents' leaves and the defaults they patch.
"""
import glob
import gzip
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
RES = HERE.parent
EXPOSURE = RES / "2026-10-06-w48-g1-refit/cuts/cut-025-w48-dl9-exposure.json.gz"
POINT_A = RES / ("2026-10-05-w46-g1-refit/gate/"
                 "d-s2-rta0.8-rs214-rfa0.5-rh10.25-re20.04-rk10.15-rk20.04-rn10.4-rn20.4-rg0/cut.json.gz")
CANDIDATES = "packages/calibration/results/2026-10-06-w48-g1-refit/fit/candidates"
DARK = ("apple-macos-27.0-1x-dark-standard-glass0.25", "apple-macos-27.0-2x-dark-standard-glass0.25")
AUTHORISED = [  # T1_DARK_AUTHORISED_REGRESSIONS, adopted-thresholds.test.ts, in its order
    (1, "checkerboard-64__rrect-lg__inactive"), (1, "checkerboard-32__rrect-lg__inactive"),
    (1, "checkerboard-32__rrect-lg__rest"), (1, "checkerboard-lc16__rrect-md__rest"),
    (1, "photo__rrect-lg__inactive"), (1, "impulse__capsule-button__rest"),
    (1, "checkerboard-64__rrect-lg__rest"), (1, "hc-text-28__rrect-lg__rest"),
    (2, "checkerboard-64__rrect-lg__inactive"), (2, "checkerboard-32__rrect-lg__inactive"),
    (2, "checkerboard-lc16__rrect-md__rest"), (2, "photo__rrect-lg__inactive"),
    (2, "checkerboard__capsule-button__inactive"), (2, "checkerboard-32__rrect-lg__rest"),
    (2, "checkerboard__capsule-button__inactive-tint-orange"), (2, "checkerboard-64__rrect-lg__rest"),
    (2, "hc-text-28__rrect-lg__rest"),
]
SPANS = {"capsule-button": 44, "rrect-sm": 64, "rrect-md": 96, "rrect-ml": 128, "rrect-lg": 160}


def cells_of(cut_path):
    cut = json.load(gzip.open(cut_path))
    return {(c["scale"], c["scene"]): c for c in cut["T1"]["cells"]
            if c["profile"] in DARK and c["tier"] == "webgpu"}


def smoothstep(e0, e1, x):
    t = min(max((x - e0) / max(e1 - e0, 1e-6), 0.0), 1.0)
    return t * t * (3 - 2 * t)


def ramp(a1, a2, dpr):
    return a1 + (a2 - a1) * min(max(dpr - 1, 0.0), 1.0)


def law(m, span, dpr):
    """optics.ts's per-pixel law at one span (the surface's shorter extent), dark 0.25 leaves."""
    top = ramp(m["sizeScatterSpanMax"], m["sizeScatterSpanMax2x"], dpr)
    floor = ramp(m["sizeScatterFloor"], m["sizeScatterFloor2x"], dpr)
    thick = smoothstep(32, 96, span)
    far = smoothstep(96, top, span)
    k_deep = min(1.0, floor + (1 - floor) * smoothstep(32, top, span)
                 + ramp(m["sizeScatterHeavyShareThick1x"], 0.0, dpr) * thick)
    start = (ramp(m["thin1x"], m["thin2x"], dpr)
             + (ramp(m["thick1x"], m["thick2x"], dpr) - ramp(m["thin1x"], m["thin2x"], dpr)) * thick
             + (ramp(m["far1x"], m["far2x"], dpr) - ramp(m["thick1x"], m["thick2x"], dpr)) * far)
    alpha = min(max(m["tintAlpha"] + ramp(m["tintAlphaFar1x"], m["tintAlphaFar2x"], dpr) * far, 0), 1)
    sized = alpha + m["sizeOcclusionGain"] * thick * (1 - alpha)
    out = dict(farS=round(far, 4), kDeep=round(k_deep, 4), edgeSharpStart=round(start, 4),
               alphaBase=round(alpha, 4), sizedAlpha=round(sized, 4))
    if dpr > 1 and m["sizeHeavyTapSigma2x"] == 0:
        out["heavyGain2x"] = round(4.8 + (9.9 - 4.8) * far, 3)
    return out


# Resolved leaves the law reads (DEFAULT_MATERIAL_PROFILE patched by each document; the receded
# documents are differences over their own active). Read off the four documents by hand; the
# `documents.json` beside this file holds the patches they were read from.
BASE = dict(sizeScatterFloor=0.4, sizeScatterFloor2x=1, sizeScatterSpanMax=256, sizeScatterSpanMax2x=256,
            thin1x=0.72, thick1x=0.52, far1x=0.2, thin2x=0.46, thick2x=0.21, far2x=0.21,
            sizeScatterHeavyShareThick1x=0, sizeOcclusionGain=0.05, tintAlphaFar1x=0, tintAlphaFar2x=0,
            sizeHeavyTapSigma2x=9)
D0219_ACTIVE = {**BASE, "tintAlpha": 0.9, "sizeScatterFloor": 0.34, "sizeHeavyTapSigma2x": 0}
D0219_RECEDED = {**D0219_ACTIVE, "tintAlpha": 0.89, "thin1x": 1, "thin2x": 1, "thick1x": 0.3,
                 "thick2x": 0.04, "far2x": 0.04, "sizeHeavyTapSigma2x": 14,
                 "sizeScatterHeavyShareThick1x": 0.25}
B2D074_ACTIVE = {**D0219_ACTIVE, "tintAlpha": 0.7, "tintAlphaFar1x": 0.2, "tintAlphaFar2x": 0.2,
                 "sizeScatterSpanMax": 160, "sizeScatterSpanMax2x": 160}
B2D074_RECEDED = {**D0219_RECEDED, "tintAlpha": 0.8, "tintAlphaFar1x": 0.2, "tintAlphaFar2x": 0.2,
                  "sizeScatterSpanMax": 160, "sizeScatterSpanMax2x": 160, "sizeScatterFloor": 0.5,
                  "thin1x": 0.4, "thin2x": 0.4, "thick1x": 0.15}


def main(argv):
    archive = Path(argv[1])
    out = {}
    landed = cells_of(EXPOSURE)
    point_a = cells_of(POINT_A)

    print("1. THE SEVENTEEN, landed (W48 exposure cut; T1 interiorStdDev, linear light)")
    print(f"{'cell':55s} {'part':8s} {'native':>7s} {'d0219':>7s} {'b2d074':>7s} {'growth':>8s}")
    rows = []
    for scale, scene in AUTHORISED:
        c = landed[(scale, scene)]
        g = c["growth"] / c["B"]
        rows.append(dict(scale=scale, scene=scene, partition=c["partition"], native=c["native"],
                         d0219=c["reference"], b2d074=c["candidate"], growthB=round(g, 2), B=c["B"]))
        print(f"{scale}x {scene:52s} {c['partition']:8s} {c['native']:7.4f} {c['reference']:7.4f} "
              f"{c['candidate']:7.4f} {g:+7.2f}B")
    out["landed"] = rows

    print("\n2. AUTHORITY: distinct T1 values per cell over every stage-2 summary in the archive (191)")
    values, seen = {}, {}
    for f in sorted(glob.glob(str(archive / CANDIDATES / "d-s2-*/summary.json"))):
        d = json.load(open(f))
        for k, c in d["cells"].items():
            values.setdefault(k, set()).add(round(c["k"], 6))
            seen[k] = c
    authority = {}
    for k in sorted(values):
        v = sorted(values[k])
        authority[k] = dict(distinct=len(v), min=v[0], max=v[-1], native=seen[k]["n"], d0219=seen[k]["c"])
        flag = "   <- NO RECEDED LEAF REACHES IT" if len(v) == 1 else ""
        print(f"  {k:52s} n={seen[k]['n']:.4f} d0219={seen[k]['c']:.4f} distinct={len(v):3d} "
              f"range {v[0]:.4f}..{v[-1]:.4f}{flag}")
    out["stage2Authority"] = authority

    print("\n3. W46 POINT A (receded scatter, tintAlpha 0.8, no far delta, d0219 active), inactive cells")
    pa = {}
    for (scale, scene), c in sorted(point_a.items()):
        if c["pose"] != "inactive":
            continue
        g = c["growth"] / c["B"]
        pa[f"{scale}x {scene}"] = dict(native=c["native"], d0219=c["reference"], pointA=c["candidate"],
                                       growthB=round(g, 2), change=c["change"])
        b = landed.get((scale, scene))
        print(f"  {scale}x {scene:50s} n={c['native']:.4f} d0219={c['reference']:.4f} "
              f"ptA={c['candidate']:.4f} ({g:+.2f}B {c['change']})"
              + (f"  b2d074={b['candidate']:.4f}" if b else ""))
    out["pointA"] = pa

    print("\n4. STAGE 1: the active rest cells by leaf (W48 fit renders; same alpha 0.9 at span 160 in")
    print("   d0219 and in every ta0.7/far0.2 point, so a difference there is the scatter's, not the body's)")
    keys = ["checkerboard-32__rrect-lg__rest", "checkerboard-64__rrect-lg__rest", "hc-text-28__rrect-lg__rest",
            "checkerboard-lc16__rrect-md__rest", "impulse__capsule-button__rest"]
    iso = {}
    for f in sorted(glob.glob(str(archive / CANDIDATES / "d-s1-*/summary.json"))):
        d = json.load(open(f))
        a = d["overrides"].get("active.dark", {})
        for scale in (1, 2):
            sfx = "" if scale == 1 else "2x"
            key = (f"{scale}x ta{a.get('optics.regular.tintAlpha')} o{a.get('sizeOcclusionGain')} "
                   f"top{a.get('sizeScatterSpanMax' + sfx)} far{a.get('tintAlphaFar' + str(scale) + 'x')} "
                   f"floor{a.get('sizeScatterFloor' + sfx)} thin{a.get('sizeScatterRampStartThin' + str(scale) + 'x')} "
                   f"gain{a.get('sizeScatterScaleGain')} heavy{a.get('sizeHeavyTapSigma' + sfx)}")
            got = [d["cells"].get(f"{scale}x {s}", {}).get("k") for s in keys]
            if all(x is not None for x in got):
                iso[key] = [round(x, 4) for x in got]
    for scale in (1, 2):
        ref = [round(landed[(scale, s)]["reference"], 4) for s in keys]
        nat = [round(landed[(scale, s)]["native"], 4) for s in keys]
        print(f"  {scale}x cells: " + " | ".join(keys))
        print(f"  {scale}x native {nat}  d0219 {ref}")
        for k in sorted(iso):
            if k.startswith(f"{scale}x ta0.7 o0.05 top160 far0.2") or k.startswith(f"{scale}x ta0.9 o0.05 top160 far0.2"):
                print(f"    {k:78s} {iso[k]}")
    out["stage1"] = iso

    print("\n5. THE LAW ON THE BED'S SPANS (optics.ts arithmetic; edgeSharpStart is the ramp start at u=0)")
    arith = {}
    for name, m in [("d0219 active", D0219_ACTIVE), ("b2d074 active", B2D074_ACTIVE),
                    ("d0219 receded", D0219_RECEDED), ("b2d074 receded", B2D074_RECEDED)]:
        for dpr in (1, 2):
            for comp, span in SPANS.items():
                r = law(m, span, dpr)
                arith[f"{name} {dpr}x {comp}"] = r
                print(f"  {name:15s} {dpr}x {comp:15s} {r}")
    out["law"] = arith

    (HERE / "attribution.json").write_text(json.dumps(out, indent=1, sort_keys=True) + "\n")


if __name__ == "__main__":
    sys.exit(main(sys.argv))
