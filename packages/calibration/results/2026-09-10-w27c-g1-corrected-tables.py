"""Create-only, scale-separated tables from completed corrected capture records."""
import collections
import hashlib
import json
import pathlib
import sys

baseline_path, checked_path, holdout_path, output_path = map(pathlib.Path, sys.argv[1:])
baseline, checked, holdout = [json.loads(p.read_text()) for p in
                             [baseline_path, checked_path, holdout_path]]
before = {(r['profile'], r['scene']): r for r in baseline['rows']}
groups = collections.defaultdict(list)
for row in checked['rows'] + holdout['rows']:
    assert not row['problems']
    assert row['geometry']['devicePixelRatio'] == row['scale']
    assert row['geometry']['viewport'] == {'width': 320, 'height': 200}
    groups[(row['profile'], row['scale'], row['set'])].append(row)

tables = []
for (profile, scale, split), rows in sorted(groups.items()):
    old = [before.get((r['profile'], r['scene'])) for r in rows]
    tables.append({
        'profile': profile, 'scale': scale, 'set': split, 'n': len(rows),
        'activeBaselineMeanDeltaE': None if any(r is None for r in old) else
            sum(r['deltaE']['mean'] for r in old) / len(old),
        'inactiveMeanDeltaE': sum(r['deltaE']['mean'] for r in rows) / len(rows),
        'inactiveMaxCellMeanDeltaE': max(r['deltaE']['mean'] for r in rows),
        'inactiveMeanBodyDeltaE': sum(r['body']['deltaE'] for r in rows) / len(rows),
    })
triples = []
for row in checked['rows']:
    if row['profile'].endswith('light-standard') and row['sourceScene'] in [
            'checkerboard__capsule-button__rest', 'checkerboard__rrect-md__rest',
            'photo__rrect-md__rest']:
        triples.append({k: row[k] for k in ['profile', 'scale', 'scene', 'body']})

result = {
    'declaration': '2026-09-10-w27c-g1-corrected-declaration.json',
    'definitions': checked['definitions'],
    'sources': [{'path': str(p), 'sha256': hashlib.sha256(p.read_bytes()).hexdigest()}
                for p in [baseline_path, checked_path, holdout_path]],
    'tables': tables,
    'lightStandardBodyTriples': triples,
    'holdout': {'status': 'spent', 'rows': len(holdout['rows']),
                'baseline': 'Not separately captured on holdout; no before-value invented.',
                'selection': 'No refit follows the frozen holdout reading.'},
}
with output_path.open('x') as f:
    json.dump(result, f, indent=2)
    f.write('\n')
