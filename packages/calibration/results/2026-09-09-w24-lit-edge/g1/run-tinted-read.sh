#!/bin/bash
# W24 G1 (b) — the tinted collapsed capsule, which is the fit's CALIBRATION-side row.
#
# `impulse__capsule-button__rest-tint-orange` is in the calibration set where
# `impulse__capsule-button__rest` is validation, and it collapses just as fully (k = 1). Read
# beside the bare cell it tells whether the transmission the reference keeps survives paint —
# the same question W23 X4 asked of the collapsed rim and answered yes.
set -eu
G1="$(cd "$(dirname "$0")" && pwd)"
PY=/Users/new/.claude/jobs/5c70e47f/tmp/venv/bin/python
R=/Users/new/Developer/GitHub/designer
W="${1:-$R/packages/calibration/web-captures}"
LABEL="${2:-landed}"
cd "$R/.claude/worktrees/agent-aa8a0b1f92b46418f"
SCENE=impulse__capsule-button__rest-tint-orange
for s in 1 2; do
  for scheme in light dark; do
    P="apple-macos-26.5-${s}x-${scheme}-standard"
    F="$R/apps/reference-apple/fixtures/$P/$SCENE.png"
    C="$W/$P/$SCENE/${SCENE}__webgpu.png"
    [ -f "$F" ] || continue
    [ -f "$C" ] || continue
    $PY "$G1/read-impulse.py" \
      --bg "apps/reference-apple/fixtures/backgrounds/impulse@${s}x.png" \
      --scale "$s" --component capsule-button --title "$P $SCENE" \
      --src "native=$F" --src "$LABEL=$C"
  done
done
