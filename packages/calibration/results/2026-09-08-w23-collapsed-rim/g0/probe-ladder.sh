#!/bin/bash
# W23 G0 (d) — the ladder on the two PROBE grids, because the canonical bed cannot fit this law.
#
# The rim law has two constants per scheme and the canonical bed has, per scheme, two usable rows to
# fit them on: over a solid backdrop, unclipped, uncollapsed, and outside the holdout, the light bed
# leaves `dark-solid__rrect-md` and `impulse__rrect-md` — whose bodies differ by 0.05 — and the dark
# bed leaves `dark-solid__rrect-md` alone. Two nearly collinear rows cannot separate a slope from an
# intercept, and the first pass of `fit-law.py` shows exactly that: the 1x and the 2x solves
# disagree by a factor of three on the gain (W22's S5, failing).
#
# The probe grids are where the range is. W9's light grid and W21's dark grid both carry
# `dark-solid`, `mid-dark-solid` and `light-solid` at three sizes, and their reference bodies span
# 0.43…0.93 in the light scheme and 0.015…0.103 in the dark one. They are fitting ground and not
# holdout (the wave's Grounding Baseline says so), and their own `--set calibration,validation`
# keeps each grid's own holdout column unread.
#
# Two points per grid: the SHIPPED document, which gives each cell's band weight `W = rim / rimAlpha`
# at a known constant, and the level-gain document, which gives `W x L`. Everything else is a linear
# solve. Both grids come through `VITREA_SCENES` / `VITREA_FIXTURES`, so no canonical scene file or
# fixture is read and every capture goes to scratch.
#
# The GPU is shared: this script serialises every run and writes a DONE marker.
set -u
WORKTREE=/Users/new/Developer/GitHub/designer/.claude/worktrees/agent-aa0ee5ea92534c3fd
SCRATCH=/Users/new/.claude/jobs/5c70e47f/tmp
T="$SCRATCH/w23/g0/probe"
C="$SCRATCH/w23/g0/candidates"
W21_PROBE="$WORKTREE/packages/calibration/results/2026-09-06-w21-dark-scheme/probe"
W9_PROBE="$SCRATCH/w9-probe-fixtures"
mkdir -p "$T"
rm -f "$T/DONE"
LOG="$T/probe-runs.log"
: > "$LOG"
cd "$WORKTREE/packages/calibration"

run() {
  local label=$1 scenes=$2 fixtures=$3 profile=$4 doc=$5
  local out="$T/$label"
  rm -rf "$out"; mkdir -p "$out"
  echo "=== $(date +%H:%M:%S) $label ===" >> "$LOG"
  VITREA_SCENES="$scenes" VITREA_FIXTURES="$fixtures" VITREA_WEB_CAPTURES="$out/web-captures" \
    npx tsx cli/compare.ts --profile "$profile" --material-profile "$doc" --renderer webgpu \
    --set calibration,validation --allow-colourless-tints --write-partial \
    --out-matrix "$out/matrix.json" >> "$LOG" 2>&1
  echo "    exit=$?" >> "$LOG"
}

run probe9-base "$WORKTREE/apps/reference-apple/scenes-w9-probe.json" "$W9_PROBE" \
  apple-macos-26.5-1x-light-standard "$WORKTREE/packages/calibration/profiles/apple-macos-26.5-1x-light-standard.json"
run probe9-levelgain "$WORKTREE/apps/reference-apple/scenes-w9-probe.json" "$W9_PROBE" \
  apple-macos-26.5-1x-light-standard "$C/light-levelgain.json"
run probe21-base "$WORKTREE/apps/reference-apple/scenes-w21-probe.json" "$W21_PROBE" \
  apple-macos-26.5-1x-dark-standard "$WORKTREE/packages/calibration/profiles/apple-macos-26.5-1x-dark-standard.json"
run probe21-levelgain "$WORKTREE/apps/reference-apple/scenes-w21-probe.json" "$W21_PROBE" \
  apple-macos-26.5-1x-dark-standard "$C/dark-levelgain.json"
echo "ALL PROBE RUNS DONE $(date +%H:%M:%S)" >> "$LOG"
touch "$T/DONE"
