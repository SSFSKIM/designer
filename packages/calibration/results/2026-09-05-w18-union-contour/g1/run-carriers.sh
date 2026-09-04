#!/bin/bash
# W18 G1's pre-check (Decision Log 3, the gate) — the two carriers captured on G0's separation bed.
#
# One scratch scene bed, G0's own (`w18-web.json`: the lone 44x44 capsule, the canonical 120x44
# one, the three-up at 12 and at 40, the stack and its two parts, over `checkerboard`, `photo` and
# `light-solid`), on both tiers at both scales, in two CONFIGURATIONS:
#
#   cfgA   carrier A alone — the shadow on each surface's own L3 and nowhere else, so a surface
#          does not sample its own shadow and still samples its later neighbours'.
#   cfgAB  both carriers   — a group of more than one member paints every member's shadow from the
#          group's last-painted host, which is the whole closure.
#
# The instrument for cfgA is one branch stood down in `planCssTierShadow`, applied here and
# reverted by `git checkout` after the run — the same shape as G0's declined profile documents, and
# for the same reason: the two configurations have to differ in exactly one thing.
#
# The calibration page aliases `@vitreajs/vitrea-web` straight at `platform-web/src/index.ts`
# (`web/vite.config.ts`), so the branch's source is what is captured and no build step stands
# between the edit and the pixels.
#
# The GPU tier is captured ONCE: this wave does not touch it (X3), the configurations differ only
# inside the CSS tier, and the captures are compared byte-for-byte against G0's own.
#
# Nothing canonical is written: scratch scenes through `VITREA_SCENES`, scratch capture roots
# through `--out`, `VITREA_FIXTURES` left unset so the page fetches the committed backgrounds
# read-only.
#
# Usage: `bash run-carriers.sh`, from `packages/calibration` in the w18-g1 worktree.
set -u
ROOT=/Users/new/Developer/GitHub/designer/.claude/worktrees/w18-g1
W=$ROOT/packages/calibration
T=/Users/new/.claude/jobs/5c70e47f/tmp/w18/g1
SCENES=/Users/new/.claude/jobs/5c70e47f/tmp/w18/g0/scenes/w18-web.json
PLAN=$ROOT/packages/platform-web/src/css-tier-shadow.ts

if pgrep -f 'compare.ts|sweep.ts|cost.mjs|capture.mjs|capture-web|VitreaReference' > /dev/null \
   || lsof -i :5189 > /dev/null 2>&1; then
  echo "GPU busy: another capture is running"; exit 2
fi

mkdir -p "$T/captures" "$T/logs"
cd "$W" || exit 1
unset VITREA_FIXTURES
export VITREA_SCENES="$SCENES"

capture() {
  local tier=$1 scale=$2 tag=$3
  echo "=== $(date +%H:%M:%S) $tag $tier @${scale}x ==="
  npx tsx scripts/capture-web.ts --all --renderer "$tier" --scale "$scale" \
    --out "$T/captures/$tag-$tier-${scale}x" >> "$T/logs/carriers.log" 2>&1
  echo "    exit=$?"
}

# The GPU tier, once — the check on X3, byte-compared against G0's captures afterwards.
capture webgpu 1 gpu
capture webgpu 2 gpu

# Both carriers: the branch exactly as it stands.
capture css 1 cfgAB
capture css 2 cfgAB

# Carrier A alone.
python3 - "$PLAN" <<'PY'
import sys
path = sys.argv[1]
text = open(path).read()
needle = "  if (members.length > 1 && !last.clipsChildren) {"
assert text.count(needle) == 1, "the carrier B branch moved; the instrument must be re-aimed"
open(path, "w").write(text.replace(needle, "  if (false && members.length > 1 && !last.clipsChildren) {"))
PY
capture css 1 cfgA
capture css 2 cfgA
git -C "$ROOT" checkout -- packages/platform-web/src/css-tier-shadow.ts
git -C "$ROOT" diff --quiet -- packages/platform-web/src/css-tier-shadow.ts \
  && echo "instrument reverted" || { echo "INSTRUMENT STILL APPLIED"; exit 3; }

echo "DONE $(date +%H:%M:%S)"
