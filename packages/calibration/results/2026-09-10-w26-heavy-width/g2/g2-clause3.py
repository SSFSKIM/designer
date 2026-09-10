"""W26 G2 — W25 clause 3, the nested pane's base, read ONCE at the holdout read.

`checkerboard__glass-over-glass__rest` is the only instance of `glass-over-glass` on this bed and
the split puts it in the HOLDOUT (claims §5.122 §6c). X3 reads the holdout once, at the declaring
child's dry run, so this clause has no non-holdout instance at any rung and belongs to this file and
to nothing else in the wave: G1c could not read it, G1b was a spike that only validated an
instrument on it, and G3 reproduces bytes rather than re-reading.

THE INSTRUMENTS ARE W25 G0's AND ARE NOT RE-DERIVED. `w25lib` is imported unedited and its reader C
— the σ-match, an affine-rescaled Gaussian sweep against the backdrop's own raster, with the gain
and standard-deviation guards that keep it from fitting quantisation dither — is the clause's own
(`--reader C`, W25 G3's reading), with reader B, the edge spread, printed beside it because W25
quoted both. The region is `widths.py`'s: the stack's BASE box eroded 6 CSS px with the overlay's
box dilated 6 px cut out of it, which is W22's stack geometry.

Reader C's validated identification bound on a 16 CSS px checkerboard is 4 device px at 1x and 8 at
2x, so a reading above it is a LOWER BOUND and is flagged. W25 G3 recorded both scales past the
bound at 2x, and that is expected to be unchanged: this wave narrows the width, it does not give the
reader more pitch to work with.

    g2-clause3.py --control <captures dir> --candidate <captures dir> [--out FILE]
"""

import argparse
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(HERE, "..", "..",
                                                "2026-09-09-w25-thick-span-composite", "g0")))
import w25lib as L  # noqa: E402

SCENE = "checkerboard__glass-over-glass__rest"
COMPONENT = "glass-over-glass"
# `validate.txt`'s bound for reader C on a 16 CSS px checkerboard, in device px.
BOUND_C = {1.0: 4.0, 2.0: 8.0}
BOUND_B = {1.0: 2.0, 2.0: 4.0}


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--control", required=True)
    ap.add_argument("--candidate", required=True)
    ap.add_argument("--out", default=os.path.join(HERE, "clause3.txt"))
    args = ap.parse_args(argv)

    lines = []

    def emit(text=""):
        lines.append(text)
        print(text, flush=True)

    comps = L.load_components()
    cell = L.Cell(COMPONENT, comps)

    emit("W26 G2 — W25 clause 3: the nested pane's base, at the wave's one holdout read")
    emit("=" * 104)
    emit("  σ in DEVICE px. `>bound` marks a reading past the reader's validated identification")
    emit("  bound on this backdrop — a lower bound and not a reading (W25 G0 `validate.txt`).")
    emit()
    emit(f"  {'profile':40s} {'tier':7s} {'source':10s} {'σ C':>8s} {'flag':>7s} "
         f"{'resid C':>8s} {'σ B':>8s} {'flag':>7s}")

    for key, (profile, scale, scheme) in sorted(L.PROFILES.items()):
        shape = (int(200 * scale), int(320 * scale))
        native = L.native_path(profile, SCENE)
        if not os.path.exists(native):
            continue
        bg = L.background_for("checkerboard", scale, shape)
        sources = [("native", "—", native)]
        for tier in ("webgpu", "css"):
            sources.append((tier, "0.14.0", L.web_path(profile, SCENE, tier, root=args.control)))
            sources.append((tier, "candidate", L.web_path(profile, SCENE, tier,
                                                          root=args.candidate)))
        for tier, when, path in sources:
            if not os.path.exists(path):
                emit(f"  {profile:40s} {tier:7s} {when:10s}   (no capture)")
                continue
            lum = L.luma_of(path)
            if lum.shape != shape:
                emit(f"  {profile:40s} {tier:7s} {when:10s}   (wrong raster)")
                continue
            mask = cell.body_mask(scale, lum.shape, 6.0)
            c = L.sigma_match(lum, bg, mask, top=64.0, ref_key=("checkerboard", scale))
            b = L.read_edge_spread(lum, bg, mask, scale, sigma_ceiling_dev=64.0)
            fc = ">bound" if (np.isfinite(c["sigmaDev"])
                              and c["sigmaDev"] > BOUND_C[scale]) else ""
            fb = ">bound" if (b["n"] and np.isfinite(b["sigmaDev"])
                              and b["sigmaDev"] > BOUND_B[scale]) else ""
            sc = c["sigmaDev"]
            sb = b["sigmaDev"] if b["n"] else float("nan")
            emit(f"  {profile:40s} {tier:7s} {when:10s} {sc:8.2f} {fc:>7s} "
                 f"{c['rmsRel']:8.4f} {sb:8.2f} {fb:>7s}")

    emit()
    emit("  Clause 3 asks the base's σ-match within 15 % of the reference's at both scales in both")
    emit("  schemes, neither side saturated. Read the native row against the two web rows of the")
    emit("  same profile and tier; a `>bound` on either side means the clause cannot be answered on")
    emit("  this bed at that scale, which is itself the reading W25 recorded.")

    with open(args.out, "w") as handle:
        handle.write("\n".join(lines) + "\n")
    print(f"\n-> {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
