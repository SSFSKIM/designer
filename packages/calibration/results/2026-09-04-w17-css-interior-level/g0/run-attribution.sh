#!/bin/bash
# W17 G0 (a) — the attribution runs.
#
# Six configurations (the committed default, the four single-term declines, all four declined
# together) × the four standard profiles (1x and 2x, light and dark), the GPU tier only,
# calibration and validation only — the holdout is NOT captured (contract X8; it is G1's single
# read of the frozen configuration). Twenty-four runs, one at a time on a shared adapter.
#
# Nothing canonical is written: every run takes `--out-matrix` under the scratch root and
# `VITREA_WEB_CAPTURES` beside it. Each configuration gets its OWN matrix file, so a re-run of one
# configuration cannot append beside another's rows, and its own capture root, so the default
# configuration's captures can be diffed byte for byte against the canonical `web-captures/`.
#
# The light document drives the two light profiles and the dark document the two dark ones, the
# way `results/2026-09-04-w16-css-two-layer/g1/run-dry.sh` does it.
#
# Usage: `bash run-attribution.sh [configuration ...]`; with no argument, all six.
set -u
REPO=/Users/new/Developer/GitHub/designer
W=$REPO/packages/calibration
T=/Users/new/.claude/jobs/5c70e47f/tmp/w17/g0

if pgrep -f 'compare.ts|sweep.ts|cost.mjs|capture.mjs' > /dev/null || lsof -i :5189 > /dev/null 2>&1; then
  echo "GPU busy: another capture is running"; exit 2
fi

cd "$W" || exit 1
unset VITREA_SCENES VITREA_FIXTURES

doc() {  # <configuration> <light|dark>
  if [ "$1" = default ]; then echo "$W/profiles/apple-macos-26.5-1x-$2-standard.json"
  else echo "$T/profiles/w17-g0-$1-$2.json"; fi
}

run() {  # <configuration> <profileKey> <light|dark>
  local config=$1 profile=$2 scheme=$3
  echo "=== $(date +%H:%M:%S) $config / $profile ==="
  VITREA_WEB_CAPTURES="$T/captures/$config" npx tsx cli/compare.ts \
    --profile "$profile" --material-profile "$(doc "$config" "$scheme")" \
    --renderer webgpu --set calibration,validation --write-partial \
    --out-matrix "$T/matrices/$config.json" >> "$T/logs/$config.log" 2>&1
  echo "    exit=$?"
}

CONFIGS=("$@")
if [ ${#CONFIGS[@]} -eq 0 ]; then
  CONFIGS=(default no-lens no-rim no-highlight no-lift all-declined)
fi

for config in "${CONFIGS[@]}"; do
  run "$config" apple-macos-26.5-1x-light-standard light
  run "$config" apple-macos-26.5-2x-light-standard light
  run "$config" apple-macos-26.5-1x-dark-standard dark
  run "$config" apple-macos-26.5-2x-dark-standard dark
done
echo "DONE $(date +%H:%M:%S)"
