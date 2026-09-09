#!/bin/bash
# W26 G0 — the three candidates' ladder: one rung per value of one constant, both scales.
#
# Each rung is the committed documents with ONE of the three candidate constants overridden
# (`g0-candidate.py`), captured over the named ladder rows on the GPU tier into that rung's own
# scratch directory (`g0-rung.sh`). Nothing here touches `profiles/`, the canonical matrix or the
# canonical captures — X2. One capture process at a time — X4.
#
# Candidate (ii)'s σ is written to BOTH scale anchors, because `heavyTapSigmaAtScale` interpolates
# between them and a rung naming only the 1x end would drag the 2x end toward the 2x default of 0;
# the ladder's question is whether ONE nominal width comes back out of reader A at each scale, so
# each scale is asked for the same nominal.
set -u
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PY=/Users/new/.claude/jobs/5c70e47f/tmp/venv/bin/python
T=/Users/new/.claude/jobs/5c70e47f/tmp/w26/g0

rung() {
  local name=$1; shift
  $PY "$HERE/g0-candidate.py" "$T/$name/doc" "$@" > /dev/null
  "$HERE/g0-rung.sh" "$name" "$T/$name/doc/apple-macos-26.5-1x-light-standard.json" \
    "$T/$name/doc/apple-macos-26.5-1x-dark-standard.json" both
}

# Candidate (ii): the Gaussian at the tap, σ in device px, over the wave's 10–25 device px range.
for s in 10 13 16 19 22 25; do
  rung "t$s" "light:sizeHeavyTapSigma=$s" "light:sizeHeavyTapSigma2x=$s"
done

# Candidate (i): the fractional pyramid level, either side of the level the gain already draws.
rung "oM100" "light:sizeHeavyLevelOffset=-1.0"
rung "oM050" "light:sizeHeavyLevelOffset=-0.5"
rung "oP050" "light:sizeHeavyLevelOffset=0.5"
rung "oP100" "light:sizeHeavyLevelOffset=1.0"

# Candidate (iii): the second chain level's share.
for s in 025 050 100; do
  rung "s$s" "light:sizeHeavySecondShare=0.$s"
done

touch "$T/LADDER-DONE"
