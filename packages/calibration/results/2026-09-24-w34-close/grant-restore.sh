#!/bin/bash
# W34 wave close, Decision Log 4: the original bundle's grant positively checked after the user
# re-added it, then the side bundle re-checked. Scratch only; nothing under the repository.
set -u
REPO=/Users/new/Developer/GitHub/designer
E=$REPO/packages/calibration/results/2026-09-23-w34-g0-contour-bed
SPEC=$HOME/vitrea-w34/scratch/grant-before/scenes.json
idle() { ioreg -c IOHIDSystem | awk '/HIDIdleTime/ {print int($NF/1000000000); exit}'; }
waitidle() { while [ "$(idle)" -lt 75 ]; do sleep 5; done; echo "idle $(idle)s at $(date -u +%FT%TZ)"; }
check() { # name app harness label
  local name=$1 app=$2 harness=$3 label=$4 root=$HOME/vitrea-w34/scratch/$1
  mkdir -p "$root"; cp "$SPEC" "$root/scenes.json"
  export VITREA_SCALE=2 VITREA_SCENES=$root/scenes.json VITREA_FIXTURES=$root
  waitidle
  python3 "$E/record-machine.py" "$label-open" > "$root/attest.open.json"
  "$harness" backgrounds > "$root/backgrounds.log" 2>&1 || { echo "$name: backgrounds failed"; }
  open -W --env VITREA_SCALE=2 --env VITREA_SCENES="$root/scenes.json" --env VITREA_FIXTURES="$root" \
    --stdout "$root/capture.out" --stderr "$root/capture.err" "$app" --args capture \
    --run-label "$label" --reset-interstitial 6 --min-idle-seconds 60 --initial-settle 1.75 \
    --scenes checkerboard__capsule-button__rest
  python3 "$E/record-machine.py" "$label-close" > "$root/attest.close.json"
  if [ -f "$root/manifest.json" ]; then
    python3 -c "
import json;m=json.load(open('$root/manifest.json'));f=m['profiles'][0]['fixtures'][0]
print('$name: CAPTURED materialRendered=%s presentedActive=%s deterministic=%s repeatNoise=%s'%(f['materialRendered'],f.get('presentedActive'),f.get('deterministic'),f.get('repeatNoise')))"
  else
    echo "$name: NO MANIFEST"; grep -m2 -i "3801\|TCC\|Screen Recording\|denied\|error" "$root/capture.err" | cut -c1-160
  fi
}
check grant-restore-original "$REPO/apps/reference-apple/build/VitreaReference.app" "$REPO/apps/reference-apple/build/harness" w34-close-grant-restore-original-1
check grant-restore-side "$HOME/vitrea-w34/side/VitreaReference.app" "$HOME/vitrea-w34/side/harness" w34-close-grant-restore-side-1
echo DONE
