"""DL5r's fixed byte witness and irreversible analysis ordering; no numerical publication.

The old run stopped after 634 of 2,553 keyed writes. Its directory must equal the manifest;
the successor must equal the complete declared key population plus phase.json. Only the 634
already-written keys are equality witnesses. New keys are NOT exemptions from that witness.
"""
import hashlib
import json
import os
from pathlib import Path
import traceback

KEY = ('profile', 'renderer', 'scene', 'statistic')
AUTHORITY = ('executionRoot', 'executionClaim', 'contract', 'batch')


def encode(value):
    return (json.dumps(value, sort_keys=True, indent=2, allow_nan=False)+'\n').encode()


def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def pin(path): return {'path': str(Path(path).resolve()), 'sha256': sha(path)}


def parse(raw):
    def invalid(_): raise ValueError('Nonfinite JSON')
    def unique(items):
        out = {}
        for name, value in items:
            if name in out: raise ValueError('Duplicate JSON field')
            out[name] = value
        return out
    return json.loads(raw, parse_constant=invalid, object_pairs_hook=unique)


def filename(key): return hashlib.sha256(encode(list(key))).hexdigest()+'.json'


def write_once(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    # Persist the directory link too: losing a newly-created marker directory on a crash
    # must not turn an already-spent analysis into an available one.
    parent_fd = os.open(path.parent.parent, os.O_RDONLY)
    try: os.fsync(parent_fd)
    finally: os.close(parent_fd)
    with path.open('xb') as stream:
        stream.write(encode(value)); stream.flush(); os.fsync(stream.fileno())
    fd = os.open(path.parent, os.O_RDONLY)
    try: os.fsync(fd)
    finally: os.close(fd)
    return pin(path)


def old_bytes(manifest, directory):
    """Verify ALL old raw bytes and exact membership BEFORE machine-parsing even one row."""
    directory = Path(directory).resolve()
    items = manifest['files']
    paths = [Path(item['path']) for item in items]
    if (manifest['count'] != len(items) or len(set(paths)) != len(paths)
            or any(p.parent != directory or p.is_symlink() for p in paths)
            or set(directory.iterdir()) != set(paths)):
        raise ValueError('Original raw population differs')
    for item, path in zip(items, paths):
        raw = path.read_bytes()
        if len(raw) != item['bytes'] or hashlib.sha256(raw).hexdigest() != item['sha256']:
            raise ValueError('Original raw bytes differ')
    return paths


def _bound(value, name, keys, authority):
    if (value.get('schema') != 'w50-keyed-measurement-evidence-1'
            or value.get('phase') != 'gate'
            or any(value.get(k) != authority[k] for k in AUTHORITY)):
        raise ValueError('Keyed evidence changed its authority')
    key = tuple(value['row'][k] for k in KEY)
    if key not in keys or filename(key) != name:
        raise ValueError('Keyed evidence changed its identity')
    return {k: v for k, v in value.items() if k not in AUTHORITY}


def compare(manifest, old, new, expected, old_authority, new_authority):
    old, new = Path(old).resolve(), Path(new).resolve()
    if old == new or new.is_relative_to(old) or old.is_relative_to(new):
        raise ValueError('Successor output must be separate')
    paths = old_bytes(manifest, old)
    keys = {tuple(key) for key in expected}
    names = {filename(key) for key in keys}
    if len(keys) != len(expected) or len(names) != len(keys):
        raise ValueError('Duplicate declared key')
    if (any(p.is_symlink() or not p.is_file() for p in new.iterdir())
            or {p.name for p in new.iterdir()} != names | {'phase.json'}
            or not {p.name for p in paths} <= names):
        raise ValueError('Successor keyed population differs')
    # Check every new binding, including the keys the stopped run never reached.
    for name in sorted(names):
        _bound(parse((new/name).read_bytes()), name, keys, new_authority)
    digests = []
    for item, path in zip(manifest['files'], paths):
        # Recheck immediately before parsing, so a file changed after the first pass refuses.
        raw = path.read_bytes()
        if len(raw) != item['bytes'] or hashlib.sha256(raw).hexdigest() != item['sha256']:
            raise ValueError('Original raw bytes differ')
        before = encode(_bound(parse(raw), path.name, keys, old_authority))
        after = encode(_bound(parse((new/path.name).read_bytes()), path.name, keys, new_authority))
        if before != after: raise ValueError('Non-authority witness mismatch')
        digests.append({'file': path.name, 'sha256': hashlib.sha256(before).hexdigest()})
    return {'status': 'MATCH', 'count': len(paths), 'exemptions': [],
            'sha256': hashlib.sha256(encode(digests)).hexdigest()}


def once(marker, claim, measure, witness, judge):
    """Only the marker creation can refuse a replay; no callback runs on restart.

    Callers quarantine this whole operation, including callbacks and their exceptions. A hard
    crash may leave only the marker: that is terminal UNMEASURED, never permission to retry.
    """
    write_once(marker, claim)
    try:
        measured = measure()
        proof = witness()
        report = judge(measured)
        return {'status': report['status'], 'report': report, 'witness': proof}
    except BaseException:
        traceback.print_exc()  # The caller encloses the entire operation in run_private.
        return {'status': 'NEITHER', 'measurementStatus': 'UNMEASURED'}
