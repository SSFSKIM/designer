#!/bin/bash
# The grant-free arm of G0 (c): what each bundle DECLARES for the same cells.
#
#   dump-arms.sh <bundle.app> <out-root> [settle]
#
# `dump-layers` walks SwiftUI's Core Animation layer tree and records the material's
# declared parameters. It captures no pixels and needs no Screen Recording grant,
# which is the whole reason it can run against a side build at all — and the reason
# the SDK question does not have to wait on a TCC decision to be asked at all.
#
# What it can and cannot settle is worth stating where it is run. The material is
# composited by the window server out of this tree, so two bundles that hand the
# window server the same filter type with the same inputs are asking for the same
# composite; that is strong evidence and it is not a pixel proof, because the
# window server could in principle read the requesting binary's linked SDK itself.
# The pixel arm is `capture`, and it needs the grant.
#
# The cell set is the charter's: a structured backdrop (checkerboard capsule), the
# light `hc-text__rrect-sm`, a corner-bearing large radius, a photo `rrect-md` in
# each scheme, and one inactive cell through the `.accessory` recede.
set -euo pipefail

APP="${1:?usage: dump-arms.sh <bundle.app> <out-root> [settle]}"
OUT="${2:?usage: dump-arms.sh <bundle.app> <out-root> [settle]}"
SETTLE="${3:-8}"

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO="$(cd "$HERE/../../../.." && pwd)"
SPEC="$REPO/apps/reference-apple/scenes.json"

ACTIVE=checkerboard__capsule-button__rest,hc-text__rrect-sm__rest,dark-solid__rrect-80__rest,photo__rrect-md__rest
# A `rest` id, presented in the recede, and not `photo__rrect-md__inactive`.
# `dump-layers` calls `refuseScenesUnreachableInPose(..., pose: .active)` before it
# reads `--inactive`, so it refuses every declared inactive id whatever pose it is
# about to present in (measured 2026-09-18; the W27e recipe never hit it because
# its probe spec declares only `rest` ids). The recede is a property of the
# presentation rather than of the scene — `Capture.presentInactive`'s own doc
# comment says so — so a `rest` id in the `.accessory` pose is the same reading
# under a name the harness accepts.
INACTIVE=photo__rrect-md__rest

if pgrep -f 'compare.ts|sweep.ts|capture-web|VitreaReference|playwright' >/dev/null; then
  echo "REFUSED: a capture process is already running (the GPU is shared; one at a time)." >&2
  exit 7
fi

mkdir -p "$OUT"
for SCHEME in light dark; do
  open -W --env VITREA_SCENES="$SPEC" \
    --stdout "$OUT/$SCHEME.out" --stderr "$OUT/$SCHEME.err" "$APP" \
    --args dump-layers --scenes "$ACTIVE" --scheme "$SCHEME" --settle "$SETTLE" \
    --require-key --out "$OUT/$SCHEME"
done

# The recede, through the same `.accessory` path the inactive capture pose uses.
# `--require-key` would refuse it, and that is the point: the two arms are
# different poses and neither may borrow the other's attestation.
#
# The bare binary, not `open -W`. LaunchServices cannot block on an `.accessory`
# application — `open -W` returns "Unable to block on application" immediately and
# the run's output would be read before it exists. The runbook's rule that a
# capture goes through `open` is about the TCC identity; `dump-layers` captures no
# pixels and asks TCC for nothing, so the bundle identity buys it nothing here.
VITREA_SCENES="$SPEC" "$APP/Contents/MacOS/VitreaReference" \
  dump-layers --inactive --scenes "$INACTIVE" --scheme light --settle "$SETTLE" \
  --out "$OUT/inactive" > "$OUT/inactive.out" 2> "$OUT/inactive.err"

echo "done → $OUT"
ls "$OUT"/light "$OUT"/dark "$OUT"/inactive
