#!/usr/bin/env bash
#
# W29 G3 — the canonical read, at the sealed documents.
#
#   ./canonical-read.sh calibration,validation
#   ./canonical-read.sh holdout                  # once per frozen configuration
#
# Separate from `read.sh` for one reason: this one writes the committed evidence.
# It appends 27 rows to `results/matrix.json` beside the 26.5 rows and writes the
# canonical `web-captures/` tree, so it refuses to run at anything but the sealed
# documents — the hashes below are the ones `sealed-documents.txt` records, and a
# document whose bytes have moved since is not the document the ledger says was
# read.
#
# `--alpha` is not optional here even though it costs a third page load per scene:
# W20's declaration-conformance rows are asserted on EVERY texture-tier cell that
# carries a shape axis, so a 27 row captured without it is a gated cell with a
# gate that cannot read it.
#
# It reduces nothing and rewrites nothing: a 27 cell key has never existed in the
# matrix, so every row it writes is new (`upsertCellResult`), and the 26.5 rows
# are the file's own, untouched. The 26.5 bounds and floors keep running over them
# afterwards, which is what proves it.
set -euo pipefail
cd "$(dirname "$0")/../.."

SETS="${1:?usage: canonical-read.sh <fixture sets>}"
LIGHT=profiles/apple-macos-27.0-1x-light-standard-glass0.5.json
DARK=profiles/apple-macos-27.0-1x-dark-standard-glass0.5.json
LIGHT_SHA=fa872c683f3e98211cc8766dae9c9d89ea6691dee92fe2530b693ada54185ec2
DARK_SHA=96b36eedf1c425c17098465a6cffcdef38f19fff811d61abaaba10c8b020ead1

check() {
  local got
  got=$(shasum -a 256 "$1" | cut -d' ' -f1)
  [ "$got" = "$2" ] || { echo "canonical-read: $1 is $got, sealed at $2" >&2; exit 1; }
}
check "$LIGHT" "$LIGHT_SHA"
check "$DARK" "$DARK_SHA"

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
    *-dark-*) doc="$DARK" ;;
    *)        doc="$LIGHT" ;;
  esac
  for renderer in webgpu css; do
    echo "── $profile / $renderer / $doc / set $SETS ──"
    npx tsx cli/compare.ts \
      --profile "$profile" \
      --material-profile "$doc" \
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
