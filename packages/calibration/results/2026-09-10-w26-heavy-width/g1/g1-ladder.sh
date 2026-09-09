#!/bin/bash
# W26 G1 — the width ladder on the STRUCTURAL tap: one rung per value of one constant, both scales.
#
# G0's ladder measured the same constant through a 9 x 9 grid inside the optics pass. G1 rebuilt it
# as a third pyramid texture through the existing separable body blur (W26 Decision Log 2 (b)), and
# a mechanism that changed has to be re-read rather than inherited — the acceptance is that the
# structural tap lands within 5 % of the grid's reading at the same constant, and that is a
# statement about captures, not about arithmetic.
#
# `r0` is the inert default and is the baseline for X5 and for the byte-identity check against the
# canonical 0.14.0 captures. The rest name ONE constant at BOTH scale anchors, for G0's reason:
# `heavyTapSigmaAtScale` interpolates between them, so a rung naming only the 1x end would drag the
# 2x end toward the 2x default of 0, and the ladder's question is whether one nominal width comes
# back out of the readers at each scale.
set -u
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PY=/Users/new/.claude/jobs/5c70e47f/tmp/venv/bin/python
G0="$HERE/../g0"
T=/Users/new/.claude/jobs/5c70e47f/tmp/w26/g1

rung() {
  local name=$1; shift
  $PY "$G0/g0-candidate.py" "$T/$name/doc" "$@" > /dev/null
  "$HERE/g1-rung.sh" "$name" "$T/$name/doc/apple-macos-26.5-1x-light-standard.json" \
    "$T/$name/doc/apple-macos-26.5-1x-dark-standard.json" ladder both
}

rung r0

# The 2x fit's own bracket first (prior 11-12; G0 found 11.3 lands two of three), then G0's ladder
# re-run on the structural tap so the 1x mapping the lattice reader is asked for is a mapping of
# what actually draws.
for s in 11.3 11 12 10 13 16 19 22 25; do
  tag="t$(echo "$s" | tr -d '.')"
  rung "$tag" "light:sizeHeavyTapSigma=$s" "light:sizeHeavyTapSigma2x=$s"
done

touch "$T/LADDER-DONE"
