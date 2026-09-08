#!/bin/bash
# W22 G0 — the fit's rendered points and the collapse prediction, to SCRATCH.
#
# Three candidate documents, each the shipped document plus its own named leaves
# (`make-candidates.mjs`), rendered on the canonical bed at the gate:
#
#   light-spec0-rim018   the light profile with `optics.regular.specularGain` 0 and nothing else —
#                        the test of whether the specular's rows separate it at all, since the
#                        shipped 0.55 is the only thing that can make top differ from bottom.
#   light-spec0-rim004   the same with `rimAlpha` 0.04, so the two points fix the line the rim
#                        excess follows in `rimAlpha` (W21 G1's method: the rim is additive).
#   dark-tonemax0        the dark patch with `backdropToneMax` 0 — the prediction the design asks
#                        for, so that what un-collapsing the dark material costs and buys is a
#                        measured number on every dark cell rather than an argument.
#
# GPU tier, both scales per scheme, `--set calibration,validation`. The holdout is not read.
# Everything goes to scratch through `--out-matrix` and `VITREA_WEB_CAPTURES`.
#
# The GPU is shared: one capture process at a time, and this script serialises every run.
set -u
cd /Users/new/Developer/GitHub/designer/.claude/worktrees/agent-ac5e591b52341c4ce
unset VITREA_SCENES VITREA_FIXTURES
T=/Users/new/.claude/jobs/5c70e47f/tmp/w22/g0
C="$T/candidates"
mkdir -p "$T/fit"
rm -f "$T/fit/DONE"
LOG="$T/fit/fit-runs.log"
: > "$LOG"
cd packages/calibration
run() {
  local label=$1 profile=$2 doc=$3
  local out="$T/fit/$label"
  mkdir -p "$out"
  echo "=== $(date +%H:%M:%S) $label / $profile ==="
  VITREA_WEB_CAPTURES="$out/web-captures" npx tsx cli/compare.ts --profile "$profile" \
    --material-profile "$doc" --renderer webgpu --set calibration,validation \
    --allow-colourless-tints --write-partial --out-matrix "$out/matrix.json" >> "$LOG" 2>&1
  echo "    exit=$?"
}
run light-spec0-rim018-1x apple-macos-26.5-1x-light-standard "$C/light-spec0-rim018.json"
run light-spec0-rim018-2x apple-macos-26.5-2x-light-standard "$C/light-spec0-rim018.json"
run light-spec0-rim004-1x apple-macos-26.5-1x-light-standard "$C/light-spec0-rim004.json"
run light-spec0-rim004-2x apple-macos-26.5-2x-light-standard "$C/light-spec0-rim004.json"
run dark-tonemax0-1x apple-macos-26.5-1x-dark-standard "$C/dark-tonemax0.json"
run dark-tonemax0-2x apple-macos-26.5-2x-dark-standard "$C/dark-tonemax0.json"
echo "ALL FIT RUNS DONE $(date +%H:%M:%S)"
touch "$T/fit/DONE"
