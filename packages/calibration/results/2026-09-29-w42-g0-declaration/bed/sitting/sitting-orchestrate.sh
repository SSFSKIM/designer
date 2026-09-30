#!/bin/bash
# W42 G1: the whole sitting in its one declared order (pass-spec.py `order`): the dump step
# for the 2x endpoints (mode 68) and the 1x endpoints (mode 69), then the four 2x passes and
# their sentinels (mode 68), then the four 1x passes and theirs (mode 69); the display is
# restored to mode 68 on every exit path. Derived from W39 G1's tools/sitting-orchestrate.sh.
#
# One driver invocation per pass (all its runs). The driver waits for >= 75 s of HID idle
# before EVERY run and judges every gate itself; this script only switches the display, and
# a switch waits for >= 300 s of HID idle first (memo D's run-1x.sh rule). ANY failure — a
# mode that does not take, a refusal, a quarantine, a dump departure — stops the sitting
# here. Nothing is retried. A continuation is the operator's explicit act: START_AT=<pass>
# FIRST_RUN=<n> resumes at that pass, beginning with run n (the driver refuses an existing
# run-N and any out-of-order pass, whatever this script is told).
#
# The fixes of the bed review of b151aff4:
# - B-M1: before any launch, `sitting.py pin-check` must accept the bed as the pinned, hashed
#   declaration; a refusal launches nothing.
# - b3: the pass list is computed first, its status checked, and read on fd 3; every driver
#   gets </dev/null, so no child can swallow the remaining passes; the last pass of the
#   selection must be the last one reached, or the sitting reports a STOP.
# - b4: the script detaches itself into its own session (nohup + setsid) unless
#   W42_FOREGROUND=1, so a torn-down agent or terminal session cannot orphan it mid-mode; the
#   EXIT trap (reached from HUP, INT and TERM too) restores mode 68 and verifies it. Every
#   launch runs under it (the driver refuses one without W42_ORCHESTRATED), the rehearsals
#   included: REHEARSAL=1 PASSES="<pass> ..." runs each named pass as its rehearsal, at its
#   display mode (a dump pass as `dump --rehearse`, a bed pass as the TCC-refusal rehearsal).
# - b5: STOP_AFTER=dumps ends the sitting after the dump step (no grant is needed for it);
#   the continuation is START_AT=2x-light-active.
#
# The verification round (53400aa5, finding 3): bash runs a trap only once its FOREGROUND child
# returns, and a driver runs a whole multi-run pass, so a SIGTERM used to leave mode 69 on
# while captures went on. The driver and the idle wait now run as tracked background jobs under
# an interruptible `wait`; on HUP, INT or TERM the orchestrator sends the driver SIGTERM (it
# kills its launch, ends the native app and quarantines the run), KILLs it and its children if
# it has not gone in 20 s, ends any native app still running by its binary path, and only then
# exits, so the EXIT trap restores mode 68 and verifies it.
#
# Environment: VITREA_SITTING_DIR (required; outside every checkout), optionally
# W42_EVIDENCE (a directory the attestations of each pass are copied into by
# collect-pass.py) and W42_EVIDENCE_REPO (a checkout whose W42_EVIDENCE is committed after
# each pass, adding that directory only). W42_PREDECLARATION=1 is for rehearsals before the
# declaration is hashed (the driver launches nothing else under it).
set -uo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
: "${VITREA_SITTING_DIR:?VITREA_SITTING_DIR must name the sitting root}"
L=$VITREA_SITTING_DIR/logs
mkdir -p "$L"
ST=$L/orchestrator-status.txt
say() { echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) $*" | tee -a "$ST"; }

if [ "${W42_FOREGROUND:-0}" != 1 ] && [ -z "${W42_DETACHED:-}" ]; then
  W42_DETACHED=1 nohup python3.12 -c 'import os, sys; os.setsid(); os.execvp(sys.argv[1], sys.argv[1:])' \
    bash "$HERE/sitting-orchestrate.sh" </dev/null >>"$L/orchestrator-console.txt" 2>&1 &
  echo "$!" > "$L/orchestrator.pid"
  echo "sitting-orchestrate: detached as pid $! in its own session; follow $ST"
  exit 0
fi

SCREEN=7709FD0F-F423-4277-B0C8-7CA94F85723A
DP=${DISPLAYPLACER:-/opt/homebrew/bin/displayplacer}
export W42_ORCHESTRATED=1
PIN_FILE=$HERE/../../../2026-09-26-w39-g0-colour-edge-bed/bundle-pin.json
APP=${VITREA_APP:-$(python3.12 -c 'import json, sys; print(json.load(open(sys.argv[1]))["path"])' "$PIN_FILE")}
NATIVE=$(cd "$APP" 2>/dev/null && pwd -P || echo "$APP")/Contents/MacOS/VitreaReference
CHILD=""
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
  if pkill -f "$NATIVE" 2>/dev/null; then say "CANCEL: a native launch was still running; terminated"; fi
  say "CANCEL: done; restoring the display"
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
restore() {
  local rc=$? now
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
say "orchestrator pid $$ (process group $(ps -o pgid= -p $$ | tr -d ' ')) REHEARSAL=${REHEARSAL:-0}" \
  "STOP_AFTER=${STOP_AFTER:-} START_AT=${START_AT:-} PASSES=${PASSES:-} W42_PREDECLARATION=${W42_PREDECLARATION:-0}"

if ! python3.12 "$HERE/sitting.py" pin-check > "$L/pin-check.json" 2>&1 </dev/null; then
  say "STOP: the bed is not the pinned declaration ($L/pin-check.json); nothing launched"
  exit 5
fi
say "pin-check: $(python3.12 -c 'import json, sys; d = json.load(open(sys.argv[1])); print("scenes", d["scenesSha256"][:12], "bed", d["splitSha256"][:12], "predeclaration" if d.get("predeclaration") else "declared")' "$L/pin-check.json")"

ORDER=$(python3.12 "$HERE/pass-spec.py" order </dev/null)
rc=$?
if [ $rc -ne 0 ] || [ -z "$ORDER" ]; then say "STOP: pass-spec.py order failed (exit $rc) or is empty; nothing launched"; exit 6; fi
case "${STOP_AFTER:-}" in ''|dumps) ;; *) say "STOP: STOP_AFTER=$STOP_AFTER is not a declared stop (dumps)"; exit 6 ;; esac
if [ "${REHEARSAL:-0}" = 1 ]; then
  [ -n "${PASSES:-}" ] || { say "STOP: REHEARSAL=1 needs PASSES"; exit 6; }
  [ -z "${START_AT:-}" ] || { say "STOP: a rehearsal has no continuation (START_AT)"; exit 6; }
elif [ -n "${PASSES:-}" ]; then
  say "STOP: PASSES selects rehearsals only; the sitting runs its one order"; exit 6
fi
SELECTED=""
started=${START_AT:+no}
started=${started:-yes}
while read -r name kind key want runs; do
  if [ "${STOP_AFTER:-}" = dumps ] && [ "$kind" != dump ]; then break; fi
  if [ "${REHEARSAL:-0}" = 1 ]; then
    case " $PASSES " in *" $name "*) ;; *) continue ;; esac
    [ "$kind" != sentinel ] || { say "STOP: a sentinel pass has no rehearsal ($name)"; exit 6; }
  elif [ "$started" = no ]; then
    [ "$name" = "$START_AT" ] || continue
    started=yes
  fi
  SELECTED+="$name $kind $key $want $runs"$'\n'
done <<< "$ORDER"
[ "$started" = yes ] || { say "STOP: START_AT=$START_AT names no pass"; exit 4; }
if [ "${REHEARSAL:-0}" = 1 ]; then
  for asked in $PASSES; do
    grep -q "^$asked " <<< "$SELECTED" || { say "STOP: PASSES names $asked, which this selection lacks"; exit 4; }
  done
fi
[ -n "$SELECTED" ] || { say "STOP: the selection is empty"; exit 4; }
LAST=$(printf '%s' "$SELECTED" | tail -n 1 | cut -d' ' -f1)
say "selection: $(printf '%s' "$SELECTED" | cut -d' ' -f1 | tr '\n' ' ')(last $LAST)"

reached=""
first_pass=yes
while read -r -u 3 name kind key want runs; do
  [ -n "$name" ] || continue
  first=1
  if [ "$first_pass" = yes ] && [ -n "${START_AT:-}" ]; then first=${FIRST_RUN:-1}; fi
  first_pass=no
  setmode "$want" || { say "STOP $name: display mode $want did not take"; exit 2; }
  $DP list > "$L/$name-display-before.txt" 2>&1
  D=(bash "$HERE/run-sitting-w42.sh")
  if [ "${REHEARSAL:-0}" = 1 ]; then
    say "START rehearsal $name ($kind) at mode $want"
    case $kind in
      dump) D+=(dump "$key" --rehearse) ;;
      bed) D+=(capture "$key" --rehearse-refusal) ;;
    esac
  else
    say "START $name ($kind, runs $first..$runs) at mode $want"
    case $kind in
      dump) D+=(dump "$key") ;;
      sentinel) D+=(capture "$key" "$first" --sentinel) ;;
      bed) D+=(capture "$key" "$first") ;;
    esac
  fi
  job "$L/$name-driver.txt" "${D[@]}"
  rc=$?
  $DP list > "$L/$name-display-after.txt" 2>&1
  if [ "${REHEARSAL:-0}" != 1 ] && [ -n "${W42_EVIDENCE:-}" ]; then
    python3.12 "$HERE/collect-pass.py" "$name" >> "$ST" 2>&1 </dev/null 3<&-
    if [ -n "${W42_EVIDENCE_REPO:-}" ]; then
      git -C "$W42_EVIDENCE_REPO" add -- "$W42_EVIDENCE" && git -C "$W42_EVIDENCE_REPO" commit -q -m "W42 G1: $name $([ $rc = 0 ] && echo admitted || echo "STOPPED (driver exit $rc)")

The pass's attestations, admissions, dump checks and driver log as they stand; manifests,
capture logs and PNGs stay under the raw root until the archive producer files them.
Charter clause 4, G1." -- "$W42_EVIDENCE"
    fi
  fi
  if [ $rc -ne 0 ]; then say "STOP $name: driver exit $rc"; exit 3; fi
  say "DONE $name"
  reached=$name
done 3<<< "$SELECTED"
[ "$reached" = "$LAST" ] || { say "STOP: the pass list ended at '${reached:-nothing}', not at $LAST"; exit 4; }
if [ "${REHEARSAL:-0}" = 1 ]; then say "REHEARSALS DONE ($LAST)"
elif [ "${STOP_AFTER:-}" = dumps ]; then say "DUMPS DONE: stopped after $LAST (STOP_AFTER=dumps); continue with START_AT=2x-light-active"
else say "ALL PASSES DONE"; fi
