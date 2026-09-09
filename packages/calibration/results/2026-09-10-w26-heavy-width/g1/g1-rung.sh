#!/bin/bash
# W26 G1 — one rung: a candidate material rendered over this child's rows, GPU tier, to SCRATCH.
#
# G0's `g0-rung.sh` with one axis added. G0 asked a mechanism's question and eighteen named rows in
# the light scheme answered it; G1 fits constants, and a fit's off-row checks, X5's thin cells and
# the level's solids are not the same eighteen rows. So the row set is an argument:
#
#   ladder  the eighteen G0 named — reader A's three impulse spans, readers B and C's coarse
#           checkerboards, and X5's thin cells — light only, both scales. What a WIDTH ladder needs,
#           and cheap enough to run ten of.
#   probe   `--set probe` at the four standard profiles: 52 scenes x {1x,2x} x {light,dark}. What
#           the share, the level, the mid-span "one width per source" check and the thin-cell sweep
#           need, because those questions are asked of spans and backdrops the ladder does not carry.
#
#   g1-rung.sh <rung> <light-doc.json> <dark-doc.json> [ladder|probe] [1x|2x|both]
#
# One capture process at a time (X4); everything under `--out-matrix` and `VITREA_WEB_CAPTURES` in
# scratch (X2) — the canonical matrix, `web-captures/`, `fixtures/` and `scenes.json` are never
# written. A DONE marker is written last so a background waiter has one file to watch.
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/../../../../.."
unset VITREA_SCENES VITREA_FIXTURES VITREA_MATRIX_PATH
RUNG=${1:?rung}
LIGHT=${2:?light document}
DARK=${3:?dark document}
ROWS=${4:-ladder}
SCALES=${5:-both}
T=/Users/new/.claude/jobs/5c70e47f/tmp/w26/g1/$RUNG
mkdir -p "$T"
export VITREA_WEB_CAPTURES="$T/web-captures"
MATRIX="$T/rung.json"
rm -f "$T/DONE" "$MATRIX"
LOG="$T/runs.log"
: > "$LOG"

LADDER_SCENES=\
impulse__rrect-md__rest,impulse__rrect-ml__rest,impulse__rrect-lg__rest,\
checkerboard-32__rrect-md__rest,checkerboard-32__rrect-ml__rest,checkerboard-32__rrect-lg__rest,\
checkerboard-64__rrect-md__rest,checkerboard-64__rrect-ml__rest,checkerboard-64__rrect-lg__rest,\
impulse__rrect-sm__rest,checkerboard-32__rrect-sm__rest,checkerboard-64__rrect-sm__rest,\
checkerboard-32__capsule-button__rest,checkerboard-64__capsule-button__rest,\
checkerboard-4__capsule-button__rest,light-solid__rrect-sm__rest,\
checkerboard__rrect-sm__rest,photo__rrect-sm__rest

cd packages/calibration
echo "=== $(date +%H:%M:%S) rung=$RUNG rows=$ROWS scales=$SCALES ==="
echo "=== light $(shasum -a 256 "$LIGHT" | cut -c1-12)  dark $(shasum -a 256 "$DARK" | cut -c1-12) ==="
run() {
  echo "=== $(date +%H:%M:%S) $1 ==="
  if [ "$ROWS" = "probe" ]; then
    npx tsx cli/compare.ts --profile "$1" --material-profile "$2" --renderer webgpu \
      --set probe --alpha --write-partial --out-matrix "$MATRIX" >> "$LOG" 2>&1
  else
    npx tsx cli/compare.ts --profile "$1" --material-profile "$2" --renderer webgpu \
      --set probe,validation,calibration --scene "$LADDER_SCENES" \
      --alpha --write-partial --out-matrix "$MATRIX" >> "$LOG" 2>&1
  fi
  echo "    exit=$?"
}
case "$SCALES" in
  1x|both) run apple-macos-26.5-1x-light-standard "$LIGHT" ;;
esac
case "$SCALES" in
  2x|both) run apple-macos-26.5-2x-light-standard "$LIGHT" ;;
esac
if [ "$ROWS" = "probe" ]; then
  case "$SCALES" in
    1x|both) run apple-macos-26.5-1x-dark-standard "$DARK" ;;
  esac
  case "$SCALES" in
    2x|both) run apple-macos-26.5-2x-dark-standard "$DARK" ;;
  esac
fi
echo "RUNG $RUNG DONE $(date +%H:%M:%S)"
touch "$T/DONE"
