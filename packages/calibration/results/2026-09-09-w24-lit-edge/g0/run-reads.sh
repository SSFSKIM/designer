#!/bin/bash
# W24 G0 (b) — the angular read on both canonical beds and both probe grids.
#
# Every cell of all six canonical profiles, native against the LANDED 0.12.0 captures, on the GPU
# tier and on the CSS tier beside it as context; then W9's light probe grid and W21's dark probe
# grid, native, read by the same instrument with their own scene files and their own fixture beds.
# Nothing here writes anything canonical: the canonical captures and fixtures are READ from the main
# checkout (`web-captures/` is gitignored and lives there), and every output lands under this
# findings directory.
#
# The holdout is included in the canonical table on purpose and only here: W23 G3 spent the read of
# the holdout's landed captures, and clause (b) asks for the whole bed. Nothing in this gate is
# fitted or captured on a holdout row.
set -eu
PY=/Users/new/.claude/jobs/5c70e47f/tmp/venv/bin/python
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKTREE="$(cd "$HERE/../../../../.." && pwd)"
MAIN=/Users/new/Developer/GitHub/designer
SCENES="$WORKTREE/apps/reference-apple/scenes.json"
FIXTURES="$MAIN/apps/reference-apple/fixtures"
CAPTURES="$MAIN/packages/calibration/web-captures"
OUT="$HERE/angular-read.txt"
mkdir -p "$HERE/reads"

read_canonical() {
  local profile=$1 tier=$2
  "$PY" "$HERE/read-angular.py" --scenes "$SCENES" --fixtures "$FIXTURES" --profile "$profile" \
    --captures "$CAPTURES" --tier "$tier" --sets calibration,validation,holdout,recorded \
    --json "$HERE/reads/${profile}__${tier}.json" --label "$profile / $tier"
}

{
  echo "W24 G0 (b) — the rim around the whole contour, binned by the normal's angle."
  echo "read-angular.py, 16 bins of 22.5 deg centred on the compass; peak excess over the eroded"
  echo "body along the inward normal from 1 CSS px outside to 4 CSS px inside; linear Rec.709."
  echo "native = apps/reference-apple/fixtures; web = the landed 0.12.0 canonical captures."
  echo "ratio = brightest bin / dimmest bin; bright = the brightest bin's compass direction;"
  echo "floor = the dimmest bin as a fraction of the brightest (the ambient floor)."
  echo
  for PROFILE in apple-macos-26.5-1x-light-standard apple-macos-26.5-2x-light-standard \
                 apple-macos-26.5-1x-dark-standard apple-macos-26.5-2x-dark-standard \
                 apple-macos-26.5-1x-light-reduced-transparency \
                 apple-macos-26.5-1x-light-increased-contrast; do
    for TIER in webgpu css; do
      echo "##############################################################################"
      read_canonical "$PROFILE" "$TIER"
      echo
    done
  done

  echo "##############################################################################"
  echo "W9's light probe grid and W21's dark probe grid — the reference only (vitrea's side of"
  echo "these grids is captured by the ladder, ladder/probe*-base)."
  echo
  "$PY" "$HERE/read-angular.py" --scenes "$WORKTREE/apps/reference-apple/scenes-w9-probe.json" \
    --fixtures /Users/new/.claude/jobs/5c70e47f/tmp/w9-probe-fixtures \
    --profile apple-macos-26.5-1x-light-standard --sets calibration,validation \
    --json "$HERE/reads/probe9-native.json" --label "W9 light probe grid / native"
  echo
  "$PY" "$HERE/read-angular.py" --scenes "$WORKTREE/apps/reference-apple/scenes-w21-probe.json" \
    --fixtures "$WORKTREE/packages/calibration/results/2026-09-06-w21-dark-scheme/probe" \
    --profile apple-macos-26.5-1x-dark-standard --sets calibration,validation \
    --json "$HERE/reads/probe21-native.json" --label "W21 dark probe grid / native"
} > "$OUT" 2>&1
echo "-> $OUT"
