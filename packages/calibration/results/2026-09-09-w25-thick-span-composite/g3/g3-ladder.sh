#!/bin/bash
# W25 G3 — one ladder rung: a candidate material rendered over the probe set, GPU tier, to SCRATCH.
#
# `g3-probe-run.sh`'s sibling, and the difference is what it is for. The probe run captures the
# whole set on both tiers at the material the working tree carries; a rung captures the GPU tier
# only, at a material that lives in scratch and never enters a committed document. The CSS tier is
# not on the ladder because none of this wave's three constants reaches it: the share and the level
# are the renderer's, and the along-side field integrates to zero around the contour so the tier's
# one inset shadow cannot see it (G2 §4, X8's residual).
#
#   g3-ladder.sh <rung> <light-doc.json> <dark-doc.json>
#
# One capture process at a time (X4); everything under `--out-matrix` and `VITREA_WEB_CAPTURES` in
# scratch (X2). A DONE marker is written last so a background waiter has one file to watch.
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/../../../../.."
unset VITREA_SCENES VITREA_FIXTURES VITREA_MATRIX_PATH
RUNG=${1:?rung}
LIGHT=${2:?light document}
DARK=${3:?dark document}
T=/Users/new/.claude/jobs/5c70e47f/tmp/w25/g3/$RUNG
mkdir -p "$T"
export VITREA_WEB_CAPTURES="$T/web-captures"
MATRIX="$T/probe.json"
rm -f "$T/DONE" "$MATRIX"
LOG="$T/runs.log"
: > "$LOG"
cd packages/calibration
echo "=== $(date +%H:%M:%S) rung=$RUNG ==="
echo "=== light $(shasum -a 256 "$LIGHT" | cut -c1-12)  dark $(shasum -a 256 "$DARK" | cut -c1-12) ==="
run() {
  echo "=== $(date +%H:%M:%S) $1 ==="
  npx tsx cli/compare.ts --profile "$1" --material-profile "$2" --renderer webgpu \
    --set probe --alpha --write-partial --out-matrix "$MATRIX" >> "$LOG" 2>&1
  echo "    exit=$?"
}
run apple-macos-26.5-1x-light-standard "$LIGHT"
run apple-macos-26.5-2x-light-standard "$LIGHT"
run apple-macos-26.5-1x-dark-standard  "$DARK"
run apple-macos-26.5-2x-dark-standard  "$DARK"
echo "RUNG $RUNG DONE $(date +%H:%M:%S)"
touch "$T/DONE"
