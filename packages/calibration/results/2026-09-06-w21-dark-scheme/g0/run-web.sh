#!/bin/bash
# W21 G0 — vitrea's side on the dark probe grid, to SCRATCH, one capture at a time.
#
# Three renders of the same 56-cell grid on the GPU tier, all read afterwards by `read.py` under the
# declared geometry so that vitrea and the reference are measured by one instrument:
#
#   web0        the SHIPPED dark profile — `backdropToneResponseStrength` 0, the response law
#               standing down, the body carried by the 0.05 tint at alpha 0.97 (C9a's four-cell fit);
#   web1        the same document with `backdropToneResponseStrength` 1 and NOTHING else changed, so
#               the law runs on the LIGHT reference's anchors. This is not a candidate — it is the
#               far end of the reachable span, and web0/web1 together give the required strength per
#               cell that claims 5.33's endpoint table reports;
#   candidate   the same document with `backdropToneResponseThin` / `Thick` replaced by the anchors
#               the probe measured and `backdropToneResponseStrength` 1. A first read, not a fit:
#               G1 fits, on the probe's calibration split.
#
# Every capture goes to scratch — `VITREA_WEB_CAPTURES` and `--out-matrix` — and every read is on the
# PROBE bed through `VITREA_SCENES` / `VITREA_FIXTURES`, so no canonical file is written or read.
# `--set calibration,validation` keeps the probe's holdout column and its one `recorded` cell out of
# every capture: the wave's holdout read is the CANONICAL bed's, at G1 (W21 X6).
#
# Usage: `bash run-web.sh <label> <materialProfileDoc> <outRoot>`
set -eu
LABEL="${1:?usage: run-web.sh <label> <materialProfileDoc> <outRoot>}"
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
