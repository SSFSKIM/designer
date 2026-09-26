#!/bin/bash
# collect.sh <pass-scale e.g. active-2x>: copy one rehearsal's attestations (not the generated
# background PNGs) into the G1 evidence dir, with a read-only TCC read and the raw location.
set -euo pipefail
P=$1
SRC=/Users/new/vitrea-w39/run/held/attempt-2/rehearsal-g1/rehearsal-$P
EV=/Users/new/vitrea-w39/g1/packages/calibration/results/2026-09-26-w39-g1-colour-edge-sitting/rehearsal/attempt-2/$P
mkdir -p "$EV"
RUN=$(ls -d "$SRC"/run-1 "$SRC"/QUARANTINE-run-1-* 2>/dev/null | head -1 || true)
find "$RUN" -maxdepth 1 -type f -exec cp -p {} "$EV"/ \;
cp -p "$SRC/scenes-run-1.json" "$EV"/
cp -p /Users/new/vitrea-w39/run/held/attempt-2/rehearsal-logs/$P-driver.txt "$EV"/driver.txt
python3.12 - "$EV" "$RUN" <<'PY'
import json, subprocess, sys
ev, run = sys.argv[1], sys.argv[2]
cmd = ['sqlite3', '-readonly', '-json', '/Library/Application Support/com.apple.TCC/TCC.db',
       "select service,client,auth_value,last_modified from access where service='kTCCServiceScreenCapture' and client like '%vitrea%';"]
r = subprocess.run(cmd, capture_output=True, text=True)
open(f'{ev}/tcc-read.json', 'w').write(json.dumps(dict(command=cmd, exitCode=r.returncode, stdout=r.stdout, stderr=r.stderr), indent=2) + '\n')
open(f'{ev}/location.json', 'w').write(json.dumps(dict(rawRoot=run, admitted=json.load(open(f'{run}/rehearsal.json'))['outcome'] == 'refused-tcc'), indent=2) + '\n')
PY
ls "$EV"
