#!/bin/bash
# W22 G1 (3d) — the nested pane read PER PANE, both beds, both tiers, both scales, before and after.
#
# G0's `read-stack.py`, unchanged (X2's stack instrument: the base's declared box with the overlay's
# dilated box cut out, the overlay's box, each eroded 6 CSS px, each with its own 3 px rim band per
# side). G0 could take no "after" column at all — both `glass-over-glass` cells are HOLDOUT and X5
# reserves the wave's one holdout read for this gate — so this is the FIRST reading of these cells
# against the reference at the corrected input (W22 G3's backdrop-stack fix, claims §5.95).
#
# Three columns per profile per tier: native (the committed fixture, the same in both), before (the
# canonical `web-captures/` in the main checkout, the W21 bed) and after (this gate's dry run).
#
# Usage: `bash run-stack.sh <afterCaptures> <beforeCaptures>`
set -eu
PY=/Users/new/.claude/jobs/5c70e47f/tmp/venv/bin/python
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKTREE="$(cd "$HERE/../../../../.." && pwd)"
READER="$WORKTREE/packages/calibration/results/2026-09-08-w22-resting-sweep/g0/read-stack.py"
SCENES="$WORKTREE/apps/reference-apple/scenes.json"
FIXTURES="$WORKTREE/apps/reference-apple/fixtures"
AFTER="${1:?usage: run-stack.sh <afterCaptures> <beforeCaptures>}"
BEFORE="${2:?}"

mkdir -p "$HERE/stack-reads"
# The placement assertion and the injection recovery, once, so the instrument's own numbers sit
# beside this gate's readings rather than only in G0's.
"$PY" "$READER" --scenes "$SCENES" --fixtures "$FIXTURES" \
  --profile apple-macos-26.5-2x-dark-standard --assert-placement --inject-check \
  > "$HERE/stack-reads/instrument.txt" 2>&1
echo "instrument -> stack-reads/instrument.txt"

for PROFILE in apple-macos-26.5-1x-light-standard apple-macos-26.5-2x-light-standard \
               apple-macos-26.5-1x-dark-standard apple-macos-26.5-2x-dark-standard; do
  for TIER in webgpu css; do
    for WHEN in before after; do
      [ "$WHEN" = before ] && CAP="$BEFORE" || CAP="$AFTER"
      OUT="$HERE/stack-reads/$PROFILE-$TIER-$WHEN"
      "$PY" "$READER" --scenes "$SCENES" --fixtures "$FIXTURES" --profile "$PROFILE" \
        --captures "$CAP" --tier "$TIER" --json "$OUT.json" > "$OUT.txt" 2>&1
      echo "read $PROFILE / $TIER / $WHEN"
    done
  done
done
