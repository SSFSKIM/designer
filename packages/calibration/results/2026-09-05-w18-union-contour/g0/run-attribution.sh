#!/bin/bash
# W18 G0 (b) — the per-term attribution runs.
#
# Eight configurations (the committed default, six single-term declines, and the charter's five
# declined together) x two tiers x two scales, over the twelve separation scenes that carry the
# question: the lone 44x44 circle, the 120x44 capsule at the same span, and the three-up at the
# declared spacing and at one past every merge threshold, over `checkerboard`, `photo` and
# `light-solid`.
#
# Both tiers under every document, which is the point. `optics.ts` derives the CSS tier's material
# from the same profile the renderer resolves, so a declined term is declined on both sides, and the
# CSS-minus-GPU difference under each decline is that term's share of the residual rather than the
# term's own size. A decline that moves the difference by nothing has no share, however large the
# term is.
#
# `capture-web` hashes the profile FILE into each cell's `capturePath`, and each configuration gets
# its own capture root, so no two configurations can be confused and the default configuration's
# captures can be diffed byte for byte against the (a) run's.
#
# Usage: `bash run-attribution.sh [configuration ...]`; with no argument, all eight.
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
  checkerboard__capsule-sm__rest checkerboard__capsule-button__rest
  checkerboard__toolbar-group__rest checkerboard__toolbar-group-wide__rest
  photo__capsule-sm__rest photo__capsule-button__rest
  photo__toolbar-group__rest photo__toolbar-group-wide__rest
  light-solid__capsule-sm__rest light-solid__capsule-button__rest
  light-solid__toolbar-group__rest light-solid__toolbar-group-wide__rest
)

CONFIGS=("$@")
if [ ${#CONFIGS[@]} -eq 0 ]; then
  CONFIGS=(default no-lens no-rim no-highlight no-lift no-inner-shadow no-outer-shadow all-declined)
fi

for config in "${CONFIGS[@]}"; do
  for tier in webgpu css; do
    for scale in 1 2; do
      echo "=== $(date +%H:%M:%S) $config / $tier @${scale}x ==="
      if [ "$config" = default ]; then
        npx tsx scripts/capture-web.ts "${SCENES[@]}" --renderer "$tier" --scale "$scale" \
          --out "$T/captures/attr-$config-$tier-${scale}x" >> "$T/logs/attr.log" 2>&1
      else
        npx tsx scripts/capture-web.ts "${SCENES[@]}" --renderer "$tier" --scale "$scale" \
          --material-profile "$T/profiles/w18-g0-$config-light.json" \
          --out "$T/captures/attr-$config-$tier-${scale}x" >> "$T/logs/attr.log" 2>&1
      fi
      echo "    exit=$?"
    done
  done
done
echo "DONE $(date +%H:%M:%S)"
