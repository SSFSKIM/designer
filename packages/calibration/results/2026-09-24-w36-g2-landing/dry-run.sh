#!/bin/sh
# W36 G2's publish rehearsal, copied for 0.24.0 (§5.180; W36 clause 8).
# The same dry publish and pack commands; only the gate version and scratch
# directory move. This does not invoke changeset publish or publish a package.
# Inspect rewritten workspace ranges and LICENSE/NOTICE/README/dist in each tarball.
set -e
here=$(cd "$(dirname "$0")" && pwd)
repo=$(cd "$here/../../../.." && pwd)
out=${1:-/tmp/w36-g2-pack}
mkdir -p "$out"

for package in core platform-web react; do
  echo "══ $package"
  cd "$repo/packages/$package"
  pnpm publish --dry-run --no-git-checks
  pnpm pack --pack-destination "$out" > /dev/null
done

cd "$out"
for tarball in *.tgz; do
  echo "── $tarball"
  tar -tzf "$tarball" | grep -E "package/(LICENSE|NOTICE|README.md)$" || echo "  MISSING a required file"
  echo "  dist entries: $(tar -tzf "$tarball" | grep -c '^package/dist/')"
  tar -xOzf "$tarball" package/package.json | python3 -c "import json,sys; d=json.load(sys.stdin); print('  version', d['version']); print('  dependencies', json.dumps(d.get('dependencies', {}))); print('  peerDependencies', json.dumps(d.get('peerDependencies', {})))"
  echo "  size: $(wc -c < "$tarball") bytes"
done
