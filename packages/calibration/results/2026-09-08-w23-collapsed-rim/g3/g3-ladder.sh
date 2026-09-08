#!/bin/bash
# W23 G3 — the painted rim's ladder: how much of the author's colour the rim's light is spent in.
#
# `rimTintChroma` multiplies the pixel's own tint strength, so it moves PAINTED pixels only and an
# untinted capture is byte-identical at every value — which is the mechanism's own proof (S10) and
# also why one point per bed fixes its leverage: the term is linear in the constant and reaches no
# other row.
#
# GPU tier, `--set calibration,validation` — the HOLDOUT IS NOT CAPTURED at any point of this
# ladder; the wave's holdout read is the final dry run's. Everything to scratch through
# `--out-matrix` and `VITREA_WEB_CAPTURES`; nothing canonical is written.
#
# The GPU is shared: this serialises every run and writes a DONE marker at the end.
#
# Usage: `bash g3-ladder.sh <phase>` — `base`, `probe`, or `confirm`.
set -u
WORKTREE=/Users/new/Developer/GitHub/designer/.claude/worktrees/w23-g1
T=/Users/new/.claude/jobs/5c70e47f/tmp/w23/g3
C="$T/candidates"
PHASE="${1:-base}"
unset VITREA_SCENES VITREA_FIXTURES VITREA_MATRIX_PATH
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

case "$PHASE" in
  base)
    run base-light-1x apple-macos-26.5-1x-light-standard "$C/light-fit.json"
    run base-light-2x apple-macos-26.5-2x-light-standard "$C/light-fit.json"
    run base-dark-1x  apple-macos-26.5-1x-dark-standard  "$C/dark-fit.json"
    run base-dark-2x  apple-macos-26.5-2x-dark-standard  "$C/dark-fit.json"
    ;;
  probe)
    run chroma1-light-1x apple-macos-26.5-1x-light-standard "$C/light-chroma1.json"
    run chroma1-light-2x apple-macos-26.5-2x-light-standard "$C/light-chroma1.json"
    run chroma1-dark-1x  apple-macos-26.5-1x-dark-standard  "$C/dark-chroma1.json"
    run chroma1-dark-2x  apple-macos-26.5-2x-dark-standard  "$C/dark-chroma1.json"
    ;;
  ct055)
    run ct055-light-1x apple-macos-26.5-1x-light-standard "$C/light-ct055.json"
    run ct055-light-2x apple-macos-26.5-2x-light-standard "$C/light-ct055.json"
    run ct055-dark-1x  apple-macos-26.5-1x-dark-standard  "$C/dark-ct055.json"
    run ct055-dark-2x  apple-macos-26.5-2x-dark-standard  "$C/dark-ct055.json"
    ;;
  confirm)
    run confirm-light-1x apple-macos-26.5-1x-light-standard "$C/light-confirm.json"
    run confirm-light-2x apple-macos-26.5-2x-light-standard "$C/light-confirm.json"
    run confirm-dark-1x  apple-macos-26.5-1x-dark-standard  "$C/dark-confirm.json"
    run confirm-dark-2x  apple-macos-26.5-2x-dark-standard  "$C/dark-confirm.json"
    ;;
  *) echo "unknown phase $PHASE"; exit 2;;
esac
echo "ALL $PHASE RUNS DONE $(date +%H:%M:%S)" | tee -a "$LOG"
touch "$T/ladder/DONE-$PHASE"
