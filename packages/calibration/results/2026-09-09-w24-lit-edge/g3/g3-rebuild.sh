#!/bin/bash
# W24 G3: the canonical rebuild at the landing (W24 Decision Log 3 (i); claims §5.109). `main` at the
# merged tree (`b3c5d28`) and the two profile documents G2 froze — the LIGHT document re-recorded on
# the lit edge's law and the collapse's transmission (`rimLitAxis` [-0.7071, -0.7071],
# `rimLitExponent` 1.15, `collapseTransmission` 0.017, `collapseTransmission2x` 0.070; resolved
# fingerprint 7968a7f8106b10a4, file sha256 cecea9cd…) and the DARK document, whose own patch does
# not move at all — both mechanisms being the material's — but which inherits the four through the
# default (resolved 0d741cd19cd1243b, file sha256 ef4af5ae…).
#
# BOTH documents' hashes move, so every cell's key moves with them and the old rows would otherwise
# sit beside the new ones: `results/matrix.json` is removed first and the WHOLE bed is rebuilt, both
# tiers, all six profiles, into the CANONICAL matrix and the CANONICAL `web-captures/` (no
# --out-matrix, no VITREA_WEB_CAPTURES).
#
# The previous canonical captures and matrix are copied to scratch first: they are the 0.12.0 bed,
# the referee's "before" and the landing sheet's "GPU before" column.
#
# `--alpha` takes the declaration-conformance capture on every cell (W20 Decision Log 2 ruling 2;
# `adopted-thresholds.test.ts` fails a rebuild without them) and `--write-partial` records a cell
# whose axis is absent. Calibration and validation run before the holdout, in G2's order, so the
# holdout is the last thing the bed reads — it was read once at G2's dry run (X3) and this rebuild
# reproduces those bytes rather than taking a second reading of them.
#
# The GPU tier runs before the CSS tier within each column so every dom cell's coherence axis is
# measured against a GPU capture already on disk. The GPU is shared: one capture process at a time,
# and this script serialises every run. Derived from W23 G2's `g2-rebuild.sh` and this wave's
# `g2/g2-dryrun-run.sh`, whose flags it must reproduce byte for byte.
#
# `1x-light-increased-contrast / css / holdout` is expected to exit 1 on
# `hc-text__capsule-button__rest` ("contourCurvature: a 0.00px contour sampled 512 times at sigma=3
# carries no curvature") — pre-existing, reproduced on the canonical bed at every landing since W20.
set -u
cd /Users/new/Developer/GitHub/designer
unset VITREA_SCENES VITREA_FIXTURES VITREA_WEB_CAPTURES VITREA_MATRIX_PATH
T=/Users/new/.claude/jobs/5c70e47f/tmp/w24/g3
mkdir -p "$T/before"
LOG="$T/g3-runs.log"
rm -f "$T/DONE"
echo "=== $(date +%H:%M:%S) build ==="
pnpm -r build > "$T/build.log" 2>&1 || { echo "BUILD FAILED"; exit 1; }
echo "=== $(date +%H:%M:%S) HEAD $(git rev-parse --short HEAD) $(git status --short | wc -l | tr -d ' ') dirty ==="
echo "=== light document $(shasum -a 256 packages/calibration/profiles/apple-macos-26.5-1x-light-standard.json | cut -c1-16) ==="
echo "=== dark  document $(shasum -a 256 packages/calibration/profiles/apple-macos-26.5-1x-dark-standard.json | cut -c1-16) ==="
cd packages/calibration
cp results/matrix.json "$T/before/matrix-0.12.0.json"
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
