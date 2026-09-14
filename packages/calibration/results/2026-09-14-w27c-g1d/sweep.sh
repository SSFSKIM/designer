#!/bin/bash
# Declared WebGPU sweeps. Every output is scratch; the canonical matrix is never opened.
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
PKG="$(cd "$HERE/../.." && pwd)"
OUT="${OUT:-/tmp/w27c-g1d-sweeps}"
RUN=(npx tsx results/2026-09-14-w27c-g1d/g1d-run.ts --out "$OUT")
cd "$PKG"

case "${1:?usage: sweep.sh t1|t2-rt|t2-ic}" in
  t1)
    cells='^(mid-light-solid__(rrect-sm|rrect-lg)|light-solid__(rrect-sm|rrect-lg)|mid-dark-solid__rrect-sm|dark-solid__rrect-sm|hc-text__rrect-sm|checkerboard-lc16__capsule-button)__inactive$'
    controls='^(checkerboard|photo)__capsule-button__inactive$'
    "${RUN[@]}" --label t1-baseline \
      --patch results/2026-09-14-w27c-g1d/sweeps/baseline.json \
      --profiles dark-standard --cells "$cells" --controls "$controls"
    for id in anchor-0.5490 step-0.7000 step-0.7400 step-0.7652 step-0.8000 step-0.8500; do
      "${RUN[@]}" --label "t1-$id" \
        --patch "results/2026-09-14-w27c-g1d/sweeps/t1-$id.json" \
        --profiles dark-standard --cells "$cells" --controls "$controls"
    done
    ;;
  t2-rt)
    cells='^(checkerboard__rrect-md|photo__rrect-md|dark-solid__rrect-(48|80)|hc-text-28__rrect-md|light-solid__rrect-ml)__inactive$'
    "${RUN[@]}" --label t2-rt-baseline \
      --patch results/2026-09-14-w27c-g1d/sweeps/baseline.json \
      --profiles reduced-transparency --cells "$cells"
    for lift in 0.88 0.9 0.92 0.94 0.96; do
      "${RUN[@]}" --label "t2-rt-$lift" \
        --patch "results/2026-09-14-w27c-g1d/sweeps/t2-rt-$lift.json" \
        --profiles reduced-transparency --cells "$cells"
    done
    ;;
  t2-ic)
    cells='^(checkerboard__rrect-md|photo__rrect-md|dark-solid__rrect-(48|80)|hc-text-28__rrect-md|light-solid__rrect-ml)__inactive$'
    "${RUN[@]}" --label t2-ic-baseline \
      --patch results/2026-09-14-w27c-g1d/sweeps/baseline.json \
      --profiles increased-contrast --cells "$cells"
    for lift in 0.96 0.98 0.99 1; do
      "${RUN[@]}" --label "t2-ic-$lift" \
        --patch "results/2026-09-14-w27c-g1d/sweeps/t2-ic-$lift.json" \
        --profiles increased-contrast --cells "$cells"
    done
    ;;
  *) echo "unknown sweep $1" >&2; exit 2;;
esac
