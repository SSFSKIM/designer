#!/bin/bash
# W23 G0 (d) — the ladder's captures read by the same instrument as the bed.
#
# Usage: `bash read-ladder.sh <label> <profile>` for each point, or with no arguments to read
# every point that exists under the scratch ladder directory.
set -eu
PY=/Users/new/.claude/jobs/5c70e47f/tmp/venv/bin/python
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKTREE="$(cd "$HERE/../../../../.." && pwd)"
MAIN=/Users/new/Developer/GitHub/designer
T=/Users/new/.claude/jobs/5c70e47f/tmp/w23/g0/ladder
SCENES="$WORKTREE/apps/reference-apple/scenes.json"
FIXTURES="$MAIN/apps/reference-apple/fixtures"

mkdir -p "$HERE/ladder"
read_one() {
  local label=$1 profile=$2
  [ -d "$T/$label/web-captures" ] || { echo "skip $label (no captures)"; return 0; }
  "$PY" "$HERE/read-contour.py" --scenes "$SCENES" --fixtures "$FIXTURES" --profile "$profile" \
    --captures "$T/$label/web-captures" --tier webgpu --sets calibration,validation \
    --json "$HERE/ladder/$label.json" > "$HERE/ladder/$label.txt" 2>/dev/null
  echo "read $label"
}

for LABEL in light-levelgain light-envgain light-fit; do
  read_one "$LABEL-1x" apple-macos-26.5-1x-light-standard
  read_one "$LABEL-2x" apple-macos-26.5-2x-light-standard
done
for LABEL in dark-levelgain dark-fit; do
  read_one "$LABEL-1x" apple-macos-26.5-1x-dark-standard
  read_one "$LABEL-2x" apple-macos-26.5-2x-dark-standard
done

# The two probe grids, read against their own scene files and their own fixture beds.
PROBE=/Users/new/.claude/jobs/5c70e47f/tmp/w23/g0/probe
read_probe() {
  local label=$1 scenes=$2 fixtures=$3 profile=$4
  [ -d "$PROBE/$label/web-captures" ] || { echo "skip $label (no captures)"; return 0; }
  "$PY" "$HERE/read-contour.py" --scenes "$scenes" --fixtures "$fixtures" --profile "$profile" \
    --captures "$PROBE/$label/web-captures" --tier webgpu --sets calibration,validation \
    --json "$HERE/ladder/$label.json" > "$HERE/ladder/$label.txt" 2>/dev/null
  echo "read $label"
}
for LABEL in probe9-base probe9-levelgain probe9-fit; do
  read_probe "$LABEL" "$WORKTREE/apps/reference-apple/scenes-w9-probe.json" \
    /Users/new/.claude/jobs/5c70e47f/tmp/w9-probe-fixtures apple-macos-26.5-1x-light-standard
done
for LABEL in probe21-base probe21-levelgain probe21-fit; do
  read_probe "$LABEL" "$WORKTREE/apps/reference-apple/scenes-w21-probe.json" \
    "$WORKTREE/packages/calibration/results/2026-09-06-w21-dark-scheme/probe" \
    apple-macos-26.5-1x-dark-standard
done
