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
import platform
import shutil
import subprocess
import sys


class OriginText(str):
    def __new__(cls, value, origin):
        result = super().__new__(cls, value); result.origin = origin; return result


class OriginBytes(bytes):
    def __new__(cls, value, origin):
        result = super().__new__(cls, value); result.origin = origin; return result


class ReadOnly:
    def __init__(self, forbidden=()):
        self.forbidden = set(forbidden); self.active = False; self.originals = {}
        self.metadata_pins = {}; self.payload_paths = set()

    def __enter__(self):
        null = os.lstat('/dev/null')
        if not stat.S_ISCHR(null.st_mode) or os.devnull != '/dev/null':
            raise ValueError('Expected existing /dev/null character device')
        self.devnull = (null.st_dev, null.st_ino, null.st_rdev, stat.S_IFMT(null.st_mode))
        self.active = True; sys.addaudithook(self.audit)
        self.loads = json.loads
        def loads(raw, *args, **kwargs):
            value = raw.encode() if isinstance(raw, str) else bytes(raw)
            digest = hashlib.sha256(value).hexdigest()
            if digest in self.forbidden:
                origin = raw.origin if isinstance(raw, (OriginText, OriginBytes)) else None
                if (origin in self.payload_paths or origin is None or
                        self.metadata_pins.get(origin) != digest):
                    raise ValueError('Read-only preflight forbids numerical gate payload JSON parsing')
            return self.loads(raw, *args, **kwargs)
        json.loads = loads
        self.read_text, self.read_bytes = Path.read_text, Path.read_bytes
        read_text, read_bytes = self.read_text, self.read_bytes
        def text(path, *args, **kwargs):
            return OriginText(read_text(path, *args, **kwargs), str(path.resolve()))
        def binary(path, *args, **kwargs):
            return OriginBytes(read_bytes(path, *args, **kwargs), str(path.resolve()))
        Path.read_text, Path.read_bytes = text, binary
        def refuse(*args, **kwargs): raise ValueError('Read-only preflight forbids descriptor mutation')
        for name in ('write', 'writev', 'pwrite', 'ftruncate', 'fchmod', 'fchown'):
            if hasattr(os, name):
                self.originals[name] = getattr(os, name); setattr(os, name, refuse)
        return self

    def __exit__(self, *_):
        self.active = False; json.loads = self.loads
        Path.read_text, Path.read_bytes = self.read_text, self.read_bytes
        for name, value in self.originals.items(): setattr(os, name, value)

    def stdlib_caller(self, module, function):
        frame = sys._getframe(1)
        while frame:
            if (frame.f_code.co_filename == module.__file__ and
                    frame.f_code.co_name == function): return True
            frame = frame.f_back
        return False

    def devnull_open(self, path, flags):
        if path != '/dev/null' or flags & ~(os.O_RDWR | os.O_CLOEXEC) or flags & os.O_ACCMODE != os.O_RDWR:
            return False
        if not self.stdlib_caller(subprocess, '_get_devnull'): return False
        value = os.lstat('/dev/null')
        identity = (value.st_dev, value.st_ino, value.st_rdev, stat.S_IFMT(value.st_mode))
        if identity != self.devnull or not stat.S_ISCHR(value.st_mode):
            raise ValueError('Existing /dev/null identity/type changed')
        return True

    def audit(self, event, args):
        if not self.active: return
        if event == 'open':
            path, mode, flags = args
            if ((isinstance(mode, str) and any(c in mode for c in 'wax+')) or
                    flags & (os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_TRUNC | os.O_APPEND)):
                if not self.devnull_open(path, flags):
                    raise ValueError('Read-only preflight forbids writable opens')
        elif event.startswith('socket.') or event in ('os.remove', 'os.rmdir', 'os.mkdir',
                'os.rename', 'os.link', 'os.symlink', 'os.chmod', 'os.chown', 'os.truncate',
                'os.utime', 'os.system', 'os.posix_spawn', 'os.fork', 'mmap.__new__'):
            raise ValueError('Read-only preflight forbids state mutation')
        elif event == 'subprocess.Popen':
            argv = args[1]
            if (argv == ['uname', '-p'] and self.stdlib_caller(platform, 'from_subprocess')
                    and shutil.which('uname') == '/usr/bin/uname' and args[3] is None):
                return
            if (isinstance(argv, (list, tuple)) and len(argv) == 3 and list(argv[:2]) == ['file', '-b']
                    and Path(argv[2]).resolve() == Path(sys.executable).resolve()
                    and self.stdlib_caller(platform, '_syscmd_file')
                    and shutil.which('file') == '/usr/bin/file'
                    and args[3] == dict(os.environ, LC_ALL='C')):
                return
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
              runner.COMPLETE, runner.PENDING, runner.FAILED, runner.INVOCATION, *runner.PREVIOUS]
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
        boundary_guard.payload_paths.update(str(Path(item['path']).resolve())
            for row in declared_union['members'] for item in [row['payload'], *row['artifacts']])
        boundary_guard.payload_paths.update(str(Path(item['path']).resolve()) for item in manifest['files'])
        root, view, contract, batch, manifest, authority, guard = A.verify_seal()
        # A retained capture can copy a static config verbatim. Its hash is then not a
        # sufficient provenance discriminator: only the independently root-pinned original
        # pathname may parse those bytes; every capture pathname remains denied.
        boundary_guard.metadata_pins.update({str((A.REPO/item['path']).resolve()): item['sha256']
            for item in root['inputs'] if (A.REPO/item['path']).resolve().is_relative_to(A.REPO)})
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
            'reviewStatus': 'PENDING_FINAL_REVIEW', 'preparation': A.PREPARATION,
            'originalClaim': W.pin(original_claim_path), 'auditCommit': A.AUDIT_COMMIT,
            'rulingCommit': A.RULING, 'spentMarker': W.pin(A.MARKER),
            'captureUnion': W.pin(A.UNION), 'unreadManifest': W.pin(A.MANIFEST),
            'sources': authority['closure']['sources'], 'environment': authority['closure']['environment'],
            'paths': paths, 'namespace': {'output': str(A.OUTPUT), 'marker': str(A.NEW_MARKER),
                'logicalClaim': str(runner.LOGICAL), 'preflightRecord': str(A.PREFLIGHT),
                'invocationFence': str(runner.INVOCATION)},
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
