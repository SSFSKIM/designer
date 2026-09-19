#!/bin/bash
# One pass of the macOS 27 bed — W29 acceptance clause 2, Decision Log 3, claims §5.150.
#
#   ./run-sitting-27.sh <inactive|active> <1|2> [<a11y mode>] [first] [last]
#
# where <a11y mode> is one of `standard`, `reduced-transparency`,
# `increased-contrast` (contrast alone, which is all macOS 27 gives you by
# turning it on) or `increased-contrast-coupled` (contrast AND reduce
# transparency, the state macOS 26.5 forced — see (8) below).
#
# A PASS is one scale, one accessibility mode and one pose, and all three are
# named on the command line. The W27 script named a pass by pose and scale only
# and took the accessibility mode from whatever System Settings happened to be
# in, which cost that sitting an hour: the two accessibility passes resumed over
# the banked standard runs until they were given their own `VITREA_SITTING_DIR`
# by hand (its RUNBOOK §5). Here the mode is part of the pass's identity, so it
# is part of the run directory's name and part of what the pre-flight refuses on.
# A RUN is one snapshot of that pass in its own directory with its own manifest;
# the bar is seven runs (clause 2, one bar per pass), and `cli/materialize.ts`
# decides the published byte-state per cell across them afterwards.
#
# Set DRY=1 to present and attest every cell without capturing or writing a
# fixture. That is a rehearsal of every REFUSAL rather than of the capture: this
# script's own attestation gates, the fixture root, the backgrounds, the scene
# resolution, the presentation and the per-cell pose attestation all run exactly
# as they will in the real pass. Under DRY a bare `first` rehearses once rather
# than seven identical times, because a rehearsal of the 2x inactive pass costs
# twelve minutes and seven of them say nothing the first did not.
#
# WHAT THIS CARRIES THAT THE W27 SCRIPT DID NOT — every item is an axis macOS 27
# introduced or an assumption G0 measured false (plan.md §"What G1 has to carry"):
#
#   1. The version gate inverts: 26.5 was the thing to protect, 27.0 is the thing
#      to capture, and the build is named as well as the version.
#   2. The appearance slider. `NSGlassTintAmount` moves 10 of 10 probe cells
#      beyond their own run-to-run spread, in both poses, at both scales, in both
#      schemes (claims §5.149 §4), and nothing in the harness reads it. It is read
#      here, refused unless it is the ruled 0.5, and recorded per run.
#   3. Show Borders, which macOS 27 decouples from Increase Contrast. It has no
#      key in `com.apple.universalaccess` and no SDK property; the user's toggle
#      against a 635-domain snapshot found it at `ButtonShapesEnabled` in
#      `com.apple.Accessibility` (W29 Surprises), and that is what is read.
#   4. The capturing bundle's linked SDK, read from the binary with `vtool`
#      rather than from the environment. X2 asks for the binary; the manifest's
#      own `sdk` field is `VITREA_SDK` and reads `unknown` through a pass's launch.
#      It is a RECORD and not a proof: G0 measured that `ld` writes `sdk == minos`
#      on this build path whatever SDK compiled the sources, so the number says
#      which binary captured, not what it was built against.
#   5. The display's mode, before the pass rather than after it. The harness reads
#      the real backing scale and SKIPS a profile whose key states another, so a
#      pass launched at the wrong display mode does not mislabel a fixture — it
#      quietly captures the other scale's profiles into a directory the operator
#      believes holds this scale's. `displayplacer` is read here and refused, and
#      the manifest's own `actualBackingScale` is checked afterwards.
#   6. A closing re-read of every one of those values, diffed against the opening
#      read. The opening read is a gate like the idle gate and covers the instant
#      it ran; the axes it covers are all settable from a shell or a preference
#      pane while a 27-minute run is in progress, and a slider moved mid-run
#      would file cells at two positions under one key.
#   7. A derived, 27-only scene specification. See `pass-spec.py`: the harness
#      selects profiles by accessibility mode and scale and by nothing else, so a
#      pass against the canonical declaration would select both beds'
#      profiles and spend twice the sitting writing 27 pixels into
#      `apple-macos-26.5-…` directories.
#   8. The two increased-contrast states, held apart. macOS 27 decoupled Reduce
#      transparency from Increase Contrast, so `increased-contrast` is contrast
#      ALONE and `increased-contrast-coupled` is the state 26.5 forced — both
#      toggles on — which is the only state comparable with the 26.5 bed like for
#      like (W29 Decision Log 4 (b); claims §5.151 §9, §5.152). The harness cannot
#      tell them apart: `SystemAccessibility.current` answers "is contrast on".
#      Two things separate them here, and neither is advice. The derived
#      specification carries exactly ONE contrast profile, named by the pass, so
#      the bundle is never offered both; and this script refuses unless BOTH
#      toggles read the way the pass's mode declares — contrast alone refuses on a
#      coupled machine as surely as the coupled pass refuses on a decoupled one,
#      because a run in the wrong state filed under either key is exactly the
#      confound the second pass exists to remove.
#
# The per-cell pose attestation audit and its quarantine are the W27 script's,
# unchanged in what they require of a cell, with the run-level checks of (1),
# (5) and the HID-idle report added beside them.
set -euo pipefail

MODE="${1:-}"; SCALE="${2:-}"; A11Y="${3:-standard}"; FIRST="${4:-1}"
usage() {
  echo "usage: $0 <inactive|active> <1|2> [standard|increased-contrast|increased-contrast-coupled|reduced-transparency] [first] [last]" >&2
  exit 64
}
case "$MODE" in inactive|active) ;; *) usage;; esac
case "$SCALE" in 1|2) ;; *) usage;; esac
case "$A11Y" in standard|increased-contrast|increased-contrast-coupled|reduced-transparency) ;; *) usage;; esac
# The pass's mode is a state of the machine; the harness's is a value it can
# read. They are the same string for three of the four modes and differ for the
# fourth, because `SystemAccessibility.current` returns `increased-contrast`
# whenever contrast is on and cannot see the second toggle (SceneViews.swift).
# So the coupled pass declares the mode the harness knows, selects the coupled
# profile through the derived specification, and proves the second toggle in its
# own attestation — WANT_RT below.
MACHINE_A11Y="$A11Y"
CONTRAST_VARIANT=decoupled
# Which Reduce Transparency reading the pass requires, or `any` where the mode
# does not state one. Both contrast passes state one: the whole point of the
# second is that the toggle the 26.5 bed had on is an axis of the bed now.
WANT_RT=any
case "$A11Y" in
  increased-contrast-coupled)
    MACHINE_A11Y=increased-contrast; CONTRAST_VARIANT=coupled; WANT_RT=on;;
  increased-contrast)
    WANT_RT=off;;
esac
# Under DRY a bare `first` means one rehearsal, not seven; a real pass keeps the
# seven-run bar as its default so that omitting the argument cannot under-bank.
if [ -n "${5:-}" ]; then LAST="$5"
elif [ "${DRY:-0}" = "1" ]; then LAST="$FIRST"
else LAST=7; fi

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO="$(cd "$HERE/../../../.." && pwd)"
# The granted bundle, in the MAIN checkout. It holds the wave's one irreplaceable
# Screen Recording grant, it is never rebuilt (X4), and any other bundle added to
# Screen Recording under its identifier EVICTS that grant (W29 Surprises, measured
# 2026-09-18). A worktree does not get its own copy for that reason.
APP="${VITREA_APP:-/Users/new/Developer/GitHub/designer/apps/reference-apple/build/VitreaReference.app}"
BIN="$APP/Contents/MacOS/VitreaReference"
HARNESS="${VITREA_HARNESS:-/Users/new/Developer/GitHub/designer/apps/reference-apple/build/harness}"
# The declaration this pass captures. `VITREA_SCENES` points at the CANONICAL
# file — the worktree's copy, which is where clause 2's 27 profiles are declared;
# the pass runs against the 27-only specification derived from it below. The
# granted bundle was compiled from the main checkout, so its `#filePath`-based
# ROOT cannot see an amended declaration in a worktree: the path is passed
# explicitly to both resolvers, `backgrounds` and the open-launched app.
CANONICAL="${VITREA_SCENES:-$REPO/apps/reference-apple/scenes.json}"
T="${VITREA_SITTING_DIR:-$HOME/vitrea-w29-27-run}"

# Test seams. `run-sitting-27.test.sh` stubs these to exercise the refusals below
# without putting the machine into the state each one refuses — which for Reduce
# Transparency, Increase Contrast and Show Borders means a hand in System
# Settings, and for the display mode means switching the screen. The same reason
# `VITREA_HARNESS` and `VITREA_LAUNCHER` exist in the W27 script.
SW_VERS="${VITREA_SW_VERS:-sw_vers}"
DEFAULTS="${VITREA_DEFAULTS:-defaults}"
VTOOL="${VITREA_VTOOL:-xcrun vtool}"
DISPLAYPLACER="${VITREA_DISPLAYPLACER:-displayplacer}"
# The shared-GPU guard's own reader. A seam because the guard is real and correct
# and would otherwise refuse the test's non-dry rows whenever a genuine capture is
# in progress — turning the one pre-flight that works from anywhere into one that
# needs an idle machine, which is the opposite of what it is for.
PGREP="${VITREA_PGREP:-pgrep}"

# ---------------------------------------------------------------------------
# The declared configuration of this bed. Each constant is a ruling or a reading
# of the machine, cited where it came from; a pass that finds the machine
# somewhere else refuses rather than recording the difference and continuing.
# ---------------------------------------------------------------------------
# The OS this bed IS. The W27 script's gate refused anything that was not 26.5
# because an updated machine could never produce 26.5 evidence again; this one
# refuses anything that is not 27.0 because a 26.x or 27.1 pass filed under these
# keys would be the mistake no later read could undo.
OS_SERIES="27.0"
# Build 26A428 — the build Apple posted as the RC on 2026-09-09 and shipped as
# 27.0, and the build every G0 reading was taken on (machine.json). A point
# update is a different bed and a Decision Log entry, not a silent continuation.
OS_BUILD_DECLARED="26A428"
# Decision Log 3 (a): the bed is captured at the system default, which G0
# measured to be 0.5 — the value the material renders at with the key absent, and
# the knee of both declared ramps (claims §5.149 §4). The machine's as-found
# 0.5459057 is a recorded reading and not a bed, and it is 0.046 off centre,
# which is above the noise bar on all ten probe cells.
GLASS_DECLARED="0.5"
# The BetterDisplay virtual screen `가상 16:9`, persistent id 7709FD0F-…: mode 68
# renders at backingScaleFactor 2.0 and mode 69 at 1.0 (machine.json, and both
# were reached and left during G0). Without this third-party driver there is no
# 1x bed at all — four of the six keys.
MODE_FOR_2X=68
MODE_FOR_1X=69

if [ "$SCALE" = "2" ]; then WANT_DISPLAY_MODE="$MODE_FOR_2X"; else WANT_DISPLAY_MODE="$MODE_FOR_1X"; fi
PASS="$A11Y-$MODE-${SCALE}x"

refuse() { echo "REFUSED: $*" >&2; exit 1; }

# ---------------------------------------------------------------------------
# The attestation read. One function, called at the opening of a run and again at
# its close, writing the same field set both times so the two are diffable.
#
# X2's bar is that an attestation is a read that can REFUSE. Every value here is
# read from the machine or from the binary — never from the environment, and
# never transcribed from a note — and every one of them either matches what this
# pass declares or stops the pass. `vtool`'s SDK figure is the single exception
# and is labelled as a record, for the reason G0 measured (see the header).
#
# The refusals fire on the OPENING read only, and that is not a softening of the
# closing one. By the time the closing read runs, a `manifest.json` is on disk
# and the resume branch skips any run that has one — so a closing read that
# exited here would leave a run whose state moved looking exactly like a banked
# one, and the documented recovery would step over it. The closing read therefore
# records, and the DIFF against the opening read decides; a disagreement on any
# field goes down the same quarantine path a failed cell does. Every field the
# opening read gates is in that diff, so nothing it would have refused can pass.
# ---------------------------------------------------------------------------
read_state() {
  local out="$1" phase="$2"
  local os_version os_build glass rt ic borders machine_a11y display_mode
  os_version="$($SW_VERS -productVersion)"
  os_build="$($SW_VERS -buildVersion)"
  # A missing key is read as its documented default rather than as a failure:
  # `reduceTransparency` and `increaseContrast` are absent from the domain until
  # something has written them, and absent means off. `NSGlassTintAmount` is the
  # opposite case and is NOT defaulted — absent renders at 0.5 (measured), but a
  # bed whose position was inferred from an absence rather than read is a bed
  # nobody can reproduce, so the pass requires the key to be there and to say 0.5.
  rt="$($DEFAULTS read com.apple.universalaccess reduceTransparency 2>/dev/null || echo 0)"
  ic="$($DEFAULTS read com.apple.universalaccess increaseContrast 2>/dev/null || echo 0)"
  borders="$($DEFAULTS read com.apple.Accessibility ButtonShapesEnabled 2>/dev/null || echo 0)"
  glass="$($DEFAULTS read -g NSGlassTintAmount 2>/dev/null || echo absent)"
  # The harness's own selection rule, mirrored: contrast first, because macOS
  # force-enables Reduce Transparency with Increase Contrast and the coupled state
  # is the only increased-contrast state a user can reach (SceneViews.swift,
  # `SystemAccessibility.current`). Refusing on the machine's MODE rather than on
  # the two booleans separately is what makes this gate the same question the
  # harness will ask when it decides which profiles to select.
  if [ "$ic" != "0" ]; then machine_a11y="increased-contrast"
  elif [ "$rt" != "0" ]; then machine_a11y="reduced-transparency"
  else machine_a11y="standard"; fi
  # `|| true` so that `pipefail` cannot turn a displayplacer that errors into a
  # silent exit: an unreadable display mode has a named refusal below and must
  # reach it. Absent the driver there is no 1x bed at all — four of the six keys.
  display_mode="$($DISPLAYPLACER list 2>/dev/null \
    | sed -n 's/^  mode \([0-9]*\):.*<-- current mode$/\1/p' | head -1 || true)"
  {
    echo "phase=$phase"
    echo "pass=$PASS"
    echo "readAt=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
    echo "os=$os_version $os_build"
    echo "osProductVersion=$os_version"
    echo "osBuild=$os_build"
    echo "glassTintAmount=$glass"
    echo "reduceTransparency=$rt"
    echo "increaseContrast=$ic"
    echo "a11yMode=$machine_a11y"
    # The pass's own name for the state, beside the machine's. They differ only
    # for the coupled contrast pass, where the machine's reading cannot express
    # what the key claims, and `materialize` judges the KEY against the two
    # booleans above rather than against this field (src/run-provenance.ts).
    echo "passA11yMode=$A11Y"
    echo "showBorders=$borders"
    echo "displayplacerMode=${display_mode:-unreadable}"
    echo "displayModeDeclaredForScale=$WANT_DISPLAY_MODE"
    echo "bundlePath=$APP"
    echo "bundleCdHash=$BUNDLE_CDHASH"
    echo "bundleBinarySha256=$BUNDLE_SHA"
    echo "bundleMinOS=$BUNDLE_MINOS"
    echo "bundleRecordedSdk=$BUNDLE_SDK"
    echo "bundleRecordedSdkNote=LC_BUILD_VERSION's sdk field; ld writes sdk == minos on this build path, so this identifies the binary and is not a reading of the SDK it compiled against (claims §5.149 §1)"
    echo "sceneSpecCanonicalSha256=$CANONICAL_SHA"
    echo "passSpecSha256=$PASS_SPEC_SHA"
  } > "$out"
  [ "$phase" = "open" ] || return 0

  case "$os_version" in
    "$OS_SERIES"*) ;;
    *) refuse "macOS $os_version is not $OS_SERIES. This bed is $OS_SERIES evidence only.";;
  esac
  [ "$os_build" = "$OS_BUILD_DECLARED" ] \
    || refuse "macOS build $os_build is not the declared $OS_BUILD_DECLARED. A point update is a different bed and a Decision Log entry."
  [ "$glass" = "$GLASS_DECLARED" ] \
    || refuse "NSGlassTintAmount reads '$glass', not the ruled $GLASS_DECLARED. Decision Log 3 (a) captures this bed at the system default; set it with 'defaults write -g NSGlassTintAmount -float $GLASS_DECLARED'."
  [ "$machine_a11y" = "$MACHINE_A11Y" ] \
    || refuse "this pass declares accessibility mode '$A11Y' and the machine is in '$machine_a11y' (reduceTransparency=$rt increaseContrast=$ic). The mode is a read-only system value: set it in System Settings > Accessibility > Display and re-run."
  # And the second toggle, which the machine's MODE cannot carry. On 26.5 it
  # needed no reading: contrast force-enabled transparency reduction and the
  # checkbox could not be uncleared, so contrast-on meant both-on. macOS 27 made
  # them independent, which makes a run's transparency state an axis of the bed —
  # the two contrast passes differ in nothing else, and a run that drifted across
  # this line would be filed under a key that names the other state.
  if [ "$WANT_RT" = "on" ] && [ "$rt" = "0" ]; then
    refuse "this pass declares the COUPLED increased-contrast state and Reduce transparency reads 0. Decision Log 4 (b) captures it with BOTH toggles on, which is the state macOS 26.5 forced and the only one comparable with the 26.5 bed; turn Reduce transparency on in System Settings > Accessibility > Display and re-run."
  fi
  if [ "$WANT_RT" = "off" ] && [ "$rt" != "0" ]; then
    refuse "this pass declares increased contrast ALONE and Reduce transparency reads '$rt'. macOS 27 decouples the two toggles, so a machine with both on is the coupled state: run it as 'increased-contrast-coupled', which files under its own key, rather than filing the coupled state under the decoupled bed's key (claims §5.151 §9)."
  fi
  [ "$borders" = "0" ] \
    || refuse "Show Borders (com.apple.Accessibility ButtonShapesEnabled) reads '$borders', not 0. It is off in every run of this bed and is not an evidence class in this wave."
  [ -n "$display_mode" ] \
    || refuse "displayplacer reported no current mode. Without the BetterDisplay virtual screen there is no 1x bed at all, and the scale a fixture claims cannot be checked before the capture."
  [ "$display_mode" = "$WANT_DISPLAY_MODE" ] \
    || refuse "the display is at mode $display_mode and a ${SCALE}x pass needs mode $WANT_DISPLAY_MODE. Switch it with displayplacer and re-run; the harness would otherwise capture the other scale's profiles into this pass's directory."
}

# ---------------------------------------------------------------------------
# Pre-flight, once per pass.
# ---------------------------------------------------------------------------
# The shared-GPU guard, on the real pass only. A dry run captures nothing and
# reads no pixels, so blocking it on a concurrent browser suite would only make
# the cheapest check in the runbook the one you cannot run when you want it.
if [ "${DRY:-0}" != "1" ] \
   && $PGREP -f 'compare.ts|sweep.ts|capture-web|VitreaReference|playwright' >/dev/null; then
  echo "REFUSED: a capture process is already running (the GPU is shared; one at a time)." >&2
  $PGREP -fl 'compare.ts|sweep.ts|capture-web|VitreaReference|playwright' | cut -c1-100 >&2
  exit 7
fi
[ -x "$HARNESS" ] || refuse "no harness at $HARNESS — this bed captures with the granted bundle, which is never rebuilt (X4)."
[ -x "$BIN" ] || refuse "no binary at $BIN."
[ -f "$CANONICAL" ] || refuse "no scene declaration at $CANONICAL."

# The capturing bundle's identity and its linked-SDK record, read from the binary.
BUNDLE_SHA="$(shasum -a 256 "$BIN" | cut -d' ' -f1)"
# The cdhash is the identity TCC keys the Screen Recording grant on, so it is
# worth recording beside the binary's digest — but it is a RECORD and not a gate:
# the digest already names the binary uniquely, and a pass should not stop because
# `codesign` could not be read. `|| true` because `pipefail` would otherwise make
# an unreadable signature a silent exit rather than the word "unreadable".
BUNDLE_CDHASH="$(codesign -dvvv "$APP" 2>&1 | sed -n 's/^CDHash=//p' | head -1 || true)"
[ -n "$BUNDLE_CDHASH" ] || BUNDLE_CDHASH="unreadable"
VTOOL_OUT="$($VTOOL -show-build-version "$BIN" 2>/dev/null || true)"
BUNDLE_MINOS="$(printf '%s\n' "$VTOOL_OUT" | sed -n 's/^ *minos *//p' | head -1)"
BUNDLE_SDK="$(printf '%s\n' "$VTOOL_OUT" | sed -n 's/^ *sdk *//p' | head -1)"
[ -n "$BUNDLE_MINOS" ] && [ -n "$BUNDLE_SDK" ] \
  || refuse "vtool read no LC_BUILD_VERSION from $BIN. X2 asks for the capturing bundle's linked SDK from the binary, and a field that cannot be read is not recorded as a guess."

mkdir -p "$T"
# The 27-only specification, derived at the opening of every pass from the
# canonical declaration and refused unless that declaration is still the keys the
# bed names — clause 2's six plus Decision Log 4 (b)'s coupled contrast profile —
# each at the ruled slider position, each declaring its 26.5 counterpart's scenes;
# then narrowed to the ONE contrast profile this pass's mode names. See
# `pass-spec.py`.
PASS_SPEC="$T/$PASS.scenes-27.json"
SPEC_READ="$(python3 "$HERE/pass-spec.py" spec "$CANONICAL" "$PASS_SPEC" "$CONTRAST_VARIANT")"
CANONICAL_SHA="$(printf '%s\n' "$SPEC_READ" | sed -n 's/^canonicalSha256=//p')"
PASS_SPEC_SHA="$(printf '%s\n' "$SPEC_READ" | sed -n 's/^passSpecSha256=//p')"
# The profiles this pass could possibly file under — the derived specification's
# own list, read back rather than restated. The run-level audit checks every key
# the harness actually filed against it, which is what catches a contrast pass
# that filed under the other contrast profile: the two never appear in one
# derived specification, so the list is the narrow statement and not a broad one.
PASS_PROFILES="$(printf '%s\n' "$SPEC_READ" | sed -n 's/^profiles=//p')"
# The cells this pass presents, derived from the same document, per pose and per
# accessibility mode. `--scenes` is required rather than optional: the profiles
# declare both poses' states and the harness refuses the whole run if any cell it
# would attempt states the pose this run is not presenting.
SCENES="$(python3 "$HERE/pass-spec.py" ids "$PASS_SPEC" "$MODE" "$MACHINE_A11Y" "$SCALE")"
SCENE_COUNT="$(printf '%s' "$SCENES" | tr ',' '\n' | grep -c . || true)"

# The tint attestation is the LAST thing a run does, so a bundle that will fail it
# fails after every cell is captured. It is decidable from bytes already on disk,
# so it is decided here, once, before the pass starts — over the committed bed,
# under the rule this pass's pose will apply. Inactive passes only: under the
# active pose's rule the committed bundle's recovered inactive cells are reported
# and the rehearsal exits non-zero, which has nothing to say about an active pass
# and would refuse every one of them before a window opened (W27's own defect).
if [ "${DRY:-0}" != "1" ] && [ "$MODE" = "inactive" ]; then
  "$HARNESS" rehearse-tints --pose "$MODE" > "$T/$PASS-rehearsal.out" 2>&1 || {
    echo "REFUSED: the tint attestation would refuse a $MODE bundle. See $T/$PASS-rehearsal.out" >&2
    tail -6 "$T/$PASS-rehearsal.out" >&2
    exit 9
  }
fi

# Built as plain strings rather than arrays: macOS ships bash 3.2, where `set -u`
# treats an empty array's expansion as unbound and takes the whole pass down on
# the first run that happens not to need a flag.
POSE_ARG=""
[ "$MODE" = "inactive" ] && POSE_ARG="--inactive"
DRY_ARG=""
[ "${DRY:-0}" = "1" ] && DRY_ARG="--dry-run"

echo "pass: $PASS runs $FIRST..$LAST  cells=$SCENE_COUNT ids  dry=${DRY:-0}"
echo "sitting dir: $T"
echo "pass spec:   $PASS_SPEC ($PASS_SPEC_SHA)"

for N in $(seq "$FIRST" "$LAST"); do
  D="$T/$PASS/run-$N"
  if [ -e "$D/manifest.json" ]; then echo "run $N: already banked, skipping"; continue; fi
  rm -rf "$D"; mkdir -p "$D"

  # The attestation, BEFORE anything is presented or captured. It writes into the
  # run's own directory, so the record travels with the bytes it describes and a
  # quarantined run keeps its own.
  read_state "$D/attest.read" open

  # Backgrounds into this run's own root. `capture` composites the raster it
  # renders and RECORDS a path, so it proves the file on disk is the same bytes
  # before it writes a fixture; without this the run refuses.
  echo "run $PASS-$N: backgrounds $(date -u +%H:%M:%SZ)"
  VITREA_SCALE="$SCALE" VITREA_FIXTURES="$D" VITREA_SCENES="$PASS_SPEC" \
    "$HARNESS" backgrounds > "$D.backgrounds.out" 2>&1 \
    || { echo "run $N: backgrounds FAILED"; tail -5 "$D.backgrounds.out"; exit 2; }

  for A in $(seq 1 40); do
    echo "run $PASS-$N attempt $A: capture $(date -u +%H:%M:%SZ)"
    rm -f "$D.out" "$D.err"
    # `open`, not the bare binary: Screen Recording is granted per bundle, and the
    # bundle is the identity TCC knows. It does not disturb the pose — an
    # `.accessory` application cannot be activated by being opened, which is
    # measured in claims §5.136 and by `deactivate-probe`.
    ${VITREA_LAUNCHER:-open -W} --env VITREA_SCALE="$SCALE" --env VITREA_FIXTURES="$D" \
      --env VITREA_SCENES="$PASS_SPEC" --stdout "$D.out" --stderr "$D.err" "$APP" \
      --args capture ${POSE_ARG} ${DRY_ARG} \
      --run-label "w29-27-$PASS-$N" \
      --reset-interstitial 6 --min-idle-seconds 45 --scenes "$SCENES"
    if [ "${DRY:-0}" = "1" ]; then
      # Anything the rehearsal REFUSED or would refuse goes to this terminal, not
      # into a log nobody opens. A rehearsal whose only visible output is a count
      # is a rehearsal that cannot warn. `|| true`: grep exits 1 when it finds
      # nothing, which under `set -e` is the HEALTHY path killing the script.
      grep -hE "WOULD REFUSE|^error:" "$D.out" "$D.err" 2>/dev/null | sed 's/^/  /' || true
      grep -c "dry-run" "$D.out" | sed 's/^/  cells presented: /'
      read_state "$D/attest.close" close
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

  # The closing re-read, and the diff. Every axis the opening read gates is
  # settable while a 27-minute run is in progress — the slider from any shell,
  # the accessibility modes and Show Borders from a preference pane, the display
  # mode from displayplacer — so a run whose state moved under it has cells at two
  # configurations under one key, and the fields that name the configuration are
  # compared rather than trusted. `phase` and `readAt` differ by construction.
  read_state "$D/attest.close" close
  DRIFT="$(diff <(grep -v '^phase=\|^readAt=' "$D/attest.read") \
                <(grep -v '^phase=\|^readAt=' "$D/attest.close") || true)"

  # The attestation audit, per run. It requires FOUR things of every cell, not
  # only the pose: `deterministic` (the settle loop converged), `materialRendered`
  # (the capture path can see Liquid Glass at all), and — for an inactive pass —
  # `presentedActive: false` plus a `presentation` block whose `observedPose` is
  # `inactive` with `isKeyWindow` and `appIsActive` both false. For an inactive
  # pass `presentedActive` is false on every cell BY DESIGN, so the active bed's
  # audit line would score a correct inactive bed at zero; this is the inversion
  # claims §5.134 §5 asks for. Beside it, and new here, three run-level checks
  # read out of the manifest the harness itself wrote: the OS and build it
  # records, the backing scale it actually measured, and the HID idle it recorded
  # per cell — the last a REPORT, because the harness gates idle once at a run's
  # opening and records it per cell without refusing, so a touch mid-run files a
  # cell with its idle beside it and `sitting.md` is where that is listed.
  ATTESTED=$(MODE="$MODE" SCALE="$SCALE" OS_SERIES="$OS_SERIES" \
             PASS_PROFILES="$PASS_PROFILES" \
             OS_BUILD_DECLARED="$OS_BUILD_DECLARED" python3 -c '
import json, os, re, sys
m = json.load(open(sys.argv[1]))
mode, want_scale = os.environ["MODE"], float(os.environ["SCALE"])
hw = m.get("hardware") or {}
problems = []
# `osVersion` reads "Version 27.0 (Build 26A428)", so it is parsed rather than
# prefix-matched; `osBuild` is kern.osversion and is compared whole.
series = re.search(r"(\d+)\.(\d+)", hw.get("osVersion", "") or "")
if series is None or ".".join(series.groups()) != os.environ["OS_SERIES"]:
    problems.append("manifest osVersion %r is not %s" % (hw.get("osVersion"), os.environ["OS_SERIES"]))
if hw.get("osBuild") != os.environ["OS_BUILD_DECLARED"]:
    problems.append("manifest osBuild %r is not %s" % (hw.get("osBuild"), os.environ["OS_BUILD_DECLARED"]))
for p in m["profiles"]:
    actual = (p.get("display") or {}).get("actualBackingScale")
    if actual != want_scale:
        problems.append("%s captured at backingScale %r, not %g" % (p["profileKey"], actual, want_scale))
    if not p["profileKey"].startswith("apple-macos-27.0-"):
        problems.append("%s is not a 27 profile key" % p["profileKey"])
    elif p["profileKey"] not in os.environ["PASS_PROFILES"].split(","):
        problems.append("%s is not a profile this pass declared" % p["profileKey"])
f = [x for p in m["profiles"] for x in p["fixtures"]]
if mode == "inactive":
    ok = [x for x in f if x.get("presentedActive") is False and x["deterministic"]
          and x["materialRendered"]
          and (x.get("presentation") or {}).get("observedPose") == "inactive"
          and (x.get("presentation") or {}).get("isKeyWindow") is False
          and (x.get("presentation") or {}).get("appIsActive") is False]
else:
    ok = [x for x in f if x.get("presentedActive") and x["deterministic"] and x["materialRendered"]]
under = [x for x in f if isinstance(x.get("hidIdleSeconds"), (int, float)) and x["hidIdleSeconds"] < 45]
unread = [x for x in f if x.get("hidIdleSeconds") is None]
# Two lines, not one: a problem line carries spaces, and one line word-split by
# the shell would turn a sentence into four fields.
print("%d %d %d %d" % (len(ok), len(f), len(under), len(unread)))
for p in problems:
    print(p)' "$D/manifest.json")
  # Deliberately unquoted: the first line is four numbers and the split IS the parse.
  # shellcheck disable=SC2046
  set -- $(printf '%s\n' "$ATTESTED" | head -1)
  OK="$1"; TOTAL="$2"; UNDER_IDLE="$3"; IDLE_UNREAD="$4"
  PROBLEMS="$(printf '%s\n' "$ATTESTED" | tail -n +2)"
  echo "run $PASS-$N: attested $OK $TOTAL  cells under 45s idle: $UNDER_IDLE  idle unreadable: $IDLE_UNREAD"
  [ -n "$PROBLEMS" ] && { echo "run $PASS-$N: RUN-LEVEL PROBLEMS"; echo "$PROBLEMS" | sed 's/^/    /'; }
  [ -n "$DRIFT" ] && { echo "run $PASS-$N: STATE DRIFTED between the opening and closing read:"; echo "$DRIFT" | sed 's/^/    /'; }
  if [ "$OK" -lt "$TOTAL" ] || [ -n "$PROBLEMS" ] || [ -n "$DRIFT" ]; then
    # QUARANTINE, not just stop. The run's manifest.json is already on disk, and
    # the resume branch above skips any run that has one — so leaving a failed run
    # in place would make the documented recovery ("re-run the same command") step
    # silently OVER it and hand it to `materialize` as banked evidence. Renaming
    # the directory is what makes the failure survive the recovery.
    Q="$T/$PASS/QUARANTINE-run-$N-$(date -u +%Y%m%dT%H%M%SZ)"
    mv "$D" "$Q"
    # The logs travel with it. They are siblings of the run directory, and the
    # documented retake deletes two of them and overwrites the third — so leaving
    # them behind would destroy the per-run record the runbook asks to be
    # committed, for the one run whose record matters most.
    for L in "$D.out" "$D.err" "$D.backgrounds.out"; do
      [ -e "$L" ] && mv "$L" "$Q/$(basename "$L")"
    done
    echo "STOPPING: run $N attested $OK of $TOTAL — it is not evidence."
    echo "Quarantined to $Q (no manifest.json under the run name, so re-running this"
    echo "pass re-takes run $N rather than stepping over it). Keep it: what failed to"
    echo "attest is the finding. Report the session state rather than spending the"
    echo "remaining runs."
    exit 6
  fi
done
echo "PASS $PASS DONE $(date -u +%H:%M:%SZ)"
