#!/bin/bash
# W25 G3b — the JOINT ladder: a grid over (rimLitExponent, rimAlongSideSlope), rendered.
#
# The two constants multiply the same rim amplitude and peak on the same diagonal, so the plane is
# swept rather than either axis alone. Every point is a RENDER — no model of the rim stands between
# the objective and the pixels — and the objective is evaluated on the rendered bins and ranges by
# `g3b-fit.py`, which is why the grid is coarse enough to run and fine enough to locate a minimum
# that a confirmation rung then reproduces.
#
# One capture process at a time (X4): the rungs run strictly in sequence. Everything to scratch.
set -u
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PY=/Users/new/.claude/jobs/5c70e47f/tmp/venv/bin/python
DOCS=/Users/new/.claude/jobs/5c70e47f/tmp/w25/g3b/docs
for P in 0.40 0.55 0.70 0.85 1.00 1.15 1.30; do
  for S in 0.00 0.25 0.45 0.65; do
    TAG="p$(echo "$P" | tr -d '.')s$(echo "$S" | tr -d '.')"
    if [ -f "/Users/new/.claude/jobs/5c70e47f/tmp/w25/g3b/$TAG/DONE" ]; then
      echo "skip $TAG (already rendered)"
      continue
    fi
    "$PY" "$HERE/g3-candidate.py" "$DOCS/$TAG" \
      "both:optics.regular.rimLitExponent=$P" \
      "both:optics.regular.rimAlongSideSlope=$S" > /dev/null
    "$HERE/g3b-ladder.sh" "$TAG" \
      "$DOCS/$TAG/apple-macos-26.5-1x-light-standard.json" \
      "$DOCS/$TAG/apple-macos-26.5-1x-dark-standard.json" | tail -1
  done
done
echo "SWEEP DONE $(date +%H:%M:%S)"
touch /Users/new/.claude/jobs/5c70e47f/tmp/w25/g3b/SWEEP-DONE
