#!/bin/bash
# W12 G2b referee (the ω 0.8 A/B round, W12 Decision Log 4): the six webgpu per-profile
# runs to a SCRATCH matrix and scratch captures inside THIS worktree (the canonical
# matrix.json and web-captures/ of the main checkout are untouched), then the whole-bed
# scan against the G2 landing (matrix-g2.json) and the 0.3.0 bed (matrix-w11c-g2-close.json).
#
# Only webgpu runs: the CSS tier has no lens by contract, so a lens-only constant cannot
# move a CSS cell, and the G2 referee's twelve runs proved that tier byte-stable under a
# far larger lens change. The scan reads the CSS rows from the G2 matrix instead.
set -u
cd /Users/new/Developer/GitHub/designer/.claude/worktrees/agent-a82623fa9fc3b23f9/packages/calibration
unset VITREA_SCENES VITREA_FIXTURES
T=/Users/new/.claude/jobs/5c70e47f/tmp/w12
export VITREA_WEB_CAPTURES="$T/web-captures-g2b"
OUT="$T/matrix-g2b.json"
LOG="$T/g2b-referee-runs.log"
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
for renderer in webgpu; do
  run apple-macos-26.5-1x-light-standard "$LIGHT" "$renderer"
  run apple-macos-26.5-2x-light-standard "$LIGHT" "$renderer"
  run apple-macos-26.5-1x-light-increased-contrast "$LIGHT" "$renderer"
  run apple-macos-26.5-1x-light-reduced-transparency "$LIGHT" "$renderer"
  run apple-macos-26.5-1x-dark-standard "$DARK" "$renderer"
  run apple-macos-26.5-2x-dark-standard "$DARK" "$renderer"
done
echo "ALL RUNS DONE $(date +%H:%M:%S)"
