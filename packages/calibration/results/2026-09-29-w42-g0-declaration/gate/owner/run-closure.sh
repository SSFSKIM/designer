#!/bin/zsh
R=/Users/new/vitrea-w42/g0-decl/packages/calibration/results/2026-09-29-w42-g0-declaration/gate/owner/run-owner.py
P=/tmp/w42-g0-int/owner-inputs
CAN=/Users/new/Developer/GitHub/designer/packages/calibration/web-captures
O=/tmp/w42-g0-int/owner-closure
mkdir -p $O
CANDS=(); for f in $P/candidate/*.json; do CANDS+=(--candidate $f); done
run() { name=$1; shift; python3.12 -B $R "$@" --out $O/$name > $O/$name.stdout 2> $O/$name.stderr; echo "$name exit $?" >> $O/exits.txt; }
BASE=(--base-stage $P/base-light --base-stage $P/base-dark --base-captures $CAN)
C=(--captures $P/cand-captures)
export OPENBLAS_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1
run closure-green "${BASE[@]}" --stage $P/cand-light-closure --stage $P/cand-dark "${CANDS[@]}" $C & sleep 15
run closure-red-no-closures "${BASE[@]}" --stage $P/cand-light-closure --stage $P/cand-dark "${CANDS[@]}" $C --no-closures & sleep 15
run closure-plus-new "${BASE[@]}" --stage $P/cand-light-closure-plus-new --stage $P/cand-dark "${CANDS[@]}" $C &
wait
