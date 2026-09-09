#!/bin/bash
# W25 G4: the canonical rebuild at the landing configuration (W25 Decision Log 7 (d); claims §5.116).
# `main` at the merge of G3b (`1d7987f`) and the two profile documents G3b froze — the LIGHT document
# carrying the jointly re-fitted pair (`optics.regular.rimLitExponent` 1.15 -> 0.85 and
# `optics.regular.rimAlongSideSlope` 0 -> 0.10; resolved fingerprint 9b7806cdefd1d1d6, file sha256
# 602b9fc6…) and the DARK document, whose own patch does not move at all — both constants being the
# material's — but which inherits the pair through the default (resolved eec7c2ea8dc89cae, file
# sha256 d9be6210…).
#
# BOTH documents' hashes move, so every cell's key moves with them and the old rows would otherwise
# sit beside the new ones: `results/matrix.json` is removed first and the WHOLE bed is rebuilt, both
# tiers, all six profiles, into the CANONICAL matrix and the CANONICAL `web-captures/` (no
# --out-matrix, no VITREA_WEB_CAPTURES).
#
# AND THEN the probe set, which is new this wave: `--set probe` on the four standard profiles on
# both tiers, into the same canonical matrix and captures. The probe set is captured routinely by
# the harness and gated by nothing (Decision Log 3 (e)); the rows enter the matrix under
# `fixtureSet: "probe"` and `adopted-thresholds.test.ts` drops them from every gated view by name.
# It runs last so a failure there cannot cost the bed a capture.
#
# The previous canonical captures and matrix are copied to scratch first: they are the 0.13.0 bed,
# the referee's "before" and the landing sheets' "GPU before" column.
#
# `--alpha` takes the declaration-conformance capture on every cell (W20 Decision Log 2 ruling 2;
# `adopted-thresholds.test.ts` fails a rebuild without them) and `--write-partial` records a cell
# whose axis is absent. Calibration and validation run before the holdout, in G3's order, so the
# holdout is the last of the gated bed to be read — it was read once at G3b's dry run (X3) and this
# rebuild reproduces those bytes rather than taking a second reading of them.
#
# The GPU tier runs before the CSS tier within each column so every dom cell's coherence axis is
# measured against a GPU capture already on disk. The GPU is shared: one capture process at a time,
# and this script serialises every run. The flags are G3b's `g3-dryrun-run.sh`, `g3-holdout-run.sh`
# and `g3-probe-run.sh` byte for byte, minus their scratch redirections, because G4 has to reproduce
# their captures.
#
# `1x-light-increased-contrast / css / holdout` is expected to exit 1 on
# `hc-text__capsule-button__rest` ("contourCurvature: a 0.00px contour sampled 512 times at sigma=3
# carries no curvature") — pre-existing, reproduced on the canonical bed at every landing since W20.
set -u
cd /Users/new/Developer/GitHub/designer
unset VITREA_SCENES VITREA_FIXTURES VITREA_WEB_CAPTURES VITREA_MATRIX_PATH
T=/Users/new/.claude/jobs/5c70e47f/tmp/w25/g4
mkdir -p "$T/before"
LOG="$T/g4-runs.log"
rm -f "$T/DONE"
echo "=== $(date +%H:%M:%S) build ==="
pnpm -r build > "$T/build.log" 2>&1 || { echo "BUILD FAILED"; exit 1; }
echo "=== $(date +%H:%M:%S) HEAD $(git rev-parse --short HEAD) $(git status --short | wc -l | tr -d ' ') dirty ==="
echo "=== light document $(shasum -a 256 packages/calibration/profiles/apple-macos-26.5-1x-light-standard.json | cut -c1-16) ==="
echo "=== dark  document $(shasum -a 256 packages/calibration/profiles/apple-macos-26.5-1x-dark-standard.json | cut -c1-16) ==="
cd packages/calibration
cp results/matrix.json "$T/before/matrix-0.13.0.json"
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
echo "=== $(date +%H:%M:%S) the probe column ==="
for renderer in webgpu css; do
  run apple-macos-26.5-1x-light-standard "$LIGHT" "$renderer" probe
  run apple-macos-26.5-2x-light-standard "$LIGHT" "$renderer" probe
  run apple-macos-26.5-1x-dark-standard "$DARK" "$renderer" probe
  run apple-macos-26.5-2x-dark-standard "$DARK" "$renderer" probe
done
echo "ALL RUNS DONE $(date +%H:%M:%S)"
touch "$T/DONE"
