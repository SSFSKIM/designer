#!/usr/bin/env bash
# W33 G1b closing chain, after the one sealed read (claims §5.172).
set -euo pipefail
cd "$(dirname "$0")/../../../.."
HERE=packages/calibration/results/2026-09-22-w33-g1b-rim-fit
pnpm -r build > "$HERE/chain-build.txt" 2>&1
pnpm -r lint > "$HERE/chain-lint.txt" 2>&1
pnpm -r test > "$HERE/chain-test.txt" 2>&1
python3 "$HERE/../2026-09-16-w29-freeze/freeze.py" verify > "$HERE/freeze-close.txt"
python3.12 "$HERE/browser-checks.py" goldens > "$HERE/goldens.txt" 2>&1
python3.12 "$HERE/browser-checks.py" window > "$HERE/window-activation.txt" 2>&1
pnpm --fail-if-no-match --filter @vitrea/calibration run check-capture-tree > "$HERE/check-capture-tree-close.txt" 2>&1
python3.12 - <<'PY'
import hashlib,json
from pathlib import Path
h=Path('packages/calibration/results/2026-09-22-w33-g1b-rim-fit')
pins=json.loads((h/'unmoved-byte-pins.json').read_text())
for p,sha in pins.items():
    assert hashlib.sha256(Path(p).read_bytes()).hexdigest()==sha,p
(h/'unmoved-byte-check.txt').write_text(f'{len(pins)} pinned document/source/fixture/golden files byte-identical.\n')
PY
printf 'build lint test freeze goldens window capture-tree byte-pins: PASS\n' > "$HERE/chain.txt"
