#!/bin/sh
# W32 G2 — the discrimination proof behind `cut-discrimination.txt` (claims §5.169 §1, §3).
#
#   sh results/2026-09-21-w32-g2-landing/cut-discrimination.sh > cut-discrimination.txt 2>&1
#
# Run from the package root. It takes its own copies of the three files it
# perturbs, restores every one of them from those copies after each
# perturbation, and prints the three SHA-256 at the end against the copies, so a
# reader can see the committed files are the unperturbed ones.
set -u
D=results/2026-09-21-w32-g2-landing
B=$(mktemp -d)
cp test/adopted-thresholds.test.ts "$B/att.bak"
cp $D/exterior-cut.json "$B/ec.bak"
cp $D/chroma-cut.json "$B/cc.bak"
run() {
  printf '── %s\n' "$1"
  pnpm --filter @vitrea/calibration --fail-if-no-match exec vitest run test/adopted-thresholds.test.ts 2>&1 \
    | grep -E "^ *Tests  |^ *Test Files |^ +× " | sed 's/^/   /' | head -14
  printf '\n'
}
restore() { cp "$B/att.bak" test/adopted-thresholds.test.ts; cp "$B/ec.bak" $D/exterior-cut.json; cp "$B/cc.bak" $D/chroma-cut.json; }

cat <<'EOF'
W32 G2 — the new and re-pointed rows discriminate, proved rather than asserted
=============================================================================================

  W31 G2's closure and W31 G3c's `append-check-discrimination.txt` record the same lesson from
  two directions — a clause that cannot fail reads PASS forever, and the only way that class is
  ever found is by making it fail — and a newly adopted row is where it matters, because it has
  never been red. Five perturbations, each restored before the next so nothing accumulates,
  including by name the seeded bogus excuse W32 Decision Log 4 asks this gate to prove.

  Every perturbation is made in place and reverted from a copy taken before the first; the two
  cuts' SHA-256 are printed at the end against the copies, so the committed files are the
  unperturbed ones.

EOF
run "baseline — C1's twelve rows, M1, M2 and the two owner cases"

# 1. a passing C1 cell pushed past the bound
python3 - <<'PY'
import json
d=json.load(open('results/2026-09-21-w32-g2-landing/exterior-cut.json'))
n=0
for r in d['rows']:
    if r['bed']=='1x light' and r['span']==96 and r['tier']=='webgpu' and r['state']!='inactive' \
       and r['set']!='holdout' and r['T'] is not None:
        r['T']=0.0061; n+=1
json.dump(d, open('results/2026-09-21-w32-g2-landing/exterior-cut.json','w'), indent=1)
print(f"   (every 1x light span-96 T set to 0.0061, {n} cells)")
PY
run "C1: the 1x light span-96 cells pushed to T 0.0061"
restore

# 2. one C1 cell moved away from the matrix it was read off
python3 - <<'PY'
import json
p='results/2026-09-21-w32-g2-landing/exterior-cut.json'
d=json.load(open(p))
for r in d['rows']:
    if (r['bed']=='2x dark' and r['span']==160 and r['tier']=='webgpu' and r['T'] is not None
            and r['state']!='inactive' and r['set']!='holdout'
            and '/'.join(r['bandsUsed'])=='/'.join(r['admitted'])):
        print(f"   ({r['profile']} {r['scene']}: T {r['T']:.8f} -> 0.00100000)")
        r['T']=0.001; break
json.dump(d, open(p,'w'), indent=1)
PY
run "C1: one cell's T moved away from the matrix it was read off (still inside the bound)"
restore

# 3. the band rule moved under the cut
python3 - <<'PY'
import json
p='results/2026-09-21-w32-g2-landing/exterior-cut.json'
d=json.load(open(p))
n=0
for r in d['rows']:
    if r['span']==160 and r['admitted']==['3-6','6-12']:
        r['admitted']=['3-6','6-12','12-24']; n+=1
json.dump(d, open(p,'w'), indent=1)
print(f"   (span 160's admitted set widened to three bands on {n} rows)")
PY
run "C1: the admitted band set at span 160 widened under the cut"
restore

# 4. one M2 cell moved 3% off its re-baselined reference
python3 - <<'PY'
import json
p='results/2026-09-21-w32-g2-landing/chroma-cut.json'
d=json.load(open(p))
for c in d['cells']:
    if c['scene']=='photo__rrect-md__rest' and c['profile'].endswith('1x-light-standard-glass0.5'):
        print(f"   ({c['profile']} {c['scene']}: Δsd {c['structureDeltaFraction']*100:.3f}% -> -3.000%)")
        c['structureDeltaFraction']=-0.03
        c['interiorStdDevWeb']=c['interiorStdDevWebReference']*0.97
        break
json.dump(d, open(p,'w'), indent=2)
PY
run "M2: one cell moved 3% off THIS gate's reference"
restore

# 5. the bogus excuse — Decision Log 4's own ask
python3 - <<'PY'
from pathlib import Path
p=Path('test/adopted-thresholds.test.ts'); s=p.read_text()
anchor='''  "texture / validation / photo__rrect-sm__rest / apple-macos-27.0-2x-light-standard-glass0.5 :: chromaStructureRatioR": { measured: 1.44950, bound: "≤ 1.40" },\n'''
assert anchor in s
seeded='''  "texture / calibration / photo__rrect-md__rest / apple-macos-27.0-1x-light-standard-glass0.5 :: interiorStdDevStructureDelta": { measured: 0.00049, bound: "≤ 0.02" },\n'''
p.write_text(s.replace(anchor, anchor+seeded, 1))
print("   (a bogus M2 excuse seeded for photo__rrect-md__rest on 1x light, a cell that PASSES)")
PY
run "M2: a bogus excuse for a passing cell (Decision Log 4's own proof)"
restore

run "restored — baseline again"
echo "── the committed files, against the copies taken before the first perturbation"
for f in exterior-cut.json chroma-cut.json; do
  a=$(shasum -a 256 "$D/$f" | cut -d' ' -f1)
  case $f in exterior-cut.json) b=$(shasum -a 256 "$B/ec.bak" | cut -d' ' -f1);; *) b=$(shasum -a 256 "$B/cc.bak" | cut -d' ' -f1);; esac
  if [ "$a" = "$b" ]; then echo "   $f  $a  identical"; else echo "   $f  DIFFERS"; fi
done
a=$(shasum -a 256 test/adopted-thresholds.test.ts | cut -d' ' -f1); b=$(shasum -a 256 "$B/att.bak" | cut -d' ' -f1)
[ "$a" = "$b" ] && echo "   adopted-thresholds.test.ts  $a  identical" || echo "   adopted-thresholds.test.ts  DIFFERS"
