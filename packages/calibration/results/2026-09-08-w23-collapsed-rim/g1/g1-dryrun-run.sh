#!/bin/bash
# W23 G1 — the dry run on the CANONICAL bed at the frozen configuration, to SCRATCH (X3, X5).
#
# What is frozen: G0's branch with main merged, plus this gate's landed constants —
#
#   light  optics.regular.rimAlpha 0.18 -> 0.844, rimLevelGain -0.628 (new), rimWidth2x 1.35 (new)
#   both   rimCollapsed 0.038 (new), rimCollapsedTinted 0.299 (new)
#   dark   optics.regular.rimAlpha 0.082 -> 0.0265, rimLevelGain +2.334 (new)
#   css    cssTierMapping.borderAlphaPerRimAlpha 1.95 -> 0.64, re-based onto the law's amplitude
#   removed  rimEnvGain, declined on every row of both beds
#
# resolvedMaterialSha256 d3e6fdaa858bebce (light, was f6c54a1ea236447a) and 18b6178d388d60a0
# (dark, was d86f480c0e136627). BOTH documents move this wave, so all six profiles are re-run and
# not one of them rides along as a byte check.
#
# Nothing below may be re-run at a different document without the holdout read being void: this is
# the wave's ONE holdout read (X3), and G2 reproduces these captures byte for byte from the main
# checkout.
#
# The order matters. Calibration and validation first on both tiers and every profile, then the
# holdout, so that a stop firing on the calibration rows can stop the gate before the holdout is
# opened. The GPU tier runs before the CSS tier within each column so every dom cell's coherence
# axis is measured against a GPU capture already on disk.
#
# The flags are the canonical rebuild's, because G2 has to reproduce these bytes with them:
# `--alpha` for the declaration-conformance rows `adopted-thresholds.test.ts` requires, and
# `--write-partial` so a cell whose axis is absent is still recorded.
#
# Everything goes to scratch: `--out-matrix` and `VITREA_WEB_CAPTURES` both move, so the canonical
# `results/matrix.json` and `web-captures/` are untouched in this worktree AND in the main checkout,
# and `apps/reference-apple/fixtures/` and `scenes.json` are read-only inputs throughout.
#
# The GPU is shared: one capture process at a time, and this script serialises every run.
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/../../../../.."
unset VITREA_SCENES VITREA_FIXTURES VITREA_MATRIX_PATH
T=/Users/new/.claude/jobs/5c70e47f/tmp/w23/g1/dryrun
mkdir -p "$T"
export VITREA_WEB_CAPTURES="$T/web-captures"
MATRIX="$T/g1-dryrun.json"
rm -f "$MATRIX" "$T/DONE"
LOG="$T/g1-runs.log"
: > "$LOG"
echo "=== $(date +%H:%M:%S) build ==="
pnpm -r build > "$T/build.log" 2>&1 || { echo "BUILD FAILED"; exit 1; }
echo "=== $(date +%H:%M:%S) HEAD $(git rev-parse --short HEAD) $(git status --short | wc -l | tr -d ' ') dirty ==="
cd packages/calibration
echo "=== light document $(shasum -a 256 profiles/apple-macos-26.5-1x-light-standard.json | cut -c1-12) ==="
echo "=== dark  document $(shasum -a 256 profiles/apple-macos-26.5-1x-dark-standard.json | cut -c1-12) ==="
LIGHT=profiles/apple-macos-26.5-1x-light-standard.json
DARK=profiles/apple-macos-26.5-1x-dark-standard.json
run() {
  local profile=$1 doc=$2 renderer=$3 sets=$4
  echo "=== $(date +%H:%M:%S) $profile / $renderer / $sets ==="
  npx tsx cli/compare.ts --profile "$profile" --material-profile "$doc" --renderer "$renderer" \
    --set "$sets" --alpha --write-partial --out-matrix "$MATRIX" >> "$LOG" 2>&1
  echo "    exit=$?"
}
for SETS in calibration,validation holdout; do
  echo "=== $(date +%H:%M:%S) the $SETS column ==="
  for RENDERER in webgpu css; do
    run apple-macos-26.5-1x-light-standard "$LIGHT" "$RENDERER" "$SETS"
    run apple-macos-26.5-2x-light-standard "$LIGHT" "$RENDERER" "$SETS"
    run apple-macos-26.5-1x-light-increased-contrast "$LIGHT" "$RENDERER" "$SETS"
    run apple-macos-26.5-1x-light-reduced-transparency "$LIGHT" "$RENDERER" "$SETS"
    run apple-macos-26.5-1x-dark-standard "$DARK" "$RENDERER" "$SETS"
    run apple-macos-26.5-2x-dark-standard "$DARK" "$RENDERER" "$SETS"
  done
done
echo "ALL RUNS DONE $(date +%H:%M:%S)"
touch "$T/DONE"
