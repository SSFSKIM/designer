"""Hash-verified role exports. Operational archiving never computes image statistics.

The archive of record contains raw admitted runs and their attestations, including blind bytes.
An analytical export contains only that role's frames, per-frame native metadata and necessary
no-glass dependencies. It never copies the raw manifest/admission that names other roles. Blind
exports are deliberately unavailable until G1's frozen-candidate exposure is implemented.
"""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import tempfile

HERE = Path(__file__).resolve().parent

def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def safe(root, rel):
    root, part = Path(root).resolve(), Path(rel)
    if part.is_absolute() or '..' in part.parts or not part.parts:
        raise ValueError('Archive path escapes its root')
    current = root
    for p in part.parts:
        current /= p
        if current.is_symlink():
            raise ValueError('Archive symlinks are refused')
    if not current.resolve().is_relative_to(root):
        raise ValueError('Archive path escapes its root')
    return current


def checked_rows(root, rows):
    names = [r['path'] for r in rows]
    if len(set(names)) != len(names) or 'index.json' in names or 'index.sha256' in names:
        raise ValueError('Duplicate or reserved archive path')
    for row in rows:
        path = safe(root, row['path'])
        if not path.is_file() or sha(path.read_bytes()) != row['sha256']:
            raise ValueError('Archive hash mismatch: ' + row['path'])
        if not set(row['roles']) <= {'calibration', 'validation', 'blind', 'operational'}:
            raise ValueError('Unknown archive role')
    return rows


def write_archive(source, out, rows):
    source, out = Path(source), Path(out)
    checked_rows(source, rows)
    if out.exists():
        raise ValueError('Archive destination exists; never overwrite evidence')
    out.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='.w50-archive-', dir=out.parent) as td:
        tree = Path(td)/'tree'; tree.mkdir()
        for row in rows:
            target = tree/row['path']; target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(safe(source, row['path']), target)
        doc = dict(schema='w50-role-archive-1', files=sorted(rows, key=lambda r: r['path']))
        raw = (json.dumps(doc, indent=2, allow_nan=False)+'\n').encode()
        (tree/'index.json').write_bytes(raw)
        (tree/'index.sha256').write_text(sha(raw)+'  index.json\n')
        verify_archive(tree)
        tree.rename(out)
    return sha(raw)


def verify_archive(root, expected_sha=None):
    root = Path(root)
    raw = safe(root, 'index.json').read_bytes()
    digest = sha(raw)
    if expected_sha is not None and digest != expected_sha:
        raise ValueError('Archive root hash differs from registered evidence')
    if safe(root, 'index.sha256').read_text() != digest+'  index.json\n':
        raise ValueError('Archive index hash mismatch')
    doc = json.loads(raw)
    if doc.get('schema') != 'w50-role-archive-1':
        raise ValueError('Unknown archive schema')
    checked_rows(root, doc['files'])
    actual = {str(p.relative_to(root)) for p in root.rglob('*') if p.is_file() or p.is_symlink()}
    expected = {r['path'] for r in doc['files']} | {'index.json', 'index.sha256'}
    if actual != expected:
        raise ValueError('Archive membership mismatch')
    return doc


def export_role(source, out, role, expected_sha=None):
    if role not in ('calibration', 'validation'):
        raise ValueError('blind export is closed until the frozen-candidate exposure')
    doc = verify_archive(source, expected_sha)
    rows = [dict(r, roles=[role]) for r in doc['files'] if role in r['roles']]
    return write_archive(source, out, rows)


def collect(sitting, manifest, plan, declaration_sha):
    """Bind every planned capture to an admitted run and its actual frame bytes; no pixels read."""
    sitting = Path(sitting).resolve()
    roles = {r['id']: [r['role']] for r in manifest['cells']}
    roles.update({r['id']: r['roles'] for r in manifest['references']})
    rows = []
    plan_sha = sha((HERE.parent/'sitting-g1.json').read_bytes())
    for p in plan['passes']:
        for run in range(1, p['runs']+1):
            directory = sitting/p['name']/f'run-{run}'
            admission = json.loads((directory/'admission.json').read_bytes())
            if admission.get('run') != run or admission.get('pass') != p['name']:
                raise ValueError('Run identity differs from its declared repetition/pass')
            if admission.get('admitted') is not True or admission.get('dry') is not False or \
                    admission.get('planSha256') != plan_sha or \
                    admission.get('declaration', {}).get('declarationSha256') != declaration_sha:
                raise ValueError('Run is not admitted under this declaration')
            raw = (directory/'manifest.json').read_bytes()
            if sha(raw) != admission['manifestSha256']:
                raise ValueError('Native manifest hash changed')
            native = json.loads(raw)
            expected = {k+'/'+s for k, ids in p['profiles'].items() for s in ids}
            if run == 1:
                expected |= {k+'/'+s for k, ids in p.get('run1Only', {}).items() for s in ids}
            if set(admission['frames']) != expected:
                raise ValueError('Admitted capture membership differs from the pass plan')
            found = set()
            for profile in native['profiles']:
                for f in profile['fixtures']:
                    cell = profile['profileKey']+'/'+f['sceneId']
                    if cell in found or cell not in expected:
                        raise ValueError('Unexpected or duplicate native fixture')
                    found.add(cell)
                    file = safe(directory, f['file'])
                    rel = str(file.relative_to(sitting))
                    rows.append(dict(path=rel, sha256=admission['frames'][cell], roles=roles.get(cell, ['operational']),
                                     kind='frame', cell=cell, run=run, native=f,
                                     declarationSha256=declaration_sha, manifestSha256=admission['manifestSha256']))
            if found != expected:
                raise ValueError('Native manifest is missing a planned fixture')
            frame_paths = {r['path'] for r in rows}
            for file in directory.rglob('*'):
                if file.is_symlink():
                    raise ValueError('Run has a symlink')
                if file.is_file() and str(file.relative_to(sitting)) not in frame_paths:
                    rows.append(dict(path=str(file.relative_to(sitting)), sha256=sha(file.read_bytes()),
                                     roles=['operational'], kind='attestation'))
    if sum(r['kind'] == 'frame' for r in rows) != 1600:
        raise ValueError('Incomplete sitting: exactly 1600 admitted frames required')
    return checked_rows(sitting, rows)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=('verify', 'export'))
    parser.add_argument('source', type=Path)
    parser.add_argument('--sha256', required=True, help='Registered archive index hash, not a path assertion')
    parser.add_argument('--out', type=Path)
    parser.add_argument('--role', choices=('calibration', 'validation'))
    args = parser.parse_args()
    if args.command == 'verify':
        doc = verify_archive(args.source, args.sha256)
        print(json.dumps(dict(verified=True, files=len(doc['files']))))
    else:
        if not args.out or not args.role:
            parser.error('export requires --out and --role')
        print(export_role(args.source, args.out, args.role, args.sha256))
