#!/Users/new/vitrea-w49/py/bin/python -I -B
"""Archive one owner projection read as its committed evidence: projection.json.gz, one gzip per
row under rows/, and projection-index.json naming each row by key and content pin.

The superseded evidence (owner/evidence, 0a6fe6cb3) was written by a script that was not
committed; this one reproduces it. `verify-superseded` rebuilds that evidence from its
retained external read and compares every byte, so the r2 evidence is the same encoding:
a row file is named by the first 20 hex of sha256('|'.join(key)) and holds the member as
compact JSON (UTF-8, insertion order) and a newline, gzip level 9, mtime 0; the whole read is
gzip'd the same way; the index is indented JSON whose source pins the external read.

  index.py write PROJECTION EVIDENCE_DIR     (write-once files inside EVIDENCE_DIR)
  index.py verify-superseded

Stdout carries counts and hashes only.
"""
import gzip
import hashlib
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[5]
KEY = ('profile', 'renderer', 'scene', 'statistic')
SUPERSEDED_READ = Path('/Users/new/vitrea-w50/g1-owner-read/projection.json')


def sha(raw): return hashlib.sha256(raw).hexdigest()
def compress(raw): return gzip.compress(raw, compresslevel=9, mtime=0)


def build(projection, evidence):
    """{relative path: bytes} for the archive of one read; nothing is written."""
    raw = Path(projection).read_bytes()
    batch = json.loads(raw)
    if batch.get('schema') != 'w50-owner-evidence-batch-1' or len(batch.get('rows', [])) != 640:
        raise ValueError('Expected one complete 640-row owner projection batch')
    evidence = Path(evidence).resolve().relative_to(REPO)
    files, rows, names = {}, [], set()
    for member in batch['rows']:
        key = [member['row'][k] for k in KEY]
        name = hashlib.sha256('|'.join(key).encode()).hexdigest()[:20]
        if name in names:
            raise ValueError('Row file name collision')
        names.add(name)
        body = compress((json.dumps(member, separators=(',', ':'), ensure_ascii=False)+'\n').encode())
        path = str(evidence/'rows'/(name+'.json.gz'))
        files[path] = body
        rows.append({'key': key, 'evidence': {'path': path, 'sha256': sha(body)}})
    index = {'schema': 'w50-owner-projection-index-1',
             'source': {'path': str(Path(projection).resolve()), 'sha256': sha(raw)}, 'rows': rows}
    files[str(evidence/'projection-index.json')] = (json.dumps(index, indent=2)+'\n').encode()
    files[str(evidence/'projection.json.gz')] = compress(raw)
    return files


def write(projection, evidence):
    evidence = Path(evidence)
    (evidence/'rows').mkdir(parents=True, exist_ok=False)
    files = build(projection, evidence)
    for path, raw in files.items():
        with (REPO/path).open('xb') as handle:
            handle.write(raw)
    index = str(evidence.resolve().relative_to(REPO)/'projection-index.json')
    print(json.dumps({'rows': len(files)-2, 'index': {'path': index, 'sha256': sha(files[index])}}))


def verify_superseded():
    files = build(SUPERSEDED_READ, HERE.parent/'evidence')
    differing = [path for path, raw in files.items() if (REPO/path).read_bytes() != raw]
    committed = {str(p.relative_to(REPO)) for p in (HERE.parent/'evidence/rows').iterdir()}
    extra = committed - set(files)
    if differing or extra:
        raise ValueError(f'Superseded evidence not reproduced: {len(differing)} differ, {len(extra)} extra')
    print(json.dumps({'status': 'REPRODUCED', 'files': len(files)}))


if __name__ == '__main__':
    verb, *args = sys.argv[1:]
    if verb == 'write' and len(args) == 2:
        write(Path(args[0]), Path(args[1]))
    elif verb == 'verify-superseded' and not args:
        verify_superseded()
    else:
        raise SystemExit(__doc__)
