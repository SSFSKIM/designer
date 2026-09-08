#!/bin/bash
# W24 G2 — THE WAVE'S ONE HOLDOUT READ, on the frozen configuration, to SCRATCH (X3).
#
# What is frozen: G0's and G1's branches merged into main, plus this gate's landed constants —
#
#   both   optics.regular.rimLitExponent 1.15 (new), rimLitAxis [-0.7071, -0.7071] (new)
#   both   collapseTransmission 0.017 (new), collapseTransmission2x 0.070 (new)
#   both   the one-sided specular retired from the rim on both tiers
#   css    adaptedSourceOptics carries the transmission as A' = A - k.c with the tint re-solved;
#          interiorBandLight integrates the lit factor over the corner arcs
#
# resolvedMaterialSha256 7968a7f8106b10a4 (light, was c426a37744c38cce) and 0d741cd19cd1243b
# (dark, was bf5752ac1b152238). BOTH documents move this wave, so all six profiles are re-run and
# not one of them rides along as a byte check.
#
# `g2-dryrun-run.sh`'s twin, and it is run ONCE, LAST, on the constants above and on nothing else.
# Every clause and every stop was read on the calibration and validation columns before this ran and
# none of them fired; nothing in the material, the documents, the goldens or the code moved between
# the two runs. G3 reproduces these captures byte for byte from the main checkout, out of
# `g2-digests.txt`. Re-running this at a different document would void the read.
#
# The GPU tier runs before the CSS tier so every dom cell's coherence axis is measured against a GPU
# capture already on disk. The flags are the canonical rebuild's — `--alpha`
# for the declaration-conformance rows and `--write-partial` so a cell whose axis is absent is still
# recorded — because G3 has to reproduce these bytes with them.
#
# Everything goes to scratch: `--out-matrix` and `VITREA_WEB_CAPTURES` both move, so the canonical
# `results/matrix.json` and `web-captures/` are untouched in this worktree AND in the main checkout,
# and `apps/reference-apple/fixtures/` and `scenes.json` are read-only inputs throughout.
#
# The GPU is shared: one capture process at a time, and this script serialises every run.
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/../../../../.."
unset VITREA_SCENES VITREA_FIXTURES VITREA_MATRIX_PATH
T=/Users/new/.claude/jobs/5c70e47f/tmp/w24/g2
mkdir -p "$T"
export VITREA_WEB_CAPTURES="$T/web-captures"
MATRIX="$T/g2-dryrun.json"
rm -f "$T/DONE-holdout"
LOG="$T/g2-runs.log"
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
SETS=holdout
for RENDERER in webgpu css; do
  run apple-macos-26.5-1x-light-standard "$LIGHT" "$RENDERER" "$SETS"
  run apple-macos-26.5-2x-light-standard "$LIGHT" "$RENDERER" "$SETS"
  run apple-macos-26.5-1x-light-increased-contrast "$LIGHT" "$RENDERER" "$SETS"
  run apple-macos-26.5-1x-light-reduced-transparency "$LIGHT" "$RENDERER" "$SETS"
  run apple-macos-26.5-1x-dark-standard "$DARK" "$RENDERER" "$SETS"
  run apple-macos-26.5-2x-dark-standard "$DARK" "$RENDERER" "$SETS"
done
echo "ALL HOLDOUT RUNS DONE $(date +%H:%M:%S)"
touch "$T/DONE-holdout"
