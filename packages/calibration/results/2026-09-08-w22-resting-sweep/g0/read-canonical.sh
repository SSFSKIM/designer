#!/bin/bash
# W22 G0 (c) — both canonical beds read per side under the DECLARED geometry, before and after.
#
# W21's `g1/read-canonical.sh` widened from the two dark profiles to all four standard profiles,
# because this wave's defect is not dark-specific: the sweep parked a band on the left of every
# resting surface in BOTH schemes, and the light bed has never been read per side at all (W22
# Purpose). The reader is W21's `g0/read.py` unchanged — the same body (declared box eroded 6 CSS
# px), the same rim band (the outer 3 CSS px) and the same per-side peak — so the before and after
# columns differ only by what vitrea drew.
#
# Sixteen reads: four profiles x {webgpu} x {before, after} plus the CSS tier on both schemes for
# the record, since the CSS tier has no sweep and its captures are expected not to move.
#
# `--sets calibration,validation`. The holdout is NOT read here (W22 X5 spends the wave's one
# holdout read at G1's dry run); the native side is the committed fixtures in both columns.
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
  for WHEN in before after; do
    [ "$WHEN" = before ] && CAP="$BEFORE" || CAP="$AFTER"
    OUT="$HERE/canonical-reads/$PROFILE-webgpu-$WHEN"
    "$PY" "$READER" --scenes "$SCENES" --fixtures "$FIXTURES" --profile "$PROFILE" \
      --captures "$CAP" --tier webgpu --sets calibration,validation \
      --json "$OUT.json" > "$OUT.txt"
    echo "read $PROFILE / webgpu / $WHEN -> canonical-reads/$(basename "$OUT").json"
  done
  # The CSS tier, from the canonical captures only: it draws no sweep, so there is no "after" to
  # take and the column exists to say what the other tier's rim looks like beside the GPU one.
  OUT="$HERE/canonical-reads/$PROFILE-css-before"
  "$PY" "$READER" --scenes "$SCENES" --fixtures "$FIXTURES" --profile "$PROFILE" \
    --captures "$BEFORE" --tier css --sets calibration,validation \
    --json "$OUT.json" > "$OUT.txt"
  echo "read $PROFILE / css / before -> canonical-reads/$(basename "$OUT").json"
done
