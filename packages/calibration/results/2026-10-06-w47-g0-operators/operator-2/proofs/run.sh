#!/bin/zsh
# W47 G0(b): op1-only before tree versus the reviewed merged op1+op2 tree.
# Both paths are explicit; each launcher uses THAT worktree's census, GPU lock and pinned browser.
set -u
HERE=${0:A:h}
export W47_CENSUS_DEADLINE=$(( $(date +%s) + 7200 ))
BEFORE=$HOME/vitrea-w47/g0-op2-before
AFTER=$HOME/vitrea-w47/g0-op2
OUT=$HOME/vitrea-w47/op2-proofs
mkdir -p $OUT
run() {
  local tree=$1 label=$2 port=$3; shift 3
  local gate=$tree/packages/calibration/results/2026-10-06-w47-g0-operators/with-gpu.sh
  (cd $tree/packages/renderer-webgpu && env -u VITREA_MATRIX_PATH CI=1 VITREA_GOLDEN_SERVER_PORT=$port \
    python3.12 -B $HERE/census-retry.py $gate "op2-proof $label" "$@") >> $OUT/${label}.log 2>&1
  local code=$?
  echo "$label exit $code"
  [[ $code -eq 0 ]] || return $code
}
for phase in before after; do
  tree=$BEFORE; port=5577
  [[ $phase = after ]] && { tree=$AFTER; port=5578; }
  for repeat in 1 2; do
    dir=$OUT/${phase}-${repeat}
    if [[ -e $dir ]]; then
      if [[ ${1:-} = --resume && -f $dir/cases.json ]] && grep -q '1 passed' $OUT/${phase}-${repeat}.log; then
        echo "$phase-$repeat already recorded successfully; keep its evidence"
        continue
      fi
      echo "$dir exists without a completed recorder, or --resume absent; refuse overwrite"
      exit 1
    fi
    run $tree ${phase}-${repeat} $port env W47_FINE_PROOF_OUT=$dir \
      pnpm exec playwright test e2e/gpu/w47-fine-tap.spec.ts --grep "records every case" || exit $?
  done
  run $tree ${phase}-goldens $port pnpm exec playwright test --grep @golden || exit $?
done
run $AFTER after-assertions 5578 pnpm exec playwright test e2e/gpu/w47-fine-tap.spec.ts \
  --grep "keeps every endpoint" || exit $?
run $AFTER op1-replay 5578 env W47_PROOF_OUT=$OUT/op1-replay \
  pnpm exec playwright test e2e/gpu/w47-alpha-far.spec.ts --grep "records every case" || exit $?
