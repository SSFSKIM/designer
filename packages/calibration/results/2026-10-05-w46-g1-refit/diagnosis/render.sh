#!/bin/zsh
# W46 G1 step 0 (Decision Log 8 item 1): render the one non-withheld validation cell
# impulse__capsule-button__inactive on both dark 0.25 profiles, WebGPU, in candidate mode from G0's
# committed ladder candidates (built from the snapshots, X62): the shipped rung (control, receded
# tintAlpha 0.89) and the receded rungs 0.8 and 0.7 with the active at 0.9. Scratch only.
set -u
HERE=${0:A:h}
CAL=${HERE:h:h:h}
G0=$CAL/results/2026-10-05-w46-g0-declaration
OUT=$HOME/vitrea-w46/g1-scratch/diagnosis
SCENE=impulse__capsule-button__inactive
mkdir -p $HERE/logs
for label in control i-r-0.8 i-r-0.7; do
  for scale in 1 2; do
    dir=$OUT/$label/${scale}x
    mkdir -p $dir
    log=$HERE/logs/${label}__${scale}x.txt
    ( cd $CAL && env -u VITREA_MATRIX_PATH VITREA_WEB_CAPTURES=$dir/web-captures \
      $HERE/../with-gpu.sh "diagnosis $label/${scale}x" \
      pnpm run -s compare -- --profile apple-macos-27.0-${scale}x-dark-standard-glass0.25 \
        --renderer webgpu \
        --candidate-document results/2026-10-05-w46-g0-declaration/ladders/candidates/$label/candidate.json \
        --set validation --scene $SCENE --alpha --write-partial --out-matrix $dir/matrix.json ) > $log 2>&1
    code=$?
    echo "$label/${scale}x exit $code"
    [[ $code -eq 0 ]] || exit $code
  done
done
