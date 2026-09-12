#!/bin/bash
# One pass of the W27c G1b checking bed — claims §5.134 §5, W27 Decision Log 13.
#
#   ./run-sitting.sh <inactive|active> <1|2> [first] [last]
#
# A PASS is one scale, one accessibility mode and one pose; the accessibility mode
# is whatever System Settings is in when the pass starts, because macOS exposes
# reduce-transparency and increase-contrast as read-only environment values and the
# harness refuses to file a fixture whose profile key claims a mode the machine is
# not in. A RUN is one snapshot of that pass, written into its own directory with
# its own manifest. The probe bar is seven runs; `materialize` decides the
# published byte-state per cell across them afterwards.
#
# Set DRY=1 to present and attest every cell without capturing or writing anything.
# That is not a rehearsal of the capture, it is a rehearsal of every refusal: the
# fixture root, the backgrounds, the scene resolution, the presentation and the
# per-cell pose attestation all run exactly as they will in the real pass.
set -euo pipefail

MODE="${1:-}"; SCALE="${2:-}"; FIRST="${3:-1}"; LAST="${4:-7}"
case "$MODE" in inactive|active) ;; *) echo "usage: $0 <inactive|active> <1|2> [first] [last]" >&2; exit 64;; esac
case "$SCALE" in 1|2) ;; *) echo "usage: $0 <inactive|active> <1|2> [first] [last]" >&2; exit 64;; esac

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO="$(cd "$HERE/../../../.." && pwd)"
APP="${VITREA_APP:-$REPO/apps/reference-apple/build/VitreaReference.app}"
# `VITREA_HARNESS` exists for `run-sitting.test.sh`, which stubs it to exercise
# this script's control flow — the pre-flight, the dry branch, the audit and the
# quarantine — without a display, a GUI session or an unlocked screen. Those paths
# are otherwise only reachable on the one machine and in the one state, which is
# how two of them shipped broken.
HARNESS="${VITREA_HARNESS:-$REPO/apps/reference-apple/build/harness}"
SCENES="$(cat "$HERE/bed-$MODE.txt")"
T="${VITREA_SITTING_DIR:-$HOME/vitrea-w27-26.5-run}"

# The version gate, first and unconditional. This bed exists because macOS 27
# ships 2026-09-14 and an updated machine can never produce 26.5 evidence again;
# a pass that ran on 27 and was filed under the 26.5 profile keys would be the one
# mistake this session cannot undo.
OS="$(sw_vers -productVersion)"
case "$OS" in 26.5*) ;; *) echo "REFUSED: macOS $OS is not 26.5. This bed is 26.5 evidence only." >&2; exit 1;; esac

# The shared-GPU guard, on the real pass only. A dry run captures nothing and
# reads no pixels, so blocking it on a concurrent browser suite would only make
# the cheapest check in this runbook the one you cannot run when you want it.
if [ "${DRY:-0}" != "1" ] \
   && pgrep -f 'compare.ts|sweep.ts|capture-web|VitreaReference|playwright' >/dev/null; then
  echo "REFUSED: a capture process is already running (the GPU is shared; one at a time)." >&2
  pgrep -fl 'compare.ts|sweep.ts|capture-web|VitreaReference|playwright' | cut -c1-100 >&2
  exit 7
fi
[ -x "$HARNESS" ] || { echo "REFUSED: no harness at $HARNESS — run apps/reference-apple/build.sh" >&2; exit 1; }

# Built as plain strings rather than arrays: macOS ships bash 3.2, where `set -u`
# treats an empty array's expansion as unbound and takes the whole pass down on the
# first run that happens not to need a flag.
DRY_ARG=""
[ "${DRY:-0}" = "1" ] && DRY_ARG="--dry-run"
POSE_ARG=""
[ "$MODE" = "inactive" ] && POSE_ARG="--inactive"

# The tint attestation is the LAST thing a run does, so a bundle that will fail it
# fails after every cell is captured. It is decidable from bytes already on disk,
# so it is decided here, once, before the pass starts — over the committed bed,
# under the rule this pass's pose will apply.
# Inactive passes only. The rehearsal reads the COMMITTED bundle, which holds the
# recovered inactive bed and none of this bed's active cells — so under the active
# pose's rule it reports the 27 recovered inactive cells the recede exempts and
# exits non-zero, which has nothing to say about an active pass and would refuse
# every one of them before a window opened.
if [ "${DRY:-0}" != "1" ] && [ "$MODE" = "inactive" ]; then
  "$HARNESS" rehearse-tints --pose "$MODE" > "$T-rehearsal.out" 2>&1 || {
    echo "REFUSED: the tint attestation would refuse a $MODE bundle. See $T-rehearsal.out" >&2
    tail -6 "$T-rehearsal.out" >&2
    exit 9
  }
fi

mkdir -p "$T"
echo "pass: $MODE ${SCALE}x runs $FIRST..$LAST  scenes=$(tr ',' '\n' <<<"$SCENES" | wc -l | tr -d ' ')  dry=${DRY:-0}"
echo "sitting dir: $T"

for N in $(seq "$FIRST" "$LAST"); do
  D="$T/$MODE-${SCALE}x/run-$N"
  if [ -e "$D/manifest.json" ]; then echo "run $N: already banked, skipping"; continue; fi
  rm -rf "$D"; mkdir -p "$D"

  # Backgrounds into this run's own root. `capture` composites the raster it
  # renders and RECORDS a path, so it proves the file on disk is the same bytes
  # before it writes a fixture; without this the run refuses.
  echo "run $MODE-${SCALE}x-$N: backgrounds $(date -u +%H:%M:%SZ)"
  VITREA_SCALE="$SCALE" VITREA_FIXTURES="$D" "$HARNESS" backgrounds > "$D.backgrounds.out" 2>&1 \
    || { echo "run $N: backgrounds FAILED"; tail -5 "$D.backgrounds.out"; exit 2; }

  for A in $(seq 1 40); do
    echo "run $MODE-${SCALE}x-$N attempt $A: capture $(date -u +%H:%M:%SZ)"
    rm -f "$D.out" "$D.err"
    # `open`, not the bare binary: Screen Recording is granted per bundle, and the
    # bundle is the identity TCC knows. It does not disturb the pose — an
    # `.accessory` application cannot be activated by being opened, which is
    # measured in claims §5.135 and by `deactivate-probe`.
    ${VITREA_LAUNCHER:-open -W} --env VITREA_SCALE="$SCALE" --env VITREA_FIXTURES="$D" \
      --stdout "$D.out" --stderr "$D.err" "$APP" \
      --args capture ${POSE_ARG} ${DRY_ARG} \
      --run-label "w27-26.5-$MODE-${SCALE}x-$N" \
      --reset-interstitial 6 --min-idle-seconds 45 --scenes "$SCENES"
    if [ "${DRY:-0}" = "1" ]; then
      # Anything the rehearsal REFUSED or would refuse goes to this terminal, not
      # into a log nobody opens. A rehearsal whose only visible output is a count
      # is a rehearsal that cannot warn.
      # `|| true`: grep exits 1 when it finds nothing, which under `set -e` is the
      # HEALTHY path killing the script before it prints the count.
      grep -hE "WOULD REFUSE|^error:" "$D.out" "$D.err" 2>/dev/null | sed 's/^/  /' || true
      grep -c "dry-run" "$D.out" | sed 's/^/  cells presented: /'
      break
    fi
    if [ -f "$D/manifest.json" ]; then echo "run $N: complete $(date -u +%H:%M:%SZ)"; break; fi
    if grep -q -i "idle" "$D.err" "$D.out" 2>/dev/null; then
      echo "run $N attempt $A: refused for idle — leave the machine alone"; sleep 90; continue
    fi
    echo "run $N attempt $A: FAILED"; tail -12 "$D.err" "$D.out"; exit 3
  done
  [ "${DRY:-0}" = "1" ] && continue
  [ -f "$D/manifest.json" ] || { echo "run $N: gave up"; exit 4; }

  # The attestation audit, per run. It requires FOUR things of every cell, not
  # only the pose: `deterministic` (the settle loop converged), `materialRendered`
  # (the capture path can see Liquid Glass at all), and — for an inactive pass —
  # `presentedActive: false` plus a `presentation` block whose `observedPose` is
  # `inactive` with `isKeyWindow` and `appIsActive` both false. For an inactive
  # pass `presentedActive` is false on every cell BY DESIGN, so the active bed's
  # audit line would score a correct inactive bed at zero; this is the inversion
  # claims §5.134 §5 asks for.
  ATTESTED=$(MODE="$MODE" python3 -c '
import json, os, sys
m = json.load(open(sys.argv[1]))
f = [x for p in m["profiles"] for x in p["fixtures"]]
if os.environ["MODE"] == "inactive":
    ok = [x for x in f if x.get("presentedActive") is False and x["deterministic"]
          and x["materialRendered"]
          and (x.get("presentation") or {}).get("observedPose") == "inactive"
          and (x.get("presentation") or {}).get("isKeyWindow") is False
          and (x.get("presentation") or {}).get("appIsActive") is False]
else:
    ok = [x for x in f if x.get("presentedActive") and x["deterministic"] and x["materialRendered"]]
print(f"{len(ok)} {len(f)}")' "$D/manifest.json")
  echo "run $MODE-${SCALE}x-$N: attested $ATTESTED"
  set -- $ATTESTED
  if [ "$1" -lt "$2" ]; then
    # QUARANTINE, not just stop. The run's manifest.json is already on disk, and
    # the resume branch above skips any run that has one — so leaving a failed run
    # in place would make the documented recovery ("re-run the same command") step
    # silently OVER it and hand it to `materialize` as banked evidence. Renaming
    # the directory is what makes the failure survive the recovery.
    Q="$T/$MODE-${SCALE}x/QUARANTINE-run-$N-$(date -u +%Y%m%dT%H%M%SZ)"
    mv "$D" "$Q"
    # The logs travel with it. They are siblings of the run directory, and the
    # documented retake deletes two of them and overwrites the third — so leaving
    # them behind would destroy the per-run record the runbook asks to be
    # committed, for the one run whose record matters most.
    for L in "$D.out" "$D.err" "$D.backgrounds.out"; do
      [ -e "$L" ] && mv "$L" "$Q/$(basename "$L")"
    done
    echo "STOPPING: run $N attested $1 of $2 — it is not evidence."
    echo "Quarantined to $Q (no manifest.json under the run name, so re-running this"
    echo "pass re-takes run $N rather than stepping over it). Keep it: what failed to"
    echo "attest is the finding. Report the session state rather than spending the"
    echo "remaining runs."
    exit 6
  fi
done
echo "PASS $MODE ${SCALE}x DONE $(date -u +%H:%M:%SZ)"
