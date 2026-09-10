#!/bin/bash
# W26 G3 — the canonical rebuild at the landed configuration (W26 Decision Log 10 (c) and (d);
# claims §5.126). `main` at the merge of G2c and G3a with this child's step 1 on top: the LIGHT
# document naming sizeHeavyTapSigma 9 / sizeHeavyTapSigma2x 9 (resolved b2b570e4adcea8fb, unmoved
# since G2's declaration) and the DARK document naming both at 0 (resolved 874be66ea501621b — its
# own W26 G1 fingerprint, the one G1 proved byte-identical to 0.14.0).
#
# `results/matrix.json` is REMOVED first. A cell's key carries the material document's file sha256
# and BOTH documents' hashes moved this wave, so every key moves with them and the old rows would
# otherwise sit beside the new ones and be read by the gate as duplicates (W25 G3b failed 25 of 37
# cases on exactly that). The whole gated bed is then rebuilt — six profiles, two tiers,
# `calibration,validation` then `holdout` — into the CANONICAL matrix and the CANONICAL
# `web-captures/`: no `--out-matrix`, no VITREA_WEB_CAPTURES.
#
# THEN the probe set on the four standard profiles on both tiers, LAST, so a refusal there cannot
# cost the gated bed a capture.
#
# The GPU tier runs before the CSS tier within each column so every dom cell's coherence axis is
# measured against a GPU capture already on disk — the order G2b's own matrix was assembled in, and
# the difference between a coherence row and a stale one.
#
# `--alpha` takes the declaration-conformance capture on every cell (W20 Decision Log 2 ruling 2;
# `adopted-thresholds.test.ts` fails a rebuild without them) and `--write-partial` records a cell
# whose axis is absent.
#
# THE HOLDOUT IS NOT A SECOND READING. X3 spends this wave's one holdout read at G2's dry run; what
# this run does with those cells is REPRODUCE their bytes, and `g3-referee` checks every one of them
# against `g2/g2b-digests.txt` (the light GPU rows) and against the pre-rebuild canonical digests
# (the dark and CSS rows, which do not move this wave).
#
# The previous canonical matrix and captures are copied to scratch first: they are the 0.14.0 bed,
# the referee's "before" and the landing sheets' "0.14.0" column.
#
# Two exits of 1 are EXPECTED and are the instrument's, not this wave's — both reproduced at every
# landing since W20 / W25 G4:
#   1x-light-increased-contrast / css / holdout   hc-text__capsule-button__rest, a 0.00px contour
#   several probe runs                            checkerboard-64__rrect-sm and dark-solid__rrect-48
set -u
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
"$HERE/g3-guard.sh" || exit 1
cd "$HERE/../../../../.."
unset VITREA_SCENES VITREA_FIXTURES VITREA_WEB_CAPTURES VITREA_MATRIX_PATH
T=/Users/new/.claude/jobs/5c70e47f/tmp/w26/g3
mkdir -p "$T/before"
LOG="$T/rebuild-runs.log"
rm -f "$T/DONE-REBUILD"
echo "=== $(date +%H:%M:%S) build ==="
pnpm -r build > "$T/rebuild-build.log" 2>&1 || { echo "BUILD FAILED"; exit 1; }
echo "=== $(date +%H:%M:%S) HEAD $(git rev-parse --short HEAD) $(git status --short | wc -l | tr -d ' ') dirty ==="
cd packages/calibration
LIGHT=profiles/apple-macos-26.5-1x-light-standard.json
DARK=profiles/apple-macos-26.5-1x-dark-standard.json
echo "=== light document $(shasum -a 256 $LIGHT | cut -c1-16) resolved $(python3 -c 'import json,sys;print(json.load(open(sys.argv[1]))["resolvedMaterialSha256"])' $LIGHT) ==="
echo "=== dark  document $(shasum -a 256 $DARK  | cut -c1-16) resolved $(python3 -c 'import json,sys;print(json.load(open(sys.argv[1]))["resolvedMaterialSha256"])' $DARK) ==="
cp results/matrix.json "$T/before/matrix-0.14.0.json"
rm -rf "$T/before/web-captures"; cp -R web-captures "$T/before/web-captures"
rm -rf web-captures; mkdir -p web-captures
rm -f results/matrix.json
: > "$LOG"
run() {
  local profile=$1 doc=$2 renderer=$3 sets=$4
  echo "=== $(date +%H:%M:%S) $profile / $renderer / $sets ==="
  npx tsx cli/compare.ts --profile "$profile" --material-profile "$doc" --renderer "$renderer" \
    --set "$sets" --alpha --write-partial >> "$LOG" 2>&1
  echo "    exit=$?"
}
for SETS in calibration,validation holdout; do
  echo "=== $(date +%H:%M:%S) the $SETS column ==="
  for renderer in webgpu css; do
    run apple-macos-26.5-1x-light-standard             "$LIGHT" "$renderer" "$SETS"
    run apple-macos-26.5-2x-light-standard             "$LIGHT" "$renderer" "$SETS"
    run apple-macos-26.5-1x-light-increased-contrast   "$LIGHT" "$renderer" "$SETS"
    run apple-macos-26.5-1x-light-reduced-transparency "$LIGHT" "$renderer" "$SETS"
    run apple-macos-26.5-1x-dark-standard              "$DARK"  "$renderer" "$SETS"
    run apple-macos-26.5-2x-dark-standard              "$DARK"  "$renderer" "$SETS"
  done
done
echo "=== $(date +%H:%M:%S) the probe column ==="
for renderer in webgpu css; do
  run apple-macos-26.5-1x-light-standard "$LIGHT" "$renderer" probe
  run apple-macos-26.5-2x-light-standard "$LIGHT" "$renderer" probe
  run apple-macos-26.5-1x-dark-standard  "$DARK"  "$renderer" probe
  run apple-macos-26.5-2x-dark-standard  "$DARK"  "$renderer" probe
done
echo "ALL RUNS DONE $(date +%H:%M:%S)"
touch "$T/DONE-REBUILD"
