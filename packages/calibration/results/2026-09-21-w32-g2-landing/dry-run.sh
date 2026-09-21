#!/bin/sh
# The publish rehearsal at 0.21.0, short of publishing (claims §5.165 §5).
#
# W29 G4's script by way of W30 G4's, unchanged but for this line and the scratch directory.
#
# `pnpm publish --dry-run` per published package, and then the two things npm would get
# wrong on its own, read off the packed tarball rather than assumed: every `workspace:`
# range rewritten to a real one, and `dist/`, `LICENSE`, `NOTICE` and `README.md` present.
# `pnpm pack` is what produces the tarball the rehearsal inspects; it writes to scratch.
set -e
here=$(cd "$(dirname "$0")" && pwd)
repo=$(cd "$here/../../../.." && pwd)
out=${1:-/tmp/w32-g2-pack}
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
