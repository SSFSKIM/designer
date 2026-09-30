#!/bin/bash
# watch.sh <milestone-regex> <limit-seconds>: wait on the detached W42 sitting. Read-only. Only the
# CURRENT orchestrator's status lines count (from its "orchestrator pid <PID>" line on), since a
# continuation appends to the same status file. Exits (one line of reason, then that run's status
# tail) on the milestone, on any terminal or failure line, on a new QUARANTINE directory, on a
# permission prompt, or on the orchestrator process vanishing (pid + start time + command). Every
# poll appends the session read to session-trace.txt, so a lost focus comes with its reads.
R=$HOME/vitrea-w42/g1/run; ST=$R/logs/orchestrator-status.txt; TR=$HOME/vitrea-w42/g1/watch/session-trace.txt
PID=$(cat "$R/logs/orchestrator.pid"); ID=$(ps -o lstart=,command= -p "$PID")
cur() { awk -v p="orchestrator pid $PID " 'index($0,p){f=1} f' "$ST"; }
want=$1; limit=$2; start=$(date +%s); reason=""
nq0=$(find "$R" -maxdepth 2 -name 'QUARANTINE-*' | wc -l)
while :; do
  s=$(~/vitrea-w39/scratch/read-session 2>/dev/null)
  if cur | grep -qE "^[0-9T:Z-]+ (STOP|CANCEL|RESTORE FAILED|ALL PASSES DONE|restore:)"; then reason="terminal line"; break; fi
  if [ -n "$want" ] && cur | grep -qE "$want"; then reason="milestone: $want"; break; fi
  nq=$(find "$R" -maxdepth 2 -name 'QUARANTINE-*' | wc -l)
  if [ "$nq" -gt "$nq0" ]; then reason="new QUARANTINE directory"; break; fi
  if echo "$s" | grep -q universalAccessAuthWarn; then reason="PROMPT on screen"; break; fi
  if [ "$(ps -o lstart=,command= -p "$PID" 2>/dev/null)" != "$ID" ]; then sleep 5
    cur | grep -qE "^[0-9T:Z-]+ (restore:|RESTORE FAILED)" && { reason="terminal line"; break; }
    reason="orchestrator process gone with no terminal line"; break; fi
  [ $(( $(date +%s) - start )) -ge "$limit" ] && { reason="watch limit ${limit}s reached (still running)"; break; }
  sleep 20
done
echo "WATCH EXIT at $(date -u +%FT%TZ): $reason"
cur | tail -n 12 | cut -c1-240
find "$R" -maxdepth 2 -name 'QUARANTINE-*'
