#!/bin/bash
# W24 G1 (c) — the ladder: the collapse's transmission measured on vitrea's own pixels.
#
# The wave's rule is W23's: every fit is on captures the real pipeline produced at a named
# constant, never on an arithmetic prediction. Here the ladder can be SHORT because the mechanism
# is exactly linear in its constant on the cells it reaches. Where the collapse is full (k = 1 —
# every `impulse__capsule-button` cell, which is what the wave reads) the shader's composite
# reduces to
#
#     colour = (1 − c)·toneColour + c·backdrop,
#
# so the dot's excess over the body is `c` times the excess vitrea's own blurred backdrop carries
# there, and ONE non-zero rung per profile fixes that excess exactly. The `fit` phase then renders
# the solved constant and confirms it rather than assuming the algebra.
#
# One document serves both scales, so a candidate carries both anchors and the 1x and 2x runs read
# the same file at two profile keys.
#
# `probe` also renders a c = 0 control on one profile, because the byte-identity claim needs a
# capture and not an argument: at 0 the new code path must reproduce the landed 0.12.0 PNGs.
#
# Five points then four, GPU tier, `--set calibration,validation` — the HOLDOUT IS NOT CAPTURED
# at any rung (X3). Everything goes to scratch through `--out-matrix` and `VITREA_WEB_CAPTURES`;
# nothing canonical is written.
#
# The GPU is shared (X4): G0 captures first, this script serialises its own runs and writes a DONE
# marker at the end.
#
# Usage: `bash ladder.sh <phase>` where phase is `probe` or `fit`.
set -u
WORKTREE=/Users/new/Developer/GitHub/designer/.claude/worktrees/agent-aa8a0b1f92b46418f
T=/Users/new/.claude/jobs/5c70e47f/tmp/w24/g1
C="$T/candidates"
PHASE="${1:-probe}"
unset VITREA_SCENES VITREA_FIXTURES VITREA_ALLOW_FALLBACK_ADAPTER
mkdir -p "$T/ladder"
rm -f "$T/ladder/DONE-$PHASE"
LOG="$T/ladder/$PHASE.log"
: > "$LOG"
cd "$WORKTREE/packages/calibration"

run() {
  local label=$1 profile=$2 doc=$3
  local out="$T/ladder/$label"
  mkdir -p "$out"
  echo "=== $(date +%H:%M:%S) $label / $profile ===" | tee -a "$LOG"
  VITREA_WEB_CAPTURES="$out/web-captures" npx tsx cli/compare.ts --profile "$profile" \
    --material-profile "$doc" --renderer webgpu --set calibration,validation \
    --allow-colourless-tints --write-partial --out-matrix "$out/matrix.json" >> "$LOG" 2>&1
  echo "    exit=$?" | tee -a "$LOG"
}

if [ "$PHASE" = probe ]; then
  run control-1x-light apple-macos-26.5-1x-light-standard "$C/light-c0.json"
  run probe-1x-light   apple-macos-26.5-1x-light-standard "$C/light-probe.json"
  run probe-2x-light   apple-macos-26.5-2x-light-standard "$C/light-probe.json"
  run probe-1x-dark    apple-macos-26.5-1x-dark-standard  "$C/dark-probe.json"
  run probe-2x-dark    apple-macos-26.5-2x-dark-standard  "$C/dark-probe.json"
else
  run fit-1x-light apple-macos-26.5-1x-light-standard "$C/light-fit.json"
  run fit-2x-light apple-macos-26.5-2x-light-standard "$C/light-fit.json"
  run fit-1x-dark  apple-macos-26.5-1x-dark-standard  "$C/dark-fit.json"
  run fit-2x-dark  apple-macos-26.5-2x-dark-standard  "$C/dark-fit.json"
fi
echo "ALL $PHASE RUNS DONE $(date +%H:%M:%S)" | tee -a "$LOG"
touch "$T/ladder/DONE-$PHASE"
