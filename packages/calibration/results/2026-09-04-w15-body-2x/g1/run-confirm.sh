#!/bin/bash
# W15 G1: the single confirmation run at the chosen 2x constants — four profiles into one matrix,
# calibration + validation + HOLDOUT (contract X8: the 2x holdout's one reading of the frozen
# configuration; the landing reproduces it). Usage:
#
#   bash results/2026-09-04-w15-body-2x/g1/run-confirm.sh <chosen-light.json> <chosen-dark.json>
#
# The chosen documents are full material-profile documents (the canonical light/dark profiles
# with the sweep's winning 2x constants in their patch), written by the parent from the sweep's
# point profile. Captures go to scratch; nothing canonical is touched.
set -u
LIGHT=$1; DARK=$2
T=/Users/new/.claude/jobs/5c70e47f/tmp/w15/g1
W=/Users/new/Developer/GitHub/designer/.claude/worktrees/w15-g1/packages/calibration
if pgrep -f 'compare.ts|sweep.ts' > /dev/null || lsof -i :5189 > /dev/null 2>&1; then
  echo "GPU busy: another capture is running"; exit 2
fi
cd "$W"
rm -f "$T/matrix-confirm.json"; rm -rf "$T/web-captures-confirm"
run() {
  local profile=$1 doc=$2
  echo "=== $(date +%H:%M:%S) $profile ==="
  VITREA_WEB_CAPTURES="$T/web-captures-confirm" npx tsx cli/compare.ts --profile "$profile" \
    --material-profile "$doc" --renderer webgpu --set calibration,validation,holdout \
    --write-partial --out-matrix "$T/matrix-confirm.json" >> "$T/confirm-runs.log" 2>&1
  echo "    exit=$?"
}
run apple-macos-26.5-1x-light-standard "$LIGHT"
run apple-macos-26.5-2x-light-standard "$LIGHT"
run apple-macos-26.5-1x-dark-standard "$DARK"
run apple-macos-26.5-2x-dark-standard "$DARK"
echo "CONFIRM DONE $(date +%H:%M:%S)"
