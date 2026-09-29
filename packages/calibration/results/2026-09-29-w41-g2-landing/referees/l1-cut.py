"""Re-derive the adopted L1 record from current and named W33 rows (§5.180 clause 8).

This is a record producer, not a passing verdict. The owner test derives these
figures independently and enforces the declared absolute and growth clauses.
"""
import argparse
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
CAL = HERE.parent.parent
G0 = HERE.parent / '2026-09-24-w36-g0-level-cut'
G1 = HERE.parent / '2026-09-24-w36-g1-black-branch'
parser = argparse.ArgumentParser()
parser.add_argument('--matrix', type=Path, default=CAL / 'results/matrix.json')
parser.add_argument('--out', type=Path, default=HERE / 'l1-cut.json')
args = parser.parse_args()
d = json.loads((G0 / 'l1-declaration.json').read_text())
spec = json.loads((CAL.parent.parent / 'apps/reference-apple/scenes.json').read_text())
allowed = set(spec['split']['calibration'] + spec['split']['validation'])
sealed = json.loads((G1 / 'sealed-manifest.json').read_text())['documents']

def selected(c):
    return (c['key']['profileKey'].startswith('apple-macos-27.0-') and
            '-standard-' in c['key']['profileKey'] and c['tier'] == 'texture' and
            c['key']['web']['renderer'] == 'webgpu' and c['key']['sceneId'] in allowed)

def key(c):
    return c['key']['profileKey'] + '/' + c['key']['sceneId']

def value(c, metric):
    return c.get('material', {}).get(metric, {}).get('value')

baseline = {}
for scheme, generation in d['baselineGeneration'].items():
    for c in json.loads((CAL / generation['supersededFile']).read_text())['cells']:
        if selected(c) and f'-{scheme}-standard-' in c['key']['profileKey']:
            for digest in [generation['active'], generation['receded']]:
                assert 'sha256:' + digest in c['key']['web']['capturePath']
            assert key(c) not in baseline
            baseline[key(c)] = c
rows = []
for c in json.loads(args.matrix.read_text())['cells']:
    if not selected(c):
        continue
    old = baseline[key(c)]
    for name, document in sealed.items():
        scheme = 'dark' if '-dark-' in name else 'light'
        if f'-{scheme}-standard-' in c['key']['profileKey']:
            assert 'sha256:' + document['fileSha256'][:12] in c['key']['web']['capturePath']
    n, w = value(c, 'interiorMeanNative'), value(c, 'interiorMeanWeb')
    bn, bw = value(old, 'interiorMeanNative'), value(old, 'interiorMeanWeb')
    assert n == bn
    error = None if n is None or w is None else abs(w - n)
    before = None if bn is None or bw is None else abs(bw - bn)
    growth = None if error is None or before is None else error - before
    rows.append(dict(cell=key(c), capturePath=c['key']['web']['capturePath'], native=n, web=w,
                     baselineError=before, error=error, growth=growth,
                     status='UNMEASURED' if error is None else 'MEASURED',
                     existingMiss=before is not None and before > d['absoluteBound']))
rows.sort(key=lambda r: r['cell'])
result = dict(claims='c9a §5.180', atDocuments='shipped', withHoldout=False,
              matrixSha256=hashlib.sha256(args.matrix.read_bytes()).hexdigest(),
              absoluteBound=d['absoluteBound'], growthBound=d['growthBound'],
              baselineGeneration=d['baselineGeneration'], population=len(rows),
              measured=sum(r['error'] is not None for r in rows),
              missing=[r['cell'] for r in rows if r['error'] is None],
              absoluteMisses=[r for r in rows if r['error'] is not None and r['error'] > d['absoluteBound']],
              growthFailures=[r for r in rows if r['growth'] is not None and r['growth'] > d['growthBound']],
              cells=rows)
with args.out.open('x') as f:
    json.dump(result, f, indent=2)
    f.write('\n')
print('L1', result['population'], 'measured', result['measured'], 'missing', len(result['missing']),
      'absolute misses', len(result['absoluteMisses']), 'growth failures', len(result['growthFailures']),
      'maximum growth', max(r['growth'] for r in rows if r['growth'] is not None))
