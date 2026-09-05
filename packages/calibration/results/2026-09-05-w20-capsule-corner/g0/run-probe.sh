#!/bin/bash
# W20 G0 — the native corner probe, by W9's protocol (claims §5.30), in W19 G0's shape.
#
# One run is a whole snapshot of the profile directory plus its own manifest, taken before anything
# is decided; `cli/materialize.ts` then publishes the majority byte-state per cell across the
# attested runs. A run that fails its own attestation — HID activity during it, a cell captured with
# the window not key, a cell that did not settle — is disqualified and replaced, and the
# disqualification is recorded in `provenance.json` rather than quietly dropped. The tracker's entry
# "The reference harness loses cells to window activation with the machine idle" is why the run
# budget is generous: a probe banks about seven attested runs in ten.
#
# The app is launched from the MAIN checkout's bundle, not from this worktree: the Screen Recording
# grant is keyed to that bundle identity. The scene bed and the fixtures directory come in through
# the two env overrides the whole pipeline honours, as `open --env` rather than `launchctl setenv`,
# so nothing canonical is read or written on either side.
#
# Usage: `bash run-probe.sh <runRoot> <firstRun> <lastRun>`
set -u
T="${1:?usage: run-probe.sh <runRoot> <firstRun> <lastRun>}"
FIRST="${2:?}"
LAST="${3:?}"

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKTREE="$(cd "$HERE/../../../../.." && pwd)"
SCENES="$WORKTREE/apps/reference-apple/scenes-w20-probe.json"
APP=/Users/new/developer/github/designer/apps/reference-apple/build/VitreaReference.app
HARNESS=/Users/new/developer/github/designer/apps/reference-apple/build/harness
mkdir -p "$T"

for N in $(seq "$FIRST" "$LAST"); do
  D="$T/run-$N"
  mkdir -p "$D"
  echo "run $N: backgrounds $(date -u +%H:%M:%SZ)"
  VITREA_SCENES="$SCENES" VITREA_FIXTURES="$D" "$HARNESS" backgrounds > "$D.backgrounds.out" 2>&1 \
    || { echo "run $N: backgrounds FAILED"; tail -5 "$D.backgrounds.out"; exit 2; }
  for A in $(seq 1 40); do
    echo "run $N attempt $A: capture $(date -u +%H:%M:%SZ)"
    rm -f "$D.out" "$D.err"
    open -W --env VITREA_SCENES="$SCENES" --env VITREA_FIXTURES="$D" \
      --stdout "$D.out" --stderr "$D.err" "$APP" \
      --args capture --run-label "w20-probe-$N" --reset-interstitial 6 --min-idle-seconds 45
    if [ -f "$D/manifest.json" ]; then echo "run $N: complete $(date -u +%H:%M:%SZ)"; break; fi
    if grep -q -i "idle" "$D.err" "$D.out" 2>/dev/null; then
      echo "run $N attempt $A: refused for idle"; sleep 90; continue
    fi
    echo "run $N attempt $A: FAILED"; tail -8 "$D.err" "$D.out"; exit 3
  done
  [ -f "$D/manifest.json" ] || { echo "run $N: gave up"; exit 4; }
done
echo "PROBE RUNS DONE $(date -u +%H:%M:%SZ)"
