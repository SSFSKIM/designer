#!/bin/bash
# W22 G0 (c) — W21's `rimAlpha` fit re-run on W21's own rows with the band gone.
#
# W21 G1 excluded the left side and fitted 0.082 over three sides of six cells (claims 5.90 2).
# This re-runs the identical fit script over the identical bed and the identical two rendered
# points, at the gate, so the only difference between the two reports is the sweep — and W22
# clause 3 is answered by comparing them: a constant whose rows re-choose it does not move.
#
# W21's `fit-rim.py` is used unmodified and still prints the left column as "no (sweep)"; with the
# band gone that column is now a fourth fitted-quality row, and the confirmation table's `clause 4`
# verdict on it is the reading that matters.
#
# Usage: `bash run-probe-fit.sh`
set -eu
PY=/Users/new/.claude/jobs/5c70e47f/tmp/venv/bin/python
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
W21="$HERE/../../2026-09-06-w21-dark-scheme"
WORKTREE="$(cd "$HERE/../../../../.." && pwd)"
SCENES="$WORKTREE/apps/reference-apple/scenes-w21-probe.json"
PROBE="$(cd "$W21/probe" && pwd)"
T=/Users/new/.claude/jobs/5c70e47f/tmp/w22/g0/probe

mkdir -p "$HERE/probe-reads"
for LABEL in probe-dark-rim002 probe-dark-rim018 probe-dark-rim0082; do
  "$PY" "$W21/g0/read.py" --scenes "$SCENES" --fixtures "$PROBE" \
    --profile apple-macos-26.5-1x-dark-standard --captures "$T/$LABEL/web-captures" \
    --tier webgpu --sets calibration,validation \
    --json "$HERE/probe-reads/$LABEL.json" > "$HERE/probe-reads/$LABEL.txt" 2>/dev/null
  echo "read $LABEL"
done

"$PY" "$W21/g1/fit-rim.py" \
  "0.02=$HERE/probe-reads/probe-dark-rim002.json" \
  "0.18=$HERE/probe-reads/probe-dark-rim018.json" \
  --confirm "0.082=$HERE/probe-reads/probe-dark-rim0082.json" \
  --out "$HERE/probe-fit-rim.txt" > /dev/null
echo "-> probe-fit-rim.txt"
