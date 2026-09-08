#!/bin/bash
# W22 G2: the canonical rebuild at the landing (W22 Decision Log 4 (e); claims §5.96). `main` at the
# code and the profile documents G1 froze — the LIGHT document re-recorded on G1's fit
# (`optics.regular.specularGain` 0.55 -> 0, `resolvedMaterialSha256` f6c54a1ea236447a, file sha256
# 9360d73b…), the dark document untouched (d86f480c0e136627, ebfb0858…). The light document's hash
# moves, so every light cell's key moves with it and the old rows would otherwise sit beside the new
# ones: `results/matrix.json` is removed first and the WHOLE bed is rebuilt, both tiers, all six
# profiles, into the CANONICAL matrix and the CANONICAL `web-captures/` (no --out-matrix, no
# VITREA_WEB_CAPTURES).
#
# The previous canonical captures and matrix are copied to scratch first: they are the W21 bed, the
# referee's "before" and the landing sheet's "GPU before" column.
#
# `--alpha` takes the declaration-conformance capture on every cell (W20 Decision Log 2 ruling 2;
# `adopted-thresholds.test.ts` fails a rebuild without them) and `--write-partial` records a cell
# whose axis is absent. Calibration and validation run before the holdout, in G1's order, so the
# holdout is the last thing the bed reads — it was read once at the dry run (X5) and this rebuild
# reproduces those bytes rather than taking a second reading of them.
#
# The GPU tier runs before the CSS tier within each column so every dom cell's coherence axis is
# measured against a GPU capture already on disk. The GPU is shared: one capture process at a time,
# and this script serialises every run. Derived from W21's g2-rebuild.sh and G1's g1-dryrun-run.sh.
#
# `1x-light-increased-contrast / css / holdout` is expected to exit 1 on
# `hc-text__capsule-button__rest` ("contourCurvature: a 0.00px contour sampled 512 times at σ=3
# carries no curvature") — pre-existing, reproduced at G1 §3 and on the canonical bed before it.
set -u
cd /Users/new/Developer/GitHub/designer
unset VITREA_SCENES VITREA_FIXTURES VITREA_WEB_CAPTURES VITREA_MATRIX_PATH
T=/Users/new/.claude/jobs/5c70e47f/tmp/w22/g2
mkdir -p "$T"
LOG="$T/g2-runs.log"
rm -f "$T/DONE"
echo "=== $(date +%H:%M:%S) build ==="
pnpm -r build > "$T/build.log" 2>&1 || { echo "BUILD FAILED"; exit 1; }
echo "=== $(date +%H:%M:%S) HEAD $(git rev-parse --short HEAD) $(git status --short | wc -l | tr -d ' ') dirty ==="
echo "=== light document $(shasum -a 256 packages/calibration/profiles/apple-macos-26.5-1x-light-standard.json | cut -c1-12) ==="
echo "=== dark  document $(shasum -a 256 packages/calibration/profiles/apple-macos-26.5-1x-dark-standard.json | cut -c1-12) ==="
cd packages/calibration
cp results/matrix.json "$T/matrix-before-w22.json"
rm -rf "$T/../g2-before"; cp -R web-captures "$T/../g2-before"
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
