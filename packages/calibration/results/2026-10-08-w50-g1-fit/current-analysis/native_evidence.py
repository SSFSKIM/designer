"""DL5g typed provenance only: three original native runs, never a PNG-shaped document pin.

The completed reader has already verified each role report/export and run identity. This pure
projection retains those complete evidence records and the ORIGINAL G0 support prose. Values,
masks, repeats and budgets remain separate; an envelope certifies no metric or landing verdict.
The parent may serialize each object and content-pin those bytes for the pre-fit reader.
"""
import copy
from pathlib import PurePosixPath
import re


def digest(value):
    if not isinstance(value, str) or not re.fullmatch('[0-9a-f]{64}', value):
        raise ValueError('Native provenance needs complete content hashes')


def relative(value, suffix):
    if not isinstance(value, str) or not value or not value.endswith(suffix):
        raise ValueError('Native provenance path has the wrong artifact type')
    path = PurePosixPath(value)
    if path.is_absolute() or '..' in path.parts or str(path) != value:
        raise ValueError('Native provenance path escapes its declared source root')


def content_pin(value, suffix):
    if not isinstance(value, dict) or set(value) != {'path', 'sha256'}:
        raise ValueError('Native provenance requires an exact content pin')
    relative(value['path'], suffix); digest(value['sha256'])


def envelope(original, cell, provenance):
    """Return a content-pinnable native record for one exact original reference statistic."""
    role = original.get('role')
    if role not in ('calibration', 'validation') or not isinstance(original.get('support'), str) \
            or not original['support'] or any(original.get(k) != cell.get(k) for k in ('profile', 'scene', 'role')) \
            or original.get('nativeIdentity') != cell.get('id') \
            or original.get('referenceIdentity') != cell.get('reference') \
            or original.get('statistic') not in cell.get('statistics', {}):
        raise ValueError('Native envelope differs from its original G0 identity/support/statistic')
    if cell['id'] != original['profile']+'/'+original['scene']:
        raise ValueError('Native cell identity differs from original profile/scene')
    native_read, batch, export = (provenance[k] for k in ('nativeRead', 'nativeBatch', 'nativeExport'))
    content_pin(native_read, '.json.gz'); content_pin(batch, '.json')
    if not isinstance(export, dict) or set(export) != {'role', 'root', 'indexSha256'} \
            or export['role'] != role or not isinstance(export['root'], str) \
            or not PurePosixPath(export['root']).is_absolute() or '..' in PurePosixPath(export['root']).parts:
        raise ValueError('Native envelope requires its original exposed role export')
    digest(export['indexSha256'])
    runs = cell.get('runs', [])
    if [r.get('run') for r in runs] != [1, 2, 3]:
        raise ValueError('Native envelope requires three ordered original runs')
    records = []
    for run in runs:
        record = run.get('evidence', {})
        if run.get('dependency') != cell['reference'] or record.get('run') != run['run'] \
                or record.get('cell') != cell['id'] or record.get('roles') != [role] \
                or record.get('kind') != 'frame' or not isinstance(record.get('native'), dict):
            raise ValueError('Native envelope run/role/dependency/metadata differs')
        relative(record.get('path'), '.png')
        for name in ('sha256', 'declarationSha256', 'manifestSha256'): digest(record.get(name))
        records.append(copy.deepcopy(record))
    return dict(schema='w50-native-three-run-evidence-1',
        **{key:copy.deepcopy(original[key]) for key in
           ('profile', 'scene', 'statistic', 'nativeIdentity', 'referenceIdentity', 'role', 'support')},
        runs=records, nativeRead=copy.deepcopy(native_read), nativeBatch=copy.deepcopy(batch),
        nativeExport=copy.deepcopy(export))


def source_probe():
    """One synthetic provenance projection, with no report, export or image I/O."""
    row = dict(profile='synthetic', scene='cell', statistic='deep8-channel-median', role='calibration',
        nativeIdentity='synthetic/cell', referenceIdentity='synthetic/no-glass', support='Original G0 prose.')
    runs = [dict(run=n, dependency=row['referenceIdentity'], evidence=dict(run=n,
        path=f'run-{n}/synthetic/cell.png', sha256=str(n)*64, declarationSha256='a'*64,
        manifestSha256='b'*64, roles=['calibration'], kind='frame', cell=row['nativeIdentity'],
        native={'synthetic': True})) for n in (1, 2, 3)]
    cell = dict(id=row['nativeIdentity'], profile=row['profile'], scene=row['scene'], role=row['role'],
        reference=row['referenceIdentity'], statistics={row['statistic']: {}}, runs=runs)
    provenance = dict(nativeRead={'path': 'synthetic/calibration.json.gz', 'sha256': 'c'*64},
        nativeBatch={'path': 'synthetic/read-batch.json', 'sha256': 'd'*64},
        nativeExport={'role': 'calibration', 'root': '/synthetic/calibration', 'indexSha256': 'e'*64})
    result = envelope(row, cell, provenance)
    if result['support'] != row['support'] or len(result['runs']) != 3:
        raise ValueError('Synthetic native provenance projection failed')
    return {'status': 'SOURCE_ONLY'}
