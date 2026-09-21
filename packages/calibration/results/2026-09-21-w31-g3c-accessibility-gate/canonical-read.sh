#!/usr/bin/env bash
#
# W31 G3c — the canonical read, at the two LIGHT documents this gate MOVED.
#
#   ./canonical-read.sh calibration,validation     # four light profiles, two tiers
#   ./canonical-read.sh ladder                     # the pitch ladder, as probe rows
#   ./canonical-read.sh holdout                    # once per frozen configuration
#
# `results/2026-09-21-w31-g3-chroma-fit/canonical-read.sh`, COPIED rather than
# reused on that file's own rule: it hard-codes the hashes IT read and refuses
# any other bytes, and nothing under `results/` is edited after commit. The
# refusal, the exclusivity check, the three machine reads and the 45-scene ladder
# are verbatim; the four hashes are this gate's, filled from
# `comment-generation.txt` and never by hand.
#
# **FOUR profiles and not six.** W31 G3c moves the two LIGHT documents' bytes
# (`comment-generation.ts`) and leaves the dark pair alone, so only the four
# profiles those light documents serve fall out of their bounds and only they
# are re-read: 1x and 2x light standard, reduced transparency, and increased
# contrast coupled. The dark pair's hashes are checked here anyway — a read that
# did not touch them should be able to say so.
#
# **The ladder, where the profile carries it.** G3's read took the 45 ladder
# scenes on WebGPU at 1x and 2x light and on the CSS tier at 1x light, and gave
# the two accessibility profiles none: they declare 5 of the 45 and every one of
# those is `probe`, which the accessibility beds do not gate. This read
# reproduces that selection exactly, because a generation that is not row for
# row the generation it supersedes is not a re-read.
#
# **The holdout is read ONCE, after `configuration.py record`** (Decision Log
# 1 (b) as clause 6 enforces it), with `--source-moved-because` naming the
# non-fit reason: the renderer moved and no fitted constant did. The record is
# `results/2026-09-21-w31-g3c-accessibility-gate/configuration.txt` and the
# refusal it would have raised at unmoved sources is `configuration-refusal.txt`.
#
# `--alpha` is not optional, for W29 G3's reason: W20's declaration-conformance
# rows are asserted on every texture-tier cell carrying a shape axis, so a row
# captured without it is a gated cell with a gate that cannot read it.
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
# The two light hashes MOVED at this gate and the two dark ones did not.
LIGHT_SHA=49490eb9ff7acf823430c41c1d0cf6d55cea23cc0e1a36bff3246f66e3fbfbde
DARK_SHA=b5714a8662880ff7a70fbfa51a2fa14e3098f11889fcec30edfac6450322bf06
LIGHT_RECEDED_SHA=14c6bacf2eda44c1971c09ee45c59cbbc5e7c8f8b407b7abb17e7afd321bdcdc
DARK_RECEDED_SHA=cc4ed1038996c0b1b0b51eb0bdf07fae637c004cc671aa5069336fbfdf27013e

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
  # WebGPU on the two light STANDARD profiles and the CSS tier on the 1x one —
  # G3's selection with its two dark runs dropped, because the dark documents
  # did not move. The two accessibility profiles get none, exactly as in G3.
  for profile in "${PROFILES[@]:0:2}"; do
    run "$profile" webgpu "$LIGHT" "$LIGHT_RECEDED" --set probe --scene "$LADDER"
  done
  run "${PROFILES[0]}" css "$LIGHT" "$LIGHT_RECEDED" --set probe --scene "$LADDER"
else
  for profile in "${PROFILES[@]}"; do
    for renderer in webgpu css; do
      run "$profile" "$renderer" "$LIGHT" "$LIGHT_RECEDED" --set "$MODE"
    done
  done
fi

echo "── closing machine read ──"
echo "RT=$(defaults read com.apple.universalaccess reduceTransparency 2>/dev/null || echo 0)" \
     "IC=$(defaults read com.apple.universalaccess increaseContrast 2>/dev/null || echo 0)" \
     "NSGlassTintAmount=$(defaults read -g NSGlassTintAmount 2>/dev/null || echo absent)"
