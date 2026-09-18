#!/bin/bash
# The harness half of the SDK-gating pixel arm — W29 Decision Log 3 (c), claims §5.150.
#
# G0 settled SDK gating on the DECLARED material: two bundles from one toolchain
# and one source revision, recording `sdk 26.5` and `sdk 27.0`, declare a
# byte-identical Core Animation filter tree on 9 of 9 cells, and the granted
# bundle — which records the oldest value of the three — agrees on 8 of 9
# (`sdk-gating.json`). It could not settle it on PIXELS, because the window
# server composites from that tree and could in principle read the requesting
# binary's own linked SDK, and the side bundle had no Screen Recording grant.
#
# Decision Log 3 (c) gave it one: the user added the 27-SDK side bundle by path,
# which — as X4 now records with a sharper reason — EVICTED the granted harness
# bundle's entry, because TCC keeps one row per bundle identifier and the last
# code hash added owns it. The parent used that window to capture the side
# bundle's half at slider 0.5 (three active runs of four ids in two schemes,
# `~/vitrea-w29-g0-scratch/sdk-pixel/side-sdk27/active-r{1,2,3}`), and the grant
# was then moved back.
#
# This is the other half, with the granted bundle. Everything except the bundle
# is held identical to the side arm, deliberately: the same four ids, the same two
# schemes, the same 2x scale, the same slider position, the same
# `--reset-interstitial 6`, three runs, and **the main checkout's scenes.json**
# rather than this worktree's amended one — the side arm ran against version 5,
# which declares the six 26.5 keys and not the six 27 ones, so running against
# version 6 here would add eight cells under 27 keys that the other arm has no
# counterpart for and would change two things at once.
#
# The bar is each arm's own three-run spread. A difference between the bundles
# means nothing until the same cell's difference from itself is on the page beside
# it, which is the construction G0's slider probe used and G2's noise bar will use.
set -euo pipefail

MAIN=/Users/new/Developer/GitHub/designer
APP="$MAIN/apps/reference-apple/build/VitreaReference.app"
H="$MAIN/apps/reference-apple/build/harness"
SPEC="$MAIN/apps/reference-apple/scenes.json"
OUT="$HOME/vitrea-w29-g0-scratch/sdk-pixel/harness"
IDS="checkerboard__capsule-button__rest,dark-solid__rrect-80__rest,hc-text__rrect-sm__rest,photo__rrect-md__rest"

# One capture process at a time; the GPU is shared (X7).
pgrep -f 'compare.ts|sweep.ts|capture-web|VitreaReference|playwright' >/dev/null \
  && { echo "REFUSED: a capture process is already running." >&2; exit 7; }

# The bed's slider position, and the three accessibility axes, read before the
# arm rather than assumed. The same refusals `run-sitting-27.sh` applies.
[ "$(defaults read -g NSGlassTintAmount)" = "0.5" ] || { echo "REFUSED: slider is not 0.5" >&2; exit 1; }
[ "$(defaults read com.apple.universalaccess reduceTransparency)" = "0" ] || { echo "REFUSED: RT" >&2; exit 1; }
[ "$(defaults read com.apple.universalaccess increaseContrast)" = "0" ] || { echo "REFUSED: IC" >&2; exit 1; }
[ "$(defaults read com.apple.Accessibility ButtonShapesEnabled)" = "0" ] || { echo "REFUSED: Show Borders" >&2; exit 1; }
[ "$(sw_vers -productVersion)" = "27.0" ] || { echo "REFUSED: not macOS 27.0" >&2; exit 1; }

mkdir -p "$OUT"
for R in 1 2 3; do
  D="$OUT/active-r$R"; rm -rf "$D"; mkdir -p "$D"
  { echo "slider=$(defaults read -g NSGlassTintAmount)"
    echo "reduceTransparency=$(defaults read com.apple.universalaccess reduceTransparency)"
    echo "increaseContrast=$(defaults read com.apple.universalaccess increaseContrast)"
    echo "showBorders=$(defaults read com.apple.Accessibility ButtonShapesEnabled)"
    echo "os=$(sw_vers -productVersion) $(sw_vers -buildVersion)"
  } > "$D/attest.read"
  VITREA_SCALE=2 VITREA_FIXTURES="$D" VITREA_SCENES="$SPEC" "$H" backgrounds > "$D.backgrounds.out" 2>&1
  S=$(date -u +%s)
  open -W --env VITREA_SCALE=2 --env VITREA_FIXTURES="$D" --env VITREA_SCENES="$SPEC" \
    --stdout "$D.out" --stderr "$D.err" "$APP" \
    --args capture --run-label "w29-g1-sdk-pixel-harness-active-r$R" \
    --reset-interstitial 6 --scenes "$IDS"
  E=$(date -u +%s)
  [ -f "$D/manifest.json" ] || { echo "active r$R FAILED"; tail -4 "$D.err"; exit 3; }
  echo "active r$R ok $((E - S))s fixtures=$(find "$D" -name '*.png' -path '*apple-macos*' | wc -l | tr -d ' ')"
done
echo DONE
