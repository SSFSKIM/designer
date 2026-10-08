"""LIVE owner role under the real dispatcher; synthetic authority, stubbed owner child.

The owner seam binds its own repository root, so the role, common helper and owner-candidate
boundary sources are copied byte-identically into the synthetic repository, as
owner-candidate/live-test.py does. No owner input, capture, material or native data is read.
"""
import contextlib
import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
FIT = HERE.parent
REL = Path('packages/calibration/results/2026-10-08-w50-g1-fit')
SECRET = 'OWNER_SECRET_12345.875'
COPIES = ('live-roles/owner.py', 'live-roles/common.py', 'owner-candidate/live.py',
          'owner-candidate/live-node.mjs', 'owner-candidate/live-python.py', 'owner-candidate/live-python-shim',
          'owner-candidate/live-probe.mjs', 'owner/node-guard.mjs', 'web/node-guard.mjs',
          'web/vite-guard.mjs', 'execution/guard.py')
VENV = Path('/Users/new/vitrea-w49/py')


def module(path, name):
    spec = importlib.util.spec_from_file_location(name, path); value = importlib.util.module_from_spec(spec)
    sys.modules[name] = value; spec.loader.exec_module(value); return value


K = module(HERE/'livekit.py', 'w50_owner_role_test_kit')


def pin(path):
    path = Path(path).resolve()
    return {'path': str(path), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}


def child_result(returncode=0, stdout=None, stderr=''):
    if stdout is None:
        stdout = json.dumps({'cells': {}, 'aggregates': {}, 'intrinsic': {}, 'provenance': {},
                             'noNewTrade': 'synthetic'})
    return type('Result', (), {'returncode': returncode, 'stdout': stdout, 'stderr': stderr})()


CAPTURE = '''from pathlib import Path
import hashlib,json,sys
def put(path,value):
 path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(value));return {'path':str(path),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
def capture(context,member,config):
 sys.modules['w50_g1_dispatch'].require_render_admission(context,member['run'],current=member['lane']=='current')
 run=member['run'];base=Path(run['captureRoot']);candidate=run['candidate']
 artifacts={k:put(base/(k+'.json'),v) for k,v in {'png':{},'cell':{'capturePath':'declarationSha256='+candidate['sha256'][:12]},
  'report':{'page':{'sceneId':member['scene'],'candidateDocument':{'declarationSha256':candidate['sha256'][:12]}}}}.items()}
 record={'profile':run['profile'],'renderer':run['renderer'],'scene':member['scene'],'lane':member['lane'],
  'candidate':candidate,'artifacts':artifacts,'secret':'%s'}
 pair=put(base/'pair.json',{'first':artifacts['png']})
 record.update(repeatPair=pair,repeatAdmission=put(base/'repeat-admission__css.json',{'manifest':pair,'pair':{'first':artifacts['png']},'originalArtifacts':artifacts}))
 return {'record':record,'artifacts':list(artifacts.values())}
def verify(context,member,record,config):pass
def recover(context,member,config):return None
''' % SECRET
NATIVE = '''import sys
def prepare(context,config):
 sys.modules['w50_g1_dispatch'].require_native_preparation(context)
 return {'ready':True,'native':'%s','artifacts':[]}
def verify(context,payload,config):pass
''' % SECRET
MEASUREMENT = 'def evaluate(context,captures,config):\n return {"synthetic":"measurement"}\n'
JUDGE = '''def evaluate(context,evidence,config):
 assert set(evidence['owner'])=={'report','snapshot'}
 return {'status':'NEITHER','owner':evidence['owner']['snapshot']}
'''


class OwnerRole(unittest.TestCase):
    def build(self, phase='exposure'):
        self.cand = {'path': 'candidate.json', 'sha256': 'a'*64}
        base = {'path': 'baseline.json', 'sha256': 'b'*64}
        run = {'id': 'r', 'profile': 'apple-macos-27.0-1x-dark-standard-glass0.25', 'renderer': 'css',
               'sceneSource': 'w50', 'candidate': self.cand, 'scenes': ['one'], 'sets': ['holdout'],
               'captureRoot': 'unused', 'matrixPath': 'unused'}
        if phase == 'exposure': run['baselineCandidate'] = base
        self.gate_captures = {'status': 'CAPTURED', 'captures': [], 'synthetic': {'exact': ['gate', 1]}}
        kit = K.Kit(self, phase=phase, runs=[run], cohort=[self.cand],
                    gate={'captures': self.gate_captures, 'report': {}})
        self.kit = kit; fit = kit.repo/REL
        for rel in COPIES:
            target = fit/rel; target.parent.mkdir(parents=True, exist_ok=True); shutil.copyfile(FIT/rel, target)
        (fit/'owner-candidate/live-python-shim').chmod(0o755)
        (fit/'owner-candidate/bridge.ts').write_text('export const executeRequest = () => ({});\n')
        intrinsic = kit.pin(kit.put('intrinsic.json', {'syntheticRecords': []}))
        kit.batch['ownerIntrinsicRecords'] = intrinsic; kit.put('batch.json', kit.batch)
        kit.body['batch'] = kit.pin(kit.batch_path)
        node = pin(shutil.which('node'))
        tsx = pin(FIT.parents[1]/'node_modules/tsx/dist/esm/api/index.mjs')
        sources = [{'path': str(p.relative_to(kit.repo)), 'sha256': pin(p)['sha256']}
                   for p in sorted(fit.rglob('*')) if p.is_file()]
        closure = kit.put('owner-runtime.json', {'schema': 'w50-owner-candidate-runtime-1', 'sources': sources,
            'exercise': 'synthetic source-only', 'probe': pin(fit/'owner-candidate/live-probe.mjs'),
            'toolchain': {'node': node, 'tsx': tsx}})
        config = kit.put('owner-config.json', {'schema': 'w50-owner-candidate-config-1',
            'ownerInputs': pin(kit.put('owner-inputs.json', {})),
            'completedOwnerReferences': pin(kit.put('owner-references.json', {})),
            'originalInventory': pin(kit.repo/kit.references['path']),
            'frozenSourceClosure': pin(kit.put('frozen.json', {'sources': []})),
            'sourcePins': {}, 'runtimeClosure': pin(closure), 'node': node, 'tsx': tsx,
            'interpreter': pin(VENV/'bin/python'), 'pythonLaunch': str(VENV/'bin/python'),
            'pythonPrefix': str(VENV), 'pythonVenvConfig': pin(VENV/'pyvenv.cfg'),
            'python': str(fit/'owner-candidate/live-python-shim'), 'pythonEnvironment': {}})
        self.config = kit.pin(config)
        kit.doc['inputs'] = [self.config, kit.pin(closure)]
        kit.put('root.json', kit.doc); kit.body['executionRootSha256'] = K.sha(kit.root)
        # A live root is sealed; common.registered reads it through the dispatcher's sealed().
        Path(str(kit.root)+'.sha256').write_text(f'{K.sha(kit.root)}  root.json\n')
        if phase == 'exposure':
            gate_batch = kit.put('gate-batch.json', {'phase': 'gate', 'cohort': [self.cand],
                                                     'ownerIntrinsicRecords': intrinsic})
            gate = kit.put('gate.json', {'phase': 'gate', 'cohort': [self.cand],
                'executionRootSha256': K.sha(kit.root), 'batch': kit.pin(gate_batch)})
            result = kit.put('gate.json.result.json', {'contractSha256': K.sha(gate),
                                                       'captures': self.gate_captures})
            kit.body.update(gateContract=kit.pin(gate), gateResult=kit.pin(result))
        kit.write(kit.contract, kit.body)
        self.role = kit.register('owner', fit/'live-roles/owner.py', self.config)
        self.captures = {'status': 'CAPTURED', 'captures': [], 'synthetic': {'exact': ['exposure', 2]}}
        return kit

    def setUp(self):
        self.child = patch.object(subprocess, 'run', return_value=child_result()).start()
        self.addCleanup(patch.stopall)

    def marker(self, **changes):
        kit = self.kit
        return kit.L.write_once(kit.store.analysis_marker, {'schema': 'w50-live-analysis-claim-1',
            'logicalContract': kit.L.pin(kit.contract), 'captures': kit.L.pin(kit.batch_path),
            'pid': os.getpid(), 'gpuLease': kit.D._LEASE['token'], 'output': str(kit.output), **changes})

    def test_analysis_snapshot_carries_this_execution_claim(self):
        kit = self.build()
        with kit.lease():
            claim = self.marker()
            with kit.stage('analysis', claim) as context:
                result = self.role.evaluate(context, self.captures, self.config)
        snapshot = json.loads(Path(result['snapshot']['path']).read_text())
        self.assertEqual(snapshot['executionClaim'], claim)
        self.assertEqual(snapshot['claim'], pin(str(kit.contract)+'.started.json'))
        self.assertEqual(snapshot['exposureCaptures'], self.captures)
        self.assertEqual(snapshot['gateCaptures'], self.gate_captures)
        self.assertEqual(result['report']['noNewTrade'], 'synthetic')
        self.assertTrue(Path(result['snapshot']['path']).is_relative_to(kit.output))
        self.assertEqual(self.child.call_count, 1)

    def test_capture_and_qualification_stages_refuse_before_any_owner_read(self):
        kit = self.build()
        with kit.lease():
            attempt, claim = kit.attempt_claim()
            for stage in ('capture', 'qualification'):
                with self.subTest(stage=stage), kit.stage(stage, claim, attempt['members'][:1]) as context:
                    with self.assertRaisesRegex(ValueError, 'outside its LIVE stage'):
                        self.role.evaluate(context, self.captures, self.config)
        self.assertFalse((kit.output/'owner-candidate.snapshot.json').exists())
        self.child.assert_not_called()

    def test_analysis_claim_of_another_process_or_lease_refuses(self):
        for changes in ({'pid': -1}, {'gpuLease': 'W50 pid=1 owner=another\n'}):
            with self.subTest(changes=changes):
                kit = self.build()
                with kit.lease():
                    claim = self.marker(**changes)
                    with kit.stage('analysis', claim) as context:
                        with self.assertRaisesRegex(ValueError, 'process and lease'):
                            self.role.evaluate(context, self.captures, self.config)
        self.child.assert_not_called()

    def test_attempt_claim_cannot_stand_in_for_the_analysis_marker(self):
        kit = self.build()
        with kit.lease():
            _, claim = kit.attempt_claim()
            with kit.stage('analysis', claim) as context:
                with self.assertRaisesRegex(ValueError, 'full-union analysis marker'):
                    self.role.evaluate(context, self.captures, self.config)
        self.assertFalse(kit.store.analysis_marker.exists())
        self.child.assert_not_called()

    def test_copied_context_and_gate_phase_refuse(self):
        kit = self.build()
        with kit.lease():
            claim = self.marker()
            with kit.stage('analysis', claim) as context:
                with self.assertRaisesRegex(ValueError, 'No genuine live context'):
                    self.role.evaluate(dict(context), self.captures, self.config)
        gate = self.build(phase='gate')
        with gate.lease():
            claim = self.marker()
            with gate.stage('analysis', claim) as context:
                with self.assertRaisesRegex(ValueError, 'exposure-only'):
                    self.role.evaluate(context, self.captures, self.config)
        self.child.assert_not_called()

    def test_unregistered_config_refuses(self):
        kit = self.build()
        other = kit.pin(kit.put('other-config.json', json.loads(Path(kit.repo/self.config['path']).read_text())))
        with kit.lease():
            claim = self.marker()
            with kit.stage('analysis', claim) as context:
                with self.assertRaisesRegex(ValueError, 'prospective root input'):
                    self.role.evaluate(context, self.captures, other)
        self.child.assert_not_called()

    # DL5k enforcement: the role runs inside the real execute_analysis quarantine.
    def flow(self, outcome):
        kit = self.build()
        for role, text in (('capture', CAPTURE), ('native', NATIVE), ('measurement', MEASUREMENT), ('judge', JUDGE)):
            path = kit.base/(role+'.py'); path.write_text(text); kit.register(role, path, {})
        def noisy(*args, **kwargs):
            print(SECRET); print(SECRET, file=sys.stderr)
            os.write(1, (SECRET+'\n').encode()); os.write(2, (SECRET+'\n').encode())
            if outcome == 'refused':return child_result(1, '', 'owner refused '+SECRET)
            return child_result(stdout=json.dumps({'cells': {'secret': SECRET}, 'aggregates': {},
                'intrinsic': {}, 'provenance': {}, 'noNewTrade': SECRET}))
        self.child.side_effect = noisy
        with patch.object(kit.C.D, 'validate_report', lambda *a, **k: None), self.streams() as seen:
            attempt = kit.D.prepare_attempt(kit.root, kit.contract)
            done = kit.D.execute_attempt(kit.root, kit.contract, attempt)
            self.assertFalse(kit.store.analysis_marker.exists()); self.child.assert_not_called()
            event = kit.D.execute_analysis(kit.root, kit.contract)
            status = kit.D.public_status(kit.root, kit.contract)
        public = json.dumps([done, event, status]) + seen()
        self.assertEqual(done['code'], 'ATTEMPT_COMPLETE')
        self.assertNotIn(SECRET, public)
        self.assertIn(SECRET, (kit.output/'quarantine/analysis.log').read_text())
        self.assertEqual(self.child.call_count, 1)
        return kit, event

    @contextlib.contextmanager
    def streams(self):
        """Python-level and file-descriptor-level stdout/stderr of the whole flow."""
        seen = []; text = io.StringIO(); saved = [os.dup(1), os.dup(2)]
        with tempfile.TemporaryFile() as sink:
            sys.stdout.flush(); sys.stderr.flush()
            os.dup2(sink.fileno(), 1); os.dup2(sink.fileno(), 2)
            try:
                with contextlib.redirect_stdout(text), contextlib.redirect_stderr(text):
                    yield lambda: ''.join(seen)
            finally:
                for fd, original in zip((1, 2), saved): os.dup2(original, fd); os.close(original)
                sink.seek(0); seen.extend([text.getvalue(), sink.read().decode()])

    def test_completed_owner_evidence_is_quarantined(self):
        kit, event = self.flow('complete')
        self.assertEqual(event, {'schema': 'w50-live-public-event-1', 'code': 'ANALYSIS_COMPLETE', 'phase': 'exposure'})
        result = json.loads(Path(str(kit.contract)+'.result.json').read_text())
        snapshot = json.loads(Path(result['report']['owner']['path']).read_text())
        self.assertEqual(snapshot['executionClaim'], kit.L.pin(kit.store.analysis_marker))

    def test_refused_owner_child_stops_analysis_without_publishing_values(self):
        kit, event = self.flow('refused')
        self.assertEqual(event, {'schema': 'w50-live-public-event-1', 'code': 'ANALYSIS_STOPPED', 'phase': 'exposure'})
        self.assertFalse(Path(str(kit.contract)+'.result.json').exists())
        with self.assertRaises(ValueError): kit.store.plan()

    def test_source_probe_is_source_only(self):
        self.assertEqual(module(HERE/'owner.py', 'w50_owner_role_probe').source_probe(), {'status': 'SOURCE_ONLY'})


if __name__ == '__main__':
    unittest.main()
