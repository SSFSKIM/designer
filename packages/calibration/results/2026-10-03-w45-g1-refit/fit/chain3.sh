#!/bin/zsh
# W45 G1 continuation (the 2026-10-04 ruling): stage 1's factorial and its thick/far pass on both
# paths, each step resumed after recover.py when a render left a partial objective.
cd /Users/new/vitrea-w45/g1/packages/calibration/results/2026-10-03-w45-g1-refit/fit
G0F=../../2026-10-03-w45-g0-operator/fit
step() {  # verb lineage logname
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
step stage1 c05 c05-stage1 || exit 11
step stage1 joint joint-stage1 || exit 12
step thick c05 c05-thick || exit 13
step thick joint joint-thick || exit 14
