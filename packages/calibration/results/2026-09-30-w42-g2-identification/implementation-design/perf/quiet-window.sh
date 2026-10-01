#!/bin/zsh
# The perf wave's final before/after, run in one quiet window. Restores the worktree on exit.
set -u
R=~/vitrea-w42/g2-impl/packages/renderer-webgpu
LOG=/tmp/w42-perf/quiet.log
FILES=(body-law-pass.ts body-law.ts index.ts renderer.ts timing.ts wgsl/body-law.ts wgsl/index.ts)
restore() {
  cd $R && git checkout -q -- src e2e/fixtures/harness.ts && rm -f e2e/bench/w42-profile.spec.ts
  echo "restored: $(git status --short src e2e | wc -l) modified" >> $LOG
}
trap restore EXIT
cd $R
: > $LOG
load() { echo "[$1] $(date -u +%H:%M:%SZ) $(uptime | sed 's/.*load averages:/load/')" >> $LOG; }
budget() {  # $1 tag
  for i in 1 2 3; do
    load "$1 budget run $i start"
    npx playwright test e2e/bench/budget.spec.ts --project=chromium-gpu --reporter=json > /tmp/w42-perf/budget-$1-$i.json 2>/tmp/w42-perf/budget-$1-$i.err
    load "$1 budget run $i end (exit $?)"
  done
}
static() {  # $1 tag
  cp /tmp/w42-perf/harness.knobs.ts e2e/fixtures/harness.ts && cp /tmp/w42-perf/w42-profile.spec.ts e2e/bench/
  load "$1 static start"
  W42_PROFILE_ROWS="$(cat /tmp/w42-perf/rows-static.json)" W42_PROFILE_OUT=/tmp/w42-perf/static-$1.json \
    npx playwright test e2e/bench/w42-profile.spec.ts --project=chromium-gpu > /tmp/w42-perf/static-$1.log 2>&1
  load "$1 static end (exit $?)"
  git checkout -q -- e2e/fixtures/harness.ts && rm -f e2e/bench/w42-profile.spec.ts
}
old() { for f in $FILES; do git show fbb2136e:packages/renderer-webgpu/src/$f > src/$f; done; }
budget quiet-after
static quiet-after
old
static quiet-before
budget quiet-before
git checkout -q -- src
budget quiet-after2
load done
