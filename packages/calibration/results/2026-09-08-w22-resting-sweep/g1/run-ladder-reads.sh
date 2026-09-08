#!/bin/bash
# W22 G1 (1) — the ladder's rendered points read under the declared geometry, and the fit run on them.
#
# The reader is W21's `g0/read.py`, unchanged, which is the wave's instrument (W22 X2): the same body
# (declared box eroded 6 CSS px), the same rim band (the outer 3 CSS px) and the same per-side peak
# every gate in this wave reads. The native column is the committed fixtures and is identical in
# every ladder point, so a column's difference is the candidate document's `specularGain` and
# nothing else.
#
# Usage: `bash run-ladder-reads.sh`
set -eu
PY=/Users/new/.claude/jobs/5c70e47f/tmp/venv/bin/python
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKTREE="$(cd "$HERE/../../../../.." && pwd)"
READER="$WORKTREE/packages/calibration/results/2026-09-06-w21-dark-scheme/g0/read.py"
SCENES="$WORKTREE/apps/reference-apple/scenes.json"
FIXTURES="$WORKTREE/apps/reference-apple/fixtures"
T=/Users/new/.claude/jobs/5c70e47f/tmp/w22/g1

mkdir -p "$HERE/ladder-reads"
for GAIN in spec000 spec0025 spec005 spec010 spec015 spec025 spec040 spec055; do
  for SCALE in 1x 2x; do
    "$PY" "$READER" --scenes "$SCENES" --fixtures "$FIXTURES" \
      --profile "apple-macos-26.5-$SCALE-light-standard" \
      --captures "$T/ladder/$GAIN-$SCALE/web-captures" --tier webgpu --sets calibration \
      --json "$HERE/ladder-reads/light-$SCALE-$GAIN.json" \
      > "$HERE/ladder-reads/light-$SCALE-$GAIN.txt" 2>/dev/null
    echo "read $GAIN $SCALE"
  done
done

"$PY" "$HERE/fit-specular.py" "$HERE/ladder-reads" --out "$HERE/fit-specular.txt" > /dev/null
echo "fit -> fit-specular.txt"
