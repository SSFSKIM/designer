#!/bin/bash
# W26 G1c — does `sizeScatterGainFar2x` still grade anything once the heavy texture is in place?
#
# Two rungs at the SAME candidate width, differing only in that constant: `gf99` at the committed
# 9.9 and `gf48` at 4.8, which equals `sizeScatterGainMax2x` and therefore flattens the span
# grading to nothing. `wgsl/optics.ts` overwrites the chain tap with the heavy texture wherever the
# group's source carries one, and `scatterLod` — the only consumer of `gainEff`, which is the only
# consumer of the three gain constants — feeds only that discarded tap. So the prediction is
# byte-identity, and `g1c-clause.py --gain-silence` measures it.
set -u
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PY=/Users/new/.claude/jobs/5c70e47f/tmp/venv/bin/python
G0="$HERE/../g0"
T=/Users/new/.claude/jobs/5c70e47f/tmp/w26/g1c
ONE=${1:-9}
TWO=${2:-9}

rung() {
  local name=$1 far=$2
  $PY "$G0/g0-candidate.py" "$T/$name/doc" \
    "both:sizeHeavyTapSigma=$ONE" "both:sizeHeavyTapSigma2x=$TWO" \
    "both:sizeScatterGainFar2x=$far" > /dev/null
  "$HERE/g1c-rung.sh" "$name" \
    "$T/$name/doc/apple-macos-26.5-1x-light-standard.json" \
    "$T/$name/doc/apple-macos-26.5-1x-dark-standard.json" reader both
}

rung gf99 9.9
rung gf48 4.8
touch "$T/GAIN-DONE"
echo "GAIN DONE $(date +%H:%M:%S)"
