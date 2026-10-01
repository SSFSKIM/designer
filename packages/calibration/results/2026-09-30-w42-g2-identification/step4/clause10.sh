#!/bin/zsh
# W42 G2 step 4: clause 10's referees on one document set's scratch stages, in the G0 gate's
# candidate-admission mode (gate/referees/README.txt, gate/stops/README.txt,
# gate/owner/README.txt), and E2 per cell (Decision Log 5e). Outputs go to $OUT (scratch); the
# summaries worth keeping are copied beside this file by the caller.
#
#   clause10.sh <set>        (after render.py canon <set> and stage.py <set>; base = shipped)
set -uo pipefail
SET=$1
STEP4=${0:A:h}
REPO=${STEP4:h:h:h:h:h}
GATE=$REPO/packages/calibration/results/2026-09-29-w42-g0-declaration/gate
SCRATCH=${W42_STEP4_SCRATCH:-/tmp/w42-g2-step4}
CAN=/Users/new/Developer/GitHub/designer/packages/calibration/web-captures
CAPS=$SCRATCH/canon/$SET/captures
OUT=$SCRATCH/clause10/$SET
mkdir -p $OUT
export OPENBLAS_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1

# The set's non-shipped documents, as the stage rows name them, each pinned by its SHA12.
CANDS=()
DOCS=()
for row in $(python3.12 -c "
import json,sys
d=json.load(open('$STEP4/documents/documents.json'))['sets']['$SET']
for k in ('light','lightReceded','dark','darkReceded'):
    if not d[k]['shipped']: print(d[k]['path']+'='+d[k]['sha256'])
"); do
  CANDS+=(--candidate $row)
  DOCS+=(--document $REPO/${row%=*})
done
SRC=(--stage $SCRATCH/stages/$SET-light --stage $SCRATCH/stages/$SET-dark $CANDS)

cd $GATE/referees
python3.12 -B chroma-cut.py $SRC --out $OUT/chroma-cut.json > $OUT/chroma-cut.txt 2>&1
python3.12 -B m2-rebaseline.py --cut $OUT/chroma-cut.json --out $OUT/m2-rebaseline.json > $OUT/m2-rebaseline.txt 2>&1
python3.12 -B exterior-cut.py $SRC --out $OUT > $OUT/exterior-cut.txt 2>&1
python3.12 -B l1-cut.py $SRC --out $OUT/l1-cut.json > $OUT/l1-cut.txt 2>&1
python3.12 -B black-cut.py $SRC --captures $CAPS --captures $CAN --out $OUT/black-cut.json > $OUT/black-cut.txt 2>&1 \
  || echo "black-cut exit $?" >> $OUT/black-cut.txt
python3.12 -B scratch-union.py $SRC --out $OUT/union.json > $OUT/scratch-union.txt 2>&1

cd $GATE/rehearsal
python3.12 -B e2abs.py --tree $CAPS --out $OUT/e2abs.json > $OUT/e2abs.txt 2>&1
python3.12 -B $STEP4/e2cell.py $OUT/e2abs.json $OUT/e2cell.json > $OUT/e2cell.txt 2>&1

cd $GATE/stops
python3.12 -B stops.py --candidate-root $CAPS $DOCS --out $OUT/stops.json --text $OUT/stops.txt > $OUT/stops-run.txt 2>&1 \
  || echo "stops exit $?" >> $OUT/stops-run.txt

cd $GATE/owner
OWNER_CANDS=()
for d in $DOCS; do [[ $d == --document ]] || OWNER_CANDS+=(--candidate $d); done
python3.12 -B run-owner.py --stage $SCRATCH/stages/$SET-light --stage $SCRATCH/stages/$SET-dark \
  $OWNER_CANDS --captures $CAPS \
  --base-stage $SCRATCH/stages/shipped-light --base-stage $SCRATCH/stages/shipped-dark \
  --base-captures $SCRATCH/canon/shipped/captures \
  --out $SCRATCH/owner/$SET > $OUT/owner.txt 2>&1 || echo "owner exit $?" >> $OUT/owner.txt
echo done
