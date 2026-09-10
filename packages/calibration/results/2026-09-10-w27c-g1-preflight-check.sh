#!/bin/bash
# Proves apps/reference-apple's fresh-capture preflight (SceneSpec.swift,
# `scenesUnsupportedForFreshCapture`) does what W27c G1 added it to do:
#
#   - a spec whose scenes are all 'rest' or 'pressed' passes — the existing
#     active-only beds still capture
#   - a spec carrying a recovered 'inactive' scene (the W27c window-recede pose,
#     claims §5.128, §5.130) is refused, by name
#
# Real code, not a description of it: this compiles the check driver directly
# against the production SceneSpec.swift and runs the built binary — no GUI, no
# window, no TCC. Usage:
#
#   ./2026-09-10-w27c-g1-preflight-check.sh
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
NATIVE="$HERE/../../../apps/reference-apple"
DEVELOPER_DIR="${DEVELOPER_DIR:-/Applications/Xcode.app/Contents/Developer}"
TOOLCHAIN="$DEVELOPER_DIR/Toolchains/XcodeDefault.xctoolchain/usr/bin"
SDK="$DEVELOPER_DIR/Platforms/MacOSX.platform/Developer/SDKs/MacOSX.sdk"

if [ ! -x "$TOOLCHAIN/swiftc" ]; then
  echo "error: no swiftc at $TOOLCHAIN — set DEVELOPER_DIR to an Xcode install" >&2
  exit 1
fi

BIN="$(mktemp -d)/preflight-check"
echo "compiling against $NATIVE/Sources/SceneSpec.swift ..."
"$TOOLCHAIN/swiftc" \
  -parse-as-library -O -swift-version 6 \
  -sdk "$SDK" -target arm64-apple-macos26.0 \
  -o "$BIN" \
  "$HERE/2026-09-10-w27c-g1-preflight-driver.swift" \
  "$NATIVE/Sources/SceneSpec.swift"

fail=0

echo
echo "== active-only fixture: expect PASS (no scene refused) =="
if ! "$BIN" "$HERE/2026-09-10-w27c-g1-preflight-fixture-active.json" pass; then
  fail=1
fi

echo
echo "== inactive-carrying fixture: expect REFUSE (bg__c__inactive named) =="
if ! "$BIN" "$HERE/2026-09-10-w27c-g1-preflight-fixture-inactive.json" refuse; then
  fail=1
fi

echo
if [ "$fail" -eq 0 ]; then
  echo "preflight-check: PASS"
else
  echo "preflight-check: FAIL" >&2
fi
exit "$fail"
