#!/bin/zsh
# W47 G0 (f): exactly the declared two scenes, never the referee, under the shared GPU gate.
set -u
HERE=${0:A:h}
CAL=${HERE:h:h:h}
OUT=$HOME/vitrea-w47/diag
mkdir -p $HERE/logs
labels=(${@:-control body deep weights zero-share})
for label in $labels; do
  for scale in 1 2; do
    dir=$OUT/$label/${scale}x
    mkdir -p $dir
    log=$HERE/logs/${label}__${scale}x.txt
    ( cd $CAL && env -u VITREA_MATRIX_PATH VITREA_WEB_CAPTURES=$dir/web-captures \
      $HERE/../with-gpu.sh "diagnostic $label/${scale}x" \
      pnpm run -s compare -- --profile apple-macos-27.0-${scale}x-dark-standard-glass0.25 \
        --renderer webgpu --candidate-document $HERE/candidates/$label/candidate.json \
        --set probe --scene checkerboard-8__rrect-md__inactive,checkerboard-8__rrect-lg__inactive \
        --alpha --write-partial --out-matrix $dir/matrix.json ) > $log 2>&1
    code=$?
    echo "$label/${scale}x exit $code"
    [[ $code -eq 0 ]] || exit $code
  done
done
