#!/bin/bash
# W26 G2 — both canonical beds read BEFORE and AFTER, on the two instruments S11 is stated on.
#
# W25 G3's `read-canonical.sh` with this wave's paths and one substantive change, which is the
# BEFORE column. W25 read its before column out of the canonical `web-captures/` in the shared
# checkout. This child cannot: the canonical captures there are the 0.14.0 bed, which is the right
# material, but they were taken by a different run on a different day and this wave's deltas are
# one to three display codes. W26 G1c captured the 0.14.0 control on THIS machine in THIS session
# (`c0b`, both tiers, 170 cells) and proved it byte-identical to the canonical captures on all fifty
# rows it overlaps, so `c0b` is the before column and the comparison is between two runs of the same
# harness on the same adapter.
#
# The readers are unchanged and are the earlier waves' own:
#   * W23's CONTOUR read (`../../2026-09-09-w25-thick-span-composite/g3/read-contour.py`) — the
#     straight spans for S11's first half and the eroded body every body stop is read on.
#   * W24's ANGULAR read (`../../2026-09-09-w24-lit-edge/g0/read-angular.py`) — the rim binned by
#     the normal's direction, S11's second half.
#
# Neither is a reader of the body's WIDTH, which is what this wave moved, and that is the point:
# they are the check that a body change stayed in the body. The width's own reader is the family
# reader (`g2-read.py`).
#
# `--sets` is a parameter and not a constant: calibration and validation are read first, and the
# holdout is added only after the holdout column has been captured (X3).
#
# Usage: `bash g2-read-canonical.sh <afterCaptures> <beforeCaptures> [sets]`
set -eu
PY=/Users/new/.claude/jobs/5c70e47f/tmp/venv/bin/python
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKTREE="$(cd "$HERE/../../../../.." && pwd)"
W25="$HERE/../../2026-09-09-w25-thick-span-composite/g3"
CONTOUR="$W25/read-contour.py"
ANGULAR="$HERE/../../2026-09-09-w24-lit-edge/g0/read-angular.py"
SCENES="$WORKTREE/apps/reference-apple/scenes.json"
FIXTURES="$WORKTREE/apps/reference-apple/fixtures"
AFTER="${1:?usage: g2-read-canonical.sh <afterCaptures> <beforeCaptures> [sets]}"
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
