"""DL5p bind-only recovery: recovery.py's authentication and run.py's recover-bind step.

The synthetic cases use livekit's world as root 3: its real dispatcher and roles, a committed
synthetic root 2 with sealed pre-fit evidence, a refusal preserving the world's own cohort as
the carried point, and a git history holding all of them. The initializer stand-in refuses
assemble and initialize outright, so a case that reached either would fail. The real-tree case
authenticates the committed declaration (dl5p-recovery.json) read-only: no bind, prefit or
numerical referee runs, and the eleven preserved files are checked against their literal hashes.
"""
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import unittest

HERE = Path(__file__).resolve().parent
FIT = HERE.parent
REPO = FIT.parents[3]


def module(path, name):
    spec = importlib.util.spec_from_file_location(name, path); value = importlib.util.module_from_spec(spec)
    sys.modules[name] = value; spec.loader.exec_module(value); return value


T = module(HERE/'kit.py', 'w50_live_run_recovery_test_kit')
R = module(HERE/'run.py', 'w50_live_run_recovery_operator')
V = R.V
C = R.C
ALLOWED = set(R.FIELDS) | {'schema'}
LIVE = 'packages/calibration/results/2026-10-08-w50-g1-fit/live-execution'
POINT = 'packages/calibration/results/2026-10-08-w50-g1-fit/fit/live-initializer'
DIGEST = '044bc4a5753c12f01c53f4c7886113ed67a8a2fa07106745002e9d31f8078002'
# The eleven files root 2's initializer wrote (attempt-1-refusal.json, 6d36b7fbd), by literal hash.
PRESERVED = {
    '0.25/active.dark.json': '39d9900ed181230ed2d8f53bc51d1ffc75f85c6cdd035f01b5ac5ccb025e274c',
    '0.25/active.light.json': '5d6f7eba023b48df6e80b72d3ebc8ea38f49e4ce672504502c2c8f6b765b7a31',
    '0.25/candidate.json': 'af1c181af52ebece971a161deeb2dc345bb5783affdc2943e67242ebb60deb89',
    '0.25/receded.dark.json': 'd20ffbeccf1d16f4e9f391ffae21b1ae940d074e54fd1dca46a052137f4ac395',
    '0.25/receded.light.json': 'abb005cc841506b71916acb51a2bfbaf5bb7b3117432b1eac35e0650ecce8eb7',
    '0.5/active.dark.json': '3cc4ed0d9d22d71d7c289e7041bb3034b897fca1f23ddc1f012ce43194bcdd68',
    '0.5/active.light.json': 'a217b7f7d2a72c6ec2282caebf5b897b2cc07fb55050bdb8f64371862a1be780',
    '0.5/candidate.json': '0f0873c64303a8b315fd9d23f45bc18967a4c709bef19ff4e43c55368c100fd3',
    '0.5/receded.dark.json': '0ab7b8aebdb0a66285c30f81731cf35401dbbaca7fbc0152e63a4cc8ac6a7b49',
    '0.5/receded.light.json': '83e2156ba37924041e65d8cb8308c94d311b4e8bf57b9dab287a628bc7d76071',
    'initializer.json': '323030c41f6657cbf5f63ed1a1bd2196ae841dd129c9d0ddfd9619173a75b710'}


def events(case, lines):
    out = [json.loads(line) for line in lines]
    for event in out:
        case.assertLessEqual(set(event), ALLOWED); case.assertEqual(event['schema'], 'w50-live-run-event-1')
    return out


class BindOnly:
    """fit/execution.py's bind_arguments over the world's cohort; assemble/initialize never run."""
    def __init__(self, world, numerical=None): self.world = world; self.calls = []; self.numerical = numerical
    def assemble(self, root): raise AssertionError('assemble called under the recovery')
    def initialize(self, root): raise AssertionError('initialize called under the recovery')
    def bind_arguments(self, root, cohort):
        self.calls.append((root, cohort)); w = self.world
        return {'cohort': self.numerical or w.pin(w.repo/'numerical-cohort.json'),
                'argumentManifest': w.pin(w.repo/'arguments.json'), 'preFitEvidence': dict(w.prefit)}


def git(repo, *args): subprocess.run(['git', '-C', str(repo), *args], check=True, capture_output=True)


def commit(repo, *paths):
    git(repo, 'add', '--', *map(str, paths)); git(repo, 'commit', '-q', '-m', 'synthetic')
    return subprocess.run(['git', '-C', str(repo), 'rev-parse', 'HEAD'], check=True, capture_output=True,
                          text=True).stdout.strip()


class Recovery:
    """The world re-rooted as root 3 over a committed synthetic root 2 (module docstring)."""

    def __init__(self, case, carried=None):
        self.case = case; w = self.world = T.K.EndToEnd(case); live = w.fit_dir/'live-execution'
        git(w.repo, 'init', '-q'); git(w.repo, 'config', 'user.email', 't@t'); git(w.repo, 'config', 'user.name', 't')
        self.charter = w.text('docs/charter.md', 'DL5o (parent). Earlier.\n\nDL5p (parent, synthetic). Bind only.\n'
                              'Carry the ONE point forward.\n\nDL5q (later).\n')
        self.before = commit(w.repo, self.charter)
        self.root2 = live/'execution-root-2.json'; self.root2.write_text('{"synthetic": "root 2"}\n')
        Path(str(self.root2)+'.sha256').write_text(f'{V.sha(self.root2)}  {self.root2.name}\n')
        evidence = live/'execution-root-2.pre-fit-evidence.json'; evidence.write_text('{"synthetic": "root 2 prefit"}\n')
        Path(str(evidence)+'.sha256').write_text(f'{V.sha(evidence)}  {evidence.name}\n')
        self.cohort = carried or T.candidate(w)['cohort']
        self.initializer = w.put(str(T.K.REL_FIT/'fit/live-initializer/candidates/x/initializer.json'),
                                 {'preFitEvidence': w.pin(evidence)})
        files = V.closure(w.repo, self.initializer, self.cohort)
        self.refusal = w.put(str(T.K.REL_FIT/'fit/live-initializer/attempt-1-refusal.json'),
                             {'schema': V.REFUSAL, 'status': V.REFUSED, 'root': w.pin(self.root2), 'files': files})
        self.commit = commit(w.repo, self.root2, Path(str(self.root2)+'.sha256'), evidence, Path(str(evidence)+'.sha256'),
                             *(w.repo/f['path'] for f in [*files, self.refusal]))
        self.declaration = w.fit_dir/'live-run/dl5p-recovery.json'
        self.declare()
        self.seal()

    def declare(self, **change):
        w = self.world; c = self.commit
        body = V.declare(w.repo, charter='docs/charter.md', ruling_commit=c, root=self.root2, evidence_commit=c,
                         refusal=w.repo/self.refusal['path'], refusal_commit=c, initializer=w.repo/self.initializer['path'],
                         cohort=[(i['position'], w.repo/i['path']) for i in self.cohort], statement='synthetic')
        body.update(change); self.declaration.parent.mkdir(parents=True, exist_ok=True)
        self.declaration.write_text(json.dumps(body, indent=2)+'\n'); return body

    def seal(self):
        """Root 3: the world's root, registering the declaration, superseding root 2 under DL5p."""
        w = self.world; decl = V.load(self.declaration); before = decl['predecessor']
        doc = {**w.doc, 'inputs': [*w.doc['inputs'], w.pin(self.declaration)],
               'supersedes': {'schema': V.LINK, 'root': before['root'], 'sealingCommit': self.commit,
                              'ruling': {'id': 'DL5p', 'text': w.pin(self.charter)},
                              'history': {'statement': 'synthetic', 'slots': [], 'commit': before['commit'],
                                          'entries': [before['preFitEvidence'], before['preFitEvidenceSeal']]}}}
        root = w.fit_dir/'live-execution/execution-root-3.json'
        root.write_text(json.dumps(doc, indent=2)+'\n')
        Path(str(root)+'.sha256').write_text(f'{V.sha(root)}  {root.name}\n')
        w.root = root; w.D._CORE.update(root=str(root.resolve()), sha=V.sha(root))
        return root

    def operator(self, lines, initializer=None, numerical=None):
        w = self.world; initializer = initializer or BindOnly(w)
        numerical = numerical or (lambda cohort: w.repo/w.numerical['path'])
        op = R.Operator(repo=w.repo, live=w.fit_dir/'live-execution', work=w.base/'outputs',
                        call=C.run_inprocess(w.D, initializer), numerical=numerical,
                        declarations=lambda: T.declarations(w), transport=lambda decl: T.transport(w, decl),
                        owner_records=lambda decl, candidate: w.intrinsic, out=lines.append, recovery=self.declaration)
        self.case.assertEqual(op.root, w.root.resolve())
        return op, initializer

    def hashes(self):
        w = self.world
        return {f['path']: V.sha(w.repo/f['path']) for f in [*V.closure(w.repo, self.initializer, self.cohort), self.refusal]}


class Synthetic(unittest.TestCase):
    def run_steps(self, op, lines, *steps):
        codes = []
        for argv in steps:
            lines.clear(); R.main(list(argv), op); codes.append([e['code'] for e in events(self, lines)])
        return codes

    def test_the_carried_point_is_bound_once_and_admitted_downstream_unchanged(self):
        world = Recovery(self); lines = []; before = world.hashes()
        op, initializer = world.operator(lines)
        self.assertEqual(R.main(['recover-bind'], op), 0)
        self.assertEqual([e['code'] for e in events(self, lines)], ['RECOVERY_RECORDED', 'CANDIDATE_WRITTEN'])
        self.assertEqual(initializer.calls, [(str(op.root), world.cohort)])
        recorded = V.load(op.record('recovered.json')); candidate = V.load(op.record('candidate.json'))
        self.assertEqual((recorded['cohort'], recorded['initializer']), (world.cohort, world.initializer))
        self.assertEqual(recorded['preFitEvidence'], world.world.prefit)
        self.assertEqual(candidate['recovery'], V.pin(world.world.repo, op.record('recovered.json')))
        self.assertEqual(candidate['initializer'], world.initializer)
        # Downstream steps admit the point only through that record; the fit runs to its verdict.
        self.assertEqual(self.run_steps(op, lines, ['fit-batch'], ['run', 'fit']),
                         [['BATCH_WRITTEN'], ['PHASE_CREATED', 'ATTEMPT', 'ANALYSIS', 'VERDICT']])
        # Nothing computes another point: initialize is refused and recover-bind finds the record.
        self.assertEqual(self.run_steps(op, lines, ['initialize'], ['recover-bind']), [['EXISTS'], ['EXISTS']])
        op.record('candidate.json').rename(op.record('candidate.held'))
        self.assertEqual(self.run_steps(op, lines, ['initialize']), [['REFUSED']])
        self.assertEqual(len(initializer.calls), 1)
        self.assertEqual(world.hashes(), before)

    def test_an_interrupted_referee_resumes_only_the_referee(self):
        world = Recovery(self); lines = []; attempts = []
        def numerical(cohort):
            attempts.append(cohort)
            if len(attempts) == 1: raise KeyboardInterrupt
            return world.world.repo/world.world.numerical['path']
        op, initializer = world.operator(lines, numerical=numerical)
        self.assertEqual(R.main(['recover-bind'], op), 1)
        self.assertEqual([e['code'] for e in events(self, lines)], ['RECOVERY_RECORDED', 'ERROR'])
        self.assertFalse(op.record('candidate.json').exists())
        self.assertEqual(self.run_steps(op, lines, ['recover-bind']), [['RECOVERY_RESUMED', 'CANDIDATE_WRITTEN']])
        self.assertEqual(len(initializer.calls), 1); self.assertEqual(attempts[0], attempts[1])

    def test_a_changed_or_replaced_cohort_is_refused_before_any_bind(self):
        cases = {}
        def changed_endpoint(world):
            endpoint = world.world.repo/V.closure(world.world.repo, world.initializer, world.cohort)[2]['path']
            endpoint.write_text(endpoint.read_text()+' ')
        def edited_declaration(world):
            world.declare(statement='edited after root 3 registered it')
        def reordered_cohort(world):
            world.declare(cohort=list(reversed(world.cohort))); world.seal()
        def unpreserved_candidate(world):
            # A different, committed candidate re-declared and re-registered: the refusal never preserved it.
            w = world.world; first = w.repo/world.cohort[0]['path']
            other = first.with_name('replacement.json'); other.write_text(first.read_text().replace('}', ' }', 1))
            world.commit = commit(w.repo, other)
            world.cohort = [{'position': .25, **w.pin(other)}, world.cohort[1]]
            world.declare(); world.seal()
        def uncommitted_point(world):
            # Root 2's facts must be committed bytes: a declaration naming a commit before them refuses.
            world.declare(refusal={'record': world.refusal, 'commit': world.before}); world.seal()
        def rewritten_after_commit(world):
            # A preserved file rewritten and re-pinned everywhere still differs from its committed blob.
            w = world.world; init = w.repo/world.initializer['path']
            init.write_text(init.read_text().replace('}', ' }', 1)); world.initializer = w.pin(init)
            files = V.closure(w.repo, world.initializer, world.cohort)
            world.refusal = w.put(world.refusal['path'], {**V.load(w.repo/world.refusal['path']), 'files': files})
            world.declare(); world.seal()
        cases.update(changed_endpoint=changed_endpoint, edited_declaration=edited_declaration,
                     reordered_cohort=reordered_cohort, unpreserved_candidate=unpreserved_candidate,
                     uncommitted_point=uncommitted_point, rewritten_after_commit=rewritten_after_commit)
        for name, change in cases.items():
            with self.subTest(name):
                world = Recovery(self); lines = []; change(world)
                op, initializer = world.operator(lines)
                self.assertEqual(R.main(['recover-bind'], op), 1)
                self.assertEqual([e['code'] for e in events(self, lines)], ['REFUSED'])
                self.assertEqual(initializer.calls, [])
                self.assertFalse(op.record('recovered.json').exists())

    def test_a_bind_over_another_cohort_or_pre_fit_evidence_is_never_recorded(self):
        for name in ('cohort', 'prefit'):
            with self.subTest(name):
                world = Recovery(self); lines = []; w = world.world
                if name == 'cohort':
                    other = w.put('synthetic/other-numerical-cohort.json', {'candidates': list(reversed(world.cohort)),
                        'structuredArguments': w.pin(w.repo/'arguments.json')})
                    initializer = BindOnly(w, numerical=other)
                else:
                    initializer = BindOnly(w)
                    original = initializer.bind_arguments
                    initializer.bind_arguments = lambda root, cohort: {**original(root, cohort),
                        'preFitEvidence': V.load(world.declaration)['predecessor']['preFitEvidence']}
                op, _ = world.operator(lines, initializer=initializer)
                self.assertEqual(R.main(['recover-bind'], op), 1)
                self.assertEqual([e['code'] for e in events(self, lines)], ['REFUSED'])
                self.assertFalse(op.record('recovered.json').exists())

    def test_a_replaced_recovery_record_refuses_the_resume(self):
        world = Recovery(self); lines = []
        op, initializer = world.operator(lines, numerical=lambda cohort: (_ for _ in ()).throw(KeyboardInterrupt))
        self.assertEqual(R.main(['recover-bind'], op), 1)
        record = op.record('recovered.json'); value = V.load(record)
        record.write_text(json.dumps({**value, 'cohort': list(reversed(value['cohort']))}, indent=2)+'\n')
        op.numerical = lambda cohort: world.world.repo/world.world.numerical['path']
        self.assertEqual(self.run_steps(op, lines, ['recover-bind']), [['REFUSED']])
        self.assertFalse(op.record('candidate.json').exists()); self.assertEqual(len(initializer.calls), 1)

    def test_the_candidate_record_is_admitted_only_with_its_authenticated_recovery(self):
        world = Recovery(self); lines = []
        op, _ = world.operator(lines)
        self.assertEqual(R.main(['recover-bind'], op), 0)
        path = op.record('candidate.json'); good = V.load(path)
        stray = world.world.put('synthetic/stray.json', V.load(op.record('recovered.json')))
        for name, value in {'no recovery': {k: v for k, v in good.items() if k != 'recovery'},
                            'another recovery record': {**good, 'recovery': stray},
                            'changed recovery record': {**good, 'recovery': {**good['recovery'], 'sha256': '0'*64}},
                            'another numerical cohort': {**good, 'numericalCohort': good['argumentManifest']}}.items():
            with self.subTest(name):
                path.write_text(json.dumps(value, indent=2)+'\n')
                self.assertEqual(self.run_steps(op, lines, ['fit-batch']), [['REFUSED']])
                self.assertFalse(op.record('fit-batch.json').exists())
        path.write_text(json.dumps(good, indent=2)+'\n')
        with self.subTest('absent declaration'):
            held = world.declaration.with_suffix('.held'); world.declaration.rename(held)
            self.assertEqual(self.run_steps(op, lines, ['fit-batch']), [['REFUSED']])
            held.rename(world.declaration)
        self.assertEqual(self.run_steps(op, lines, ['fit-batch']), [['BATCH_WRITTEN']])

    def test_the_root_must_register_the_declaration_and_succeed_root_2_under_dl5p(self):
        for name in ('unregistered', 'another ruling', 'another history'):
            with self.subTest(name):
                world = Recovery(self); lines = []; w = world.world; doc = V.load(w.root)
                if name == 'unregistered': doc['inputs'] = [i for i in doc['inputs'] if i != w.pin(world.declaration)]
                if name == 'another ruling': doc['supersedes']['ruling']['id'] = 'DL5o'
                if name == 'another history': doc['supersedes']['history']['entries'] = doc['supersedes']['history']['entries'][:1]
                w.root.write_text(json.dumps(doc, indent=2)+'\n')
                Path(str(w.root)+'.sha256').write_text(f'{V.sha(w.root)}  {w.root.name}\n')
                w.D._CORE.update(sha=V.sha(w.root))
                op, initializer = world.operator(lines)
                self.assertEqual(R.main(['recover-bind'], op), 1)
                self.assertEqual([e['code'] for e in events(self, lines)], ['REFUSED'])
                self.assertEqual(initializer.calls, [])


class RealTree(unittest.TestCase):
    """The committed declaration over the real tree, read-only (no bind, prefit or referee)."""

    def test_the_declaration_authenticates_the_preserved_point_byte_for_byte(self):
        decl = V.evidence(REPO, R.DECLARATION)
        files = V.closure(REPO, decl['initializer'], decl['cohort'])
        self.assertEqual({f['path']: f['sha256'] for f in files},
                         {f'{POINT}/candidates/{DIGEST}/{k}': v for k, v in PRESERVED.items()})
        for f in files: self.assertEqual(V.sha(REPO/f['path']), f['sha256'])
        self.assertEqual(decl['predecessor']['root'], {'path': f'{LIVE}/execution-root-2.json',
            'sha256': '2e6f4c990f4cd38810994549b95804333ea883a0ea886320648d9f88d0853dd5'})
        self.assertEqual(decl['predecessor']['preFitEvidence'], {'path': f'{LIVE}/execution-root-2.pre-fit-evidence.json',
            'sha256': 'c788ca9bd747ffb9c6383c5f32f9707e62e11e1410284c49dad728f116e86fb3'})
        self.assertEqual(V.provenance(REPO, decl['initializer'], decl['cohort']), [decl['predecessor']['preFitEvidence']])
        self.assertEqual(decl['refusal']['record']['sha256'], 'ad3f3cf08889cb3640eae0471ed844761054b8b8bf8a5ebf7cff198d639dab8f')

    def test_root_2_is_not_a_recovery_root(self):
        root2 = REPO/LIVE/'execution-root-2.json'
        with self.assertRaises(V.Refused): V.admit(REPO, root2, V.load(root2), R.DECLARATION)


if __name__ == '__main__':
    unittest.main()
