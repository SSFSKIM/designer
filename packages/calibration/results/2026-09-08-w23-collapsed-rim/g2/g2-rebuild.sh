#!/bin/bash
# W23 G2: the canonical rebuild at the landing (W23 Decision Log 4 (f); claims §5.104). `main` at the
# code and the two profile documents G3 froze — the LIGHT document re-recorded on G1's law and G3's
# composition (`rimAlpha` 0.844, `rimLevelGain` -0.628, `rimWidth2x` 1.35, `rimCollapsed` 0.038,
# `rimCollapsedTinted` 0.520, `rimTintChroma` 1; resolved fingerprint c426a37744c38cce, file sha256
# a94be1ff…) and the DARK document re-recorded on the dark amplitude law (`rimAlpha` 0.0265,
# `rimLevelGain` +2.334; resolved bf5752ac1b152238, file sha256 f4cf35d3…).
#
# BOTH documents' hashes move, so every cell's key moves with it and the old rows would otherwise sit
# beside the new ones: `results/matrix.json` is removed first and the WHOLE bed is rebuilt, both
# tiers, all six profiles, into the CANONICAL matrix and the CANONICAL `web-captures/` (no
# --out-matrix, no VITREA_WEB_CAPTURES).
#
# The previous canonical captures and matrix are copied to scratch first: they are the 0.11.0 bed,
# the referee's "before" and the landing sheet's "GPU before" column.
#
# `--alpha` takes the declaration-conformance capture on every cell (W20 Decision Log 2 ruling 2;
# `adopted-thresholds.test.ts` fails a rebuild without them) and `--write-partial` records a cell
# whose axis is absent. Calibration and validation run before the holdout, in G3's order, so the
# holdout is the last thing the bed reads — it was read once at G3's dry run (X3) and this rebuild
# reproduces those bytes rather than taking a second reading of them.
#
# The GPU tier runs before the CSS tier within each column so every dom cell's coherence axis is
# measured against a GPU capture already on disk. The GPU is shared: one capture process at a time,
# and this script serialises every run. Derived from W22 G2's g2-rebuild.sh and G3's
# g3-dryrun-run.sh, whose flags it must reproduce byte for byte.
#
# `1x-light-increased-contrast / css / holdout` is expected to exit 1 on
# `hc-text__capsule-button__rest` ("contourCurvature: a 0.00px contour sampled 512 times at sigma=3
# carries no curvature") — pre-existing, reproduced at G3 §6 and on the canonical bed before it.
set -u
cd /Users/new/Developer/GitHub/designer
unset VITREA_SCENES VITREA_FIXTURES VITREA_WEB_CAPTURES VITREA_MATRIX_PATH
T=/Users/new/.claude/jobs/5c70e47f/tmp/w23/g2
mkdir -p "$T/before"
LOG="$T/g2-runs.log"
rm -f "$T/DONE"
echo "=== $(date +%H:%M:%S) build ==="
pnpm -r build > "$T/build.log" 2>&1 || { echo "BUILD FAILED"; exit 1; }
echo "=== $(date +%H:%M:%S) HEAD $(git rev-parse --short HEAD) $(git status --short | wc -l | tr -d ' ') dirty ==="
echo "=== light document $(shasum -a 256 packages/calibration/profiles/apple-macos-26.5-1x-light-standard.json | cut -c1-16) ==="
echo "=== dark  document $(shasum -a 256 packages/calibration/profiles/apple-macos-26.5-1x-dark-standard.json | cut -c1-16) ==="
cd packages/calibration
cp results/matrix.json "$T/before/matrix-0.11.0.json"
rm -rf "$T/before/web-captures"; cp -R web-captures "$T/before/web-captures"
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
