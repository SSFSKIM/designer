#!/bin/bash
# W23 G1 — every ladder point read by the wave's own instrument (X1), the same reader G0 wrote.
#
# `read-contour.py` is G0's, copied beside this gate's evidence rather than referenced across
# directories, so that this gate's numbers can be reproduced from this gate's directory alone.
#
# Usage: `bash g1-read-ladder.sh` — reads every point that has captures under the scratch ladder.
set -eu
PY=/Users/new/.claude/jobs/5c70e47f/tmp/venv/bin/python
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKTREE="$(cd "$HERE/../../../../.." && pwd)"
T=/Users/new/.claude/jobs/5c70e47f/tmp/w23/g1/ladder
SCENES="$WORKTREE/apps/reference-apple/scenes.json"
FIXTURES="$WORKTREE/apps/reference-apple/fixtures"

mkdir -p "$HERE/ladder"
read_one() {
  local label=$1 profile=$2
  [ -d "$T/$label/web-captures" ] || { echo "skip $label (no captures)"; return 0; }
  "$PY" "$HERE/read-contour.py" --scenes "$SCENES" --fixtures "$FIXTURES" --profile "$profile" \
    --captures "$T/$label/web-captures" --tier webgpu --sets calibration,validation \
    --json "$HERE/ladder/$label.json" > "$HERE/ladder/$label.txt" 2>/dev/null
  echo "read $label"
}

for LABEL in base confirm confirm2; do
  read_one "$LABEL-light-1x" apple-macos-26.5-1x-light-standard
  read_one "$LABEL-light-2x" apple-macos-26.5-2x-light-standard
  read_one "$LABEL-dark-1x"  apple-macos-26.5-1x-dark-standard
  read_one "$LABEL-dark-2x"  apple-macos-26.5-2x-dark-standard
done
read_one w2x12-light-2x apple-macos-26.5-2x-light-standard
read_one w2x12-dark-2x  apple-macos-26.5-2x-dark-standard
read_one tk1-light-1x   apple-macos-26.5-1x-light-standard
read_one tk1-dark-1x    apple-macos-26.5-1x-dark-standard
