#!/bin/bash
# W22 G1 — the dry run on the CANONICAL bed at the frozen configuration, to SCRATCH (contract X5).
#
# What is frozen: main at `3e88921` (W22 G0's shimmer gate and G3's backdrop-stack fix both merged)
# plus this gate's single fitted constant — `optics.regular.specularGain` 0.55 -> 0 on the light
# profile, `resolvedMaterialSha256` f6c54a1ea236447a. The dark document does NOT move: its patch has
# pinned `specularGain` 0 since W21 G1, so its resolved material and its digest d86f480c0e136627
# stand, and `platform-web/src/dark-profile.ts` regenerates byte-identical. Nothing below may be
# re-run at a different document without the holdout read being void: this is the wave's ONE holdout
# read, and G2 reproduces these captures byte for byte from the main checkout.
#
# ALL SIX PROFILES, both tiers. W21's dry run took the two dark profiles and one light one, because
# only the dark document moved. This wave's constant is on the LIGHT document, which the two light
# standard profiles and BOTH accessibility profiles resolve through, so four of the six move and the
# gate cannot be run over a partial bed at all (G0 §4: the cross-tier identity check fails on any
# partial rebuild). The two dark profiles ride along for the same reason W21's light one did — as a
# byte check that nothing in the renderer's defaults moved under this gate's edits.
#
# The order matters. Calibration and validation first on both tiers and every profile, then the
# holdout, so that a stop firing on the calibration rows can stop the gate before the holdout is
# opened. The GPU tier runs before the CSS tier within each column so every dom cell's coherence
# axis is measured against a GPU capture already on disk.
#
# The flags are the CANONICAL rebuild's (`w21/g2/g2-rebuild.sh`), because G2 has to reproduce these
# bytes with them: `--alpha` for the declaration-conformance rows `adopted-thresholds.test.ts`
# requires (G0 §7.6 — a bed without them fails the W20 conformance rows for absence), and
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
T=/Users/new/.claude/jobs/5c70e47f/tmp/w22/g1/dryrun
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
