#!/bin/bash
# dump-one.sh <out-root> <label> <scale 1|2> <scheme light|dark> <pose active|inactive> <settle> <ids-csv>
#
# One `dump-layers` launch of the W39 side bundle over the W42 bed (scenes-w42-body.json), for
# G0's s = 112 acceptance check (charter "The bed", H; the parent's call on v2). Derived from
# memo D's run-one.sh (~/vitrea-w42/grounding/dumps/, not edited): the same launch, the same
# opening/closing attestation and gate (slider 0.5, Reduce Transparency, Increase Contrast and
# Show Borders 0, the display mode, the binary pin), plus the X6 foreign-process census
# RECORDED at both ends. A dump captures no pixel and needs no grant; the caller waits for
# HID idle first with memo D's gate.sh. The pose is attested inside every dump and checked by
# dumpcheck.py. No write goes under memo D's scratch or the repository.
set -uo pipefail
OUT=$1; LABEL=$2; SCALE=$3; SCHEME=$4; POSE=$5; SETTLE=$6; IDS=$7
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
APP=/Users/new/vitrea-w39/side/VitreaReference.app
PIN=02052b175dd14bfbe2713d8e566c9b650011000f8f72de87a965f070c38b6498
SPEC="$(cd "$HERE/.." && pwd)/scenes-w42-body.json"
FOREIGN='Chromium|playwright|compare\.ts|capture-web|VitreaReference|Google Chrome|Chrome Helper|Playwright|headless[-_ ]shell'
case "$OUT" in /Users/new/Developer/*|/Users/new/vitrea-w42/grounding*|/Users/new/vitrea-w42/g0-*/packages*)
  echo "REFUSE: output root $OUT is inside a checkout or memo D's scratch"; exit 2;; esac
D=$OUT/$LABEL
[ -e "$D" ] && { echo "REFUSE: $D exists"; exit 2; }
mkdir -p "$D" "$OUT/.fixtures"
WANTMODE=$([ "$SCALE" = 2 ] && echo 68 || echo 69)
attest() {
  { echo "phase=$1"; echo "at=$(date -u +%FT%TZ)"; echo "slider=$(defaults read -g NSGlassTintAmount)";
    echo "reduceTransparency=$(defaults read com.apple.universalaccess reduceTransparency)";
    echo "increaseContrast=$(defaults read com.apple.universalaccess increaseContrast)";
    echo "showBorders=$(defaults read com.apple.Accessibility ButtonShapesEnabled)";
    echo "systemAppearance=$(defaults read -g AppleInterfaceStyle 2>/dev/null || echo Light)";
    echo "os=$(sw_vers -productVersion) $(sw_vers -buildVersion)";
    echo "displayplacerMode=$(/opt/homebrew/bin/displayplacer list | sed -n 's/^  mode \([0-9]*\):.*<-- current mode$/\1/p')";
    echo "binarySha256=$(shasum -a 256 $APP/Contents/MacOS/VitreaReference | cut -c1-64)";
    echo "specSha256=$(shasum -a 256 "$SPEC" | cut -c1-64)";
    echo "foreignProcesses=$(ps -axo pid=,command= | grep -E "$FOREIGN" | grep -v -E 'grep|dump-one' | wc -l | tr -d ' ')";
    echo "session=$(/Users/new/vitrea-w39/scratch/read-session)"; } > "$D/attest.$1"
}
attest open
grep -q "^slider=0.5$" "$D/attest.open" && grep -q "^reduceTransparency=0$" "$D/attest.open" \
  && grep -q "^increaseContrast=0$" "$D/attest.open" && grep -q "^showBorders=0$" "$D/attest.open" \
  && grep -q "^displayplacerMode=$WANTMODE$" "$D/attest.open" && grep -q "^binarySha256=$PIN$" "$D/attest.open" \
  || { echo "REFUSE: gate failed"; cat "$D/attest.open"; exit 2; }
POSEARG=$([ "$POSE" = inactive ] && echo --inactive || echo --require-key)
S=$(date +%s)
open -W --env VITREA_SCALE=$SCALE --env VITREA_SCENES="$SPEC" --env VITREA_FIXTURES="$OUT/.fixtures" \
  --stdout "$D/dump.out" --stderr "$D/dump.err" "$APP" --args dump-layers --scenes "$IDS" \
  --settle "$SETTLE" --scheme "$SCHEME" $POSEARG --out "$D/json" &
OPID=$!
N=$(echo "$IDS" | tr ',' '\n' | grep -c .)
LIMIT=$(python3 -c "print(int($N*($SETTLE+1.5)+90))")
while kill -0 $OPID 2>/dev/null; do
  sleep 5
  if [ $(( $(date +%s) - S )) -gt $LIMIT ]; then
    echo "OVERRUN after $LIMIT s; session: $(/Users/new/vitrea-w39/scratch/read-session)"
    pkill -f "$APP/Contents/MacOS/VitreaReference"; sleep 2; kill $OPID 2>/dev/null
    attest close; exit 5
  fi
done
wait $OPID; RC=$?
E=$(date +%s)
attest close
GOT=$(ls "$D/json" 2>/dev/null | grep -c '\.json$')
echo "$LABEL rc=$RC $((E-S))s dumps=$GOT/$N"
[ -s "$D/dump.err" ] && { echo "stderr:"; tail -5 "$D/dump.err"; }
[ "$RC" = 0 ] && [ "$GOT" = "$N" ]
