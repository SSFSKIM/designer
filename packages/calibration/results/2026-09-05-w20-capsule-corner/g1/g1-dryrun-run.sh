#!/bin/bash
# W20 G1: the corrected corner over the bed, GPU tier only, to SCRATCH.
#
# The fix is `resolveCorner`'s Apple branch keeping the requested radius and compressing the
# shoulder (claims §5.84; W20 Decision Log 2 ruling 1). This run measures what that does to the
# bed on G0's instrument (contract X1): the same six profiles, the same `--alpha` conformance
# rows, calibration and validation only, holdout untouched, nothing canonical written.
#
# The GPU tier ONLY. The CSS tier draws the DOM's shape and no CSS code moved, so re-running it
# would only re-capture bytes the wave has already declared fixed (X3); G2 verifies it.
set -u
cd /Users/new/Developer/GitHub/designer/.claude/worktrees/agent-a463558bb21d8d14b
unset VITREA_SCENES VITREA_FIXTURES
T=/Users/new/.claude/jobs/5c70e47f/tmp/w20/g1
mkdir -p "$T"
export VITREA_WEB_CAPTURES="$T/web-captures"
MATRIX="$T/g1-dryrun.json"
rm -f "$MATRIX"
LOG="$T/g1-runs.log"
: > "$LOG"
rm -f "$T/DONE"
echo "=== $(date +%H:%M:%S) build ==="
pnpm -r build > "$T/build.log" 2>&1 || { echo "BUILD FAILED"; exit 1; }
echo "=== $(date +%H:%M:%S) HEAD $(git rev-parse --short HEAD) ==="
cd packages/calibration
LIGHT=profiles/apple-macos-26.5-1x-light-standard.json
DARK=profiles/apple-macos-26.5-1x-dark-standard.json
run() {
  local profile=$1 doc=$2
  echo "=== $(date +%H:%M:%S) $profile / webgpu ==="
  npx tsx cli/compare.ts --profile "$profile" --material-profile "$doc" --renderer webgpu \
    --set calibration,validation --alpha --write-partial --out-matrix "$MATRIX" >> "$LOG" 2>&1
  echo "    exit=$?"
}
run apple-macos-26.5-1x-light-standard "$LIGHT"
run apple-macos-26.5-2x-light-standard "$LIGHT"
run apple-macos-26.5-1x-dark-standard "$DARK"
run apple-macos-26.5-2x-dark-standard "$DARK"
run apple-macos-26.5-1x-light-increased-contrast "$LIGHT"
run apple-macos-26.5-1x-light-reduced-transparency "$LIGHT"
echo "ALL RUNS DONE $(date +%H:%M:%S)"
touch "$T/DONE"
