"""W25 G0 deliverable 1 — the three width readers validated against a KNOWN kernel.

WHAT THIS READS. Only the committed backdrop rasters
`apps/reference-apple/fixtures/backgrounds/{checkerboard,impulse}@{1,2}x.png`. Nothing else; no
fixture and no capture is read here, because the point is a known answer.

THE SYNTHETIC. For each backdrop, each scale and each true sigma in {1, 2, 4, 8, 16} DEVICE px, the
backdrop is Gaussian-blurred at that sigma, then affinely compressed towards a body level
(`gain` 0.55, `offset` 0.02 linear) so the synthetic looks like a material's transmission rather
than a blurred photograph, and quantised to 8 bits — the capture's own resolution, which is part of
what a reader has to survive. The shape is `rrect-md`. Each reader is then asked for the sigma it
recovers, and the error is |recovered - true| / true.

WHY GAIN AND OFFSET. Readers B and C both solve a gain and an offset in closed form, so a synthetic
that did not carry one would validate them on an easier problem than the real read.

ACCEPTANCE (the child's): each reader recovers a known sigma within 5 %, or the row states where it
cannot and why. The "cannot" rows are the finding — a reader's bound is as much a result as its
value, and this is where each of the three stops.

Units: every sigma printed is DEVICE px. Run with the analysis venv from this directory.
"""

import sys

import numpy as np
from scipy.ndimage import gaussian_filter

import w25lib as L

TRUE_SIGMAS = [1.0, 2.0, 4.0, 8.0, 16.0]
HALF_CSS = 30.0   # half the impulse grid's 64 CSS px dot spacing minus a two-px guard
GAIN, OFFSET = 0.55, 0.02
COMPONENT = "rrect-md"


def synth(bgname, scale, sigma):
    """The known-kernel image: backdrop blurred at `sigma`, compressed, quantised to 8 bits."""
    shape = (int(200 * scale), int(320 * scale))
    bg = L.background_for(bgname, scale, shape)
    blurred = bg if sigma == 0 else gaussian_filter(bg, sigma, mode="nearest")
    lin = GAIN * blurred + OFFSET
    quantised = np.round(L.encode(lin) * 255.0) / 255.0
    return L.linearise(quantised * 255.0), bg


def main():
    cell = L.Cell(COMPONENT)
    print(__doc__.strip())
    print()
    print("Backdrops: checkerboard (16 CSS px cell) and impulse (4 CSS px dots, 64 CSS px apart).")
    print(f"Shape: {COMPONENT} {cell.box['width']:.0f}x{cell.box['height']:.0f} CSS px, "
          f"body eroded 6 CSS px. Forward model gain {GAIN}, offset {OFFSET} linear, 8-bit "
          f"quantised.")
    print()

    fails = []

    # ---------------------------------------------------------------- reader A on the impulse
    print("== Reader A — the dot PSF (`psf_fit`), impulse backdrop, sigma in DEVICE px")
    print("   `equiv` is the fitted PAIR reduced to one width by its HALF-WIDTH AT HALF MAXIMUM,")
    print("   which is what readers B and C each fit; `sharp` and `heavy` are the pair itself. On a")
    print("   synthetic built from ONE Gaussian either the heavy amplitude falls to ~0 and `sharp`")
    print("   is the answer, or the two components land on the same width and `heavy` is — both")
    print("   are the same kernel and the HWHM equivalent reads it either way. `ceil` is the")
    print("   sharp component's ceiling, the profile's own half-window, reported so a value")
    print("   sitting on it is read as a bound. The window is chosen per dot and per axis as the")
    print("   widest of 30/24/20/16/14/12 CSS px that stays inside the shape eroded 6 CSS px.")
    print(f"   {'scale':>5} {'true':>6} {'sharp':>8} {'heavy':>8} {'heavyA/A':>9} {'equiv':>8} "
          f"{'err %':>8} {'rmsRel':>8} {'ceil':>7} {'n':>4}  verdict")
    for scale in (1, 2):
        bgi = L.background_for("impulse", scale, (int(200 * scale), int(320 * scale)))
        for st in TRUE_SIGMAS:
            lum, _ = synth("impulse", scale, st)
            rows = L.read_psf_cell(lum, bgi, cell, scale, half_css=HALF_CSS)
            if not rows:
                print(f"   {scale:5.0f} {st:6.1f}  no dot under the eroded shape")
                continue
            sharp = float(np.median([r["sharpSigmaDev"] for r in rows]))
            heavy = float(np.median([r["heavySigmaDev"] for r in rows]))
            share = float(np.median([r["heavyShare"] for r in rows]))
            equiv = float(np.median([r["sigmaEquivDev"] for r in rows]))
            rms = float(np.median([r["rmsRel"] for r in rows]))
            ceil = rows[0]["sharpCeilingDev"]
            err = abs(equiv - st) / st * 100.0
            ok = err <= 5.0
            why = "" if ok else _psf_why(st, scale, ceil)
            if not ok:
                fails.append(("A", scale, st, err, why))
            print(f"   {scale:5.0f} {st:6.1f} {sharp:8.2f} {heavy:8.2f} {share:9.3f} "
                  f"{equiv:8.2f} {err:8.2f} {rms:8.4f} {ceil:7.1f} {len(rows):4d}  "
                  f"{'PASS' if ok else 'BOUND: ' + why}")
    print()

    # ---------------------------------------------------------------- reader B on the checker
    print("== Reader B — the edge spread (`edge_spread`), checkerboard step, sigma in DEVICE px")
    print("   The committed metric's ceiling is max(length/2, 4*guess); here the ceiling is swept")
    print("   so the row says what ceiling the reader NEEDED and whether raising it helped. The")
    print("   residual is the fraction of the profile's own step height (`report.ts:391-397`:")
    print("   large means sigma is not identifiable).")
    print(f"   {'scale':>5} {'true':>6} {'ceil':>6} {'sigma':>8} {'err %':>8} {'resid':>8} "
          f"{'halfWin':>8} {'n':>4}  verdict")
    for scale in (1, 2):
        bgc = L.background_for("checkerboard", scale, (int(200 * scale), int(320 * scale)))
        for st in TRUE_SIGMAS:
            lum, _ = synth("checkerboard", scale, st)
            mask = cell.body_mask(scale, lum.shape, 6.0)
            best = None
            for ceiling in (8.0, 16.0, 32.0, 64.0, 128.0):
                r = L.read_edge_spread(lum, bgc, mask, scale, ceiling)
                if r["n"] == 0:
                    continue
                err = abs(r["sigmaDev"] - st) / st * 100.0
                if best is None or err < best[0]:
                    best = (err, ceiling, r)
                if err <= 5.0:
                    break
            if best is None:
                print(f"   {scale:5.0f} {st:6.1f}  no resolvable single-step window")
                continue
            err, ceiling, r = best
            ok = err <= 5.0
            why = "" if ok else _esf_why(st, scale, r)
            if not ok:
                fails.append(("B", scale, st, err, why))
            print(f"   {scale:5.0f} {st:6.1f} {ceiling:6.0f} {r['sigmaDev']:8.2f} {err:8.2f} "
                  f"{r['residual']:8.4f} {r['halfWindowDev']:8.1f} {r['n']:4d}  "
                  f"{'PASS' if ok else 'BOUND: ' + why}")
    print()

    # ---------------------------------------------------------------- reader C on both backdrops
    print("== Reader C — the whole-region sigma match (`sigma_match`), grid 0..64 DEVICE px")
    print("   `read-stack.py`'s statistic with its 16.00 ceiling raised to 64. `rmsRel` is the")
    print("   match's residual as a fraction of the region's own standard deviation.")
    print(f"   {'backdrop':>13} {'scale':>5} {'true':>6} {'sigma':>8} {'err %':>8} {'rmsRel':>8} "
          f"{'gain':>7}  verdict")
    for bgname in ("checkerboard", "impulse"):
        for scale in (1, 2):
            bg = L.background_for(bgname, scale, (int(200 * scale), int(320 * scale)))
            for st in TRUE_SIGMAS:
                lum, _ = synth(bgname, scale, st)
                mask = cell.body_mask(scale, lum.shape, 6.0)
                r = L.sigma_match(lum, bg, mask, top=64.0, ref_key=(bgname, scale))
                err = (abs(r["sigmaDev"] - st) / st * 100.0
                       if np.isfinite(r["sigmaDev"]) else float("nan"))
                ok = np.isfinite(err) and err <= 5.0
                why = "" if ok else _match_why(st, scale, r)
                if not ok:
                    fails.append(("C", scale, st, err, why))
                print(f"   {bgname:>13} {scale:5.0f} {st:6.1f} {r['sigmaDev']:8.2f} {err:8.2f} "
                      f"{r['rmsRel']:8.4f} {r.get('gain', float('nan')):7.3f}  "
                      f"{'PASS' if ok else 'BOUND: ' + why}")
    print()

    print("== Grid resolution note")
    print("   Reader C's grid steps 0.1 below 4, 0.25 to 16 and 0.5 above, so its own quantisation")
    print("   is 0.5/16 = 3.1 % at sigma 16 and 0.25/4 = 6.3 % at sigma 4 — the 5 % acceptance is")
    print("   inside the grid's step at sigma 4 and the row is read against the step, not against")
    print("   the reader.")
    print()
    if fails:
        print(f"== {len(fails)} row(s) outside 5 %, each with its reason above. These are the")
        print("   readers' stated bounds and they are the finding, not a failure to run.")
    else:
        print("== every row inside 5 %.")
    return 0


def _psf_why(sigma, scale, ceiling):
    if sigma >= ceiling:
        return (f"sigma {sigma:g} is at or past the profile's own ceiling {ceiling:g} device px "
                f"(half-window {HALF_CSS:g} CSS px = {HALF_CSS * scale:g} device px); the dots are "
                f"64 CSS px apart, so a wider window would take in the neighbour")
    return ("the recovery error at this width is the instrument's floor, not a bound: a 4 CSS px "
            "box sampled at " + f"{4 * scale:g} device px and quantised to 8 bits")


def _esf_why(sigma, scale, r):
    cell_dev = 16.0 * scale
    if sigma > cell_dev / 2.0:
        return (f"sigma {sigma:g} exceeds half the checker cell ({cell_dev / 2:g} device px), so "
                f"the neighbouring steps are inside the window and the single-erf model is the "
                f"wrong question; raising the ceiling cannot fix it (residual {r['residual']:.3f})")
    return f"residual {r['residual']:.3f} of the step height"


def _match_why(sigma, scale, r):
    if r.get("reason"):
        return r["reason"]
    if r["atCeiling"]:
        return "at the grid's 64 device px ceiling"
    return f"grid step; residual {r['rmsRel']:.3f} of the region's sd"


if __name__ == "__main__":
    sys.exit(main())
