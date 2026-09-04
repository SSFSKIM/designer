#!/bin/bash
# W17 G1: the probe pre-check — the three W16 probe cells at both light-standard scales, on one
# tier, into a scratch matrix beside the canonical W16 bed (nothing canonical is touched).
#
#   bash run-probe.sh <tag> <renderer>
#
# `tag` names the configuration the branch was built at: `cfg2` is the full form (the ordering
# fix, the inner shadow and the tint's lerp inside the sharp layer's linear-light filter), `cfg1`
# is the ordering fix and the inner shadow ALONE with the `rgba()` overlay still carrying the
# tint, and `gpu` is the GPU tier's byte-identity scan. Both tiers of one configuration share a
# matrix so the cross-tier coherence rows compute.
set -u
TAG=$1; RENDERER=$2
W=/Users/new/Developer/GitHub/designer/.claude/worktrees/w17-g1/packages/calibration
T=/Users/new/.claude/jobs/5c70e47f/tmp/w17/g1
# Decision Log 4's list: the three W16 cells, the two `toolbar-group` scenes the region's clipping
# was measured on, the `impulse` capsule the chain's quantum truncated, and one dark-scheme
# checkerboard cell for the boundary (c) draws.
SCENES=checkerboard__rrect-md__rest,checkerboard__capsule-button__rest,checkerboard__rrect-ml__rest,checkerboard__toolbar-group__rest,photo__toolbar-group__rest,impulse__capsule-button__rest
if pgrep -f 'compare.ts|sweep.ts|cost.mjs|capture.mjs' > /dev/null || lsof -i :5189 > /dev/null 2>&1; then
  echo "GPU busy: another capture is running"; exit 2
fi
mkdir -p "$T"
cd "$W"; unset VITREA_SCENES VITREA_FIXTURES
LIGHT=profiles/apple-macos-26.5-1x-light-standard.json
DARK=profiles/apple-macos-26.5-1x-dark-standard.json
run() {
  local profile=$1 doc=$2 scenes=$3
  echo "=== $(date +%H:%M:%S) $profile / $RENDERER / $TAG ==="
  VITREA_WEB_CAPTURES="$T/web-captures-$TAG" npx tsx cli/compare.ts --profile "$profile" \
    --material-profile "$doc" --renderer "$RENDERER" --scene "$scenes" --write-partial \
    --out-matrix "$T/matrix-$TAG.json" >> "$T/runs-$TAG.log" 2>&1
  echo "    exit=$?"
}
run apple-macos-26.5-1x-light-standard "$LIGHT" "$SCENES"
run apple-macos-26.5-2x-light-standard "$LIGHT" "$SCENES"
# The dark scheme's own checkerboard cell, on the dark document, for the boundary (c) draws.
run apple-macos-26.5-1x-dark-standard "$DARK" checkerboard__rrect-md__rest
run apple-macos-26.5-2x-dark-standard "$DARK" checkerboard__rrect-md__rest
echo "DONE $TAG/$RENDERER $(date +%H:%M:%S)"
