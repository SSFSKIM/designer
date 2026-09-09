"""W25 G2 — the OKLab ΔE per cell per rung: the thin-invariance read and the bed's cost.

WHAT THIS READS. The reference fixtures for the canonical 1x beds and the two probe grids
(read-only), and the rungs' web captures under the scratch root. It writes only the text file it is
told to.

THE METRIC IS THE MATRIX's. `packages/calibration/src/color.ts:75` `linearRgbToOklab` and `:101`
`oklabDistance` restated term for term, averaged over the declared component region — the same
region `component-region.ts` places and the same distance `oklabDeltaEMean` reports. It is restated
in Python rather than called because the ladder's readers are Python and a second language in the
middle of one read is a second chance to disagree; the coefficients are copied, not re-derived, and
a value read here on the canonical bed reproduces the committed matrix's to the digit it prints.

WHAT IT IS FOR. X5: the thin capsule does not move, and a thin cell (span ≤ 44) whose ΔE moves by
more than 0.001 at any rung stops the ladder. That is a statement about EVERY thin cell of the bed
at every rung, so it is measured on all of them and not argued from the shape of the formula — the
shape of the formula is the unit test's job.

Usage: deltae.py --rung r0 --rung rA … [--scratch DIR] [--out FILE]
"""

import argparse
import json
import os
import sys

import numpy as np
from PIL import Image

G0 = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "g0")
sys.path.insert(0, G0)
import w25lib as L  # noqa: E402

SCRATCH_DEFAULT = "/Users/new/.claude/jobs/5c70e47f/tmp/w25/g2"
WITHDRAWN = {("w21", "dark-solid__rrect-sm__rest"), ("w21", "light-solid__rrect-sm__rest")}
BEDS = {
    "w9": (os.path.join(L.RESULTS, "2026-09-02-w9-probe", "apple-macos-26.5-1x-light-standard"),
           os.path.join(L.REPO, "apps", "reference-apple", "scenes-w9-probe.json")),
    "w21": (os.path.join(L.RESULTS, "2026-09-06-w21-dark-scheme", "probe",
                         "apple-macos-26.5-1x-dark-standard"),
            os.path.join(L.REPO, "apps", "reference-apple", "scenes-w21-probe.json")),
    "canon-light": (os.path.join(L.FIXTURES, "apple-macos-26.5-1x-light-standard"), L.SCENES),
    "canon-dark": (os.path.join(L.FIXTURES, "apple-macos-26.5-1x-dark-standard"), L.SCENES),
}
THIN_SPAN = 44.0


def oklab(path):
    """The image in OKLab, per pixel — `color.ts:75`'s coefficients exactly."""
    rgb = np.asarray(Image.open(path).convert("RGB"), dtype=np.float64) / 255.0
    c = np.where(rgb <= 0.04045, rgb / 12.92, ((rgb + 0.055) / 1.055) ** 2.4)
    r, g, b = c[..., 0], c[..., 1], c[..., 2]
    l = np.cbrt(0.4122214708 * r + 0.5363325363 * g + 0.0514459929 * b)
    m = np.cbrt(0.2119034982 * r + 0.6806995451 * g + 0.1073969566 * b)
    s = np.cbrt(0.0883024619 * r + 0.2817188376 * g + 0.6299787005 * b)
    return np.stack([
        0.2104542553 * l + 0.7936177850 * m - 0.0040720468 * s,
        1.9779984951 * l - 2.4285922050 * m + 0.4505937099 * s,
        0.0259040371 * l + 0.7827717662 * m - 0.8086757660 * s,
    ], axis=-1)


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--rung", action="append", required=True)
    ap.add_argument("--scratch", default=SCRATCH_DEFAULT)
    ap.add_argument("--out", default=None)
    args = ap.parse_args(argv)

    shape = (200, 320)
    table = {}
    for bed, (native_dir, scenes_path) in BEDS.items():
        matrix = json.load(open(scenes_path))
        comps = matrix["components"]
        holdout = set(matrix.get("split", {}).get("holdout", []))
        for scene in matrix["scenes"]:
            sid = scene["id"]
            if scene.get("state") != "rest" or "tint" in scene or (bed, sid) in WITHDRAWN:
                continue
            if sid in holdout or scene["component"] not in comps:
                continue
            native = os.path.join(native_dir, f"{sid}.png")
            if not os.path.exists(native):
                continue
            cell = L.Cell(scene["component"], comps)
            mask = cell.body_mask(1.0, shape, 0.0)
            ref = None
            for rung in args.rung:
                web = os.path.join(args.scratch, rung, bed, sid, f"{sid}__webgpu.png")
                if not os.path.exists(web):
                    continue
                if ref is None:
                    ref = oklab(native)
                d = np.linalg.norm(oklab(web) - ref, axis=-1)
                table.setdefault((bed, sid, float(cell.short)), {})[rung] = float(d[mask].mean())

    out = open(args.out, "w") if args.out else sys.stdout
    w = out.write
    w("W25 G2 — OKLab ΔE mean per cell per rung, and X5's thin-invariance read\n")
    w("=" * 100 + "\n\n")
    w("ΔE is the mean OKLab distance between the rung's WebGPU capture and the reference fixture\n")
    w("over the declared component region — the matrix's own `oklabDeltaEMean`, restated. The\n")
    w("`Δ vs r0` columns are what X5 reads: a THIN cell (span ≤ 44) moved by more than 0.001 at\n")
    w("any rung stops the ladder.\n\n")
    rungs = args.rung
    base = rungs[0]
    w(f"{'bed':12} {'scene':40} {'span':>5} " + "".join(f"{r:>9}" for r in rungs)
      + "".join(f"{'Δ ' + r:>10}" for r in rungs[1:]) + "\n")
    worst_thin = (0.0, None)
    for (bed, sid, span) in sorted(table):
        row = table[(bed, sid, span)]
        if base not in row:
            continue
        line = (f"{bed:12} {sid:40} {span:5.0f} "
                + "".join(f"{row.get(r, float('nan')):9.5f}" for r in rungs)
                + "".join(f"{row.get(r, float('nan')) - row[base]:+10.5f}" for r in rungs[1:]))
        thin = span <= THIN_SPAN
        w(line + ("   THIN" if thin else "") + "\n")
        if thin:
            for r in rungs[1:]:
                if r in row and abs(row[r] - row[base]) > worst_thin[0]:
                    worst_thin = (abs(row[r] - row[base]), (bed, sid, r))
    w("\n")
    w(f"worst thin-cell movement over all rungs: {worst_thin[0]:.6f}"
      + (f"  at {worst_thin[1]}" if worst_thin[1] else "") + "\n")
    w(f"X5's stop is 0.001 — {'PASS' if worst_thin[0] <= 0.001 else 'STOP'}\n")
    for group, keep in (("all four 1x beds", lambda k: True),
                       ("the canonical 1x beds only", lambda k: k[0].startswith("canon")),
                       ("the two probe grids only", lambda k: not k[0].startswith("canon")),
                       ("thick cells only (span > 44)", lambda k: k[2] > THIN_SPAN),
                       ("thin cells only (span <= 44)", lambda k: k[2] <= THIN_SPAN)):
        w(f"\n  -- {group} --\n")
        for r in rungs:
            vals = [row[r] for k, row in table.items() if keep(k) and r in row and base in row]
            b = [row[base] for k, row in table.items() if keep(k) and r in row and base in row]
            if vals:
                w(f"  rung {r:4}: mean ΔE over {len(vals):3d} cells {np.mean(vals):.5f} "
                  f"({np.mean(vals) - np.mean(b):+.5f} against {base})\n")
    if args.out:
        out.close()
        print(f"-> {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
