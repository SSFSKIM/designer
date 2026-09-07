#!/bin/bash
# W21 G2: the canonical rebuild at the landing (W21 Decision Log 3 (d); claims §5.90). `main` at
# the code and the profile document that G1 froze — the dark document re-recorded on G0's measured
# anchors (`resolvedMaterialSha256` d86f480c0e136627, file sha256 ebfb0858…), the light document
# untouched. The dark profile's hash moves, so a cell's key moves with it and the old rows would
# otherwise sit beside the new ones: `results/matrix.json` is removed first and the WHOLE bed is
# rebuilt, both tiers, all six profiles, into the CANONICAL matrix and the CANONICAL
# `web-captures/` (no --out-matrix, no VITREA_WEB_CAPTURES).
#
# The previous canonical matrix and captures are copied to scratch first: they are the W20 bed,
# which is the referee's "before" for the light profiles' byte check (X3) and for the dark rows'
# movement.
#
# `--alpha` takes the declaration-conformance capture on every cell (W20 Decision Log 2 ruling 2;
# the canonical matrix has carried those rows since W20's landing and `adopted-thresholds.test.ts`
# fails a rebuild without them). Calibration and validation run before the holdout, in G1's order,
# so the holdout is the last thing the bed reads — it was read once at the dry run (X6) and this
# rebuild has to reproduce those bytes, not take a second reading of them.
#
# The GPU tier runs before the CSS tier so every dom cell's coherence axis is measured against a
# GPU capture already on disk. The GPU is shared: one capture process at a time, and this script
# serialises every run. Derived from W20's g2-rebuild.sh.
set -u
cd /Users/new/Developer/GitHub/designer
unset VITREA_SCENES VITREA_FIXTURES VITREA_WEB_CAPTURES VITREA_MATRIX_PATH
T=/Users/new/.claude/jobs/5c70e47f/tmp/w21/g2
mkdir -p "$T"
LOG="$T/g2-runs.log"
rm -f "$T/DONE"
echo "=== $(date +%H:%M:%S) build ==="
pnpm -r build > "$T/build.log" 2>&1 || { echo "BUILD FAILED"; exit 1; }
echo "=== $(date +%H:%M:%S) HEAD $(git rev-parse --short HEAD) $(git status --short | wc -l | tr -d ' ') dirty ==="
echo "=== dark document $(shasum -a 256 packages/calibration/profiles/apple-macos-26.5-1x-dark-standard.json | cut -c1-12) ==="
cd packages/calibration
cp results/matrix.json "$T/matrix-before-w21.json"
rm -rf "$T/web-captures-before-w21"; cp -R web-captures "$T/web-captures-before-w21"
rm -rf web-captures; mkdir -p web-captures
rm -f results/matrix.json
: > "$LOG"
LIGHT=profiles/apple-macos-26.5-1x-light-standard.json
DARK=profiles/apple-macos-26.5-1x-dark-standard.json
run() {
  local profile=$1 doc=$2 renderer=$3 sets=$4
  echo "=== $(date +%H:%M:%S) $profile / $renderer / $sets ==="
  npx tsx cli/compare.ts --profile "$profile" --material-profile "$doc" --renderer "$renderer" \
    --set "$sets" --alpha --write-partial >> "$LOG" 2>&1
  echo "    exit=$?"
}
for SETS in calibration,validation holdout; do
  echo "=== $(date +%H:%M:%S) the $SETS column ==="
  for renderer in webgpu css; do
    run apple-macos-26.5-1x-light-standard "$LIGHT" "$renderer" "$SETS"
    run apple-macos-26.5-2x-light-standard "$LIGHT" "$renderer" "$SETS"
    run apple-macos-26.5-1x-light-increased-contrast "$LIGHT" "$renderer" "$SETS"
    run apple-macos-26.5-1x-light-reduced-transparency "$LIGHT" "$renderer" "$SETS"
    run apple-macos-26.5-1x-dark-standard "$DARK" "$renderer" "$SETS"
    run apple-macos-26.5-2x-dark-standard "$DARK" "$renderer" "$SETS"
  done
done
echo "ALL RUNS DONE $(date +%H:%M:%S)"
touch "$T/DONE"
