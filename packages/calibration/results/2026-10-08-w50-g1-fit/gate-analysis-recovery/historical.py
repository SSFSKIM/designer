"""DL5s historical proof reader. Returns live paths only AFTER both provenance checks.

The historical proof's pin is never rewritten to a live pin. Missing blobs fail unless the
exact committed exception witness supplies an archive or an explicitly late-preserved log.
Only proof authentication uses this adapter; capture provenance and projection are untouched.
"""
import gzip
import hashlib
from pathlib import Path
import re
import subprocess
import types


def digest(raw): return hashlib.sha256(raw).hexdigest()


class Historical:
    def __init__(self, repo, commit, delta_commit, delta_paths, exceptions=None,
                 preservation_commit=None):
        self.repo = Path(repo).resolve()
        self.commit, self.delta_commit = commit, delta_commit
        self.delta_paths = frozenset(delta_paths)
        self.exceptions = exceptions or {}
        self.preservation_commit = preservation_commit
        self.cache = {}
        for value in (commit, delta_commit, *([preservation_commit] if preservation_commit else [])):
            if not re.fullmatch('[a-f0-9]{40}', value) or self.git('cat-file', '-t', value) != b'commit\n':
                raise ValueError('Historical authority needs an exact existing commit')

    def git(self, *args):
        result = subprocess.run(['git', '-C', str(self.repo), *args], capture_output=True)
        if result.returncode: raise ValueError('Missing historical git object')
        return result.stdout

    def path(self, name):
        if not isinstance(name, str) or Path(name).is_absolute() or str(Path(name)) != name or '..' in Path(name).parts:
            raise ValueError('Historical pin needs a canonical repository-relative path')
        path = self.repo/name
        if any(p.is_symlink() for p in (path, *path.parents)):
            raise ValueError('Historical pin has a symlink component')
        return path

    def blob(self, name, commit=None):
        self.path(name)
        return self.git('cat-file', 'blob', f'{commit or self.commit}:{name}')

    def historical_bytes(self, item):
        name = item['path']; self.path(name)
        try: raw = self.blob(name)
        except ValueError:
            exception = self.exceptions.get(name)
            if not exception or exception['sha256'] != item['sha256']:
                raise ValueError('Missing blob has no exact historical exception') from None
            if exception['authentication'] == 'COMMITTED_GZIP_BLOB_DECOMPRESSION':
                if exception['archiveCommit'] != self.commit:
                    raise ValueError('Archive is not from the proof commit')
                archive = exception['archive']; compressed = self.blob(archive['path'])
                if digest(compressed) != archive['sha256']:
                    raise ValueError('Historical archive pin differs')
                raw = gzip.decompress(compressed)
            elif exception['authentication'] == 'HISTORICAL_PROOF_SHA256_LATE_PRESERVATION':
                if not self.preservation_commit: raise ValueError('No late preservation commit')
                raw = self.blob(name, self.preservation_commit)
            else: raise ValueError('Unknown historical exception')
            if len(raw) != exception['bytes']:
                raise ValueError('Historical exception size differs')
        else:
            if name in self.exceptions:
                raise ValueError('Exception falsely claims no historical blob')
        if digest(raw) != item['sha256'] or ('bytes' in item and len(raw) != item['bytes']):
            raise ValueError('Historical proof pin differs from its attested bytes')
        return raw

    def checked(self, repo, item):
        if Path(repo).resolve() != self.repo: raise ValueError('Historical proof belongs to another repository')
        name = item['path']; path = self.path(name)
        key = (name, item['sha256'], item.get('bytes'))
        if key not in self.cache:
            raw = self.historical_bytes(item)
            expected = self.blob(name, self.delta_commit) if name in self.delta_paths else raw
            self.cache[key] = digest(expected)
        if not path.is_file() or digest(path.read_bytes()) != self.cache[key]:
            raise ValueError('Live proof input differs outside the exact committed two-file delta')
        return path


class Facade:
    def __init__(self, original, **overrides):
        self.original = original; self.__dict__.update(overrides)
    def __getattr__(self, name): return getattr(self.original, name)


def verify_prefit(authority, root_path, root, reader):
    """Run unchanged semantic, lineage and proof validators over authenticated historical pins.

    Only the proof pin reader changes. The rest of prefit.py, including completion, exemptions
    and the proof schemas/checks, runs unchanged. No source module or old seal is edited.
    """
    D = authority.D
    evidence_path = authority.C.slot(root_path, 'prefit')
    # Evidence and sidecar themselves must exist byte-for-byte at the historical commit.
    for path in (evidence_path, Path(str(evidence_path)+'.sha256')):
        reader.checked(reader.repo, D.pin(reader.repo, path))
    evidence = D.sealed(evidence_path)
    proofs = []
    pins = list(evidence['sources']) + [evidence['references']]
    for item in evidence['evidence'].values():
        path = reader.checked(reader.repo, item)
        proof = D.load(path); proofs.append(proof)
        pins.extend(proof['sources']); pins.extend(proof['outputs'])
    for item in pins: reader.checked(reader.repo, item)
    # The registered production closure is historical too, not just the lists of test pins.
    for path, sha in evidence['executionClosure']['sources'].items():
        reader.checked(reader.repo, {'path': path, 'sha256': sha})
    named = {(p['path'], p['sha256']) for p in pins}
    original_module = D.module

    def module(path, name):
        result = original_module(path, name)
        if Path(path) == Path(root_path).parent/'prefit.py':
            original_pin = result.pin_path
            def proof_pin(item, repo, external=False):
                if not external and (item.get('path'), item.get('sha256')) in named:
                    return reader.checked(repo, item)
                return original_pin(item, repo, external=external)
            result.pin_path = proof_pin
        return result

    adapted = types.ModuleType('w50_dl5s_historical_authority')
    adapted.__dict__.update(authority.__dict__)
    adapted.D = Facade(D, checked=reader.checked, module=module)
    # Function globals, not a process-wide monkeypatch; the original LIVE validator remains live.
    for name, value in list(adapted.__dict__.items()):
        if isinstance(value, types.FunctionType) and value.__globals__ is authority.__dict__:
            adapted.__dict__[name] = types.FunctionType(value.__code__, adapted.__dict__, name,
                                                       value.__defaults__, value.__closure__)
    return adapted.verify_prefit(root_path, root)
