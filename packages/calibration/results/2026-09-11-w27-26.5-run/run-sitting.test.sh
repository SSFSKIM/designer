#!/bin/bash
# Regression test for run-sitting.sh's control flow, with the harness stubbed.
#
# The script it tests drives an unrepeatable session, and its branches are
# otherwise reachable only on the capture machine, in a GUI session, on an
# unlocked screen — which is how two defects shipped: a pre-flight that refused
# every active pass, and a `grep` under `set -e` that killed the healthy path.
# Neither needed a display to find. Nothing here opens a window or captures
# anything; `VITREA_HARNESS` and `VITREA_LAUNCHER` stand in for the harness.
set -uo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SCRIPT="$HERE/run-sitting.sh"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
fails=0
ok()   { echo "  ok   $1"; }
bad()  { echo "  FAIL $1"; fails=$((fails + 1)); }

# The stub. `rehearse-tints` exits with $STUB_REHEARSAL; a capture writes the
# manifest $STUB_MANIFEST describes and echoes one line per requested scene.
cat > "$TMP/harness" <<'STUB'
#!/bin/bash
case "$1" in
  backgrounds) mkdir -p "$VITREA_FIXTURES/backgrounds"; echo "backgrounds"; exit 0;;
  rehearse-tints) echo "rehearse $*"; exit "${STUB_REHEARSAL:-0}";;
esac
exit 0
STUB
chmod +x "$TMP/harness"

# The launcher stub mimics `open -W`: it parses --env/--stdout/--stderr/--args.
cat > "$TMP/launcher" <<'LAUNCH'
#!/bin/bash
out=/dev/null; err=/dev/null; scenes=""; dry=0
while [ $# -gt 0 ]; do
  case "$1" in
    --env) export "${2?}"; shift 2;;
    --stdout) out="$2"; shift 2;;
    --stderr) err="$2"; shift 2;;
    --args) shift; break;;
    -W) shift;;
    *) shift;;
  esac
done
for a in "$@"; do [ "$a" = "--dry-run" ] && dry=1; done
prev=""
for a in "$@"; do [ "$prev" = "--scenes" ] && scenes="$a"; prev="$a"; done
{
  n=$(echo "$scenes" | tr ',' '\n' | grep -c .)
  for i in $(seq 1 "$n"); do echo "  [$i/$n] stub dry-run inactive"; done
  [ "${STUB_WOULD_REFUSE:-0}" = "1" ] && echo "WOULD REFUSE: stubbed"
} > "$out" 2>"$err"
if [ "$dry" = "0" ]; then
  mkdir -p "$VITREA_FIXTURES"
  cp "${STUB_MANIFEST:?}" "$VITREA_FIXTURES/manifest.json"
fi
exit 0
LAUNCH
chmod +x "$TMP/launcher"

run() { VITREA_HARNESS="$TMP/harness" VITREA_LAUNCHER="$TMP/launcher" \
        VITREA_APP=/stub VITREA_SITTING_DIR="$1" "$SCRIPT" "${@:2}" 2>&1; }

echo "== run-sitting.sh =="

# 1. An ACTIVE pass must not consult the inactive rehearsal. The committed bundle
#    holds the recovered inactive bed and none of this bed's active cells, so the
#    active rule reports 27 exempt-by-pose cells and exits non-zero — which says
#    nothing about an active pass and used to refuse every one of them.
out="$(STUB_REHEARSAL=8 run "$TMP/s1" active 2 1 1)"; code=$?
if [ "$code" = "9" ]; then bad "active pass gated on the inactive rehearsal (exit 9)"
elif grep -q "rehearse" <<<"$out"; then bad "active pass ran rehearse-tints"
else ok "active pass does not run the inactive rehearsal"; fi

# 2. An INACTIVE pass still refuses when the rehearsal refuses.
out="$(STUB_REHEARSAL=8 run "$TMP/s2" inactive 2 1 1)"; code=$?
[ "$code" = "9" ] && ok "inactive pass refuses on a failing rehearsal" \
                  || bad "inactive pass ignored a failing rehearsal (exit $code)"

# 3. A clean DRY run reports its count and succeeds — the `grep`-under-`set -e`
#    regression, where finding nothing to warn about killed the script.
out="$(DRY=1 run "$TMP/s3" inactive 2 1 1)"; code=$?
if [ "$code" != "0" ]; then bad "clean dry run exited $code"
elif ! grep -q "cells presented:" <<<"$out"; then bad "clean dry run printed no count"
elif ! grep -q "PASS inactive 2x DONE" <<<"$out"; then bad "clean dry run did not finish"
else ok "clean dry run reports its count and finishes"; fi

# 4. A dry run WITH something to report surfaces it to the terminal.
out="$(DRY=1 STUB_WOULD_REFUSE=1 run "$TMP/s4" inactive 2 1 1)"; code=$?
if [ "$code" != "0" ]; then bad "warning dry run exited $code"
elif ! grep -q "WOULD REFUSE" <<<"$out"; then bad "dry run buried its warning in a log"
else ok "dry run surfaces WOULD REFUSE to the terminal"; fi

# 5. A run that fails its audit is quarantined WITH its logs, and leaves no
#    manifest.json under the run name — so the documented retake re-takes it
#    rather than stepping over it, and the record of the failure survives.
cat > "$TMP/bad-manifest.json" <<'MJ'
{"schemaVersion":3,"sceneSpecVersion":4,"generatedAt":"x","hardware":{"model":"m","cpu":"c","osVersion":"o","osBuild":"b","xcodeVersion":"x","sdk":"s"},
 "backgrounds":{},"caveats":[],"split":{"calibration":[],"validation":[],"holdout":[],"recorded":[],"probe":[],"note":"n"},
 "profiles":[{"profileKey":"p","colorScheme":"light","a11yMode":"standard",
  "display":{"requestedScale":2,"actualBackingScale":2,"pixelSize":[1,1],"colorSpace":"sRGB"},
  "fixtures":[{"sceneId":"a","file":"p/a.png","fixtureSet":"probe","captureMethod":"screencapturekit",
    "materialRendered":true,"width":1,"height":1,"deterministic":true,"repeatNoise":0,
    "presentedActive":false,"capturedAt":"t",
    "presentation":{"declaredPose":"inactive","observedPose":"inactive","isKeyWindow":false,
      "appIsActive":false,"activationPolicy":"accessory","windowCanBecomeKey":false,
      "mechanism":"m","attestedAt":"t"}},
   {"sceneId":"b","file":"p/b.png","fixtureSet":"probe","captureMethod":"screencapturekit",
    "materialRendered":true,"width":1,"height":1,"deterministic":true,"repeatNoise":0,
    "presentedActive":true,"capturedAt":"t",
    "presentation":{"declaredPose":"inactive","observedPose":"active","isKeyWindow":true,
      "appIsActive":true,"activationPolicy":"regular","windowCanBecomeKey":true,
      "mechanism":"m","attestedAt":"t"}}]}]}
MJ
out="$(STUB_MANIFEST="$TMP/bad-manifest.json" run "$TMP/s5" inactive 2 1 1)"; code=$?
Q="$(find "$TMP/s5" -maxdepth 2 -name 'QUARANTINE-run-1-*' -type d 2>/dev/null | head -1)"
if [ "$code" != "6" ]; then bad "a failing audit exited $code, not 6"
elif [ -z "$Q" ]; then bad "a failing audit did not quarantine the run"
elif [ -e "$TMP/s5/inactive-2x/run-1/manifest.json" ]; then bad "quarantine left a resumable manifest"
elif [ ! -e "$Q/manifest.json" ]; then bad "quarantine lost the manifest"
elif [ ! -e "$Q/run-1.out" ]; then bad "quarantine left the run's logs behind to be overwritten"
else ok "a failing audit quarantines the run with its logs and leaves nothing resumable"; fi

# 6. A healthy run banks, and re-running the pass skips it.
cat > "$TMP/good-manifest.json" <<'MJ'
{"schemaVersion":3,"sceneSpecVersion":4,"generatedAt":"x","hardware":{"model":"m","cpu":"c","osVersion":"o","osBuild":"b","xcodeVersion":"x","sdk":"s"},
 "backgrounds":{},"caveats":[],"split":{"calibration":[],"validation":[],"holdout":[],"recorded":[],"probe":[],"note":"n"},
 "profiles":[{"profileKey":"p","colorScheme":"light","a11yMode":"standard",
  "display":{"requestedScale":2,"actualBackingScale":2,"pixelSize":[1,1],"colorSpace":"sRGB"},
  "fixtures":[{"sceneId":"a","file":"p/a.png","fixtureSet":"probe","captureMethod":"screencapturekit",
    "materialRendered":true,"width":1,"height":1,"deterministic":true,"repeatNoise":0,
    "presentedActive":false,"capturedAt":"t",
    "presentation":{"declaredPose":"inactive","observedPose":"inactive","isKeyWindow":false,
      "appIsActive":false,"activationPolicy":"accessory","windowCanBecomeKey":false,
      "mechanism":"m","attestedAt":"t"}}]}]}
MJ
out="$(STUB_MANIFEST="$TMP/good-manifest.json" run "$TMP/s6" inactive 2 1 1)"; code=$?
out2="$(STUB_MANIFEST="$TMP/good-manifest.json" run "$TMP/s6" inactive 2 1 1)"
if [ "$code" != "0" ]; then bad "a healthy run exited $code"
elif ! grep -q "attested 1 1" <<<"$out"; then bad "a healthy run did not attest"
elif ! grep -q "already banked, skipping" <<<"$out2"; then bad "re-running did not skip a banked run"
else ok "a healthy run banks and the pass resumes over it"; fi

echo ""
[ "$fails" = "0" ] && { echo "all ok"; exit 0; } || { echo "$fails failed"; exit 1; }
