#!/bin/bash
# W22 G0 (e1) — the dark `impulse` capsule's two instruments, and the collapse prediction.
#
# Three columns per scale on the dark bed: the reference's fixtures, vitrea at the gate (the
# shipped dark document), and vitrea at the same document with `backdropToneMax` 0 — the design's
# prediction, so that what un-collapsing the dark material does to EVERY dark cell is measured.
# The light bed runs too, on the same cells, because the `impulse` capsule exists in both schemes
# and the eye's finding was stated on the dark one.
#
# Usage: `bash run-glow.sh`
set -eu
PY=/Users/new/.claude/jobs/5c70e47f/tmp/venv/bin/python
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKTREE="$(cd "$HERE/../../../../.." && pwd)"
SCENES="$WORKTREE/apps/reference-apple/scenes.json"
FIXTURES="$WORKTREE/apps/reference-apple/fixtures"
T=/Users/new/.claude/jobs/5c70e47f/tmp/w22/g0
CANONICAL=/Users/new/Developer/GitHub/designer/packages/calibration/results/matrix.json

mkdir -p "$HERE/glow-reads"
for SCALE in 1x 2x; do
  "$PY" "$HERE/read-glow.py" --scenes "$SCENES" --fixtures "$FIXTURES" \
    --profile "apple-macos-26.5-$SCALE-dark-standard" --matrix "$CANONICAL" \
    --web "gate=$T/after/web-captures" "toneMax0=$T/fit/dark-tonemax0-$SCALE/web-captures" \
    --out "$HERE/glow-reads/dark-$SCALE.txt"
  echo "glow read dark $SCALE"
done
for SCALE in 1x 2x; do
  "$PY" "$HERE/read-glow.py" --scenes "$SCENES" --fixtures "$FIXTURES" \
    --profile "apple-macos-26.5-$SCALE-light-standard" --matrix "$CANONICAL" \
    --web "gate=$T/after/web-captures" \
    --out "$HERE/glow-reads/light-$SCALE.txt"
  echo "glow read light $SCALE"
done
