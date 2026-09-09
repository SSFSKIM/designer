#!/bin/bash
# W25 G1 — the sitting: the probe set captured natively by W9's protocol (claims §5.30), in W21 G0's
# runner's shape (`results/2026-09-06-w21-dark-scheme/g0/run-probe.sh`), with the three changes
# `g1/sitting.md` §3 names: no `VITREA_SCENES` (the set is canonical, W25 Decision Log 3 (e)), the
# run label `w25-<scale>-N`, and `VITREA_SCALE` as the scale pass. One run is a whole snapshot —
# both standard profiles at the scale, 158 fixtures — taken before anything is decided;
# `cli/materialize.ts --set probe` then publishes the majority byte-state per cell across the
# attested runs, probe cells only, so the frozen bed's 108 cells in each snapshot are never
# republished.
#
# The app is launched from the MAIN checkout's bundle (the Screen Recording grant is keyed to its
# ad-hoc signature, re-granted after this wave's rebuild), through `open --env` so the GUI session
# sees `VITREA_FIXTURES` and nothing canonical is written. `--allow-colourless-tints` for W21's
# reason: the tint pathway is intermittent on this machine and the guard would otherwise discard a
# whole attested run to protect its few tinted cells.
#
# Usage: `bash run-sitting.sh <runRoot> <scale 1|2> <firstRun> <lastRun>`
set -u
T="${1:?usage: run-sitting.sh <runRoot> <scale> <firstRun> <lastRun>}"
SCALE="${2:?}"
FIRST="${3:?}"
LAST="${4:?}"
# 158 cells per run at this scale; the tracker's activation loss costs a handful, the failure this
# guards against costs all of them.
MIN_FIRST_RUN_ATTESTED="${MIN_FIRST_RUN_ATTESTED:-140}"

if ioreg -n Root -d1 2>/dev/null | grep -q '"CGSSessionScreenIsLocked"=Yes'; then
  echo "REFUSED: the screen is locked (CGSSessionScreenIsLocked=Yes) — the harness cannot make its"
  echo "window key, so every cell would fail presentedActive. Unlock the console session and re-run."
  exit 5
fi
if pgrep -f 'compare.ts|sweep.ts|cost.mjs|capture.mjs|capture-web|VitreaReference|playwright' >/dev/null; then
  echo "REFUSED: a capture process is running (the GPU is shared; one at a time)."; exit 7
fi

APP=/Users/new/Developer/GitHub/designer/apps/reference-apple/build/VitreaReference.app
HARNESS=/Users/new/Developer/GitHub/designer/apps/reference-apple/build/harness
mkdir -p "$T/${SCALE}x"

for N in $(seq "$FIRST" "$LAST"); do
  D="$T/${SCALE}x/run-$N"
  mkdir -p "$D"
  echo "run ${SCALE}x-$N: backgrounds $(date -u +%H:%M:%SZ)"
  VITREA_SCALE="$SCALE" VITREA_FIXTURES="$D" "$HARNESS" backgrounds > "$D.backgrounds.out" 2>&1 \
    || { echo "run $N: backgrounds FAILED"; tail -5 "$D.backgrounds.out"; exit 2; }
  for A in $(seq 1 40); do
    echo "run ${SCALE}x-$N attempt $A: capture $(date -u +%H:%M:%SZ)"
    rm -f "$D.out" "$D.err"
    open -W --env VITREA_SCALE="$SCALE" --env VITREA_FIXTURES="$D" \
      --stdout "$D.out" --stderr "$D.err" "$APP" \
      --args capture --run-label "w25-${SCALE}x-$N" --reset-interstitial 6 --min-idle-seconds 45 \
      --allow-colourless-tints
    if [ -f "$D/manifest.json" ]; then echo "run ${SCALE}x-$N: complete $(date -u +%H:%M:%SZ)"; break; fi
    if grep -q -i "idle" "$D.err" "$D.out" 2>/dev/null; then
      echo "run $N attempt $A: refused for idle"; sleep 90; continue
    fi
    echo "run $N attempt $A: FAILED"; tail -8 "$D.err" "$D.out"; exit 3
  done
  [ -f "$D/manifest.json" ] || { echo "run $N: gave up"; exit 4; }

  # Attestation over every profile in the snapshot (two at each scale), the first run being the
  # budget's own pre-flight.
  ATTESTED=$(python3 -c '
import json, sys
m = json.load(open(sys.argv[1]))
f = [x for p in m["profiles"] for x in p["fixtures"]]
ok = [x for x in f if x["presentedActive"] and x["deterministic"] and x["materialRendered"]]
print(f"{len(ok)} {len(f)}")' "$D/manifest.json")
  echo "run ${SCALE}x-$N: attested $ATTESTED"
  if [ "$N" = "$FIRST" ]; then
    set -- $ATTESTED
    if [ "$1" -lt "$MIN_FIRST_RUN_ATTESTED" ]; then
      echo "STOPPING: run $N attested $1 of $2, below the $MIN_FIRST_RUN_ATTESTED the budget is"
      echo "worth spending. Report the session state rather than the remaining runs."
      exit 6
    fi
  fi
done
echo "SITTING ${SCALE}x RUNS DONE $(date -u +%H:%M:%SZ)"
