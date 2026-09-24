"""W35 read-only access extensions (§5.177, clause 4).

W34's spent receipt path is not changed. Native W34 payloads use Wave.reader.
Canonical fixtures have their own declaration and therefore their own role guard;
they are never inserted into a fabricated W34 inventory. Canonical probe rows
are admitted as diagnostics under W25 DL3(e), by the parent's W35 ruling;
holdout and recorded stay refused. W34 uses only calibration/validation. Public APIs take cell
identities, not paths. Every payload open follows membership and role admission.
"""
import hashlib
import json
from pathlib import Path
import importlib.util

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
spec = importlib.util.spec_from_file_location('w34_roles', HERE / 'wave.py')
W = importlib.util.module_from_spec(spec)
spec.loader.exec_module(W)


def cell_parts(cell):
    if not isinstance(cell, str) or cell.count('/') != 1:
        raise ValueError('a declared profile/scene cell is required, not a path')
    profile, scene = cell.split('/')
    if not profile.startswith('apple-macos-') or not scene or any(x in cell for x in ['..', '\\']):
        raise ValueError('invalid cell identity')
    return profile, scene


class CanonicalRoles:
    def __init__(self):
        self.path = ROOT / 'apps/reference-apple/scenes.json'
        self.spec = json.loads(self.path.read_text())
        self.roles = {s: role for role in ['calibration', 'validation', 'holdout', 'recorded', 'probe']
                      for s in self.spec['split'].get(role, [])}
        self.scenes = {s['id']: s for s in self.spec['scenes']}
        self.cells = {p['key']+'/'+sid for p in self.spec['profiles']
                      for sid in (self.scenes if p['scenes'] == 'all' else p['scenes'])}

    def admit(self, cell):
        profile, sid = cell_parts(cell)
        if cell not in self.cells: raise ValueError('undeclared canonical cell')
        if self.roles[sid] not in ['calibration', 'validation', 'probe']:
            raise PermissionError('canonical '+self.roles[sid]+' is not authorised')
        return profile, sid


def confined(root, path):
    path = path.resolve()
    if root not in path.parents: raise ValueError('payload escaped declared root')
    return path


class WebReader:
    def __init__(self, root, roles, provenance=None):
        self.root = Path(root).resolve()
        self.roles = roles
        self.provenance = provenance

    @classmethod
    def w34(cls, root=None):
        evidence = HERE.parent / '2026-09-24-w34-g2-contour-identification'
        provenance = {r['cell']: r['pngSha256'] for r in
                      json.loads((evidence/'web-provenance.json').read_text())} if root is None else None
        return cls(root or evidence/'web-captures', W.default_wave(), provenance)

    @classmethod
    def canonical(cls, root): return cls(root, CanonicalRoles())

    def admit(self, cell):
        profile, sid = cell_parts(cell)
        if isinstance(self.roles, CanonicalRoles): return self.roles.admit(cell)
        if cell not in self.roles.cells: raise ValueError('undeclared W34 cell')
        if self.roles.roles[sid] not in ['calibration', 'validation']:
            raise PermissionError('W34 '+self.roles.roles[sid]+' is not authorised')
        if sid not in self.roles.launch_scenes(): raise ValueError('native-only cell has no web payload')
        return profile, sid

    def read(self, cell, kind='png'):
        profile, sid = self.admit(cell)
        names = {'png': sid+'__webgpu.png', 'metadata': 'cell__webgpu.json',
                 'report': 'report__webgpu.json'}
        if kind not in names: raise ValueError('unsupported payload kind')
        raw = confined(self.root, self.root/profile/sid/names[kind]).read_bytes()
        if kind == 'png' and self.provenance is not None:
            if hashlib.sha256(raw).hexdigest() != self.provenance[cell]:
                raise ValueError('W34 web capture hash mismatch')
        return raw


class CanonicalNativeReader:
    def __init__(self):
        self.roles = CanonicalRoles()
        self.root = (ROOT/'apps/reference-apple/fixtures').resolve()

    def read(self, cell, kind='png'):
        profile, sid = self.roles.admit(cell)
        if kind == 'png': path = self.root/profile/(sid+'.png')
        elif kind == 'background':
            scene = self.roles.scenes[sid]
            # Fixture captures and references share the declared backing scale.
            scale = '2x' if '-2x-' in profile else '1x'
            path = self.root/'backgrounds'/(scene['background']+'@'+scale+'.png')
        elif kind == 'metadata': path = self.root/profile/(sid+'.json')
        else: raise ValueError('unsupported native payload kind')
        return confined(self.root, path).read_bytes()
