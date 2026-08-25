#!/bin/bash
# Run the harness with the toolchain provenance the manifest records.
#
# Usage:
#   ./capture.sh backgrounds                    # shared raster backgrounds
#   ./capture.sh probe                          # what can this machine capture?
#   ./capture.sh capture                        # fixtures, ScreenCaptureKit (needs TCC)
#   ./capture.sh capture --method nsview-cachedisplay
#
# VITREA_SCALE=2 ./capture.sh ...  to target the spec's canonical 2x profiles on a
# Retina machine. On a 1x display the harness records the real backingScaleFactor
# and adds a caveat rather than pretending the request was honoured.
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DEVELOPER_DIR="${DEVELOPER_DIR:-/Applications/Xcode.app/Contents/Developer}"
export DEVELOPER_DIR

if [ ! -x "$HERE/build/harness" ]; then
  echo "harness not built — running build.sh" >&2
  "$HERE/build.sh"
fi

# `xcodebuild -version` is one of the few wrappers that answers without the
# license gate, so the provenance is recordable even while the gate is closed.
VITREA_XCODE_VERSION="$("$DEVELOPER_DIR/usr/bin/xcodebuild" -version 2>/dev/null | tr '\n' ' ' | sed 's/  */ /g; s/ $//')"
VITREA_XCODE_VERSION="${VITREA_XCODE_VERSION:-unknown}"
export VITREA_XCODE_VERSION

SDK_PATH="$DEVELOPER_DIR/Platforms/MacOSX.platform/Developer/SDKs/MacOSX.sdk"
VITREA_SDK="$(/usr/libexec/PlistBuddy -c 'Print :Version' "$SDK_PATH/SDKSettings.plist" 2>/dev/null || echo unknown)"
export VITREA_SDK="MacOSX${VITREA_SDK}.sdk"

echo "Xcode: $VITREA_XCODE_VERSION"
echo "SDK:   $VITREA_SDK"
echo "scale: ${VITREA_SCALE:-1}x"
echo

exec "$HERE/build/harness" "$@"
