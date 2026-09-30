#!/bin/bash
# The dump check of the cells added by the parent's rulings from the instrument stream's
# separation proof: one scene per new shape in every pose and scheme it is captured in, at 2x
# (display mode 68), each launch behind memo D's idle gate, each dump checked by dumpcheck.py.
#   rrect-md-o-44-2  (depth 34, active)         capsule-button-o+4-16 (end, receded)
#   rrect-md-o+20+16 (corner, receded)          rrect-ml-o-36-24 (dark 16/112, both poses)
set -uo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OUT=${OUT:-/Users/new/vitrea-w42/g0-bed-scratch/dumps-rulings}
GATE=/Users/new/vitrea-w42/grounding/dumps/gate.sh
while read -r SCHEME POSE IDS; do
  $GATE || { echo "idle gate refused ($?)"; exit 3; }
  "$HERE/dump-one.sh" "$OUT" "2x-$SCHEME-$POSE" 2 "$SCHEME" "$POSE" 8 "$IDS" || { echo "dump failed"; exit 4; }
  P=$([ "$POSE" = inactive ] && echo receded || echo active)
  python3.12 "$HERE/dumpcheck.py" check "$OUT/2x-$SCHEME-$POSE/json" --scheme "$SCHEME" --pose "$P" --scale 2 \
    --expect "$IDS" --out "$OUT/2x-$SCHEME-$POSE/check.json"
done <<'LIST'
light active c-s8-hi-d34-rrect-md__rest
dark active c-s8-lo-d34-rrect-md__rest,c-s8-hi-p4-rrect-ml__rest
light inactive c-s16-lo-corner-rrect-md__rest,c-s16-lo-end-capsule-button__rest
dark inactive c-s16-hi-corner-rrect-md__rest,c-s16-hi-end-capsule-button__rest,c-s8-hi-p4-rrect-ml__rest
LIST
echo "display mode at exit: $(/opt/homebrew/bin/displayplacer list | sed -n 's/^  mode \([0-9]*\):.*<-- current mode$/\1/p')"
