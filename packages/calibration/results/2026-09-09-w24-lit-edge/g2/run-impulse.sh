#!/bin/bash
# W24 G2 — clause 2: the collapsed impulse capsule's centre dot, native against the landed bed and
# against this gate's dry run, in both schemes at both scales.
#
# G1's instrument unchanged (`g1/read-impulse.py`, validated on the background itself, where a
# 4 CSS px dot reads peak 1.0, FWHM 4.00 CSS px and integral 4.000 exactly at both scales). Three
# sources per cell so the clause and its baseline are on one line: the committed fixture, the
# 0.12.0 capture the wave is stated against, and the dry run.
#
# The clause as W24 Decision Log 2 (f) re-declared it: the centre dot's peak within 0.005 of the
# reference's, with the FWHM and the collapsed body RECORDED. Both of those are printed for every
# dot the shape covers, so the two sub-clauses the wave carries by name are legible here rather
# than only in the findings.
#
# Usage: `bash run-impulse.sh <afterCaptures> [beforeCaptures] > impulse-read.txt`
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKTREE="$(cd "$HERE/../../../../.." && pwd)"
MAIN=/Users/new/Developer/GitHub/designer
PY=/Users/new/.claude/jobs/5c70e47f/tmp/venv/bin/python
IMPULSE="$HERE/../g1/read-impulse.py"
AFTER="${1:?usage: run-impulse.sh <afterCaptures> [beforeCaptures]}"
BEFORE="${2:-$MAIN/packages/calibration/web-captures}"
cd "$WORKTREE"

echo "W24 G2 — clause 2: the collapsed impulse capsule's dot, native | landed 0.12.0 | this gate"
echo "peak is the excess over the LOCAL body in linear luma; fwhm is in CSS px; the body printed"
echo "under each source is the mean over the declared shape eroded 6 CSS px."
echo

$PY "$IMPULSE" --validate

read_cell () {  # profile scene component scale tier
  local prof="$1" scene="$2" comp="$3" scale="$4" tier="$5"
  $PY "$IMPULSE" \
    --bg "apps/reference-apple/fixtures/backgrounds/impulse@${scale}x.png" \
    --scale "$scale" --component "$comp" --title "$prof $scene ($tier)" \
    --src "native=$WORKTREE/apps/reference-apple/fixtures/$prof/$scene.png" \
    --src "landed=$BEFORE/$prof/$scene/${scene}__${tier}.png" \
    --src "w24=$AFTER/$prof/$scene/${scene}__${tier}.png"
}

for s in 1 2; do
  for tier in webgpu css; do
    read_cell "apple-macos-26.5-${s}x-light-standard" impulse__capsule-button__rest \
      capsule-button "$s" "$tier"
    read_cell "apple-macos-26.5-${s}x-dark-standard" impulse__capsule-button__rest \
      capsule-button "$s" "$tier"
    read_cell "apple-macos-26.5-${s}x-light-standard" impulse__rrect-md__rest rrect-md "$s" "$tier"
  done
done
