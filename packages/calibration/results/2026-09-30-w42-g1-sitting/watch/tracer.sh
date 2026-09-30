#!/bin/bash
# tracer.sh: append one read-session line every 20 s to session-trace.txt for as long as the
# CURRENT orchestrator lives (pid + start time + command), then exit. Read-only.
R=$HOME/vitrea-w42/g1/run; TR=$HOME/vitrea-w42/g1/watch/session-trace.txt
PID=$(cat "$R/logs/orchestrator.pid"); ID=$(ps -o lstart=,command= -p "$PID")
echo "$(date -u +%FT%TZ) TRACE START orchestrator pid $PID" >> "$TR"
while [ "$(ps -o lstart=,command= -p "$PID" 2>/dev/null)" = "$ID" ]; do
  echo "$(date -u +%FT%TZ) $(~/vitrea-w39/scratch/read-session 2>/dev/null)" >> "$TR"; sleep 20
done
echo "$(date -u +%FT%TZ) TRACE END orchestrator pid $PID gone" >> "$TR"
