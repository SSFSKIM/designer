#!/bin/bash
# W26 G1 — the share ladder, with the width in place.
#
# The order the wave chartered: the width first, then the share on the same rows. `c1` is the
# candidate width — the 2x anchor at the fit's own minimum and the 1x anchor at the width the chain
# already draws (`CHAIN_LEVEL_SIGMA[4]` = 13.418 device px), which is what keeps `rampAtScale`
# continuous between the two anchors while the 1x FIT waits for an instrument that can take it.
#
# Two levers, in opposite directions, because that is what the readings ask for:
#   * at 1x reader A puts the heavy share at 0.28 against the reference's 0.47, so
#     `sizeScatterHeavyShareThick1x` lifts `kDeep`;
#   * at 2x it puts it at 0.80-1.00 against the reference's 0.69, so the lever is
#     `sizeScatterFloor2x` coming DOWN off 1 — the lift is not merely inert there, it is pointed
#     the wrong way.
set -u
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PY=/Users/new/.claude/jobs/5c70e47f/tmp/venv/bin/python
G0="$HERE/../g0"
T=/Users/new/.claude/jobs/5c70e47f/tmp/w26/g1
W="light:sizeHeavyTapSigma=13.418 light:sizeHeavyTapSigma2x=11.0"

rung() {
  local name=$1; shift
  $PY "$G0/g0-candidate.py" "$T/$name/doc" $W "$@" > /dev/null
  "$HERE/g1-rung.sh" "$name" "$T/$name/doc/apple-macos-26.5-1x-light-standard.json" \
    "$T/$name/doc/apple-macos-26.5-1x-dark-standard.json" ladder both
}

rung c1
for f in 0.85 0.75 0.65 0.55; do
  rung "c1f${f#0.}" "light:sizeScatterFloor2x=$f"
done
for l in 0.15 0.25 0.35 0.45; do
  rung "c1l${l#0.}" "light:sizeScatterHeavyShareThick1x=$l"
done

touch "$T/SHARE-DONE"
