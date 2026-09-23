#!/bin/bash
# Build the native calibration harness.
#
# This invokes `swiftc` from the Xcode toolchain DIRECTLY, with an explicit SDK
# path, rather than going through `xcodebuild` or `swift build`. That is not a
# stylistic preference — it is the only route that works on this machine, and the
# reason is worth recording:
#
#   The Xcode license on record is for Xcode 16.4
#   (`IDEXcodeVersionForAgreedToGMLicense` in
#   /Library/Preferences/com.apple.dt.Xcode.plist), while the installed Xcode is
#   26.6. Every license-gated wrapper — `xcodebuild`, `xcrun`, `swift`, and
#   therefore SwiftPM — refuses to run until someone with admin rights accepts the
#   new agreement (`sudo xcodebuild -license accept`). The compiler binaries
#   themselves are not gated, so a direct invocation with `-sdk` builds fine.
#
# Once the license is accepted this script keeps working unchanged; it is not a
# workaround that has to be undone, just a build that does not need Xcode's
# project machinery. There is no .xcodeproj on purpose: the harness is four source
# files and a shell script, and a generated pbxproj would be a second, staler
# description of the same thing.
set -euo pipefail

DEVELOPER_DIR="${DEVELOPER_DIR:-/Applications/Xcode.app/Contents/Developer}"
TOOLCHAIN="$DEVELOPER_DIR/Toolchains/XcodeDefault.xctoolchain/usr/bin"
SDK="$DEVELOPER_DIR/Platforms/MacOSX.platform/Developer/SDKs/MacOSX.sdk"
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# `VITREA_BUILD_OUT` builds into a second directory and leaves `build/` alone.
# Screen Recording is granted to the bundle's signature, and a rebuild is a new
# signature, so a harness change that must run DURING a sitting — a dump path,
# which captures no pixels and needs no grant — is built beside the granted
# bundle rather than over it (2026-09-12).
OUT="${VITREA_BUILD_OUT:-$HERE/build}"
BUNDLE_ID="${VITREA_BUNDLE_ID:-dev.vitrea.reference-apple}"
# Resolve aliases before the refusal: a symlink into a granted output is still
# that output. Both historical bundles share an identifier and must be protected
# in every checkout, not only the checkout this script was invoked from (§5.174).
OUT="$(python3 -c 'import os,sys; print(os.path.realpath(sys.argv[1]))' "$OUT")"
# The macOS volume may be case-insensitive. Changing spelling must not bypass
# the same protected location; this guard does not change any binary input.
OUT_CHECK="$(printf '%s/' "$OUT" | tr '[:upper:]' '[:lower:]')"
case "$OUT_CHECK" in
  */apps/reference-apple/build/*|*/apps/reference-apple/build-probe/*)
    if [ "${VITREA_ALLOW_PROTECTED_REBUILD:-0}" != "1" ]; then
      echo "REFUSED: protected output $OUT. Use an external VITREA_BUILD_OUT and a distinct VITREA_BUNDLE_ID; an intentional protected rebuild requires VITREA_ALLOW_PROTECTED_REBUILD=1." >&2
      exit 1
    fi;;
esac
case "$BUNDLE_ID" in
  ""|*[!a-zA-Z0-9.-]*) echo "error: invalid VITREA_BUNDLE_ID" >&2; exit 1;;
esac

if [ ! -x "$TOOLCHAIN/swiftc" ]; then
  echo "error: no swiftc at $TOOLCHAIN — set DEVELOPER_DIR to an Xcode install" >&2
  exit 1
fi
if [ ! -d "$SDK" ]; then
  echo "error: no macOS SDK at $SDK" >&2
  exit 1
fi

# The output root can be innocent while an existing bundle (or a child that
# codesign visits) redirects a write elsewhere. This generated bundle needs no
# symlinked children: refuse them before the first mkdir, plist or compiler write.
# OUT/harness is our convenience link and is deliberately outside this check.
python3 - "$OUT/VitreaReference.app" <<'PYGUARD'
import os
from pathlib import Path
import sys
app = Path(sys.argv[1])
if app.is_symlink():
    raise SystemExit(f"REFUSED: symlinked bundle destination {app}")
for root, dirs, files in os.walk(app, followlinks=False):
    for name in dirs + files:
        path = Path(root) / name
        if path.is_symlink():
            raise SystemExit(f"REFUSED: symlinked bundle descendant {path}")
PYGUARD

mkdir -p "$OUT"

# An .app bundle, not a bare executable. Screen Recording (TCC) is granted per
# application identity, and only a bundle with a stable CFBundleIdentifier has
# one — a loose binary inherits whatever granted the terminal that launched it.
APP="$OUT/VitreaReference.app"
mkdir -p "$APP/Contents/MacOS"

cat > "$APP/Contents/Info.plist" <<PLIST
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>CFBundleExecutable</key><string>VitreaReference</string>
  <key>CFBundleIdentifier</key><string>$BUNDLE_ID</string>
  <key>CFBundleName</key><string>Vitrea Reference</string>
  <key>CFBundlePackageType</key><string>APPL</string>
  <key>CFBundleShortVersionString</key><string>1.0</string>
  <key>LSMinimumSystemVersion</key><string>26.0</string>
  <key>NSHighResolutionCapable</key><true/>
</dict>
</plist>
PLIST

echo "swiftc → $APP/Contents/MacOS/VitreaReference"
"$TOOLCHAIN/swiftc" \
  -parse-as-library \
  -O \
  -swift-version 6 \
  -sdk "$SDK" \
  -target arm64-apple-macos26.0 \
  -framework AppKit -framework ScreenCaptureKit -framework IOKit \
  -o "$APP/Contents/MacOS/VitreaReference" \
  "$HERE"/Sources/*.swift

# Ad-hoc signature: enough for a stable bundle identity on this machine. A real
# Developer ID would be needed to move the bundle between machines.
codesign --force --sign - "$APP" >/dev/null 2>&1 || {
  echo "error: codesign failed — no usable capture bundle was built" >&2
  exit 1
}

# A convenience symlink for the non-GUI subcommand (`backgrounds`), which needs no
# bundle identity at all.
ln -sf "VitreaReference.app/Contents/MacOS/VitreaReference" "$OUT/harness"

echo "built. Try:"
echo "  $OUT/harness backgrounds"
echo "  $OUT/harness probe"
