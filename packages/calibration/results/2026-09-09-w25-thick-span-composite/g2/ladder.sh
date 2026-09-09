#!/usr/bin/env bash
# W25 G2 — the scratch ladder: one rung is one material, rendered to scratch.
#
# WHAT THIS WRITES. Only under $OUT (the scratch root, default
# /Users/new/.claude/jobs/5c70e47f/tmp/w25/g2). It never touches `scenes.json`,
# `fixtures/`, the canonical `results/matrix.json` or the canonical
# `web-captures/` — X2. Every capture goes through `capture:web` with `--out`
# pointed into scratch, which is the driver `compare` uses for the web side and
# none of its matrix bookkeeping.
#
# THE GPU DISCIPLINE (X4). One capture process at a time, and the caller checks
# `pgrep -f 'compare.ts|sweep.ts|cost.mjs|capture.mjs|capture-web|VitreaReference|playwright'`
# empty and `lsof -i :5189` clear before every launch. This script runs its four
# captures strictly in sequence and writes a DONE marker when the rung is
# complete, so a background waiter has one file to watch.
#
# THE BEDS A RUNG RENDERS.
#   w9    — the W9 light probe grid (56 scenes, 1x, light), whose coarse
#           checkerboards are the only fixtures on disk that carry the heavy
#           share (G0 §6, finding 3).
#   w21   — the W21 dark probe grid (56 scenes, 1x, dark), the same at the other
#           scheme, minus the two withdrawn `rrect-sm`-over-a-solid cells.
#   canon-light / canon-dark — the canonical 1x bed minus its holdout, which is
#           where the level term's rows and the thin-invariance rung live.
#
# The probe grids' backdrop rasters come from the W21 probe's own `backgrounds/`
# directory, which is the only committed copy of `checkerboard-32`,
# `checkerboard-64` and the rest. They are synthetic and scheme-independent —
# the same PNGs the W9 grid was captured over — so one mount serves both grids.
#
# The canonical rungs NAME their scenes rather than passing `--all`, and the ten
# holdout ids are what they leave out: X3 reserves the holdout for G3's dry run
# on the frozen configuration, and a rung that rendered them would have read
# them. The list comes from `scenes.json`'s own `split`, never restated here.
#
# Usage:  ladder.sh <rung> <light-profile.json> <dark-profile.json>
set -euo pipefail

RUNG="${1:?rung name}"
LIGHT="${2:?light material profile}"
DARK="${3:?dark material profile}"

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../../.." && pwd)"
CAL="$REPO/packages/calibration"
OUT="${W25_SCRATCH:-/Users/new/.claude/jobs/5c70e47f/tmp/w25/g2}/$RUNG"
PROBE_BG="$CAL/results/2026-09-06-w21-dark-scheme/probe"

mkdir -p "$OUT"
rm -f "$OUT/DONE"

cd "$CAL"

CANON=$(node -e '
  const m = require(process.argv[1]);
  const out = new Set(m.split.holdout);
  const ids = m.scenes.filter((s) => !out.has(s.id) && s.state === "rest").map((s) => s.id);
  process.stdout.write(ids.join(" "));
' "$REPO/apps/reference-apple/scenes.json")

run() {  # run <label> <scenes-json> <scheme> <fixtures-root> <profile> [ids…]
  local label="$1" scenes="$2" scheme="$3" fixtures="$4" profile="$5"
  shift 5
  echo "-- rung $RUNG / $label --------------------------------------------"
  VITREA_FIXTURES="$fixtures" VITREA_SCENES="$scenes" \
    pnpm exec tsx scripts/capture-web.ts "$@" \
      --scale 1 --color-scheme "$scheme" --renderer webgpu \
      --out "$OUT/$label" --material-profile "$profile"
}

run w9  "$REPO/apps/reference-apple/scenes-w9-probe.json"  light "$PROBE_BG" "$LIGHT" --all
run w21 "$REPO/apps/reference-apple/scenes-w21-probe.json" dark  "$PROBE_BG" "$DARK" --all
# shellcheck disable=SC2086
run canon-light "$REPO/apps/reference-apple/scenes.json" light \
  "$REPO/apps/reference-apple/fixtures" "$LIGHT" $CANON
# shellcheck disable=SC2086
run canon-dark "$REPO/apps/reference-apple/scenes.json" dark \
  "$REPO/apps/reference-apple/fixtures" "$DARK" $CANON

date -u +%Y-%m-%dT%H:%M:%SZ > "$OUT/DONE"
echo "rung $RUNG complete -> $OUT"
