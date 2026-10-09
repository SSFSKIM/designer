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
from unittest import mock

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
    def __init__(self, case, *, failing_suite=False, failing_node=False):
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
        (suite/'synthetic.test.mjs').write_text("import {test} from 'node:test';\nimport assert from 'node:assert/strict';\n"
                                                f"test('synthetic', () => assert.equal({str(not failing_node).lower()}, true));\n")
        self.suites = [('suite-synthetic', suite, [sys.executable, '-I', '-B', '-m', 'unittest', 'discover', '-q', '-p', 'test_*.py']),
                       ('node-synthetic', suite, [shutil.which('node'), '--test', '--test-reporter=tap', 'synthetic.test.mjs'])]
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

    def layout(self, verify=True, calls=None):
        def verified(root):
            if calls is not None: calls.append(root)
            return A.verify_prefit(root, D.sealed(root))
        return P.Layout(self.repo, fit=self.repo/FIT_REL, live=self.live, root=self.root,
                        evidence=CHAIN.slot(self.root, 'prefit'), proofs=self.repo/FIT_REL/'live-run/prefit-proofs',
                        review=self.review, standing=self.standing, suites=self.suites,
                        validate_body=lambda path, doc: doc, discover=GUARD.discover, builder=self.builder,
                        verify=verified if verify else None, precheck=P.in_memory_verifier(LIVE))


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
        self.assertEqual([c['id'] for c in closure['checks']],
                         ['root-seal', 'validate-body', 'fresh-discovery', 'suite-synthetic', 'node-synthetic'])
        self.assertEqual([c['tests'] for c in closure['checks'][3:]], [1, 1])
        self.assertIn(world.pin(world.repo/FIT_REL/'suite/synthetic.test.mjs'), closure['sources'])
        self.assertFalse(any(p.name == P.STAGED_PROOF for p in (layout.proofs/'logs').rglob('*')))
        review = json.loads((layout.proofs/'independentReview.json').read_text())
        self.assertEqual([c['id'] for c in review['checks']],
                         ['record-shape', 'round-first', 'round-final', 'converged', 'root-bound-reviewed'])
        with self.assertRaisesRegex(AssertionError, 'written once'): P.build(world.layout())

    def test_a_todo_round_writes_nothing_and_runs_no_suite(self):
        world = Synthetic(self)
        world.record({'id': 'final', 'range': {'base': world.base, 'head': world.final}, 'reviewers': 'TODO', 'findings': 'TODO'})
        layout = world.layout()
        with self.assertRaisesRegex(AssertionError, 'TODO'): P.build(layout)
        self.assertFalse(layout.evidence.exists())
        self.assertFalse((layout.proofs/'independentReview.json').exists())
        self.assertFalse((layout.proofs/'executionClosure.json').exists())
        self.assertFalse((layout.proofs/'logs').exists())

    def test_only_a_literal_todo_marker_refuses(self):
        self.assertTrue(P._todo({'head': 'TODO: the last reviewed commit'}))
        self.assertTrue(P._todo({'TODO': 'x'}))
        self.assertTrue(P._todo([{'reviewers': ' TODO'}]))
        self.assertFalse(P._todo({'summary': 'Check the TODO refusal before the suites run.'}))
        self.assertFalse(P._todo({'summary': 'TODOS are tracked elsewhere'}))
        world = Synthetic(self)
        world.record({'id': 'final', 'range': {'base': world.base, 'head': world.final}, 'reviewers': ['r'],
                      'findings': [{'severity': 'P3', 'summary': 'The TODO check runs too late.', 'disposition': 'deferred',
                                    'reason': 'tracker'}]})
        P.build(world.layout(verify=False))
        self.assertTrue((world.layout(verify=False).proofs/'independentReview.json').is_file())

    def test_a_failing_in_memory_check_writes_no_evidence(self):
        # A recorded recovery that supersedes a file a standing proof pins: LIVE's prefit_lineage
        # refuses that evidence, so it must refuse before the evidence is sealed, not after.
        world = Synthetic(self); world.record()
        world.put(FIT_REL/'owner/r2/supersedes.json', {'superseded': {'log': world.pin(world.repo/FIT_REL/'standing-log.txt')}})
        git(world.repo, 'add', '-A'); git(world.repo, 'commit', '-qm', 'supersede')
        world.record({'id': 'final', 'range': {'base': world.base, 'head': git(world.repo, 'rev-parse', 'HEAD')},
                      'reviewers': ['r'], 'findings': []})
        calls = []; layout = world.layout(calls=calls)
        with self.assertRaisesRegex(ValueError, 'superseded'): P.build(layout)
        self.assertFalse(layout.evidence.exists())
        self.assertFalse(Path(str(layout.evidence)+'.sha256').exists())
        self.assertEqual(calls, [])
        self.assertEqual(CHAIN.slot_entries(world.root), [])

    def test_the_precheck_mirrors_live_verify_prefit_or_refuses(self):
        P.in_memory_verifier(LIVE)
        text = (LIVE/'authority.py').read_text()
        self.assertIn("    if evidence.get('executionClosure') != doc['closure']:", text)
        twice = text.replace("    if evidence.get('executionClosure') != doc['closure']:",
                             "    D.sealed(C.slot(path, 'prefit'))\n    if evidence.get('executionClosure') != doc['closure']:")
        with self.assertRaisesRegex(AssertionError, 'reads its slot twice'): P.in_memory_verifier(LIVE, twice)
        extra = text.replace('    pinned=_verify_prefit(path,doc)\n', '    pinned=_verify_prefit(path,doc)\n    roots=[]\n')
        self.assertNotEqual(extra, text)
        with self.assertRaisesRegex(AssertionError, 'verify_prefit changed shape'): P.in_memory_verifier(LIVE, extra)

    def test_a_crash_after_the_log_rename_is_adopted_on_the_next_run(self):
        world = Synthetic(self); world.record()
        layout = world.layout()
        with mock.patch.object(P, 'install', side_effect=KeyboardInterrupt):
            with self.assertRaises(KeyboardInterrupt): P.build(layout)
        self.assertTrue((layout.proofs/'logs/executionClosure'/P.STAGED_PROOF).is_file())
        self.assertFalse((layout.proofs/'executionClosure.json').exists())
        built = P.build(world.layout())
        self.assertEqual(built['verifyPrefit'], world.pin(layout.evidence))
        self.assertFalse((layout.proofs/'logs/executionClosure'/P.STAGED_PROOF).exists())
        # A staged proof whose logs no longer verify is never adopted.
        world = Synthetic(self); world.record(); layout = world.layout()
        with mock.patch.object(P, 'install', side_effect=KeyboardInterrupt):
            with self.assertRaises(KeyboardInterrupt): P.build(layout)
        (layout.proofs/'logs/executionClosure/suite-synthetic.log').write_text('changed\n')
        with self.assertRaises(Exception): P.build(world.layout())
        self.assertFalse((layout.proofs/'executionClosure.json').exists())
        self.assertFalse(layout.evidence.exists())

    def test_rounds_are_contiguous_or_separated_only_by_root_bound_free_gaps(self):
        def final(world, base):
            world.record({'id': 'final', 'range': {'base': base, 'head': world.final}, 'reviewers': ['r'], 'findings': []})
        # A gap that moved no root-bound file (notes.txt) is admitted and counted.
        world = Synthetic(self); final(world, world.fix)
        P.build(world.layout(verify=False))
        review = json.loads((world.layout().proofs/'independentReview.json').read_text())
        log = next(c for c in review['checks'] if c['id'] == 'converged')['log']
        self.assertEqual(json.loads((world.repo/log['path']).read_text())['gapsWithoutRootBoundChange'], 1)
        # An overlap (the round starts before the previous head) refuses.
        world = Synthetic(self)
        world.record(); record = json.loads(world.review.read_text())
        record['rounds'][0]['range']['head'] = world.fix
        world.review.write_text(json.dumps(record))
        with self.assertRaisesRegex(AssertionError, r"failed checks \['converged'\]"): P.build(world.layout(verify=False))
        # A gap that moved a root-bound file refuses, even when a later commit moved it back.
        world = Synthetic(self)
        world.put(FIT_REL/'extra-input.json', {'input': 2}); git(world.repo, 'commit', '-qam', 'moved')
        moved = git(world.repo, 'rev-parse', 'HEAD')
        world.put(FIT_REL/'extra-input.json', {'input': 1}); git(world.repo, 'commit', '-qam', 'restored')
        world.record({'id': 'final', 'range': {'base': moved, 'head': git(world.repo, 'rev-parse', 'HEAD')},
                      'reviewers': ['r'], 'findings': []})
        with self.assertRaisesRegex(AssertionError, r"failed checks \['converged'\]"): P.build(world.layout(verify=False))

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
        world = Synthetic(self, failing_node=True); world.record()
        layout = world.layout(verify=False)
        with self.assertRaisesRegex(AssertionError, r"executionClosure not written; failed checks \['node-synthetic'\]"):
            P.build(layout)
        self.assertFalse((layout.proofs/'executionClosure.json').exists())
        world = Synthetic(self); world.record()
        world.put('mod.py', None, text='VALUE = 2\n')
        with self.assertRaisesRegex(AssertionError, 'fresh-discovery'): P.build(world.layout(verify=False))

    def test_the_default_suites_cover_owner_and_every_node_directory(self):
        suites = {cid: (cwd, argv) for cid, cwd, argv in P.default_suites(P.REPO, FIT, P.PY, node='node')}
        self.assertIn('suite-owner', suites)
        calibration = P.REPO/P.CALIBRATION
        for name in P.NODE:
            cwd, argv = suites[f'node-{name}']
            self.assertEqual(cwd, calibration)
            self.assertEqual(argv[:5], ['node', '--import', 'tsx', '--test', '--test-reporter=tap'])
            expected = sorted([*(FIT/name).glob('*.test.ts'), *(FIT/name).glob('*.test.mjs')])
            self.assertEqual([calibration/a for a in argv[5:]], expected)
            self.assertEqual(P.suite_sources(cwd, argv), expected)

    def test_newest_proof_generation(self):
        with tempfile.TemporaryDirectory() as name:
            fit = Path(name)
            for folder in ('prefit-proofs', 'prefit-proofs-r2', 'prefit-proofs-r10'):
                (fit/folder).mkdir(); (fit/folder/'repeatBar.json').write_text('{}')
            (fit/'prefit-proofs'/'nativeArchive.json').write_text('{}')
            self.assertEqual(P.newest_proof(fit, 'repeatBar'), fit/'prefit-proofs-r10/repeatBar.json')
            self.assertEqual(P.newest_proof(fit, 'nativeArchive'), fit/'prefit-proofs/nativeArchive.json')


class Proofs(unittest.TestCase):
    def test_each_root_after_root_2_writes_its_own_proofs(self):
        fit = Path('/f'); proofs = fit/'live-run/prefit-proofs'
        self.assertEqual(P.default_proofs(fit, fit/'live-execution/execution-root-2.json'), proofs)
        self.assertEqual(P.default_proofs(fit, fit/'live-execution/execution-root-3.json'), proofs/'execution-root-3')
        self.assertEqual(P.default_proofs(fit, fit/'live-execution/execution-root-12.json'), proofs/'execution-root-12')
        # Root 2's sealed evidence pins its proofs where they are.
        evidence = json.loads((FIT/'live-execution/execution-root-2.pre-fit-evidence.json').read_text())
        for kind in ('executionClosure', 'independentReview'):
            self.assertEqual(evidence['evidence'][kind]['path'],
                             'packages/calibration/results/2026-10-08-w50-g1-fit/live-run/prefit-proofs/'+kind+'.json')


if __name__ == '__main__':
    unittest.main()
