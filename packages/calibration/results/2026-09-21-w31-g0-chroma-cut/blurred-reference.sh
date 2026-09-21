#!/usr/bin/env bash
#
# W31 G0 — ratio (iii) over the untinted chroma cells (claims §5.161 §3).
#
# A second pass over the SAME scratch captures rather than a flag on the first,
# because recovering the reference radius bisects over separable Gaussians of
# the whole backdrop and the two ratios the wave's tolerance is declared on do
# not need it. `--skip-capture`: no browser runs, so no X6 read is owed.
#
# Its own matrix file, so the first pass's rows are not rewritten by a second
# measurement of the same keys. A recorded number is never rewritten.
set -euo pipefail
cd "$(dirname "$0")/../.."
HERE=results/2026-09-21-w31-g0-chroma-cut
MATRIX="$HERE/scratch-matrix-blurred.json"
SCENES="photo__capsule-button__inactive,photo__capsule-button__rest,photo__glass-over-glass__inactive,photo__glass-over-glass__rest,photo__rrect-lg__inactive,photo__rrect-lg__rest,photo__rrect-md__inactive,photo__rrect-md__rest,photo__rrect-ml__inactive,photo__rrect-ml__rest,photo__rrect-sm__inactive,photo__rrect-sm__rest,photo__toolbar-group__inactive,photo__toolbar-group__rest,mid-chroma-solid__capsule-button__inactive,mid-chroma-solid__capsule-button__rest,mid-chroma-solid__rrect-lg__inactive,mid-chroma-solid__rrect-lg__rest,mid-chroma-solid__rrect-md__inactive,mid-chroma-solid__rrect-md__rest"
SETS=calibration,validation,holdout,probe
LIGHT=profiles/apple-macos-27.0-1x-light-standard-glass0.5.json
DARK=profiles/apple-macos-27.0-1x-dark-standard-glass0.5.json

for profile in apple-macos-27.0-1x-light-standard-glass0.5 apple-macos-27.0-2x-light-standard-glass0.5 \
               apple-macos-27.0-1x-dark-standard-glass0.5 apple-macos-27.0-2x-dark-standard-glass0.5; do
  case "$profile" in *-dark-*) doc="$DARK"; receded="${DARK%.json}-receded.json" ;;
                     *) doc="$LIGHT"; receded="${LIGHT%.json}-receded.json" ;; esac
  for renderer in webgpu css; do
    echo "── $profile / $renderer ──"
    VITREA_WEB_CAPTURES=/tmp/w31-g0-captures npx tsx cli/compare.ts \
      --profile "$profile" --material-profile "$doc" --receded-profile "$receded" \
      --renderer "$renderer" --skip-capture --alpha --write-partial --blurred-chroma-reference \
      --set "$SETS" --scene "$SCENES" --out-matrix "$MATRIX" || true
  done
done
for profile in apple-macos-26.5-1x-light-standard apple-macos-26.5-2x-light-standard \
               apple-macos-26.5-1x-dark-standard apple-macos-26.5-2x-dark-standard; do
  for renderer in webgpu css; do
    echo "── $profile / $renderer ──"
    VITREA_WEB_CAPTURES=/tmp/w31-g0-captures npx tsx cli/compare.ts \
      --profile "$profile" --renderer "$renderer" --skip-capture --alpha --write-partial \
      --blurred-chroma-reference --set "$SETS" --scene "$SCENES" --out-matrix "$MATRIX" || true
  done
done
