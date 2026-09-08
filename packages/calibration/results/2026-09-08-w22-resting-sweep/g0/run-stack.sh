#!/bin/bash
# W22 G0 (e2) — the nested pane read per pane, on both beds, both tiers, both scales.
#
# The web column is the CANONICAL `web-captures/` in the main checkout — the recorded W21-landing
# bed. It is not a new holdout read: both `glass-over-glass` cells are in the holdout split, the
# wave's one holdout read belongs to G1 (X5), and no capture is taken here. What is read is the
# reference's own fixtures and captures that already exist as committed evidence.
#
# The injection check (X3) runs once, on the first cell of the first read, and its recovery error is
# the instrument's floor on this geometry.
#
# Usage: `bash run-stack.sh`
set -eu
PY=/Users/new/.claude/jobs/5c70e47f/tmp/venv/bin/python
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKTREE="$(cd "$HERE/../../../../.." && pwd)"
SCENES="$WORKTREE/apps/reference-apple/scenes.json"
FIXTURES="$WORKTREE/apps/reference-apple/fixtures"
CAPTURES=/Users/new/Developer/GitHub/designer/packages/calibration/web-captures

mkdir -p "$HERE/stack-reads"
FIRST=--inject-check
for PROFILE in apple-macos-26.5-1x-light-standard apple-macos-26.5-2x-light-standard \
               apple-macos-26.5-1x-dark-standard apple-macos-26.5-2x-dark-standard; do
  for TIER in webgpu css; do
    OUT="$HERE/stack-reads/$PROFILE-$TIER"
    "$PY" "$HERE/read-stack.py" --scenes "$SCENES" --fixtures "$FIXTURES" --profile "$PROFILE" \
      --captures "$CAPTURES" --tier "$TIER" --assert-placement $FIRST \
      --json "$OUT.json" > "$OUT.txt" 2>/dev/null
    FIRST=
    echo "read $PROFILE / $TIER -> stack-reads/$(basename "$OUT").json"
  done
done
