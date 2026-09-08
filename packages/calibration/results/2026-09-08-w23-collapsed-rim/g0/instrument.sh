#!/bin/bash
# W23 G0 (a) — the instrument's validation, in one file: injection, the corner sweep, the
# cross-check against the parent's `contour-profile.py`.
#
# Three things have to be true before any number this gate quotes means anything.
#
#   (i)  The reader returns an amplitude it is GIVEN. A synthetic line of known linear amplitude,
#        one CSS px deep, is painted along every straight span of a real capture and read back —
#        unquantised, where the answer must be exact, and re-quantised to the bed's 8 bits, where
#        what comes back is the bed's own resolution and is quoted in codes.
#   (ii) The straight span is actually straight. Apple's corner is continuous, not circular, so the
#        first contour row is still climbing well past the nominal radius; the read is swept over
#        the corner factor until it converges, and the factor is chosen from that sweep.
#   (iii) It agrees with the reader the parent's grounding read used (`finding/contour-profile.py`
#        and `contour-table.txt`, claims §5.99) on the cells that reader read.
#
# Usage: `bash instrument.sh > instrument.txt`
set -u
PY=/Users/new/.claude/jobs/5c70e47f/tmp/venv/bin/python
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKTREE="$(cd "$HERE/../../../../.." && pwd)"
MAIN=/Users/new/Developer/GitHub/designer
R="$HERE/read-contour.py"
SCENES="$WORKTREE/apps/reference-apple/scenes.json"
CAP="$MAIN/packages/calibration/web-captures"
T=/Users/new/.claude/jobs/5c70e47f/tmp/w23/g0

echo "W23 G0 (a) — the contour reader validated: injection, the corner sweep, the cross-check"
echo
echo "reader: results/2026-09-08-w23-collapsed-rim/g0/read-contour.py"
echo "body: the declared box eroded 6 CSS px (W21's). depth: 2 CSS px. corner factor: 1.6."
echo "units: linear Rec.709 luminance per CSS px."
echo
echo "=============================================================================="
echo "(i) INJECTION — a synthetic line of known amplitude, one CSS px deep, on the"
echo "    straight span of a real capture"
echo "=============================================================================="
inject() {
  "$PY" "$R" --scenes "$SCENES" --scene "$2" --amplitude "$3" \
    --inject "$CAP/$1/$2/$2__webgpu.png" --inject-out "$T/inj-$1-$2"
  echo
}
inject apple-macos-26.5-1x-light-standard dark-solid__rrect-md__rest 0.05
inject apple-macos-26.5-1x-light-standard dark-solid__rrect-md__rest 0.005
inject apple-macos-26.5-1x-light-standard light-solid__rrect-md__rest 0.005
inject apple-macos-26.5-1x-light-standard checkerboard__rrect-sm__rest 0.03
inject apple-macos-26.5-2x-light-standard dark-solid__rrect-md__rest 0.05
inject apple-macos-26.5-2x-dark-standard dark-solid__capsule-button__rest 0.02
inject apple-macos-26.5-2x-dark-standard dark-solid__rrect-md__rest 0.005

echo "=============================================================================="
echo "(ii) THE CORNER SWEEP — where the straight span becomes straight"
echo "=============================================================================="
"$PY" "$HERE/corner-sweep.py"
echo
echo "=============================================================================="
echo "(iii) CROSS-CHECK against the parent's contour-profile.py / contour-table.txt"
echo "=============================================================================="
"$PY" "$HERE/crosscheck.py"
