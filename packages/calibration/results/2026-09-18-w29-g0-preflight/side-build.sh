#!/bin/bash
# One side bundle for G0 (c)'s SDK-gating comparison — never `apps/reference-apple/build/`.
#
#   side-build.sh <sdk-path> <out-dir> <recorded-sdk-version>
#
# This mirrors `apps/reference-apple/build.sh` — same sources, same `swiftc`
# flags, same bundle identifier, same ad-hoc signature — and differs from it in
# exactly two ways, both of which the comparison needs:
#
#   1. the SDK is an argument rather than whatever `DEVELOPER_DIR` points at, so
#      two bundles can be built from one toolchain against two SDKs and the SDK
#      is then the only variable between them;
#   2. the recorded SDK version in `LC_BUILD_VERSION` is passed to the linker
#      explicitly. That is not a flourish. `swiftc` links through `clang` with
#      `--sysroot` rather than `-isysroot`, and clang reads `SDKSettings.plist`
#      only for the latter — so `build.sh`'s plain invocation records
#      `sdk == minos` whatever SDK it compiled against (measured 2026-09-18:
#      both a 26.5-SDK and a 27-SDK build of these sources came out `sdk 26.0`).
#      macOS gates appearance behaviour on that recorded field, so a side build
#      meant to ask whether the material is SDK-gated has to carry the field it
#      is being asked about.
#
# The toolchain is the Command Line Tools' (Swift 6.4): Xcode 26.6's compiler
# refuses the 27 SDK outright — "this SDK is not supported by the compiler" —
# so one toolchain across both arms is also the only way to hold the compiler
# fixed while the SDK moves.
set -euo pipefail

SDK="${1:?usage: side-build.sh <sdk-path> <out-dir> <recorded-sdk-version>}"
OUT="${2:?usage: side-build.sh <sdk-path> <out-dir> <recorded-sdk-version>}"
SDKVER="${3:?usage: side-build.sh <sdk-path> <out-dir> <recorded-sdk-version>}"

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO="$(cd "$HERE/../../../.." && pwd)"
SOURCES="$REPO/apps/reference-apple/Sources"
SWIFTC="${VITREA_SWIFTC:-/Library/Developer/CommandLineTools/usr/bin/swiftc}"

case "$OUT" in
  "$REPO"/*) echo "REFUSED: $OUT is inside the repository. X4: side builds live outside it." >&2; exit 1;;
esac

mkdir -p "$OUT"
APP="$OUT/VitreaReference.app"
rm -rf "$APP"
mkdir -p "$APP/Contents/MacOS"

cat > "$APP/Contents/Info.plist" <<'PLIST'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>CFBundleExecutable</key><string>VitreaReference</string>
  <key>CFBundleIdentifier</key><string>dev.vitrea.reference-apple</string>
  <key>CFBundleName</key><string>Vitrea Reference</string>
  <key>CFBundlePackageType</key><string>APPL</string>
  <key>CFBundleShortVersionString</key><string>1.0</string>
  <key>LSMinimumSystemVersion</key><string>26.0</string>
  <key>NSHighResolutionCapable</key><true/>
</dict>
</plist>
PLIST

"$SWIFTC" \
  -parse-as-library \
  -O \
  -swift-version 6 \
  -sdk "$SDK" \
  -target arm64-apple-macos26.0 \
  -framework AppKit -framework ScreenCaptureKit -framework IOKit \
  -Xlinker -platform_version -Xlinker macos -Xlinker 26.0 -Xlinker "$SDKVER" \
  -o "$APP/Contents/MacOS/VitreaReference" \
  "$SOURCES"/*.swift 2>&1 | grep -vE '^\s*$|warning:|note:|^ *[0-9]+ \||^ *\||\[#Deprecated' || true

codesign --force --sign - "$APP" >/dev/null 2>&1 || {
  echo "warning: codesign failed — TCC cannot identify the app" >&2
}
ln -sf "VitreaReference.app/Contents/MacOS/VitreaReference" "$OUT/harness"
echo "built $APP against $SDK, recorded sdk $SDKVER"
