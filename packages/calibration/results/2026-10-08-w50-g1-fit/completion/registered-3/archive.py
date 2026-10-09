#!/Users/new/vitrea-w49/py/bin/python -I -B
"""Archive the executed r3 assembly exactly, and place its LIVE copy (DL5o, in DL5l's pattern).

After `run.py execute`, this writes, once each:
  evidence/completed-references.json.gz  gzip level 9, mtime 0, of the completed inventory;
  evidence/artifacts.tar.gz              the content-addressed artifacts as a deterministic tar
                                         (sorted names, mtime 0, uid/gid 0, no owner names),
                                         gzip level 9, mtime 0;
  evidence/archive.json                  what each archive holds, by hash, beside the
                                         superseded archive it replaces;
  live-inputs/completed-references-r3.json  byte-identical copy (gitignored), because the LIVE
                                         root pins its inputs repo-relative.
Each archive is checked to round-trip to the external bytes before anything is recorded.
Stdout carries counts and hashes only.
"""
import collections
import gzip
import hashlib
import io
import json
import os
from pathlib import Path
import tarfile

HERE = Path(__file__).resolve().parent
FIT = HERE.parents[1]
REPO = FIT.parents[3]
OUT = Path('/Users/new/vitrea-w50/g1-completion-r3')
EVIDENCE = HERE/'evidence'
LIVE = FIT/'live-inputs/completed-references-r3.json'


def sha(raw): return hashlib.sha256(raw).hexdigest()
def rel(path): return str(Path(path).resolve().relative_to(REPO))


def write_once(path, raw):
    with Path(path).open('xb') as handle:
        handle.write(raw); handle.flush(); os.fsync(handle.fileno())
    return {'path': rel(path), 'sha256': sha(raw)}


def artifacts_tar(root):
    buffer = io.BytesIO()
    with tarfile.open(fileobj=buffer, mode='w', format=tarfile.PAX_FORMAT) as tar:
        def add(name, raw=None):
            info = tarfile.TarInfo(name)
            info.mtime, info.uid, info.gid, info.uname, info.gname = 0, 0, 0, '', ''
            if raw is None:
                info.type, info.mode = tarfile.DIRTYPE, 0o755
                tar.addfile(info)
            else:
                info.size, info.mode = len(raw), 0o644
                tar.addfile(info, io.BytesIO(raw))
        add('artifacts')
        for path in sorted(root.iterdir()):
            add('artifacts/'+path.name, path.read_bytes())
    return buffer.getvalue()


def members(raw):
    with tarfile.open(fileobj=io.BytesIO(gzip.decompress(raw))) as tar:
        return {m.name.split('/', 1)[1]: tar.extractfile(m).read() for m in tar.getmembers() if m.isfile()}


def main():
    completed = (OUT/'completed-references.json').read_bytes()
    bundle = OUT/'bundle.json'
    archive = gzip.compress(completed, compresslevel=9, mtime=0)
    if gzip.decompress(archive) != completed:
        raise ValueError('Inventory archive does not round-trip')
    names = sorted(p.name for p in (OUT/'artifacts').iterdir())
    if any(name != sha((OUT/'artifacts'/name).read_bytes())+'.json' for name in names):
        raise ValueError('Artifact is not named by its content hash')
    tar = gzip.compress(artifacts_tar(OUT/'artifacts'), compresslevel=9, mtime=0)
    if members(tar) != {name: (OUT/'artifacts'/name).read_bytes() for name in names}:
        raise ValueError('Artifact archive does not round-trip')
    cells = json.loads(completed)['cells']
    statuses = collections.Counter(f"{c['role']} {c['status']}" for c in cells)
    EVIDENCE.mkdir()
    inventory = write_once(EVIDENCE/'completed-references.json.gz', archive)
    artifacts = write_once(EVIDENCE/'artifacts.tar.gz', tar)
    live = write_once(LIVE, completed)
    superseded = json.loads((FIT/'completion/registered-2/evidence/archive.json').read_bytes())
    record = {
        'schema': 'w50-reference-assembly-archive-1', 'status': 'EXACT_BYTES_ARCHIVED',
        'binding': {'path': rel(HERE/'binding.json'), 'sha256': sha((HERE/'binding.json').read_bytes())},
        'supersedes': {'archive': {'path': 'packages/calibration/results/2026-10-08-w50-g1-fit/completion/'
                                           'registered-2/evidence/archive.json',
                                   'sha256': sha((FIT/'completion/registered-2/evidence/archive.json').read_bytes())},
                       'binding': superseded['binding'],
                       'completedReferences': superseded['completedReferences']['original']['sha256'],
                       'record': 'completion/registered-3/supersedes.json; owner/r3/supersedes.json'},
        'completedReferences': {
            'original': {'path': str(OUT/'completed-references.json'), 'sha256': sha(completed),
                         'bytes': len(completed)},
            'archive': {**inventory, 'encoding': 'gzip level9 mtime0 (python gzip.compress)'},
            'liveCopy': {**live, 'note': 'identical bytes, gitignored; the LIVE root pins it repo-relative'}},
        'bundle': {'path': str(bundle), 'sha256': sha(bundle.read_bytes()),
                   'note': 'not archived: validate_registered re-derives it deterministically from the binding'},
        'artifacts': {'root': str(OUT/'artifacts'), 'files': len(names), 'contentAddressedNamesVerified': True,
                      'archive': {**artifacts, 'encoding': 'tar (PAX, sorted, mtime 0, uid/gid 0, no owner '
                                  'names, dir 0755, files 0644) gzip level9 mtime0 (python gzip.compress)'}},
        'summary': {'rows': len(cells), 'statuses': dict(sorted(statuses.items()))},
        'boundary': 'Reference evidence only; blind rows identity-only; no candidate, fit, gate or exposure value.'}
    pin = write_once(EVIDENCE/'archive.json', (json.dumps(record, indent=2, allow_nan=False)+'\n').encode())
    print(json.dumps({'archive': pin, 'completedReferences': record['completedReferences']['original'],
                      'artifacts': len(names), 'liveCopy': live}, indent=1))


if __name__ == '__main__':
    main()
