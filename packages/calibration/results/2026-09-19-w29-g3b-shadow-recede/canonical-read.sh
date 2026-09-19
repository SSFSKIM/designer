#!/usr/bin/env bash
#
# W29 G3b — the canonical read, at the four sealed documents.
#
#   ./canonical-read.sh calibration,validation
#   ./canonical-read.sh holdout                  # once per frozen configuration
#
# G3's `canonical-read.sh` with the receded pair added, and it refuses at any
# bytes but the four `sealed-documents.txt` records. A document change re-keys
# every row it drew. The material profile document's hash is in the cell's
# `capturePath`, and since this child the receded document's is there too, so
# "the sealed configuration" is four files and the refusal names all four.
#
# **Every 27 profile is re-read**, not only the ones whose documents moved. The
# active documents' `outerShadow` block moved (Decision Log 6 (a)) and every
# profile resolves one of them, so every active row re-keys; the inactive rows
# re-key twice over, once for that and once for the candidate receded document
# they are now posed with. Decision Log 6 (a) says this in the ruling: "the
# documents are re-sealed and every 27 profile is re-read once under the new
# hashes, because a document change re-keys every row."
#
# `--alpha` is not optional, for G3's reason: W20's declaration-conformance rows
# are asserted on every texture-tier cell carrying a shape axis, so a row
# captured without it is a gated cell with a gate that cannot read it.
#
# It reduces nothing and rewrites nothing. Every row it writes is new — no cell
# key in the matrix has ever carried these document hashes — so `upsertCellResult`
# appends beside the 26.5 rows and beside G3's 27 rows, all of which stay exactly
# as they are. The 26.5 bounds and floors keep running over their own rows
# afterwards, which is what proves it.
set -euo pipefail
cd "$(dirname "$0")/../.."

SETS="${1:?usage: canonical-read.sh <fixture sets>}"
LIGHT=profiles/apple-macos-27.0-1x-light-standard-glass0.5.json
DARK=profiles/apple-macos-27.0-1x-dark-standard-glass0.5.json
LIGHT_RECEDED=profiles/apple-macos-27.0-1x-light-standard-glass0.5-receded.json
DARK_RECEDED=profiles/apple-macos-27.0-1x-dark-standard-glass0.5-receded.json

# Filled from `sealed-documents.txt` after `seal.ts` runs, and never by hand.
LIGHT_SHA=f42ddec1cf5a9544c39d1aa81ac78fbb3dac5815a634db7de597fc280c2b01c5
DARK_SHA=272d1b0c3e102adae85205b2bbc818d254983b3008579198b2fa28953dcae335
LIGHT_RECEDED_SHA=59d4b20a459669ccdb2577f87c49075dce38dfb4e1bcf640a2b54dd01e61b30f
DARK_RECEDED_SHA=5c81bc72edad101a5ea86d74e60b27c2b309410e25a50c4850e9078a967c66b9

check() {
  local got
  got=$(shasum -a 256 "$1" | cut -d' ' -f1)
  [ "$got" = "$2" ] || { echo "canonical-read: $1 is $got, sealed at $2" >&2; exit 1; }
}
check "$LIGHT" "$LIGHT_SHA"
check "$DARK" "$DARK_SHA"
check "$LIGHT_RECEDED" "$LIGHT_RECEDED_SHA"
check "$DARK_RECEDED" "$DARK_RECEDED_SHA"

if pgrep -f 'compare.ts|sweep.ts|capture-web|VitreaReference|playwright' > /dev/null; then
  echo "canonical-read: another capture process is running (X7)" >&2
  exit 1
fi
RT=$(defaults read com.apple.universalaccess reduceTransparency 2>/dev/null || echo 0)
IC=$(defaults read com.apple.universalaccess increaseContrast 2>/dev/null || echo 0)
GLASS=$(defaults read -g NSGlassTintAmount 2>/dev/null || echo absent)
echo "machine: $(sw_vers -productVersion)/$(sw_vers -buildVersion) RT=$RT IC=$IC NSGlassTintAmount=$GLASS"
echo "display: $(displayplacer list 2>/dev/null | grep -c 'current mode') current mode(s); mode 68 expected"
[ "$RT" = "0" ] || { echo "canonical-read: Reduce Transparency is $RT" >&2; exit 1; }
[ "$IC" = "0" ] || { echo "canonical-read: Increase Contrast is $IC" >&2; exit 1; }
[ "$GLASS" = "0.5" ] || { echo "canonical-read: NSGlassTintAmount is $GLASS" >&2; exit 1; }

PROFILES=(
  apple-macos-27.0-1x-light-standard-glass0.5
  apple-macos-27.0-2x-light-standard-glass0.5
  apple-macos-27.0-1x-dark-standard-glass0.5
  apple-macos-27.0-2x-dark-standard-glass0.5
  apple-macos-27.0-1x-light-reduced-transparency-glass0.5
  apple-macos-27.0-1x-light-increased-contrast-coupled-glass0.5
)

for profile in "${PROFILES[@]}"; do
  case "$profile" in
    *-dark-*) doc="$DARK"; receded="$DARK_RECEDED" ;;
    *)        doc="$LIGHT"; receded="$LIGHT_RECEDED" ;;
  esac
  for renderer in webgpu css; do
    echo "── $profile / $renderer / $doc + $receded / set $SETS ──"
    npx tsx cli/compare.ts \
      --profile "$profile" \
      --material-profile "$doc" \
      --receded-profile "$receded" \
      --renderer "$renderer" \
      --set "$SETS" \
      --alpha \
      --write-partial
  done
done

echo "── closing machine read ──"
echo "RT=$(defaults read com.apple.universalaccess reduceTransparency 2>/dev/null || echo 0)" \
     "IC=$(defaults read com.apple.universalaccess increaseContrast 2>/dev/null || echo 0)" \
     "NSGlassTintAmount=$(defaults read -g NSGlassTintAmount 2>/dev/null || echo absent)"
