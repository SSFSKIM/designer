#!/bin/zsh
# Orchestrator-requested liveness check after G0(f), not fitting or a new diagnostic choice.
set -u
HERE=${0:A:h}
CAL=${HERE:h:h:h:h}
OUT=$HOME/vitrea-w47/diag/positive-control
for label in coarse-control coarse-deep fine-deep40; do
  if [[ $label = coarse-control ]]; then
    candidate=$HERE/../candidates/control/candidate.json
    scene=checkerboard-64__rrect-md__inactive
  elif [[ $label = coarse-deep ]]; then
    candidate=$HERE/../candidates/deep/candidate.json
    scene=checkerboard-64__rrect-md__inactive
  else
    candidate=$HERE/candidates/deep40/candidate.json
    scene=checkerboard-8__rrect-md__inactive,checkerboard-8__rrect-lg__inactive
  fi
  for scale in 1 2; do
    dir=$OUT/$label/${scale}x
    mkdir -p $dir
    (cd $CAL && env -u VITREA_MATRIX_PATH VITREA_WEB_CAPTURES=$dir/web-captures \
      $HERE/../../with-gpu.sh "diagnostic-positive $label/${scale}x" \
      pnpm run -s compare -- --profile apple-macos-27.0-${scale}x-dark-standard-glass0.25 \
        --renderer webgpu --candidate-document $candidate --set probe --scene $scene \
        --alpha --write-partial --out-matrix $dir/matrix.json) > $HERE/logs/${label}__${scale}x.txt 2>&1
    code=$?
    echo "$label/${scale}x exit $code"
    [[ $code -eq 0 ]] || exit $code
  done
done
