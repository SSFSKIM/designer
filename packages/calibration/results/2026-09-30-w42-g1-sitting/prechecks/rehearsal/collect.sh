#!/bin/bash
# collect.sh <rehearsal root> <attempt name>: copy one TCC-refusal rehearsal attempt into the G1
# evidence. W42 G1 phase 1, check 2 (derived from W39 G1's rehearsal/attempt-2/collect.sh).
#
# Per pass, the sitting's own collect-pass.py (attestations, launch, rehearsal verdict or refusal,
# the driver log, the scenes file's SHA-256). Beside it, what that tool leaves out or git would
# drop: each run's idle-wait log as driver-idle.txt, since `*.log` is gitignored, and the harness's
# stderr, which carries the TCC-gate sentence the verdict is read from. Then the orchestrator's
# logs and one read-only system TCC read. Never a generated background PNG.
set -euo pipefail
ROOT=$1
EV="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/$2"
SITTING="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../2026-09-29-w42-g0-declaration/bed/sitting" && pwd)"
mkdir -p "$EV/logs"
for pass in "$ROOT"/rehearsal-*; do
  name=$(basename "$pass")
  VITREA_SITTING_DIR="$ROOT" W42_EVIDENCE="$EV" PYTHONDONTWRITEBYTECODE=1 \
    python3.12 "$SITTING/collect-pass.py" "$name"
  for run in "$pass"/run-* "$pass"/QUARANTINE-run-*; do
    [ -d "$run" ] || continue
    out="$EV/attest/$name/$(basename "$run")"
    [ -f "$run/driver-idle.log" ] && cp -p "$run/driver-idle.log" "$out/driver-idle.txt"
    [ -f "$run/producer-capture.err" ] && cp -p "$run/producer-capture.err" "$out/producer-capture.err"
  done
done
for f in orchestrator-status.txt orchestrator-console.txt pin-check.json; do
  cp -p "$ROOT/logs/$f" "$EV/logs/"
done
cp -p "$ROOT"/logs/*-display-*.txt "$EV/logs/"
PYTHONDONTWRITEBYTECODE=1 python3.12 - "$EV" <<'PY'
import datetime, json, subprocess, sys
cmd = ['sqlite3', '-readonly', '-json', '/Library/Application Support/com.apple.TCC/TCC.db',
       "select service,client,auth_value,last_modified from access where client like '%vitrea%';"]
r = subprocess.run(cmd, capture_output=True, text=True)
open(f'{sys.argv[1]}/tcc-at-collect.json', 'w').write(json.dumps(dict(
    at=datetime.datetime.now(datetime.timezone.utc).isoformat(), command=cmd, exitCode=r.returncode,
    stdout=r.stdout, stderr=r.stderr), indent=2) + '\n')
PY
find "$EV" -type f | sort
