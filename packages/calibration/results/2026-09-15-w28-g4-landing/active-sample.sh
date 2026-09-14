#!/bin/sh
# W28 G4, the other half of the seam proof: the ACTIVE pose is unmoved too.
#
# The inactive half is `seam-identity.ts`, against G2's own captures. This half runs
# the ordinary `compare` pipeline — the one the canonical matrix is built by, with its
# own accessibility translation, material-profile selection and capture driver — over
# the six scenes every profile's canonical capture directory holds, on both tiers, into
# a scratch capture root. `compare-active.py` then compares the PNGs byte for byte with
# the canonical `web-captures/` on this machine.
#
# The matrix goes to scratch as well: this run measures nothing the canonical matrix
# should keep, and `--out-matrix` outside `results/` is the harness's own refusal seam.
set -e
here=$(cd "$(dirname "$0")" && pwd)
pkg=$(cd "$here/../.." && pwd)
out=${1:-/tmp/w28-g4-active}
scenes="checkerboard__capsule-button__rest checkerboard__rrect-md__rest photo__capsule-button__rest photo__capsule-button__rest-tint-orange photo__rrect-lg__rest photo__rrect-md__rest"

cd "$pkg"
for profile in \
  apple-macos-26.5-1x-dark-standard \
  apple-macos-26.5-2x-dark-standard \
  apple-macos-26.5-1x-light-standard \
  apple-macos-26.5-2x-light-standard \
  apple-macos-26.5-1x-light-increased-contrast \
  apple-macos-26.5-1x-light-reduced-transparency
do
  case "$profile" in
    *dark*) doc=profiles/apple-macos-26.5-1x-dark-standard.json ;;
    *)      doc=profiles/apple-macos-26.5-1x-light-standard.json ;;
  esac
  for renderer in webgpu css; do
    echo "── $profile / $renderer"
    VITREA_WEB_CAPTURES="$out/captures" npx tsx cli/compare.ts \
      --profile "$profile" \
      --material-profile "$doc" \
      --renderer "$renderer" \
      --set calibration,validation,probe \
      --scene $(echo "$scenes" | tr ' ' ',') \
      --out-matrix "$out/matrix.json" \
      --write-partial
  done
done
