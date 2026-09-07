#!/bin/bash
# W21 G1 — one fit candidate rendered on the dark probe grid, to SCRATCH.
#
# G0's `run-web.sh` with one change: the fixtures path no longer needs canonicalising here, because
# `packages/calibration/web/vite.config.ts` now resolves `VITREA_FIXTURES` before it mounts it and
# before it checks containment (W21 Decision Log 2 (g); claims §5.89 §8). The `cd`-and-`pwd` dance
# G0 had to write around that bug is gone.
#
# `--set calibration,validation` keeps the probe's holdout column and its `recorded` cell out of
# every capture: the wave's one holdout read is the CANONICAL bed's, at this gate's dry run (X6).
#
# Usage: `bash run-probe-web.sh <label> <materialProfileDoc> <outRoot>`
set -eu
LABEL="${1:?usage: run-probe-web.sh <label> <materialProfileDoc> <outRoot>}"
DOC="${2:?}"
OUT="${3:?}"

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKTREE="$(cd "$HERE/../../../../.." && pwd)"
SCENES="$WORKTREE/apps/reference-apple/scenes-w21-probe.json"
PROBE="$HERE/../probe"
PROFILE=apple-macos-26.5-1x-dark-standard

mkdir -p "$OUT/$LABEL"
export VITREA_SCENES="$SCENES"
export VITREA_FIXTURES="$PROBE"
export VITREA_WEB_CAPTURES="$OUT/$LABEL/web-captures"
cd "$WORKTREE/packages/calibration"
npx tsx cli/compare.ts --profile "$PROFILE" --material-profile "$DOC" --renderer webgpu \
  --set calibration,validation --write-partial --out-matrix "$OUT/$LABEL/matrix.json" \
  > "$OUT/$LABEL/compare.log" 2>&1
echo "WEB $LABEL DONE $(date -u +%H:%M:%SZ) -> $OUT/$LABEL"
