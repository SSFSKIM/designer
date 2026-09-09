#!/bin/bash
# W25 G3b — one rung of the JOINT (exponent, slope) ladder: the solid rows only, to SCRATCH.
#
# W25 Decision Log 6 re-opens W24's `optics.regular.rimLitExponent` so that it can be fitted
# TOGETHER with W25's `optics.regular.rimAlongSideSlope`. The two multiply the same rim amplitude
# and both peak on the same top-left/bottom-right diagonal, so neither can be read without the
# other: the exponent was fitted with the position term absent and absorbed part of its grading on
# the corner arcs, which is what G3's dry run measured (`g3-dryrun.md` §7.11).
#
# A rung renders only what the two readers read — the untinted FLAT-SOLID rows, where the
# along-side term is separable from the lens at all (G0 §4) and where W24's angular clause was
# stated — on the four standard profiles. That is about sixteen scenes a profile rather than a
# whole bed, so a rung is a minute and a grid over the plane is affordable.
#
# THE HOLDOUT IS NOT RENDERED. `mid-dark-solid__capsule-button__rest` is the bed's only holdout
# solid, and X3 reserves it for the dry run; the fit never opens it. It is listed below by name so
# that its absence is a decision on the page rather than an oversight.
#
#   g3b-ladder.sh <rung> <light-doc.json> <dark-doc.json>
#
# One capture process at a time (X4); everything under `--out` in scratch (X2). A DONE marker is
# written last so a background waiter has one file to watch.
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/../../../../.."
unset VITREA_MATRIX_PATH
RUNG=${1:?rung}
LIGHT=${2:?light document}
DARK=${3:?dark document}
REPO="$(pwd)"
T=/Users/new/.claude/jobs/5c70e47f/tmp/w25/g3b/$RUNG
mkdir -p "$T"
rm -f "$T/DONE"
LOG="$T/runs.log"
: > "$LOG"

# The fitting rows: the five untinted solid CALIBRATION cells of the canonical bed and the twelve
# solid rows of the probe set. `mid-dark-solid__capsule-button__rest` (holdout) is deliberately
# absent.
SCENES="light-solid__capsule-button__rest dark-solid__capsule-button__rest \
light-solid__rrect-md__rest dark-solid__rrect-md__rest light-solid__rrect-ml__rest \
light-solid__rrect-sm__rest light-solid__rrect-lg__rest dark-solid__rrect-sm__rest \
dark-solid__rrect-lg__rest mid-dark-solid__rrect-sm__rest mid-dark-solid__rrect-md__rest \
mid-dark-solid__rrect-lg__rest dark-solid__rrect-48__rest dark-solid__rrect-64__rest \
dark-solid__rrect-80__rest dark-solid__rrect-ml__rest dark-solid__rrect-md-clear20__rest"

cd packages/calibration
echo "=== $(date +%H:%M:%S) rung=$RUNG ==="
echo "=== light $(shasum -a 256 "$LIGHT" | cut -c1-12)  dark $(shasum -a 256 "$DARK" | cut -c1-12) ==="
run() {  # run <profile> <scale> <scheme> <document>
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
echo "RUNG $RUNG DONE $(date +%H:%M:%S)"
touch "$T/DONE"
