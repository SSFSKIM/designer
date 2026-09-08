#!/bin/bash
# W24 G0 (a) — the angular instrument's validations, all three of them.
#
# (1) INJECTION. A synthetic rim of known angular profile painted one CSS px inside the declared
#     contour and read back, on four cells that between them cover both shapes, both scales and
#     both schemes. Three forms per cell: flat/unquantised (the reader's own arithmetic, bounded),
#     flat/8-bit (the bed's resolution at that body level, in codes), and over the untouched
#     capture (composition on real pixels).
# (2) THE PARENT'S READER. The same cells read through the parent finding's window
#     (`finding/angular-read.py`: 1..4 DEVICE px at a 0.5 device px step, 720 points) so that the
#     two readers can be put beside each other on the numbers the wave was chartered on.
# (3) THE GEOMETRY DIAGNOSTIC. Per bin, how many boundary samples it holds, how far inside the
#     declared contour their peaks sat, what fraction ran to the end of the search window
#     (TRUNCATED) and what fraction sat OUTSIDE the contour — the two ways this reader can be
#     reading something that is not the rim.
set -eu
PY=/Users/new/.claude/jobs/5c70e47f/tmp/venv/bin/python
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKTREE="$(cd "$HERE/../../../../.." && pwd)"
MAIN=/Users/new/Developer/GitHub/designer
SCENES="$WORKTREE/apps/reference-apple/scenes.json"
FIXTURES="$MAIN/apps/reference-apple/fixtures"
CAPTURES="$MAIN/packages/calibration/web-captures"
T=/Users/new/.claude/jobs/5c70e47f/tmp/w24/g0
OUT="$HERE/instrument.txt"
mkdir -p "$T/inject"

inject_one() {
  local profile=$1 scene=$2 amp=$3
  "$PY" "$HERE/read-angular.py" --scenes "$SCENES" --profile "$profile" --scene "$scene" \
    --inject "$FIXTURES/$profile/$scene.png" --amplitude "$amp" --axis 315 --ambient 0.2 \
    --exponent 1.0 --inject-out "$T/inject/$profile-$scene"
}

{
  echo "W24 G0 (a) — read-angular.py validated."
  echo
  echo "=============================================================================="
  echo "(1) INJECTION — a synthetic rim of A x (0.2 + 0.8 |cos(theta - 315deg)|), one CSS px deep"
  echo "=============================================================================="
  echo "The expectation is binned over the SAME boundary samples the read uses, not evaluated at"
  echo "the bin's centre: |cos| has a kink at its zero, so over the 22.5 deg of the dimmest bin its"
  echo "mean stands 40 % above its centre value and a perfect reader would look five codes wrong."
  echo "The bound on the flat/unquantised form is 0.0005 of linear luminance."
  echo
  inject_one apple-macos-26.5-2x-dark-standard dark-solid__rrect-md__rest 0.05
  echo
  inject_one apple-macos-26.5-1x-dark-standard dark-solid__capsule-button__rest 0.02
  echo
  inject_one apple-macos-26.5-2x-light-standard dark-solid__rrect-md__rest 0.20
  echo
  inject_one apple-macos-26.5-1x-light-standard mid-dark-solid__capsule-button__rest 0.10
  echo
  echo "=============================================================================="
  echo "(2) THE PARENT'S READER — the finding's window, on the cells it read"
  echo "=============================================================================="
  echo "finding/angular-read.py bins by ARCLENGTH clockwise from the top-left of the top edge and"
  echo "searches 1..4 DEVICE px at 0.5 device px; this reader bins by the normal's ANGLE and"
  echo "searches 1..4 CSS px at 0.25 CSS px. Where they can be compared directly is the SEGMENT"
  echo "mean, which neither binning touches, and the two agree there to 0.0001 on every segment of"
  echo "every cell the parent read (the diagnostic below prints them). Run here with the parent's"
  echo "own window, so that the difference between the two tables is the binning alone."
  echo
  for P in apple-macos-26.5-2x-dark-standard apple-macos-26.5-2x-light-standard \
           apple-macos-26.5-1x-dark-standard; do
    "$PY" "$HERE/read-angular.py" --scenes "$SCENES" --fixtures "$FIXTURES" --profile "$P" \
      --captures "$CAPTURES" --tier webgpu --sets calibration,validation,holdout \
      --parent-compat --label "$P / webgpu / the parent's window"
    echo
  done
  echo "=============================================================================="
  echo "(3) THE GEOMETRY DIAGNOSTIC — samples, peak depth, truncation, outside"
  echo "=============================================================================="
  echo "A bin whose peak ran to the far end of the window (TRUNCATED) has not been bounded by the"
  echo "reader; a bin whose peak sat outside the declared contour (OUTSIDE) is reading the"
  echo "backdrop. Both are printed per bin and both feed fit-law.py's mask."
  echo
  "$PY" "$HERE/diagnose.py" "$HERE/reads"
} > "$OUT" 2>&1
echo "-> $OUT"
