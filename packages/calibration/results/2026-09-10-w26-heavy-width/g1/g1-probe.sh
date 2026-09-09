#!/bin/bash
# W26 G1 — one material over the whole probe set, at the four standard profiles.
#
# The ladder's eighteen named rows answer a width's question and none of the others. The level
# above the knee is read on the probe SOLIDS, the "one width per source" check is read on the
# mid-span rows (spans 44 -> 96) that the ladder does not carry, and X5's sweep wants every thin
# cell rather than three of them. So a material that is going to be recommended is captured over
# `--set probe` at both scales in both schemes, and everything after that is a difference between
# two capture roots — `p0` the inert default, `pc` the candidate.
#
#   g1-probe.sh <rung> [light:key=value ...]
#
# One capture process at a time (X4); scratch only (X2).
set -u
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PY=/Users/new/.claude/jobs/5c70e47f/tmp/venv/bin/python
G0="$HERE/../g0"
T=/Users/new/.claude/jobs/5c70e47f/tmp/w26/g1
NAME=${1:?rung}
shift
$PY "$G0/g0-candidate.py" "$T/$NAME/doc" "$@" > /dev/null
"$HERE/g1-rung.sh" "$NAME" "$T/$NAME/doc/apple-macos-26.5-1x-light-standard.json" \
  "$T/$NAME/doc/apple-macos-26.5-1x-dark-standard.json" probe both
touch "$T/PROBE-$NAME-DONE"
