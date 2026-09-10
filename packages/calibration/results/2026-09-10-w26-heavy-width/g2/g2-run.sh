#!/bin/bash
# W26 G2 — one column of the dry run, to SCRATCH, in THIS WORKTREE.
#
#   g2-run.sh <tag> <bed|probe|holdout> [webgpu,css]
#
# W25 G3's three run scripts folded into one, because this child runs the same command over three
# `--set` columns and a third copy of the same twenty lines would be three places for a flag to
# drift. The column is the argument; the order the columns are run in is the declaration's (§5) and
# is enforced by the caller, not here — the holdout is X3's one read and a script cannot be trusted
# to be the thing that remembers that.
#
# WHERE IT RUNS, and why it is not the shared checkout. G1c captured in the checkout and proved with
# `g1c-same.sh` that every capture-relevant source was byte-identical to it, because a worktree
# carries no `node_modules`. That proof cannot be made by a child that CHANGES those sources: this
# landing moves `material.ts` and `platform-web/src/optics.ts`, and a capture taken in the checkout
# would be a capture of the OLD material on the CSS tier while looking exactly like a valid run.
# `pnpm install --frozen-lockfile` against the same store makes this worktree the same toolchain in
# seconds, so the run is this branch's code by construction rather than by comparison.
#
# The GPU tier runs before the CSS tier within each column so every dom cell's coherence axis is
# measured against a GPU capture already on disk, which is the canonical rebuild's order. The flags
# are the canonical rebuild's — `--alpha` and `--write-partial` — because G3 has to reproduce these
# bytes with them.
#
# The matrix is REMOVED, not appended to. A cell's key carries the material document's sha256, so a
# second run at a second material leaves every cell twice and the gate reads both (W25 G3b failed 25
# of 37 gate cases on that alone). The captures share ONE root per tag on purpose: the family reader
# needs rows from the bed column and the probe column of the same material in one place, and a
# capture is written per profile and scene, so the columns cannot collide.
#
# One capture process at a time (X4); `g2-guard.sh` refuses to start beside another. Everything to
# scratch through `--out-matrix` and `VITREA_WEB_CAPTURES` (X2): the canonical `results/matrix.json`,
# `web-captures/`, `apps/reference-apple/fixtures/` and `scenes.json` are never written.
set -u
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
"$HERE/g2-guard.sh" || exit 1
cd "$HERE/../../../../.."
unset VITREA_SCENES VITREA_FIXTURES VITREA_MATRIX_PATH
TAG=${1:?tag}
COLUMN=${2:?bed|probe|holdout}
TIERS=${3:-webgpu,css}
T=/Users/new/.claude/jobs/5c70e47f/tmp/w26/g2/$TAG
mkdir -p "$T"
export VITREA_WEB_CAPTURES="$T/web-captures"
MATRIX="$T/$COLUMN.json"
rm -f "$T/DONE-$COLUMN" "$MATRIX"
LOG="$T/$COLUMN-runs.log"
: > "$LOG"
echo "=== $(date +%H:%M:%S) build ==="
pnpm -r build > "$T/build-$COLUMN.log" 2>&1 || { echo "BUILD FAILED"; exit 1; }
echo "=== $(date +%H:%M:%S) tag=$TAG column=$COLUMN HEAD $(git rev-parse --short HEAD) $(git status --short | wc -l | tr -d ' ') dirty ==="
cd packages/calibration
LIGHT=profiles/apple-macos-26.5-1x-light-standard.json
DARK=profiles/apple-macos-26.5-1x-dark-standard.json
echo "=== light document $(shasum -a 256 $LIGHT | cut -c1-12) ==="
echo "=== dark  document $(shasum -a 256 $DARK  | cut -c1-12) ==="
case "$COLUMN" in
  bed)     SETS=calibration,validation ;;
  probe)   SETS=probe ;;
  holdout) SETS=holdout ;;
  *) echo "unknown column $COLUMN" >&2; exit 2 ;;
esac
run() {
  echo "=== $(date +%H:%M:%S) $1 / $3 / $SETS ==="
  npx tsx cli/compare.ts --profile "$1" --material-profile "$2" --renderer "$3" \
    --set "$SETS" --alpha --write-partial --out-matrix "$MATRIX" >> "$LOG" 2>&1
  echo "    exit=$?"
}
for RENDERER in ${TIERS//,/ }; do
  run apple-macos-26.5-1x-light-standard "$LIGHT" "$RENDERER"
  run apple-macos-26.5-2x-light-standard "$LIGHT" "$RENDERER"
  run apple-macos-26.5-1x-dark-standard  "$DARK"  "$RENDERER"
  run apple-macos-26.5-2x-dark-standard  "$DARK"  "$RENDERER"
  # The probe set exists only for the four standard profiles; the bed and the holdout carry the two
  # accessibility ones as well and a run that skipped them would gate on a partial bed.
  if [ "$COLUMN" != "probe" ]; then
    run apple-macos-26.5-1x-light-increased-contrast    "$LIGHT" "$RENDERER"
    run apple-macos-26.5-1x-light-reduced-transparency  "$LIGHT" "$RENDERER"
  fi
done
echo "COLUMN $COLUMN DONE $TAG $(date +%H:%M:%S)"
touch "$T/DONE-$COLUMN"
