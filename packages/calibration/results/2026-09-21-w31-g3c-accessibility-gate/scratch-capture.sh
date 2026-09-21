#!/usr/bin/env bash
#
# W31 G3c — the lift rule, measured on scratch before it is committed to
# (Decision Log 3 (d); claims §5.164 §13).
#
#   ./scratch-capture.sh accessibility <label>   # RT + IC, both tiers, untinted photo
#   ./scratch-capture.sh identity <label>        # four standard cells, WebGPU tier
#
# `results/2026-09-21-w31-g3-chroma-fit/scratch-capture.sh` narrowed to this
# gate's two questions, COPIED rather than reused on that directory's own
# convention: nothing under `results/` is edited after commit, and a script that
# hard-codes the bed it measured is the only kind whose numbers a later reader
# can reproduce. Kept verbatim: the exclusivity refusal in two parts, the X6
# read, the scratch-only output, and the rule that nothing is appended to
# `results/matrix.json`.
#
# **The holdout is not in either mode.** `--set` is `calibration,validation`,
# which is also what makes the accessibility readings comparable LIKE FOR LIKE
# with the pre-fit figures Decision Log 3 (d) quotes — those are the
# calibration+validation medians of `pre-fit-matrix.json`, three cells a bed.
# The gate's one holdout read happens once, after `configuration.py record`.
set -euo pipefail
cd "$(dirname "$0")/../.."

MODE="${1:?usage: scratch-capture.sh accessibility|identity <label>}"
LABEL="${2:?usage: scratch-capture.sh accessibility|identity <label>}"
HERE=results/2026-09-21-w31-g3c-accessibility-gate
SCRATCH="${VITREA_G3C_SCRATCH:-/tmp/w31-g3c-captures}/$LABEL"
MATRIX="$SCRATCH/matrix.json"

if pgrep -f 'compare.ts|sweep.ts|capture-web|VitreaReference' > /dev/null; then
  echo "scratch-capture: another calibration capture is running (X6)" >&2
  exit 1
fi
FOREIGN=$( { pgrep -f 'playwright' || true; } | wc -l | tr -d ' ')
echo "foreign browser automation processes at start: $FOREIGN" | tee -a "$HERE/browser-runs.txt"
"$HERE/x6-read.sh" "w31-g3c-$MODE-$LABEL" | tee -a "$HERE/browser-runs.txt"

LIGHT=profiles/apple-macos-27.0-1x-light-standard-glass0.5.json
DARK=profiles/apple-macos-27.0-1x-dark-standard-glass0.5.json
LIGHT_RECEDED=profiles/apple-macos-27.0-1x-light-standard-glass0.5-receded.json
DARK_RECEDED=profiles/apple-macos-27.0-1x-dark-standard-glass0.5-receded.json

# Every untinted `photo` cell, both poses. `compare` intersects `--scene` with
# `--set`, so a component a profile does not declare simply plans nothing.
PHOTO=$(printf 'photo__%s__%s,' \
  capsule-button rest capsule-button inactive \
  rrect-md rest rrect-md inactive \
  rrect-ml rest rrect-ml inactive \
  rrect-sm rest rrect-sm inactive \
  toolbar-group rest toolbar-group inactive \
  glass-over-glass rest glass-over-glass inactive \
  rrect-lg rest rrect-lg inactive | sed 's/,$//')

mkdir -p "$SCRATCH"

run() {
  local profile="$1" renderer="$2" doc="$3" receded="$4" scenes="$5"
  echo "── $profile / $renderer ──"
  VITREA_WEB_CAPTURES="$SCRATCH/web-captures" npx tsx cli/compare.ts \
    --profile "$profile" --material-profile "$doc" --receded-profile "$receded" \
    --renderer "$renderer" --alpha --write-partial \
    --set calibration,validation --scene "$scenes" --out-matrix "$MATRIX"
}

if [ "$MODE" = "accessibility" ]; then
  for profile in apple-macos-27.0-1x-light-reduced-transparency-glass0.5 \
                 apple-macos-27.0-1x-light-increased-contrast-coupled-glass0.5; do
    for renderer in webgpu css; do
      run "$profile" "$renderer" "$LIGHT" "$LIGHT_RECEDED" "$PHOTO"
    done
  done
else
  # The identity spot-check's bed: one active and one inactive cell per scheme,
  # on the WebGPU tier — the tier the rule touches. Run once at this branch's
  # renderer and once at `c3e6815a`'s, and diff the PNGs.
  PAIR=photo__rrect-md__rest,photo__rrect-md__inactive
  run apple-macos-27.0-1x-light-standard-glass0.5 webgpu "$LIGHT" "$LIGHT_RECEDED" "$PAIR"
  run apple-macos-27.0-1x-dark-standard-glass0.5 webgpu "$DARK" "$DARK_RECEDED" "$PAIR"
fi

echo "── closing machine read ──"
"$HERE/x6-read.sh" "w31-g3c-$MODE-$LABEL-close" | tee -a "$HERE/browser-runs.txt"
echo "scratch matrix: $MATRIX"
