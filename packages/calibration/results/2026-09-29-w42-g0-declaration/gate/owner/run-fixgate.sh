#!/bin/zsh
# The fix wave's owner-runner proof (the gate review of b151aff4: findings 1, 2, 8 and item A1).
# Inputs: python3.12 -B proof-inputs.py --out /tmp/w42-g0-fixgate/owner-inputs
R=/Users/new/vitrea-w42/g0-fix-gate/packages/calibration/results/2026-09-29-w42-g0-declaration/gate/owner/run-owner.py
P=/tmp/w42-g0-fixgate/owner-inputs
CAN=/Users/new/Developer/GitHub/designer/packages/calibration/web-captures
O=/tmp/w42-g0-fixgate/owner
COMMIT=${COMMIT:-44462152}
mkdir -p $O
CANDS=(); for f in $P/candidate/*.json; do CANDS+=(--candidate $f); done
run() { name=$1; shift; python3.12 -B $R --commit $COMMIT "$@" --out $O/$name > $O/$name.stdout 2> $O/$name.stderr; echo "$name exit $?" >> $O/exits.txt; }
BASE=(--base-stage $P/base-light --base-stage $P/base-dark --base-captures $CAN)
C=(--captures $P/cand-captures "${CANDS[@]}")
export OPENBLAS_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1
run g1-red-no-rt --base-stage $P/base-light-no-rt --base-stage $P/base-dark --base-captures $CAN \
    --stage $P/cand-light-no-rt --stage $P/cand-dark $C & sleep 20
run green "${BASE[@]}" --stage $P/cand-light --stage $P/cand-dark $C & sleep 20
run g2-green --base-stage $P/base-light-g2 --base-stage $P/base-dark-g2 --base-captures $CAN \
    --stage $P/cand-light-g2 --stage $P/cand-dark-g2 $C & sleep 20
run a1-green "${BASE[@]}" --stage $P/cand-light-a1 --stage $P/cand-dark-a1 $C & sleep 20
run a1-fifth "${BASE[@]}" --stage $P/cand-light-a1-fifth --stage $P/cand-dark-a1 $C & sleep 20
run a1-no-insertion "${BASE[@]}" --stage $P/cand-light-a1 --stage $P/cand-dark-a1 $C \
    --no-l1-growth-named-misses & sleep 20
run closure-move "${BASE[@]}" --stage $P/cand-light-closure-move --stage $P/cand-dark $C & sleep 20
run closure-move-no-closures "${BASE[@]}" --stage $P/cand-light-closure-move --stage $P/cand-dark $C \
    --no-closures & sleep 20
run closure-move-plus-new "${BASE[@]}" --stage $P/cand-light-closure-move-plus-new \
    --stage $P/cand-dark $C & sleep 20
run g8-red-shared --base-stage $P/base-light-seeded --base-stage $P/base-dark --base-captures $CAN \
    --stage $P/cand-light-seeded --stage $P/cand-dark $C & sleep 20
run m2-toward "${BASE[@]}" --stage $P/cand-light-m2-toward --stage $P/cand-dark $C &
wait
