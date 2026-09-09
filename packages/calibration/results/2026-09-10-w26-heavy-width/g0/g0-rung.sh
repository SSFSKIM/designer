#!/bin/bash
# W26 G0 — one ladder rung: a candidate material rendered over this child's ladder rows, GPU tier,
# to SCRATCH.
#
# W25 G3's `g3-ladder.sh` narrowed to the rows a WIDTH can move. G0's question is a mechanism's,
# not a material's, so it does not need the whole probe set at four profiles: reader A answers on
# the three impulse rows, readers B and C on the two coarse checkerboards, and X5 is read on the
# thin cells (span <= 44) — all of them in the LIGHT scheme at both scales, because a heavy tap is
# a scheme-independent mechanism and the dark bed would only double the capture time. The rows are
# named rather than taken from a set because `impulse__rrect-md` is a validation row and the rest
# are probe rows, so no single `--set` selects them.
#
#   g0-rung.sh <rung> <light-doc.json> <dark-doc.json> [scales]
#
# `scales` is `1x`, `2x` or `both` (default). One capture process at a time (X4); everything under
# `--out-matrix` and `VITREA_WEB_CAPTURES` in scratch (X2). A DONE marker is written last so a
# background waiter has one file to watch.
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/../../../../.."
unset VITREA_SCENES VITREA_FIXTURES VITREA_MATRIX_PATH
RUNG=${1:?rung}
LIGHT=${2:?light document}
DARK=${3:?dark document}
SCALES=${4:-both}
T=/Users/new/.claude/jobs/5c70e47f/tmp/w26/g0/$RUNG
mkdir -p "$T"
export VITREA_WEB_CAPTURES="$T/web-captures"
MATRIX="$T/rung.json"
rm -f "$T/DONE" "$MATRIX"
LOG="$T/runs.log"
: > "$LOG"

# Reader A's rows, readers B and C's rows, and X5's thin rows, in one comma list.
SCENES=\
impulse__rrect-md__rest,impulse__rrect-ml__rest,impulse__rrect-lg__rest,\
checkerboard-32__rrect-md__rest,checkerboard-32__rrect-ml__rest,checkerboard-32__rrect-lg__rest,\
checkerboard-64__rrect-md__rest,checkerboard-64__rrect-ml__rest,checkerboard-64__rrect-lg__rest,\
impulse__rrect-sm__rest,checkerboard-32__rrect-sm__rest,checkerboard-64__rrect-sm__rest,\
checkerboard-32__capsule-button__rest,checkerboard-64__capsule-button__rest,\
checkerboard-4__capsule-button__rest,light-solid__rrect-sm__rest,\
checkerboard__rrect-sm__rest,photo__rrect-sm__rest

cd packages/calibration
echo "=== $(date +%H:%M:%S) rung=$RUNG scales=$SCALES ==="
echo "=== light $(shasum -a 256 "$LIGHT" | cut -c1-12)  dark $(shasum -a 256 "$DARK" | cut -c1-12) ==="
run() {
  echo "=== $(date +%H:%M:%S) $1 ==="
  npx tsx cli/compare.ts --profile "$1" --material-profile "$2" --renderer webgpu \
    --set probe,validation,calibration --scene "$SCENES" \
    --alpha --write-partial --out-matrix "$MATRIX" >> "$LOG" 2>&1
  echo "    exit=$?"
}
case "$SCALES" in
  1x|both) run apple-macos-26.5-1x-light-standard "$LIGHT" ;;
esac
case "$SCALES" in
  2x|both) run apple-macos-26.5-2x-light-standard "$LIGHT" ;;
esac
echo "RUNG $RUNG DONE $(date +%H:%M:%S)"
touch "$T/DONE"
