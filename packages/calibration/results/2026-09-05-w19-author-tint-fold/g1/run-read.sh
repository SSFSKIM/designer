#!/bin/bash
# W19 G1 — the pre-check's readers, over one pair of capture roots.
#
# The captures themselves are taken by G0's `run-ladder.sh` unchanged, on G0's own scratch bed
# (`make-scenes.mjs` from the canonical `scenes.json`, twenty scenes, verified byte-identical to
# G0's): eight runs, one at a time on the shared adapter, the GPU tier first. This reads them.
#
# Four readers on the standard-light roots at each scale, and one on each fold profile:
#
#   ladder.ts       G0's, unchanged — CSS − GPU interior mean under the declared region, the
#                   spread beside it, and the form each cell drew from `report__css.json` (S4).
#   predict.ts      G0's, unchanged — the fold's own prediction from the tier's untinted capture
#                   per pixel, and the clamp share under both tables (S5).
#   hue.ts          this wave's — the cross-tier OKLab ΔE the interior mean under-reports, run on
#                   BOTH the pre-fold captures and this run's so the move is a difference.
#   moved.ts        this wave's — what moved between the two CSS roots, per cell, with the
#                   differing pixels classified against the region eroded by two device px (S3).
#   granularity.ts  this wave's — W10's per-pixel-versus-per-source tint shade, per cell, which
#                   Decision Log 2 (7) requires beside any checkerboard cell that misses S4.
#
# X4 travels with every reading: `x4-recovery.ts` is re-run on THIS run's captures, under the same
# masks, before any number above is used.
#
# Nothing canonical is written: every path is an argument and every output lands under the scratch
# root the caller names.
#
# Usage, from `packages/calibration`:
#   bash results/2026-09-05-w19-author-tint-fold/g1/run-read.sh <scenesJson> <afterRoot> \
#     <beforeRoot> <partsDir>
#
# `<afterRoot>` and `<beforeRoot>` each hold the eight capture trees `run-ladder.sh` writes
# (`std-{webgpu,css}-{1,2}x`, `fold-{increased-contrast,reduced-transparency}-{webgpu,css}-1x`);
# `<beforeRoot>` is G0's.
set -u
SCENES="${1:?usage: run-read.sh <scenesJson> <afterRoot> <beforeRoot> <partsDir>}"
AFTER="${2:?}"
BEFORE="${3:?}"
PARTS="${4:?}"
D=results/2026-09-05-w19-author-tint-fold
mkdir -p "$PARTS"

for scale in 1 2; do
  npx tsx $D/g0/ladder.ts "$SCENES" "$AFTER/std-webgpu-${scale}x" "$AFTER/std-css-${scale}x" \
    "$scale" "$PARTS/ladder-${scale}x.json"
  npx tsx $D/g0/predict.ts "$SCENES" "$AFTER/std-webgpu-${scale}x" "$AFTER/std-css-${scale}x" \
    "$scale" "$PARTS/predict-${scale}x.json"
  npx tsx $D/g1/hue.ts "$SCENES" "$AFTER/std-webgpu-${scale}x" "$AFTER/std-css-${scale}x" \
    "$scale" "$PARTS/hue-after-${scale}x.json"
  npx tsx $D/g1/hue.ts "$SCENES" "$BEFORE/std-webgpu-${scale}x" "$BEFORE/std-css-${scale}x" \
    "$scale" "$PARTS/hue-before-${scale}x.json"
  npx tsx $D/g1/moved.ts "$SCENES" "$BEFORE/std-css-${scale}x" "$AFTER/std-css-${scale}x" \
    "$scale" css "$PARTS/moved-${scale}x.json"
  npx tsx $D/g1/granularity.ts "$SCENES" "$AFTER/std-webgpu-${scale}x" "$AFTER/std-css-${scale}x" \
    "$scale" "$PARTS/granularity-${scale}x.json"
done

for acc in increased-contrast reduced-transparency; do
  npx tsx $D/g0/ladder.ts "$SCENES" "$AFTER/fold-$acc-webgpu-1x" "$AFTER/fold-$acc-css-1x" 1 \
    "$PARTS/ladder-fold-$acc.json"
done

npx tsx $D/g0/x4-recovery.ts "$SCENES" "$AFTER/std-css-1x" css \
  photo__capsule-button__rest-tint-orange-010 1 > "$PARTS/x4-recovery.txt" 2>&1
echo "DONE $(date -u +%H:%M:%SZ)"
