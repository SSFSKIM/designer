"""Test helper (not a role): the REAL LIVE dispatcher/journal under synthetic admitted authority.

Kit: root/pre-fit/numerical/gate admission is an explicit fixture boundary, exactly as in
live-execution/test_execution.py. The context, lease, capability checks, stages and journal
are the real implementation, so a role tested here meets LIVE's actual API, not a permissive
fake. EndToEnd (below) narrows the boundary to root admission and pre-fit verification: the
whole fit/gate/exposure chain runs through the real dispatcher with all seven real roles.
"""
import contextlib
import copy
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import sys
import tempfile
import uuid

HERE = Path(__file__).resolve().parent
LIVE = HERE.parent/'live-execution'
KEY = ('profile', 'renderer', 'scene', 'statistic')


def module(path, name):
    spec = importlib.util.spec_from_file_location(name, path); value = importlib.util.module_from_spec(spec)
    sys.modules[name] = value; spec.loader.exec_module(value); return value


def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()


class Kit:
    """One logical phase over a synthetic repository; roles/configs are supplied by the test."""
    def __init__(self, case, *, phase, runs, cohort, statistics=('x',), inputs=(), root=None, gate=None):
        t = tempfile.TemporaryDirectory(); case.addCleanup(t.cleanup)
        base = Path(t.name).resolve(); self.base = base
        self.repo = base/'repo'; self.repo.mkdir(); self.output = base/'outside'
        tag = uuid.uuid4().hex
        self.D = module(LIVE/'dispatch.py', 'livekit_dispatch_'+tag)
        self.C = module(LIVE/'common.py', 'livekit_common_'+tag)
        self.L = module(LIVE/'lifecycle.py', 'livekit_lifecycle_'+tag)
        self.Q = module(LIVE/'quarantine.py', 'livekit_quarantine_'+tag)
        self.D._CORE = {'C': self.C, 'L': self.L, 'Q': self.Q}
        old = self.C.D.GPU_LOCK; self.C.D.GPU_LOCK = base/'lease'
        case.addCleanup(setattr, self.C.D, 'GPU_LOCK', old)
        case.addCleanup(lambda: sys.modules.pop('w50_g1_dispatch', None))
        self.batch = {'schema': 'w50-g1-batch-1', 'phase': phase, 'cohort': cohort, 'runs': runs}
        self.batch_path = self.put('batch.json', self.batch)
        cells = [{'profile': r['profile'], 'renderer': r['renderer'], 'scene': s, 'statistic': x, 'role': 'calibration'}
                 for r in runs for s in r['scenes'] for x in statistics]
        self.references = self.pin(self.put('references.json', {'cells': cells}))
        self.doc = {'repo': str(self.repo), 'inputs': list(inputs), 'references': self.references,
            'baselineDocuments': [r['baselineCandidate'] for r in runs if 'baselineCandidate' in r],
            'repeatAdmission': {}, 'phaseDependencies': {'ownerUnionKeys': [], 'pendingOwnerKeys': []},
            'reportedKeys': [], 'emptySupportKeys': [], **(root or {})}
        self.root = self.repo/'root.json'; self.reseal()
        self.contract = self.repo/'phase.json'
        self.body = {'phase': phase, 'executionRootSha256': sha(self.root), 'cohort': cohort,
                     'batch': self.pin(self.batch_path), 'outputMarker': self.L.claim_output(self.output, self.contract)}
        if phase == 'exposure':
            self.gate_contract = self.put('gate.json', {'phase': 'gate', 'cohort': cohort})
            self.gate_result = self.put('gate.json.result.json', {'synthetic': 'gate result'})
            self.body.update(gateContract=self.pin(self.gate_contract), gateResult=self.pin(self.gate_result))
        self.write(self.contract, self.body)
        Path(str(self.contract)+'.sha256').write_text(f'{sha(self.contract)}  {self.contract.name}\n')
        self.store = self.L.Store(self.contract, self.batch, self.output)
        self.expected = [{k: c[k] for k in KEY} for c in cells]
        self.data = (self.doc, self.body, self.batch_path, self.batch, self.expected, self.store)
        self.D._phase = lambda *a: self.data
        gate = gate or {'captures': {'captures': []}, 'report': {}}
        self.D.result_for = lambda *a: gate
        self.endpoint_calls = []
        self.admission = type('Admission', (), {})()
        self.admission.endpoints = lambda doc, item, current=False: self.endpoint_calls.append((item['sha256'], current))
        self.admission.validate_numerical = lambda *a: self.pin(self.put('numerical.json', {'synthetic': 'admission'}))
        self.admission.validate_captures = lambda batch, captures, output: {'members': [], 'artifacts': []}
        self.D.admission_module = lambda doc: self.admission
        self.components = {}

    def reseal(self):
        """Write root.json from self.doc with the dispatcher's seal sidecar (tests may extend
        self.doc after creating the files its pins name; self.data holds the same dict)."""
        self.root.write_text(json.dumps(self.doc, indent=2)+'\n')
        Path(str(self.root)+'.sha256').write_text(f'{sha(self.root)}  {self.root.name}\n')
        return self.root

    def put(self, name, value):
        path = self.repo/name; path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(value, indent=2)+'\n'); return path

    def write(self, path, value):
        Path(path).parent.mkdir(parents=True, exist_ok=True); Path(path).write_text(json.dumps(value)+'\n')

    def pin(self, path):
        """Repository-relative root/input pin (the original dispatcher's pin form)."""
        return {'path': str(Path(path).resolve().relative_to(self.repo)), 'sha256': sha(path)}

    def register(self, role, entrypoint, config):
        """A role module loaded from its real source file by the dispatcher's own `source`."""
        self.components[role] = (self.D.source(entrypoint, 'livekit_role_'+role+'_'+uuid.uuid4().hex), config)
        self.D._component = lambda doc, name: self.components[name]
        return self.components[role][0]

    def logical_claim(self):
        logical = Path(str(self.contract)+'.started.json')
        if not logical.exists():
            self.L.write_once(logical, {'contractSha256': sha(self.contract), 'batchSha256': sha(self.batch_path),
                'phase': self.body['phase'], 'pid': os.getpid(), 'gpuLease': self.D._LEASE['token'],
                'output': str(self.output), 'numericalAdmission': self.pin(self.put('numerical.json', {'synthetic': 'admission'}))})
        return logical

    def attempt_claim(self):
        """A planned and started attempt held by this process (Store.plan/Store.start)."""
        attempt = self.store.plan(); self.logical_claim()
        return attempt, self.store.start(attempt, self.D._LEASE['token'])

    def analysis_claim(self):
        return self.L.write_once(self.store.analysis_marker, {'schema': 'w50-live-analysis-claim-1',
            'logicalContract': self.L.pin(self.contract), 'captures': self.L.pin(self.batch_path),
            'pid': os.getpid(), 'gpuLease': self.D._LEASE['token'], 'output': str(self.output)})

    @contextlib.contextmanager
    def lease(self):
        with self.C.D.owned_gpu_lock():
            self.D._LEASE = self.C.D._LEASE
            try: yield
            finally: self.D._ACTIVE = None; self.D._LEASE = None

    @contextlib.contextmanager
    def stage(self, stage, claim, members=(), payloads=()):
        """A genuine dispatcher context for `stage`; the caller already holds the lease."""
        self.logical_claim()
        context = self.D._context(self.root, self.contract, self.data, stage, claim, list(members), list(payloads))
        try: yield context
        finally: self.D._ACTIVE = None


# ---------------------------------------------------------------------------------------------
# EndToEnd: one synthetic world for the real dispatcher and all seven real role sources.
#
# The synthetic repository mirrors the real layout. Every Python source the draft root's closure
# executes is copied byte for byte to its own relative path, and the root registers the seven
# role entrypoints and configs by content pin, so the dispatcher's own _component loads each role
# exactly as a sealed root wires it. Stand-ins replace only the lowest seams, each at the file or
# process boundary the real role crosses:
#   * the two CURRENT3 paired transports (browser, census, renderer, GPU draw);
#   * the root-bound DL5h repeat helper (pair statistics against the native bar);
#   * measurement/phase_sources.py (PNG decoding and native/current report reading). Its blind
#     path reads the REAL native role's checkpointed native read, so native values reach the
#     judge from the real preparation; only the candidate pixel reading is synthetic;
#   * the owner role's Node/TS referee child (subprocess.run on live-node.mjs);
#   * root admission and pre-fit verification (authority.validate_body, prefit proofs), which
#     run against the real draft root instead (draft_root.py).
# The native archive is synthetic frames in the real archive format; the real native role reads
# it. Numerical admission, batch/phase validation, the journal, measurement projection, routing,
# the judge, the fit analysis, the fit record and report validation are the real sources.
# ---------------------------------------------------------------------------------------------
import shutil
import subprocess
import types

REL_RESULTS = Path('packages/calibration/results')
REL_FIT = REL_RESULTS/'2026-10-08-w50-g1-fit'
REL_CURRENT3 = REL_RESULTS/'2026-10-08-w50-g1-current3'
REL_G0 = REL_RESULTS/'2026-10-08-w50-g0-declaration'
REAL_REPO = HERE.parents[4]
P1 = 'apple-macos-27.0-1x-dark-standard-glass0.25'
P2 = 'apple-macos-27.0-2x-dark-standard-glass0.25'
P5 = 'apple-macos-27.0-1x-dark-standard-glass0.5'
CURRENT_GENERATION = 'b2d074d2df24-940384c06f73'
W48_GENERATION = 'd0219cd684bf'
ROLE_FILES = {'capture': ('live-roles/capture.py', 'synthetic/capture-config.json'),
              'native': ('live-roles/native.py', 'synthetic/native-config.json'),
              'measurement': ('live-roles/measurement.py', 'synthetic/measurement-config.json'),
              'owner': ('live-roles/owner.py', 'synthetic/owner-config.json'),
              'judge': ('judge/live.py', 'synthetic/judge-config.json'),
              'fit': ('fit/live.py', 'synthetic/fit-config.json'),
              'initializer': ('fit/execution.py', 'synthetic/initializer-config.json')}
# Non-Python files a copied role or the initializer's runtime check names by path and hash.
EXTRA_FILES = ('owner-candidate/live-node.mjs', 'owner-candidate/live-python.py',
               'owner-candidate/live-python-shim', 'owner-candidate/live-probe.mjs', 'owner-candidate/bridge.ts',
               'owner/node-guard.mjs', 'web/node-guard.mjs', 'web/vite-guard.mjs', 'execution/guard.py',
               'fit/runtime-entry.mjs', 'fit/runtime-bridge.ts', 'fit/runtime-probe.ts')
OWNER_RUNTIME = ('owner-candidate/live.py', 'owner-candidate/live-node.mjs', 'owner-candidate/live-python.py',
                 'owner-candidate/live-python-shim', 'owner-candidate/bridge.ts', 'owner/node-guard.mjs',
                 'web/node-guard.mjs', 'web/vite-guard.mjs', 'execution/guard.py', 'owner-candidate/live-probe.mjs')
VENV = Path('/Users/new/vitrea-w49/py')
# The owner Node closure's source-only probe answers this at the process boundary; the synthetic
# runtime closure records its hash as the exercise the owner preflight must reproduce.
PROBE_STDOUT = '{"exercise":"synthetic source-only","pixels":"NONE"}\n'
OWNER_AGGREGATES = ('C1', 'M1/0.25/dark/rest')
INTRINSIC_RECORDS = ('beforeActive', 'beforeReceded', 'methods', 'activeEntries')

STANDIN_COMMON = r'''
import hashlib, json, sys, types
from pathlib import Path
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]
G0 = ROOT/'synthetic/g0'
CANVAS = {'width': 4, 'height': 3}
def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def pin(path): path = Path(path).resolve(); return dict(path=str(path), sha256=sha(path))
def read_json(path): return json.loads(Path(path).read_text())
read = read_json
def write_new(path, value):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with Path(path).open('x') as stream: stream.write(json.dumps(value, indent=2)+'\n')
write = write_new
def png(width, height):
    return b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR'+width.to_bytes(4, 'big')+height.to_bytes(4, 'big')+b'synthetic'
def scale(profile): return 2 if '-2x-' in profile else 1
def position(profile): return .25 if profile.endswith('glass0.25') else .5
def pose(scene): return 'receded' if scene.endswith('__inactive') else 'active'
def load_source(path, name):
    value = types.ModuleType(name); value.__file__ = str(path)
    exec(compile(Path(path).read_bytes(), str(path), 'exec'), value.__dict__); return value
def pin_file(pin, base=ROOT):
    path = (base/pin['path']).resolve()
    if sha(path) != pin['sha256']: raise ValueError('Changed pinned file')
    return path
def external(path): return Path(path).resolve()
def candidate_info(pin, position, *, current=False):
    """The real candidate document format (execution/test_support.py), read by its endpoint pins."""
    path = pin_file(pin); doc = read_json(path)
    if doc.get('glassTintAmount') != position: raise ValueError('Candidate position differs from plan')
    endpoints = {}
    for slot, item in doc['endpoints'].items():
        endpoint = read_json(path.parent/item['path'])
        endpoints[slot] = dict(path=str(path.parent/item['path']), sha256=item['sha256'],
                               profileKey=endpoint['profileKey'], resolvedMaterialSha256='0'*16, patch=endpoint['patch'])
    return dict(path=str(path), sha256=sha(path), endpoints=endpoints)
def page(run, scene, tier, endpoint):
    return dict(sceneId=scene, requestedRenderer=tier, devicePixelRatio=scale(run['profile']),
                candidateDocument=dict(declarationSha256=run['candidate']['sha256'][:12]),
                candidate=run['candidate']['sha256'], profileKey=endpoint['profileKey'])
def pair(folder, scene, tier, value):
    dims = (CANVAS['width']*value['devicePixelRatio'], CANVAS['height']*value['devicePixelRatio'])
    for side, suffix in (('first', ''), ('second', '__repeat')):
        (folder/f'{scene}__{tier}{suffix}.png').write_bytes(png(*dims))
        write_new(folder/f'page__{tier}__{side}.json', value)
    write_new(folder/f'report__{tier}.json', dict(page=value))
    write_new(folder/f'repeat__{tier}.json', dict(schema=1, kind='w50-retained-repeat-pair', reading='first',
        scene=scene, renderer=tier,
        first=dict(image=pin(folder/f'{scene}__{tier}.png'), report=pin(folder/f'page__{tier}__first.json')),
        second=dict(image=pin(folder/f'{scene}__{tier}__repeat.png'), report=pin(folder/f'page__{tier}__second.json'))))
def admit_repeat(context, run, record):
    dispatcher = sys.modules['w50_g1_dispatch']
    helper = load_source(dispatcher.checked(ROOT, context['repeatAdmission']['entrypoint']), 'synthetic_repeat')
    return helper.admit_pair(context, run, record, record['repeatPair'])
def source_probe(): return {'status': 'SOURCE_ONLY'}
'''

STANDIN_W50 = '"""SYNTHETIC STAND-IN for CURRENT3\'s W50 new-bed paired transport (no browser/census/GPU)."""' + \
    STANDIN_COMMON + r'''
def scene_plan(run, phase='fit'):
    scenes = ROOT/'synthetic/scenes-w50.json'
    return dict(source='w50', scenesPath=str(scenes), scenesSha256=sha(scenes), canvas=dict(CANVAS),
                dpr=scale(run['profile']), position=position(run['profile']),
                scenes=[dict(scene=s, role='calibration', background='grey', span=96, pose=pose(s)) for s in run['scenes']])
def fixture_info(run, plan):
    fixtures = run['fixtures']
    return dict(path=fixtures['path'], manifestSha256=fixtures['manifestSha256'],
                backgrounds=[dict(key=f'grey@{plan["dpr"]}x', path=fixtures['path']+'/grey.png', sha256='c'*64)])
def validate_report(envelope, run, endpoint, *, abscissa='silhouette', phase='fit'):
    value = envelope['page']
    if value.get('sceneId') not in run['scenes'] or value.get('candidate') != run['candidate']['sha256'] \
            or value.get('profileKey') != endpoint['profileKey']:
        raise ValueError('Synthetic report differs from its member')
    return [dict(scene=value['sceneId'], encodedLuminance=.5, provenance=dict(kind=abscissa))]
def _capture_run(context, run, *, current):
    dispatcher = sys.modules['w50_g1_dispatch']
    dispatcher.require_render_admission(context, run, current=current)
    plan = scene_plan(run, context['phase']); lane = 'current' if current else 'candidate'
    candidate = candidate_info(run['candidate'], plan['position'], current=current)
    fixture = fixture_info(run, plan)
    for item in read_json(pin_file(run['webSourceClosure']))['sources']: pin_file(item)
    output, matrix = external(run['captureRoot']), external(run['matrixPath'])
    output.mkdir(parents=True); matrix.parent.mkdir(parents=True, exist_ok=True)
    records = []
    for spec in plan['scenes']:
        scene = spec['scene']; tier = run['renderer']
        write_new(output/f'census-{scene}.json', {'passes': True})
        endpoint = candidate['endpoints'][f'{spec["pose"]}.dark']
        argv = ['node', 'capture-web.ts', '--renderer', tier, '--scale', str(plan['dpr']),
                '--candidate-document', candidate['path'], '--out', str(output), scene]
        write_new(output/f'request-{scene}.json', dict(argv=argv, sceneSource=plan['source'],
            scenesSha256=plan['scenesSha256'], candidate=run['candidate'], fixture=fixture, lane=lane))
        (output/f'capture-{scene}.log').write_text('synthetic driver\n')
        folder = output/scene; folder.mkdir()
        pair(folder, scene, tier, page(run, scene, tier, endpoint))
        write_new(folder/f'cell__{tier}.json', dict(renderer=tier, colorSpace='srgb',
                  capturePath=f'declarationSha256={run["candidate"]["sha256"][:12]}'))
        report = folder/f'report__{tier}.json'
        arguments = validate_report(read_json(report), run, endpoint, abscissa='source', phase=context['phase'])
        artifacts = {name: pin(path) for name, path in [('png', folder/f'{scene}__{tier}.png'), ('report', report),
                                                        ('cell', folder/f'cell__{tier}.json')]}
        for argument in arguments:
            argument['provenance'].update(report=artifacts['report'], capture=artifacts['png'],
                sceneSource=plan['source'], scenesSha256=plan['scenesSha256'], candidateDocument=run['candidate'],
                baseline=current, endpoint={k: v for k, v in endpoint.items() if k != 'patch'})
        record = dict(profile=run['profile'], renderer=tier, scene=scene, candidate=run['candidate'], lane=lane,
            sceneSource=plan['source'], canvas=plan['canvas'], dpr=plan['dpr'], artifacts=artifacts,
            arguments=arguments, background=fixture['backgrounds'][0])
        record['repeatPair'] = pin(folder/f'repeat__{tier}.json')
        record['repeatAdmission'] = admit_repeat(context, run, record)
        write_new(folder/'w50-capture.json', record); records.append(record)
    write_new(matrix, dict(schema='w50-web-capture-index-1', captures=records))
    return records
'''

STANDIN_CANONICAL = '"""SYNTHETIC STAND-IN for CURRENT3\'s canonical compare transport (no browser/census/GPU)."""' + \
    STANDIN_COMMON + r'''
WEB = HERE.parent/'web'
SCENES = ROOT/'synthetic/scenes.json'
def scene_plan(run, phase, document=None):
    return dict(scenes=[dict(id=s, state='inactive' if s.endswith('__inactive') else 'rest', fixtureSet='calibration',
                             component='c', background='bg') for s in run['scenes']],
                dpr=scale(run['profile']), scheme='dark', a11y='standard', position=position(run['profile']),
                canvas=dict(CANVAS), tints={}, components={'c': {'kind': 'rrect'}})
def validate_matrix(matrix, run, candidate):
    rows = matrix['cells']
    if [(r['key']['profileKey'], r['key']['web']['renderer'], r['key']['sceneId']) for r in rows] != \
            [(run['profile'], run['renderer'], s) for s in run['scenes']]:
        raise ValueError('Measured membership differs from run')
    if any(f'declarationSha256={run["candidate"]["sha256"][:12]}' not in r['key']['web']['capturePath'] for r in rows):
        raise ValueError('Candidate provenance differs')
    return rows
def validate_report(envelope, run, plan, scene, endpoint):
    value = envelope['page']
    if value.get('sceneId') != scene['id'] or value.get('candidate') != run['candidate']['sha256'] \
            or value.get('profileKey') != endpoint['profileKey']:
        raise ValueError('Synthetic canonical report differs')
def capture_artifacts(folder, scene, tier, web, dpr):
    meta = folder/f'cell__{tier}.json'; report = folder/f'report__{tier}.json'; image = folder/f'{scene["id"]}__{tier}.png'
    if read(meta) != web or web.get('renderer') != tier or web.get('colorSpace') != 'srgb':
        raise ValueError('Capture metadata differs or has wrong tier/colour space')
    header = image.read_bytes()[:24]
    if header[:8] != b'\x89PNG\r\n\x1a\n' or tuple(int.from_bytes(header[i:i+4], 'big') for i in (16, 20)) != \
            (CANVAS['width']*dpr, CANVAS['height']*dpr):
        raise ValueError('Capture dimensions differ from canonical raster')
    artifacts = {name: dict(path=str(p), sha256=sha(p)) for name, p in [('cell', meta), ('report', report), ('png', image)]}
    artifacts['files'] = [dict(path=str(p), sha256=sha(p)) for p in sorted(folder.iterdir()) if p.is_file()]
    return artifacts
def capture_run(context, run, *, current=False):
    dispatcher = sys.modules['w50_g1_dispatch']
    dispatcher.require_render_admission(context, run, current=current)
    plan = scene_plan(run, context['phase']); lane = 'current' if current else 'candidate'
    web = load_source(WEB/'adapter.py', 'synthetic_canonical_web')
    candidate = web.candidate_info(run['candidate'], plan['position'], current=current)
    for item in read(web.pin_file(run['webSourceClosure']))['sources']: web.pin_file(item)
    captures, matrix = web.external(run['captureRoot']), web.external(run['matrixPath'])
    captures.mkdir(parents=True); matrix.parent.mkdir(parents=True, exist_ok=True)
    write(captures/'native-request.json', dict(profile=run['profile'], scenes=run['scenes']))
    write(captures/'request.json', dict(argv=['compare'], run=run, phase=context['phase'], lane=lane,
        contractSha256=sha(context['contract']), batchSha256=sha(context['batchPath']), scenesSha256=sha(SCENES)))
    cells = []; tier = run['renderer']
    for scene in plan['scenes']:
        sid = scene['id']; folder = captures/run['profile']/sid; folder.mkdir(parents=True)
        write(captures/f'census-{sid}.json', {'passes': True})
        paired = ['node', '--import', 'tsx', 'capture-web.ts', sid, '--renderer', tier, '--scale', str(plan['dpr']),
                  '--candidate-document', candidate['path'], '--out', str(captures/run['profile']), '--alpha']
        write(captures/f'request-{sid}.json', dict(argv=['compare', '--scene', sid], paired=paired))
        (captures/f'capture-{sid}.log').write_text('paired\n')
        endpoint = candidate['endpoints'][f'{"receded" if scene["state"] == "inactive" else "active"}.dark']
        pair(folder, sid, tier, page(run, sid, tier, endpoint))
        metadata = dict(renderer=tier, colorSpace='srgb', capturePath=f'declarationSha256={run["candidate"]["sha256"][:12]}')
        write(folder/f'cell__{tier}.json', metadata)
        fresh = {str(p): sha(p) for p in folder.iterdir() if p.is_file()}
        (captures/f'compare-{sid}.log').write_text('compare\n'); write(captures/f'exit-{sid}.json', dict(returncode=0))
        write(captures/f'fresh-{sid}.json', dict(schema='w50-fresh-paired-input-1', artifacts=fresh))
        write(captures/f'native-admission-{sid}.json', {'synthetic': 'native admission'})
        cells.append(dict(key=dict(profileKey=run['profile'], sceneId=sid, web=metadata), fixtureSet='calibration'))
    write(matrix, dict(schemaVersion=5, cells=cells))
    records = []
    for row in validate_matrix(read(matrix), run, candidate['path']):
        scene = next(s for s in plan['scenes'] if s['id'] == row['key']['sceneId']); sid = scene['id']
        folder = captures/run['profile']/sid
        endpoint = candidate['endpoints'][f'{"receded" if scene["state"] == "inactive" else "active"}.dark']
        validate_report(read(folder/f'report__{tier}.json'), run, plan, scene, endpoint)
        artifacts = capture_artifacts(folder, scene, tier, row['key']['web'], plan['dpr'])
        artifacts['transport'] = [pin(captures/name) for name in (f'census-{sid}.json', f'request-{sid}.json',
            f'exit-{sid}.json', f'compare-{sid}.log', f'capture-{sid}.log', f'fresh-{sid}.json', 'request.json',
            'native-request.json', f'native-admission-{sid}.json')]
        record = dict(profile=run['profile'], renderer=tier, scene=sid, sceneSource='canonical', lane=lane,
            candidate=run['candidate'], endpoint=endpoint, matrix=pin(matrix), row=row, artifacts=artifacts,
            coherenceStatus='NOT_APPLICABLE' if tier == 'webgpu' else
                'MEASURED' if row.get('coherence') is not None else 'UNMEASURED')
        record['repeatPair'] = pin(folder/f'repeat__{tier}.json')
        record['repeatAdmission'] = web.admit_repeat(context, run, record)
        records.append(record)
    write(captures/'complete.json', dict(status='CAPTURED', captures=records, matrixSha256=sha(matrix)))
    return records
'''

STANDIN_REPEAT = r'''"""SYNTHETIC STAND-IN for the root-bound DL5h repeat helper: identical pairs, member-owned proofs."""
import hashlib, json, sys, types
from pathlib import Path
S = types.SimpleNamespace(FIT=Path(__file__).resolve().parent,
    M=types.SimpleNamespace(N=types.SimpleNamespace(required_arguments=lambda inventory: set())))
def sha(raw): return hashlib.sha256(raw).hexdigest()
def _pin(path): return dict(path=str(path), sha256=sha(Path(path).read_bytes()))
def _read(pin):
    raw = Path(pin['path']).read_bytes()
    if sha(raw) != pin['sha256']: raise ValueError('Changed retained pin')
    return json.loads(raw)
def _folder(run, record):
    folder = Path(run['captureRoot'])
    if run['sceneSource'] == 'canonical': folder /= run['profile']
    return folder/record['scene']
def read_pair(context, run, record, pair_pin):
    folder = _folder(run, record)
    if pair_pin['path'] != str(folder/f'repeat__{record["renderer"]}.json'): raise ValueError('Pair aliases another member')
    pair = _read(pair_pin)
    return dict(pair=pair, pages=[_read(pair[side]['report']) for side in ('first', 'second')],
                envelope=_read(record['artifacts']['report']), identical=True, noise=0.0, folder=folder)
def receipt_binding(context, run, record, config, rows, *, needs_statistics=False):
    return dict(config=context['repeatAdmission']['config'], declaredRows=rows,
        **{name: sha(Path(context[field]).read_bytes()) for name, field in (('executionRootSha256', 'executionRoot'),
            ('contractSha256', 'contract'), ('batchSha256', 'batchPath'))})
def _body(binding, record, retained):
    return dict(schema='w50-repeat-admission-1', reading='first', scene=record['scene'], lane=record['lane'],
        manifest=record['repeatPair'], config=binding['config'], pair=retained['pair'],
        originalArtifacts={k: record['artifacts'][k] for k in ('png', 'report', 'cell')},
        declaredStatistics=[r['statistic'] for r in binding['declaredRows']],
        **{k: binding[k] for k in ('executionRootSha256', 'contractSha256', 'batchSha256')})
def retained_proof(output, run, record, retained):
    if record['repeatAdmission']['path'] != str(retained['folder']/f'repeat-admission__{run["renderer"]}.json'):
        raise ValueError('Repeat proof is not the member-owned receipt')
    return _read(record['repeatAdmission'])
def verify_pair_semantics(binding, run, record, retained, proof):
    if proof != _body(binding, record, retained): raise ValueError('Repeat receipt is not bound to this exact pair')
def admit_pair(context, run, record, pair_pin):
    dispatcher = sys.modules['w50_g1_dispatch']
    dispatcher.require_render_admission(context, run, current=record['lane'] == 'current')
    config = dispatcher.load(dispatcher.checked(context['repo'], context['repeatAdmission']['config']))
    rows = [r for r in dispatcher.load(dispatcher.checked(context['repo'], config['references']))['cells']
            if all(r[k] == record[k] for k in ('profile', 'renderer', 'scene'))]
    retained = read_pair(context, run, record, pair_pin)
    path = retained['folder']/f'repeat-admission__{run["renderer"]}.json'
    body = _body(receipt_binding(context, run, record, config, rows), {**record, 'repeatAdmission': None}, retained)
    with path.open('x') as stream: stream.write(json.dumps(body, indent=2)+'\n')
    return _pin(path)
'''

STANDIN_GUARD = 'def validate_tone_values(argument):\n    assert "encodedLuminance" in argument\n'

STANDIN_PHASE_SOURCES = r'''"""SYNTHETIC STAND-IN for measurement/phase_sources.py: the PNG and native-report reading seam.

The real measure_phase calls PhaseSources(context, root, config), then measure_member,
current_measurement, blind_envelope and validate_blind_rows. The shapes mirror the real reader.
Exposed new-bed rows carry a three-run native identity, canonical rows a native PNG pin, and
frozen canonical T1 its named production statistic. Blind cells read the REAL native role's
checkpointed native read: cell statistics, repeat bundles and per-run support witnesses, mapped as
measurement/capture.evaluate_native_supports maps them. Only the candidate pixel reading is
synthetic: the native value (or, for canonical T1, the original current), moved by
synthetic/control.json's offset for a named key on the candidate lane.
"""
import copy, hashlib, json, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]
KEY = ('profile', 'renderer', 'scene', 'statistic')
LEVELS = {'deep8-channel-median': ('deep8', 'encoded-RGB-codes'),
          'central8-channel-median': ('center8', 'encoded-RGB-codes'),
          'deep8-far24-luma-mean': ('deep8_far24', 'encoded-luma-codes'),
          'deep8-far24-luma-median': ('deep8_far24', 'encoded-luma-codes'),
          'T1-full-silhouette': ('full-silhouette', 'linear-luma')}
PRODUCER = 'packages/calibration/src/metrics/material.ts#interiorLevel'


def read(path): return json.loads(Path(path).read_text())
def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def control():
    path = ROOT/'synthetic/control.json'
    return read(path) if path.is_file() else {}


def shifted(value, delta):
    if value is None or not delta: return copy.deepcopy(value)
    return [min(255, v+delta) for v in value] if isinstance(value, list) else value+delta


class PhaseSources:
    def __init__(self, context, root, config):
        self.live = sys.modules['w50_g1_dispatch']; self.live.require_context(context)
        if root != self.live.sealed(context['executionRoot']):
            raise ValueError('Source reader root differs from the actual registered root')
        if config['completedCurrentEvidence'] != root.get('currentEvidence'):
            raise ValueError('Current measurements differ from the root-bound composed current evidence')
        self.context, self.root, self.config = context, root, config
        self.repo = Path(context['repo'])
        self.exposed = read(ROOT/'synthetic/exposed-native.json')

    def offset(self, key, lane):
        return control().get('offsets', {}).get('|'.join(key), 0) if lane == 'candidate' else 0

    def material(self, candidate_pin):
        """The drawn document pair: the candidate document's dark endpoint content hashes."""
        doc = read(self.repo/candidate_pin['path'])
        return {'documentPair': {'activeSha256': doc['endpoints']['active.dark']['sha256'],
                                 'recededSha256': doc['endpoints']['receded.dark']['sha256']}}

    def measure_member(self, run, receipt, rows):
        self.live.require_read_admission(self.context, run, current=receipt['lane'] == 'current')
        material = self.material(run['candidate'])
        evidence = {'capture': copy.deepcopy(receipt['artifacts']['png']), 'material': material}
        if any(r['role'] == 'blind' for r in rows):
            return self.blind(run, receipt, rows, evidence)
        if all(r['statistic'] == 'owner-contracts' for r in rows):
            # An owner-only member: pointers only, as the real canonical_member's 'owner' family.
            return {'statistics': {}, 'evidence': evidence, 'material': material, 'arguments': [],
                    'declaration': {'sceneSource': 'canonical', 'family': 'owner', 'inputCode': None, 'span': None,
                                    'pose': 'receded' if receipt['scene'].endswith('__inactive') else 'active',
                                    'scale': 2 if '-2x-' in receipt['profile'] else 1,
                                    'position': .25 if receipt['profile'].endswith('glass0.25') else .5}}
        spec = self.exposed['/'.join(receipt[k] for k in KEY[:3])]
        statistics = {}
        for row in rows:
            if row['statistic'] == 'owner-contracts': continue
            key = tuple(row[k] for k in KEY)
            value = spec['statistics'][row['statistic']]
            statistic = self.statistic(row, value, shifted(value['candidate'], self.offset(key, receipt['lane'])))
            if value['kind'] == 'canonical':
                statistic['productionStatistic'] = dict(estimator='PRODUCTION_TS_INTERIOR_LEVEL',
                    statistic=row['statistic'], producer=PRODUCER, field='material.interiorStdDevWeb',
                    reading='first', scene=row['scene'], units='linear-luma', value=statistic['value'],
                    capture=copy.deepcopy(evidence['capture']), matrix=copy.deepcopy(receipt['matrix']))
            statistics[row['statistic']] = statistic
        return {'statistics': statistics, 'evidence': evidence, 'material': material,
                'declaration': copy.deepcopy(spec['declaration']), 'arguments': []}

    def statistic(self, row, value, reading):
        support, units = LEVELS[row['statistic']]
        out = dict(status='MEASURED', measurementStatus='MEASURED', value=reading, nativeValue=copy.deepcopy(value['native']),
                   required=True, support=support, units=units, nativeRepeat=copy.deepcopy(value['repeat']),
                   nativeSupportWitnesses=copy.deepcopy(value['witnesses']))
        if value['kind'] == 'canonical': out['nativeImage'] = copy.deepcopy(value['nativeImage'])
        else: out.update(nativeRuns=copy.deepcopy(value['runs']), nativeProvenance={'synthetic': 'exposed native'})
        return out

    def current_measurement(self, row, *, name):
        value = self.exposed['/'.join(row[k] for k in KEY[:3])]['statistics'][name]
        pair = row['currentDocumentPair']
        evidence = {'capture': copy.deepcopy(value['currentCapture']),
                    'material': {'documentPair': {'activeSha256': pair['active.dark'], 'recededSha256': pair['receded.dark']},
                                 'originalDocumentPair': copy.deepcopy(pair)}}
        return self.statistic(row, value, copy.deepcopy(value['current'])), evidence

    def blind(self, run, receipt, rows, evidence):
        """A statistic the completed read stopped (DL5n) or recorded UNMEASURED_REPORTED
        (DL5m 4) is not computed: it reaches the judge UNMEASURED, native side null."""
        if self.context['phase'] != 'exposure' or any(r['role'] != 'blind' for r in rows):
            raise ValueError('Original blind population may only be measured inside exposure')
        payload = self.live.qualification_native(self.context)
        artifacts = payload['nativeExposure']
        stops = {(s['cell'], s['statistic']): s['reason'] for s in payload['stops']}
        native = read(artifacts['nativeRead']['path'])
        if native['ready'] is not payload['ready'] or \
                {(s['cell'], s['statistic']): s['reason'] for s in native['stops']} != stops:
            raise ValueError('Native read stops differ from the checkpoint payload')
        cells = [c for c in native['cells'] if (c['profile'], c['scene']) == (receipt['profile'], receipt['scene'])]
        if len(cells) != 1: raise ValueError('Blind member has no unique native cell')
        cell = cells[0]
        provenance = {'nativeRead': copy.deepcopy(artifacts['nativeRead']),
                      'nativeExposure': copy.deepcopy(artifacts['artifactManifest'])}
        evidence.update(copy.deepcopy(provenance))
        statistics = {}
        for name, value in cell['statistics'].items():
            support, units = LEVELS[name]
            witnesses = [dict(run=r['run'], **{k: r['readings']['supports'][support][k]
                              for k in ('pixels', 'maskShape', 'maskPackedBitsSha256')}) for r in cell['runs']]
            unread = (cell['id'], name) in stops or value.get('status') == 'UNMEASURED_REPORTED'
            complete = value.get('value') is not None and not unread
            key = (receipt['profile'], receipt['renderer'], receipt['scene'], name)
            reading = shifted(value['value'], self.offset(key, receipt['lane'])) if complete else None
            status = 'UNMEASURED' if unread else 'UNMEASURED_EMPTY_SUPPORT' if not complete else \
                'REPORTED' if not value['required'] else 'MEASURED'
            statistic = dict(status=status, measurementStatus='MEASURED' if complete else
                             'UNMEASURED' if unread else 'UNMEASURED_EMPTY_SUPPORT',
                             required=value['required'], support=support, units=units, value=reading,
                             runValues=[reading]*3, aggregation='coordinatewise-median-of-three-run-statistics',
                             nativeValue=None if unread else copy.deepcopy(value['value']),
                             nativeRepeat=None if unread else copy.deepcopy(value['repeat']),
                             nativeSupportWitnesses=witnesses)
            if not value['required']: statistic['B'] = None
            statistic['nativeRuns'] = [copy.deepcopy(r['evidence']) for r in cell['runs']]
            statistic['nativeProvenance'] = copy.deepcopy(provenance)
            statistics[name] = statistic
        declaration = {'sceneSource': 'w50', 'family': cell['family'], 'inputCode': cell.get('level'),
                       'span': cell['span'], 'pose': cell['pose'], 'scale': cell['scale'], 'position': cell['glass']}
        return {'statistics': statistics, 'evidence': evidence, 'material': evidence['material'],
                'declaration': declaration, 'nativeCell': cell}

    def blind_envelope(self, row, measured):
        """The real envelope (phase_sources.blind_envelope), over the real native artifact manifest."""
        cell, evidence = measured['nativeCell'], measured['evidence']
        if row['role'] != 'blind' or any(row[k] != cell[k] for k in ('profile', 'scene', 'role')) \
                or row['nativeIdentity'] != cell['id'] or row['referenceIdentity'] != cell['reference'] \
                or row['statistic'] not in cell['statistics'] or [r['run'] for r in cell['runs']] != [1, 2, 3]:
            raise ValueError('Blind typed envelope differs from the exact original row/run population')
        if sha(evidence['nativeExposure']['path']) != evidence['nativeExposure']['sha256']:
            raise ValueError('Changed native exposure artifact manifest')
        artifact = read(evidence['nativeExposure']['path'])
        if artifact['nativeRead'] != evidence['nativeRead']:
            raise ValueError('Blind envelope substituted its actual preparation reading')
        return {'schema': 'w50-native-three-run-evidence-1',
            **{k: copy.deepcopy(row[k]) for k in
               ('profile', 'scene', 'statistic', 'nativeIdentity', 'referenceIdentity', 'role', 'support')},
            'runs': [copy.deepcopy(r['evidence']) for r in cell['runs']],
            'nativeRead': copy.deepcopy(evidence['nativeRead']), 'nativeExposure': copy.deepcopy(evidence['nativeExposure']),
            'nativeExport': {'role': 'blind', 'root': artifact['export']['path'],
                             'indexSha256': artifact['export']['indexSha256']}}

    def validate_blind_rows(self, rows):
        for row in rows:
            item = row['nativeEvidence']
            if read(item['path']).get('schema') != 'w50-native-three-run-evidence-1' or sha(item['path']) != item['sha256']:
                raise ValueError('Blind row lacks its typed native envelope')


def source_probe():
    return {'status': 'SOURCE_ONLY'}
'''


def _axes(reason='synthetic owner referee'):
    out = {name: {'state': 'NOT_APPLICABLE', 'reason': reason} for name in ('M1', 'M2', 'C1', 'X1', 'L1', 'E2', 'coherence')}
    out['M1'] = {'state': 'MEASURED', 'verdict': 'within', 'R': 1.0}
    return out


class EndToEnd:
    """One synthetic world: a sealed root, three batches and the real dispatcher (see above)."""

    def __init__(self, case, *, offsets=None, levels=None):
        """offsets: candidate-lane reading shifts by key (synthetic/control.json). levels: native
        frame levels by (cell id, run), overriding the archive's defaults (a blind data property)."""
        self.levels = dict(levels or {})
        temp = tempfile.TemporaryDirectory(); case.addCleanup(temp.cleanup)
        self.case = case; self.base = Path(temp.name).resolve()
        self.repo = self.base/'repo'; self.repo.mkdir()
        (self.base/'outputs').mkdir()
        self.outputs = {phase: self.base/'outputs'/phase for phase in ('fit', 'gate', 'exposure')}
        self.fit_dir = self.repo/REL_FIT
        self.copy_sources()
        self.load_dispatcher()
        self.build_declaration()
        self.build_inventory()
        self.build_inputs()
        self.build_root()
        self.build_batches()
        self.put('synthetic/control.json', {'offsets': offsets or {}})
        self.child = []; self.probes = []
        real = subprocess.run
        def run(args, *a, **kw):
            if isinstance(args, (list, tuple)) and len(args) == 2 and str(args[1]).endswith('owner-candidate/live-node.mjs'):
                return self.owner_child(args, kw)
            if isinstance(args, (list, tuple)) and str(args[-1]).endswith('owner-candidate/live-probe.mjs'):
                self.probes.append(list(args))
                return subprocess.CompletedProcess(args, 0, stdout=PROBE_STDOUT, stderr='')
            return real(args, *a, **kw)
        from unittest import mock
        patcher = mock.patch.object(subprocess, 'run', side_effect=run); patcher.start(); case.addCleanup(patcher.stop)

    # files -----------------------------------------------------------------------------------
    def put(self, relative, value):
        path = self.repo/relative; path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(value, indent=2, sort_keys=True)+'\n'); return self.pin(path)

    def text(self, relative, value):
        path = self.repo/relative; path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(value); return path

    def pin(self, path):
        return {'path': str(Path(path).resolve().relative_to(self.repo)), 'sha256': sha(path)}

    @staticmethod
    def absolute(path):
        path = Path(path).resolve(); return {'path': str(path), 'sha256': sha(path)}

    # sources ---------------------------------------------------------------------------------
    def copy_sources(self):
        """Every Python source the draft root's composite probe executes, byte for byte."""
        draft = json.loads((REAL_REPO/REL_FIT/'live-execution/execution-root.draft.json').read_text())
        self.copied = sorted(draft['closure']['sources'])
        for relative in self.copied:
            target = self.repo/relative; target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(REAL_REPO/relative, target)
        for relative in EXTRA_FILES:
            target = self.fit_dir/relative; target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(REAL_REPO/REL_FIT/relative, target)
        (self.fit_dir/'owner-candidate/live-python-shim').chmod(0o755)
        self.standins = {REL_CURRENT3/'web/adapter.py': STANDIN_W50, REL_CURRENT3/'canonical/adapter.py': STANDIN_CANONICAL,
                         REL_FIT/'measurement/phase_sources.py': STANDIN_PHASE_SOURCES,
                         Path('synthetic/repeat-helper.py'): STANDIN_REPEAT,
                         Path('synthetic/g0/audit/numerical_guard.py'): STANDIN_GUARD}
        for relative, text in self.standins.items(): self.text(relative, text)

    def load_dispatcher(self):
        live, tag = self.fit_dir/'live-execution', uuid.uuid4().hex
        self.D = module(live/'dispatch.py', 'e2e_dispatch_'+tag)
        self.C = module(live/'common.py', 'e2e_common_'+tag)
        self.L = module(live/'lifecycle.py', 'e2e_lifecycle_'+tag)
        self.Q = module(live/'quarantine.py', 'e2e_quarantine_'+tag)
        old = self.C.D.GPU_LOCK; self.C.D.GPU_LOCK = self.base/'gpu.lock'
        self.case.addCleanup(setattr, self.C.D, 'GPU_LOCK', old)
        self.case.addCleanup(lambda: sys.modules.pop('w50_g1_dispatch', None))

    # declaration, native bed and archive -------------------------------------------------------
    def build_declaration(self):
        F = module(REAL_REPO/REL_FIT/'execution/test_support.py', 'e2e_candidate_fixture_'+uuid.uuid4().hex)
        self.reader = module(REAL_REPO/REL_FIT/'native/test_reader.py', 'e2e_native_fixture_'+uuid.uuid4().hex)
        built = F.build(self.repo, REAL_REPO/REL_G0, self.C.D.PROOFS)
        self.cohort, self.baselines, self.numerical = built['cohort'], built['baselines'], built['numerical']
        self.manifest, self.scenes = self.bed()
        manifest = Path(built['manifest']); manifest.write_text(json.dumps(self.manifest, indent=2)+'\n')
        scenes = manifest.with_name('scenes-w50.json'); scenes.write_text(json.dumps(self.scenes, indent=2)+'\n')
        self.manifest_pin, self.scenes_pin = self.pin(manifest), self.pin(scenes)
        one, two = Path(built['one']), Path(built['two'])
        for path in (one, two):
            doc = json.loads(path.read_text())
            doc['sources'] = [p for p in doc['sources'] if p['path'] != self.manifest_pin['path']]
            doc['sources'] += [self.manifest_pin, self.scenes_pin]
            if path == two:
                doc['partOneSha256'] = sha(one)
                doc['selection'] = ['Minimum worst exposed low-end level error', 'Minimum mean absolute low-end level error',
                                    'Minimum squared normalized coefficient distance from current over range[0,1]',
                                    'Lexicographic candidate id']
                doc['candidateDomain']['rankingNormalisationRange'] = 1
            path.write_text(json.dumps(doc, sort_keys=True)+'\n')
        self.one, self.two = self.pin(one), self.pin(two)
        self.text('synthetic/scenes-w50.json', '{"synthetic": "new-bed scene plan"}\n')
        self.text('synthetic/scenes.json', '{"synthetic": "canonical scenes"}\n')
        self.build_archive()

    def bed(self):
        """native/test_reader.py's bed with live-roles/test_native.py's additions: the structured
        and DL5c-control blind cells beside the uniform and span ones, all at glass 0.5."""
        manifest, scenes = self.reader.bed()
        for cell in manifest['cells']:
            if cell['background'].startswith('grey-'): cell['level'] = int(cell['background'][5:])
        profile = self.reader.PROFILE
        calibration = next(c for c in manifest['cells'] if c['family'] == 'structured')
        structured = dict(calibration, span=224, role='blind', scene='cell-impulse-sparse-s224__rest',
                          id=profile+'/cell-impulse-sparse-s224__rest')
        manifest['cells'].append(structured)
        ref = next(r for r in manifest['references'] if r['id'] == structured['reference'])
        ref['roles'].append('blind'); ref['roles'].sort()
        scenes['scenes'].append(dict(id=structured['scene'], background='impulse-sparse', component='span-224', state='rest'))
        scenes['split']['holdout'].append(structured['scene']); scenes['profiles'][0]['scenes'].append(structured['scene'])
        control = dict(next(c for c in manifest['cells'] if c['family'] == 'span' and c['span'] == 224),
                       background='grey-000', level=0, pose='receded', scene='cell-grey-000-s224__inactive',
                       id=profile+'/cell-grey-000-s224__inactive', reference=profile+'/ref-grey-000__inactive',
                       passName='bed-receded')
        manifest['cells'].append(control)
        manifest['references'].append(dict(id=control['reference'], scene='ref-grey-000__inactive', profile=profile,
            background='grey-000', roles=['blind'], passName='bed-receded', run=1))
        for scene, component in ((control['scene'], 'span-224'), ('ref-grey-000__inactive', 'none')):
            scenes['scenes'].append(dict(id=scene, background='grey-000', component=component, state='inactive'))
            scenes['profiles'][0]['scenes'].append(scene)
        scenes['split']['holdout'].append(control['scene']); scenes['split']['recorded'].append('ref-grey-000__inactive')
        return manifest, scenes

    def build_archive(self):
        archive = self.base/'archive'; archive.mkdir(); rows = []
        declaration = sha(self.repo/self.one['path'])
        for spec in self.manifest['cells']+self.manifest['references']:
            is_ref = 'roles' in spec
            # The DL5c control's body is drawn at its black backdrop, so its detected support is empty.
            level = -50 if spec.get('id', '').endswith('cell-grey-000-s224__inactive') else \
                -30 if spec.get('pose') == 'receded' else 20
            for run in ([1] if is_ref else [1, 2, 3]):
                role = 'blind' if is_ref and 'blind' in spec['roles'] else spec.get('role', 'calibration')
                row, raw = self.reader.fixture_row(spec, run, self.scenes, role,
                                                   level=self.levels.get((spec['id'], run), level))
                row['roles'] = spec['roles'] if is_ref else [spec['role']]
                row['declarationSha256'] = declaration
                if spec['scene'].endswith('inactive'):
                    row['native']['presentedActive'] = False
                    row['native']['presentation'] = dict(observedPose='inactive', isKeyWindow=False, appIsActive=False)
                file = archive/row['path']; file.parent.mkdir(parents=True, exist_ok=True); file.write_bytes(raw)
                rows.append(row)
        index = self.reader.reseal(archive, rows)
        asset = self.base/'archive.tar.zst'; asset.write_bytes(b'synthetic archive asset')
        pack = self.put('synthetic/pack.json', dict(indexSha256=index, sha256=sha(asset), declarationSha256=declaration))
        self.native_config = self.put('synthetic/native-config.json', dict(schema='w50-native-exposure-inputs-1',
            archiveRoot=str(archive), archiveIndexSha256=index, archiveAsset=self.absolute(asset), pack=pack,
            manifest=self.manifest_pin, scenes=self.scenes_pin, partOne=self.one, partTwo=self.two))
        prepare = self.D.source(self.fit_dir/'exposure/prepare.py', 'e2e_fixture_plan_'+uuid.uuid4().hex)
        self.plans = prepare.read_fixture_plan(archive/'index.json', index, self.manifest, self.scenes,
                                               self.outputs['exposure']/'native-blind')
        self.native_pack = pack

    # inventory ---------------------------------------------------------------------------------
    def original(self, profile, renderer, scene, statistic, role, **extra):
        return {**dict(profile=profile, renderer=renderer, scene=scene, statistic=statistic, role=role,
                       support='synthetic original support', B=None, historical=[], currentGeneration=CURRENT_GENERATION,
                       currentDocumentPair={'active.dark': 'a'*64, 'receded.dark': 'b'*64}), **extra}

    def build_inventory(self):
        rows, exposed = [], {}
        def level(profile, renderer, position):
            scene = 'cell-grey-004-s096__rest'
            rows.append(self.original(profile, renderer, scene, 'deep8-channel-median', 'calibration',
                                      nativeIdentity=f'{profile}/{scene}'))
            current = self.text(f'synthetic/current/{profile}-{renderer}-{scene}.png', 'current capture\n')
            exposed[f'{profile}/{renderer}/{scene}'] = {
                'declaration': dict(sceneSource='w50', family='uniform', inputCode=4, span=96, pose='active',
                                    scale=1, position=position),
                'statistics': {'deep8-channel-median': dict(kind='w50', native=[20]*3, current=[22]*3, candidate=[20]*3,
                    repeat={'barCodes': [.5]*3, 'passes': True}, runs=[{'run': n, 'sha256': str(n)*64} for n in (1, 2, 3)],
                    witnesses=[{'run': n, 'maskShape': [64, 64], 'pixels': 100, 'maskPackedBitsSha256': 'c'*64}
                               for n in (1, 2, 3)], currentCapture=self.absolute(current))}}
        level(P1, 'webgpu', .25); level(P1, 'css', .25); level(P5, 'webgpu', .5)
        def target(profile, scene, stratum, role):
            fidelity = {'statistic': 'T1-full-silhouette', 'native': .25, 'current': .375, 'reference': .75}
            rows.append(self.original(profile, 'webgpu', scene, 'T1-full-silhouette', role, B=.0625, stratum=stratum,
                                      fidelity=fidelity, native=.25, current=.375))
            image = self.text(f'synthetic/native/{profile}-{scene}.png', 'native image\n')
            current = self.text(f'synthetic/current/{profile}-{scene}.png', 'current capture\n')
            exposed[f'{profile}/webgpu/{scene}'] = {
                'declaration': dict(sceneSource='canonical', family='texture', inputCode=None, span=None,
                                    pose='receded' if scene.endswith('__inactive') else 'active',
                                    scale=2 if '-2x-' in profile else 1, position=.25),
                'statistics': {'T1-full-silhouette': dict(kind='canonical', native=.25, current=.375, candidate=.375,
                    repeat={'code': .0625, 'bar': .03125, 'B': .0625}, nativeImage=self.absolute(image),
                    witnesses=[{'run': 1, 'maskShape': [384, 512], 'pixels': 1000, 'maskPackedBitsSha256': 'd'*64}],
                    currentCapture=self.absolute(current))}}
        target(P1, 'checkerboard__rrect-md__rest', 'C', 'calibration')
        target(P2, 'checkerboard__rrect-md__rest', 'C', 'calibration')
        target(P1, 'checkerboard-8__rrect-lg__inactive', 'F', 'validation')
        target(P2, 'checkerboard-8__rrect-lg__inactive', 'F', 'validation')
        target(P1, 'photo__rrect-md__rest', 'P', 'calibration')
        target(P2, 'photo__rrect-md__rest', 'P', 'historical-prediction-check')
        rows.append(self.original(P1, 'webgpu', 'checkerboard__rrect-md__rest', 'owner-contracts', 'calibration'))
        rows.append(self.original(P1, 'css', 'checkerboard__rrect-md__rest', 'owner-contracts', 'calibration'))
        rows.append(self.original(P2, 'webgpu', 'photo__rrect-md__rest', 'owner-contracts', 'calibration'))
        names = {'uniform': ('deep8-channel-median', 'central8-channel-median')}
        every = ('deep8-channel-median', 'central8-channel-median', 'deep8-far24-luma-mean',
                 'deep8-far24-luma-median', 'T1-full-silhouette')
        for cell in self.manifest['cells']:
            if cell['role'] != 'blind': continue
            for renderer in ('webgpu', 'css'):
                for statistic in names.get(cell['family'], every):
                    rows.append(self.original(cell['profile'], renderer, cell['scene'], statistic, 'blind',
                                              nativeIdentity=cell['id'], referenceIdentity=cell['reference']))
        self.rows = rows; self.exposed = exposed
        self.inventory = {'schema': 'w50-reference-inventory-1', 'cells': rows, 'generations': {
            CURRENT_GENERATION: {'documentPair': {'active.dark': 'a'*64, 'receded.dark': 'b'*64}},
            W48_GENERATION: {'documentPair': {'active.dark': '1'*64, 'receded.dark': '2'*64}}}}
        self.references = self.put('synthetic/references.json', self.inventory)
        self.completed = self.put('synthetic/completed-references.json', {'cells': copy.deepcopy(rows)})
        self.put('synthetic/exposed-native.json', exposed)
        self.dependencies = self.C.D.derive_phase_dependencies(rows)

    # inputs ------------------------------------------------------------------------------------
    def build_inputs(self):
        prepare = self.D.source(self.fit_dir/'exposure/prepare.py', 'e2e_keys_'+uuid.uuid4().hex)
        blind = {(c['profile'], c['scene']) for c in self.manifest['cells'] if c['role'] == 'blind'}
        self.reported = [list(k) for k in prepare.R.reported_reference_keys(self.manifest, self.scenes)
                         if (k[0], k[2]) in blind]
        self.empty = [list(k) for k in prepare.empty_support_keys(self.manifest, self.scenes)]
        owners = {name: {'readingSchema': {'requiredFinite': [], 'requiredArrays': [], 'conditionalFinite': [],
                                           'unmeasuredExceptions': [], 'aggregate': None}}
                  for name in ('M1', 'M2', 'C1', 'X1', 'L1', 'E2', 'coherence')}
        owners['M1']['readingSchema']['requiredFinite'] = ['R']
        self.owner_contracts = self.put('synthetic/owner-contracts.json', {'schema': 'w50-owner-contracts-1', 'axes': owners})
        self.binding = self.put('synthetic/binding.json', {'original': self.references, 'reportedKeys': self.reported,
            'emptySupportKeys': self.empty, 'ownerContracts': self.owner_contracts})
        cut = [dict(profile=r['profile'], tier='webgpu', scene=r['scene'], stratum=r['stratum'],
                    scale=2 if '-2x-' in r['profile'] else 1,
                    pose='inactive' if r['scene'].endswith('__inactive') else 'rest',
                    native=r['native'], candidate=r['current'], reference=r['fidelity']['reference'], B=r['B'],
                    code=.0625, bar=.03125) for r in self.rows if r.get('stratum')]
        self.cut = self.put('synthetic/cut.json', {'T1': {'cells': cut}})
        self.targets = self.put('synthetic/targets-config.json', {'schema': 'w50-target-contract-config-1',
            'inventory': self.references, 'cut': self.cut, 'currentGeneration': CURRENT_GENERATION,
            'w48Generation': W48_GENERATION})
        configs = {}
        # The prepared current owner report's membership (judge/live.owner_membership): every owner
        # union cell the referee stand-in reports, and its aggregates.
        self.owner_report = self.put('synthetic/owner-current-report.json', {'synthetic': 'prepared current owner report'})
        union = {'report': self.owner_report, 'aggregates': sorted(OWNER_AGGREGATES),
                 'cells': sorted({'/'.join(k[:3]) for k in self.dependencies['ownerUnionKeys']})}
        configs['judge'] = self.put(ROLE_FILES['judge'][1], {'schema': 'w50-judge-config-1', 'references': self.references,
            'binding': self.binding, 'ownerContracts': self.owner_contracts, 'targets': self.targets, 'ownerUnion': union})
        configs['fit'] = self.put(ROLE_FILES['fit'][1], {'schema': 'w50-fit-analysis-config-1', 'partTwo': self.two,
                                                         'references': self.references})
        self.composition = self.put('synthetic/completed-current-composition.json', {'synthetic': 'composition'})
        self.native_batch = self.put('synthetic/native-read-batch.json', {'schema': 'w50-native-read-batch-1',
            'inputs': {'manifest': self.manifest_pin, 'declaration': self.one, 'scenes': self.scenes_pin}})
        reports = {role: self.put(f'synthetic/native-{role}.json', {'synthetic': role})
                   for role in ('calibration', 'validation')}
        self.current = self.put('synthetic/completed-current.json', {'schema': 'w50-completed-current-evidence-2',
            'status': 'EVIDENCE_ONLY', 'currentComposition': self.composition,
            'originals': {'references': self.references, 'scenes': self.scenes_pin},
            'native': {'batch': self.native_batch, 'reports': reports}, 'arguments': [], 'referenceEvidence': []})
        canonical = self.put('synthetic/canonical-references.json', {'schema': 'w50-canonical-reference-evidence-1',
                                                                     'partitions': {}})
        configs['measurement'] = self.put(ROLE_FILES['measurement'][1], {'schema': 'w50-phase-measurement-inputs-1',
            'completedReferences': self.completed, 'completedCurrentEvidence': self.current,
            'canonicalReferenceEvidence': canonical,
            'native': {'batch': self.native_batch, 'scenes': self.scenes_pin, 'reports': reports}})
        configs['capture'] = self.put(ROLE_FILES['capture'][1], {'schema': 'w50-live-capture-config-1', 'transports': {
            'canonical': self.pin(self.repo/REL_CURRENT3/'canonical/adapter.py'),
            'w50': self.pin(self.repo/REL_CURRENT3/'web/adapter.py')}})
        configs['native'] = self.native_config
        self.repeat_config = self.put('synthetic/repeat-config.json', {'schema': 'w50-repeat-config-1',
                                                                       'references': self.references})
        self.host = self.pin(self.text('synthetic/new-bed-host.mjs', '// synthetic new-bed host\n'))
        self.web_closure = self.put('synthetic/web-source-closure.json', {'sources': [self.host]})
        # LIVE checks the owner's intrinsic records structurally before any marker: declarations
        # exactly the cohort, and both positions' receded records resolving by hash.
        receded = {position: {name: self.pin(self.text(f'synthetic/intrinsic/{position}-{name}.json',
                                                        json.dumps({'synthetic': name, 'position': position})+'\n'))
                              for name in INTRINSIC_RECORDS} for position in ('0.25', '0.5')}
        self.intrinsic = self.put('synthetic/owner-intrinsic.json', {'candidateDeclarations': self.cohort,
                                                                     'recededRecords': receded})
        node = self.absolute(shutil.which('node'))
        tsx = self.absolute(REAL_REPO/'packages/calibration/node_modules/tsx/dist/esm/api/index.mjs')
        owner_runtime = self.put('synthetic/owner-runtime.json', {'schema': 'w50-owner-candidate-runtime-1',
            'sources': [self.pin(self.fit_dir/p) for p in OWNER_RUNTIME], 'exercise': 'synthetic source-only',
            'probe': self.absolute(self.fit_dir/'owner-candidate/live-probe.mjs'), 'toolchain': {'node': node, 'tsx': tsx},
            'exerciseSha256': hashlib.sha256(PROBE_STDOUT.encode()).hexdigest()})
        configs['owner'] = self.put(ROLE_FILES['owner'][1], {'schema': 'w50-owner-candidate-config-1',
            'ownerInputs': self.absolute(self.text('synthetic/owner-inputs.json', '{}\n')),
            'completedOwnerReferences': self.absolute(self.text('synthetic/owner-references.json', '{}\n')),
            'originalInventory': self.absolute(self.repo/self.references['path']),
            'frozenSourceClosure': self.absolute(self.text('synthetic/frozen-owner.json', '{"sources": []}\n')),
            'sourcePins': {}, 'runtimeClosure': self.absolute(self.repo/owner_runtime['path']), 'node': node, 'tsx': tsx,
            'interpreter': self.absolute(VENV/'bin/python'), 'pythonLaunch': str(VENV/'bin/python'),
            'pythonPrefix': str(VENV), 'pythonVenvConfig': self.absolute(VENV/'pyvenv.cfg'),
            'python': str(self.fit_dir/'owner-candidate/live-python-shim'), 'pythonEnvironment': {}})
        fit_runtime = self.put('synthetic/fit-runtime-closure.json', {'schema': 'w50-fit-runtime-closure-1',
            'sources': [self.pin(self.fit_dir/p) for p in ('fit/runtime-entry.mjs', 'fit/runtime-bridge.ts',
                        'fit/runtime-probe.ts', 'owner/node-guard.mjs', 'web/node-guard.mjs')],
            'node': node, 'exercise': {'status': 'SYNTHETIC_PRODUCTION_BRIDGE_EXERCISED',
                'probe': self.pin(self.fit_dir/'fit/runtime-probe.ts'),
                'branches': {'fixedJoinEndpoints': 4, 'builtCandidates': 2, 'heldTransfers': 2, 'heldMutationRefusals': 2}}})
        configs['initializer'] = self.put(ROLE_FILES['initializer'][1], {'schema': 'w50-fit-initializer-inputs-1',
            'completedCurrent': self.current, 'output': str(REL_FIT/'fit/live-initializer'),
            'runtime': {'closure': fit_runtime, 'node': node}})
        self.configs = configs
        self.prefit = self.put('synthetic/pre-fit-evidence.json', {'references': self.completed, 'synthetic': 'pre-fit'})
        self.inputs = []
        for item in (*configs.values(), self.references, self.binding, self.owner_contracts, self.targets, self.cut,
                     self.two, self.completed, self.current, canonical, self.native_batch, self.scenes_pin, *reports.values(),
                     self.native_pack, self.repeat_config, self.web_closure, self.host, owner_runtime, fit_runtime,
                     self.composition):
            if item not in self.inputs: self.inputs.append(item)

    # root ----------------------------------------------------------------------------------------
    def build_root(self):
        instruments = {name: {'entrypoint': self.pin(self.fit_dir/entrypoint), 'config': self.configs[name]}
                       for name, (entrypoint, _) in ROLE_FILES.items()}
        for role in instruments.values():
            for item in role.values():
                if item not in self.inputs: self.inputs.append(item)
        sources = {relative: sha(self.repo/relative) for relative in self.copied if relative.endswith('.py')}
        self.doc = {'schema': 'w50-g1-execution-root-1', 'repo': str(self.repo), 'lifecycle': 'logical-phase-attempts-1',
            'quarantine': 'instrument-api-role-discipline-1', 'bootstrap': self.pin(self.fit_dir/'live-execution/dispatch.py'),
            'partOne': self.one, 'partTwo': self.two, 'references': self.references, 'manifest': self.manifest_pin,
            'candidateDomain': json.loads((self.repo/self.two['path']).read_text())['candidateDomain'],
            'phaseDependencies': self.dependencies, 'reportedKeys': self.reported, 'emptySupportKeys': self.empty,
            'ownerBudgetKeys': self.C.D.owner_budget_keys(self.rows), 'ownerContracts': self.owner_contracts,
            'baselineDocuments': self.baselines,
            'repeatAdmission': {'entrypoint': self.pin(self.repo/'synthetic/repeat-helper.py'), 'config': self.repeat_config},
            'newBedHost': self.host, 'currentEvidence': self.current, 'currentComposition': self.composition,
            'instruments': instruments, 'inputs': self.inputs, 'closure': {'sources': sources, 'environment': {}}}
        self.root = self.fit_dir/'live-execution/execution-root.json'
        self.root.write_text(json.dumps(self.doc, indent=2)+'\n')
        Path(str(self.root)+'.sha256').write_text(f'{sha(self.root)}  {self.root.name}\n')
        world = self
        def admitted(path):
            doc = world.C.D.sealed(path)
            cells = world.C.D.load(world.C.D.checked(doc['repo'], doc['references']))['cells']
            world.C.D.verify_phase_dependencies(doc, cells)
            return doc
        authority = types.SimpleNamespace(root_doc=admitted, verify_prefit=lambda path, doc: dict(world.prefit))
        self.D._CORE = {'C': self.C, 'A': authority, 'L': self.L, 'Q': self.Q, 'root': str(self.root.resolve()),
                        'sha': sha(self.root), 'guard': None}

    # batches -----------------------------------------------------------------------------------
    def build_batches(self):
        candidates = {.25: self.cohort[0], .5: self.cohort[1]}
        baselines = {.25: self.baselines[0], .5: self.baselines[1]}
        blind = {(c['profile'], c['scene']): c for c in self.manifest['cells'] if c['role'] == 'blind'}
        def runs(keys, phase):
            groups = {}
            for profile, renderer, scene in sorted({tuple(k[:3]) for k in keys}):
                source = 'w50' if scene.startswith('cell-') else 'canonical'
                pose = 'receded' if scene.endswith('__inactive') else 'active'
                group = (profile, renderer, source, pose if source == 'w50' and phase == 'exposure' else '')
                groups.setdefault(group, []).append(scene)
            out = []
            for index, ((profile, renderer, source, pose), scenes) in enumerate(sorted(groups.items())):
                position = .25 if profile.endswith('glass0.25') else .5
                run = {'id': f'{phase}-{index}', 'profile': profile, 'renderer': renderer, 'sceneSource': source,
                       'candidate': candidates[position], 'scenes': scenes,
                       'sets': ['holdout'] if phase == 'exposure' else ['calibration', 'validation'],
                       'captureRoot': 'unused', 'matrixPath': 'unused', 'numericalReferee': self.numerical,
                       'webSourceClosure': self.web_closure,
                       'fixtures': {'path': '/synthetic-fixtures', 'manifestSha256': 'f'*64, 'backgrounds': {}}}
                if phase == 'exposure':
                    run['baselineCandidate'] = baselines[position]
                    if source == 'w50':
                        plan = self.plans[f'{profile}|{pose}']
                        run.update(nativeExposureConfig=self.native_config,
                                   fixtures={k: plan[k] for k in ('path', 'manifestSha256', 'backgrounds')})
                out.append(run)
            return out
        fit_keys = [k for k in self.dependencies['gateKeys'] if k[2] == 'cell-grey-004-s096__rest']
        self.batches = {}
        for phase, keys in (('fit', fit_keys), ('gate', self.dependencies['gateKeys']),
                            ('exposure', self.dependencies['exposureKeys'])):
            batch = {'schema': 'w50-g1-batch-1', 'phase': phase, 'cohort': self.cohort, 'runs': runs(keys, phase)}
            if phase != 'fit': batch['ownerIntrinsicRecords'] = self.intrinsic
            self.put(f'synthetic/batches/{phase}.json', batch)
            self.batches[phase] = self.repo/f'synthetic/batches/{phase}.json'

    # the owner referee child (stand-in at the process boundary) ---------------------------------
    def owner_child(self, args, kwargs):
        request = json.loads(kwargs['input'])
        snapshot = json.loads(Path(request['snapshot']['path']).read_text())
        cells = {'/'.join(k[:3]): _axes() for k in snapshot['ownerUnionKeys']}
        report = {'cells': cells, 'aggregates': {name: {'state': 'MEASURED', 'verdict': 'within'} for name in OWNER_AGGREGATES},
                  'intrinsic': {'X75': {f'endpoint-{i:02}': {'state': 'MEASURED', 'verdict': 'within'} for i in range(12)},
                                'X76': {p: {'state': 'MEASURED', 'verdict': 'within'} for p in ('0.25', '0.5')}},
                  'provenance': {'synthetic': 'owner referee stand-in'}, 'noNewTrade': 'synthetic',
                  'liveUnion': {'snapshot': request['snapshot'], 'config': request['config'],
                                'gateResult': snapshot['gateResult'], 'claim': snapshot['claim'],
                                'cohort': snapshot['cohort'], 'ownerKeys': snapshot['ownerUnionKeys'],
                                'scope': 'FULL_SAME_CANDIDATE_UNION; metric evidence only, full judge owns verdict'}}
        self.child.append(snapshot)
        return subprocess.CompletedProcess(args, 0, stdout=json.dumps(report), stderr='')

    # driving the real dispatcher -----------------------------------------------------------------
    def log(self, path):
        path = Path(path)
        return path.read_text()[-4000:] if path.is_file() else '(no log)'

    def phase(self, name, fit_record=None):
        """create_phase, prepare_attempt, execute_attempt and execute_analysis, as an operator runs them."""
        contract = Path(self.D.create_phase(self.root, self.batches[name], self.outputs[name], fit_record))
        attempt = self.D.prepare_attempt(self.root, contract)
        event = self.D.execute_attempt(self.root, contract, attempt)
        log = self.outputs[name]/'attempts'/f'{attempt["ordinal"]:06d}'/'quarantine/worker.log'
        self.case.assertEqual(event['code'], 'ATTEMPT_COMPLETE', self.log(log))
        event = self.D.execute_analysis(self.root, contract)
        self.case.assertEqual(event, {'schema': 'w50-live-public-event-1', 'code': 'ANALYSIS_COMPLETE', 'phase': name},
                              self.log(self.outputs[name]/'quarantine/analysis.log'))
        return contract, json.loads(Path(str(contract)+'.result.json').read_text())

    def fit_record(self, contract):
        """fit/live.fit_record over the one completed fit, written once where the gate reads it."""
        fit = self.D.source(self.fit_dir/'fit/live.py', 'e2e_fit_record_'+uuid.uuid4().hex)
        record = fit.fit_record(self.root, [self.pin(Path(str(contract)+'.result.json'))])
        path = self.fit_dir/'live-execution/fit-record.json'
        self.C.D.write_once(path, record)
        return path, record

    def initializer(self):
        """fit/execution.py's admission and state under this root, with this dispatcher as its bootstrap."""
        execution = self.D.source(self.fit_dir/'fit/execution.py', 'e2e_initializer_'+uuid.uuid4().hex)
        execution._bootstrap = lambda root_path: self.D
        return execution, execution._state(self.root)
