#!/usr/bin/env bash
#
# W30 G3 — the canonical read, at the four documents this child sealed.
#
#   ./canonical-read.sh calibration,validation     # six profiles, two tiers
#   ./canonical-read.sh ladder                     # the pitch ladder, as probe rows
#   ./canonical-read.sh holdout                    # once per frozen configuration
#
# W29 G3b's `results/2026-09-19-w29-g3b-shadow-recede/canonical-read.sh`, copied
# rather than reused: that file hard-codes the hashes IT sealed and refuses any
# other bytes, and nothing under `results/` is edited after commit. The refusal,
# the `pgrep` exclusivity check and the three machine reads are verbatim; the
# four hashes are this child's, filled from `sealed-documents.txt` after
# `seal.ts` runs and never by hand.
#
# **Every 27 profile is re-read**, not only the ones whose documents moved. All
# four documents move here — the two active ones carry the σ law and the refitted
# anchors, the two receded ones inherit the anchors leaf for leaf — so every
# active row re-keys and every inactive row re-keys twice over. A document change
# re-keys every row it drew.
#
# **The ladder pass is this child's addition** (charter Decision Log 2 (a)). The
# macOS 27 generation of `results/matrix.json` carries no probe row at all
# (claims §5.156 §3), so the pitch ladder — the only evidence that can identify a
# scale-selective scatter, and the only macOS 27 web reading at span 160 outside
# three holdout cells — has never been committed at a macOS 27 document. The
# ruling grants the 45 ladder scenes on the WebGPU tier for the four standard
# profiles and on the CSS tier for the two 1x standard ones, and NOT the whole
# probe set (about 180 rows per profile-tier, which would put the working file
# within reach of GitHub's refusal for no gated benefit). `--set probe` with an
# explicit `--scene` list is how that selection is made: `compare` intersects the
# two filters, so the pair names exactly the ladder's own probe rows and they are
# written with `fixtureSet: "probe"`, which is what the gate drops as it drops
# every probe row.
#
# `--alpha` is not optional, for W29 G3's reason: W20's declaration-conformance
# rows are asserted on every texture-tier cell carrying a shape axis, so a row
# captured without it is a gated cell with a gate that cannot read it.
#
# It reduces nothing and rewrites nothing. Every row it writes is new — no cell
# key in the matrix has ever carried these document hashes — so `upsertCellResult`
# appends beside the 26.5 rows and beside W29 G3b's 27 rows, all of which stay
# exactly as they are.
set -euo pipefail
cd "$(dirname "$0")/../.."

MODE="${1:?usage: canonical-read.sh <fixture sets|ladder>}"
LIGHT=profiles/apple-macos-27.0-1x-light-standard-glass0.5.json
DARK=profiles/apple-macos-27.0-1x-dark-standard-glass0.5.json
LIGHT_RECEDED=profiles/apple-macos-27.0-1x-light-standard-glass0.5-receded.json
DARK_RECEDED=profiles/apple-macos-27.0-1x-dark-standard-glass0.5-receded.json

# Filled from `sealed-documents.txt` after `seal.ts` runs, and never by hand.
LIGHT_SHA=d731b38389943e4e3cbec1fb787f40f265642a5ea18681270843eb5f97902bf5
DARK_SHA=ce1af58886ff5fcff16084fc7332de446804f446acb2975a3a9f48fccda9c0e8
LIGHT_RECEDED_SHA=b4a5914c7b9c424bb82046a19515ba981b77053b7affca6f10523e0a034c119f
DARK_RECEDED_SHA=d449ea0649f47e4b83c9a6f592df21561b11fd660070f6fa629f885fb654bc52

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
