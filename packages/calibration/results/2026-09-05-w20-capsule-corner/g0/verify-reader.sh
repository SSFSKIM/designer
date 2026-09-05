#!/bin/bash
# W20 G0 — verify the contour reader against a shape whose answer is already known, before the
# probe's own captures exist.
#
# The canonical bed's `capsule-button` is the same 120 x 44 `Capsule()` this probe carries as its
# control, and it is a circular stadium by definition. Staging it under the probe's own scene ids —
# by SYMLINK, into scratch, so the canonical fixtures are only ever read — lets the reader be scored
# on a known curve while the probe's runs are still being taken. What it reports here is the reader's
# own error, and it is what every rung's number is quoted against.
#
# Usage: `bash verify-reader.sh <scratchDir>`
set -eu
SCRATCH="${1:?usage: verify-reader.sh <scratchDir>}"
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKTREE="$(cd "$HERE/../../../../.." && pwd)"
FIX="$WORKTREE/apps/reference-apple/fixtures"
PROFILE=apple-macos-26.5-1x-light-standard
PY=/Users/new/.claude/jobs/5c70e47f/tmp/venv/bin/python

rm -rf "$SCRATCH"
mkdir -p "$SCRATCH/$PROFILE" "$SCRATCH/backgrounds"
ln -sf "$FIX/backgrounds/checkerboard@1x.png" "$SCRATCH/backgrounds/checkerboard@1x.png"
for BG in light-solid checkerboard; do
  ln -sf "$FIX/$PROFILE/${BG}__capsule-button__rest.png" \
         "$SCRATCH/$PROFILE/${BG}__capsule-120x44__rest.png"
done

"$PY" "$HERE/read-contours.py" --probe "$SCRATCH" --candidates "$SCRATCH/../candidates.json" \
  --out "$SCRATCH/read"
