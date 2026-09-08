#!/bin/bash
# W24 G1 (b) — `solve-state.txt`: the collapse's and the solve's state on every cell the wave reads,
# off the calibration page's own published group state in the landed 0.12.0 reports.
set -eu
G1="$(cd "$(dirname "$0")" && pwd)"
PY=/Users/new/.claude/jobs/5c70e47f/tmp/venv/bin/python
W="${1:-/Users/new/Developer/GitHub/designer/packages/calibration/web-captures}"
CELLS=""
for s in 1x 2x; do
  for scene in impulse__capsule-button__rest impulse__capsule-button__rest-tint-orange \
               impulse__rrect-md__rest dark-solid__capsule-button__rest \
               dark-solid__capsule-button__rest-tint-orange dark-solid__rrect-md__rest \
               checkerboard__capsule-button__rest photo__capsule-button__rest \
               mid-dark-solid__capsule-button__rest light-solid__capsule-button__rest; do
    for scheme in light dark; do
      d="$W/apple-macos-26.5-$s-$scheme-standard/$scene"
      [ -f "$d/report__webgpu.json" ] && CELLS="$CELLS apple-macos-26.5-$s-$scheme-standard/$scene"
    done
  done
done
# shellcheck disable=SC2086
$PY "$G1/solve-state.py" "$W" $CELLS
