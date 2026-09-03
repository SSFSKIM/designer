#!/bin/bash
# The single confirmation run at the chosen constants: four profiles into one matrix.
set -u
T=/Users/new/.claude/jobs/5c70e47f/tmp/w13/sweep-4
cd /Users/new/Developer/GitHub/designer/.claude/worktrees/w13-g1/packages/calibration
rm -f "$T/matrix-confirm.json"
run() {
  local profile=$1 doc=$2
  echo "=== $(date +%H:%M:%S) $profile ==="
  VITREA_WEB_CAPTURES="$T/web-captures-confirm" npx tsx cli/compare.ts --profile "$profile" \
    --material-profile "$doc" --renderer webgpu --set calibration,validation,holdout \
    --write-partial --out-matrix "$T/matrix-confirm.json" >> "$T/confirm-runs.log" 2>&1
  echo "    exit=$?"
}
run apple-macos-26.5-1x-light-standard "$T/chosen-light.json"
run apple-macos-26.5-2x-light-standard "$T/chosen-light.json"
run apple-macos-26.5-1x-dark-standard "$T/chosen-dark.json"
run apple-macos-26.5-2x-dark-standard "$T/chosen-dark.json"
echo "CONFIRM DONE $(date +%H:%M:%S)"
