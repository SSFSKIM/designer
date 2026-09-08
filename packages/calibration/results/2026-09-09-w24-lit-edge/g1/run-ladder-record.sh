#!/bin/bash
# W24 G1 (c) — `ladder.txt`: every rung read the same way, from the scratch captures.
# Usage: `bash run-ladder-record.sh > ladder.txt`
set -eu
G1="$(cd "$(dirname "$0")" && pwd)"
PY=/Users/new/.claude/jobs/5c70e47f/tmp/venv/bin/python
M=/Users/new/Developer/GitHub/designer/packages/calibration/results/matrix.json
T=/Users/new/.claude/jobs/5c70e47f/tmp/w24/g1/ladder

cat <<'HEAD'
W24 G1 (c) — the ladder: the collapse's transmission on vitrea's own pixels

Nine rendered points, GPU tier (apple/metal-3), `--set calibration,validation` — the holdout is not
captured at any rung (X3). Everything under
`/Users/new/.claude/jobs/5c70e47f/tmp/w24/g1/ladder/`; nothing canonical was written.

  control-1x-light   collapseTransmission = 0      the byte-identity control
  probe-{1x,2x}-{light,dark}   = 0.10              the leverage rung
  fit-{1x,2x}-{light,dark}     = 0.017 / 0.070     the confirmation

The fit is exact arithmetic on one rung, because at k = 1 (every `impulse__capsule-button` cell)
the composite is `colour = (1 − c)·toneColour + c·backdrop` and the dot's excess is therefore
LINEAR in c:

  1x   c* = 0.10 × 0.0066 / 0.0386 = 0.0171 → 0.017
  2x   c* = 0.10 × 0.0254 / 0.0363 = 0.0700 → 0.070

and the confirmation rungs render +0.0067 and +0.0256 against the reference's +0.0066 and +0.0254.
The two scales differ by a factor of four because vitrea's own blurred backdrop carries nearly the
same excess at both (0.386 and 0.363) where the reference's transmitted peak is four times larger
at 2x — the kernel finding of `g1-findings.md` §5, stated as a constant.

HEAD

echo "======== the control at c = 0, against the landed 0.12.0 bytes"
bash "$G1/read-ladder.sh" control-1x-light apple-macos-26.5-1x-light-standard 1 | sed -n '/byte identity/,$p'

for spec in "probe-1x-light apple-macos-26.5-1x-light-standard 1" \
            "probe-2x-light apple-macos-26.5-2x-light-standard 2" \
            "probe-1x-dark apple-macos-26.5-1x-dark-standard 1" \
            "probe-2x-dark apple-macos-26.5-2x-dark-standard 2" \
            "fit-1x-light apple-macos-26.5-1x-light-standard 1" \
            "fit-2x-light apple-macos-26.5-2x-light-standard 2" \
            "fit-1x-dark apple-macos-26.5-1x-dark-standard 1" \
            "fit-2x-dark apple-macos-26.5-2x-dark-standard 2"; do
  # shellcheck disable=SC2086
  bash "$G1/read-ladder.sh" $spec
done

echo
echo "======== the bed's own metrics on the cells that move, fit against the landed matrix"
for spec in "fit-1x-light apple-macos-26.5-1x-light-standard" \
            "fit-2x-light apple-macos-26.5-2x-light-standard" \
            "fit-1x-dark apple-macos-26.5-1x-dark-standard" \
            "fit-2x-dark apple-macos-26.5-2x-dark-standard"; do
  set -- $spec
  echo "-- $1"
  $PY "$G1/moved-rows.py" "$M" "$T/$1/matrix.json" "$2" \
    impulse__capsule-button__rest impulse__rrect-md__rest dark-solid__capsule-button__rest \
    impulse__capsule-button__rest-tint-orange
done
