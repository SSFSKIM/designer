#!/bin/bash
# W24 G0 (c) — the short scratch ladder: the lit edge's leverage on vitrea's own pixels.
#
# The wave's rule is that every fit is on captures the real pipeline produced at a named constant.
# The rim term is not linear in this constant — it is an exponent — so one point cannot fix it and
# the ladder carries two: exponent 1 on all four canonical profiles, and exponent 2 on the two 2x
# profiles, which are the rows whose arcs the raster actually carries. The LANDED 0.12.0 captures
# are the ladder's third point at exponent 0 and are not re-rendered.
#
# Two more runs give the probe grids their vitrea side at the shipped documents, so that the read
# of (b) has a web column on W9's light grid and W21's dark grid as well as a native one.
#
# Eight runs, GPU tier, `--set calibration,validation` — THE HOLDOUT IS NOT CAPTURED at any point
# (X3). Everything goes to scratch through `--out-matrix` and `VITREA_WEB_CAPTURES`; nothing
# canonical is written.
#
# The GPU is shared: this script serialises every run and writes the wave's `DONE` marker at the
# end, which is what G1 waits on before it may capture (X4).
set -u
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKTREE="$(cd "$HERE/../../../../.." && pwd)"
T=/Users/new/.claude/jobs/5c70e47f/tmp/w24/g0
C="$T/candidates"
unset VITREA_SCENES VITREA_FIXTURES
mkdir -p "$T/ladder"
rm -f "$T/DONE"
LOG="$T/ladder/runs.log"
: > "$LOG"
cd "$WORKTREE/packages/calibration"

run() {
  local label=$1 profile=$2 doc=$3
  local out="$T/ladder/$label"
  rm -rf "$out"; mkdir -p "$out"
  echo "=== $(date +%H:%M:%S) $label / $profile / $(basename "$doc") ===" | tee -a "$LOG"
  VITREA_WEB_CAPTURES="$out/web-captures" npx tsx cli/compare.ts --profile "$profile" \
    --material-profile "$doc" --renderer webgpu --set calibration,validation \
    --allow-colourless-tints --write-partial --out-matrix "$out/matrix.json" >> "$LOG" 2>&1
  echo "    exit=$?" | tee -a "$LOG"
}

run_probe() {
  local label=$1 scenes=$2 fixtures=$3 profile=$4 doc=$5
  local out="$T/ladder/$label"
  rm -rf "$out"; mkdir -p "$out"
  echo "=== $(date +%H:%M:%S) $label / $profile / $(basename "$doc") ===" | tee -a "$LOG"
  VITREA_SCENES="$scenes" VITREA_FIXTURES="$fixtures" VITREA_WEB_CAPTURES="$out/web-captures" \
    npx tsx cli/compare.ts --profile "$profile" --material-profile "$doc" --renderer webgpu \
    --set calibration,validation --allow-colourless-tints --write-partial \
    --out-matrix "$out/matrix.json" >> "$LOG" 2>&1
  echo "    exit=$?" | tee -a "$LOG"
}

run light-lit1-1x apple-macos-26.5-1x-light-standard "$C/light-lit1.json"
run light-lit1-2x apple-macos-26.5-2x-light-standard "$C/light-lit1.json"
run dark-lit1-1x  apple-macos-26.5-1x-dark-standard  "$C/dark-lit1.json"
run dark-lit1-2x  apple-macos-26.5-2x-dark-standard  "$C/dark-lit1.json"
run light-lit2-2x apple-macos-26.5-2x-light-standard "$C/light-lit2.json"
run dark-lit2-2x  apple-macos-26.5-2x-dark-standard  "$C/dark-lit2.json"

run_probe probe9-base "$WORKTREE/apps/reference-apple/scenes-w9-probe.json" \
  /Users/new/.claude/jobs/5c70e47f/tmp/w9-probe-fixtures \
  apple-macos-26.5-1x-light-standard \
  "$WORKTREE/packages/calibration/profiles/apple-macos-26.5-1x-light-standard.json"
run_probe probe21-base "$WORKTREE/apps/reference-apple/scenes-w21-probe.json" \
  "$WORKTREE/packages/calibration/results/2026-09-06-w21-dark-scheme/probe" \
  apple-macos-26.5-1x-dark-standard \
  "$WORKTREE/packages/calibration/profiles/apple-macos-26.5-1x-dark-standard.json"

echo "ALL RUNS DONE $(date +%H:%M:%S)" | tee -a "$LOG"
touch "$T/DONE"
