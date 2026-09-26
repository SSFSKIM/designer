#!/bin/bash
# Operator stop (W39 G1): Google Chrome was launched at 03:45:37Z during active-1x run 1 and is
# frontmost. Let run 1 finish and be judged by its own gates; interrupt THIS worker's own sitting
# driver (pid given) the moment run 1's admission is written, before run 2 launches, so the
# driver's own handler quarantines whatever run 2 had begun. Nothing else is signalled.
PID=$1; D=/Users/new/vitrea-w39/run/active-1x
LOG=/Users/new/vitrea-w39/run/logs/operator-stop.txt
echo "$(date -u +%FT%T.%NZ) armed: driver pid $PID" >> $LOG
while kill -0 $PID 2>/dev/null; do
  if [ -f $D/run-1/admission.json ] || ls -d $D/QUARANTINE-run-1-* >/dev/null 2>&1; then
    kill -INT $PID
    echo "$(date -u +%FT%T.%NZ) SIGINT sent to driver $PID; run-1 admission present: $([ -f $D/run-1/admission.json ] && echo yes || echo no)" >> $LOG
    ls -la $D >> $LOG
    exit 0
  fi
  sleep 0.1
done
echo "$(date -u +%FT%T.%NZ) driver exited on its own before run 1 was judged" >> $LOG
