#!/bin/bash
# W17 G1: the k sweep of Decision Log 4 (b) — the filter region's reach in units of the composed
# heavy width, measured on the two `toolbar-group` scenes at both light-standard scales.
#
#   bash run-sweep.sh <k>
#
# `k` is written into `CSS_TIER_FILTER_REGION_SIGMA` by the caller before the build; this script
# only captures, into a matrix tagged by the value so the three runs sit side by side.
set -u
K=$1
W=/Users/new/Developer/GitHub/designer/.claude/worktrees/w17-g1/packages/calibration
T=/Users/new/.claude/jobs/5c70e47f/tmp/w17/g1
SCENES=checkerboard__toolbar-group__rest,photo__toolbar-group__rest
if pgrep -f 'compare.ts|sweep.ts|cost.mjs|capture.mjs' > /dev/null || lsof -i :5189 > /dev/null 2>&1; then
  echo "GPU busy: another capture is running"; exit 2
fi
cd "$W"; unset VITREA_SCENES VITREA_FIXTURES
LIGHT=profiles/apple-macos-26.5-1x-light-standard.json
for RENDERER in webgpu css; do
  for PROFILE in apple-macos-26.5-1x-light-standard apple-macos-26.5-2x-light-standard; do
    echo "=== $(date +%H:%M:%S) k=$K $PROFILE / $RENDERER ==="
    VITREA_WEB_CAPTURES="$T/web-captures-k$K" npx tsx cli/compare.ts --profile "$PROFILE" \
      --material-profile "$LIGHT" --renderer "$RENDERER" --scene "$SCENES" --write-partial \
      --out-matrix "$T/matrix-k$K.json" >> "$T/runs-k$K.log" 2>&1
    echo "    exit=$?"
  done
done
echo "DONE k=$K $(date +%H:%M:%S)"
