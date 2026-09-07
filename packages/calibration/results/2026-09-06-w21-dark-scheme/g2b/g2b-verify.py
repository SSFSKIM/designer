"""W21 G2b — the referee over the scratch read (Part 3).

Four questions, each answered against a file rather than against a recollection:

  (i)   the GPU tier did not move — the 1x dark webgpu captures reproduce `g1/g1-digests.txt`;
  (ii)  contract X3 — every LIGHT capture on the CSS tier is byte-identical to the canonical bed;
  (iii) what the dark CSS rows did — the thirteen gate rows and every dark CSS cell's OKLab ΔE
        mean, against the W20 bed (kept in scratch by G2's rebuild) and against what G2 landed;
  (iv)  the bed's shape — the scratch matrix still carries the canonical bed's 229 cells, so the
        replacement replaced rather than appended.

    g2b-verify.py <scratchMatrix> <scratchCaptures> [--out <file>]
"""

import argparse
import hashlib
import json
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", ".."))
CAL = os.path.join(ROOT, "packages", "calibration")
WAVE = os.path.join(CAL, "results", "2026-09-06-w21-dark-scheme")
CANON_CAPTURES = os.path.join(CAL, "web-captures")
CANON_MATRIX = os.path.join(CAL, "results", "matrix.json")
W20_MATRIX = "/Users/new/.claude/jobs/5c70e47f/tmp/w21/g2/matrix-before-w21.json"
DARK = ("apple-macos-26.5-1x-dark-standard", "apple-macos-26.5-2x-dark-standard")


def sha(path):
    with open(path, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def cells(matrix_path):
    """Every cell of a result matrix, keyed (profile, tier, scene) — the newest row per key."""
    doc = json.load(open(matrix_path))
    out = {}
    for cell in doc["cells"]:
        key = (cell["key"]["profileKey"], cell["tier"], cell["key"]["sceneId"])
        out[key] = cell
    return out, len(doc["cells"])


def metric(cell, axis, name):
    reading = (cell.get(axis) or {}).get(name)
    return None if reading is None else reading["value"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("matrix")
    ap.add_argument("captures")
    ap.add_argument("--out")
    args = ap.parse_args()
    out = open(args.out, "w") if args.out else sys.stdout

    def p(*a):
        print(*a, file=out)

    p("W21 G2b — the referee over the scratch read")
    p("scratch matrix   ", args.matrix)
    p("scratch captures ", args.captures)
    p()

    # (i) the GPU tier's digests
    p("(i) CONTRACT: the GPU tier is untouched — 1x dark webgpu against g1-digests.txt")
    want = {}
    for line in open(os.path.join(WAVE, "g1", "g1-digests.txt")):
        parts = line.split()
        if len(parts) == 2 and len(parts[0]) == 64 and parts[1].endswith(".png"):
            want[parts[1]] = parts[0]
    checked = same = 0
    for rel, digest in sorted(want.items()):
        if not rel.startswith("apple-macos-26.5-1x-dark-standard/") or "__webgpu.png" not in rel:
            continue
        path = os.path.join(args.captures, rel)
        checked += 1
        if os.path.exists(path) and sha(path) == digest:
            same += 1
        else:
            p("    MOVED", rel)
    p(f"    {same} / {checked} byte-identical to G1's digests")
    p()

    # (ii) contract X3
    p("(ii) CONTRACT X3: every light CSS capture byte-identical to the canonical bed")
    checked = same = 0
    for profile in sorted(os.listdir(CANON_CAPTURES)):
        if "light" not in profile:
            continue
        base = os.path.join(CANON_CAPTURES, profile)
        if not os.path.isdir(base):
            continue
        for scene in sorted(os.listdir(base)):
            png = os.path.join(base, scene, f"{scene}__css.png")
            if not os.path.exists(png):
                continue
            mine = os.path.join(args.captures, profile, scene, f"{scene}__css.png")
            checked += 1
            if os.path.exists(mine) and sha(mine) == sha(png):
                same += 1
            else:
                p("    MOVED", profile, scene)
    p(f"    {same} / {checked} byte-identical")
    p()

    # (iii) the dark CSS rows
    landed, _ = cells(CANON_MATRIX)
    mine, total = cells(args.matrix)
    w20 = cells(W20_MATRIX)[0] if os.path.exists(W20_MATRIX) else {}
    p("(iii) THE DARK CSS ROWS — OKLab ΔE mean, W20 bed / G2 landed / G2b")
    p("    profile  set          scene                                   W20      G2       G2b")
    for profile in DARK:
        for key in sorted(k for k in mine if k[0] == profile and k[1] == "dom"):
            cell = mine[key]
            a = metric(w20.get(key), "perceptual", "oklabDeltaEMean") if key in w20 else None
            b = metric(landed.get(key), "perceptual", "oklabDeltaEMean")
            c = metric(cell, "perceptual", "oklabDeltaEMean")
            f = lambda v: "  -    " if v is None else f"{v:.5f}"
            p(f"    {profile[-17:-9]:8} {cell['fixtureSet']:12} {key[2]:38} {f(a)}  {f(b)}  {f(c)}")
    p()

    p("    the thirteen rows the gate read RED at G2, landed -> G2b")
    rows = [
        ("apple-macos-26.5-1x-dark-standard", "dom", "checkerboard__glass-over-glass__rest", "perceptual", "ssimMean"),
        ("apple-macos-26.5-2x-dark-standard", "dom", "checkerboard__glass-over-glass__rest", "perceptual", "ssimMean"),
        ("apple-macos-26.5-2x-dark-standard", "texture", "checkerboard__glass-over-glass__rest", "shape", "silhouetteIoU"),
        ("apple-macos-26.5-1x-dark-standard", "dom", "checkerboard__capsule-button__rest", "coherence", "interiorLevelRatioGpuOverCss"),
        ("apple-macos-26.5-2x-dark-standard", "dom", "checkerboard__capsule-button__rest", "coherence", "interiorLevelRatioGpuOverCss"),
        ("apple-macos-26.5-1x-dark-standard", "dom", "photo__rrect-md__rest", "coherence", "interiorLevelRatioGpuOverCss"),
        ("apple-macos-26.5-2x-dark-standard", "dom", "photo__rrect-md__rest", "coherence", "interiorLevelRatioGpuOverCss"),
        ("apple-macos-26.5-1x-dark-standard", "dom", "photo__rrect-lg__rest", "coherence", "interiorLevelRatioGpuOverCss"),
        ("apple-macos-26.5-2x-dark-standard", "dom", "photo__rrect-lg__rest", "coherence", "interiorLevelRatioGpuOverCss"),
        ("apple-macos-26.5-1x-dark-standard", "dom", "photo__capsule-button__rest", "coherence", "interiorLevelRatioGpuOverCss"),
        ("apple-macos-26.5-2x-dark-standard", "dom", "photo__capsule-button__rest", "coherence", "interiorLevelRatioGpuOverCss"),
        ("apple-macos-26.5-1x-dark-standard", "dom", "checkerboard__glass-over-glass__rest", "coherence", "crossTierOklabDeltaEMean"),
        ("apple-macos-26.5-2x-dark-standard", "dom", "checkerboard__glass-over-glass__rest", "coherence", "crossTierOklabDeltaEMean"),
    ]
    for profile, tier, scene, axis, name in rows:
        key = (profile, tier, scene)
        b = metric(landed.get(key), axis, name)
        c = metric(mine.get(key), axis, name)
        f = lambda v: "   -    " if v is None else f"{v:.5f}"
        p(f"    {profile[-17:-9]:8} {tier:8} {scene:38} {name:28} {f(b)} -> {f(c)}")
    p()

    # every dark dom cell's coherence rows, so the predicate's population is visible
    p("    every dark dom cell: interior level ratio and cross-tier ΔE, landed -> G2b")
    for profile in DARK:
        for key in sorted(k for k in mine if k[0] == profile and k[1] == "dom"):
            f = lambda v: "   -   " if v is None else f"{v:.4f}"
            p(
                f"    {profile[-17:-9]:8} {key[2]:38}"
                f" ratio {f(metric(landed.get(key),'coherence','interiorLevelRatioGpuOverCss'))}"
                f" -> {f(metric(mine[key],'coherence','interiorLevelRatioGpuOverCss'))}"
                f" | ΔE {f(metric(landed.get(key),'coherence','crossTierOklabDeltaEMean'))}"
                f" -> {f(metric(mine[key],'coherence','crossTierOklabDeltaEMean'))}"
            )
    p()

    # (iv) the bed's shape
    p("(iv) THE BED'S SHAPE")
    p(f"    scratch matrix rows {total}, distinct cells {len(mine)}; canonical {len(landed)}")
    if total != len(mine):
        p("    APPENDED: a key was written twice — reduce to the newest row per key before gating.")


if __name__ == "__main__":
    main()
