#!/bin/bash
# W22 G1 (3a) — both canonical beds read per side under the DECLARED geometry, before and after.
#
# The reader is W21's `g0/read.py`, unchanged, which is the wave's instrument (X2). The BEFORE
# column is the canonical `web-captures/` in the MAIN checkout — the W21 bed at the 0.10.0 landing,
# which is what clause 2 and clause 4 are stated against — and the AFTER column is this gate's dry
# run in scratch. The native side is the committed fixtures in both columns, so a column's
# difference is the fitted constant and nothing else.
#
# Four standard profiles x {webgpu, css} x {before, after}. The CSS tier is read in BOTH columns
# this time, unlike G0's: the CSS tier draws no sweep, so G0 had no "after" to take, but W22 G1's
# constant reaches the CSS tier through `interiorBandLight`'s derived interior level, so its
# captures move and have to be read rather than assumed.
#
# `--sets calibration,validation,holdout`: this gate opens the holdout (X5), so the holdout cells
# are read here for the first time at the corrected input.
#
# Usage: `bash read-canonical.sh <afterCaptures> <beforeCaptures>`
set -eu
PY=/Users/new/.claude/jobs/5c70e47f/tmp/venv/bin/python
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKTREE="$(cd "$HERE/../../../../.." && pwd)"
READER="$WORKTREE/packages/calibration/results/2026-09-06-w21-dark-scheme/g0/read.py"
SCENES="$WORKTREE/apps/reference-apple/scenes.json"
FIXTURES="$WORKTREE/apps/reference-apple/fixtures"
AFTER="${1:?usage: read-canonical.sh <afterCaptures> <beforeCaptures>}"
BEFORE="${2:?}"

mkdir -p "$HERE/canonical-reads"
for PROFILE in apple-macos-26.5-1x-light-standard apple-macos-26.5-2x-light-standard \
               apple-macos-26.5-1x-dark-standard apple-macos-26.5-2x-dark-standard; do
  for TIER in webgpu css; do
    for WHEN in before after; do
      [ "$WHEN" = before ] && CAP="$BEFORE" || CAP="$AFTER"
      OUT="$HERE/canonical-reads/$PROFILE-$TIER-$WHEN"
      "$PY" "$READER" --scenes "$SCENES" --fixtures "$FIXTURES" --profile "$PROFILE" \
        --captures "$CAP" --tier "$TIER" --sets calibration,validation,holdout \
        --json "$OUT.json" > "$OUT.txt"
      echo "read $PROFILE / $TIER / $WHEN"
    done
  done
done
