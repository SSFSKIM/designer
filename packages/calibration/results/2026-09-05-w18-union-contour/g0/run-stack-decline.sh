#!/bin/bash
# W18 G0 (c) — the stack under the outer shadow's decline.
#
# (b) attributes the whole of the neighbours' term, and part of the lone box's, to one mechanism:
# the CSS tier's per-host `box-shadow`, which its own `backdrop-filter` samples. The stack is the
# wave's second mechanism family and the same question has to be asked of it before its residual is
# attributed to the overlay's sampling route — a base host's shadow is a real element under a real
# overlay, and an unasked question would leave the route named on an assumption.
#
# Six scenes (the stack, its base alone, its overlay alone, over `checkerboard` and `photo`), both
# tiers, both scales, under `no-outer-shadow`. The default configuration for the same six is the
# (a) run's, which is byte-comparable.
#
# Usage: `bash run-stack-decline.sh`, from `packages/calibration`.
set -u
W=/Users/new/Developer/GitHub/designer/packages/calibration
T=/Users/new/.claude/jobs/5c70e47f/tmp/w18/g0

if pgrep -f 'compare.ts|sweep.ts|cost.mjs|capture.mjs' > /dev/null || lsof -i :5189 > /dev/null 2>&1; then
  echo "GPU busy: another capture is running"; exit 2
fi

cd "$W" || exit 1
unset VITREA_FIXTURES
export VITREA_SCENES="$T/scenes/w18-web.json"

SCENES=(
  checkerboard__glass-over-glass__rest checkerboard__stack-base__rest checkerboard__stack-over__rest
  photo__glass-over-glass__rest photo__stack-base__rest photo__stack-over__rest
)

for tier in webgpu css; do
  for scale in 1 2; do
    echo "=== $(date +%H:%M:%S) no-outer-shadow / $tier @${scale}x ==="
    npx tsx scripts/capture-web.ts "${SCENES[@]}" --renderer "$tier" --scale "$scale" \
      --material-profile "$T/profiles/w18-g0-no-outer-shadow-light.json" \
      --out "$T/captures/stack-no-outer-shadow-$tier-${scale}x" >> "$T/logs/stack.log" 2>&1
    echo "    exit=$?"
  done
done
echo "DONE $(date +%H:%M:%S)"
