#!/bin/sh
# W45 G2: which declaration check reads what (claims §5.207 §10; the tracker's W45 live-document entry).
#
# W45 G1's witness (results/2026-10-03-w45-g1-refit/close-checks-gate.txt), repeated at the landing's
# head: with the two light 0.25 documents put back to c05's bytes (git show 67a82a00:<path>), run
# both checks, then restore the sealed bytes with git checkout and verify their hashes. Nothing is
# committed in between and nothing else runs meanwhile. Run after chain.sh, never beside it.
set -eu
here=$(cd "$(dirname "$0")" && pwd)
package=$(cd "$here/../../.." && pwd)
cd "$package"
out="$here/declaration-witness.txt"
light=profiles/apple-macos-27.0-1x-light-standard-glass0.25.json
receded=profiles/apple-macos-27.0-1x-light-standard-glass0.25-receded.json
[ -z "$(git status --short -- profiles)" ] || { echo "profiles/ is not clean; refusing" | tee "$out"; exit 1; }
{
  echo "W45 G2 declaration witness at $(git rev-parse HEAD) ($(date -u +%Y-%m-%dT%H:%M:%SZ))"
  echo "sealed before: $(shasum -a 256 $light | cut -c1-12) $(shasum -a 256 $receded | cut -c1-12)"
} > "$out"
restore() { git checkout -- "$light" "$receded"; }
trap restore EXIT INT TERM HUP
git show "67a82a00:packages/calibration/$light" > "$light"
git show "67a82a00:packages/calibration/$receded" > "$receded"
echo "c05 put back: $(shasum -a 256 $light | cut -c1-12) $(shasum -a 256 $receded | cut -c1-12)" >> "$out"
set +e
python3.12 -B results/2026-10-03-w45-g0-operator/declare.py check > "$here/declaration-witness-check.txt" 2>&1
c=$?
python3.12 -B results/2026-10-03-w45-g0-operator/declare.py check-fit > "$here/declaration-witness-check-fit.txt" 2>&1
f=$?
set -e
restore
trap - EXIT INT TERM HUP
{
  echo "with c05's bytes: declare.py check exit $c ($(tail -1 "$here/declaration-witness-check.txt"))"
  echo "with c05's bytes: declare.py check-fit exit $f ($(tail -1 "$here/declaration-witness-check-fit.txt"))"
  echo "restored: $(shasum -a 256 $light | cut -c1-12) $(shasum -a 256 $receded | cut -c1-12); git status -- profiles: '$(git status --short -- profiles)'"
} >> "$out"
cat "$out"
