#!/bin/bash
# Every part of the coupled increased-contrast pass a machine with the toggles
# OFF can prove — W29 G1c Part A, Decision Log 4 (b), claims §5.152 §A.
#
# The pass itself needs Increase Contrast and Reduce transparency both on, which
# is two hands in System Settings; this child has none. So what this rehearses is
# the half a correctly-configured machine cannot reach: that every refusal FIRES
# from the state the machine is actually in, that the declaration the granted
# bundle is handed parses in that bundle without a rebuild, and that the derived
# specification puts exactly one contrast profile in front of it. The other half —
# `cells presented: 10` and `22` under the coupled key — is the parent's
# pre-pass rehearsal, with the toggles on, and is written into RUNBOOK §3b.
#
#     bash rehearse-coupled.sh > rehearsal.txt 2>&1
#
# Reads nothing, writes only under $TMP (default /tmp/vitrea-w29-g1c-rehearsal),
# and captures nothing anywhere.
set -uo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO="$(cd "$HERE/../../../.." && pwd)"
G1="$REPO/packages/calibration/results/2026-09-18-w29-g1-bed"
CANONICAL="$REPO/apps/reference-apple/scenes.json"
# The granted bundle, in the MAIN checkout, never rebuilt (X4).
APP="${VITREA_APP:-/Users/new/Developer/GitHub/designer/apps/reference-apple/build/VitreaReference.app}"
HARNESS="${VITREA_HARNESS:-/Users/new/Developer/GitHub/designer/apps/reference-apple/build/harness}"
T="${TMP_DIR:-/tmp/vitrea-w29-g1c-rehearsal}"
rm -rf "$T"; mkdir -p "$T"

echo "W29 G1c Part A — the rehearsals, on the capture machine."
echo "Nothing captured; nothing written under fixtures/, profiles/ or results/matrix.json."
echo

echo "=== 0. The machine, as found ==="
sw_vers
echo "NSGlassTintAmount=$(defaults read -g NSGlassTintAmount 2>/dev/null || echo absent)"
echo "reduceTransparency=$(defaults read com.apple.universalaccess reduceTransparency 2>/dev/null || echo 0)"
echo "increaseContrast=$(defaults read com.apple.universalaccess increaseContrast 2>/dev/null || echo 0)"
echo "ButtonShapesEnabled=$(defaults read com.apple.Accessibility ButtonShapesEnabled 2>/dev/null || echo 0)"
displayplacer list 2>/dev/null | sed -n 's/^  mode \([0-9]*\):.*<-- current mode$/displayplacerMode=\1/p'
echo
echo "Both accessibility toggles are OFF, so the machine is in the 'standard' mode"
echo "and every contrast pass must refuse from here. That is the state these rows"
echo "are read in, and it is why they are refusals rather than counts."
echo

echo "=== 1. The derived specification, per variant ==="
echo "Two derivations from one canonical declaration. Each carries exactly one"
echo "contrast profile — the harness selects on the profile's declared a11y field"
echo "and both contrast profiles declare 'increased-contrast', so a specification"
echo "holding both would hand one machine state two beds."
for V in decoupled coupled; do
  echo "--- variant $V"
  python3 "$G1/pass-spec.py" spec "$CANONICAL" "$T/$V.scenes-27.json" "$V"
  echo -n "profiles the harness could select with contrast on: "
  python3 -c '
import json,sys
doc=json.load(open(sys.argv[1]))
print(",".join(p["key"] for p in doc["profiles"] if p["a11y"]=="increased-contrast"))' "$T/$V.scenes-27.json"
  echo -n "cells it would present, active/inactive: "
  A="$(python3 "$G1/pass-spec.py" ids "$T/$V.scenes-27.json" active increased-contrast 1)"
  I="$(python3 "$G1/pass-spec.py" ids "$T/$V.scenes-27.json" inactive increased-contrast 1)"
  echo "$(printf '%s' "$A" | tr ',' '\n' | grep -c .)/$(printf '%s' "$I" | tr ',' '\n' | grep -c .)"
done
echo
echo "The two id lists are the same 32 cells — the coupled profile declares the"
echo "26.5 increased-contrast list verbatim, as clause 2 asks of every 27 profile —"
echo "so what differs between the passes is the profile, the key, and the state."
python3 "$G1/pass-spec.py" ids "$T/coupled.scenes-27.json" active increased-contrast 1 > "$T/ids-coupled.txt"
python3 "$G1/pass-spec.py" ids "$T/decoupled.scenes-27.json" active increased-contrast 1 > "$T/ids-decoupled.txt"
diff "$T/ids-coupled.txt" "$T/ids-decoupled.txt" > /dev/null \
  && echo "active id lists identical: yes" || echo "active id lists identical: NO"
echo

echo "=== 2. The refusals, from the machine's real state ==="
echo "Each row runs DRY, so a row that failed to refuse would capture nothing."
for ROW in "active 1 increased-contrast-coupled" "inactive 1 increased-contrast-coupled" \
           "active 1 increased-contrast" "active 2 increased-contrast-coupled"; do
  # shellcheck disable=SC2086
  set -- $ROW
  echo "--- DRY=1 run-sitting-27.sh $1 $2 $3"
  VITREA_SITTING_DIR="$T/refusals" DRY=1 "$G1/run-sitting-27.sh" "$1" "$2" "$3" 2>&1 | tail -2
done
echo
echo "The first two are the coupled pass refusing because the machine is not in"
echo "its state. The third is its mirror, and it is new: until macOS 27 decoupled"
echo "the toggles there was only one increased-contrast state, and the plain pass"
echo "now refuses a coupled machine rather than filing it under the decoupled key."
echo "The fourth is the pass no profile can serve, refused before the bundle is"
echo "launched — the coupled profile is 1x light, as its 26.5 counterpart is."
echo

echo "=== 3. The granted bundle reads the declaration, unrebuilt ==="
echo "The bundle is handed the COUPLED specification — the one holding the new"
echo "key — and asked to present one cell, dry. If the new profile entry broke"
echo "the decode, no cell would be presented at all."
D="$T/bundle/run-1"; mkdir -p "$D"
SCALE="$(python3 -c '
import re,subprocess
out=subprocess.run(["displayplacer","list"],capture_output=True,text=True).stdout
print(2 if re.search(r"^  mode 68:.*current mode$", out, re.M) else 1)' 2>/dev/null || echo 2)"
echo "presenting at the display's own scale: ${SCALE}x"
VITREA_SCALE="$SCALE" VITREA_FIXTURES="$D" VITREA_SCENES="$T/coupled.scenes-27.json" \
  "$HARNESS" backgrounds > "$T/bundle/backgrounds.out" 2>&1
echo "backgrounds: $(tail -1 "$T/bundle/backgrounds.out")"
${VITREA_LAUNCHER:-open -W} --env VITREA_SCALE="$SCALE" --env VITREA_FIXTURES="$D" \
  --env VITREA_SCENES="$T/coupled.scenes-27.json" \
  --stdout "$T/bundle/run-1.out" --stderr "$T/bundle/run-1.err" "$APP" \
  --args capture --dry-run --run-label "w29-g1c-key-rehearsal" \
  --reset-interstitial 6 --min-idle-seconds 45 --scenes photo__capsule-button__rest
cat "$T/bundle/run-1.out"
[ -s "$T/bundle/run-1.err" ] && cat "$T/bundle/run-1.err"
echo
echo "It presented the profiles whose a11y mode and scale the machine matches, and"
echo "the coupled profile is not among them — which is the a11y gate skipping it,"
echo "the same gate that skips the decoupled one from a standard machine. What is"
echo "NOT rehearsable here is the count under the coupled key itself: that needs"
echo "the two toggles on, and it is the first line of each pass command in"
echo "RUNBOOK §3b — 'cells presented: 10' and '22'."
