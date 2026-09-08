#!/bin/bash
# W24 G0 (c) — the ladder's captures read by the same two instruments the gates read.
#
# `read-angular.py` for the shape the wave is fitting, and W23's own `read-contour.py` for the
# straight-span band the wave promised not to move (clause 4, S11): the second is copied from
# `results/2026-09-08-w23-collapsed-rim/g0/` unchanged, because a check that W23's numbers hold has
# to be W23's reader and not a re-implementation of it.
set -eu
PY=/Users/new/.claude/jobs/5c70e47f/tmp/venv/bin/python
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKTREE="$(cd "$HERE/../../../../.." && pwd)"
MAIN=/Users/new/Developer/GitHub/designer
W23="$WORKTREE/packages/calibration/results/2026-09-08-w23-collapsed-rim/g0"
T=/Users/new/.claude/jobs/5c70e47f/tmp/w24/g0/ladder
SCENES="$WORKTREE/apps/reference-apple/scenes.json"
FIXTURES="$MAIN/apps/reference-apple/fixtures"
mkdir -p "$HERE/ladder"

angular() {
  local label=$1 profile=$2 scenes=$3 fixtures=$4
  [ -d "$T/$label/web-captures" ] || { echo "skip $label (no captures)"; return 0; }
  "$PY" "$HERE/read-angular.py" --scenes "$scenes" --fixtures "$fixtures" --profile "$profile" \
    --captures "$T/$label/web-captures" --tier webgpu --sets calibration,validation \
    --json "$HERE/ladder/$label.json" --label "$label / $profile" > "$HERE/ladder/$label.txt"
  echo "read $label"
}

contour() {
  local label=$1 profile=$2
  [ -d "$T/$label/web-captures" ] || return 0
  "$PY" "$W23/read-contour.py" --scenes "$SCENES" --fixtures "$FIXTURES" --profile "$profile" \
    --captures "$T/$label/web-captures" --tier webgpu --sets calibration,validation \
    --json "$HERE/ladder/$label-contour.json" --label "$label / $profile" \
    > "$HERE/ladder/$label-contour.txt"
  echo "contour $label"
}

# The LANDED bed read by the same contour reader, so section 3 of `fit-vitrea.py` compares like
# with like: W23's straight-span numbers as the 0.12.0 captures actually hold them.
for BED in light dark; do
  for SCALE in 1x 2x; do
    PROFILE="apple-macos-26.5-$SCALE-$BED-standard"
    "$PY" "$W23/read-contour.py" --scenes "$SCENES" --fixtures "$FIXTURES" --profile "$PROFILE" \
      --captures "$MAIN/packages/calibration/web-captures" --tier webgpu \
      --sets calibration,validation --json "$HERE/reads/contour-$PROFILE.json" \
      --label "landed 0.12.0 / $PROFILE" > "$HERE/reads/contour-$PROFILE.txt"
    echo "contour landed $PROFILE"
  done
done

for POINT in lit1 lit2; do
  for BED in light dark; do
    for SCALE in 1x 2x; do
      LABEL="$BED-$POINT-$SCALE"
      PROFILE="apple-macos-26.5-$SCALE-$BED-standard"
      angular "$LABEL" "$PROFILE" "$SCENES" "$FIXTURES"
      contour "$LABEL" "$PROFILE"
    done
  done
done

angular probe9-base apple-macos-26.5-1x-light-standard \
  "$WORKTREE/apps/reference-apple/scenes-w9-probe.json" \
  /Users/new/.claude/jobs/5c70e47f/tmp/w9-probe-fixtures
angular probe21-base apple-macos-26.5-1x-dark-standard \
  "$WORKTREE/apps/reference-apple/scenes-w21-probe.json" \
  "$WORKTREE/packages/calibration/results/2026-09-06-w21-dark-scheme/probe"
