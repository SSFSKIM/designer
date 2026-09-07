"""W21 G2c — the referee over the landed canonical bed (W21 Decision Log 4 (e)).

Five questions, each answered against a file rather than against a recollection:

  (i)   **The measurement Decision Log 4 (a) makes of itself.** Every LIGHT capture on the CSS
        tier, all four light profiles at both scales, byte-identical to the bed before this
        landing. Reported against two befores, because they differ from each other by one cell for
        a reason G2 recorded: the W20 bed (`web-captures-before-w21/`, the ruling's named
        reference) and the bed G2 landed (`web-captures-g2-landed/`, copied by `g2c-rebuild.sh`).
        A light capture that moves against BOTH voids the ruling.
  (ii)  The GPU tier untouched: the dark captures against `g1/g1-digests.txt` and every GPU
        capture against the G2-landed copy, byte for byte. Nothing re-rendered them; this proves
        nothing moved them either.
  (iii) What the dark CSS rows did — every cell's OKLab ΔE mean against the W20 bed and against
        G2's landing, and the thirteen rows the gate read RED at G2.
  (iv)  Which FORM each dark surface drew, off the capture's own report — the honesty core, since
        Decision Log 4 (a) decides it per surface.
  (v)   The bed's shape: 229 cells on the same keys, so the runs replaced rather than appended.

    g2c-verify.py [--out <file>]
"""

import argparse
import hashlib
import json
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", ".."))
CAL = os.path.join(ROOT, "packages", "calibration")
WAVE = os.path.join(CAL, "results", "2026-09-06-w21-dark-scheme")
CAPTURES = os.path.join(CAL, "web-captures")
MATRIX = os.path.join(CAL, "results", "matrix.json")
SCRATCH = "/Users/new/.claude/jobs/5c70e47f/tmp/w21"
W20_CAPTURES = os.path.join(SCRATCH, "g2", "web-captures-before-w21")
W20_MATRIX = os.path.join(SCRATCH, "g2", "matrix-before-w21.json")
G2_CAPTURES = os.path.join(SCRATCH, "g2c", "web-captures-g2-landed")
G2_MATRIX = os.path.join(SCRATCH, "g2c", "matrix-g2-landed.json")
DARK = ("apple-macos-26.5-1x-dark-standard", "apple-macos-26.5-2x-dark-standard")

THIRTEEN = [
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


def sha(path):
    with open(path, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def cells(path):
    doc = json.load(open(path))
    out = {}
    for cell in doc["cells"]:
        out[(cell["key"]["profileKey"], cell["tier"], cell["key"]["sceneId"])] = cell
    return out, len(doc["cells"])


def metric(cell, axis, name):
    if cell is None:
        return None
    reading = (cell.get(axis) or {}).get(name)
    return None if reading is None else reading["value"]


def walk(root, tier):
    """(relative path, absolute path) for every capture of one tier under a capture tree."""
    for profile in sorted(os.listdir(root)):
        base = os.path.join(root, profile)
        if not os.path.isdir(base):
            continue
        for scene in sorted(os.listdir(base)):
            png = os.path.join(base, scene, f"{scene}__{tier}.png")
            if os.path.exists(png):
                yield f"{profile}/{scene}/{scene}__{tier}.png", png


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out")
    args = ap.parse_args()
    out = open(args.out, "w") if args.out else sys.stdout

    def p(*a):
        print(*a, file=out)

    p("W21 G2c — the referee over the landed canonical bed")
    p()

    # (i) contract X3, the ruling's own measurement
    p("(i) THE RULING'S MEASUREMENT (Decision Log 4 (a)): every light CSS capture byte-identical")
    for label, before in (("W20 bed", W20_CAPTURES), ("G2 landed", G2_CAPTURES)):
        checked = same = 0
        moved = []
        for rel, png in walk(CAPTURES, "css"):
            if "light" not in rel.split("/")[0]:
                continue
            other = os.path.join(before, rel)
            checked += 1
            if os.path.exists(other) and sha(other) == sha(png):
                same += 1
            else:
                moved.append(rel)
        p(f"    against the {label}: {same} / {checked} byte-identical")
        for rel in moved:
            p(f"        MOVED {rel}")
    p()

    # (ii) the GPU tier
    p("(ii) THE GPU TIER UNTOUCHED")
    want = {}
    for line in open(os.path.join(WAVE, "g1", "g1-digests.txt")):
        parts = line.split()
        if len(parts) == 2 and len(parts[0]) == 64 and parts[1].endswith("__webgpu.png"):
            want[parts[1]] = parts[0]
    same = sum(1 for rel, d in want.items()
               if os.path.exists(os.path.join(CAPTURES, rel)) and sha(os.path.join(CAPTURES, rel)) == d)
    p(f"    dark, against g1-digests.txt: {same} / {len(want)} byte-identical")
    checked = identical = 0
    for rel, png in walk(CAPTURES, "webgpu"):
        other = os.path.join(G2_CAPTURES, rel)
        checked += 1
        if os.path.exists(other) and sha(other) == sha(png):
            identical += 1
        else:
            p(f"        MOVED {rel}")
    p(f"    every GPU capture, against the G2-landed copy: {identical} / {checked} byte-identical")
    p()

    # (iii) the dark CSS rows
    landed, _ = cells(MATRIX)
    g2 = cells(G2_MATRIX)[0] if os.path.exists(G2_MATRIX) else {}
    w20 = cells(W20_MATRIX)[0] if os.path.exists(W20_MATRIX) else {}
    p("(iii) THE DARK CSS ROWS — OKLab ΔE mean against Apple: W20 bed / G2 / G2c")
    p("    profile  set          scene                                       W20      G2       G2c")
    for profile in DARK:
        total = {}
        for key in sorted(k for k in landed if k[0] == profile and k[1] == "dom"):
            cell = landed[key]
            a = metric(w20.get(key), "perceptual", "oklabDeltaEMean")
            b = metric(g2.get(key), "perceptual", "oklabDeltaEMean")
            c = metric(cell, "perceptual", "oklabDeltaEMean")
            f = lambda v: "  -    " if v is None else f"{v:.5f}"
            p(f"    {profile[-17:-9]:8} {cell['fixtureSet']:12} {key[2]:42} {f(a)}  {f(b)}  {f(c)}")
            total.setdefault(cell["fixtureSet"], []).append((a, b, c))
        for fixture_set, rows in sorted(total.items()):
            mean = lambda i: sum(r[i] for r in rows if r[i] is not None) / max(
                1, sum(1 for r in rows if r[i] is not None))
            p(f"    {profile[-17:-9]:8} {fixture_set:12} {'MEAN of ' + str(len(rows)) + ' cells':42}"
              f" {mean(0):.5f}  {mean(1):.5f}  {mean(2):.5f}")
    p()

    p("    the thirteen rows the gate read RED at G2, G2 -> G2c")
    for profile, tier, scene, axis, name in THIRTEEN:
        key = (profile, tier, scene)
        b = metric(g2.get(key), axis, name)
        c = metric(landed.get(key), axis, name)
        f = lambda v: "   -    " if v is None else f"{v:.5f}"
        p(f"    {profile[-17:-9]:8} {tier:8} {scene:38} {name:28} {f(b)} -> {f(c)}")
    p()

    p("    every dark dom cell: interior level ratio and cross-tier ΔE, G2 -> G2c")
    for profile in DARK:
        for key in sorted(k for k in landed if k[0] == profile and k[1] == "dom"):
            f = lambda v: "   -   " if v is None else f"{v:.4f}"
            p(
                f"    {profile[-17:-9]:8} {key[2]:42}"
                f" ratio {f(metric(g2.get(key),'coherence','interiorLevelRatioGpuOverCss'))}"
                f" -> {f(metric(landed[key],'coherence','interiorLevelRatioGpuOverCss'))}"
                f" | ΔE {f(metric(g2.get(key),'coherence','crossTierOklabDeltaEMean'))}"
                f" -> {f(metric(landed[key],'coherence','crossTierOklabDeltaEMean'))}"
            )
    p()

    # (iv) the form each surface drew, off the capture's own report
    p("(iv) WHICH FORM DREW (the capture's own `cssTint`, per group)")
    for profile in sorted(os.listdir(CAPTURES)):
        base = os.path.join(CAPTURES, profile)
        if not os.path.isdir(base):
            continue
        forms = {}
        for scene in sorted(os.listdir(base)):
            report = os.path.join(base, scene, "report__css.json")
            if not os.path.exists(report):
                continue
            doc = json.load(open(report))
            forms[scene] = sorted({g["state"].get("cssTint") for g in doc["page"]["groups"]})
        encoded = [s for s, f in forms.items() if "encoded" in f]
        p(f"    {profile}: {len(forms)} cells, {len(encoded)} encoded")
        for scene in encoded:
            p(f"        encoded  {scene}")
    p()

    # (v) the bed's shape
    p("(v) THE BED'S SHAPE")
    rows = json.load(open(MATRIX))
    p(f"    matrix rows {len(rows['cells'])}, distinct cells {len(landed)}; G2 landed {len(g2)}")
    if len(rows["cells"]) != len(landed):
        p("    APPENDED: a key was written twice.")
    if set(landed) != set(g2):
        p(f"    KEYS MOVED: +{sorted(set(landed) - set(g2))} -{sorted(set(g2) - set(landed))}")


if __name__ == "__main__":
    main()
