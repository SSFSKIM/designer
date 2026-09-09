#!/bin/bash
# W25 G3 — the dry run on the CANONICAL bed at the frozen configuration, to SCRATCH (X3, X5).
#
# What is frozen: G0's, G1's and G2's branches merged into main, plus this gate's one landed
# constant —
#
#   both   optics.regular.rimAlongSideSlope 0.45 (new, on the material's default; the light patch
#          names it and the dark difference document inherits it)
#   none   sizeScatterHeavyShareThick1x / …2x and sizeToneLevelFar stay at 0, declined on the probe
#          set's own measurement (this document's §1)
#   css    nothing: the field's integral around the contour is exactly zero, so `interiorBandLight`
#          returns the same number and the mirror carries no new constant
#
# resolvedMaterialSha256 290f52cb025fce7b (light, was 52a633135b9da151) and 64ef5c3002d15009
# (dark, was 2f47777637f8df50). BOTH documents move this wave, so all six profiles are re-run and
# not one of them rides along as a byte check.
#
# THIS SCRIPT RUNS THE CALIBRATION AND VALIDATION COLUMNS ONLY. The holdout is `g3-holdout-run.sh`
# and it is not run until every clause and every stop has been read on these rows: it is the wave's
# ONE holdout read (X3), and G4 reproduces it byte for byte from the main checkout.
#
# The GPU tier runs before the CSS tier within each column so every dom cell's coherence axis is
# measured against a GPU capture already on disk. The flags are the canonical rebuild's — `--alpha`
# for the declaration-conformance rows and `--write-partial` so a cell whose axis is absent is still
# recorded — because G4 has to reproduce these bytes with them.
#
# Everything goes to scratch: `--out-matrix` and `VITREA_WEB_CAPTURES` both move, so the canonical
# `results/matrix.json` and `web-captures/` are untouched in this worktree AND in the main checkout,
# and `apps/reference-apple/fixtures/` and `scenes.json` are read-only inputs throughout.
#
# The GPU is shared: one capture process at a time, and this script serialises every run.
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/../../../../.."
unset VITREA_SCENES VITREA_FIXTURES VITREA_MATRIX_PATH
T=/Users/new/.claude/jobs/5c70e47f/tmp/w25/g3/dryrun
mkdir -p "$T"
export VITREA_WEB_CAPTURES="$T/web-captures"
MATRIX="$T/g3-dryrun.json"
rm -f "$T/DONE-calval"
LOG="$T/g3-runs.log"
: > "$LOG"
echo "=== $(date +%H:%M:%S) build ==="
pnpm -r build > "$T/build.log" 2>&1 || { echo "BUILD FAILED"; exit 1; }
echo "=== $(date +%H:%M:%S) HEAD $(git rev-parse --short HEAD) $(git status --short | wc -l | tr -d ' ') dirty ==="
cd packages/calibration
echo "=== light document $(shasum -a 256 profiles/apple-macos-26.5-1x-light-standard.json | cut -c1-12) ==="
echo "=== dark  document $(shasum -a 256 profiles/apple-macos-26.5-1x-dark-standard.json | cut -c1-12) ==="
LIGHT=profiles/apple-macos-26.5-1x-light-standard.json
DARK=profiles/apple-macos-26.5-1x-dark-standard.json
run() {
  local profile=$1 doc=$2 renderer=$3 sets=$4
  echo "=== $(date +%H:%M:%S) $profile / $renderer / $sets ==="
  npx tsx cli/compare.ts --profile "$profile" --material-profile "$doc" --renderer "$renderer" \
    --set "$sets" --alpha --write-partial --out-matrix "$MATRIX" >> "$LOG" 2>&1
  echo "    exit=$?"
}
SETS=calibration,validation
for RENDERER in webgpu css; do
  run apple-macos-26.5-1x-light-standard "$LIGHT" "$RENDERER" "$SETS"
  run apple-macos-26.5-2x-light-standard "$LIGHT" "$RENDERER" "$SETS"
  run apple-macos-26.5-1x-light-increased-contrast "$LIGHT" "$RENDERER" "$SETS"
  run apple-macos-26.5-1x-light-reduced-transparency "$LIGHT" "$RENDERER" "$SETS"
  run apple-macos-26.5-1x-dark-standard "$DARK" "$RENDERER" "$SETS"
  run apple-macos-26.5-2x-dark-standard "$DARK" "$RENDERER" "$SETS"
done
echo "ALL CALIBRATION/VALIDATION RUNS DONE $(date +%H:%M:%S)"
touch "$T/DONE-calval"
