#!/usr/bin/env bash
#
# W32 G1 — the canonical read, at the four documents this child SEALED.
#
#   ./canonical-read.sh calibration,validation     # six profiles, two tiers
#   ./canonical-read.sh ladder                     # the widened ladder, as probe rows
#   ./canonical-read.sh holdout                    # once per frozen configuration
#
# W31 G3's `results/2026-09-21-w31-g3-chroma-fit/canonical-read.sh`, copied
# rather than reused on that file's own rule: it hard-codes the hashes IT sealed
# and refuses any other bytes, and nothing under `results/` is edited after
# commit. The refusal, the exclusivity check, the three machine reads and the
# profile list are verbatim; the four hashes are this child's, filled from
# `sealed-documents.txt` and never by hand, and the ladder is **sourced from
# `ladder.sh`** rather than inlined — the rounds and the read must name the same
# set or the material the fit converged on is not the material the rows describe.
#
# **Why there is a read at all, and why it is in this branch.** The four macOS 27
# documents move here — the two lengths, the σ law, the seven active amplitudes
# and the receded documents' stand-down to zero — and `SHIPPED_DOCUMENT_HASHES`
# is built from their bytes, so every one of the 726 macOS 27 rows falls out of
# every bound the moment they do (X10). The seal and the read are one merge, and
# this is the read.
#
# **The holdout is read ONCE, after `configuration.py record`** at the cross-gate
# location W32 G0b gave it (`results/holdout-configuration/`). That script prints
# the four document hashes and a hash over the enumerated renderer sources,
# refuses a second read at document hashes any record already carries without a
# named non-fit reason, and appends to a committed log. Run it before the holdout
# mode below; its output is in the ledger.
#
# `--alpha` is not optional, for W29 G3's reason: W20's declaration-conformance
# rows are asserted on every texture-tier cell carrying a shape axis, so a row
# captured without it is a gated cell with a gate that cannot read it.
#
# It reduces nothing and rewrites nothing. Every row it writes is new — no cell
# key in the matrix has ever carried these document hashes.
set -euo pipefail
cd "$(dirname "$0")/../.."

HERE=results/2026-09-21-w32-g1-shadow-fit
MODE="${1:?usage: canonical-read.sh <fixture sets|ladder>}"
LIGHT=profiles/apple-macos-27.0-1x-light-standard-glass0.5.json
DARK=profiles/apple-macos-27.0-1x-dark-standard-glass0.5.json
LIGHT_RECEDED=profiles/apple-macos-27.0-1x-light-standard-glass0.5-receded.json
DARK_RECEDED=profiles/apple-macos-27.0-1x-dark-standard-glass0.5-receded.json

# Filled from `sealed-documents.txt` after `seal.ts` runs, and never by hand.
LIGHT_SHA=d5bdd6eac4323e2912d46d8d78a8f2d20f428a66f4eaac397c5e4c92413b42cf
DARK_SHA=431cabd391c4320e67e5977489c6b5d6e282f470e2b2e01d3906f9d2f0de9345
LIGHT_RECEDED_SHA=45acb6d916b9a37977f0b667d15e8e740b12c2d68485734ea8b324ad7f30c179
DARK_RECEDED_SHA=4e68f81869f6328c9f995be042cca593fdf91f25a8b22ac9c27f38b110f68656

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
  echo "canonical-read: another capture process is running (X6)" >&2
  exit 1
fi
RT=$(defaults read com.apple.universalaccess reduceTransparency 2>/dev/null || echo 0)
IC=$(defaults read com.apple.universalaccess increaseContrast 2>/dev/null || echo 0)
GLASS=$(defaults read -g NSGlassTintAmount 2>/dev/null || echo absent)
echo "machine: $(sw_vers -productVersion)/$(sw_vers -buildVersion) RT=$RT IC=$IC NSGlassTintAmount=$GLASS"
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

# shellcheck source=ladder.sh
. "$HERE/ladder.sh"

run() {
  local profile="$1" renderer="$2" doc="$3" receded="$4"
  shift 4
  echo "── $profile / $renderer / $doc + $receded / $* ──"
  npx tsx cli/compare.ts \
    --profile "$profile" \
    --material-profile "$doc" \
    --receded-profile "$receded" \
    --renderer "$renderer" \
    --alpha \
    --write-partial \
    "$@"
}

if [ "$MODE" = "ladder" ]; then
  # WebGPU on the four standard profiles; the CSS tier on the two 1x standard
  # ones, so the recorded CSS residual is committed evidence too.
  for profile in "${PROFILES[@]:0:4}"; do
    case "$profile" in
      *-dark-*) doc="$DARK"; receded="$DARK_RECEDED" ;;
      *)        doc="$LIGHT"; receded="$LIGHT_RECEDED" ;;
    esac
    run "$profile" webgpu "$doc" "$receded" --set probe --scene "$LADDER"
  done
  run "${PROFILES[0]}" css "$LIGHT" "$LIGHT_RECEDED" --set probe --scene "$LADDER"
  run "${PROFILES[2]}" css "$DARK" "$DARK_RECEDED" --set probe --scene "$LADDER"
else
  for profile in "${PROFILES[@]}"; do
    case "$profile" in
      *-dark-*) doc="$DARK"; receded="$DARK_RECEDED" ;;
      *)        doc="$LIGHT"; receded="$LIGHT_RECEDED" ;;
    esac
    for renderer in webgpu css; do
      run "$profile" "$renderer" "$doc" "$receded" --set "$MODE"
    done
  done
fi

echo "── closing machine read ──"
echo "RT=$(defaults read com.apple.universalaccess reduceTransparency 2>/dev/null || echo 0)" \
     "IC=$(defaults read com.apple.universalaccess increaseContrast 2>/dev/null || echo 0)" \
     "NSGlassTintAmount=$(defaults read -g NSGlassTintAmount 2>/dev/null || echo absent)"
