#!/bin/bash
# W23 G0 (d) — the ladder: the rim law's leverage measured on vitrea's own pixels.
#
# The wave's rule (its "How G0 fits without guessing"): every fit is on captures the real pipeline
# produced at a named constant, not on an arithmetic prediction. The rim term is LINEAR in each of
# its three new constants, so the landed bed is one point and one rendered point per constant fixes
# its leverage per cell — and the constants are chosen so that each ladder document attributes
# cleanly:
#
#   `rimLevelGain` and `rimEnvGain` are multiplied by `present`, and `rimCollapsed` by `toneAdapt`,
#   and those two factors are complementary. So a document carrying a level gain AND a collapsed rim
#   moves the uncollapsed cells by the first alone and the collapsed cells by the second alone;
#   there is no cell where the two mix, and one capture answers two questions without ambiguity.
#
# Five points, GPU tier, `--set calibration,validation` — the HOLDOUT IS NOT CAPTURED here, and
# `mid-dark-solid__capsule-button` and the other holdout scenes are therefore not rendered at any
# ladder constant (X3). Everything goes to scratch through `--out-matrix` and `VITREA_WEB_CAPTURES`;
# nothing canonical is written.
#
# The GPU is shared: this script serialises every run and writes a DONE marker at the end.
#
# Usage: `bash ladder.sh <phase>` where phase is `probe` (the three leverage points) or `fit`
# (the two confirmation points `make-candidates` wrote from the probe's answers).
set -u
WORKTREE=/Users/new/Developer/GitHub/designer/.claude/worktrees/agent-aa0ee5ea92534c3fd
T=/Users/new/.claude/jobs/5c70e47f/tmp/w23/g0
C="$T/candidates"
PHASE="${1:-probe}"
unset VITREA_SCENES VITREA_FIXTURES
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
  run light-levelgain-1x apple-macos-26.5-1x-light-standard "$C/light-levelgain.json"
  run light-levelgain-2x apple-macos-26.5-2x-light-standard "$C/light-levelgain.json"
  run light-envgain-1x   apple-macos-26.5-1x-light-standard "$C/light-envgain.json"
  run dark-levelgain-1x  apple-macos-26.5-1x-dark-standard  "$C/dark-levelgain.json"
  run dark-levelgain-2x  apple-macos-26.5-2x-dark-standard  "$C/dark-levelgain.json"
else
  run light-fit-1x apple-macos-26.5-1x-light-standard "$C/light-fit.json"
  run light-fit-2x apple-macos-26.5-2x-light-standard "$C/light-fit.json"
  run dark-fit-1x  apple-macos-26.5-1x-dark-standard  "$C/dark-fit.json"
  run dark-fit-2x  apple-macos-26.5-2x-dark-standard  "$C/dark-fit.json"
fi
echo "ALL $PHASE RUNS DONE $(date +%H:%M:%S)" | tee -a "$LOG"
touch "$T/ladder/DONE-$PHASE"
