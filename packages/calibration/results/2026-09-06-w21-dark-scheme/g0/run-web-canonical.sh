#!/bin/bash
# W21 G0 — vitrea's endpoint diagnostic on the CANONICAL dark bed, to scratch.
#
# The charter puts this diagnostic on the probe grid, where fifty-six cells would state the
# reachable span at every input the law has an anchor for. This script is the fallback the wave
# needs when the native probe cannot be attested: the same two renders — the shipped dark document
# at `backdropToneResponseStrength` 0 and the same document at strength 1 on the LIGHT anchors —
# over the thirteen dark cells the canonical bed already holds, read by the same declared-geometry
# instrument. It answers claims §5.33's question (which side of the reachable span the reference
# falls off, and by how much) on a smaller bed rather than not at all.
#
# The canonical bed's holdout is NOT captured: `--set calibration,validation`. The wave's one
# holdout read belongs to G1's dry run (W21 X6), and this is a diagnostic, not a gate.
#
# Everything lands in scratch — `VITREA_WEB_CAPTURES` and `--out-matrix` — and `VITREA_SCENES` /
# `VITREA_FIXTURES` are explicitly unset so the canonical scene bed and fixtures are read as they
# stand and nothing canonical is written.
#
# Usage: `bash run-web-canonical.sh <label> <materialProfileDoc> <outRoot>`
set -eu
LABEL="${1:?usage: run-web-canonical.sh <label> <materialProfileDoc> <outRoot>}"
DOC="${2:?}"
OUT="${3:?}"

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKTREE="$(cd "$HERE/../../../../.." && pwd)"
PROFILE=apple-macos-26.5-1x-dark-standard

unset VITREA_SCENES VITREA_FIXTURES
mkdir -p "$OUT/$LABEL"
export VITREA_WEB_CAPTURES="$OUT/$LABEL/web-captures"
cd "$WORKTREE/packages/calibration"
npx tsx cli/compare.ts --profile "$PROFILE" --material-profile "$DOC" --renderer webgpu \
  --set calibration,validation --write-partial --out-matrix "$OUT/$LABEL/matrix.json" \
  > "$OUT/$LABEL/compare.log" 2>&1
echo "WEB $LABEL DONE $(date -u +%H:%M:%SZ) -> $OUT/$LABEL"
