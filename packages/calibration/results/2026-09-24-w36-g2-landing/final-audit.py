"""Close the landed byte scope, counts and X6 receipts (§5.180 clause 8)."""
import hashlib
import json
from pathlib import Path
import re
import subprocess

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
CAL = HERE.parent.parent
sha = lambda raw: hashlib.sha256(raw).hexdigest()
confirmation = json.loads((HERE / 'evidence-confirmation.json').read_text())
for entry in confirmation['protectedFiles']:
    assert sha((ROOT / entry['path']).read_bytes()) == entry['sha256']
goldens = []
for path in sorted((ROOT / 'packages/renderer-webgpu/e2e/goldens').glob('*.png')):
    relative = str(path.relative_to(ROOT))
    before = subprocess.check_output(['git', '-C', str(ROOT), 'show', 'fe3067a8:' + relative])
    assert path.read_bytes() == before
    goldens.append(dict(path=relative, sha256=sha(before)))
assert len(goldens) == 13
units = (HERE / 'chain-units.txt').read_text()
counts = {p: int(n) for p, n in re.findall(r'([^\s]+) test:       Tests\s+(\d+) passed', units)}
files = {p: int(n) for p, n in re.findall(r'([^\s]+) test:  Test Files\s+(\d+) passed', units)}
assert sum(counts.values()) == 2761 and sum(files.values()) == 196
browser = [json.loads(line) for line in (HERE / 'browser-runs.txt').read_text().splitlines()]
preflights = [r for r in browser if 'settings' in r]
for row in preflights:
    assert row['settings'] == dict(ButtonShapesEnabled='0', NSGlassTintAmount='0.5',
        increaseContrast='0', reduceTransparency='0')
    assert row['idleSeconds'] >= 60 and row['captureProcessesToLaunch'] == 1
assert len(preflights) == 9
assert [r['foreignProcessCount'] for r in preflights] == [0] * 7 + [1, 1]
assert (HERE / 'laws-black.png').read_bytes() == (HERE / 'laws-black-repeat.png').read_bytes()
changed = subprocess.check_output(['git', '-C', str(ROOT), 'diff', '--name-only', 'fe3067a8'], text=True).splitlines()
assert not any('apple-macos-26.5-' in path for path in changed)
assert not any('/profiles/' in path or path.endswith('results/matrix.json') for path in changed)
result = dict(claims='c9a §5.180', protectedFilesStillUnchanged=len(confirmation['protectedFiles']),
    goldenPNGs=goldens, unitCounts=counts, unitFiles=files,
    unitTotal=sum(counts.values()), unitFileTotal=sum(files.values()),
    browserPreflightCount=len(preflights), minimumIdleSeconds=min(r['idleSeconds'] for r in preflights),
    foreignCounts=[r['foreignProcessCount'] for r in preflights],
    foreignQualification='Both count1 readings are PID85913, the owned Vite-launch shell whose command text contains the Chromium config. The raw census is retained, not rewritten. No foreign browser was closed; final eye repeats are byte-identical.',
    react='173 passed /3 skipped /1 Firefox morph-release failure; first run, not rerun',
    demo='61 full-suite passes; after black control/prose repair, 10 laws passes; 46 demo units unchanged',
    eye='Hardware apple/metal-3, no fallback, two stage PNGs byte-identical',
    frozenPathsChanged=[], materialOrMatrixChanged=[])
with (HERE / 'final-audit.json').open('x') as f:
    json.dump(result, f, indent=2)
    f.write('\n')
print('Units', result['unitTotal'], '/', result['unitFileTotal'], 'files; goldens', len(goldens), 'PNGs byte-identical')
print('X6', len(preflights), 'preflights; minimum idle', result['minimumIdleSeconds'], 'foreign counts', result['foreignCounts'])
print(result['foreignQualification'])
