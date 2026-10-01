#!/bin/bash
# W43: one sitting (W43_SITTING=g1a or g1b) in its one declared order (pass-spec.py `order` over
# the hashed plan). Each pass names its display mode (by scale) and its slider position; this
# script switches the display, writes the slider, and runs one driver call per pass. The display
# is restored to mode 68 AND the slider to its as-found value on every exit path. Derived from
# W42 G0's sitting-orchestrate.sh, which stays untouched.
#
# One driver invocation per pass (all its runs). The driver waits for >= 75 s of HID idle before
# EVERY run, judges every gate itself and watches every launch; this script switches the display
# (a switch waits for >= 300 s of HID idle first, memo D's run-1x.sh rule) and the slider. ANY
# failure (a mode that does not take, a slider write refused, a refusal, a quarantine, a sentinel
# departure, a watchdog trip) stops the sitting here. Nothing is retried. A continuation is the
# operator's explicit act: START_AT=<pass> FIRST_RUN=<n> resumes at that pass, beginning with run
# n (the driver refuses an existing run-N and any out-of-order pass, whatever this script is told).
#
# Kept from W42 (its bed review and verification round): the pin check first; the pass list
# computed first, its status checked and read on fd 3, every child on /dev/null, the last pass of
# the selection asserted; the detach into its own session; tracked background jobs under an
# interruptible wait, so HUP, INT and TERM reach the trap at once.
#
# What W43 changes:
# - THE LAUNCHER CHAIN (W42 G1 stop 4). Before detaching, the launching chain (this shell and
#   its ancestors, pid and start time) is recorded in logs/launcher-chain-<epoch>.json and named
#   in VITREA_LAUNCHER_CHAIN, so the census excludes it though setsid has cut it off from every
#   process that reads the census.
# - THE SLIDER, PER PASS (charter G0 (d), X42). The as-found NSGlassTintAmount is recorded once per
#   sitting root (logs/slider-as-found.json) before anything is written; before each pass whose
#   position differs from the current one, `sitting.py slider-set` writes it, refusing while any
#   harness or dump process is alive, and records the write; the EXIT trap restores the as-found
#   value and reads it back, beside the display mode.
# - UNIVERSAL CONTROL (W42 G1 stops 1 and 2). `record-machine.py universal-control` is read at the
#   start and summarised in the status log: a report for the operator, never a gate, since what it
#   can read does not decide whether input will arrive. The watchdog sees input that does.
# - The native app is ended by its executable image, never by a command-line pattern.
# - STOP_AFTER=<pass> ends the sitting's order after that pass (a sitting cut short drops from the
#   bottom of its own order, X47), but A CUT NEVER DROPS THE CLOSE: the slider is restored to its
#   as-found value and the display to mode 68, and then every `runAfterCut` pass after the cut
#   (the closing W42 sentinel bridges) runs in order, under W43_CUT_AFTER. REHEARSAL=1
#   PASSES="<dump pass> ..." runs dump passes as rehearsals.
# - An opening bridge that disagrees with its references (charter clause 3) ends the driver with
#   status 10; the sitting stops there, before any capture away from 0.5, the run admitted.
#
# Environment: VITREA_SITTING_DIR (required; outside every checkout), W43_SITTING (required),
# optionally W43_EVIDENCE (a directory the attestations of each pass are copied into by
# collect-pass.py) and W43_EVIDENCE_REPO (a checkout whose W43_EVIDENCE is committed after each
# pass, adding that directory only). VITREA_DEFAULTS is the `defaults` seam the suites stub.
set -uo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
: "${VITREA_SITTING_DIR:?VITREA_SITTING_DIR must name the sitting root}"
: "${W43_SITTING:?W43_SITTING must name the sitting (g1a or g1b)}"
L=$VITREA_SITTING_DIR/logs
mkdir -p "$L"
ST=$L/orchestrator-status.txt
say() { echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) $*" | tee -a "$ST"; }

if [ "${W43_FOREGROUND:-0}" != 1 ] && [ -z "${W43_DETACHED:-}" ]; then
  CHAIN="$L/launcher-chain-$(date +%s).json"
  if ! python3.12 "$HERE/record-machine.py" launcher-chain > "$CHAIN" 2>>"$L/orchestrator-console.txt"; then
    echo "sitting-orchestrate: the launcher chain could not be recorded; nothing launched" >&2
    exit 6
  fi
  W43_DETACHED=1 VITREA_LAUNCHER_CHAIN="$CHAIN" nohup python3.12 -c \
    'import os, sys; os.setsid(); os.execvp(sys.argv[1], sys.argv[1:])' \
    bash "$HERE/sitting-orchestrate.sh" </dev/null >>"$L/orchestrator-console.txt" 2>&1 &
  echo "$!" > "$L/orchestrator.pid"
  echo "sitting-orchestrate: detached as pid $! in its own session; launcher chain in $CHAIN; follow $ST"
  exit 0
fi

SCREEN=7709FD0F-F423-4277-B0C8-7CA94F85723A
DP=${DISPLAYPLACER:-/opt/homebrew/bin/displayplacer}
export W43_ORCHESTRATED=1
PIN_FILE=$HERE/../../../2026-09-26-w39-g0-colour-edge-bed/bundle-pin.json
APP=${VITREA_APP:-$(python3.12 -c 'import json, sys; print(json.load(open(sys.argv[1]))["path"])' "$PIN_FILE")}
CHILD=""
GLASS=""          # the slider's current position as this sitting last read or wrote it
SLIDER_RECORDED=no
# A tracked background job and an interruptible wait: a signal reaches its trap at once.
job() {
  local log=$1; shift
  "$@" >> "$log" 2>&1 </dev/null 3<&- &
  CHILD=$!
  say "job pid $CHILD: ${*:2:3}"
  wait "$CHILD"
  local rc=$?
  CHILD=""
  return $rc
}
end_native() {
  python3.12 "$HERE/sitting.py" end-native "$APP" </dev/null 3<&- 2>>"$ST"
}
cancel() {
  trap '' HUP INT TERM
  say "CANCEL: signal $2 received${CHILD:+; stopping pid $CHILD}"
  if [ -n "$CHILD" ] && kill -0 "$CHILD" 2>/dev/null; then
    kill -TERM "$CHILD" 2>/dev/null
    # A driver that has not gone in 20 s is KILLed with its children; `wait` reaps it either way.
    ( sleep 20; pkill -KILL -P "$CHILD"; kill -KILL "$CHILD" ) </dev/null >/dev/null 2>&1 &
    local reaper=$!
    wait "$CHILD" 2>/dev/null
    local status=$?
    pkill -P "$reaper" 2>/dev/null; kill "$reaper" 2>/dev/null
    say "CANCEL: pid $CHILD ended (status $status)"
  fi
  local ended
  ended=$(end_native)
  [ "$ended" = "[]" ] || say "CANCEL: native launches still running were ended: $ended"
  say "CANCEL: done; restoring the slider and the display"
  exit "$1"
}
mode() { $DP list | sed -n 's/^  mode \([0-9]*\):.*<-- current mode$/\1/p'; }
setmode() {
  [ "$(mode)" = "$1" ] && return 0
  job "$L/mode-switch-idle.txt" python3.12 "$HERE/sitting.py" wait-idle 300 || return 1
  $DP "id:$SCREEN mode:$1"; sleep 6
  say "display -> mode $(mode)"
  [ "$(mode)" = "$1" ]
}
setglass() {
  [ "$GLASS" = "$1" ] && return 0
  python3.12 "$HERE/sitting.py" slider-set "$1" >> "$L/slider-set.txt" 2>&1 </dev/null 3<&- || return 1
  GLASS=$1
  say "slider -> $1 (written, read back, no native process alive across it)"
}
restore() {
  local rc=$? now
  if [ "$SLIDER_RECORDED" = yes ]; then
    if python3.12 "$HERE/sitting.py" slider-restore > "$L/slider-restore.txt" 2>&1 </dev/null 3<&-; then
      say "restore: slider $(cat "$L/slider-restore.txt") (verified)"
    else
      say "RESTORE FAILED: slider: $(cat "$L/slider-restore.txt" 2>/dev/null | tail -n 2)"; rc=7
    fi
  fi
  [ "$(mode)" = 68 ] || { $DP "id:$SCREEN mode:68"; sleep 6; }
  now=$(mode)
  if [ "$now" = 68 ]; then say "restore: display mode 68 (verified)"
  else say "RESTORE FAILED: display mode ${now:-unreadable}"; rc=7; fi
  exit $rc
}
trap restore EXIT
trap 'cancel 129 HUP' HUP
trap 'cancel 130 INT' INT
trap 'cancel 143 TERM' TERM
say "orchestrator pid $$ (process group $(ps -o pgid= -p $$ | tr -d ' ')) W43_SITTING=$W43_SITTING" \
  "REHEARSAL=${REHEARSAL:-0} STOP_AFTER=${STOP_AFTER:-} START_AT=${START_AT:-} PASSES=${PASSES:-}" \
  "W43_PREDECLARATION=${W43_PREDECLARATION:-0} launcher chain ${VITREA_LAUNCHER_CHAIN:-none}"

if ! python3.12 "$HERE/sitting.py" pin-check > "$L/pin-check.json" 2>&1 </dev/null; then
  say "STOP: the plan is not the pinned declaration ($L/pin-check.json); nothing launched"
  exit 5
fi
say "pin-check: $(python3.12 -c 'import json, sys; d = json.load(open(sys.argv[1])); print(d["sitting"], "plan", d["planSha256"][:12], "predeclaration" if d.get("predeclaration") else "declared")' "$L/pin-check.json")"

UC="$L/universal-control-$(date +%s).json"
if python3.12 "$HERE/record-machine.py" universal-control > "$UC" 2>&1 </dev/null; then
  say "universal control (a report, not a gate): $(python3.12 -c 'import json, sys; d = json.load(open(sys.argv[1])); print("agent", "running" if d["agentActive"] else "absent", "| input path", "REACHABLE" if d["inputPathReachable"] else "down", "| Disable", d["disableSetting"], "| bluetooth", d["bluetoothControllerState"], "| awdl0", ",".join(d["awdlFlags"] or []))' "$UC")"
else
  say "universal control: the report could not be read ($UC)"
fi

ORDER=$(python3.12 "$HERE/pass-spec.py" order --sitting "$W43_SITTING" </dev/null)
rc=$?
if [ $rc -ne 0 ] || [ -z "$ORDER" ]; then say "STOP: pass-spec.py order failed (exit $rc) or is empty; nothing launched"; exit 6; fi
if [ -n "${STOP_AFTER:-}" ] && ! grep -q "^$STOP_AFTER " <<< "$ORDER"; then
  say "STOP: STOP_AFTER=$STOP_AFTER names no declared pass"; exit 6
fi
if [ "${REHEARSAL:-0}" = 1 ]; then
  [ -n "${PASSES:-}" ] || { say "STOP: REHEARSAL=1 needs PASSES"; exit 6; }
  [ -z "${START_AT:-}" ] || { say "STOP: a rehearsal has no continuation (START_AT)"; exit 6; }
elif [ -n "${PASSES:-}" ]; then
  say "STOP: PASSES selects rehearsals only; the sitting runs its one order"; exit 6
fi
SELECTED=""
started=${START_AT:+no}
started=${started:-yes}
while read -r name kind want runs glass flag; do
  if [ "${REHEARSAL:-0}" = 1 ]; then
    case " $PASSES " in *" $name "*) ;; *) continue ;; esac
    [ "$kind" = dump ] || { say "STOP: only a dump pass has a rehearsal ($name is a $kind pass)"; exit 6; }
  elif [ "$started" = no ]; then
    [ "$name" = "$START_AT" ] || continue
    started=yes
  fi
  SELECTED+="$name $kind $want $runs $glass $flag"$'\n'
  [ "$name" = "${STOP_AFTER:-}" ] && break
done <<< "$ORDER"
[ "$started" = yes ] || { say "STOP: START_AT=$START_AT names no pass"; exit 4; }
if [ "${REHEARSAL:-0}" = 1 ]; then
  for asked in $PASSES; do
    grep -q "^$asked " <<< "$SELECTED" || { say "STOP: PASSES names $asked, which this selection lacks"; exit 4; }
  done
fi
[ -n "$SELECTED" ] || { say "STOP: the selection is empty"; exit 4; }
LAST=$(printf '%s' "$SELECTED" | tail -n 1 | cut -d' ' -f1)
if [ -n "${STOP_AFTER:-}" ] && [ "$LAST" != "$STOP_AFTER" ]; then
  say "STOP: STOP_AFTER=$STOP_AFTER is not in this selection (it precedes START_AT or is not rehearsed)"; exit 6
fi
say "selection: $(printf '%s' "$SELECTED" | cut -d' ' -f1 | tr '\n' ' ')(last $LAST)"

# The as-found slider, recorded before anything is written (once per sitting root: a continuation
# keeps the first record, so the trap restores what the sitting found, not what a crash left).
if ! FOUND=$(python3.12 "$HERE/sitting.py" slider-as-found 2>>"$ST" </dev/null); then
  say "STOP: the as-found slider could not be recorded; nothing written, nothing launched"; exit 8
fi
SLIDER_RECORDED=yes
GLASS=$(python3.12 -c 'import json, sys; c = json.loads(sys.argv[1])["current"]; print(repr(float(c["value"])) if c["present"] else "absent")' "$FOUND")
say "slider: as-found $(python3.12 -c 'import json, sys; print(json.loads(sys.argv[1])["asFound"])' "$FOUND"); now $GLASS"

# One pass: its display mode, its slider position, one driver call, its evidence collected. Any
# failure stops the sitting here (exit), the trap restoring the slider and the display.
run_pass() {
  local name=$1 kind=$2 want=$3 runs=$4 glass=$5 first=$6 rc
  setmode "$want" || { say "STOP $name: display mode $want did not take"; exit 2; }
  setglass "$glass" || { say "STOP $name: the slider write to $glass was refused ($L/slider-set.txt)"; exit 9; }
  $DP list > "$L/$name-display-before.txt" 2>&1
  local D=(bash "$HERE/run-sitting-w43.sh")
  if [ "${REHEARSAL:-0}" = 1 ]; then
    say "START rehearsal $name ($kind) at mode $want, slider $glass"
    D+=(dump "$name" --rehearse)
  else
    say "START $name ($kind, runs $first..$runs) at mode $want, slider $glass${W43_CUT_AFTER:+, after the cut at $W43_CUT_AFTER}"
    case $kind in
      dump) D+=(dump "$name") ;;
      capture) D+=(capture "$name" "$first") ;;
    esac
  fi
  job "$L/$name-driver.txt" "${D[@]}"
  rc=$?
  $DP list > "$L/$name-display-after.txt" 2>&1
  if [ "${REHEARSAL:-0}" != 1 ] && [ -n "${W43_EVIDENCE:-}" ]; then
    python3.12 "$HERE/collect-pass.py" "$name" >> "$ST" 2>&1 </dev/null 3<&-
    if [ -n "${W43_EVIDENCE_REPO:-}" ]; then
      git -C "$W43_EVIDENCE_REPO" add -- "$W43_EVIDENCE" && git -C "$W43_EVIDENCE_REPO" commit -q -m "W43 $W43_SITTING: $name $([ $rc = 0 ] && echo admitted || echo "STOPPED (driver exit $rc)")

The pass's attestations, admissions, sentinel checks, bridge reports, idle-wait and watchdog logs
as they stand; manifests, capture logs, dumps and PNGs stay under the raw root until the archive
producer files them. Charter clause 4." -- "$W43_EVIDENCE"
    fi
  fi
  if [ $rc -eq 10 ]; then
    say "STOP $name: the opening bridge DISAGREES with its references (charter clause 3; $name/run-*/bridge.json);" \
      "nothing away from 0.5 is captured, and the run stands admitted as evidence"
    exit 3
  fi
  if [ $rc -ne 0 ]; then say "STOP $name: driver exit $rc"; exit 3; fi
  say "DONE $name"
  reached=$name
}

reached=""
first_pass=yes
while read -r -u 3 name kind want runs glass flag; do
  [ -n "$name" ] || continue
  first=1
  if [ "$first_pass" = yes ] && [ -n "${START_AT:-}" ]; then first=${FIRST_RUN:-1}; fi
  first_pass=no
  run_pass "$name" "$kind" "$want" "$runs" "$glass" "$first"
done 3<<< "$SELECTED"
[ "$reached" = "$LAST" ] || { say "STOP: the pass list ended at '${reached:-nothing}', not at $LAST"; exit 4; }

# A cut never drops the close (the coordinator's ruling on X47). After a STOP_AFTER cut, the
# slider goes back to its as-found value and the display to mode 68, and then every runAfterCut
# pass after the cut (the closing W42 sentinel bridges) runs in order; the driver lets only those
# past the passes the cut dropped, which can then never be taken later.
AFTER=""
if [ "${REHEARSAL:-0}" != 1 ] && [ -n "${STOP_AFTER:-}" ]; then
  AFTER=$(awk -v cut="$LAST" 'past && $6 == "after-cut" { print } $1 == cut { past = 1 }' <<< "$ORDER")
  DROPPED=$(awk -v cut="$LAST" 'past && $6 != "after-cut" { print $1 } $1 == cut { past = 1 }' <<< "$ORDER" | tr '\n' ' ')
fi
if [ -n "$AFTER" ]; then
  say "CUT after $LAST: dropped ${DROPPED:-nothing}; the closing bridges still run (a cut never drops the close)"
  printf 'cutAfter=%s\ndropped=%s\nafterCut=%s\nat=%s\n' "$LAST" "$DROPPED" \
    "$(cut -d' ' -f1 <<< "$AFTER" | tr '\n' ' ')" "$(date -u +%Y-%m-%dT%H:%M:%SZ)" > "$L/cut-$(date +%s).txt"
  if ! python3.12 "$HERE/sitting.py" slider-restore > "$L/slider-restore-cut.txt" 2>>"$ST" </dev/null 3<&-; then
    say "STOP: the slider did not return to its as-found value before the closing bridges"; exit 7
  fi
  GLASS=$(python3.12 -c 'import json, sys; r = json.loads(sys.argv[1])["read"]; print(repr(float(r["value"])) if r["present"] else "absent")' "$(cat "$L/slider-restore-cut.txt")")
  setmode 68 || { say "STOP: the display did not return to mode 68 before the closing bridges"; exit 2; }
  say "restore before the close: slider $GLASS (as found, verified) and display mode 68 (verified)"
  export W43_CUT_AFTER="$LAST"
  while read -r -u 3 name kind want runs glass flag; do
    [ -n "$name" ] || continue
    run_pass "$name" "$kind" "$want" "$runs" "$glass" 1
  done 3<<< "$AFTER"
  unset W43_CUT_AFTER
fi
if [ "${REHEARSAL:-0}" = 1 ]; then say "REHEARSALS DONE ($LAST)"
elif [ -n "$AFTER" ]; then say "STOPPED AFTER $LAST (STOP_AFTER), then the closing bridges through $reached; the dropped passes are not taken later without a new ruling (X47)"
elif [ -n "${STOP_AFTER:-}" ]; then say "STOPPED AFTER $LAST (STOP_AFTER); continue with START_AT=<the next pass>"
else say "ALL PASSES DONE"; fi
