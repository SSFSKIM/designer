#!/bin/bash
# W22 G0 — the fit's rendered points read under the declared geometry, and the fit run over them.
#
# Three columns per scale on the light bed: the SHIPPED constants at the gate (the "after" captures
# of `g0-capture.sh`), `specularGain` 0 at the shipped `rimAlpha` 0.18, and `specularGain` 0 at
# `rimAlpha` 0.04. The first pair isolates the specular; the second pair fixes the line the rim
# excess follows in `rimAlpha`.
#
# The dark `backdropToneMax` 0 prediction is read by the same reader, against the same fixtures, so
# every dark cell's body and rim under the un-collapsed material is beside the shipped one.
#
# Usage: `bash run-fit-reads.sh`
set -eu
PY=/Users/new/.claude/jobs/5c70e47f/tmp/venv/bin/python
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKTREE="$(cd "$HERE/../../../../.." && pwd)"
READER="$WORKTREE/packages/calibration/results/2026-09-06-w21-dark-scheme/g0/read.py"
SCENES="$WORKTREE/apps/reference-apple/scenes.json"
FIXTURES="$WORKTREE/apps/reference-apple/fixtures"
T=/Users/new/.claude/jobs/5c70e47f/tmp/w22/g0

mkdir -p "$HERE/fit-reads"
read_one() {
  local label=$1 profile=$2 captures=$3
  "$PY" "$READER" --scenes "$SCENES" --fixtures "$FIXTURES" --profile "$profile" \
    --captures "$captures" --tier webgpu --sets calibration,validation \
    --json "$HERE/fit-reads/$label.json" > "$HERE/fit-reads/$label.txt" 2>/dev/null
  echo "read $label"
}
for SCALE in 1x 2x; do
  read_one "light-$SCALE-spec0-rim018" "apple-macos-26.5-$SCALE-light-standard" \
    "$T/fit/light-spec0-rim018-$SCALE/web-captures"
  read_one "light-$SCALE-spec0-rim004" "apple-macos-26.5-$SCALE-light-standard" \
    "$T/fit/light-spec0-rim004-$SCALE/web-captures"
  read_one "dark-$SCALE-tonemax0" "apple-macos-26.5-$SCALE-dark-standard" \
    "$T/fit/dark-tonemax0-$SCALE/web-captures"
done

for SCALE in 1x 2x; do
  "$PY" "$HERE/fit-rim.py" \
    --native "$HERE/canonical-reads/apple-macos-26.5-$SCALE-light-standard-webgpu-after.json" \
    "0.04=$HERE/fit-reads/light-$SCALE-spec0-rim004.json" \
    "0.18=$HERE/fit-reads/light-$SCALE-spec0-rim018.json" \
    --baseline "shipped=$HERE/canonical-reads/apple-macos-26.5-$SCALE-light-standard-webgpu-after.json" \
    --scenes "$SCENES" --out "$HERE/fit-rim-$SCALE.txt" > /dev/null
  echo "fit $SCALE -> fit-rim-$SCALE.txt"
done
