#!/bin/sh
# The 0.25.0 publish rehearsal: W36 G2's dry-run.sh (0.24.0), with only the
# scratch directory moved. The same dry publish and pack commands per package.
# This does not invoke changeset publish or publish a package; `pnpm release` is
# the user's. pack-check.py then asserts the tarballs and counts their exports.
set -e
here=$(cd "$(dirname "$0")" && pwd)
repo=$(cd "$here/../../../.." && pwd)
out=${1:-$repo/.vitrea-tmp/rel-0.25.0-pack}
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
