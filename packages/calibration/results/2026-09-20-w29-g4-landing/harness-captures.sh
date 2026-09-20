#!/usr/bin/env bash
#
# W29 G4 — the harness's own render of the cells this landing needs, at the
# macOS 27 documents the runtime now ships.
#
# Two consumers, and neither reads a native fixture, opens a manifest, computes
# a fidelity number or writes a row:
#
#   1. `apps/demo/e2e/fixtures/checkerboard__capsule-button__rest__webgpu.png`,
#      which that spec compares the live site against. The demo draws the
#      runtime's default material and that is macOS 27's from 0.19.0, so the
#      committed macOS 26.5 copy would now fail for the right reason.
#   2. The eye's harness column (acceptance clause 7): `photo__rrect-md` in both
#      poses, at 2x, in both schemes, beside the demo and the playground.
#
# Re-capturing the WEB side of a cell spends nothing — W28 G4 established that
# (claims §5.148 §1) and it is why this is admissible over a holdout scene at
# all. `--receded-profile` is deliberately NOT passed: the point of the inactive
# pair is that the ROOT poses itself and applies the macOS 27 receded document it
# now ships, which is the selection this gate landed.
#
# Output goes to a scratch tree outside the repository. The canonical
# `web-captures/` is the capture machine's record of the canonical reads and
# nothing here is one.
set -euo pipefail
cd "$(dirname "$0")/../.."

OUT="${VITREA_G4_CAPTURES:-$HOME/vitrea-w29-g4-scratch/captures}"
LIGHT=profiles/apple-macos-27.0-1x-light-standard-glass0.5.json
DARK=profiles/apple-macos-27.0-1x-dark-standard-glass0.5.json

if pgrep -f 'compare.ts|sweep.ts|capture-web|VitreaReference|playwright' > /dev/null; then
  echo "harness-captures: another capture process is running (X7)" >&2
  exit 1
fi
RT=$(defaults read com.apple.universalaccess reduceTransparency 2>/dev/null || echo 0)
IC=$(defaults read com.apple.universalaccess increaseContrast 2>/dev/null || echo 0)
GLASS=$(defaults read -g NSGlassTintAmount 2>/dev/null || echo absent)
echo "machine: $(sw_vers -productVersion)/$(sw_vers -buildVersion) RT=$RT IC=$IC NSGlassTintAmount=$GLASS"
[ "$RT" = "0" ] || { echo "harness-captures: Reduce Transparency is $RT" >&2; exit 1; }
[ "$IC" = "0" ] || { echo "harness-captures: Increase Contrast is $IC" >&2; exit 1; }
[ "$GLASS" = "0.5" ] || { echo "harness-captures: NSGlassTintAmount is $GLASS" >&2; exit 1; }

echo "── 1x light, the demo's fixture cell ──"
npx tsx scripts/capture-web.ts checkerboard__capsule-button__rest \
  --renderer webgpu --scale 1 --color-scheme light \
  --material-profile "$LIGHT" \
  --out "$OUT/apple-macos-27.0-1x-light-standard-glass0.5"

echo "── 2x light, the eye's two poses ──"
npx tsx scripts/capture-web.ts photo__rrect-md__rest photo__rrect-md__inactive \
  --renderer webgpu --scale 2 --color-scheme light \
  --material-profile "$LIGHT" \
  --out "$OUT/apple-macos-27.0-2x-light-standard-glass0.5"

echo "── 2x dark, the same two ──"
npx tsx scripts/capture-web.ts photo__rrect-md__rest photo__rrect-md__inactive \
  --renderer webgpu --scale 2 --color-scheme dark \
  --material-profile "$DARK" \
  --out "$OUT/apple-macos-27.0-2x-dark-standard-glass0.5"

echo "── closing machine read ──"
echo "RT=$(defaults read com.apple.universalaccess reduceTransparency 2>/dev/null || echo 0)" \
     "IC=$(defaults read com.apple.universalaccess increaseContrast 2>/dev/null || echo 0)" \
     "NSGlassTintAmount=$(defaults read -g NSGlassTintAmount 2>/dev/null || echo absent)"
