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
# Environment: VITREA_SITTING_DIR (required; outside every checkout), optionally
# W42_EVIDENCE (a directory the attestations of each pass are copied into by
# collect-pass.py) and W42_EVIDENCE_REPO (a checkout whose W42_EVIDENCE is committed after
# each pass, adding that directory only).
set -uo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
: "${VITREA_SITTING_DIR:?VITREA_SITTING_DIR must name the sitting root}"
L=$VITREA_SITTING_DIR/logs
mkdir -p "$L"
ST=$L/orchestrator-status.txt
SCREEN=7709FD0F-F423-4277-B0C8-7CA94F85723A
DP=${DISPLAYPLACER:-/opt/homebrew/bin/displayplacer}
say() { echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) $*" | tee -a "$ST"; }
mode() { $DP list | sed -n 's/^  mode \([0-9]*\):.*<-- current mode$/\1/p'; }
setmode() {
  [ "$(mode)" = "$1" ] && return 0
  python3.12 "$HERE/sitting.py" wait-idle 300 >> "$L/mode-switch-idle.txt" 2>&1 || return 1
  $DP "id:$SCREEN mode:$1"; sleep 6
  say "display -> mode $(mode)"
  [ "$(mode)" = "$1" ]
}
restore() { [ "$(mode)" = 68 ] || { $DP "id:$SCREEN mode:68"; sleep 6; }; say "restore: display mode $(mode)"; }
trap restore EXIT
started=${START_AT:+no}
started=${started:-yes}
while read -r name kind key want runs; do
  first=1
  if [ "$started" = no ]; then
    [ "$name" = "$START_AT" ] || continue
    started=yes; first=${FIRST_RUN:-1}
  fi
  setmode "$want" || { say "STOP $name: display mode $want did not take"; exit 2; }
  $DP list > "$L/$name-display-before.txt" 2>&1
  say "START $name ($kind, runs $first..$runs) at mode $want"
  case $kind in
    dump) bash "$HERE/run-sitting-w42.sh" dump "$key" >> "$L/$name-driver.txt" 2>&1 ;;
    sentinel) bash "$HERE/run-sitting-w42.sh" capture "$key" "$first" --sentinel >> "$L/$name-driver.txt" 2>&1 ;;
    bed) bash "$HERE/run-sitting-w42.sh" capture "$key" "$first" >> "$L/$name-driver.txt" 2>&1 ;;
  esac
  rc=$?
  $DP list > "$L/$name-display-after.txt" 2>&1
  if [ -n "${W42_EVIDENCE:-}" ]; then
    python3.12 "$HERE/collect-pass.py" "$name" >> "$ST" 2>&1
    if [ -n "${W42_EVIDENCE_REPO:-}" ]; then
      git -C "$W42_EVIDENCE_REPO" add -- "$W42_EVIDENCE" && git -C "$W42_EVIDENCE_REPO" commit -q -m "W42 G1: $name $([ $rc = 0 ] && echo admitted || echo "STOPPED (driver exit $rc)")

The pass's attestations, admissions, dump checks and driver log as they stand; manifests,
capture logs and PNGs stay under the raw root until the archive producer files them.
Charter clause 4, G1." -- "$W42_EVIDENCE"
    fi
  fi
  if [ $rc -ne 0 ]; then say "STOP $name: driver exit $rc"; exit 3; fi
  say "DONE $name"
done < <(python3.12 "$HERE/pass-spec.py" order)
[ "$started" = yes ] || { say "STOP: START_AT=$START_AT names no pass"; exit 4; }
say "ALL PASSES DONE"
