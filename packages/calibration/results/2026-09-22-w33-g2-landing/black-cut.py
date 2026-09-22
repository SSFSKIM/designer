#!/usr/bin/env python3
"""Select X1 from G0's byte-identical referee, regenerated here (§5.173, DL4).

Run referee.py first with the canonical VITREA_WEB_CAPTURES. Its historical
native census remains diagnostic; this cut admits only shipped matrix rows.
"""
import hashlib
import json
from pathlib import Path
import re

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
referee = json.loads((HERE/'referee.json').read_text())
assert referee['includeHoldout'] is False
matrix_path = ROOT/'packages/calibration/results/matrix.json'
assert referee['matrixSha256'] == hashlib.sha256(matrix_path.read_bytes()).hexdigest()
scenes = json.loads((ROOT/'apps/reference-apple/scenes.json').read_text())
scene = {s['id']: s for s in scenes['scenes']}
roles = {s: role for role, ids in scenes['split'].items() if not role.startswith('$') for s in ids}
by_key = {(r['profile'], r['scene']): r for r in referee['black']}
rows = []
for c in json.loads(matrix_path.read_text())['cells']:
    p, sid = c['key']['profileKey'], c['key']['sceneId']
    s = scene[sid]
    if not (p.startswith('apple-macos-27.0-') and '-standard-' in p and c['tier'] == 'texture'
            and c['key']['web']['renderer'] == 'webgpu'
            and roles[sid] in ('calibration', 'validation', 'probe')
            and s['state'] in ('rest', 'inactive') and s['background'] in referee['blackBackdrops']
            and scenes['components'][s['component']]['kind'] in ('rrect', 'capsule')):
        continue
    named = re.findall(r'(?:materialProfile|recededProfile)=(\S+) sha256:([0-9a-f]{12})',
                       c['key']['web']['capturePath'])
    assert named
    for path, sha in named:
        assert hashlib.sha256((ROOT/path).read_bytes()).hexdigest()[:12] == sha
    rows.append(dict(**by_key[(p, sid)], capturePath=c['key']['web']['capturePath']))
rows.sort(key=lambda r: (r['profile'], r['scene']))
assert rows
artifact = dict(atDocuments='shipped', withHoldout=False, blackBackdrops=referee['blackBackdrops'],
                targets=dict(blackFraction=0, aboveOne=0), missed=[], cells=rows)
(HERE/'black-cut.json').write_text(json.dumps(artifact, indent=2)+'\n')
print('X1', len(rows), 'cells')
for mask in ('integer', 'analytic'):
    print(mask, {k: sum(r[mask][k] for r in rows) for k in
                 ('pixels', 'backdropBlack', 'nativeNonzero', 'aboveZero', 'aboveOne')})
excluded = [r for r in referee['black'] if '27.0' in r['profile'] and
            (r['profile'], r['scene']) not in {(s['profile'],s['scene']) for s in rows}]
print('Excluded from X1, retained in the 232-cell referee:')
for r in excluded:
    print(r['profile'], r['scene'], r['integer'])
