#!/bin/bash
# W24 G1 (c) — one ladder point read: the dot, the structured cells, and what did NOT move.
#
# Three readings per point, in the order the acceptance asks them:
#
#  1. the impulse instrument on every impulse cell the run captured, native against the rung;
#  2. the structure read on the dark thin structured cells and the collapsed stop cells;
#  3. the byte-identity diff of every capture in the rung against the landed 0.12.0 capture of the
#     same cell — S10's "nothing the mechanism does not reach moves", as digests rather than as an
#     argument. A cell whose collapse `k` is 0 must be identical at any value of the constant.
#
# Usage: `bash read-ladder.sh <label> <profileKey> <scale>`
set -u
WORKTREE=/Users/new/Developer/GitHub/designer/.claude/worktrees/agent-aa8a0b1f92b46418f
G1="$WORKTREE/packages/calibration/results/2026-09-09-w24-lit-edge/g1"
PY=/Users/new/.claude/jobs/5c70e47f/tmp/venv/bin/python
T=/Users/new/.claude/jobs/5c70e47f/tmp/w24/g1
LABEL="${1:?label}"
PROFILE="${2:?profile key}"
SCALE="${3:?scale}"
W="$T/ladder/$LABEL/web-captures"
LANDED=/Users/new/Developer/GitHub/designer/packages/calibration/web-captures
cd "$WORKTREE"

echo "######## $LABEL — $PROFILE (${SCALE}x), captures under $W"

for scene in impulse__capsule-button__rest impulse__capsule-button__rest-tint-orange; do
  [ -f "$W/$PROFILE/$scene/${scene}__webgpu.png" ] || continue
  $PY "$G1/read-impulse.py" \
    --bg "apps/reference-apple/fixtures/backgrounds/impulse@${SCALE}x.png" \
    --scale "$SCALE" --component capsule-button --title "$PROFILE $scene" \
    --src "native=apps/reference-apple/fixtures/$PROFILE/$scene.png" \
    --src "rung=$W/$PROFILE/$scene/${scene}__webgpu.png"
done
if [ -f "$W/$PROFILE/impulse__rrect-md__rest/impulse__rrect-md__rest__webgpu.png" ]; then
  $PY "$G1/read-impulse.py" \
    --bg "apps/reference-apple/fixtures/backgrounds/impulse@${SCALE}x.png" \
    --scale "$SCALE" --component rrect-md --title "$PROFILE impulse__rrect-md__rest" \
    --src "native=apps/reference-apple/fixtures/$PROFILE/impulse__rrect-md__rest.png" \
    --src "rung=$W/$PROFILE/impulse__rrect-md__rest/impulse__rrect-md__rest__webgpu.png"
fi

echo
echo "-- the structured and stop cells (body, passed structure)"
CELLS=""
for s in checkerboard__capsule-button__rest photo__capsule-button__rest \
         impulse__capsule-button__rest dark-solid__capsule-button__rest; do
  [ -f "$W/$PROFILE/$s/${s}__webgpu.png" ] && CELLS="$CELLS $PROFILE/$s/capsule-button/$SCALE"
done
# shellcheck disable=SC2086
[ -n "$CELLS" ] && $PY "$G1/read-structure.py" "$W" $CELLS

echo
echo "-- byte identity against the landed 0.12.0 capture, per cell"
for dir in "$W/$PROFILE"/*/; do
  scene=$(basename "$dir")
  a="$dir/${scene}__webgpu.png"
  b="$LANDED/$PROFILE/$scene/${scene}__webgpu.png"
  [ -f "$a" ] && [ -f "$b" ] || continue
  if cmp -s "$a" "$b"; then printf '  same      %s\n' "$scene"
  else printf '  MOVED     %s\n' "$scene"; fi
done
