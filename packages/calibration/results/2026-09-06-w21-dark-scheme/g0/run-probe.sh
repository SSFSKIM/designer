#!/bin/bash
# W21 G0 — the native dark probe, by W9's protocol (claims §5.30), in W19/W20 G0's shape.
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
# grant is keyed to that bundle identity, and the tracker's second entry is why `capture.sh probe`
# is never used from a shell. The scene bed and the fixtures directory come in through the two env
# overrides the whole pipeline honours, as `open --env` rather than `launchctl setenv`, so nothing
# canonical is read or written on either side. The one profile in the W21 bed is dark, so the
# harness switches the system appearance itself; nothing here has to.
#
# `--allow-colourless-tints` is passed, deliberately, for the reason W12's stability study passed it
# (claims §5.21): the author tint reaching the material is INTERMITTENT on this machine (§5.10,
# §5.20 — two runs minutes apart on the same binary, one carrying colour and one not), and the
# guard's default is to delete the whole staged bundle when it fires. On this probe that would throw
# away 51 attested untinted cells to protect five descriptive ones. With the flag the bed publishes,
# the caveat is recorded in the manifest, and every fixture carries its own
# `tint.colourReachedMaterial`, so a tint row is believable exactly when that flag says it is. W21's
# tinted cells are descriptive (the dark tint pathway is a stop, not a fit), so nothing binding rests
# on them; a run whose tints dropped out is still a full-strength run for everything this probe is
# for.
#
# Usage: `bash run-probe.sh <runRoot> <firstRun> <lastRun>`
set -u
T="${1:?usage: run-probe.sh <runRoot> <firstRun> <lastRun>}"
FIRST="${2:?}"
LAST="${3:?}"
MIN_FIRST_RUN_ATTESTED="${MIN_FIRST_RUN_ATTESTED:-50}"

# The pre-flight the 2026-09-06 loss paid for (findings §4d). A locked screen is invisible to every
# signal the protocol already checks: the session reads on-console and logged in, HID idle reads in
# the thousands of seconds, and ScreenCaptureKit answers OK — while `loginwindow` is the front
# application and no window can be made key, so every cell records the material's flat inactive
# appearance and fails `presentedActive`. Two hours of runs were spent discovering that. The console
# session states the flag directly, so the probe asks before it starts and refuses in a second.
if ioreg -n Root -d1 2>/dev/null | grep -q '"CGSSessionScreenIsLocked"=Yes'; then
  echo "REFUSED: the screen is locked (CGSSessionScreenIsLocked=Yes) — the harness cannot make its"
  echo "window key, so every cell would fail presentedActive. Unlock the console session and re-run."
  exit 5
fi

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKTREE="$(cd "$HERE/../../../../.." && pwd)"
SCENES="$WORKTREE/apps/reference-apple/scenes-w21-probe.json"
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
      --args capture --run-label "w21-probe-$N" --reset-interstitial 6 --min-idle-seconds 45 \
      --allow-colourless-tints
    if [ -f "$D/manifest.json" ]; then echo "run $N: complete $(date -u +%H:%M:%SZ)"; break; fi
    if grep -q -i "idle" "$D.err" "$D.out" 2>/dev/null; then
      echo "run $N attempt $A: refused for idle"; sleep 90; continue
    fi
    echo "run $N attempt $A: FAILED"; tail -8 "$D.err" "$D.out"; exit 3
  done
  [ -f "$D/manifest.json" ] || { echo "run $N: gave up"; exit 4; }

  # The first run is also the budget's own pre-flight. A run that attests nearly every cell is a
  # session that will keep attesting; a run that does not is a session state the protocol cannot
  # see, and spending nine more runs on it buys nothing. The threshold is deliberately loose — the
  # tracker's known activation loss costs a handful of cells per run and is survivable, while the
  # failure this guards against costs all of them.
  ATTESTED=$(python3 -c '
import json, sys
m = json.load(open(sys.argv[1]))
f = m["profiles"][0]["fixtures"]
ok = [x for x in f if x["presentedActive"] and x["deterministic"] and x["materialRendered"]]
print(f"{len(ok)} {len(f)}")' "$D/manifest.json")
  echo "run $N: attested $ATTESTED"
  if [ "$N" = "$FIRST" ]; then
    set -- $ATTESTED
    if [ "$1" -lt "$MIN_FIRST_RUN_ATTESTED" ]; then
      echo "STOPPING: run $N attested $1 of $2, below the $MIN_FIRST_RUN_ATTESTED the budget is"
      echo "worth spending. Report the session state rather than the remaining runs."
      exit 6
    fi
  fi
done
echo "PROBE RUNS DONE $(date -u +%H:%M:%SZ)"
