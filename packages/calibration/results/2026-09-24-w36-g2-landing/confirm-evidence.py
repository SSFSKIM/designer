"""Read-only material, bound-set and M2 confirmation (§5.180 clause 8)."""
import hashlib
import json
from pathlib import Path
import re
import subprocess

HERE = Path(__file__).resolve().parent
CAL = HERE.parent.parent
ROOT = CAL.parent.parent
G1 = HERE.parent / '2026-09-24-w36-g1-black-branch'
BASE = 'fe3067a8'
def sha(raw):
    return hashlib.sha256(raw).hexdigest()
def git(path):
    return subprocess.check_output(['git', '-C', str(ROOT), 'show', BASE + ':' + path])

sealed = json.loads((G1 / 'sealed-manifest.json').read_text())['documents']
for name, record in sealed.items():
    assert sha((CAL / 'profiles' / name).read_bytes()) == record['fileSha256']
paths = subprocess.check_output(['git', '-C', str(ROOT), 'ls-tree', '-r', '--name-only', BASE], text=True).splitlines()
protected = [p for p in paths if p.startswith(('packages/renderer-webgpu/src/',
    'packages/platform-web/src/', 'packages/core/src/', 'packages/react/src/',
    'packages/calibration/profiles/', 'packages/calibration/results/superseded/',
    'packages/renderer-webgpu/e2e/golden/')) or p == 'packages/calibration/results/matrix.json']
audit = []
for path in protected:
    before, after = git(path), (ROOT / path).read_bytes()
    assert before == after, path
    audit.append(dict(path=path, sha256=sha(after)))
thresholds = 'packages/calibration/test/adopted-thresholds.test.ts'
old, now = git(thresholds).decode(), (ROOT / thresholds).read_text()
bound_sets = {}
for name, end in [('PREDICATE_EXCLUDES', '];'), ('MISSED_27_ROWS', '\n};')]:
    pattern = r'(?:const|export const) ' + name + r'\b'
    def block(text):
        start = re.search(pattern, text).start()
        return text[start:text.index(end, start) + len(end)]
    before, after = block(old), block(now)
    assert before == after
    bound_sets[name] = dict(sha256=sha(after.encode()), unchanged=True)

cut = json.loads((G1 / 'chroma-cut.json').read_text())
recorded = json.loads((G1 / 'm2-rebaseline.json').read_text())
current = {(c['key']['profileKey'], c['key']['sceneId']): c for c in
    json.loads((CAL / 'results/matrix.json').read_text())['cells'] if c['key']['web']['renderer'] == 'webgpu'}
index = json.loads((CAL / 'results/superseded/index.json').read_text())
def generation(digest):
    return {(c['key']['profileKey'], c['key']['sceneId']): c for c in
        json.loads((CAL / 'results/superseded' / index['byDocumentSha256'][digest]).read_text())['cells']
        if c['key']['web']['renderer'] == 'webgpu' and 'sha256:' + digest in c['key']['web']['capturePath']}
w33 = {**generation('6e509c7f76cc'), **generation('eab099cc6698')}
w31 = {**generation('d0c389d70456'), **generation('880ab1e31450')}
rows = []
for r in recorded['cells']:
    key = (r['profile'], r['scene'])
    value = lambda c: c['material']['interiorStdDevWeb']['value']
    previous, initial, now_value = value(w33[key]), value(w31[key]), value(current[key])
    row = dict(profile=key[0], scene=key[1], w31PreFit=initial, waveReference=previous,
               value=now_value, perWave=(now_value - previous) / previous,
               cumulative=(now_value - initial) / initial,
               passStop=abs((now_value - previous) / previous) <= .02)
    assert row == r
    rows.append(row)
assert len(rows) == 26 and all(r['perWave'] == 0 for r in rows)
result = dict(claims='c9a §5.180', unchangedFrom=BASE, protectedFiles=audit,
              boundSets=bound_sets, sealedDocuments=sealed,
              m2=dict(referenceGeneration=cut['referenceGeneration'], cells=rows,
                      cumulativeMin=min(r['cumulative'] for r in rows),
                      cumulativeMax=max(r['cumulative'] for r in rows)))
with (HERE / 'evidence-confirmation.json').open('x') as f:
    json.dump(result, f, indent=2)
    f.write('\n')
print('Unchanged protected files:', len(audit))
print('M2:', len(rows), 'zero per-wave increments; cumulative',
      result['m2']['cumulativeMin'] * 100, result['m2']['cumulativeMax'] * 100)
print('PREDICATE_EXCLUDES and MISSED_27_ROWS byte-identical to opening main')
