#!/bin/bash
# W22 G0 (b) — vitrea's captures at the gate, on BOTH canonical beds, GPU tier, both scales.
#
# Everything here goes to scratch. `--out-matrix` moves the matrix and `VITREA_WEB_CAPTURES` moves
# the captures, so the canonical `results/matrix.json` and `web-captures/` are untouched in both the
# main checkout and this worktree; the native side is the committed fixtures, unmoved, and no
# profile document changes, so the only thing that differs from the canonical bed is the gate.
#
# `--set calibration,validation` only. The holdout is NOT read here: W22 X5 spends the wave's one
# holdout read at G1's dry run on the frozen configuration, and a spike that opened it would void
# that. `--set holdout` appears nowhere below on purpose.
#
# `--alpha` takes the declaration-conformance capture on every cell. It is not optional: W20
# Decision Log 2 ruling 2 put those rows in the canonical matrix and `adopted-thresholds.test.ts`
# fails a bed without them, so a gate that means to be run over the matrix has to carry them.
#
# The GPU is shared, so the four runs are serialised in one process and a DONE marker is the only
# thing anything waits on.
set -u
cd /Users/new/Developer/GitHub/designer/.claude/worktrees/agent-ac5e591b52341c4ce
unset VITREA_SCENES VITREA_FIXTURES
T=/Users/new/.claude/jobs/5c70e47f/tmp/w22/g0/after
mkdir -p "$T"
export VITREA_WEB_CAPTURES="$T/web-captures"
MATRIX="$T/g0-after.json"
rm -f "$MATRIX" "$T/DONE"
LOG="$T/g0-runs.log"
: > "$LOG"
echo "=== $(date +%H:%M:%S) build ==="
pnpm -r build > "$T/build.log" 2>&1 || { echo "BUILD FAILED"; exit 1; }
echo "=== $(date +%H:%M:%S) HEAD $(git rev-parse --short HEAD) $(git status --short | wc -l | tr -d ' ') dirty ==="
cd packages/calibration
LIGHT=profiles/apple-macos-26.5-1x-light-standard.json
DARK=profiles/apple-macos-26.5-1x-dark-standard.json
run() {
  local profile=$1 doc=$2
  echo "=== $(date +%H:%M:%S) $profile / webgpu / calibration,validation ==="
  npx tsx cli/compare.ts --profile "$profile" --material-profile "$doc" --renderer webgpu \
    --set calibration,validation --allow-colourless-tints --alpha --write-partial \
    --out-matrix "$MATRIX" >> "$LOG" 2>&1
  echo "    exit=$?"
}
run apple-macos-26.5-1x-light-standard "$LIGHT"
run apple-macos-26.5-2x-light-standard "$LIGHT"
run apple-macos-26.5-1x-dark-standard "$DARK"
run apple-macos-26.5-2x-dark-standard "$DARK"
echo "ALL RUNS DONE $(date +%H:%M:%S)"
touch "$T/DONE"
