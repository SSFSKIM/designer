#!/bin/bash
# W22 G1 (1) — the `specularGain` ladder, rendered on the LIGHT bed at both scales, to SCRATCH.
#
# Decision Log 2 (b) rules the constant is fitted PER CONTRAST — `T−B` and `L−R` per untinted solid
# cell — never on a mean pooled over sides, because G0 showed the pooled mean keeps the term by
# buying one side of a pair and breaking the other. A fit stated on a contrast needs the contrast
# rendered at more than the two points G0 had, so this is a ladder: eight documents that differ from
# the shipped light document in `optics.regular.specularGain` and in nothing else
# (`g0/make-candidates.mjs`, which writes a leaf override over a shipped document and nothing more).
#
# Only the five untinted solid CALIBRATION cells are captured. `mid-dark-solid__capsule-button` is
# a HOLDOUT scene (`scenes.json`'s split) and W22 X5 spends the wave's one holdout read at the dry
# run, so it cannot be a fit row; it is read once, afterwards, as a check.
#
# Everything goes to scratch: `--out-matrix` and `VITREA_WEB_CAPTURES` both move, so the canonical
# `results/matrix.json` and `web-captures/` are untouched in this worktree and in the main checkout.
#
# The GPU is shared: one capture process at a time, and this script serialises every run.
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/../../../../.."
unset VITREA_SCENES VITREA_FIXTURES
T=/Users/new/.claude/jobs/5c70e47f/tmp/w22/g1
C="$T/candidates"
mkdir -p "$T/ladder"
rm -f "$T/ladder/DONE"
LOG="$T/ladder/ladder-runs.log"
: > "$LOG"
SCENES=light-solid__capsule-button__rest,dark-solid__capsule-button__rest,light-solid__rrect-md__rest,dark-solid__rrect-md__rest,light-solid__rrect-ml__rest
cd packages/calibration
run() {
  local gain=$1 scale=$2
  local out="$T/ladder/$gain-$scale"
  mkdir -p "$out"
  echo "=== $(date +%H:%M:%S) $gain / $scale ==="
  VITREA_WEB_CAPTURES="$out/web-captures" npx tsx cli/compare.ts \
    --profile "apple-macos-26.5-$scale-light-standard" \
    --material-profile "$C/light-$gain.json" --renderer webgpu \
    --scene "$SCENES" --set calibration --allow-colourless-tints --write-partial \
    --out-matrix "$out/matrix.json" >> "$LOG" 2>&1
  echo "    exit=$?"
}
for GAIN in spec000 spec0025 spec005 spec010 spec015 spec025 spec040 spec055; do
  for SCALE in 1x 2x; do
    run "$GAIN" "$SCALE"
  done
done
echo "ALL LADDER RUNS DONE $(date +%H:%M:%S)"
touch "$T/ladder/DONE"
