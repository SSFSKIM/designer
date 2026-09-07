#!/bin/bash
# W21 G2c: the CSS tier re-captured into the CANONICAL bed (W21 Decision Log 4 (e)).
#
# Only the CSS tier runs. The GPU tier is untouched by construction — Decision Log 4 (a) and (b)
# move `optics.ts`'s conversion and `css-tier.ts`'s form, neither of which the renderer reads — so
# its captures stay on disk and the referee proves they did not move rather than re-rendering them.
# That also keeps every dom cell's cross-tier coherence measured against the GPU capture the bed
# already carries.
#
# The dark profile document is unchanged since G1, so a cell's key is unchanged and each run
# REPLACES its own rows in `results/matrix.json` rather than appending beside them; the referee
# asserts the bed still carries 229 cells on the same keys.
#
# Calibration and validation run before the holdout, so the holdout is the last thing the bed reads.
# This is the CSS tier's FIRST holdout read at this configuration and it is taken once.
#
# The GPU is shared: one capture process at a time, and this script serialises every run.
set -u
cd /Users/new/Developer/GitHub/designer
unset VITREA_SCENES VITREA_FIXTURES VITREA_WEB_CAPTURES VITREA_MATRIX_PATH
T=/Users/new/.claude/jobs/5c70e47f/tmp/w21/g2c
mkdir -p "$T"
LOG="$T/g2c-runs.log"
rm -f "$T/DONE"
echo "=== $(date +%H:%M:%S) build ==="
pnpm -r build > "$T/build.log" 2>&1 || { echo "BUILD FAILED"; exit 1; }
echo "=== $(date +%H:%M:%S) HEAD $(git rev-parse --short HEAD) $(git status --short | wc -l | tr -d ' ') dirty ==="
echo "=== dark document $(shasum -a 256 packages/calibration/profiles/apple-macos-26.5-1x-dark-standard.json | cut -c1-12) ==="
cd packages/calibration
# The bed as G2 landed it, kept for the referee: the light captures must come back byte-identical
# to these AND to the W20 bed's, and the GPU captures must not move at all.
cp results/matrix.json "$T/matrix-g2-landed.json"
rm -rf "$T/web-captures-g2-landed"; cp -R web-captures "$T/web-captures-g2-landed"
: > "$LOG"
LIGHT=profiles/apple-macos-26.5-1x-light-standard.json
DARK=profiles/apple-macos-26.5-1x-dark-standard.json
run() {
  local profile=$1 doc=$2 sets=$3
  echo "=== $(date +%H:%M:%S) $profile / css / $sets ==="
  npx tsx cli/compare.ts --profile "$profile" --material-profile "$doc" --renderer css \
    --set "$sets" --alpha --write-partial >> "$LOG" 2>&1
  echo "    exit=$?"
}
for SETS in calibration,validation holdout; do
  echo "=== $(date +%H:%M:%S) the $SETS column ==="
  run apple-macos-26.5-1x-light-standard "$LIGHT" "$SETS"
  run apple-macos-26.5-2x-light-standard "$LIGHT" "$SETS"
  run apple-macos-26.5-1x-light-increased-contrast "$LIGHT" "$SETS"
  run apple-macos-26.5-1x-light-reduced-transparency "$LIGHT" "$SETS"
  run apple-macos-26.5-1x-dark-standard "$DARK" "$SETS"
  run apple-macos-26.5-2x-dark-standard "$DARK" "$SETS"
done
echo "ALL RUNS DONE $(date +%H:%M:%S)"
touch "$T/DONE"
