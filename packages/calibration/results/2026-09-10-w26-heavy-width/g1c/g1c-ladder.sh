#!/bin/bash
# W26 G1c — the width ladder on the family reader, both anchors named, both documents patched.
#
# THE RUNGS, and why these. W26 Decision Log 5 (c) asks for σ 8 / 9 / 10 / 11 at both scales against
# a 0.14.0 control, on the reading that Apple's heavy component is 8.6–9.6 device px; the diagonal
# rungs bracket that. Two OFF-DIAGONAL rungs — (9, 8) and (9, 10) — separate the scales: with only
# diagonal rungs a 1x reading that moved with the 2x anchor would be invisible, and
# `heavyTapSigmaAtScale` interpolates between the two, so the question "does the 1x anchor alone
# move the 1x reading" has to be asked and not assumed.
#
# `c0` is (13.418, 0) and NOT (13.418, 0.001). The gate on the heavy texture is `heavySigmaCss > 0`
# (`pyramid.ts`), so 0.001 does not decline the mechanism — it builds a heavy texture at chain level
# 0 with a residual of a thousandth of a texel, which makes the deep sample the RAW backdrop. At 0
# the pyramid builds no heavy texture and the pass takes the chain tap it has always taken, which is
# the 0.14.0 path to the bit. `z001` renders 0.001 anyway, once, so that this is measured rather than
# argued: a profile must not name a near-zero heavy width at either anchor.
#
#   g1c-ladder.sh [reader|probe|bed]
set -u
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PY=/Users/new/.claude/jobs/5c70e47f/tmp/venv/bin/python
G0="$HERE/../g0"
T=/Users/new/.claude/jobs/5c70e47f/tmp/w26/g1c
ROWS=${1:-reader}

# Each row set gets its OWN scratch directory — `c0`, `c0p`, `c0b`. A rung directory is cleared at
# the start of a run, so sharing one between the reader's thirteen rows and the probe's fifty-two
# would destroy the captures a reading in flight is holding.
case "$ROWS" in
  probe) SUFFIX=p ;;
  bed) SUFFIX=b ;;
  *) SUFFIX= ;;
esac

rung() {
  local name=$1$SUFFIX one=$2 two=$3
  $PY "$G0/g0-candidate.py" "$T/$name/doc" \
    "both:sizeHeavyTapSigma=$one" "both:sizeHeavyTapSigma2x=$two" > /dev/null
  "$HERE/g1c-rung.sh" "$name" \
    "$T/$name/doc/apple-macos-26.5-1x-light-standard.json" \
    "$T/$name/doc/apple-macos-26.5-1x-dark-standard.json" "$ROWS" both
}

rung c0   13.418 0
rung d8   8      8
rung d9   9      9
rung d10  10     10
rung d11  11     11
rung x98  9      8
rung x910 9      10
if [ "$ROWS" = "reader" ]; then
  rung z001 13.418 0.001
fi

touch "$T/LADDER-$ROWS-DONE"
echo "LADDER $ROWS DONE $(date +%H:%M:%S)"
