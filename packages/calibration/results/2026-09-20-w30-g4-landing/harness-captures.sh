#!/usr/bin/env bash
#
# W30 G4 — the harness's own render of the two cells this landing's eye needs, at
# the four macOS 27 documents 0.20.0 ships.
#
# W29 G4's script (`results/2026-09-20-w29-g4-landing/harness-captures.sh`) with
# the cells changed, and the change is the reading. That gate photographed one
# scene in two POSES, because it had moved the recede. This wave moved the outer
# shadow's blur from a constant to a line in the casting span, so the pair that
# shows it is two SPANS: `photo__capsule-button__rest` at 44 CSS px, where the
# law now draws 2.13 where 0.19.0 drew 11.0, and `photo__rrect-lg__rest` at 160,
# where it draws 17.37 where 0.19.0 drew 11.0. One scene at one span would show
# the wave's operator as a tuning.
#
# Both cells at 2x in both schemes. `photo` rather than `checkerboard` because it
# is the one backdrop family carrying both spans in both schemes; the dark bed
# has no `checkerboard__rrect-lg` cell at all.
#
# Re-capturing the WEB side of a cell spends nothing — W28 G4 established that
# (claims §5.148 §1) — which is what makes this admissible over `photo__rrect-lg`,
# a holdout scene. Nothing here reads a native fixture, opens a manifest, computes
# a fidelity number or writes a row.
#
# `--receded-profile` is deliberately not passed: both cells are active poses.
#
# Output goes to a scratch tree outside the repository. The canonical
# `web-captures/` is the capture machine's record of the canonical reads and
# nothing here is one.
set -euo pipefail
cd "$(dirname "$0")/../.."

OUT="${VITREA_G4_CAPTURES:-$HOME/vitrea-w30-g4-scratch/captures}"
LIGHT=profiles/apple-macos-27.0-1x-light-standard-glass0.5.json
DARK=profiles/apple-macos-27.0-1x-dark-standard-glass0.5.json

if pgrep -f 'compare.ts|sweep.ts|capture-web|VitreaReference' > /dev/null; then
  echo "harness-captures: another capture process is running (X6)" >&2
  exit 1
fi
RT=$(defaults read com.apple.universalaccess reduceTransparency 2>/dev/null || echo 0)
IC=$(defaults read com.apple.universalaccess increaseContrast 2>/dev/null || echo 0)
GLASS=$(defaults read -g NSGlassTintAmount 2>/dev/null || echo absent)
echo "machine: $(sw_vers -productVersion)/$(sw_vers -buildVersion) RT=$RT IC=$IC NSGlassTintAmount=$GLASS"
[ "$RT" = "0" ] || { echo "harness-captures: Reduce Transparency is $RT" >&2; exit 1; }
[ "$IC" = "0" ] || { echo "harness-captures: Increase Contrast is $IC" >&2; exit 1; }
[ "$GLASS" = "0.5" ] || { echo "harness-captures: NSGlassTintAmount is $GLASS" >&2; exit 1; }

echo "── 2x light, the thin and the thick caster ──"
npx tsx scripts/capture-web.ts photo__capsule-button__rest photo__rrect-lg__rest \
  --renderer webgpu --scale 2 --color-scheme light \
  --material-profile "$LIGHT" \
  --out "$OUT/apple-macos-27.0-2x-light-standard-glass0.5"

echo "── 2x dark, the same two ──"
npx tsx scripts/capture-web.ts photo__capsule-button__rest photo__rrect-lg__rest \
  --renderer webgpu --scale 2 --color-scheme dark \
  --material-profile "$DARK" \
  --out "$OUT/apple-macos-27.0-2x-dark-standard-glass0.5"

echo "── closing machine read ──"
echo "RT=$(defaults read com.apple.universalaccess reduceTransparency 2>/dev/null || echo 0)" \
     "IC=$(defaults read com.apple.universalaccess increaseContrast 2>/dev/null || echo 0)" \
     "NSGlassTintAmount=$(defaults read -g NSGlassTintAmount 2>/dev/null || echo absent)"
