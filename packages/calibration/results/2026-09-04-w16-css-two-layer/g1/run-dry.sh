#!/bin/bash
# W16 G1: the dry run of the two-layer CSS body — the branch's build captured into a scratch
# matrix beside the canonical W15 bed (nothing canonical is touched). Usage:
#
#   bash run-dry.sh <tag> <renderer> <sets>
#
# e.g. `run-dry.sh dry webgpu calibration,validation,holdout` for the GPU tier's byte-identity
# scan (the GPU tier is bound unchanged, so reading its holdout is not a holdout read), then
# `run-dry.sh dry css calibration,validation` for the tier this wave changes, and once the
# configuration is frozen `run-dry.sh dry css holdout` for contract X8's single reading. The
# same tag keeps the tiers in one matrix so the cross-tier coherence rows compute.
set -u
TAG=$1; RENDERER=$2; SETS=$3
W=/Users/new/Developer/GitHub/designer/.claude/worktrees/w16-g1/packages/calibration
T=/Users/new/.claude/jobs/5c70e47f/tmp/w16/dry
if pgrep -f 'compare.ts|sweep.ts|cost.mjs|capture.mjs' > /dev/null || lsof -i :5189 > /dev/null 2>&1; then
  echo "GPU busy: another capture is running"; exit 2
fi
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
