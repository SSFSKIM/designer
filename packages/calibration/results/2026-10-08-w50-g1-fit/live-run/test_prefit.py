"""prefit.py on a synthetic sealed root in a synthetic git repository.

The repository holds execution/test_support.py's synthetic G0 declaration and cohort, LIVE's own
prefit.py beside the root (current3 verify_prefit loads it from there), the r2 supersession
base and ten synthetic standing proofs. Root admission (authority.validate_body) is the
fixture boundary, as in livekit; discovery is the real guard over a synthetic probe, suites
are real unittest runs, and the written evidence is verified by LIVE's own
authority.verify_prefit (current3's checks on the root's evidence slot, then the lineage).
"""
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
FIT = HERE.parent
FIT_REL = Path('packages/calibration/results/2026-10-08-w50-g1-fit')
LIVE = FIT/'live-execution'


def module(path, name):
    spec = importlib.util.spec_from_file_location(name, path); value = importlib.util.module_from_spec(spec)
    sys.modules[name] = value; spec.loader.exec_module(value); return value


P = module(HERE/'prefit.py', 'w50_live_run_test_prefit')
A = module(LIVE/'authority.py', 'w50_live_run_test_authority')
CHAIN = module(LIVE/'common.py', 'w50_live_run_test_chain')
S = module(FIT/'execution/test_support.py', 'w50_live_run_test_support')
D = A.D
GUARD = module(LIVE/'guard.py', 'w50_live_run_test_guard')


def git(repo, *args):
    return subprocess.run(['git', '-C', str(repo), '-c', 'user.name=t', '-c', 'user.email=t@t', *args],
                          check=True, capture_output=True, text=True).stdout.strip()


class Synthetic:
    def __init__(self, case, *, failing_suite=False):
        temp = tempfile.TemporaryDirectory(); case.addCleanup(temp.cleanup)
        self.repo = repo = Path(temp.name).resolve()/'repo'; repo.mkdir()
        git(repo, 'init', '-q')
        built = S.build(repo, FIT.parent/'2026-10-08-w50-g0-declaration', D.PROOFS)
        self.live = repo/FIT_REL/'live-execution'; self.live.mkdir(parents=True)
        for name in ('prefit.py', 'owner_evidence.py', 'native_evidence.py'):
            shutil.copyfile(LIVE/name, self.live/name)
        self.builder = repo/FIT_REL/'live-run/prefit.py'; self.builder.parent.mkdir()
        shutil.copyfile(HERE/'prefit.py', self.builder)
        for name in ('owner/r2/supersedes.json', 'completion/registered-2/supersedes.json'):
            self.put(FIT_REL/name, {'superseded': {}})
        self.put('mod.py', None, text='VALUE = 1\n')
        self.probe = self.put('probe.py', None, text='import runpy, pathlib\n'
                              'runpy.run_path(str(pathlib.Path(__file__).with_name("mod.py")))\n')
        original = json.loads(built['refs'].read_text())
        for row in original['cells']:
            if row['role'] == 'blind': row['status'] = 'SEALED_BLIND'
            else: row.update(native=1, current=2, B=1, status='MEASURED')
        self.complete = self.pin(self.put(FIT_REL/'live-inputs/completed.json', original))
        self.measurement = self.pin(self.put(FIT_REL/'measurement-config.json', {'completedReferences': self.complete}))
        self.extra = self.pin(self.put(FIT_REL/'extra-input.json', {'input': 1}))
        suite = repo/FIT_REL/'suite'; suite.mkdir()
        (suite/'test_ok.py').write_text('import unittest\nclass T(unittest.TestCase):\n'
                                       f'    def test(self): self.assertTrue({not failing_suite})\n')
        self.suites = [('suite-synthetic', suite, [sys.executable, '-I', '-B', '-m', 'unittest', 'discover', '-q', '-p', 'test_*.py'])]
        self.standing = {}
        log = self.put(FIT_REL/'standing-log.txt', None, text='synthetic\n')
        for kind in P.STANDING:
            sources = [self.pin(log)] + ([self.complete] if kind == 'referenceCompletion' else [])
            self.standing[kind] = self.put(FIT_REL/f'standing/{kind}.json', {'schema': P.SCHEMA, 'kind': kind,
                'status': 'PASS', 'checks': [{'id': 'synthetic', 'status': 'PASS'}], 'sources': sources,
                'outputs': [self.pin(log)]})
        git(repo, 'add', '-A'); git(repo, 'commit', '-qm', 'base')
        self.base = git(repo, 'rev-parse', 'HEAD')
        self.put('notes.txt', None, text='fixed\n'); git(repo, 'add', '-A'); git(repo, 'commit', '-qm', 'fix')
        self.fix = git(repo, 'rev-parse', 'HEAD')
        self.put('notes.txt', None, text='final\n'); git(repo, 'add', '-A'); git(repo, 'commit', '-qm', 'final')
        self.final = git(repo, 'rev-parse', 'HEAD')
        sources = {'probe.py': D.sha(self.probe), 'mod.py': D.sha(repo/'mod.py')}
        closure = GUARD.discover(repo, self.probe, sources)
        self.doc = {'repo': str(repo), 'partTwo': D.pin(repo, built['two']), 'references': D.pin(repo, built['refs']),
                    'manifest': D.pin(repo, built['manifest']), 'reportedKeys': [], 'emptySupportKeys': [],
                    'ownerBudgetKeys': [], 'ownerContracts': None, 'closure': closure,
                    'probe': D.pin(repo, self.probe), 'liveInputs': [],
                    'instruments': {'measurement': {'entrypoint': D.pin(repo, repo/'mod.py'), 'config': self.measurement}},
                    'inputs': [self.complete, self.measurement, self.extra]}
        self.root = self.live/'execution-root.json'
        D.write_sealed(self.root, self.doc)
        self.review = repo/'review-records.json'

    def put(self, relative, value, text=None):
        path = self.repo/relative; path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text if text is not None else json.dumps(value, indent=2)+'\n'); return path

    def pin(self, path): return D.pin(self.repo, path)

    def record(self, final=None):
        rounds = [{'id': 'first', 'range': {'base': self.base, 'head': self.base}, 'reviewers': ['synthetic reviewer'],
                   'findings': [{'severity': 'P1', 'summary': 'a finding', 'disposition': 'fixed', 'fixedBy': [self.fix]},
                                {'severity': 'P3', 'summary': 'a nit', 'disposition': 'deferred', 'reason': 'tracker'}]},
                  final or {'id': 'final', 'range': {'base': self.base, 'head': self.final},
                            'reviewers': ['synthetic reviewer'], 'findings': []}]
        self.review.write_text(json.dumps({'schema': 'w50-live-review-records-1', 'rounds': rounds}, indent=2)+'\n')

    def layout(self, verify=True):
        return P.Layout(self.repo, fit=self.repo/FIT_REL, live=self.live, root=self.root,
                        evidence=CHAIN.slot(self.root, 'prefit'), proofs=self.repo/FIT_REL/'live-run/prefit-proofs',
                        review=self.review, standing=self.standing, suites=self.suites,
                        validate_body=lambda path, doc: doc, discover=GUARD.discover, builder=self.builder,
                        verify=(lambda root: A.verify_prefit(root, D.sealed(root))) if verify else None)


class Prefit(unittest.TestCase):
    def test_writes_both_proofs_and_evidence_that_live_verify_prefit_admits(self):
        world = Synthetic(self); world.record()
        layout = world.layout()
        built = P.build(layout)
        evidence = D.sealed(layout.evidence)
        self.assertEqual(built['verifyPrefit'], world.pin(layout.evidence))
        self.assertEqual(evidence['sources'], [world.pin(world.root), world.pin(str(world.root)+'.sha256')])
        self.assertEqual(evidence['executionClosure'], world.doc['closure'])
        self.assertEqual(evidence['references'], world.complete)
        self.assertEqual(list(evidence['evidence']), list(D.PROOFS))
        for kind in ('executionClosure', 'independentReview'):
            proof = json.loads((layout.proofs/f'{kind}.json').read_text())
            self.assertEqual({c['status'] for c in proof['checks']}, {'PASS'})
            self.assertIn(world.pin(world.root), proof['sources'])
        closure = json.loads((layout.proofs/'executionClosure.json').read_text())
        self.assertEqual([c['id'] for c in closure['checks']], ['root-seal', 'validate-body', 'fresh-discovery', 'suite-synthetic'])
        review = json.loads((layout.proofs/'independentReview.json').read_text())
        self.assertEqual([c['id'] for c in review['checks']],
                         ['record-shape', 'round-first', 'round-final', 'converged', 'root-bound-reviewed'])
        with self.assertRaisesRegex(AssertionError, 'written once'): P.build(world.layout())

    def test_a_todo_round_writes_nothing(self):
        world = Synthetic(self)
        world.record({'id': 'final', 'range': {'base': world.base, 'head': world.final}, 'reviewers': 'TODO', 'findings': 'TODO'})
        layout = world.layout()
        with self.assertRaisesRegex(AssertionError, 'TODO'): P.build(layout)
        self.assertFalse(layout.evidence.exists())
        self.assertFalse((layout.proofs/'independentReview.json').exists())

    def test_an_open_blocking_finding_or_an_unreviewed_change_refuses(self):
        world = Synthetic(self)
        world.record({'id': 'final', 'range': {'base': world.base, 'head': world.final}, 'reviewers': ['r'],
                      'findings': [{'severity': 'P1', 'summary': 'open', 'disposition': 'fixed', 'fixedBy': [world.final]}]})
        with self.assertRaisesRegex(AssertionError, 'independentReview not written'): P.build(world.layout(verify=False))
        world = Synthetic(self); world.record()
        world.put(FIT_REL/'extra-input.json', {'input': 2})  # a root-bound input moved after the last head
        with self.assertRaisesRegex(AssertionError, r"failed checks \['root-bound-reviewed'\]"):
            P.build(world.layout(verify=False))
        self.assertFalse(world.layout(verify=False).evidence.exists())

    def test_a_failing_suite_or_changed_closure_writes_no_proof(self):
        world = Synthetic(self, failing_suite=True); world.record()
        layout = world.layout(verify=False)
        with self.assertRaisesRegex(AssertionError, r"executionClosure not written.*suite-synthetic"): P.build(layout)
        self.assertFalse((layout.proofs/'executionClosure.json').exists())
        world = Synthetic(self); world.record()
        world.put('mod.py', None, text='VALUE = 2\n')
        with self.assertRaisesRegex(AssertionError, 'fresh-discovery'): P.build(world.layout(verify=False))

    def test_newest_proof_generation(self):
        with tempfile.TemporaryDirectory() as name:
            fit = Path(name)
            for folder in ('prefit-proofs', 'prefit-proofs-r2', 'prefit-proofs-r10'):
                (fit/folder).mkdir(); (fit/folder/'repeatBar.json').write_text('{}')
            (fit/'prefit-proofs'/'nativeArchive.json').write_text('{}')
            self.assertEqual(P.newest_proof(fit, 'repeatBar'), fit/'prefit-proofs-r10/repeatBar.json')
            self.assertEqual(P.newest_proof(fit, 'nativeArchive'), fit/'prefit-proofs/nativeArchive.json')


if __name__ == '__main__':
    unittest.main()
