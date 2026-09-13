#!/bin/bash
# W27c G1c: the declared ladders, run on the WebGPU tier into scratch.
#
# One rung, one matrix, one label. Nothing canonical is written: the matrices and
# captures go to $OUT (default /tmp/w27c-g1c) and `results/matrix.json` is never
# opened. The driver refuses the run outright if either of the machine's own
# accessibility settings is on, so this script does not check them itself — a
# second copy of that gate would be a second chance to get it wrong.
#
#   ./sweep.sh t1        the dark thin far ordinate, five rungs
#   ./sweep.sh t2-s1     the accessibility cap, three rungs
#   ./sweep.sh t2-s2 0   the occlusion lift at the cap s1 selected
set -euo pipefail
cd "$(dirname "$0")/../.."
OUT="${OUT:-/tmp/w27c-g1c}"
RUN=(npx tsx results/2026-09-13-w27c-g1c-fit/g1c-run.ts --out "$OUT")

case "${1:?usage: sweep.sh t1|t2-s1|t2-s2 [cap]}" in
  t1)
    # The calibration cell and the two bed controls come through --cells; the two
    # recovered controls are outside the bed and come through --controls, which
    # records per row that neither the plurality nor the pose proof exists for
    # them. The span-44 holdout is not in either pattern and is not captured.
    for x in 0.1611 0.3 0.5 0.7 0.93261; do
      "${RUN[@]}" --label "t1-far-$x" \
        --patch "results/2026-09-13-w27c-g1c-fit/sweeps/t1-far-$x.json" \
        --profiles 'dark-standard' \
        --cells '^(light-solid|mid-dark-solid|dark-solid)__rrect-sm__inactive$' \
        --controls '^(checkerboard|photo)__capsule-button__inactive$'
    done
    ;;
  t2-s1)
    for cap in 0.45 0.2 0; do
      "${RUN[@]}" --label "t2-s1-cap-$cap" \
        --patch "results/2026-09-13-w27c-g1c-fit/sweeps/t2-s1-cap-$cap.json" \
        --profiles 'increased-contrast|reduced-transparency' \
        --cells '^(dark-solid__rrect-48|checkerboard__rrect-md|photo__rrect-md)__inactive$'
    done
    ;;
  t2-s2)
    cap="${2:?the cap s1 selected}"
    for lift in 0.92 0.96 1; do
      "${RUN[@]}" --label "t2-s2-cap-$cap-lift-$lift" \
        --patch "results/2026-09-13-w27c-g1c-fit/sweeps/t2-s2-cap-$cap-lift-$lift.json" \
        --profiles 'increased-contrast|reduced-transparency' \
        --cells '^(dark-solid__rrect-48|checkerboard__rrect-md|photo__rrect-md)__inactive$'
    done
    ;;
  *) echo "unknown ladder $1" >&2; exit 2;;
esac
