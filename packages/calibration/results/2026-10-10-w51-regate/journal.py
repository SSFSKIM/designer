"""Durable invocation fences and fail-closed terminal eligibility."""
import hashlib
import json
import os
from pathlib import Path
import uuid


def encode(value): return (json.dumps(value, sort_keys=True, indent=2, allow_nan=False)+'\n').encode()
def load(path): return json.loads(Path(path).read_bytes())
def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def pin(path): return {'path':str(Path(path).resolve()), 'sha256':sha(path)}


def sync_directory(path):
    descriptor = os.open(str(path), os.O_RDONLY)
    try: os.fsync(descriptor)
    finally: os.close(descriptor)


def write_bytes(path, raw):
    """Install fully flushed bytes without replacement; failed temporary writes remain evidence."""
    path = Path(path).absolute()
    if path.resolve()!=path or any(p.is_symlink() for p in (path,*path.parents)):
        raise ValueError('Evidence write traverses a symlink')
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary=path.with_name('.'+path.name+'.pending-'+uuid.uuid4().hex)
    with temporary.open('xb') as stream:
        stream.write(raw); stream.flush(); os.fsync(stream.fileno())
    # link is an atomic no-replace install on the same filesystem. Unlike rename, it cannot
    # replace an already claimed marker; unlike writing the final name, it cannot expose a tear.
    os.link(temporary,path)
    sync_directory(path.parent)
    temporary.unlink()
    sync_directory(path.parent)
    return pin(path)


def write_once(path, value):
    return write_bytes(path,encode(value))


def checked(item):
    path = Path(item['path'])
    if path.resolve() != path or not path.is_file() or sha(path) != item['sha256']:
        raise ValueError('Changed terminal artifact')
    return path


def fence(output, identity):
    """The first durable invocation act. Callers hold a process lock during numbering."""
    output = Path(output); folder = output/'fences'
    if folder.resolve()!=folder.absolute() or any(p.is_symlink() for p in (folder,*folder.parents)):
        raise ValueError('Fence namespace traverses a symlink')
    folder.mkdir(parents=True, exist_ok=True)
    prior = sorted(p for p in folder.glob('*.json') if len(p.stem)==6 and p.stem.isdigit())
    if any(load(p)['identity'] != identity for p in prior):
        raise ValueError('Output belongs to another execution identity')
    return write_once(folder/f'{len(prior)+1:06d}.json',
                      {'schema':'w51-invocation-fence-1','identity':identity,'pid':os.getpid()})


def fail(output, code, identity):
    """Record a precommit fault, never revoke a verdict from a later invocation.

    An unreadable terminal is not an absent one. Propagate that error without installing a
    fault; the caller can report unavailable status but cannot invent a scientific NEITHER.
    """
    output = Path(output)
    try: (output/'terminal.json').stat()
    except FileNotFoundError: pass
    else: return terminal(output)
    value = {'schema':'w51-terminal-fault-1', 'status':'NEITHER',
             'measurementStatus':'UNMEASURED', 'judgeCompleted':False,
             'fault':code, 'identity':identity}
    target = output/'fault.json'
    if target.exists(): return load(target)
    write_once(target, value)
    return value


def prepare(output, report, witness, identity):
    """Flush and validate evidence without making a completed pipeline eligible.

    The retained preparation is deliberately not a terminal record. A crash or failure here,
    including failure to persist fault.json, leaves no positive eligibility to revive.
    """
    output = Path(output)
    if (output/'fault.json').exists() or (output/'terminal.json').exists():
        raise FileExistsError('Terminal execution cannot publish again')
    if report['status'] not in ('PASS_EXPOSED_OWNER_PENDING','NEITHER') or witness['status'] != 'COMPLETE':
        raise ValueError('Only a complete exposed judge report can be published')
    report_pin = write_once(output/'report.json', report)
    witness_pin = write_once(output/'witness.json', witness)
    result = {'schema':'w51-terminal-result-1','status':report['status'], 'judgeCompleted':True,
              'identity':identity,'report':report_pin,'witness':witness_pin}
    result_pin = write_once(output/'result.json', result)
    for item in (report_pin,witness_pin,result_pin): checked(item)
    prepared = write_once(output/'terminal-prepared.json',
                          {'schema':'w51-terminal-commit-1','result':result_pin})
    source = checked(prepared)
    return {'result':result, 'source':source, 'target':output/'terminal.json'}


def commit(prepared):
    """The no-replace link is COMMIT; a later directory flush error cannot revoke it.

    Call only after all validation, serialization and owned cleanup have finished. The source
    bytes and its directory entry are already flushed. Keep that source as evidence: removing
    it here would introduce another fallible cleanup after eligibility. A crash before the link
    leaves preparation only; a crash after it but before directory fsync may lose the terminal
    entry, conservatively withholding eligibility. We cannot promise crash-atomic durability.
    Once link returns success, fsync failure is committed-with-durability-error, not permission
    to retry or to replace the scientific verdict with an instrument fault.
    """
    os.link(prepared['source'], prepared['target'])
    try:
        sync_directory(prepared['target'].parent)
    except BaseException:
        return 'COMMITTED_WITH_DURABILITY_ERROR'
    return 'COMMITTED'


def terminal(output):
    output = Path(output)
    if (output/'fault.json').exists():
        result = load(output/'fault.json')
        if result.get('schema') != 'w51-terminal-fault-1' or result.get('status') != 'NEITHER':
            raise ValueError('Invalid terminal fault')
        return result
    target = output/'terminal.json'
    if not target.exists(): return None
    result = load(checked(load(target)['result']))
    report, witness = (load(checked(result[k])) for k in ('report','witness'))
    if result['status'] != report['status'] or witness['status'] != 'COMPLETE' or not result['judgeCompleted']:
        raise ValueError('Terminal result/report/witness disagree')
    return result
