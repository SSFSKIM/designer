#!/bin/bash
# W19 G0 (b) — the readings, taken off the captures the ladder run wrote.
#
# X4 first and unconditionally: the recovery contract runs on this wave's reader, under both masks it
# uses, on a control cell that has a native fixture and on a new rung that does not, on both tiers and
# at both scales — and only then are the ladder's own rows read. A reading taken before its
# instrument was validated is not a reading.
#
# Usage: `bash run-read.sh <scenesJson> <captureRoot> <partsDir>`, from `packages/calibration`.
set -eu
SCENES="${1:?usage: run-read.sh <scenesJson> <captureRoot> <partsDir>}"
CAPTURES="${2:?}"
PARTS="${3:?}"
mkdir -p "$PARTS"
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

x4() { npx tsx "$HERE/x4-recovery.ts" "$SCENES" "$2" "$1" "$3" "$4"; }

{
  echo "["
  x4 css "$CAPTURES/std-css-1x" photo__capsule-button__rest-tint-orange-half 1
  echo ","
  x4 css "$CAPTURES/std-css-1x" photo__capsule-button__rest-tint-orange-020 1
  echo ","
  x4 webgpu "$CAPTURES/std-webgpu-1x" checkerboard__capsule-button__rest-tint-orange 1
  echo ","
  x4 css "$CAPTURES/std-css-2x" photo__capsule-button__rest-tint-orange-half 2
  echo "]"
} > "$PARTS/x4-recovery.json"

npx tsx "$HERE/ladder.ts" "$SCENES" "$CAPTURES/std-webgpu-1x" "$CAPTURES/std-css-1x" 1 "$PARTS/ladder-1x.json"
npx tsx "$HERE/ladder.ts" "$SCENES" "$CAPTURES/std-webgpu-2x" "$CAPTURES/std-css-2x" 2 "$PARTS/ladder-2x.json"
for acc in reduced-transparency increased-contrast; do
  npx tsx "$HERE/ladder.ts" "$SCENES" "$CAPTURES/fold-$acc-webgpu-1x" "$CAPTURES/fold-$acc-css-1x" 1 \
    "$PARTS/ladder-fold-$acc.json"
done
echo "READ DONE"
