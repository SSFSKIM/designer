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
APP="$REPO/apps/reference-apple/build/VitreaReference.app"
HARNESS="$REPO/apps/reference-apple/build/harness"
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
    open -W --env VITREA_SCALE="$SCALE" --env VITREA_FIXTURES="$D" \
      --stdout "$D.out" --stderr "$D.err" "$APP" \
      --args capture ${POSE_ARG} ${DRY_ARG} \
      --run-label "w27-26.5-$MODE-${SCALE}x-$N" \
      --reset-interstitial 6 --min-idle-seconds 45 --scenes "$SCENES"
    [ "${DRY:-0}" = "1" ] && { grep -c "dry-run" "$D.out" | sed 's/^/  cells presented: /'; break; }
    if [ -f "$D/manifest.json" ]; then echo "run $N: complete $(date -u +%H:%M:%SZ)"; break; fi
    if grep -q -i "idle" "$D.err" "$D.out" 2>/dev/null; then
      echo "run $N attempt $A: refused for idle — leave the machine alone"; sleep 90; continue
    fi
    echo "run $N attempt $A: FAILED"; tail -12 "$D.err" "$D.out"; exit 3
  done
  [ "${DRY:-0}" = "1" ] && continue
  [ -f "$D/manifest.json" ] || { echo "run $N: gave up"; exit 4; }

  # The attestation audit, per run. For an inactive pass `presentedActive` is
  # FALSE on every cell by design, so the active bed's audit line would read this
  # bed as a total failure; what is checked instead is the inversion claims
  # §5.134 §5 asks for — the pose observed, and both halves of it false.
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
    echo "STOPPING: run $N attested $1 of $2. A cell that did not attest its pose is not"
    echo "evidence; report the session state rather than spending the remaining runs."
    exit 6
  fi
done
echo "PASS $MODE ${SCALE}x DONE $(date -u +%H:%M:%SZ)"
