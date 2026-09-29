"""Re-derive the adopted L1 record from current and named W33 rows (§5.180 clause 8).

This is a record producer, not a passing verdict. The owner test derives these
figures independently and enforces the declared absolute and growth clauses.

W41 G2 (c9a §5.193): W36 G2's `l1-cut.py`, ported onto W40's generation store. The rows
are the current union (`--stage DIR`: the scratch union a stage would publish); the W33
baseline stays the declaration's, now resolved as its (active, receded) pair by
`matrix_store.load_generation` rather than read from the file the declaration names.
`matrixSha256` is the legacy-envelope digest of those rows, the same witness the owner
test takes over the canonical union. The shipped check reads both named documents
against the files on disk, as the owner test does, where W36 read its own seal manifest.

    python3.12 -B l1-cut.py [--stage DIR] [--out PATH]
"""
import argparse
import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
CAL = HERE.parents[2]
ROOT = CAL.parent.parent
sys.path.insert(0, str(HERE))
import referee_source  # noqa: E402
G0 = CAL / 'results/2026-09-24-w36-g0-level-cut'
parser = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
referee_source.add_source_arguments(parser)
parser.add_argument('--out', type=Path, default=HERE / 'l1-cut.json')
parser.add_argument('--claims', default='c9a §5.193')
args = parser.parse_args()
d = json.loads((G0 / 'l1-declaration.json').read_text())
spec = json.loads((ROOT / 'apps/reference-apple/scenes.json').read_text())
allowed = set(spec['split']['calibration'] + spec['split']['validation'])
shipped = {f'packages/calibration/profiles/{path.name}':
           hashlib.sha256(path.read_bytes()).hexdigest()[:12]
           for path in sorted((CAL / 'profiles').glob('*.json'))}

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
    for c in referee_source.generation(generation['active'], generation['receded'])[0]:
        if selected(c) and f'-{scheme}-standard-' in c['key']['profileKey']:
            for digest in [generation['active'], generation['receded']]:
                assert 'sha256:' + digest in c['key']['web']['capturePath']
            assert key(c) not in baseline
            baseline[key(c)] = c
source = referee_source.load(args)
rows = []
for c in source.rows:
    if not selected(c):
        continue
    old = baseline[key(c)]
    named = referee_source.store.documents(c)
    assert len(named) == 2 and all(shipped.get(path) == sha for _, path, sha in named), key(c)
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
result = dict(claims=args.claims, **({'source': source.described} if source.stage else {}),
              atDocuments='shipped', withHoldout=False,
              matrixSha256=source.legacy_sha256,
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
