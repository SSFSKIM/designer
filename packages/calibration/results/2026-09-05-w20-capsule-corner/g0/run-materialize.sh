#!/bin/bash
# W20 G0 — the probe bed, materialised from the attested runs. W19 G0's script, re-pointed.
#
# Each run is a whole snapshot of the profile directory plus its own manifest. The target directory
# is seeded from one attested run — its manifest and its backgrounds — so that `materialize` has a
# manifest to rewrite and a profile directory to write into; every cell's bytes and every cell's
# manifest entry are then replaced by whichever run the plurality rule publishes, so a published
# cell's checksum and attestations always describe the bytes beside them.
#
# `--frequency-settle` is W9's freezing mode (claims §5.30): a cell holding more than one settled
# state is published at its majority state and marked, with the frequencies recorded; a tie is still
# refused. Runs are named on the command line, so a disqualified run is simply absent and its
# disqualification is recorded in `provenance.json` rather than silently dropped.
#
# Usage: `bash run-materialize.sh <probeDir> <seedRunDir> <runDir>...`, from `packages/calibration`.
set -eu
PROBE="${1:?usage: run-materialize.sh <probeDir> <seedRunDir> <runDir>...}"
SEED="${2:?}"
shift 2

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKTREE="$(cd "$HERE/../../../../.." && pwd)"
SCENES="$WORKTREE/apps/reference-apple/scenes-w20-probe.json"
PROFILE=apple-macos-26.5-1x-light-standard

mkdir -p "$PROBE/$PROFILE"
cp "$SEED/manifest.json" "$PROBE/manifest.json"
mkdir -p "$PROBE/backgrounds"
cp "$SEED/backgrounds/"* "$PROBE/backgrounds/"

ARGS=()
for D in "$@"; do
  ARGS+=(--run "$(basename "$D")=$D")
done

VITREA_SCENES="$SCENES" VITREA_FIXTURES="$PROBE" npx tsx cli/materialize.ts "${ARGS[@]}" \
  --profile "$PROFILE" --frequency-settle
VITREA_SCENES="$SCENES" VITREA_FIXTURES="$PROBE" npx tsx cli/materialize.ts "${ARGS[@]}" \
  --profile "$PROFILE" --frequency-settle --apply
echo "MATERIALISED $(date -u +%H:%M:%SZ)"
