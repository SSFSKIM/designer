#!/usr/bin/env python3
"""Publish the frozen reader/scorer outputs without rewriting their evidence.

Run after both serial reads and the unchanged bound scorer have completed:
    python3 publish.py /tmp/vitrea-w28-g2-read
The captures stay at their recorded scratch paths. JSON copies remain byte-identical.
"""
import hashlib
import json
from pathlib import Path
import shutil
import sys
from statistics import mean

HERE = Path(__file__).resolve().parent
G1 = HERE.parent / '2026-09-14-w28-g1-silhouette'
scratch = Path(sys.argv[1]).resolve()
gpu = json.loads((scratch / 'checking.json').read_text())
css = json.loads((scratch / 'css.json').read_text())
verdict = json.loads((scratch / 'verdict.json').read_text())
seal = json.loads((G1 / 'fitted-endpoint.json').read_text())
declaration = json.loads((G1 / 'declaration.json').read_text())
planned = json.loads((G1 / 'dry-run.json').read_text())['plannedRows']
key = lambda row: row['profile'] + '/' + row['scene']
holdout = set(seal['holdout']['cells'])
assert gpu['patchSha256'] == css['patchSha256'] == seal['patchSha256']
assert gpu['renderer'] == 'webgpu' and css['renderer'] == 'css'
assert len(gpu['rows']) == len({key(r) for r in gpu['rows']}) == len(planned)
assert {key(r) for r in gpu['rows']} == set(planned)
assert len(css['rows']) == len({key(r) for r in css['rows']})
assert {key(r) for r in css['rows']} == set(planned) - holdout
assert {key(r) for r in gpu['rows'] if r['isHoldout']} == holdout
assert not any(r['isHoldout'] for r in css['rows'])
for matrix in (gpu, css):
    assert matrix['machineAccessibility']['reduceTransparency'] == 0
    assert matrix['machineAccessibility']['increaseContrast'] == 0
    for row in matrix['rows']:
        assert row['repeats'] == 2
        assert hashlib.sha256(Path(row['capture']).read_bytes()).hexdigest() == row['captureSha256']

def save(name, value):
    with (HERE / name).open('x') as handle:
        json.dump(value, handle, indent=2)
        handle.write('\n')

copies = {}
for source, target in [('checking.json', 'frozen-checking-matrix.json'),
                       ('css.json', 'css-matrix.json'), ('verdict.json', 'verdict.json')]:
    assert not (HERE / target).exists()
    shutil.copyfile(scratch / source, HERE / target)
    digest = hashlib.sha256((scratch / source).read_bytes()).hexdigest()
    assert hashlib.sha256((HERE / target).read_bytes()).hexdigest() == digest
    copies[target] = {'source': str(scratch / source), 'sha256': digest}
gpu_rows = {key(r): r for r in gpu['rows']}
css_rows = {key(r): r for r in css['rows']}
holdout_rows = []
for declared in declaration['holdout']['rows']:
    row = gpu_rows[declared['cell']]
    holdout_rows.append({'cell': declared['cell'], 'bodyDeltaE': row['body']['deltaE'],
                         'webY': row['body']['webY'], 'nativeY': row['body']['nativeY'],
                         'silhouetteMinusSourceEncoded': declared['offset'],
                         'repeats': row['repeats'],
                         'preAttestationRecovered': row['preAttestationRecovered']})
save('holdout.json', holdout_rows)
clause3 = []
for row in gpu['rows']:
    if not row['scored']:
        continue
    threshold = verdict['perProfile'][row['profile']]['clause2']['threshold']
    clause3.append({'cell': key(row), 'bodyDeltaE': row['body']['deltaE'],
                    'threshold': threshold, 'clause3Ceiling': 2 * threshold,
                    'multipleOfThreshold': row['body']['deltaE'] / threshold,
                    'multipleOfClause3Ceiling': row['body']['deltaE'] / (2 * threshold),
                    'holds': row['body']['deltaE'] <= 2 * threshold})
save('clause3-per-cell.json', clause3)
coherence = []
for cell, row in css_rows.items():
    web = gpu_rows[cell]
    coherence.append({'cell': cell, 'cssY': row['body']['webY'],
                      'webgpuY': web['body']['webY'], 'nativeY': web['body']['nativeY'],
                      'absoluteBodyYGap': abs(row['body']['webY'] - web['body']['webY'])})
per_profile = {}
for profile in sorted({r['profile'] for r in css['rows']}):
    subset = [r for r in coherence if r['cell'].startswith(profile + '/')]
    per_profile[profile] = {'cells': len(subset),
                            'meanAbsoluteBodyYGap': mean(r['absoluteBodyYGap'] for r in subset),
                            'widest': max(subset, key=lambda r: r['absoluteBodyYGap'])}
save('css-coherence.json', {'recordOnly': True, 'notAnIsolatedJensenTerm': True,
                            'perProfile': per_profile, 'rows': coherence})
save('publication.json', {'copies': copies, 'webgpuRows': len(gpu_rows),
                          'cssRows': len(css_rows), 'holdoutCells': len(holdout_rows),
                          'checkingCells': len(clause3), 'adoptsNoFloor': True,
                          'capturesRetainedAt': str(scratch)})
print(json.dumps({'publication': copies, 'holdout': holdout_rows,
                  'coherence': per_profile}, indent=2))
