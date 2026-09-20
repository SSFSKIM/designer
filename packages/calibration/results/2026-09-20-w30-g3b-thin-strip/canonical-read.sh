#!/usr/bin/env bash
#
# W30 G3b — the canonical read, at the four documents this child COMMENTED.
#
#   ./canonical-read.sh calibration,validation     # six profiles, two tiers
#   ./canonical-read.sh ladder                     # the pitch ladder, as probe rows
#   ./canonical-read.sh holdout                    # once per frozen configuration
#
# W30 G3's `results/2026-09-20-w30-g3-operators/canonical-read.sh`, copied rather
# than reused, on that file's own rule: it hard-codes the hashes IT sealed and
# refuses any other bytes, and nothing under `results/` is edited after commit.
# The refusal, the `pgrep` exclusivity check, the three machine reads, the
# profile list and the 45-scene ladder are verbatim; the four hashes are this
# child's, filled from `comment-generation.txt` and never by hand.
#
# **The material did not move and the read is a new generation anyway** (charter
# Decision Log 5 (b)). W30 G3 fitted the σ law at a renderer that returned NaN
# more than 10.06 σ inside a thin caster's shadow silhouette, which left a strip
# of every span-44 surface undrawn (claims §5.159 §6, fixed in §5.159b). A fix in
# the shader moves no document, so a re-read would key to the cells G3's read
# wrote and overwrite recorded numbers. Each of the four documents therefore
# carries a dated `$comment-w30-g3b` naming the defect, the claims section and
# the commit that fixed it: a true statement about the conditions the rows beside
# it were read under, which moves the file hash and — asserted by
# `comment-generation.ts` before and after — does NOT move
# `resolvedMaterialSha256`. G3's rows move to `results/superseded/` by G1's
# script once these have landed.
#
# `--alpha` is not optional, for W29 G3's reason: W20's declaration-conformance
# rows are asserted on every texture-tier cell carrying a shape axis, so a row
# captured without it is a gated cell with a gate that cannot read it. It is
# this gate's own instrument besides — the strip was an alpha-0 region inside a
# declared silhouette.
#
# It reduces nothing and rewrites nothing. Every row it writes is new — no cell
# key in the matrix has ever carried these document hashes.
set -euo pipefail
cd "$(dirname "$0")/../.."

MODE="${1:?usage: canonical-read.sh <fixture sets|ladder>}"
LIGHT=profiles/apple-macos-27.0-1x-light-standard-glass0.5.json
DARK=profiles/apple-macos-27.0-1x-dark-standard-glass0.5.json
LIGHT_RECEDED=profiles/apple-macos-27.0-1x-light-standard-glass0.5-receded.json
DARK_RECEDED=profiles/apple-macos-27.0-1x-dark-standard-glass0.5-receded.json

# Filled from `comment-generation.txt` after that script runs, and never by hand.
LIGHT_SHA=d0c389d7045670ec82d609f81917d4eb8945f7e2b18c2c41c71b277c4f5ef10a
DARK_SHA=880ab1e31450767c50f471ccc96e9818bbbf15a73e797cefc06f0dedc7097876
LIGHT_RECEDED_SHA=2334c7b4c5e2c83e67cdaa4823c3cce95087054b26713d4cf0bbc649a9c62ef9
DARK_RECEDED_SHA=5e71370ae6d506501ef18469390de61aadb0fcd337d4550e90a6411cb7eb0437

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

# The 45 pitch-ladder scenes, every one of them declared `probe` in
# `apps/reference-apple/scenes.json` — the seven ladder backdrops' whole scene
# set, named here so the selection is legible and so `--set probe` cannot widen
# to the other 91 probe rows the bed carries.
LADDER="checkerboard-4__capsule-button__rest,checkerboard-4__capsule-button__rest-tint-orange,checkerboard-4__rrect-lg__rest,checkerboard-4__rrect-md__inactive,checkerboard-4__rrect-md__rest,checkerboard-4__rrect-ml__rest,checkerboard-4__rrect-sm__rest,checkerboard-8__capsule-button__rest,checkerboard-8__capsule-button__rest-tint-orange,checkerboard-8__rrect-lg__inactive,checkerboard-8__rrect-lg__rest,checkerboard-8__rrect-md__inactive,checkerboard-8__rrect-md__rest,checkerboard-8__rrect-ml__rest,checkerboard-8__rrect-sm__rest,checkerboard-32__capsule-button__rest,checkerboard-32__capsule-button__rest-tint-orange,checkerboard-32__rrect-lg__inactive,checkerboard-32__rrect-lg__rest,checkerboard-32__rrect-md__rest,checkerboard-32__rrect-ml__rest,checkerboard-32__rrect-sm__rest,checkerboard-64__capsule-button__rest,checkerboard-64__capsule-button__rest-tint-orange,checkerboard-64__rrect-lg__inactive,checkerboard-64__rrect-lg__rest,checkerboard-64__rrect-md__inactive,checkerboard-64__rrect-md__rest,checkerboard-64__rrect-ml__rest,checkerboard-64__rrect-sm__rest,checkerboard-lc16__capsule-button__inactive,checkerboard-lc16__capsule-button__rest,checkerboard-lc16__rrect-lg__rest,checkerboard-lc16__rrect-md__inactive,checkerboard-lc16__rrect-md__rest,checkerboard-lc16__rrect-ml__rest,checkerboard-lc16__rrect-sm__rest,hc-text-7__rrect-lg__rest,hc-text-7__rrect-md__inactive,hc-text-7__rrect-md__rest,hc-text-7__rrect-sm__rest,hc-text-28__rrect-lg__rest,hc-text-28__rrect-md__inactive,hc-text-28__rrect-md__rest,hc-text-28__rrect-sm__rest"

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
  # ones, so B4's recorded CSS residual is committed evidence too.
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
