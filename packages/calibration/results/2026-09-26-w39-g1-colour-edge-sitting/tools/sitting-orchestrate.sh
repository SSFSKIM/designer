#!/bin/bash
# W39 G1 steps 5: the bed passes then the long-protocol sentinels, strictly in the declared
# order, one sitting-driver invocation per pass (all its runs). Before each pass: set and
# read back the pass's attested display mode, then wait for >= 75 s of HID idle. After each
# pass: read the mode back, copy the attestations into the evidence and commit. ANY failure
# (a mode that does not switch, a driver refusal or quarantine) stops the sitting here; the
# driver never retries and neither does this script. A continuation names its first run in the
# optional fourth field (kind:scale:flag:first), because the driver refuses an existing run-N.
set -uo pipefail
E=/Users/new/vitrea-w39/g1/packages/calibration/results/2026-09-26-w39-g0-colour-edge-bed
G=/Users/new/vitrea-w39/g1
EV=$G/packages/calibration/results/2026-09-26-w39-g1-colour-edge-sitting
L=/Users/new/vitrea-w39/run/logs
ST=$L/orchestrator-status.txt
SCREEN=7709FD0F-F423-4277-B0C8-7CA94F85723A
export VITREA_SITTING_DIR=/Users/new/vitrea-w39/run
say() { echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) $*" | tee -a "$ST"; }
PASSES=${PASSES:-"active:1: active:2: inactive:1: inactive:2: active:1:--sentinel active:2:--sentinel inactive:1:--sentinel inactive:2:--sentinel"}
for spec in $PASSES; do
  IFS=: read -r kind scale flag first <<<"$spec"
  name="$kind-${scale}x"; [ -n "$flag" ] && name="$name-sentinel"
  mode=$([ "$scale" = 1 ] && echo 69 || echo 68)
  /opt/homebrew/bin/displayplacer "id:$SCREEN mode:$mode"; sleep 5
  /opt/homebrew/bin/displayplacer list > "$L/$name-display-before.txt" 2>&1
  if ! grep -q "mode $mode:.*<-- current mode" "$L/$name-display-before.txt"; then
    say "STOP $name: display mode $mode did not take"; exit 2; fi
  say "START $name at mode $mode"
  /Users/new/vitrea-w39/run/setup/when-idle.sh 75 bash "$E/run-sitting-w39.sh" "$kind" "$scale" ${first:+$first} $flag > "$L/$name-driver.txt" 2>&1
  rc=$?
  /opt/homebrew/bin/displayplacer list > "$L/$name-display-after.txt" 2>&1
  python3.12 /Users/new/vitrea-w39/run/setup/collect-pass.py "$name" >> "$ST" 2>&1
  cp "$L/$name-display-before.txt" "$L/$name-display-after.txt" "$EV/attest/$name/" 2>/dev/null
  if [ $rc -ne 0 ]; then
    git -C $G add -A "$EV" && git -C $G commit -q -m "W39 G1: $name STOPPED — the driver refused (exit $rc)

The pass's attestations, driver log and any quarantine are committed as they stand; the
sitting stops here and is not retried in place. Charter G1 step 5; c9a §5.185."
    say "STOP $name: driver exit $rc"; exit 3; fi
  git -C $G add -A "$EV" && git -C $G commit -q -m "W39 G1: $name admitted

Every run admitted by the sitting driver at mode $mode, opening and closing machine reads
agreeing; the display mode read back after the pass. Attestations, driver log and the
distilled run record committed; manifests and capture logs stay producer-only. Charter G1
step 5; c9a §5.185."
  say "DONE $name ($(git -C $G log --oneline -1))"
done
say "ALL PASSES DONE"
