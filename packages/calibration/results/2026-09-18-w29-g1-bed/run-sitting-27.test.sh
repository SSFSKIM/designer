#!/bin/bash
# Regression test for run-sitting-27.sh's refusals and control flow, harness stubbed.
#
# The script it tests drives an unrepeatable session, and most of its refusals are
# otherwise reachable only by putting the capture machine into the state each one
# refuses: Reduce Transparency, Increase Contrast and Show Borders need a hand in
# System Settings, the display mode needs the screen switched, and the OS build
# needs a different operating system. None of those can be exercised in the
# rehearsal the runbook asks for — a `DRY=1` pass proves the refusals do not fire
# when the machine is RIGHT, and this proves they do fire when it is wrong, which
# is the half a rehearsal on a correctly-configured machine cannot reach.
#
# The W27 sitting shipped two defects that needed no display to find (a pre-flight
# that refused every active pass, and a `grep` under `set -e` that killed the
# healthy path); its `run-sitting.test.sh` is this file's parent and rows 7–12
# below are its rows, carried over because the audit and quarantine are unchanged.
# Nothing here opens a window or captures anything.
set -uo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO="$(cd "$HERE/../../../.." && pwd)"
SCRIPT="$HERE/run-sitting-27.sh"
CANONICAL="$REPO/apps/reference-apple/scenes.json"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
fails=0
ok()   { echo "  ok   $1"; }
bad()  { echo "  FAIL $1"; fails=$((fails + 1)); }

# ---------------------------------------------------------------------------
# The stubs. Four machine readers plus the harness and the launcher, each driven
# by an environment variable so one row can move one axis and leave the rest of
# the machine correct — which is what makes a failing row name its own cause.
# ---------------------------------------------------------------------------
cat > "$TMP/sw_vers" <<'SW'
#!/bin/bash
case "$1" in
  -productVersion) echo "${STUB_OS_VERSION:-27.0}";;
  -buildVersion)   echo "${STUB_OS_BUILD:-26A428}";;
esac
SW

cat > "$TMP/defaults" <<'DEF'
#!/bin/bash
# `defaults read` of a missing key exits 1 with nothing on stdout; STUB_*_ABSENT
# reproduces that, because "absent" and "0" are different readings and the script
# treats them differently for the slider.
case "$*" in
  *NSGlassTintAmount*)   [ "${STUB_GLASS_ABSENT:-0}" = "1" ] && exit 1; echo "${STUB_GLASS:-0.5}";;
  *reduceTransparency*)  [ "${STUB_RT_ABSENT:-0}" = "1" ] && exit 1; echo "${STUB_RT:-0}";;
  *increaseContrast*)    echo "${STUB_IC:-0}";;
  *ButtonShapesEnabled*) echo "${STUB_BORDERS:-0}";;
  *) exit 1;;
esac
DEF

cat > "$TMP/displayplacer" <<'DP'
#!/bin/bash
[ "${STUB_NO_MODE:-0}" = "1" ] && { echo "Persistent screen id: X"; exit 0; }
echo "Persistent screen id: 7709FD0F-F423-4277-B0C8-7CA94F85723A"
echo "  mode 67: res:2560x1440 hz:60 color_depth:4"
echo "  mode ${STUB_DISPLAY_MODE:-68}: res:2560x1440 hz:60 color_depth:4 scaling:on <-- current mode"
DP

# The shared-GPU guard's reader, stubbed to find nothing. The real guard is
# correct and the rows below that launch a non-dry pass would otherwise be refused
# whenever a genuine capture is in progress — which is exactly when someone would
# want to run this file.
cat > "$TMP/pgrep" <<'PG'
#!/bin/bash
exit 1
PG

cat > "$TMP/vtool" <<'VT'
#!/bin/bash
[ "${STUB_VTOOL_BLIND:-0}" = "1" ] && exit 1
echo "$2:"
echo "Load command 11"
echo "      cmd LC_BUILD_VERSION"
echo " platform MACOS"
echo "    minos 26.0"
echo "      sdk 26.0"
VT

# The harness stub. `rehearse-tints` exits with $STUB_REHEARSAL; `backgrounds`
# records the specification it was handed, which is how row 6 proves the DERIVED
# spec reached it rather than the canonical one.
cat > "$TMP/harness" <<'STUB'
#!/bin/bash
case "$1" in
  backgrounds)
    mkdir -p "$VITREA_FIXTURES/backgrounds"
    printf '%s\n' "${VITREA_SCENES:-}" > "$VITREA_FIXTURES/background-scenes"
    echo "backgrounds"
    exit 0;;
  rehearse-tints) echo "rehearse $*"; exit "${STUB_REHEARSAL:-0}";;
esac
exit 0
STUB

# The launcher stub mimics `open -W`: it parses --env/--stdout/--stderr/--args.
cat > "$TMP/launcher" <<'LAUNCH'
#!/bin/bash
# `open` does not propagate an arbitrary caller environment into the app. Drop
# the inherited value so only an explicit `--env VITREA_SCENES=...` reaches it.
unset VITREA_SCENES
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
  for i in $(seq 1 "$n"); do echo "  [$i/$n] stub dry-run"; done
  [ "${STUB_WOULD_REFUSE:-0}" = "1" ] && echo "WOULD REFUSE: stubbed"
} > "$out" 2>"$err"
if [ "$dry" = "0" ]; then
  mkdir -p "$VITREA_FIXTURES"
  printf '%s\n' "${VITREA_SCENES:-}" > "$VITREA_FIXTURES/launcher-scenes"
  cp "${STUB_MANIFEST:?}" "$VITREA_FIXTURES/manifest.json"
fi
exit 0
LAUNCH
chmod +x "$TMP"/sw_vers "$TMP"/defaults "$TMP"/displayplacer "$TMP"/vtool "$TMP"/pgrep \
         "$TMP"/harness "$TMP"/launcher

# A stand-in for the granted bundle: the script reads its binary's hash, its
# cdhash and its LC_BUILD_VERSION, so the path has to exist and be executable.
mkdir -p "$TMP/Stub.app/Contents/MacOS"
printf '#!/bin/bash\nexit 0\n' > "$TMP/Stub.app/Contents/MacOS/VitreaReference"
chmod +x "$TMP/Stub.app/Contents/MacOS/VitreaReference"

run() {
  local dir="$1"; shift
  VITREA_HARNESS="$TMP/harness" VITREA_LAUNCHER="$TMP/launcher" \
  VITREA_APP="$TMP/Stub.app" VITREA_SITTING_DIR="$dir" \
  VITREA_SW_VERS="$TMP/sw_vers" VITREA_DEFAULTS="$TMP/defaults" \
  VITREA_DISPLAYPLACER="$TMP/displayplacer" VITREA_VTOOL="$TMP/vtool" \
  VITREA_PGREP="$TMP/pgrep" \
  "$SCRIPT" "$@" 2>&1
}
# Every refusal row runs DRY, so a row that FAILED to refuse captures nothing.
dry() { DRY=1 run "$@"; }

echo "== run-sitting-27.sh =="

# 1. The version gate inverts. The W27 script refused anything that was not
#    26.5*; this bed is 27.0 evidence and a 26.x or 27.1 pass filed under these
#    keys is the mistake no later read could undo.
out="$(STUB_OS_VERSION=26.5.2 dry "$TMP/v1" active 2)"
grep -q "is not 27.0" <<<"$out" && ok "refuses an OS that is not 27.0" \
                                || bad "ran on a non-27.0 OS: $out"

# 2. The build is named as well as the version, because a 27.1 point update is a
#    different material and a Decision Log entry rather than a continuation.
out="$(STUB_OS_BUILD=26B100 dry "$TMP/v2" active 2)"
grep -q "26B100 is not the declared 26A428" <<<"$out" \
  && ok "refuses an undeclared 27 build" || bad "accepted build 26B100: $out"

# 3. The slider. Decision Log 3 (a) captures this bed at 0.5; the machine's
#    as-found 0.5459057 is a recorded reading and it moved every probe cell
#    beyond its own spread, so it is a refusal and not a rounding.
out="$(STUB_GLASS=0.5459057 dry "$TMP/v3" active 2)"
grep -q "NSGlassTintAmount reads '0.5459057'" <<<"$out" \
  && ok "refuses the machine's as-found slider position" || bad "accepted 0.5459057: $out"
#    And an ABSENT key is refused too, though the material renders at 0.5 without
#    one: a position inferred from an absence is not an attestation.
out="$(STUB_GLASS_ABSENT=1 dry "$TMP/v3b" active 2)"
grep -q "NSGlassTintAmount reads 'absent'" <<<"$out" \
  && ok "refuses an absent slider key rather than assuming the default" \
  || bad "accepted an absent slider key: $out"

# 4. The accessibility mode is part of the pass's identity. The refusal is on the
#    machine's MODE by the harness's own rule (contrast first, because macOS
#    force-couples transparency with it), so this gate asks exactly the question
#    the harness will ask when it selects profiles.
out="$(STUB_RT=1 dry "$TMP/v4" active 1)"
grep -q "declares accessibility mode 'standard' and the machine is in 'reduced-transparency'" <<<"$out" \
  && ok "refuses a standard pass on a reduced-transparency machine" \
  || bad "ran a standard pass with RT on: $out"
out="$(STUB_IC=1 STUB_RT=1 dry "$TMP/v4b" active 1 reduced-transparency)"
grep -q "and the machine is in 'increased-contrast'" <<<"$out" \
  && ok "reads the coupled state as increased-contrast, as the harness does" \
  || bad "mis-read the coupled a11y state: $out"
out="$(STUB_IC=1 STUB_RT=0 STUB_DISPLAY_MODE=69 dry "$TMP/v4c" active 1 increased-contrast)"
grep -q "cells presented:" <<<"$out" \
  && ok "runs the increased-contrast pass on a contrast-only machine" \
  || bad "refused a correct increased-contrast pass: $out"
out="$(STUB_IC=1 STUB_RT=1 STUB_DISPLAY_MODE=69 dry "$TMP/v4c2" active 1 increased-contrast-coupled)"
grep -q "cells presented:" <<<"$out" \
  && ok "runs the coupled pass on a machine with both toggles on" \
  || bad "refused a correct coupled increased-contrast pass: $out"

# 4b. The two increased-contrast states, since macOS 27 decoupled the toggles
#     (W29 Decision Log 4 (b); claims §5.152). The machine's MODE reads
#     `increased-contrast` in both, so the gate above cannot separate them and
#     the second toggle is read on its own. Each pass refuses the other's state:
#     a run in the wrong one, filed under either key, is the confound §5.151 §9
#     records — a toggle read as a material change.
#
#     The row above USED to assert that a COUPLED machine ran the plain
#     increased-contrast pass, which was right while the coupled state was the
#     only one macOS could be in. That state is the one the six-pass sitting of
#     2026-09-18 did not capture, and the reversal is the point.
out="$(STUB_IC=1 STUB_RT=1 dry "$TMP/v4d" active 1 increased-contrast)"
grep -q "declares increased contrast ALONE and Reduce transparency reads '1'" <<<"$out" \
  && ok "refuses the decoupled pass on a coupled machine" \
  || bad "filed a coupled machine under the decoupled bed's key: $out"
out="$(STUB_IC=1 STUB_RT=0 dry "$TMP/v4e" active 1 increased-contrast-coupled)"
grep -q "declares the COUPLED increased-contrast state and Reduce transparency reads 0" <<<"$out" \
  && ok "refuses the coupled pass on a contrast-only machine" \
  || bad "filed a decoupled machine under the coupled key: $out"
out="$(STUB_IC=0 STUB_RT=1 dry "$TMP/v4f" active 1 increased-contrast-coupled)"
grep -q "and the machine is in 'reduced-transparency'" <<<"$out" \
  && ok "refuses the coupled pass with contrast off" \
  || bad "ran a coupled pass with contrast off: $out"

# 5. Show Borders, the axis macOS 27 decoupled from Increase Contrast. Off in
#    every run of this bed; the key is the one the user's toggle revealed.
out="$(STUB_BORDERS=1 dry "$TMP/v5" active 2)"
grep -q "Show Borders (com.apple.Accessibility ButtonShapesEnabled) reads '1'" <<<"$out" \
  && ok "refuses with Show Borders on" || bad "ran with Show Borders on: $out"

# 6. The display's mode, before the pass. The harness SKIPS a profile whose key
#    states another scale, so a pass at the wrong mode does not mislabel a
#    fixture — it captures the other scale's profiles into this pass's directory.
out="$(STUB_DISPLAY_MODE=69 dry "$TMP/v6" active 2)"
grep -q "the display is at mode 69 and a 2x pass needs mode 68" <<<"$out" \
  && ok "refuses a 2x pass at the 1x display mode" || bad "ran 2x at mode 69: $out"
out="$(STUB_DISPLAY_MODE=68 dry "$TMP/v6b" active 1)"
grep -q "the display is at mode 68 and a 1x pass needs mode 69" <<<"$out" \
  && ok "refuses a 1x pass at the 2x display mode" || bad "ran 1x at mode 68: $out"
out="$(STUB_NO_MODE=1 dry "$TMP/v6c" active 2)"
grep -q "displayplacer reported no current mode" <<<"$out" \
  && ok "refuses when the virtual display cannot be read" || bad "ran with no display mode: $out"

# 7. The linked-SDK record. X2 asks for the capturing bundle's SDK from the
#    BINARY, and a field that cannot be read is refused rather than guessed.
out="$(STUB_VTOOL_BLIND=1 dry "$TMP/v7" active 2)"
grep -q "vtool read no LC_BUILD_VERSION" <<<"$out" \
  && ok "refuses when the binary's LC_BUILD_VERSION cannot be read" \
  || bad "recorded an unread linked SDK: $out"

# 8. A correct machine rehearses, presents every cell of the pass, and records
#    both attestation reads. The counts here are the `--scenes` **id** counts —
#    96 active and 72 inactive across the standard profiles, 10 and 22 for
#    increased contrast — because the launcher stub echoes one line per id. The
#    real harness echoes one per profile × scene, so a real rehearsal of a
#    standard pass prints 162 and 119 (plan.md's declared-cell column). What this
#    row pins is that the script derived and passed the right id list, which is
#    the part that belongs to the script.
for spec in "active 2 standard 96" "inactive 2 standard 72" \
            "active 1 increased-contrast 10" "inactive 1 reduced-transparency 21" \
            "active 1 increased-contrast-coupled 10" \
            "inactive 1 increased-contrast-coupled 22"; do
  set -- $spec
  pose="$1"; scale="$2"; mode="$3"; want="$4"
  # The stubs read their environment, and `run` is a shell function, so the
  # per-row state is exported here rather than prefixed to the call.
  STUB_DISPLAY_MODE=68; STUB_IC=0; STUB_RT=0
  [ "$scale" = "1" ] && STUB_DISPLAY_MODE=69
  # The two contrast states, which differ in the second toggle and in nothing
  # else. The coupled rows carry the same 10 and 22 ids as the decoupled pass —
  # the profile declares the 26.5 increased-contrast list verbatim — so what they
  # pin is that the derived specification put the OTHER profile in front of the
  # bundle, which row 11 reads out of the file itself.
  [ "$mode" = "increased-contrast" ] && STUB_IC=1
  [ "$mode" = "increased-contrast-coupled" ] && { STUB_IC=1; STUB_RT=1; }
  [ "$mode" = "reduced-transparency" ] && STUB_RT=1
  export STUB_DISPLAY_MODE STUB_IC STUB_RT
  out="$(dry "$TMP/p-$pose-$scale-$mode" "$pose" "$scale" "$mode")"
  n="$(sed -n 's/.*cells presented: //p' <<<"$out")"
  d="$TMP/p-$pose-$scale-$mode/$mode-$pose-${scale}x/run-1"
  if [ "${n:-0}" != "$want" ]; then bad "$mode $pose ${scale}x presented ${n:-0} ids, not $want"
  elif [ ! -f "$d/attest.read" ]; then bad "$mode $pose ${scale}x wrote no opening attestation"
  elif [ ! -f "$d/attest.close" ]; then bad "$mode $pose ${scale}x wrote no closing attestation"
  elif ! grep -q "^glassTintAmount=0.5$" "$d/attest.read"; then bad "$mode $pose ${scale}x did not record the slider"
  elif ! grep -q "^bundleRecordedSdk=26.0$" "$d/attest.read"; then bad "$mode $pose ${scale}x did not record the linked SDK"
  elif ! grep -q "^showBorders=0$" "$d/attest.read"; then bad "$mode $pose ${scale}x did not record Show Borders"
  else ok "$mode $pose ${scale}x rehearses $n ids and attests"; fi
done
unset STUB_DISPLAY_MODE STUB_IC STUB_RT

# 9. A dry run WITH something to report surfaces it to the terminal AND still
#    reaches every cell — the `grep`-under-`set -e` regression, where finding
#    nothing to warn about killed the script, and its mirror, where finding
#    something truncated the count.
out="$(STUB_WOULD_REFUSE=1 dry "$TMP/s9" inactive 2)"
n="$(sed -n 's/.*cells presented: //p' <<<"$out")"
if ! grep -q "WOULD REFUSE" <<<"$out"; then bad "dry run buried its warning in a log"
elif [ "${n:-0}" != "72" ]; then bad "a warning truncated the rehearsal to ${n:-0} cells"
else ok "dry run surfaces WOULD REFUSE and still reaches all $n ids"; fi

# 10. An ACTIVE pass must not consult the inactive tint rehearsal; an INACTIVE
#     pass still refuses when it refuses. W27's shipped defect was the first half.
out="$(STUB_REHEARSAL=8 run "$TMP/s10" active 2 standard 1 1)"; code=$?
if [ "$code" = "9" ]; then bad "active pass gated on the inactive rehearsal (exit 9)"
elif grep -q "rehearse" <<<"$out"; then bad "active pass ran rehearse-tints"
else ok "active pass does not run the inactive rehearsal"; fi
out="$(STUB_REHEARSAL=8 run "$TMP/s11" inactive 2 standard 1 1)"; code=$?
[ "$code" = "9" ] && ok "inactive pass refuses on a failing rehearsal" \
                  || bad "inactive pass ignored a failing rehearsal (exit $code)"

# 11. The DERIVED 27-only specification reaches both processes that resolve one —
#     `backgrounds` and the open-launched app, which does not inherit the shell's
#     environment — and it holds the six 27 profiles and none of the 26.5 ones.
#     A pass against the canonical file would select both beds at this scale and
#     spend twice the sitting writing 27 pixels into 26.5-keyed directories.
cat > "$TMP/manifest.json" <<'MJ'
{"schemaVersion":3,"sceneSpecVersion":6,"generatedAt":"x",
 "hardware":{"model":"m","cpu":"c","osVersion":"Version 27.0 (Build 26A428)","osBuild":"26A428","xcodeVersion":"x","sdk":"s"},
 "backgrounds":{},"caveats":[],"split":{"calibration":[],"validation":[],"holdout":[],"recorded":[],"probe":[],"note":"n"},
 "profiles":[{"profileKey":"apple-macos-27.0-2x-light-standard-glass0.5","colorScheme":"light","a11yMode":"standard",
  "display":{"requestedScale":2,"actualBackingScale":2,"pixelSize":[640,400],"colorSpace":"sRGB"},
  "fixtures":[{"sceneId":"a","file":"p/a.png","fixtureSet":"probe","captureMethod":"screencapturekit",
    "materialRendered":true,"width":1,"height":1,"deterministic":true,"repeatNoise":0,
    "presentedActive":true,"capturedAt":"t","hidIdleSeconds":300.0}]}]}
MJ
out="$(STUB_MANIFEST="$TMP/manifest.json" run "$TMP/s12" active 2 standard 1 1)"; code=$?
d="$TMP/s12/standard-active-2x/run-1"
bg="$(cat "$d/background-scenes" 2>/dev/null)"
app="$(cat "$d/launcher-scenes" 2>/dev/null)"
if [ "$code" != "0" ]; then bad "a healthy run exited $code: $out"
elif [ "$bg" != "$TMP/s12/standard-active-2x.scenes-27.json" ]; then bad "backgrounds got '$bg', not the derived spec"
elif [ "$app" != "$TMP/s12/standard-active-2x.scenes-27.json" ]; then bad "the launched app got '$app', not the derived spec"
elif grep -q '"key": "apple-macos-26.5-' "$TMP/s12/standard-active-2x.scenes-27.json"; then bad "the derived spec still declares 26.5 profiles"
elif [ "$(grep -c '"key": "apple-macos-27.0-' "$TMP/s12/standard-active-2x.scenes-27.json")" != "6" ]; then bad "the derived spec does not declare the six 27 profiles"
elif ! grep -q "attested 1 1" <<<"$out"; then bad "a healthy run did not attest: $out"
else ok "the derived 27-only spec reaches both resolvers and carries only the six 27 keys"; fi

# 11b. The coupled pass is offered ONE contrast profile and it is the coupled
#      one. The harness selects on the profile's declared `a11y`, both contrast
#      profiles declare `increased-contrast` — `SystemAccessibility.current`
#      cannot see the second toggle — so if both reached the bundle one pass
#      would capture both keys from one machine state and the second bed would be
#      a copy of the first under a different name. What prevents it is the
#      derived specification carrying exactly one of them, which is read here out
#      of the file the bundle is actually handed.
out="$(STUB_IC=1 STUB_RT=1 STUB_DISPLAY_MODE=69 dry "$TMP/s12c" active 1 increased-contrast-coupled)"
SPEC="$TMP/s12c/increased-contrast-coupled-active-1x.scenes-27.json"
if [ ! -f "$SPEC" ]; then bad "the coupled pass derived no specification: $out"
elif grep -q '"key": "apple-macos-27.0-1x-light-increased-contrast-glass0.5"' "$SPEC"; then
  bad "the coupled pass's spec still declares the decoupled contrast profile"
elif ! grep -q '"key": "apple-macos-27.0-1x-light-increased-contrast-coupled-glass0.5"' "$SPEC"; then
  bad "the coupled pass's spec does not declare the coupled profile"
elif [ "$(grep -c '"a11y": "increased-contrast"' "$SPEC")" != "1" ]; then
  bad "more than one profile in the coupled pass's spec is selectable with contrast on"
else ok "the coupled pass is offered exactly one contrast profile, the coupled one"; fi
#      And the mirror: the ordinary contrast pass still gets the decoupled one.
out="$(STUB_IC=1 STUB_RT=0 STUB_DISPLAY_MODE=69 dry "$TMP/s12d" active 1 increased-contrast)"
SPEC="$TMP/s12d/increased-contrast-active-1x.scenes-27.json"
if grep -q '"key": "apple-macos-27.0-1x-light-increased-contrast-coupled-glass0.5"' "$SPEC"; then
  bad "the decoupled pass's spec declares the coupled profile"
elif ! grep -q '"key": "apple-macos-27.0-1x-light-increased-contrast-glass0.5"' "$SPEC"; then
  bad "the decoupled pass's spec does not declare the decoupled profile"
else ok "the decoupled pass is offered exactly one contrast profile, the decoupled one"; fi

# 11c. And a run that filed under a profile this pass did not declare is
#      quarantined, read out of the manifest the harness itself wrote. The two
#      contrast keys never appear in one derived specification, so this is the
#      run-level statement that a coupled pass's cells are under the coupled key.
sed -e 's/apple-macos-27.0-2x-light-standard-glass0.5/apple-macos-27.0-1x-light-increased-contrast-glass0.5/' \
    -e 's/"actualBackingScale":2/"actualBackingScale":1/' -e 's/"requestedScale":2/"requestedScale":1/' \
  "$TMP/manifest.json" > "$TMP/wrong-contrast.json"
out="$(STUB_MANIFEST="$TMP/wrong-contrast.json" STUB_IC=1 STUB_RT=1 STUB_DISPLAY_MODE=69 \
       run "$TMP/s12e" active 1 increased-contrast-coupled 1 1)"; code=$?
if [ "$code" != "6" ]; then bad "a coupled run filed under the decoupled key exited $code, not 6"
elif ! grep -q "is not a profile this pass declared" <<<"$out"; then
  bad "a run filed under the other contrast profile was banked: $out"
else ok "a coupled run that filed under the decoupled key is quarantined"; fi

# 12. A healthy run banks and the pass resumes over it.
out2="$(STUB_MANIFEST="$TMP/manifest.json" run "$TMP/s12" active 2 standard 1 1)"
grep -q "already banked, skipping" <<<"$out2" && ok "a banked run is skipped on resume" \
  || bad "re-running did not skip a banked run: $out2"

# 13. A run that fails its per-cell audit is quarantined WITH its logs and leaves
#     no manifest.json under the run name — so the documented recovery re-takes
#     it rather than stepping over it, and the record of the failure survives.
sed 's/"presentedActive":true/"presentedActive":false/' "$TMP/manifest.json" > "$TMP/bad-cell.json"
out="$(STUB_MANIFEST="$TMP/bad-cell.json" run "$TMP/s13" active 2 standard 1 1)"; code=$?
Q="$(find "$TMP/s13" -maxdepth 2 -name 'QUARANTINE-run-1-*' -type d 2>/dev/null | head -1)"
if [ "$code" != "6" ]; then bad "a failing audit exited $code, not 6"
elif [ -z "$Q" ]; then bad "a failing audit did not quarantine the run"
elif [ -e "$TMP/s13/standard-active-2x/run-1/manifest.json" ]; then bad "quarantine left a resumable manifest"
elif [ ! -e "$Q/attest.read" ]; then bad "quarantine lost the run's attestation"
elif [ ! -e "$Q/run-1.out" ]; then bad "quarantine left the run's logs behind to be overwritten"
else ok "a failing audit quarantines the run with its logs and attestation"; fi

# 14. The RUN-LEVEL checks, read out of the manifest the harness itself wrote.
#     Each is a thing the pre-flight cannot see: the OS the CAPTURE recorded, the
#     backing scale it MEASURED, and the profile keys it actually filed under.
sed 's/"osBuild":"26A428"/"osBuild":"26B100"/' "$TMP/manifest.json" > "$TMP/bad-build.json"
out="$(STUB_MANIFEST="$TMP/bad-build.json" run "$TMP/s14" active 2 standard 1 1)"; code=$?
if [ "$code" != "6" ]; then bad "a manifest recording another build exited $code, not 6"
elif ! grep -q "manifest osBuild" <<<"$out"; then bad "the manifest's build was not checked: $out"
else ok "a run whose own manifest records another build is quarantined"; fi

sed 's/"actualBackingScale":2/"actualBackingScale":1/' "$TMP/manifest.json" > "$TMP/bad-scale.json"
out="$(STUB_MANIFEST="$TMP/bad-scale.json" run "$TMP/s15" active 2 standard 1 1)"; code=$?
if [ "$code" != "6" ]; then bad "a manifest recording another scale exited $code, not 6"
elif ! grep -q "captured at backingScale" <<<"$out"; then bad "the measured backing scale was not checked: $out"
else ok "a run the harness measured at another scale is quarantined"; fi

sed 's/apple-macos-27.0-2x-light-standard-glass0.5/apple-macos-26.5-2x-light-standard/' \
  "$TMP/manifest.json" > "$TMP/bad-key.json"
out="$(STUB_MANIFEST="$TMP/bad-key.json" run "$TMP/s16" active 2 standard 1 1)"; code=$?
if [ "$code" != "6" ]; then bad "a manifest filed under a 26.5 key exited $code, not 6"
elif ! grep -q "is not a 27 profile key" <<<"$out"; then bad "a 26.5-keyed profile was banked: $out"
else ok "a run that filed under a 26.5 key is quarantined (X1)"; fi

# 15. The closing re-read catches a machine that moved mid-run, and quarantines
#     the run rather than refusing out of the script. Every axis the opening read
#     gates is settable from a shell or a preference pane while a 27-minute run
#     is in progress, and a slider moved mid-run puts cells at two positions
#     under one key. The closing read deliberately does NOT refuse: a
#     `manifest.json` is already on disk by then, and an exit there would leave a
#     drifted run indistinguishable from a banked one.
#
#     The stub moves the slider on its SECOND read of the key, which is the
#     closing one — a counter file, because the stub is a separate process each
#     time and cannot carry state in a variable.
cat > "$TMP/drifting-defaults" <<DEF
#!/bin/bash
case "\$*" in
  *NSGlassTintAmount*)
    n=\$(cat "$TMP/glass-reads" 2>/dev/null || echo 0); echo \$((n + 1)) > "$TMP/glass-reads"
    [ "\$n" = "0" ] && echo 0.5 || echo 0.9;;
  *reduceTransparency*)  echo 0;;
  *increaseContrast*)    echo 0;;
  *ButtonShapesEnabled*) echo 0;;
  *) exit 1;;
esac
DEF
chmod +x "$TMP/drifting-defaults"
out="$(STUB_MANIFEST="$TMP/manifest.json" \
       VITREA_HARNESS="$TMP/harness" VITREA_LAUNCHER="$TMP/launcher" \
       VITREA_APP="$TMP/Stub.app" VITREA_SITTING_DIR="$TMP/s17" \
       VITREA_SW_VERS="$TMP/sw_vers" VITREA_DEFAULTS="$TMP/drifting-defaults" \
       VITREA_DISPLAYPLACER="$TMP/displayplacer" VITREA_VTOOL="$TMP/vtool" \
       VITREA_PGREP="$TMP/pgrep" \
       "$SCRIPT" active 2 standard 1 1 2>&1)"; code=$?
Q="$(find "$TMP/s17" -maxdepth 2 -name 'QUARANTINE-run-1-*' -type d 2>/dev/null | head -1)"
if [ "$code" != "6" ]; then bad "a drifting state was banked (exit $code): $out"
elif ! grep -q "STATE DRIFTED" <<<"$out"; then bad "the drift was not named: $out"
elif [ -z "$Q" ]; then bad "the drifted run was not quarantined"
elif [ ! -e "$Q/attest.close" ]; then bad "the drifted run's closing read did not travel with it"
else ok "a state that moved between the two reads quarantines the run with both reads"; fi

# 16. A pass no profile can serve is refused before the bundle is launched. The
#     two accessibility profiles are 1x light only (W29 Deferred covers dark and
#     2x accessibility), and without this the harness meets the impossible pass
#     mid-launch and fails there — after the attestation, after the backgrounds.
out="$(STUB_IC=1 STUB_RT=1 dry "$TMP/v16" active 2 increased-contrast)"
grep -q "is both a11y mode 'increased-contrast' and 2x" <<<"$out" \
  && ok "refuses an accessibility pass at a scale no profile declares" \
  || bad "let an unservable pass reach the bundle: $out"

echo ""
[ "$fails" = "0" ] && { echo "all ok"; exit 0; } || { echo "$fails failed"; exit 1; }
