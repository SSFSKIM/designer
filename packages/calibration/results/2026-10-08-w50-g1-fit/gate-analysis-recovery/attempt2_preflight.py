"""One complete admission plan, used by both the read-only diagnostic and the real invocation.

No claim/lease is fabricated for preflight. The setup-only calls below do not require one;
measurement, capture receipt parsing, the witness and judging are deliberately unreachable.
The guard is process-local role discipline, not a sandbox against a hostile interpreter.
"""
import hashlib
import json
import os
from pathlib import Path
import stat
import sys


class ReadOnly:
    def __init__(self, forbidden=()):
        self.forbidden = set(forbidden); self.active = False; self.originals = {}

    def __enter__(self):
        self.active = True; sys.addaudithook(self.audit)
        self.loads = json.loads
        def loads(raw, *args, **kwargs):
            value = raw.encode() if isinstance(raw, str) else bytes(raw)
            if hashlib.sha256(value).hexdigest() in self.forbidden:
                raise ValueError('Read-only preflight forbids numerical gate payload JSON parsing')
            return self.loads(raw, *args, **kwargs)
        json.loads = loads
        def refuse(*args, **kwargs): raise ValueError('Read-only preflight forbids descriptor mutation')
        for name in ('write', 'writev', 'pwrite', 'ftruncate', 'fchmod', 'fchown'):
            if hasattr(os, name):
                self.originals[name] = getattr(os, name); setattr(os, name, refuse)
        return self

    def __exit__(self, *_):
        self.active = False; json.loads = self.loads
        for name, value in self.originals.items(): setattr(os, name, value)

    def audit(self, event, args):
        if not self.active: return
        if event == 'open':
            _, mode, flags = args
            if ((isinstance(mode, str) and any(c in mode for c in 'wax+')) or
                    flags & (os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_TRUNC | os.O_APPEND)):
                raise ValueError('Read-only preflight forbids writable opens')
        elif event.startswith('socket.') or event in ('os.remove', 'os.rmdir', 'os.mkdir',
                'os.rename', 'os.link', 'os.symlink', 'os.chmod', 'os.chown', 'os.truncate',
                'os.utime', 'os.system', 'os.posix_spawn', 'os.fork', 'mmap.__new__'):
            raise ValueError('Read-only preflight forbids state mutation')
        elif event == 'subprocess.Popen':
            argv = args[1]
            if (not isinstance(argv, (tuple, list)) or len(argv) < 4 or argv[0] != 'git' or
                    argv[1] != '-C' or argv[3] not in ('cat-file', 'show', 'rev-parse', 'merge-base')):
                raise ValueError('Preflight permits only read-only git object commands')


def clean(path):
    path = Path(path).absolute()
    if any(p.is_symlink() for p in (path, *path.parents)):
        raise ValueError('Attempt path has a symlink component')
    return path


def prerequisites(runner, core):
    A = runner.A
    for path in (A.AUTHORITY_PATH, A.VIEW_PATH, A.CONTRACT_PATH, A.REVIEW, A.PREFLIGHT):
        clean(path)
        if os.path.lexists(path) and not path.is_file():
            raise ValueError('Attempt authority/preflight path is not a regular file')
    absent = [A.OUTPUT, A.NEW_MARKER.parent, runner.LOGICAL, runner.TERMINAL,
              runner.COMPLETE, runner.PENDING, runner.FAILED]
    for path in absent:
        clean(path)
        if os.path.lexists(path): raise ValueError('Attempt 2 namespace already spent')
    configured_lock = Path(core['C'].D.GPU_LOCK)
    # The sealed dispatcher uses /tmp, macOS's system alias for /private/tmp. Resolve its
    # parent for permission inspection, never a symlink at the lock filename itself.
    if configured_lock.is_symlink(): raise ValueError('GPU lock is a symlink')
    lock = clean(configured_lock.parent.resolve()/configured_lock.name)
    if os.path.lexists(lock): raise ValueError('Preflight requires an absent GPU lease')
    parents = {A.OUTPUT.parent, A.NEW_MARKER.parent.parent, runner.FAILED.parent, lock.parent}
    permissions = []
    for path in sorted(parents):
        clean(path)
        mode = path.stat()
        if (not stat.S_ISDIR(mode.st_mode) or not mode.st_mode & 0o222 or
                not os.access(path, os.W_OK | os.X_OK) or os.statvfs(path).f_bavail <= 0):
            raise ValueError('Attempt output/claim/lease parent is not writable')
        permissions.append({'path': str(path), 'mode': stat.S_IMODE(mode.st_mode),
                            'uid': mode.st_uid, 'gid': mode.st_gid})
    mutex = clean(str(lock)+'.mutex')
    if os.path.lexists(mutex) and (not mutex.is_file() or not os.access(mutex, os.R_OK | os.W_OK)):
        raise ValueError('GPU lease mutex is not readable/writable')
    return {'absent': [str(p) for p in absent], 'leaseAbsent': str(lock),
            'configuredLease': str(configured_lock), 'parents': permissions}


def setup(runner, live, core, data, union, boundary):
    """Actual runner modules, input validators and read adapters, prepared before any marker."""
    A, W = runner.A, runner.W
    context, hashes = live._template(A.ROOT, A.CONTRACT, data)
    context.update(executionRoot=str(A.VIEW_PATH), contract=str(A.CONTRACT_PATH),
                   output=str(A.OUTPUT), stage='analysis')
    facade = runner.ReadOnlyDispatcher(live, boundary, context)
    roles = {name: live._component(data[0], name) for name in ('measurement', 'judge')}
    for name, (module, config) in roles.items():
        core['A'].instrument_interface(name, module)
        live.checked(A.REPO, config)
    measurement, config = roles['measurement']
    measurement.P.inputs(context, facade, config)
    runner.R.install(measurement, boundary, facade, context,
        {'executionRoot': W.pin(A.ROOT), 'contract': W.pin(A.CONTRACT),
         'batchPath': W.pin(data[2])})
    # Exercise the exact read-admission module and all pure judge-input preparation. No evaluate.
    admission = live.admission_module(data[0])
    if not callable(getattr(admission, 'validate_captures', None)):
        raise ValueError('Capture read-admission interface missing')
    judge, config = roles['judge']
    root = judge.root_of(context, facade)
    document, _ = judge.originals(context, facade, root)
    _, _, targets, cut = judge.inputs(context, facade, root, config)
    judge.preflight(document, root, cut, targets)
    from PIL import Image
    Image.preinit()
    return context, hashes, facade, roles


def prepare(runner):
    """No new deterministic admission branch may live only in start(), after a claim or marker."""
    A, W = runner.A, runner.W
    with ReadOnly() as boundary_guard:
        # Metadata only. Install the no-payload-JSON fence before the full validator path.
        if W.sha(A.MANIFEST) != A.OLD.MANIFEST_SHA or W.sha(A.UNION) != A.OLD.UNION_SHA:
            raise ValueError('Original manifest/union metadata changed')
        manifest = W.parse(A.MANIFEST.read_bytes()); declared_union = W.parse(A.UNION.read_bytes())
        boundary_guard.forbidden.update(item['sha256'] for item in manifest['files'])
        boundary_guard.forbidden.update(item['sha256'] for row in declared_union['members']
            for item in [row['payload'], *row['artifacts']] if Path(item['path']).suffix == '.json')
        root, view, contract, batch, manifest, authority, guard = A.verify_seal()
        # Same source enforcement as the actual invocation. No source discovery or subprocess
        # instrument exercise is hidden behind a sealed preflight claim.
        guard.enforce(A.REPO, authority['closure']['sources'])
        live, core = runner.modules()
        paths = prerequisites(runner, core)
        data, union = runner.admit(root, view, contract, batch, live, core)
        boundary = runner.R.Boundary(A.OLD_OUTPUT, A.OUTPUT, union)
        context, hashes, dispatcher, roles = setup(runner, live, core, data, union, boundary)
        original_claim_path = Path(str(A.CONTRACT)+'.started.json')
        original_claim = W.parse(original_claim_path.read_bytes())
        if not isinstance(original_claim.get('numericalAdmission'), dict):
            raise ValueError('Original logical claim lacks numerical admission')
        proof = {'schema': 'w50-dl5s-read-only-preflight-1', 'status': 'CLEAN', 'analysis': 2,
            'attempt': 2, 'authority': W.pin(A.AUTHORITY_PATH), 'rootView': W.pin(A.VIEW_PATH),
            'contract': W.pin(A.CONTRACT_PATH), 'review': W.pin(A.REVIEW),
            'originalClaim': W.pin(original_claim_path), 'auditCommit': A.AUDIT_COMMIT,
            'rulingCommit': A.RULING, 'spentMarker': W.pin(A.MARKER),
            'captureUnion': W.pin(A.UNION), 'unreadManifest': W.pin(A.MANIFEST),
            'sources': authority['closure']['sources'], 'environment': authority['closure']['environment'],
            'paths': paths, 'namespace': {'output': str(A.OUTPUT), 'marker': str(A.NEW_MARKER),
                'logicalClaim': str(runner.LOGICAL), 'preflightRecord': str(A.PREFLIGHT)},
            'captureCount': len(union['members']), 'witnessCount': manifest['count'],
            'expectedKeys': len(data[4]), 'payloadsParsed': 0, 'writes': 0,
            'checks': ['historical-prefit-all-pins', 'exact-live-delta', 'original-fit-and-cohort',
                'complete-capture-union', 'successor-view-and-closure', 'role-interfaces-and-inputs',
                'original-read-adapter-setup', 'attempt-namespace-and-permissions']}
        # This canonical snapshot also binds exact marker/output strings and absence assertions;
        # hashing only data would not authenticate the attempted operation.
        proof['planSha256'] = hashlib.sha256(W.encode(proof)).hexdigest()
        return {'proof': proof, 'live': live, 'core': core, 'data': data, 'union': union,
                'boundary': boundary, 'template': context, 'templateHashes': hashes,
                'setupDispatcher': dispatcher, 'roles': roles, 'manifest': manifest,
                'originalClaim': original_claim, 'guard': guard,
                'sources': authority['closure']['sources']}
