#!/bin/bash
# W12 G3 referee: the twelve per-profile runs to a SCRATCH matrix and scratch captures
# (the canonical matrix.json and web-captures/ are untouched), run from the G3 landing
# worktree so the material under test is the declared one (claims §5.56).
set -u
cd /Users/new/Developer/GitHub/designer/.claude/worktrees/agent-a25a752a19656e6bc/packages/calibration
unset VITREA_SCENES VITREA_FIXTURES
T=/Users/new/.claude/jobs/5c70e47f/tmp/w12
export VITREA_WEB_CAPTURES="$T/web-captures-g3"
OUT="$T/matrix-g3.json"
LOG="$T/g3-referee-runs.log"
: > "$LOG"; rm -f "$OUT"; rm -rf "$VITREA_WEB_CAPTURES"; mkdir -p "$VITREA_WEB_CAPTURES"
LIGHT=profiles/apple-macos-26.5-1x-light-standard.json
DARK=profiles/apple-macos-26.5-1x-dark-standard.json
run() {
  local profile=$1 doc=$2 renderer=$3
  echo "=== $(date +%H:%M:%S) $profile / $renderer ==="
  npx tsx cli/compare.ts --profile "$profile" --material-profile "$doc" --renderer "$renderer" \
    --set calibration,validation,holdout --write-partial --out-matrix "$OUT" >> "$LOG" 2>&1
  echo "    exit=$?"
}
for renderer in webgpu css; do
  run apple-macos-26.5-1x-light-standard "$LIGHT" "$renderer"
  run apple-macos-26.5-2x-light-standard "$LIGHT" "$renderer"
  run apple-macos-26.5-1x-light-increased-contrast "$LIGHT" "$renderer"
  run apple-macos-26.5-1x-light-reduced-transparency "$LIGHT" "$renderer"
  run apple-macos-26.5-1x-dark-standard "$DARK" "$renderer"
  run apple-macos-26.5-2x-dark-standard "$DARK" "$renderer"
done
echo "ALL RUNS DONE $(date +%H:%M:%S)"
