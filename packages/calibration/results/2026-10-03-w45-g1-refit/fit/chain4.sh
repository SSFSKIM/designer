#!/bin/zsh
# W45 G1 continuation: the full fit map on each path's factorial ten best, then stage 2 re-run from
# each path's new stage-1 point (resumed after recover.py on a partial objective), then the joint read.
cd /Users/new/vitrea-w45/g1/packages/calibration/results/2026-10-03-w45-g1-refit/fit
G0F=../../2026-10-03-w45-g0-operator/fit
python3.12 -B factorial.py full $(cat path/factorial/top20.txt) > logs/factorial-full-top20.txt 2>&1; echo "exit $?" >> logs/factorial-full-top20.txt
step() {
  local n=1
  while true; do
    local log=logs/factorial-$3.attempt$n.txt
    python3.12 -B factorial.py $1 $2 > $log 2>&1
    local code=$?
    echo "exit $code" >> $log
    [[ $code == 0 ]] && return 0
    if grep -q "run recover.py, then the search again" $log && (( n < 8 )); then
      (cd $G0F && python3.12 -B recover.py) > logs/recover-factorial-$3.attempt$n.txt 2>&1 || return 2
      n=$((n + 1)); continue
    fi
    return 1
  done
}
step stage2 c05 c05-stage2 || exit 12
step stage2 joint joint-stage2 || exit 13
