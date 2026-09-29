#!/bin/bash
# The s = 32 receded rows' dump check (the parent's ruling from the gate rehearsal): one
# dump-layers launch per scheme in the receded pose at 2x (display mode 68), over the rows' two
# rrect-sm shapes (the centred step and the offset centre patch), each launch behind memo D's
# idle gate, each dump checked by dumpcheck.py against memo D's configuration.
set -uo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OUT=${OUT:-/Users/new/vitrea-w42/g0-bed-scratch/dumps-s32}
GATE=/Users/new/vitrea-w42/grounding/dumps/gate.sh
for c in light:hi dark:lo; do
  SCHEME=${c%%:*}; POL=${c##*:}
  IDS=d-d0-lohi-rrect-sm__rest,c-s8-$POL-rrect-sm__rest
  $GATE || { echo "idle gate refused ($?)"; exit 3; }
  "$HERE/dump-one.sh" "$OUT" "2x-$SCHEME-inactive" 2 "$SCHEME" inactive 8 "$IDS" || { echo "dump failed"; exit 4; }
  python3.12 "$HERE/dumpcheck.py" check "$OUT/2x-$SCHEME-inactive/json" --scheme "$SCHEME" --pose receded --scale 2 \
    --expect "$IDS" --out "$OUT/2x-$SCHEME-inactive/check.json"
done
echo "display mode at exit: $(/opt/homebrew/bin/displayplacer list | sed -n 's/^  mode \([0-9]*\):.*<-- current mode$/\1/p')"
