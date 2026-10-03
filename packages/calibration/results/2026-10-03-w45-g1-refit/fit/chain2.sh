#!/bin/zsh
# W45 G1 step 2: the remaining stages in order, each resumed after recover.py when a render left a
# partial objective (search.py refuses to rank one: "run recover.py, then the search again").
cd /Users/new/vitrea-w45/g1/packages/calibration/results/2026-10-03-w45-g0-operator/fit
L=../../2026-10-03-w45-g1-refit/fit
run_stage() {  # stage start base logname
  local n=1
  while true; do
    local log=$L/logs/search-$4.attempt$n.txt
    python3.12 -B $L/search_g1.py stage $1 --start $2 --base $3 > $log 2>&1
    local code=$?
    echo "exit $code" >> $log
    [[ $code == 0 ]] && return 0
    if grep -q "run recover.py, then the search again" $log && (( n < 8 )); then
      python3.12 -B recover.py > $L/logs/recover-$4.attempt$n.txt 2>&1 || return 2
      n=$((n + 1))
      continue
    fi
    return 1
  done
}
landed() { python3.12 -c "import json;print(json.load(open('$L/path/$1/$2.json'))['landed'])"; }
# joint stage 1 is done (path/joint/stage1.json); stage 2 runs through search_g1.py (the label correction)
run_stage stage2 c05 $(landed c05 stage1) c05-stage2.g1 || exit 12
run_stage stage2 joint $(landed joint stage1) joint-stage2.g1 || exit 13
