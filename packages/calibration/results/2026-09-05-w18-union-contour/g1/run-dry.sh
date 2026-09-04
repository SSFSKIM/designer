#!/bin/bash
# W18 G1 — the whole-bed dry run on the frozen configuration (charter Decision Log 3).
#
#   bash run-dry.sh <calibrationPackageRoot> <scratchRoot> <renderer> <sets>
#
# The bed is an ARGUMENT and no checkout's path is written here: this script runs from a branch in
# a worktree, and a hardcoded path would either capture the wrong tree or silently write beside
# the canonical one. Both tiers of one configuration share a matrix so the cross-tier coherence
# rows compute, and the GPU tier has to be captured FIRST — a dom cell's coherence axis is
# measured against the webgpu capture already on disk and is simply absent where there is none.
#
# The holdout is in `--set` because W18 G1 reads it ONCE on this frozen configuration (X8); the
# GPU tier is bound unchanged by this wave, so its holdout rows are not a holdout read.
#
# Nothing canonical is written: `--out-matrix` and `VITREA_WEB_CAPTURES` both point at scratch,
# and `VITREA_SCENES` / `VITREA_FIXTURES` are unset so the committed bed is read where it lies.
set -u
W=$1; T=$2; RENDERER=$3; SETS=$4
if pgrep -f 'compare.ts|sweep.ts|cost.mjs|capture.mjs|capture-web|VitreaReference' > /dev/null \
   || lsof -i :5189 > /dev/null 2>&1; then
  echo "GPU busy: another capture is running"; exit 2
fi
mkdir -p "$T"
cd "$W" || exit 1
unset VITREA_SCENES VITREA_FIXTURES
LIGHT=profiles/apple-macos-26.5-1x-light-standard.json
DARK=profiles/apple-macos-26.5-1x-dark-standard.json
run() {
  local profile=$1 doc=$2
  echo "=== $(date +%H:%M:%S) $profile / $RENDERER / $SETS ==="
  VITREA_WEB_CAPTURES="$T/web-captures" npx tsx cli/compare.ts --profile "$profile" \
    --material-profile "$doc" --renderer "$RENDERER" --set "$SETS" --write-partial \
    --out-matrix "$T/matrix.json" >> "$T/runs.log" 2>&1
  echo "    exit=$?"
}
run apple-macos-26.5-1x-light-standard "$LIGHT"
run apple-macos-26.5-2x-light-standard "$LIGHT"
run apple-macos-26.5-1x-light-increased-contrast "$LIGHT"
run apple-macos-26.5-1x-light-reduced-transparency "$LIGHT"
run apple-macos-26.5-1x-dark-standard "$DARK"
run apple-macos-26.5-2x-dark-standard "$DARK"
echo "DONE $RENDERER/$SETS $(date +%H:%M:%S)"
