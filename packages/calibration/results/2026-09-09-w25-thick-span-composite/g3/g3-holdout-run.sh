#!/bin/bash
# W25 G3 — THE WAVE'S ONE HOLDOUT READ, on the frozen configuration, to SCRATCH (X3).
#
# What is frozen: G0's, G1's and G2's branches merged into main, plus this gate's one landed
# constant —
#
#   both   optics.regular.rimLitExponent 1.15 -> 0.85 and optics.regular.rimAlongSideSlope
#          0.45 -> 0.10 — the JOINT re-fit (W25 G3b; Decision Log 6), both on the material's
#          default, the light patch naming them and the dark difference document inheriting them
#   none   sizeScatterHeavyShareThick1x / …2x and sizeToneLevelFar stay at 0, declined on the probe
#          set's own measurement and left there by the ruling (`g3-dryrun.md` §1)
#   css    nothing: the field's integral around the contour is exactly zero
#
# resolvedMaterialSha256 9b7806cdefd1d1d6 (light, was 290f52cb025fce7b) and eec7c2ea8dc89cae
# (dark, was 64ef5c3002d15009).
#
# `g3-dryrun-run.sh`'s twin, and it is run ONCE, LAST, on the constant above and on nothing else.
# Every clause and every stop was read on the calibration and validation columns before this ran and
# the firings were dispositioned in the document; nothing in the material, the documents, the
# goldens or the code moved between the two runs. G4 reproduces these captures byte for byte from
# the main checkout, out of `g3-digests.txt`. Re-running this at a different document would void the
# read.
#
# The GPU tier runs before the CSS tier so every dom cell's coherence axis is measured against a GPU
# capture already on disk. The flags are the canonical rebuild's — `--alpha` and `--write-partial` —
# because G4 has to reproduce these bytes with them.
#
# Everything goes to scratch: `--out-matrix` and `VITREA_WEB_CAPTURES` both move, so the canonical
# `results/matrix.json` and `web-captures/` are untouched in this worktree AND in the main checkout,
# and `apps/reference-apple/fixtures/` and `scenes.json` are read-only inputs throughout.
#
# The GPU is shared: one capture process at a time, and this script serialises every run.
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/../../../../.."
unset VITREA_SCENES VITREA_FIXTURES VITREA_MATRIX_PATH
T=/Users/new/.claude/jobs/5c70e47f/tmp/w25/g3/dryrun
mkdir -p "$T"
export VITREA_WEB_CAPTURES="$T/web-captures"
MATRIX="$T/g3-dryrun.json"
rm -f "$T/DONE-holdout"
LOG="$T/g3-runs.log"
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
