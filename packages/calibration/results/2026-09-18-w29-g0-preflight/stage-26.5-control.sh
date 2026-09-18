#!/bin/bash
# A read-only scratch root over four committed 26.5 cells, for G0 (e)'s control.
#
#   stage-26.5-control.sh <scratch-root>
#
# `window-geometry.ts` walks a fixture root's profile directories, and the whole
# committed bundle is 619 cells. This stages symlinks to the four scenes the edge
# reading uses, in the two 2x profiles, so the control runs over the same cells as
# the 27 arm and nothing under `fixtures/` is written, moved or copied.
set -euo pipefail

OUT="${1:?usage: stage-26.5-control.sh <scratch-root>}"
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO="$(cd "$HERE/../../../.." && pwd)"
FIX="$REPO/apps/reference-apple/fixtures"

case "$OUT" in "$REPO"/*) echo "REFUSED: $OUT is inside the repository." >&2; exit 1;; esac

rm -rf "$OUT"
mkdir -p "$OUT"
ln -s "$FIX/backgrounds" "$OUT/backgrounds"
for P in apple-macos-26.5-2x-light-standard apple-macos-26.5-2x-dark-standard; do
  mkdir -p "$OUT/$P"
  for S in photo__rrect-lg__rest checkerboard__rrect-lg__rest dark-solid__rrect-80__rest \
           photo__toolbar-group__rest; do
    [ -f "$FIX/$P/$S.png" ] && ln -s "$FIX/$P/$S.png" "$OUT/$P/$S.png"
  done
done
find "$OUT" -name '*.png' -type l | sed "s|$OUT/||" | sort
