#!/bin/bash
# W25 G3b — the check OFF the fitted rows: the checkerboard cells, at two materials.
#
# The joint pair is fitted on the flat SOLIDS, because that is the only backdrop on which the
# along-side term is separable from the lens at all (G0 §4: over a checkerboard the same reader
# correlates 0.85–0.96 with the backdrop's own level under the body). A fit made there has to be
# checked somewhere else, and the checkerboards are where the rim sits over structure — the rows
# the fit could most easily have bought its own improvement at the expense of.
#
# Two rungs and no more: the 0.13.0 material (exponent 1.15, slope 0) and the fitted pair. The
# quantity is W24's angular bin ERROR against the reference, which is the same quantity the fit
# minimises on the solids, read on rows no fit touched.
#
#   g3b-check.sh <tag> <light-doc.json> <dark-doc.json>
#
# One capture process at a time (X4); everything to scratch (X2).
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/../../../../.."
unset VITREA_MATRIX_PATH
TAG=${1:?tag}
LIGHT=${2:?light document}
DARK=${3:?dark document}
REPO="$(pwd)"
T=/Users/new/.claude/jobs/5c70e47f/tmp/w25/g3b/check-$TAG
mkdir -p "$T"
rm -f "$T/DONE"
LOG="$T/runs.log"
: > "$LOG"

# The canonical checkerboard cells that are not holdout, and the probe set's coarse checkerboards
# over the three thick spans — the rows a rim term over structure is read on.
SCENES="checkerboard__capsule-button__rest checkerboard__rrect-sm__rest \
checkerboard__rrect-md__rest checkerboard__rrect-ml__rest checkerboard__toolbar-group__rest \
checkerboard-32__rrect-md__rest checkerboard-32__rrect-ml__rest checkerboard-32__rrect-lg__rest \
checkerboard-64__rrect-md__rest checkerboard-64__rrect-ml__rest checkerboard-64__rrect-lg__rest"

cd packages/calibration
echo "=== $(date +%H:%M:%S) check=$TAG ==="
run() {
  echo "=== $(date +%H:%M:%S) $1 ==="
  # shellcheck disable=SC2086
  VITREA_FIXTURES="$REPO/apps/reference-apple/fixtures" \
  VITREA_SCENES="$REPO/apps/reference-apple/scenes.json" \
    pnpm exec tsx scripts/capture-web.ts $SCENES \
      --scale "$2" --color-scheme "$3" --renderer webgpu \
      --out "$T/$1" --material-profile "$4" >> "$LOG" 2>&1
  echo "    exit=$?"
}
run apple-macos-26.5-1x-light-standard 1 light "$LIGHT"
run apple-macos-26.5-2x-light-standard 2 light "$LIGHT"
run apple-macos-26.5-1x-dark-standard  1 dark  "$DARK"
run apple-macos-26.5-2x-dark-standard  2 dark  "$DARK"
echo "CHECK $TAG DONE $(date +%H:%M:%S)"
touch "$T/DONE"
