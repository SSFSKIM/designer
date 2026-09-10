#!/bin/bash
# W26 G1c — re-run only the rungs a row set is missing, and wait out a vitrea capture if one starts.
#
# The first probe ladder lost five of its seven rungs to a guard that refused on Playwright's
# resident daemon (see `g1c-guard.sh` for what changed and why). Re-running the whole ladder would
# re-capture the two that succeeded for nothing, so this fills the gaps: a rung is skipped if its
# scratch directory already carries a DONE marker.
#
#   g1c-fill.sh [reader|probe|bed]
set -u
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PY=/Users/new/.claude/jobs/5c70e47f/tmp/venv/bin/python
G0="$HERE/../g0"
T=/Users/new/.claude/jobs/5c70e47f/tmp/w26/g1c
ROWS=${1:-probe}
case "$ROWS" in probe) S=p ;; bed) S=b ;; *) S= ;; esac

fill() {
  local name=$1$S one=$2 two=$3
  if [ -f "$T/$name/DONE" ]; then echo "skip $name (done)"; return; fi
  $PY "$G0/g0-candidate.py" "$T/$name/doc" \
    "both:sizeHeavyTapSigma=$one" "both:sizeHeavyTapSigma2x=$two" > /dev/null
  "$HERE/g1c-rung.sh" "$name" \
    "$T/$name/doc/apple-macos-26.5-1x-light-standard.json" \
    "$T/$name/doc/apple-macos-26.5-1x-dark-standard.json" "$ROWS" both
}

fill c0   13.418 0
fill d8   8      8
fill d9   9      9
fill d10  10     10
fill d11  11     11
fill x98  9      8
fill x910 9      10
touch "$T/FILL-$ROWS-DONE"
echo "FILL $ROWS DONE $(date +%H:%M:%S)"
