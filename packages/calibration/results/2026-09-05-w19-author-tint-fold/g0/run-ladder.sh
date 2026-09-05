#!/bin/bash
# W19 G0 (b) — the strength ladder's captures, both tiers, to scratch.
#
# `compare` is not the driver, for W18 G0's reason: most of this bed's twenty scenes have no native
# fixture and never will, while the quantity under test — the CSS tier's interior mean minus the GPU
# tier's, at each strength — needs no reference at all. So the driver is `capture-web` and the reading
# is `ladder.ts`'s, under the declared component region (and under the native silhouette too, on the
# five cells the canonical bed does carry a fixture for).
#
# Eight runs, one at a time on the shared adapter, the GPU tier first so that a CSS-tier crash cannot
# leave the untouched tier unmeasured: the standard light profile at both scales on both tiers, and
# the two fold profiles at 1x on both tiers over the photo, where the charter reads strengths 0.2 and
# 0.5 with the full-strength and untinted cells beside them as controls.
#
# Nothing canonical is written: the bed is scratch through `VITREA_SCENES`, the captures land under
# the scratch root through `--out`, and `VITREA_FIXTURES` is unset so the page fetches the committed
# backgrounds read-only through the dev server's mount.
#
# Usage: `bash run-ladder.sh <scenesJson> <captureRoot> <logDir>`, from `packages/calibration`.
set -u
SCENES="${1:?usage: run-ladder.sh <scenesJson> <captureRoot> <logDir>}"
OUT="${2:?}"
LOGS="${3:?}"
mkdir -p "$OUT" "$LOGS"

wait_for_gpu() {
  while pgrep -f 'compare.ts|sweep.ts|cost.mjs|capture.mjs|capture-web|VitreaReference' > /dev/null \
     || lsof -i :5189 > /dev/null 2>&1; do
    echo "waiting for the GPU $(date -u +%H:%M:%SZ)"; sleep 20
  done
}

unset VITREA_FIXTURES
export VITREA_SCENES="$SCENES"

FOLD_CELLS="photo__capsule-button__rest photo__capsule-button__rest-tint-orange-020 \
photo__capsule-button__rest-tint-orange-half photo__capsule-button__rest-tint-orange"

for tier in webgpu css; do
  for scale in 1 2; do
    wait_for_gpu
    echo "=== $(date -u +%H:%M:%SZ) standard $tier @${scale}x"
    npx tsx scripts/capture-web.ts --all --renderer "$tier" --scale "$scale" \
      --out "$OUT/std-$tier-${scale}x" > "$LOGS/std-$tier-${scale}x.log" 2>&1
    echo "    exit=$?"
  done
done

for acc in reduced-transparency increased-contrast; do
  for tier in webgpu css; do
    wait_for_gpu
    echo "=== $(date -u +%H:%M:%SZ) $acc $tier @1x"
    # shellcheck disable=SC2086
    npx tsx scripts/capture-web.ts $FOLD_CELLS --renderer "$tier" --scale 1 \
      --accessibility "$acc" --out "$OUT/fold-$acc-$tier-1x" > "$LOGS/fold-$acc-$tier.log" 2>&1
    echo "    exit=$?"
  done
done
echo "DONE $(date -u +%H:%M:%SZ)"
