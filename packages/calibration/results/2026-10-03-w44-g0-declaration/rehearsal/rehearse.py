#!/usr/bin/env python3.12
"""W44 G0 (c): the rehearsal (charter clause 2), run after `c05-baseline.json` was committed.

T1 on three existing renders, nothing rendered here:
  c05     the published light 0.25 generation (`6d18c059eb42`) and its dark twin (`d0219cd684bf`),
          read as the candidate AND the reference (k = c), every partition (published rows);
  0.5     the published 0.5 generations (`85ad7f7e3e0d` light, `0eac5b294cc2` dark) at 0.5, read
          against themselves; nothing at 0.5 is gated (X41), the bar there is the 0.5-code floor
          assumed, not derived;
  prefit  W43's pre-fit render (the shipped 0.5 documents on the 0.25 cells), as a candidate
          against c05; its referee rows are dropped by `bed.py` and never read.

And it checks, recording every reading:
  - the pinned baseline reproduced cell for cell (every structured light row, both tiers);
  - the three findings on their named subsets, with the cells inside a subset that go the other
    way named;
  - the stop: c05's thick fine-pitch cells separated from Apple's by at least three bars;
  - the anchors on their own support (T1-deep), and T1's disagreement with T1-deep on each;
  - the landing rule's T1 clauses and the selection rule on c05 and on the pre-fit render;
  - where the moire sits in c05's fine-checker body, and which band isolates the receded 2x photo
    lattice (`readings.py` holds the reading that band defines).

    python3.12 -B rehearse.py [--captures TREE] [--prefit-captures TREE]
writes rehearsal.json and rehearsal.txt beside it (refuses to overwrite).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import statistics
import subprocess
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np
from scipy.ndimage import gaussian_filter, maximum_filter

HERE = Path(__file__).resolve().parent
EVIDENCE = HERE.parent
sys.path.insert(0, str(EVIDENCE / "cuts"))
import bed as B  # noqa: E402
import cuts as K  # noqa: E402
import readings as R  # noqa: E402
import t1  # noqa: E402

sys.path.insert(0, str(EVIDENCE / "referees"))
import plan  # noqa: E402

PREFIT = Path.home() / "vitrea-w43" / "g3-scratch" / "prefit"
PREFIT_SHA = "504c5348638265e6a141308d4f74d98dc6119dfbb9e12e15164fc6e028bdebbb"
LIGHT05 = ("apple-macos-27.0-1x-light-standard-glass0.5", "apple-macos-27.0-2x-light-standard-glass0.5")
DARK025 = ("apple-macos-27.0-1x-dark-standard-glass0.25", "apple-macos-27.0-2x-dark-standard-glass0.25")
DARK05 = ("apple-macos-27.0-1x-dark-standard-glass0.5", "apple-macos-27.0-2x-dark-standard-glass0.5")
ANCHORS = [("0.25", "checkerboard-4__rrect-md__rest", 2.9, 9.1),
           ("0.25", "checkerboard-4__rrect-md__inactive", 0.3, 10.5),
           ("0.5", "checkerboard-4__rrect-md__rest", 1.7, 2.6)]


def canonical_tree() -> Path:
    common = subprocess.run(["git", "-C", str(B.ROOT), "rev-parse", "--git-common-dir"],
                            capture_output=True, text=True, check=True).stdout.strip()
    return Path(common).resolve().parent / "packages" / "calibration" / "web-captures"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def native_png(profile, sid):
    return K.rgb((K.FIXTURES / profile / f"{sid}.png").read_bytes())


# ---------------------------------------------------------------------------------------------
def reproduce_baseline(c05: dict) -> dict:
    base = json.loads((HERE / "c05-baseline.json").read_bytes())
    mine = {(c["profile"], c["tier"], c["scene"]): c for c in c05["cells"]}
    mismatches, checked = [], 0
    for cell in base["cells"]:
        got = mine.get((cell["profile"], cell["tier"], cell["scene"]))
        checked += 1
        if got is None or got["ratio"] != cell["ratio"] or got["native"] != cell["native"]:
            mismatches.append(f"{cell['profile']} {cell['tier']} {cell['scene']}: baseline "
                              f"{cell['ratio']}, T1 {None if got is None else got['ratio']}")
    extra = len({k for k in mine if k[0] in t1.GATED_PROFILES}) - checked
    return dict(baselineSha256=sha(HERE / "c05-baseline.json"), cellsChecked=checked,
                mismatches=mismatches, t1CellsNotInBaseline=extra, reproduced=not mismatches and extra == 0)


def findings(cells) -> dict:
    two = [c for c in cells if c["tier"] == "webgpu" and c["scale"] == 2 and c["scheme"] == "light"]
    med = lambda sel: statistics.median([c["ratio"] for c in sel])  # noqa: E731
    by_bd = defaultdict(list)
    for c in two:
        if c["pose"] == "rest" and c["spanClass"] == "thin":
            by_bd[B.SCENES.by_id[c["scene"]]["background"]].append(c)
    thin = {b: med(v) for b, v in sorted(by_bd.items())}
    f_mt = [c for c in two if c["stratum"] == "F" and c["pose"] == "rest" and c["spanClass"] in ("mid", "thick")]
    inact = [c for c in two if c["pose"] == "inactive" and (c["stratum"] == "F" or B.SCENES.by_id[c["scene"]]["background"]
                                                          in ("checkerboard", "checkerboard-lc16", "checkerboard-32"))]
    named3 = [c for c in two if c["pose"] == "inactive" and (B.SCENES.by_id[c["scene"]]["background"] == "checkerboard-64" or (
        B.SCENES.by_id[c["scene"]]["background"] == "hc-text" and c["spanClass"] == "thick"))]
    nm = lambda sel: {c["scene"]: round(c["ratio"], 4) for c in sel}  # noqa: E731
    return {
        "i": dict(perBackdrop={b: round(v, 4) for b, v in thin.items()},
                  range=[min(thin.values()), max(thin.values())], holds=all(v < 0.9 for v in thin.values()),
                  thinRestCellsAtOrAbove1=nm(c for v in by_bd.values() for c in v if c["ratio"] >= 1)),
        "ii": dict(median=med(f_mt), holds=med(f_mt) > 1.5, namedUnder=nm(c for c in f_mt if c["ratio"] < 1),
                   lowestOver=min((c["ratio"], c["scene"]) for c in f_mt if c["ratio"] >= 1)),
        "iii": dict(median=med(inact), holds=med(inact) > 2, named=nm(named3),
                    subsetCellsUnder2=nm(c for c in inact if c["ratio"] < 2)),
    }


def stop_check(cells) -> dict:
    """Clause 2's stop: c05's thick fine-pitch cells (F, spans 128-160, 2x light WebGPU, both
    poses) separated from Apple's by at least three bars: |c - n| >= 3 bar."""
    sel = [c for c in cells if c["tier"] == "webgpu" and c["scale"] == 2 and c["scheme"] == "light"
           and c["stratum"] == "F" and c["spanClass"] == "thick"]
    rows = [dict(scene=c["scene"], partition=c["partition"], native=c["native"], c05=c["reference"],
                 bar=c["bar"], separationInBars=abs(c["reference"] - c["native"]) / c["bar"]) for c in sel]
    worst = min(r["separationInBars"] for r in rows)
    return dict(cells=rows, minimumSeparationInBars=worst, passes=worst >= 3,
                alsoMid=[dict(scene=c["scene"], separationInBars=abs(c["reference"] - c["native"]) / c["bar"])
                         for c in cells if c["tier"] == "webgpu" and c["scale"] == 2 and c["scheme"] == "light"
                         and c["stratum"] == "F" and c["spanClass"] == "mid"])


# ---------------------------------------------------------------------------------------------
def readings_over(rows, root: Path, profiles, tier="webgpu") -> list:
    out = []
    for r in rows:
        profile, sid = r["key"]["profileKey"], r["key"]["sceneId"]
        if profile not in profiles or r["key"]["web"]["renderer"] != tier:
            continue
        if B.SCENES.by_id[sid]["background"] not in t1.T1_BACKDROPS:
            continue
        web, digest = K.capture(root, r, tier)
        got = R.read(profile, sid, native_png(profile, sid), web)
        n, w = B.value(r, "material", "interiorStdDevNative"), B.value(r, "material", "interiorStdDevWeb")
        out.append(dict(profile=profile, scene=sid, tier=tier, scale=B.scale_of(profile),
                        stratum=t1.stratum(sid), pose=t1.pose(sid), spanClass=t1.span_class(sid),
                        partition=B.SCENES.role[sid], webSha256=digest, t1Ratio=w / n, **got))
    return out


def summarise_readings(rs) -> dict:
    groups = defaultdict(list)
    for r in rs:
        groups[f"{r['stratum']} {r['scale']}x {r['pose']}"].append(r)
        groups[f"{r['stratum']} {r['scale']}x {r['pose']} {r['spanClass']}"].append(r)
    out = {}
    for key, g in sorted(groups.items()):
        entry = dict(cells=len(g), t1=statistics.median(x["t1Ratio"] for x in g))
        for k in ("deep", "fine", "lattice"):
            v = [x["ratio"][k] for x in g if x["ratio"][k] is not None]
            entry[k] = statistics.median(v) if v else None
            entry[k + "Range"] = [min(v), max(v)] if v else None
        out[key] = entry
    return out


def anchors(c05_rows, rows05, root) -> list:
    out = []
    for pos, sid, an, aw in ANCHORS:
        profile = f"apple-macos-27.0-2x-light-standard-glass{pos}"
        row = next(r for r in (c05_rows if pos == "0.25" else rows05) if r["key"]["profileKey"] == profile
                   and r["key"]["sceneId"] == sid and r["key"]["web"]["renderer"] == "webgpu")
        web, digest = K.capture(root, row, "webgpu")
        got = R.read(profile, sid, native_png(profile, sid), web)
        n, w = B.value(row, "material", "interiorStdDevNative"), B.value(row, "material", "interiorStdDevWeb")
        out.append(dict(
            position=pos, scene=sid, sheet=dict(native=an, web=aw, ratio=aw / an),
            t1Deep=dict(native=got["native"]["deep"], web=got["web"]["deep"], ratio=got["ratio"]["deep"],
                        reproducesSheetToRounding=(round(got["native"]["deep"], 1) == an and
                                                   round(got["web"]["deep"], 1) == aw)),
            t1=dict(native=n, web=w, ratio=w / n),
            disagreement=(f"T1 reads x{w / n:.2f} (linear SD over the whole native silhouette, rim and lens "
                          f"band included: {n:.4f} / {w:.4f}); T1-deep reads x{got['ratio']['deep']:.2f} "
                          f"(encoded SD on the body eroded 8 CSS px: {got['native']['deep']:.2f} / "
                          f"{got['web']['deep']:.2f} codes)"),
            webSha256=digest))
    return out


# ---------------------------------------------------------------------------------------------
def moire(root: Path, c05_rows) -> dict:
    """Where the moire sits: the fine residual's SD (L - G(L, sigma 2 CSS px), linear, normalised
    over the native silhouette) per band of distance inside the declared contour, in bins of one
    checker cell (so a bin never selects one phase of the checker), web against native."""
    out = {}
    for scale in (2, 1):
        profile = f"apple-macos-27.0-{scale}x-light-standard-glass0.25"
        for sid in ("checkerboard-4__rrect-md__rest", "checkerboard-4__rrect-md__inactive",
                    "checkerboard-4__rrect-lg__rest", "checkerboard-8__rrect-md__rest"):
            row = next(r for r in c05_rows if r["key"]["profileKey"] == profile and r["key"]["sceneId"] == sid
                       and r["key"]["web"]["renderer"] == "webgpu")
            web, _ = K.capture(root, row, "webgpu")
            nat = native_png(profile, sid)
            g = R.cell_geometry(profile, sid, nat)
            cell = (4 if "checkerboard-4" in sid else 8) * scale
            bins, lo = [], 0
            while lo < 96 * scale // 2:
                hi = lo + cell
                sel = g["silhouette"] & (g["signedDistance"] <= -lo) & (g["signedDistance"] > -hi)
                if sel.sum() < 50:
                    break
                vals = {}
                for side, img in (("native", nat), ("web", web)):
                    L = R.P.luminance(img)
                    res = L - R.masked_gaussian(L, g["silhouette"], 2.0 * scale)
                    vals[side] = float(res[sel].std())
                bins.append(dict(insideDevicePx=[lo, hi], pixels=int(sel.sum()), **vals,
                                 ratio=vals["web"] / vals["native"] if vals["native"] else None))
                lo = hi
            deep_web = statistics.median(b["web"] for b in bins if b["insideDevicePx"][0] >= 48 * scale // 2) \
                if any(b["insideDevicePx"][0] >= 48 * scale // 2 for b in bins) else None
            dip = min((b for b in bins if b["insideDevicePx"][0] > 0), key=lambda b: b["web"])
            out[f"{scale}x {sid}"] = dict(binDevicePx=cell, bins=bins, webDeepMedian=deep_web,
                                          webMinimumBin=dip["insideDevicePx"],
                                          webMinimumOverDeep=dip["web"] / deep_web if deep_web else None)
    return out


def autocorrelation(r: np.ndarray, m: np.ndarray) -> np.ndarray:
    H, W = r.shape
    F = np.fft.rfft2(r * m, s=(2 * H, 2 * W))
    G = np.fft.rfft2(m.astype(float), s=(2 * H, 2 * W))
    a = np.fft.fftshift(np.fft.irfft2(F * np.conj(F)) / np.maximum(np.fft.irfft2(G * np.conj(G)), 1))
    return a / a[H, W]


def lattice(root: Path, c05_rows) -> dict:
    """Which band isolates the receded 2x photo lattice: masked DoG bands of linear luminance over
    the native silhouette eroded 4 CSS px, web / native, on photo__rrect-md (both poses) at 2x and
    its 1x twin, with the backdrop's own band SD; and the band residual's autocorrelation peaks,
    against the backdrop's lattice vectors."""
    out = {}
    bands_css = [(0.5, 1), (1, 2), (2, 4), (4, 8), (8, 16), (1, 4)]
    for scale in (2, 1):
        profile = f"apple-macos-27.0-{scale}x-light-standard-glass0.25"
        for sid in ("photo__rrect-md__inactive", "photo__rrect-md__rest", "photo__rrect-ml__inactive"):
            row = next(r for r in c05_rows if r["key"]["profileKey"] == profile and r["key"]["sceneId"] == sid
                       and r["key"]["web"]["renderer"] == "webgpu")
            web, _ = K.capture(root, row, "webgpu")
            nat = native_png(profile, sid)
            g = R.cell_geometry(profile, sid, nat)
            m = g["eroded"]
            H, W = m.shape
            entry = dict(bands={}, peaks={})
            for side, img in (("native", nat), ("web", web), ("backdrop", g["background"])):
                L = R.P.luminance(img)
                for lo, hi in bands_css:
                    band = R.masked_gaussian(L, m, lo * scale) - R.masked_gaussian(L, m, hi * scale)
                    entry["bands"].setdefault(f"css {lo}-{hi}", {})[side] = float(band[m].std())
                band = R.masked_gaussian(L, m, 1.0 * scale) - R.masked_gaussian(L, m, 4.0 * scale)
                a = autocorrelation(band * m, m)
                yy, xx = np.indices(a.shape)
                dist = np.hypot(yy - H, xx - W)
                cand = (a == maximum_filter(a, size=5)) & (dist >= 4 * scale) & (dist <= 30 * scale) & (yy >= H)
                order = np.argsort(a[cand])[::-1][:3]
                entry["peaks"][side] = [dict(dxDevice=int(xx[cand][i] - W), dyDevice=int(yy[cand][i] - H),
                                             correlation=round(float(a[cand][i]), 3)) for i in order]
            for name, b in entry["bands"].items():
                b["ratio"] = b["web"] / b["native"]
            out[f"{scale}x {sid}"] = entry
    return out


# ---------------------------------------------------------------------------------------------
def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--captures", type=Path, default=None)
    ap.add_argument("--prefit-captures", type=Path, default=PREFIT / "web-captures")
    args = ap.parse_args()
    root = args.captures or canonical_tree()
    if sha(PREFIT / "matrix.json") != PREFIT_SHA:
        raise SystemExit("the pre-fit scratch matrix is not W43's recorded one")
    out_json, out_txt = HERE / "rehearsal.json", HERE / "rehearsal.txt"
    if out_json.exists() or out_txt.exists():
        raise SystemExit("rehearsal outputs exist; a recorded rehearsal is never overwritten")
    manifest = plan.load_manifest()
    held = plan.referee_cells(manifest)
    bars = t1.load_bars()

    c05 = B.load_published("6d18c059eb42")
    c05d = B.load_published("d0219cd684bf")
    c05_rows = c05.rows + c05d.rows
    g05 = B.load_published("85ad7f7e3e0d")
    g05d = B.load_published("0eac5b294cc2")
    prefit = B.load([str(PREFIT / "matrix.json")], "prefit")

    on_c05 = t1.cut(c05_rows, c05_rows, t1.GATED_PROFILES + DARK025, bars, held)
    on_05 = t1.cut(g05.rows + g05d.rows, g05.rows + g05d.rows, LIGHT05 + DARK05, bars, set(),
                   partitions=("gate", "holdout"))
    on_prefit = t1.cut(prefit.rows, c05_rows, t1.GATED_PROFILES + DARK025, bars, held,
                       partitions=("gate",))

    result = dict(
        schema="w44-rehearsal-1",
        what="W44 G0 (c), charter clause 2: T1 rehearsed on c05, the 0.5 generation and the pre-fit "
             "render; the anchors; the moire and the lattice located",
        sources=dict(
            tools={p.name: sha(p) for p in (Path(__file__), EVIDENCE / "cuts/t1.py", EVIDENCE / "cuts/bed.py",
                                            EVIDENCE / "cuts/readings.py", EVIDENCE / "cuts/cuts.py")},
            bar=dict(path="bar/t1-bar.json", sha256=sha(EVIDENCE / "bar/t1-bar.json")),
            referees=dict(path="referees/referees.json", sha256=manifest["sha256"]),
            c05=c05.described()["matrices"] + c05d.described()["matrices"],
            generation05=g05.described()["matrices"] + g05d.described()["matrices"],
            prefit=prefit.described(), captures=str(root)),
        baseline=reproduce_baseline(on_c05),
        findings=findings(on_c05["cells"]),
        stop=stop_check(on_c05["cells"]),
        landing=dict(c05=t1.landing(on_c05["cells"]), prefit=t1.landing(on_prefit["cells"])),
        selection=dict(c05=t1.selection_metric(on_c05["cells"]), prefit=t1.selection_metric(on_prefit["cells"]),
                       tie=t1.selection_tie(on_c05["cells"])),
        t1=dict(c05=on_c05, generation05=on_05, prefit=on_prefit),
    )
    sel = result["selection"]
    sel["lands"] = ("tie (the fewer moved leaves lands)" if abs(sel["c05"] - sel["prefit"]) <= sel["tie"]
                    else "c05" if sel["c05"] < sel["prefit"] else "prefit")
    result["anchors"] = anchors(c05.rows, g05.rows, root)
    rs = readings_over(c05.rows, root, t1.GATED_PROFILES)
    rs_css = readings_over(c05.rows, root, t1.GATED_PROFILES, tier="css")
    rp = readings_over(prefit.rows, args.prefit_captures, t1.GATED_PROFILES)
    result["readings"] = dict(
        c05=dict(summary=summarise_readings(rs), cells=rs),
        c05Css=dict(summary=summarise_readings(rs_css), cells=rs_css),
        prefit=dict(summary=summarise_readings(rp), cells=rp))
    result["moire"] = moire(root, c05.rows)
    result["lattice"] = lattice(root, c05.rows)
    with out_json.open("x") as f:
        json.dump(result, f, indent=1)
        f.write("\n")
    text = report(result)
    with out_txt.open("x") as f:
        f.write(text)
    print(text)
    return 0


def report(r) -> str:
    L = []
    b = r["baseline"]
    L.append(f"baseline: {b['cellsChecked']} cells checked, {len(b['mismatches'])} mismatches, "
             f"{b['t1CellsNotInBaseline']} T1 cells not in it -> {'REPRODUCED' if b['reproduced'] else 'NOT REPRODUCED'}")
    f = r["findings"]
    L.append(f"(i)   thin rest medians {f['i']['range'][0]:.2f}-{f['i']['range'][1]:.2f}: "
             f"{'holds' if f['i']['holds'] else 'DOES NOT HOLD'}; thin rest cells at or above 1: {f['i']['thinRestCellsAtOrAbove1']}")
    L.append(f"(ii)  F mid/thick rest median {f['ii']['median']:.2f}: {'holds' if f['ii']['holds'] else 'DOES NOT HOLD'}; "
             f"under 1: {f['ii']['namedUnder']}; lowest over: {f['ii']['lowestOver']}")
    L.append(f"(iii) inactive subset median {f['iii']['median']:.2f}: {'holds' if f['iii']['holds'] else 'DOES NOT HOLD'}; "
             f"named: {f['iii']['named']}; subset cells under 2: {f['iii']['subsetCellsUnder2']}")
    s = r["stop"]
    L.append(f"stop: thick fine-pitch c05 cells separated by >= {s['minimumSeparationInBars']:.1f} bars "
             f"({'PASSES' if s['passes'] else 'FAILS: the wave stops for a new statistic'})")
    for c in s["cells"]:
        L.append(f"   {c['scene']:<40} {c['partition']:<8} n {c['native']:.4f} c05 {c['c05']:.4f} "
                 f"bar {c['bar']:.5f} -> {c['separationInBars']:.1f} bars")
    L.append("anchors (T1-deep on its own support; T1 beside it):")
    for a in r["anchors"]:
        L.append(f"   {a['position']:<5} {a['scene']:<36} sheet {a['sheet']['native']}/{a['sheet']['web']}  "
                 f"T1-deep {a['t1Deep']['native']:.2f}/{a['t1Deep']['web']:.2f} "
                 f"({'reproduced' if a['t1Deep']['reproducesSheetToRounding'] else 'not to rounding'}); {a['disagreement']}")
    for name in ("c05", "prefit"):
        g = r["landing"][name]
        L.append(f"landing on {name}: {g['verdict']}; F aggregate {g['fAggregate']:.4f} against c05's "
                 f"{g['fAggregateReference']:.4f}; {len(g['fNotWithin'])} F cells not within; "
                 f"{len(g['awayBeyondB'])} away beyond B; {len(g['overshoot'])} overshoot")
    sel = r["selection"]
    L.append(f"selection metric: c05 {sel['c05']:.4f}, prefit {sel['prefit']:.4f}, tie width {sel['tie']:.4f} -> {sel['lands']}")
    for name in ("c05", "prefit"):
        agg = r["t1"][name]["aggregates"]
        L.append(f"T1 aggregates on {name} (light, WebGPU and CSS; gate partition):")
        for k, v in agg.items():
            if " light " in k and not k.endswith(" both"):
                L.append(f"   {k:<34} n={v['cells']:<3} median|log| {v['medianLogError']:.4f} "
                         f"(c05 {v['referenceMedianLogError']:.4f}) {v['fidelity']} {v['change']}")
    L.append("T1 on the 0.5 generation (read, X41; bar floor assumed):")
    for k, v in r["t1"]["generation05"]["aggregates"].items():
        if " light webgpu" in k and not k.endswith(" both"):
            L.append(f"   {k:<34} n={v['cells']:<3} median|log| {v['medianLogError']:.4f} {v['fidelity']}")
    for name in ("c05", "c05Css", "prefit"):
        L.append(f"readings on {name} (medians web/native):")
        for k, v in r["readings"][name]["summary"].items():
            L.append(f"   {k:<22} n={v['cells']:<3} T1 x{v['t1']:.2f}  deep x{v['deep'] or float('nan'):.2f}  "
                     f"fine x{v['fine'] or float('nan'):.2f}  lattice x{v['lattice'] or float('nan'):.2f}")
    L.append("moire: the fine residual's SD by distance inside the contour (web / native), c05 WebGPU:")
    for k, v in r["moire"].items():
        L.append(f"   {k:<44} bins of {v['binDevicePx']} px; web minimum at {v['webMinimumBin']} px inside, "
                 f"{v['webMinimumOverDeep'] if v['webMinimumOverDeep'] is None else round(v['webMinimumOverDeep'], 2)} of its deep level")
        L.append("      " + " ".join(f"{b['insideDevicePx'][0]}:{b['web']:.3f}/{b['native']:.3f}" for b in v["bins"]))
    L.append("lattice: band SD web/native (backdrop SD), c05 WebGPU; autocorrelation peaks of the css 1-4 band:")
    for k, v in r["lattice"].items():
        L.append(f"   {k:<34} " + "  ".join(f"{n} x{b['ratio']:.2f}" for n, b in v["bands"].items()))
        for side, peaks in v["peaks"].items():
            L.append(f"      {side:<8} " + " ".join(f"({p['dxDevice']},{p['dyDevice']}) {p['correlation']}" for p in peaks))
    return "\n".join(L) + "\n"


if __name__ == "__main__":
    sys.exit(main())
