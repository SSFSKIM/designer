#!/bin/bash
# The dump check of ruling 3's active guard rows: every new scene in both active 2x passes it is
# captured in (display mode 68), behind memo D's idle gate, checked by dumpcheck.py. The rows add
# no new shape (centred rrect-lg, rrect-lg-o+0+4 and rrect-md-o-44-2 were dumped active before);
# the new scenes are dumped all the same.
set -uo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OUT=${OUT:-/Users/new/vitrea-w42/g0-bed-scratch/dumps-guard}
GATE=/Users/new/vitrea-w42/grounding/dumps/gate.sh
while read -r SCHEME IDS; do
  $GATE || { echo "idle gate refused ($?)"; exit 3; }
  "$HERE/dump-one.sh" "$OUT" "2x-$SCHEME-active" 2 "$SCHEME" active 8 "$IDS" || { echo "dump failed"; exit 4; }
  python3.12 "$HERE/dumpcheck.py" check "$OUT/2x-$SCHEME-active/json" --scheme "$SCHEME" --pose active --scale 2 \
    --expect "$IDS" --out "$OUT/2x-$SCHEME-active/check.json"
done <<'LIST'
light b-p5-c16-rrect-lg__rest,b-p5-c64-rrect-lg__rest,b-p3-c16-rrect-lg__rest,e-rg-c16-rrect-lg__rest,e-by-c16-rrect-lg__rest,c-s8-hi-d60-rrect-lg__rest
dark b-p5-c16-rrect-lg__rest,b-p5-c64-rrect-lg__rest,b-p3-c16-rrect-lg__rest,e-rg-c16-rrect-lg__rest,e-by-c16-rrect-lg__rest,c-s8-lo-d60-rrect-lg__rest,c-s8-lo-p4-d34-rrect-md__rest
LIST
echo "display mode at exit: $(/opt/homebrew/bin/displayplacer list | sed -n 's/^  mode \([0-9]*\):.*<-- current mode$/\1/p')"
