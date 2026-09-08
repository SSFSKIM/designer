#!/bin/bash
# W24 G2 — both canonical beds read BEFORE and AFTER, on both of the wave's instruments.
#
# TWO readers, because the wave binds one and holds the last wave's on the same rows:
#
#   * the ANGULAR read (`g0/read-angular.py`, X1) — clause 1, the rim around the whole contour
#     binned by the normal's angle, which is the only reader that can see a diagonal light;
#   * W23's CONTOUR read (`read-contour.py`, X1's "reported beside it") — the straight spans for
#     S11 and clause 4, and the eroded body every stop is read on.
#
# The BEFORE column is the canonical `web-captures/` in the MAIN checkout — the bed at the 0.12.0
# landing, which every clause of this wave is stated against — and the AFTER column is this gate's
# dry run in scratch. The native side is the committed fixtures in both columns, so a column's
# difference is this gate's constants and nothing else.
#
# `--sets` is a parameter and not a constant: the calibration and validation rows are read first,
# and the holdout is added only after the holdout column has been captured (X3).
#
# Usage: `bash read-canonical.sh <afterCaptures> <beforeCaptures> [sets]`
set -eu
PY=/Users/new/.claude/jobs/5c70e47f/tmp/venv/bin/python
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKTREE="$(cd "$HERE/../../../../.." && pwd)"
CONTOUR="$HERE/read-contour.py"
ANGULAR="$HERE/../g0/read-angular.py"
SCENES="$WORKTREE/apps/reference-apple/scenes.json"
FIXTURES="$WORKTREE/apps/reference-apple/fixtures"
AFTER="${1:?usage: read-canonical.sh <afterCaptures> <beforeCaptures> [sets]}"
BEFORE="${2:?}"
SETS="${3:-calibration,validation}"

mkdir -p "$HERE/canonical-reads"
for PROFILE in apple-macos-26.5-1x-light-standard apple-macos-26.5-2x-light-standard \
               apple-macos-26.5-1x-light-increased-contrast \
               apple-macos-26.5-1x-light-reduced-transparency \
               apple-macos-26.5-1x-dark-standard apple-macos-26.5-2x-dark-standard; do
  for TIER in webgpu css; do
    for WHEN in before after; do
      [ "$WHEN" = before ] && CAP="$BEFORE" || CAP="$AFTER"
      OUT="$HERE/canonical-reads/$PROFILE-$TIER-$WHEN"
      "$PY" "$CONTOUR" --scenes "$SCENES" --fixtures "$FIXTURES" --profile "$PROFILE" \
        --captures "$CAP" --tier "$TIER" --sets "$SETS" \
        --json "$OUT.json" > "$OUT.txt" 2>/dev/null
      "$PY" "$ANGULAR" --scenes "$SCENES" --fixtures "$FIXTURES" --profile "$PROFILE" \
        --captures "$CAP" --tier "$TIER" --sets "$SETS" \
        --json "$OUT-angular.json" --label "$PROFILE / $TIER / $WHEN" \
        > "$OUT-angular.txt" 2>/dev/null
      echo "read $PROFILE / $TIER / $WHEN"
    done
  done
done
