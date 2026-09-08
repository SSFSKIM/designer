#!/bin/bash
# W23 G3 — both canonical beds read BEFORE and AFTER, on both of the wave's instruments.
#
# TWO readers, because the wave binds one and re-checks a clause of the last wave on the other:
#
#   * the CONTOUR read (`read-contour.py`, G0's, X1) — clauses 1, 2 and 3 and the stops;
#   * W21's DECLARED-GEOMETRY band read (`w21/g0/read.py`) — clause 4, which re-checks W22's own
#     clause 2 on its own instrument so both verdicts stand on the record (W23 Decision Log 1 (b)).
#
# The BEFORE column is the canonical `web-captures/` in the MAIN checkout — the bed at the 0.11.0
# landing, matrix `3587400`, which every clause of this wave is stated against — and the AFTER
# column is this gate's dry run in scratch. The native side is the committed fixtures in both
# columns, so a column's difference is this gate's constants and nothing else.
#
# `--sets calibration,validation,holdout`: this gate opens the holdout (X3), so the holdout cells
# are read here at the frozen configuration for the wave's one time.
#
# Usage: `bash read-canonical.sh <afterCaptures> <beforeCaptures>`
set -eu
PY=/Users/new/.claude/jobs/5c70e47f/tmp/venv/bin/python
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKTREE="$(cd "$HERE/../../../../.." && pwd)"
CONTOUR="$HERE/read-contour.py"  # this gate's reader, with the hue columns
BAND="$WORKTREE/packages/calibration/results/2026-09-06-w21-dark-scheme/g0/read.py"
SCENES="$WORKTREE/apps/reference-apple/scenes.json"
FIXTURES="$WORKTREE/apps/reference-apple/fixtures"
AFTER="${1:?usage: read-canonical.sh <afterCaptures> <beforeCaptures>}"
BEFORE="${2:?}"

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
        --captures "$CAP" --tier "$TIER" --sets calibration,validation,holdout \
        --json "$OUT.json" > "$OUT.txt" 2>/dev/null
      "$PY" "$BAND" --scenes "$SCENES" --fixtures "$FIXTURES" --profile "$PROFILE" \
        --captures "$CAP" --tier "$TIER" --sets calibration,validation,holdout \
        --json "$OUT-band.json" > "$OUT-band.txt" 2>/dev/null
      echo "read $PROFILE / $TIER / $WHEN"
    done
  done
done
