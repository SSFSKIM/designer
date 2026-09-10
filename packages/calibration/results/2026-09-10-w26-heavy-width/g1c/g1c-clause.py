"""W26 G1c — clause 5: what `sizeScatterGainFar2x` still grades, and W25's clauses 3 and 4 read.

WHAT `sizeScatterGainFar2x` STILL GRADES, from the shader and then from captures. `wgsl/optics.ts`
takes the deep sample as `textureSampleLevel(backdropChain, refractedUv, scatterLod)` and then,
where `heavyTap.x > 0.5`, OVERWRITES it with the heavy texture. `scatterLod` is the only consumer
of `gainEff`, and `gainEff` is the only consumer of `sizeScatterGainMax`, `sizeScatterGainMax2x`
and `sizeScatterGainFar2x`. `heavyTap.x` is `pyramid?.heavy !== undefined`, and the pyramid builds
the heavy texture whenever `heavySigmaCss > 0`. So at any candidate naming a heavy width at both
anchors, the three gain constants grade NOTHING on any group whose source has a pyramid — which on
this bed is every group. That is arithmetic; `--gain-silence` measures it, by rendering the
candidate twice with `sizeScatterGainFar2x` at 9.9 and at 4.8 (which flattens the span grading
entirely) and comparing the two captures byte for byte.

W25 CLAUSE 3 — the nested pane — CANNOT BE READ BY THIS CHILD. `glass-over-glass` appears on this
bed over exactly one backdrop, `checkerboard__glass-over-glass__rest`, and that scene is in the
HOLDOUT. X3 gives the holdout to the declaring child's one dry run, so reading it here to check a
clause would spend it on a check. The clause is therefore G2's at the dry run, and that it has no
non-holdout instance at all is itself worth recording.

W25 CLAUSE 4 — the collapsed dot — CAN. `impulse__capsule-button__rest` is a validation scene.
Reader A on it returns the two-component kernel of the transmitted dot; the FWHM quoted is that of
the composed kernel by half maximum, in CSS px, native beside web.

    g1c-clause.py [--rungs c0b,d9b] [--gain-silence RUNG_A RUNG_B] [--out FILE]
"""

import argparse
import importlib.util
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
G1B = os.path.abspath(os.path.join(HERE, "..", "g1b"))
sys.path.insert(0, G1B)
import w26blib as E  # noqa: E402
import w25lib as L  # noqa: E402

SCRATCH = "/Users/new/.claude/jobs/5c70e47f/tmp/w26/g1c"
CAPSULE = "impulse__capsule-button__rest"


def fwhm_css(sharp, s1, heavy, s2, scale):
    """The composed two-component kernel's full width at half maximum, in CSS px.

    Reader A returns two Gaussians and their amplitudes; the half maximum of their SUM is not a
    property of either, so it is found on the composed profile rather than quoted from a component.
    """
    r = np.linspace(0.0, 200.0, 20001)
    k = sharp * np.exp(-0.5 * (r / max(s1, 1e-9)) ** 2) + heavy * np.exp(-0.5 * (r / max(s2, 1e-9)) ** 2)
    peak = float(k[0])
    if peak <= 0:
        return float("nan")
    below = np.nonzero(k <= peak / 2.0)[0]
    if not below.size:
        return float("nan")
    i = int(below[0])
    half = r[i - 1] + (k[i - 1] - peak / 2.0) / max(k[i - 1] - k[i], 1e-300) * (r[i] - r[i - 1])
    return 2.0 * half / scale


def read_capsule(path, scale, comps):
    if not os.path.exists(path):
        return None
    shape = (int(200 * scale), int(320 * scale))
    lum = L.luma_of(path)
    if lum.shape != shape:
        return None
    bg = L.background_for("impulse", scale, shape)
    cell = L.Cell("capsule-button", comps)
    rows = L.read_psf_cell(lum, bg, cell, scale, half_css=30.0)
    if not rows:
        return None
    return {
        "sharp": float(np.median([r["sharpSigmaDev"] for r in rows])),
        "heavy": float(np.median([r["heavySigmaDev"] for r in rows])),
        "share": float(np.median([r["heavyShare"] for r in rows])),
        "peak": float(np.median([r["sharpA"] + r["heavyA"] for r in rows])),
        "fwhm": float(np.median([
            fwhm_css(r["sharpA"], r["sharpSigmaDev"], r["heavyA"], r["heavySigmaDev"], scale)
            for r in rows])),
        "n": len(rows),
    }


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--rungs", default="c0b,d9b")
    ap.add_argument("--gain-silence", nargs=2, default=None)
    ap.add_argument("--out", default=os.path.join(HERE, "clause.txt"))
    args = ap.parse_args(argv)
    comps = L.load_components()
    lines = []
    e = lines.append
    e("W26 G1c — clause 5: the gain's silence, and W25's clauses 3 and 4")
    e("=" * 100)
    e("")

    e("### W25 clause 4 — the collapsed dot through `impulse__capsule-button__rest` (validation)")
    e("")
    e("Reader A, W25 G0's own instrument, unedited. FWHM in CSS px of the composed kernel by half")
    e("maximum; `peak` is the fitted amplitude the clause asks to be held.")
    e("")
    e(f"  {'source':>16} {'scale':>5} {'FWHM css':>9} {'sharp':>7} {'heavy':>7} {'share':>6}"
      f" {'peak':>8} {'n':>3}")
    for scale, pkey in ((1.0, "1x-light"), (2.0, "2x-light")):
        profile, _, _ = L.PROFILES[pkey]
        native = read_capsule(L.native_path(profile, CAPSULE), scale, comps)
        if native:
            e(f"  {'reference':>16} {scale:5.0f} {native['fwhm']:9.3f} {native['sharp']:7.3f}"
              f" {native['heavy']:7.3f} {native['share']:6.3f} {native['peak']:8.4f}"
              f" {native['n']:3d}")
        for rung in args.rungs.split(","):
            path = os.path.join(SCRATCH, rung, "web-captures", profile, CAPSULE,
                                f"{CAPSULE}__webgpu.png")
            web = read_capsule(path, scale, comps)
            if web:
                e(f"  {rung:>16} {scale:5.0f} {web['fwhm']:9.3f} {web['sharp']:7.3f}"
                  f" {web['heavy']:7.3f} {web['share']:6.3f} {web['peak']:8.4f} {web['n']:3d}")
    e("")

    e("### W25 clause 3 — the nested pane: NOT READ, and it cannot be")
    e("")
    e("`glass-over-glass` has exactly one scene on this bed, `checkerboard__glass-over-glass__rest`,")
    e("and the split puts it in the HOLDOUT. X3 reads the holdout once, at the declaring child's dry")
    e("run, so this child does not open it. The clause has no non-holdout instance to be checked on")
    e("at any rung, which is a property of the bed rather than of this candidate and is recorded as")
    e("one: a clause that can only be read by spending the holdout cannot gate a ladder.")
    e("")

    if args.gain_silence:
        a, b = args.gain_silence
        e("### What `sizeScatterGainFar2x` still grades")
        e("")
        e("Two captures of the SAME candidate width, differing only in `sizeScatterGainFar2x`")
        e(f"(`{a}` at the committed 9.9, `{b}` flattened to `sizeScatterGainMax2x` = 4.8). Where the")
        e("heavy texture is bound the constant grades nothing and the two are byte-identical.")
        e("")
        import hashlib
        for profile in ("apple-macos-26.5-1x-light-standard", "apple-macos-26.5-2x-light-standard",
                        "apple-macos-26.5-1x-dark-standard", "apple-macos-26.5-2x-dark-standard"):
            ra = os.path.join(SCRATCH, a, "web-captures", profile)
            rb = os.path.join(SCRATCH, b, "web-captures", profile)
            if not (os.path.isdir(ra) and os.path.isdir(rb)):
                continue
            same = diff = 0
            movers = []
            for scene in sorted(os.listdir(ra)):
                pa = os.path.join(ra, scene, f"{scene}__webgpu.png")
                pb = os.path.join(rb, scene, f"{scene}__webgpu.png")
                if not (os.path.exists(pa) and os.path.exists(pb)):
                    continue
                da = hashlib.sha256(open(pa, "rb").read()).hexdigest()
                db = hashlib.sha256(open(pb, "rb").read()).hexdigest()
                if da == db:
                    same += 1
                else:
                    diff += 1
                    movers.append(scene)
            e(f"   {profile:>40}  {same:3d} identical  "
              + ("SILENT" if diff == 0 else f"{diff} MOVED: " + ", ".join(movers[:5])))
        e("")
    text = "\n".join(lines)
    print(text)
    open(args.out, "w").write(text + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
