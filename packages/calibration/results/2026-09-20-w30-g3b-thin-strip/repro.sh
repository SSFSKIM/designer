#!/usr/bin/env bash
#
# W30 G3b — the reproduction, and the three controls that say what it is a
# function of (claims §5.159b; the finding is §5.159 §6).
#
#   ./repro.sh <scratch dir>
#
# Four one-scene captures of `checkerboard__capsule-button__rest` on the macOS 27
# light bed, each with a document built from **0.19.0's own** macOS 27 light
# document — `git show <0.19.0>:packages/calibration/profiles/…` — so no constant
# this wave fitted is involved:
#
#   s11     0.19.0 unchanged: σ 11. Draws clean.
#   s8      0.19.0 with `sigmaPx: 8` and nothing else, which is §5.159 §6's own
#           reproduction line. It reproduces — but the three σ-law leaves come
#           from the RUNTIME material the profileKey selects, not from the
#           document, so the σ actually drawn is 8 − 6.8328 = 1.1672.
#   flat8   the same with the three law leaves written to 0: σ 8 flat. CLEAN,
#           which is what makes the defect a function of σ and of nothing else.
#   flat213 the same at `sigmaPx: 2.13`: σ 2.13 flat. Reproduces.
#
# Run it once on the pre-fix renderer and once on the fixed one; `flat213` goes
# from 4220/4872 (IoU 0.8662) to 4872/4872 (IoU 1.0000) and the other three do
# not move.
set -euo pipefail
cd "$(dirname "$0")/../.."

SCRATCH="${1:?usage: repro.sh <scratch dir>}"
mkdir -p "$SCRATCH"

if pgrep -f 'compare.ts|sweep.ts|capture-web|VitreaReference|playwright' > /dev/null; then
  echo "repro: another capture process is running (X6)" >&2
  exit 1
fi
echo "machine: $(sw_vers -productVersion) RT=$(defaults read com.apple.universalaccess reduceTransparency 2>/dev/null || echo 0)" \
     "IC=$(defaults read com.apple.universalaccess increaseContrast 2>/dev/null || echo 0)" \
     "NSGlassTintAmount=$(defaults read -g NSGlassTintAmount 2>/dev/null || echo absent)"

for tag in s11 s8 flat8 flat213; do
  doc="$SCRATCH/docs-$tag/apple-macos-27.0-1x-light-standard-glass0.5.json"
  [ -f "$doc" ] || { echo "repro: $doc is missing — see the header for how each is built" >&2; exit 1; }
  echo "── $tag ──"
  VITREA_WEB_CAPTURES="$SCRATCH/cap-$tag" npx tsx cli/compare.ts \
    --profile apple-macos-27.0-1x-light-standard-glass0.5 \
    --material-profile "$doc" \
    --receded-profile "$SCRATCH/docs-$tag/apple-macos-27.0-1x-light-standard-glass0.5-receded.json" \
    --renderer webgpu --set calibration --scene checkerboard__capsule-button__rest \
    --alpha --write-partial --out-matrix "$SCRATCH/m-$tag.json"
done
