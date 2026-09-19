#!/usr/bin/env bash
#
# W29 G3 — one read of the 27 bed, per profile per tier, at a named pair of
# material profile documents.
#
#   ./read.sh <out-matrix> <light-document> <dark-document> [set] [profiles...]
#
# Every argument is a path relative to `packages/calibration`, which is also this
# script's working directory, because that is what `--out-matrix` resolves
# against. `set` defaults to `calibration,validation`; the profile list defaults
# to the five Decision Log 4 (a) declares bounds for.
#
# Three things it refuses rather than warns about, because each of them is a run
# whose numbers would be evidence of something other than what the run says:
#
#   - another capture process on the machine (X7: one at a time, and the GPU is
#     the shared resource),
#   - Reduce Transparency or Increase Contrast reading anything but 0, or the
#     appearance slider reading anything but the bed's 0.5 (the web side inherits
#     the machine's accessibility state and Playwright cannot emulate it away),
#   - an output path that is the canonical matrix or the canonical capture tree,
#     which `compare` itself refuses; this only makes the refusal early and loud.
#
# The machine's reads are printed into the log, per invocation, because the wave
# records them rather than assuming them.
set -euo pipefail
cd "$(dirname "$0")/../.."

OUT="${1:?usage: read.sh <out-matrix> <light-doc> <dark-doc> [set] [profiles...]}"
LIGHT_DOC="${2:?}"
DARK_DOC="${3:?}"
SETS="${4:-calibration,validation}"
shift 4 || shift $#

PROFILES=("$@")
if [ ${#PROFILES[@]} -eq 0 ]; then
  PROFILES=(
    apple-macos-27.0-1x-light-standard-glass0.5
    apple-macos-27.0-2x-light-standard-glass0.5
    apple-macos-27.0-1x-dark-standard-glass0.5
    apple-macos-27.0-2x-dark-standard-glass0.5
    apple-macos-27.0-1x-light-reduced-transparency-glass0.5
  )
fi

case "$OUT" in
  results/matrix.json) echo "read.sh: refusing to write the canonical matrix" >&2; exit 1 ;;
esac
: "${VITREA_WEB_CAPTURES:?read.sh: set VITREA_WEB_CAPTURES to a scratch tree}"

if pgrep -f 'compare.ts|sweep.ts|capture-web|VitreaReference|playwright' > /dev/null; then
  echo "read.sh: another capture process is running (X7)" >&2
  exit 1
fi

RT=$(defaults read com.apple.universalaccess reduceTransparency 2>/dev/null || echo 0)
IC=$(defaults read com.apple.universalaccess increaseContrast 2>/dev/null || echo 0)
GLASS=$(defaults read -g NSGlassTintAmount 2>/dev/null || echo absent)
echo "machine: $(sw_vers -productVersion)/$(sw_vers -buildVersion) RT=$RT IC=$IC NSGlassTintAmount=$GLASS"
[ "$RT" = "0" ] || { echo "read.sh: Reduce Transparency is $RT, must be 0" >&2; exit 1; }
[ "$IC" = "0" ] || { echo "read.sh: Increase Contrast is $IC, must be 0" >&2; exit 1; }
[ "$GLASS" = "0.5" ] || { echo "read.sh: NSGlassTintAmount is $GLASS, the bed is 0.5" >&2; exit 1; }

for profile in "${PROFILES[@]}"; do
  case "$profile" in
    *-dark-*) doc="$DARK_DOC" ;;
    *)        doc="$LIGHT_DOC" ;;
  esac
  for renderer in webgpu css; do
    echo "── $profile / $renderer / $doc ──"
    npx tsx cli/compare.ts \
      --profile "$profile" \
      --material-profile "$doc" \
      --renderer "$renderer" \
      --set "$SETS" \
      --out-matrix "$OUT" \
      --write-partial
  done
done

echo "── closing machine read ──"
echo "RT=$(defaults read com.apple.universalaccess reduceTransparency 2>/dev/null || echo 0)" \
     "IC=$(defaults read com.apple.universalaccess increaseContrast 2>/dev/null || echo 0)" \
     "NSGlassTintAmount=$(defaults read -g NSGlassTintAmount 2>/dev/null || echo absent)"
