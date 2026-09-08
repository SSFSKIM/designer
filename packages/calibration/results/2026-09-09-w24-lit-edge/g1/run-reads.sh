#!/bin/bash
# W24 G1 (b) — the impulse read: the four impulse cells, native against the landed 0.12.0 captures.
# `--web` points at a captures directory so the same script re-reads a scratch ladder's output.
set -euo pipefail
R="/Users/new/Developer/GitHub/designer"
G1="$R/.claude/worktrees/agent-aa8a0b1f92b46418f/packages/calibration/results/2026-09-09-w24-lit-edge/g1"
PY="/Users/new/.claude/jobs/5c70e47f/tmp/venv/bin/python"
WEB="${1:-$R/packages/calibration/web-captures}"
LABEL="${2:-landed}"
cd "$R/.claude/worktrees/agent-aa8a0b1f92b46418f"

read_cell () {  # profile scene component scale
  local prof="$1" scene="$2" comp="$3" scale="$4"
  $PY "$G1/read-impulse.py" \
    --bg "apps/reference-apple/fixtures/backgrounds/impulse@${scale}x.png" \
    --scale "$scale" --component "$comp" --title "$prof $scene" \
    --src "native=$R/apps/reference-apple/fixtures/$prof/$scene.png" \
    --src "$LABEL=$WEB/$prof/$scene/${scene}__webgpu.png"
}

$PY "$G1/read-impulse.py" --validate
for s in 1 2; do
  read_cell "apple-macos-26.5-${s}x-light-standard" impulse__capsule-button__rest capsule-button "$s"
  read_cell "apple-macos-26.5-${s}x-dark-standard"  impulse__capsule-button__rest capsule-button "$s"
  read_cell "apple-macos-26.5-${s}x-light-standard" impulse__rrect-md__rest       rrect-md       "$s"
done
