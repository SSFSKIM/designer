#!/bin/bash
set -u
S=/Users/new/.claude/jobs/5c70e47f/tmp/w25/sitting
R=/Users/new/Developer/GitHub/designer/packages/calibration/results/2026-09-09-w25-thick-span-composite/g1/run-sitting.sh
APP=/Users/new/Developer/GitHub/designer/apps/reference-apple/build/VitreaReference.app
until [ -f "$S/DONE-1x" ]; do sleep 60; done
echo "2x pass done $(date -u +%H:%M:%SZ)"; tail -3 "$S/runs-1x.log"
sleep 30
betterdisplaycli set --name="가상 16:9" --hiDPI=off; echo "hiDPI set off: $?"; sleep 15
echo "hiDPI now: $(betterdisplaycli get --name='가상 16:9' --hiDPI) res: $(betterdisplaycli get --name='가상 16:9' --resolution)"
rm -f "$S/probe1x.out" "$S/probe1x.err"
open -W --stdout "$S/probe1x.out" --stderr "$S/probe1x.err" "$APP" --args probe; sleep 2
grep -h "backingScaleFactor\|ScreenCaptureKit" "$S/probe1x.out" "$S/probe1x.err"
if ! grep -q "backingScaleFactor: 1.0" "$S/probe1x.out" "$S/probe1x.err"; then
  echo "STOP: the display did not come up at 1x; not running the 1x pass"; exit 8
fi
bash "$R" "$S/pass-1x" 1 1 7 > "$S/runs-pass-1x.log" 2>&1; echo "EXIT $?" >> "$S/runs-pass-1x.log"
touch "$S/DONE-pass-1x"; tail -4 "$S/runs-pass-1x.log"
