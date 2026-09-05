#!/bin/bash
# W19 G1 — the dry run's per-profile readers, over the whole canonical bed.
#
# The captures themselves are W18 G1's `run-dry.sh` unchanged (both tiers, GPU first, one matrix so
# the coherence rows compute, the holdout in `--set` because X8 reads it once here). This runs the
# two per-profile readers whose output `verify-dry.py` then reads:
#
#   moved.ts     what moved between the W18 bed's CSS capture and this run's, per cell, with every
#                differing pixel classified against the declared component region eroded by two
#                device pixels — S3's pixel half, which a matrix cannot see.
#   predict.ts   G0's, unchanged — the fold's own prediction from the tier's untinted capture per
#                pixel, and the clamp share under both tables, for S5.
#
# `predict.ts` derives a tinted cell's untinted base as `<background>__capsule-button__rest`, so its
# rows are meaningful only where that IS the cell's base; S5's clause is on the `orange-half` cells,
# which it is, and `verify-dry.py` reads no other row of it. It also resolves the surface under the
# nominal policy, so its fold-profile rows are recorded and not gated.
#
# Every path is an argument and nothing canonical is written.
#
# Usage, from `packages/calibration`:
#   bash results/2026-09-05-w19-author-tint-fold/g1/run-dry-readers.sh <scenesDir> <bedCapturesDir> \
#     <dryCapturesDir> <partsDir>
set -u
SCENES="${1:?usage: run-dry-readers.sh <scenesDir> <bedCaptures> <dryCaptures> <partsDir>}"
BED="${2:?}"
DRY="${3:?}"
PARTS="${4:?}"
D=results/2026-09-05-w19-author-tint-fold
mkdir -p "$PARTS"

for prof in apple-macos-26.5-1x-light-standard apple-macos-26.5-2x-light-standard \
            apple-macos-26.5-1x-light-increased-contrast \
            apple-macos-26.5-1x-light-reduced-transparency \
            apple-macos-26.5-1x-dark-standard apple-macos-26.5-2x-dark-standard; do
  case "$prof" in *-2x-*) SCALE=2;; *) SCALE=1;; esac
  npx tsx $D/g1/moved.ts "$SCENES" "$BED/$prof" "$DRY/$prof" "$SCALE" css \
    "$PARTS/moved-$prof.json"
  npx tsx $D/g0/predict.ts "$SCENES/scenes.json" "$DRY/$prof" "$DRY/$prof" "$SCALE" \
    "$PARTS/predict-$prof.json"
done
echo "DONE $(date -u +%H:%M:%SZ)"
