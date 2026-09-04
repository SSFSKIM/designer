#!/bin/bash
# W17 G1: the whole-bed dry run — the branch's build captured into a scratch matrix beside the
# canonical W16 bed (nothing canonical is touched). Usage:
#
#   bash run-dry.sh <tag> <renderer> <sets>
#
# `tag` names the configuration the branch was built at: `cfg1` is the ordering fix and the inner
# shadow ALONE with the `rgba()` overlay still carrying the tint, `cfg2` is the full form. Both
# tiers of one configuration share a matrix so the cross-tier coherence rows compute, and the GPU
# tier has to be captured FIRST — a dom cell's coherence axis is measured against the webgpu
# capture already on disk, and is simply absent where there is none.
#
# The GPU tier is bound unchanged by this wave, so reading its holdout is not a holdout read; the
# CSS tier's holdout is contract X8's single reading and is taken once, on the frozen
# configuration 2, after the referee has passed on calibration and validation.
set -u
TAG=$1; RENDERER=$2; SETS=$3
W=/Users/new/Developer/GitHub/designer/.claude/worktrees/w17-g1/packages/calibration
T=/Users/new/.claude/jobs/5c70e47f/tmp/w17/g1
if pgrep -f 'compare.ts|sweep.ts|cost.mjs|capture.mjs' > /dev/null || lsof -i :5189 > /dev/null 2>&1; then
  echo "GPU busy: another capture is running"; exit 2
fi
mkdir -p "$T"
cd "$W"; unset VITREA_SCENES VITREA_FIXTURES
LIGHT=profiles/apple-macos-26.5-1x-light-standard.json
DARK=profiles/apple-macos-26.5-1x-dark-standard.json
run() {
  local profile=$1 doc=$2
  echo "=== $(date +%H:%M:%S) $profile / $RENDERER / $SETS ==="
  VITREA_WEB_CAPTURES="$T/web-captures-$TAG" npx tsx cli/compare.ts --profile "$profile" \
    --material-profile "$doc" --renderer "$RENDERER" --set "$SETS" --write-partial \
    --out-matrix "$T/matrix-$TAG.json" >> "$T/runs-$TAG.log" 2>&1
  echo "    exit=$?"
}
run apple-macos-26.5-1x-light-standard "$LIGHT"
run apple-macos-26.5-2x-light-standard "$LIGHT"
run apple-macos-26.5-1x-light-increased-contrast "$LIGHT"
run apple-macos-26.5-1x-light-reduced-transparency "$LIGHT"
run apple-macos-26.5-1x-dark-standard "$DARK"
run apple-macos-26.5-2x-dark-standard "$DARK"
echo "DONE $TAG/$RENDERER/$SETS $(date +%H:%M:%S)"
