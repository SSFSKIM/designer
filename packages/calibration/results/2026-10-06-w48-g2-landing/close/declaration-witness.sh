#!/bin/sh
# W48 G2: which declaration check reads what (claims §5.214; the tracker's W48 live-document entry).
#
# W45 G2's witness in a SCRATCH worktree, so the landing's own tree is never touched: a detached
# worktree at the given head, installed and built, with exactly the files the landing's live
# `declare.py check` names put back to their part-1 bytes (W48 G0's merge, 3bfdaaf0c):
#   - the two dark 0.25 documents, which the freeze re-sealed (the seal/stage tool tests build from them);
#   - `results/generations/index.json`, which the publication moved;
#   - `test/tier-coherence.test.ts`, which the freeze moved (operator 1 live on the dark pair);
#   - the three runtime sources G2's comment-only commit edited;
#   - the cross-gate holdout ledger, which read 8 extended (W47's sheets test asserts the
#     pre-exposure refusal, and reads the ledger as COMMITTED, `git show HEAD:<ledger>`, so the
#     put-back bytes are committed on the scratch worktree's detached HEAD: a throwaway commit no
#     branch names, gone with the worktree).
# Then both checks run there. The worktree is removed afterwards.
#
#     sh declaration-witness.sh HEAD_SHA
set -eu
here=$(cd "$(dirname "$0")" && pwd)
repo=$(cd "$here/../../../../.." && pwd)
head=${1:?head}
base=3bfdaaf0c
wt=$HOME/vitrea-w48/g2-scratch/witness-wt
out="$here/declaration-witness.txt"
[ ! -e "$wt" ] || { echo "$wt exists; refusing" ; exit 1; }
git -C "$repo" worktree add --detach "$wt" "$head" > /dev/null 2>&1
files="packages/calibration/profiles/apple-macos-27.0-1x-dark-standard-glass0.25.json
packages/calibration/profiles/apple-macos-27.0-1x-dark-standard-glass0.25-receded.json
packages/calibration/results/generations/index.json
packages/calibration/test/tier-coherence.test.ts
packages/renderer-webgpu/src/material.ts
packages/renderer-webgpu/src/wgsl/optics.ts
packages/platform-web/src/optics.ts
packages/calibration/results/holdout-configuration/configuration-log.json"
{
  echo "W48 G2 declaration witness: a scratch worktree at $head ($(date -u +%Y-%m-%dT%H:%M:%SZ)), with these files"
  echo "put back to their bytes at $base (W48 G0's merge, the bytes part 1 pins):"
  for f in $files; do
    git -C "$wt" show "$base:$f" > "$wt/$f"
    echo "  $f $(shasum -a 256 "$wt/$f" | cut -c1-12)"
  done
} > "$out"
git -C "$wt" -c user.name=witness -c user.email=witness@localhost commit -q --no-verify -am \
  "scratch: part-1 bytes put back for the declaration witness" > /dev/null
echo "  committed on the scratch worktree's detached HEAD as $(git -C "$wt" rev-parse --short HEAD) (no branch)" >> "$out"
(cd "$wt" && pnpm install --frozen-lockfile --offline > /dev/null 2>&1 && pnpm -r build > /dev/null 2>&1) \
  || { echo "install/build failed in $wt" >> "$out"; exit 1; }
set +e
(cd "$wt/packages/calibration" && python3.12 -B results/2026-10-06-w48-g0-declaration/declare.py check) \
  > "$here/declaration-witness-check.txt" 2>&1
c=$?
(cd "$wt/packages/calibration" && python3.12 -B results/2026-10-06-w48-g0-declaration/declare.py check-fit) \
  > "$here/declaration-witness-check-fit.txt" 2>&1
f=$?
set -e
{
  echo "with those bytes: declare.py check exit $c ($(tail -1 "$here/declaration-witness-check.txt"))"
  echo "with those bytes: declare.py check-fit exit $f ($(tail -1 "$here/declaration-witness-check-fit.txt"))"
} >> "$out"
git -C "$repo" worktree remove --force "$wt"
echo "scratch worktree removed" >> "$out"
cat "$out"
