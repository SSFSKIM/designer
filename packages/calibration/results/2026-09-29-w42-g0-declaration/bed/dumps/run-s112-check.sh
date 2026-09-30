#!/bin/bash
# G0's side-bundle acceptance check of the bed's shapes, run once at 2x (display mode 68):
# one dump-layers launch per endpoint over one scene per glass component of the bed (15),
# H's rrect-112 first, each launch preceded by memo D's idle gate (gate.sh: >= 60 s HID idle,
# unlocked, no permission prompt on screen; otherwise wait for 300 s idle, at most 3 h).
set -uo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OUT=${OUT:-/Users/new/vitrea-w42/g0-bed-scratch/dumps}
GATE=/Users/new/vitrea-w42/grounding/dumps/gate.sh
IDS=h-p1-c24-rrect-112__rest,a-g000-capsule-button__rest,bp-p1-c4-capsule-button-odd__rest,c-s16-hi-capsule-button__rest,a-g160-rrect-64__rest,a-g160-rrect-80__rest,a-g096-rrect-lg__rest,c-s8-hi-d4-rrect-lg__rest,c-s8-hi-d80-rrect-lg__rest,c-s8-hi-d40-rrect-lg__rest,a-g000-rrect-md__rest,c-s8-hi-d4-rrect-md__rest,c-s8-hi-d24-rrect-md__rest,c-s32-hi-rrect-md__rest,a-g160-rrect-ml__rest
for c in light:active light:inactive dark:active dark:inactive; do
  SCHEME=${c%%:*}; POSE=${c##*:}
  $GATE || { echo "idle gate refused ($?)"; exit 3; }
  "$HERE/dump-one.sh" "$OUT" "2x-$SCHEME-$POSE" 2 "$SCHEME" "$POSE" 8 "$IDS" || { echo "dump failed"; exit 4; }
  P=$([ "$POSE" = inactive ] && echo receded || echo active)
  python3.12 "$HERE/dumpcheck.py" check "$OUT/2x-$SCHEME-$POSE/json" --scheme "$SCHEME" --pose "$P" --scale 2 \
    --expect "$IDS" --out "$OUT/2x-$SCHEME-$POSE/check.json"
done
echo "display mode at exit: $(/opt/homebrew/bin/displayplacer list | sed -n 's/^  mode \([0-9]*\):.*<-- current mode$/\1/p')"
