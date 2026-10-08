"""Test helper (not a role): the REAL LIVE dispatcher/journal under synthetic admitted authority.

Root/pre-fit/numerical/gate admission is an explicit fixture boundary, exactly as in
live-execution/test_execution.py. The context, lease, capability checks, stages and journal
are the real implementation, so a role tested here meets LIVE's actual API, not a permissive
fake.
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
