#!/bin/bash
# W26 G3 step 2 — the two control samples, to SCRATCH.
#
# The dark proof beside this one answers the question the wave's own edit raises. These two answer
# the question a landing always raises: is this checkout, on this machine, this session, still
# capturing the bytes the declaring child captured? A dark identity that held because the whole
# capture path had drifted would look exactly like a dark identity that held because the material
# did not move.
#
#   light GPU  the two light-standard profiles' gated bed, refereed against G2b's `g2b-digests.txt`
#              — the LIGHT scheme does take the heavy width, so these bytes must reproduce the
#              declaring child's and not the canonical bed's.
#   CSS        one light and one dark profile's gated bed, refereed against the canonical bed —
#              the CSS tier is byte-identical to 0.14.0 by G2b's ruling, so these must reproduce
#              the canonical bytes and not G2b's.
#
# The two expectations point in opposite directions on purpose: together they say the capture path
# is faithful in both, which one of them alone cannot.
set -u
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
"$HERE/g3-guard.sh" || exit 1
cd "$HERE/../../../../.."
unset VITREA_SCENES VITREA_FIXTURES VITREA_MATRIX_PATH
T=/Users/new/.claude/jobs/5c70e47f/tmp/w26/g3/sample
mkdir -p "$T"
export VITREA_WEB_CAPTURES="$T/web-captures"
rm -f "$T/DONE"; rm -rf "$T/web-captures"
LOG="$T/runs.log"; : > "$LOG"
cd packages/calibration
LIGHT=profiles/apple-macos-26.5-1x-light-standard.json
DARK=profiles/apple-macos-26.5-1x-dark-standard.json
run() {
  echo "=== $(date +%H:%M:%S) $1 / $3 / calibration,validation ==="
  npx tsx cli/compare.ts --profile "$1" --material-profile "$2" --renderer "$3" \
    --set calibration,validation --alpha --write-partial --out-matrix "$T/sample.json" >> "$LOG" 2>&1
  echo "    exit=$?"
}
run apple-macos-26.5-1x-light-standard "$LIGHT" webgpu
run apple-macos-26.5-2x-light-standard "$LIGHT" webgpu
run apple-macos-26.5-1x-light-standard "$LIGHT" css
run apple-macos-26.5-1x-dark-standard  "$DARK"  css
echo "SAMPLE DONE $(date +%H:%M:%S)"
touch "$T/DONE"
