#!/bin/bash
# W20 G0: the declaration-conformance instrument over the W19 bed, to SCRATCH.
#
# The instrument is the shape axis's new rows (`drawnAreaWeb`, `declaredIoUWeb`,
# `declaredContour{P95,Max}Web`), measured from a second capture of each scene taken over a
# transparent page with the backdrop raster hidden — `capture-web --alpha`, wired through
# `compare --alpha`. This run reads the defect BEFORE any fix (contract X1), so it must not
# touch the canonical matrix or the canonical captures: `--out-matrix` and `VITREA_WEB_CAPTURES`
# both point into scratch, and holdout is not in `--set`.
#
# Six profiles, two tiers. The GPU tier runs first per profile so every dom cell's coherence
# axis is measured against a capture already on disk, exactly as the canonical rebuild does.
set -u
cd /Users/new/Developer/GitHub/designer/.claude/worktrees/agent-a25a82664c39b28df
unset VITREA_SCENES VITREA_FIXTURES
T=/Users/new/.claude/jobs/5c70e47f/tmp/w20/g0-a/bed
mkdir -p "$T"
export VITREA_WEB_CAPTURES="$T/web-captures"
MATRIX="$T/g0-conformance.json"
rm -f "$MATRIX"
LOG="$T/g0-runs.log"
: > "$LOG"
echo "=== $(date +%H:%M:%S) build ==="
pnpm -r build > "$T/build.log" 2>&1 || { echo "BUILD FAILED"; exit 1; }
echo "=== $(date +%H:%M:%S) HEAD $(git rev-parse --short HEAD) ==="
cd packages/calibration
LIGHT=profiles/apple-macos-26.5-1x-light-standard.json
DARK=profiles/apple-macos-26.5-1x-dark-standard.json
run() {
  local profile=$1 doc=$2 renderer=$3
  echo "=== $(date +%H:%M:%S) $profile / $renderer ==="
  npx tsx cli/compare.ts --profile "$profile" --material-profile "$doc" --renderer "$renderer" \
    --set calibration,validation --alpha --write-partial --out-matrix "$MATRIX" >> "$LOG" 2>&1
  echo "    exit=$?"
}
for renderer in webgpu css; do
  run apple-macos-26.5-1x-light-standard "$LIGHT" "$renderer"
  run apple-macos-26.5-2x-light-standard "$LIGHT" "$renderer"
  run apple-macos-26.5-1x-dark-standard "$DARK" "$renderer"
  run apple-macos-26.5-2x-dark-standard "$DARK" "$renderer"
  run apple-macos-26.5-1x-light-increased-contrast "$LIGHT" "$renderer"
  run apple-macos-26.5-1x-light-reduced-transparency "$LIGHT" "$renderer"
done
echo "ALL RUNS DONE $(date +%H:%M:%S)"
