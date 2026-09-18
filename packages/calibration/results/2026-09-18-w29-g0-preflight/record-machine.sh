#!/bin/bash
# G0 (a): the machine record, read from the machine and the binary.
#
#   record-machine.sh > machine.json
#
# Every field is a read rather than a transcription, and where the honest answer is
# "this cannot be read here" the field says so rather than being filled in from a
# neighbouring source. Three of those are the point of the file:
#
#   * `bundle.recordedSdk` is `LC_BUILD_VERSION`'s `sdk` from the granted binary,
#     which is what macOS gates behaviour on. `bundle.compiledAgainstSdk` is NOT
#     derivable from the binary on this build path — `swiftc` links through clang
#     with `--sysroot`, which loses the SDK version, so the field records `sdk ==
#     minos` whatever SDK compiled it (measured; see `side-build.sh`).
#   * `accessibility.showBorders` is null: macOS 27's Show Borders has no key in
#     `com.apple.universalaccess`, none in the global domain, and no
#     `accessibilityDisplayShould…` property in the 27 SDK's `NSAccessibility.h`.
#     What can be attested is the absence of a key, which is not the same as the
#     setting being off.
#   * `display.colorProfile` comes from a harness run rather than from here:
#     `NSScreen.colorSpace.localizedName` is what the manifest records, and this
#     script has no AppKit.
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO="$(cd "$HERE/../../../.." && pwd)"
APP="${VITREA_APP:-/Users/new/Developer/GitHub/designer/apps/reference-apple/build/VitreaReference.app}"
BIN="$APP/Contents/MacOS/VitreaReference"
VTOOL=/Applications/Xcode.app/Contents/Developer/Toolchains/XcodeDefault.xctoolchain/usr/bin/vtool
DEV=/Applications/Xcode.app/Contents/Developer
DISPLAY_ID="${VITREA_DISPLAY_ID:-7709FD0F-F423-4277-B0C8-7CA94F85723A}"

read_or_null() { "$@" 2>/dev/null || echo null; }
json_str() { printf '%s' "$1" | python3 -c 'import json,sys; print(json.dumps(sys.stdin.read()))'; }

OS_VERSION=$(sw_vers -productVersion)
OS_BUILD=$(sw_vers -buildVersion)
MODEL=$(sysctl -n hw.model)
CPU=$(sysctl -n machdep.cpu.brand_string)
RT=$(defaults read com.apple.universalaccess reduceTransparency 2>/dev/null || echo 0)
IC=$(defaults read com.apple.universalaccess increaseContrast 2>/dev/null || echo 0)
DWC=$(defaults read com.apple.universalaccess differentiateWithoutColor 2>/dev/null || echo 0)
TINT=$(defaults read -g NSGlassTintAmount 2>/dev/null || echo null)
TINT_TYPE=$(defaults read-type -g NSGlassTintAmount 2>/dev/null | sed 's/^Type is //' || echo "absent")
# The display's colour profile and name as the HARNESS read them, out of a run this
# gate took. `NSScreen.colorSpace.localizedName` is the field the six 26.5 profiles
# carry, so a reading taken any other way would not be comparable to them.
MANIFEST="${1:-}"
if [ -n "$MANIFEST" ] && [ -f "$MANIFEST" ]; then
  COLOR_PROFILE=$(python3 -c 'import json,sys
m = json.load(open(sys.argv[1]))
print(m["profiles"][0]["display"].get("displayColorProfile") or "")' "$MANIFEST")
  HARNESS_NAME=$(python3 -c 'import json,sys
m = json.load(open(sys.argv[1]))
print(m["profiles"][0]["display"].get("displayName") or "")' "$MANIFEST")
else
  COLOR_PROFILE=""
  HARNESS_NAME=""
fi
XCODE=$("$DEV/usr/bin/xcodebuild" -version 2>/dev/null | tr '\n' ' ' | sed 's/  */ /g; s/ $//')
XCODE_SDK=$(/usr/libexec/PlistBuddy -c 'Print :Version' \
  "$DEV/Platforms/MacOSX.platform/Developer/SDKs/MacOSX.sdk/SDKSettings.plist" 2>/dev/null || echo unknown)
CLT_SDKS=$(ls /Library/Developer/CommandLineTools/SDKs | tr '\n' ' ')
CLT_VER=$(pkgutil --pkg-info=com.apple.pkg.CLTools_Executables 2>/dev/null | awk '/^version:/{print $2}')
CLT_SWIFTC=$(/Library/Developer/CommandLineTools/usr/bin/swiftc --version 2>/dev/null | head -1)
MINOS=$($VTOOL -show "$BIN" 2>/dev/null | awk '/minos/{print $2; exit}')
SDKREC=$($VTOOL -show "$BIN" 2>/dev/null | awk '/^ *sdk /{print $2; exit}')
CDHASH=$(codesign -dvvv "$APP" 2>&1 | awk -F= '/^CDHash=/{print $2}')
BINSHA=$(shasum -a 256 "$BIN" | cut -d' ' -f1)
CURRENT_MODE=$(displayplacer list 2>/dev/null | awk '/<-- current mode/{print $2}' | tr -d ':')
MODE68=$(displayplacer list 2>/dev/null | grep -c '^  mode 68:' || true)
MODE69=$(displayplacer list 2>/dev/null | grep -c '^  mode 69:' || true)
SCREEN=$(system_profiler SPDisplaysDataType 2>/dev/null | awk '/^        [^ ].*:$/{gsub(/^ +| *:$/,""); print; exit}')
PERSISTENT=$(displayplacer list 2>/dev/null | awk '/Persistent screen id:/{print $4; exit}')

cat <<JSON
{
  "recordedAt": "$(date -u +%FT%TZ)",
  "gate": "W29 G0 (a); claims 5.149",
  "os": { "productVersion": "$OS_VERSION", "build": "$OS_BUILD",
          "kernel": $(json_str "$(uname -v)") },
  "hardware": { "model": "$MODEL", "cpu": $(json_str "$CPU") },
  "accessibility": {
    "reduceTransparency": $RT,
    "increaseContrast": $IC,
    "differentiateWithoutColor": $DWC,
    "showBorders": null,
    "showBordersNote": "No key in com.apple.universalaccess, none in the global domain, and no accessibilityDisplayShould* property for it in MacOSX27.sdk NSAccessibility.h. The absence of a key is what is attested; the setting's state is not readable here."
  },
  "glassSlider": { "key": "NSGlassTintAmount", "domain": "NSGlobalDomain",
                   "value": $TINT, "type": "$TINT_TYPE" },
  "toolchain": {
    "xcode": $(json_str "$XCODE"),
    "xcodeMacOSXSdkVersion": "$XCODE_SDK",
    "commandLineToolsVersion": $(json_str "${CLT_VER:-unknown}"),
    "commandLineToolsSdks": $(json_str "$CLT_SDKS"),
    "commandLineToolsSwiftc": $(json_str "${CLT_SWIFTC:-unknown}")
  },
  "bundle": {
    "path": $(json_str "$APP"),
    "binarySha256": "$BINSHA",
    "cdHash": "${CDHASH:-unknown}",
    "minos": "$MINOS",
    "recordedSdk": "$SDKREC",
    "compiledAgainstSdk": null,
    "compiledAgainstSdkNote": "Not derivable from the binary. swiftc links through clang with --sysroot, which does not read SDKSettings.plist, so ld records sdk == minos whatever SDK was used. The bundle was built by build.sh under Xcode 26.6, whose MacOSX.sdk is 26.5."
  },
  "display": {
    "persistentScreenId": "$PERSISTENT",
    "name": $(json_str "$SCREEN"),
    "harnessDisplayName": $(json_str "$HARNESS_NAME"),
    "colorProfile": $(json_str "$COLOR_PROFILE"),
    "colorProfileSource": $(json_str "$MANIFEST"),
    "colorProfileNote": "NSScreen.colorSpace.localizedName as the harness reads it, taken from a G0 scratch run; this is the field the six 26.5 profiles carry beside displayName.",
    "currentMode": ${CURRENT_MODE:-null},
    "mode68Present": $([ "$MODE68" -gt 0 ] && echo true || echo false),
    "mode69Present": $([ "$MODE69" -gt 0 ] && echo true || echo false)
  }
}
JSON
