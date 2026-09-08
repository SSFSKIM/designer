#!/bin/bash
# W23 G3 — the tinted rows read for HUE as well as amplitude, on the reader this gate extended.
#
# Three columns, all through the same instrument: the NATIVE fixtures, the LANDED 0.11.0 bed (the
# canonical `web-captures/` in the main checkout) and G1's dry run in scratch. The hue clause is
# stated on the contour ROW's straight-span mean colour, so the reader now carries `row0Rgb` and
# `row0Oklab` beside the amplitude columns it already had.
#
# Reads only; nothing is captured and no holdout is spent.
#
# Usage: bash read-chroma.sh <label> <capturesDir>
set -eu
PY=/Users/new/.claude/jobs/5c70e47f/tmp/venv/bin/python
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKTREE="$(cd "$HERE/../../../../.." && pwd)"
SCENES="$WORKTREE/apps/reference-apple/scenes.json"
FIXTURES="$WORKTREE/apps/reference-apple/fixtures"
LABEL="${1:?usage: read-chroma.sh <label> <capturesDir>}"
CAPS="${2:?}"
mkdir -p "$HERE/reads"
for PROFILE in apple-macos-26.5-1x-light-standard apple-macos-26.5-2x-light-standard \
               apple-macos-26.5-1x-dark-standard apple-macos-26.5-2x-dark-standard; do
  for TIER in webgpu css; do
    OUT="$HERE/reads/$LABEL-$PROFILE-$TIER"
    [ -d "$CAPS/$PROFILE" ] || { echo "skip $LABEL/$PROFILE (no captures)"; continue; }
    "$PY" "$HERE/read-contour.py" --scenes "$SCENES" --fixtures "$FIXTURES" --profile "$PROFILE" \
      --captures "$CAPS" --tier "$TIER" --sets calibration,validation \
      --json "$OUT.json" > "$OUT.txt" 2>/dev/null
    echo "read $LABEL / $PROFILE / $TIER"
  done
done
