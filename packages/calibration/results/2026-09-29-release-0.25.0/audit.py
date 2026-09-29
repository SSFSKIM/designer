"""Close the 0.25.0 chain: re-read every count from the logs and write audit.json.

    python3 audit.py

Nothing here is typed by hand into the record: each number is parsed from the
step log that produced it and asserted, so the README and the c9d row can quote
this file. Also asserts that the release branch touches no material, profile,
matrix, generation or golden path relative to origin/main. Writes exclusively.
"""
import json
import re
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
read = lambda name: (HERE / name).read_text()


def suite(name):
    text = read(name)
    counts = {kind: int(n) for n, kind in re.findall(
        r'^\s+(\d+) (passed|failed|skipped|flaky|did not run|interrupted)', text, re.M)}
    return counts


status = [line for line in read('chain-status.txt').splitlines() if 'exit=' in line]
exits = dict(line.split(' exit=') for line in status)
assert exits.pop('platform-web') == '1'
assert all(v == '0' for v in exits.values()), exits

units = read('chain-units.txt')
tests = {p: int(n) for p, n in re.findall(r'([^\s]+) test:       Tests\s+(\d+) passed', units)}
files = {p: int(n) for p, n in re.findall(r'([^\s]+) test:  Test Files\s+(\d+) passed', units)}
assert not re.search(r'Tests .*(failed|skipped)', units)

suites = {name: suite(f'chain-{name}.txt') for name in
          ['goldens', 'gpu', 'platform-web', 'platform-web-run2', 'react-e2e', 'demo-e2e']}
assert suites['goldens'] == {'passed': 34}
assert suites['gpu'] == {'passed': 49}
assert suites['platform-web'] == {'failed': 246, 'passed': 165}
assert read('chain-platform-web.txt').count("Executable doesn't exist") == 246
assert suites['platform-web-run2'] == {'passed': 411}
assert suites['react-e2e'] == {'skipped': 3, 'passed': 174}
assert suites['demo-e2e'] == {'passed': 83}

freeze = [read(f'chain-freeze-{w}.txt').strip() for w in ('open', 'close')]
assert freeze == ['26.5 freeze intact: 1818 entries'] * 2
digests = read('chain-digests.txt')
assert digests.count('\nok   ') + digests.startswith('ok   ') == 6 and 'all six digests unmoved' in digests
goldens = read('chain-goldens-bytes.txt')
assert '13 golden PNGs, byte-identical to v0.24.0 and HEAD' in goldens
tree = re.search(r'totals\s+captures (\d+)\s+match (\d+)\s+mismatch (\d+)\s+misfiled (\d+)\s+'
                 r'superseded (\d+)\s+unreadable (\d+)\s+no-row (\d+)', read('chain-capture-tree.txt'))
gated = re.findall(r'TOTAL at a shipped document\s+(\d+) row\(s\),\s+(\d+) gated', read('chain-gated-count.txt'))
assert gated == [('1107', '229'), ('786', '230')]

runs = [json.loads(line) for line in read('browser-runs.txt').splitlines()]
preflights = [r for r in runs if 'settings' in r]
for row in preflights:
    assert row['admitted'] and row['foreignProcessCount'] == 0 and row['idleSeconds'] >= 60
    assert row['settings'] == dict(ButtonShapesEnabled='0', NSGlassTintAmount='0.5',
                                   increaseContrast='0', reduceTransparency='0')
waits = (HERE / 'x6-waits.txt').read_text().splitlines() if (HERE / 'x6-waits.txt').exists() else []

pack = json.loads(read('pack-check.json'))
changed = subprocess.check_output(['git', '-C', str(ROOT), 'diff', '--name-only', 'origin/main...HEAD'],
                                  text=True).splitlines()
own = 'packages/calibration/results/2026-09-29-release-0.25.0/'
protected = [p for p in changed if p.startswith('packages/calibration/') and not p.startswith(own)
             or p.startswith('packages/renderer-webgpu/e2e/goldens/')
             or p.endswith('renderer-webgpu/src/material.ts')
             or p.startswith('packages/platform-web/src/macos27-profile')
             or p.startswith('packages/platform-web/src/dark-profile')]
assert protected == [], protected

result = dict(
    release='0.25.0', head=subprocess.check_output(['git', '-C', str(ROOT), 'rev-parse', 'HEAD'],
                                                   text=True).strip(),
    chainStatus=status, freeze=[1818, 1818],
    captureTree=dict(zip(['captures', 'match', 'mismatch', 'misfiled', 'superseded', 'unreadable',
                          'noRow'], map(int, tree.groups()))),
    digests=[line.split()[1] + ' ' + line.split()[3] for line in digests.splitlines()
             if line.startswith('ok ')],
    unitTests=tests, unitFiles=files, unitTotal=sum(tests.values()), unitFileTotal=sum(files.values()),
    suites=suites,
    platformWebRun1='246 Firefox/WebKit launch errors (executable absent from the Playwright cache), '
                    '0 other failures; run 2 after installing firefox-1538 and webkit-2336',
    goldenPNGs=13, gated=dict(macOS26_5=dict(rows=1107, gated=229), macOS27=dict(rows=786, gated=230)),
    x6=dict(preflights=len(preflights), labels=[r['label'] for r in preflights],
            minimumIdleSeconds=min(r['idleSeconds'] for r in preflights),
            waitedSeconds=[r['waitedSeconds'] for r in preflights],
            pollsBeyondFirst=len(waits), foreignCounts=[r['foreignProcessCount'] for r in preflights]),
    tarballs={r['name']: dict(bytes=r['bytes'], exports=r['exports'], dependencies=r['dependencies'])
              for r in pack},
    branchPathsTouchingMaterialOrEvidence=protected)
with (HERE / 'audit.json').open('x') as f:
    json.dump(result, f, indent=2)
    f.write('\n')
print(json.dumps(result, indent=2))
