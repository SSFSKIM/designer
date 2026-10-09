"""batches.py: memberships from the real declarations; batches LIVE admits on a synthetic root.

The real-declaration cases read the sealed root's references, manifest, part 2 and scene
documents and the committed current batches only: no blind archive, checkpoint or statistic.
"""
import copy
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
FIT = HERE.parent
REPO = FIT.parents[3]
import importlib.util, sys
spec = importlib.util.spec_from_file_location('w50_live_run_test_kit', HERE/'kit.py')
T = importlib.util.module_from_spec(spec); sys.modules['w50_live_run_test_kit'] = T; spec.loader.exec_module(T)
B = T.B
ROOT = FIT/'live-execution/execution-root.json'
G0 = 'packages/calibration/results/2026-10-08-w50-g0-declaration'
FIVE = ['backdropToneAnchorX', 'backdropToneBlackStrength', 'optics.clear.rimLevelGain',
        'outerShadow.liftAmplitude', 'outerShadow.thinOcclusionDark']


def dummy_candidate(decl):
    """Pins that resolve (the root's gate0 baselines) standing in for a fitted cohort."""
    positions = decl.baselines()
    return {'cohort': [{'position': p, **positions[p]} for p in (.25, .5)], 'numericalReferee': positions[.25]}


class RealDeclarations(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.decl = B.Declarations.sealed(ROOT)
        cls.transport = B.transport_fields(cls.decl)

    def test_gate_and_exposure_are_the_dl5d_tables(self):
        deps = self.decl.dependencies
        self.assertEqual(self.decl.cells('gate'), sorted({tuple(k[:3]) for k in deps['gateKeys']}))
        self.assertEqual(self.decl.cells('exposure'), sorted({tuple(k[:3]) for k in deps['exposureKeys']}))
        self.assertFalse(set(self.decl.cells('gate')) & set(self.decl.cells('exposure')))

    def test_fit_is_the_calibration_and_validation_gate_cells_of_both_sources(self):
        fit, gate = set(self.decl.cells('fit')), set(self.decl.cells('gate'))
        self.assertTrue(fit < gate)
        self.assertEqual(fit, {c for c in gate if self.decl.split(c[2]) in B.FIT_SETS})
        self.assertEqual({self.decl.scene_source(c[2]) for c in fit}, {'w50', 'canonical'})
        # Every exposed new-bed cell is calibration or validation, so the fit draws all of them.
        self.assertEqual({c for c in fit if self.decl.scene_source(c[2]) == 'w50'},
                         {c for c in gate if self.decl.scene_source(c[2]) == 'w50'})
        rows = [r for k, r in self.decl.rows.items() if k[:3] in fit]
        self.assertFalse({r['role'] for r in rows} & B.WITHHELD)
        # The blind split and its deferred physical closure are nowhere in fit or gate.
        withheld = {(g['profile'], g['scene']) for g in self.decl.dependencies['groups']}
        self.assertFalse({(c[0], c[2]) for c in gate} & withheld)

    def test_real_fit_and_gate_runs_carry_the_current_chain_fields(self):
        self.assertEqual(len(self.transport['w50']['fixtures']), 8)  # four profiles, two poses
        for phase in ('fit', 'gate'):
            doc = B.build(self.decl, phase, dummy_candidate(self.decl), self.transport,
                          None if phase == 'fit' else {'path': 'x', 'sha256': '0'*64})
            self.assertEqual(B.members(doc), sorted(self.decl.cells(phase)))
            self.assertEqual(len({r['id'] for r in doc['runs']}), len(doc['runs']))
            for run in doc['runs']:
                splits = {self.decl.split(s) for s in run['scenes']}
                self.assertEqual(set(run['sets']), splits)
                self.assertNotIn('holdout', run['sets'])
                if phase == 'fit': self.assertLessEqual(set(run['sets']), set(B.FIT_SETS))
                self.assertNotIn('baselineCandidate', run)
                if run['sceneSource'] == 'w50':
                    poses = {self.decl.pose(s) for s in run['scenes']}
                    self.assertEqual(len(poses), 1)
                    self.assertEqual(run['fixtures'], self.transport['w50']['fixtures'][run['profile']+'|'+poses.pop()])
                else:
                    self.assertEqual(run['nativeManifest'], self.transport['canonical']['nativeManifest'])

    def test_real_exposure_runs_hold_one_pose_and_a_same_position_baseline(self):
        keys = {c[0]+'|'+self.decl.pose(c[2]) for c in self.decl.cells('exposure') if self.decl.scene_source(c[2]) == 'w50'}
        plans = {k: {'path': '/planned/'+k, 'manifestSha256': '0'*64, 'backgrounds': {}} for k in keys}
        config = self.decl.root['instruments']['native']['config']
        doc = B.build(self.decl, 'exposure', dummy_candidate(self.decl), self.transport,
                      {'path': 'x', 'sha256': '0'*64}, (config, plans))
        self.assertEqual(B.members(doc), sorted(self.decl.cells('exposure')))
        baselines = self.decl.baselines()
        for run in doc['runs']:
            self.assertEqual(run['baselineCandidate'], baselines[B.position(run['profile'])])
            if run['sceneSource'] == 'w50':
                self.assertEqual(run['nativeExposureConfig'], config)
                self.assertEqual(run['fixtures'], plans[run['profile']+'|'+self.decl.pose(run['scenes'][0])])
                self.assertEqual({self.decl.pose(s) for s in run['scenes']}, {self.decl.pose(run['scenes'][0])})

    def test_a_changed_scene_split_or_a_duplicate_scene_refuses(self):
        scenes = copy.deepcopy(self.decl.scenes)
        scene = self.decl.cells('fit')[0][2]
        source = self.decl.scene_source(scene)
        scenes[source]['split']['holdout'].append(scene)
        with self.assertRaisesRegex(ValueError, 'exactly one declared split'):
            B.Declarations(ROOT, self.decl.root, scenes).cells('fit')


def build_candidates(repo, charts):
    """The real fit/candidate.ts over the root's gate0 baselines, into repo (identity if charts is None)."""
    script = repo/'build.mts'
    script.write_text(f"""import {{ buildCandidate }} from {json.dumps(str(FIT/'fit/candidate.ts'))};
const out: any[] = [];
for (const [position, folder] of [[.25, 'glass025'], [.5, 'glass05']] as const) {{
  const path = {json.dumps(str(FIT/'inputs/current-material'))} + '/' + folder + '/candidate.json';
  const sha = (await import('node:crypto')).createHash('sha256').update((await import('node:fs')).readFileSync(path)).digest('hex');
  out.push({{ position, ...buildCandidate({{ path, sha256: sha }}, {json.dumps(charts)},
    {json.dumps(str(repo/'candidates'))} + '/' + folder, ['live-run test point']) }});
}}
console.log(JSON.stringify(out));
""")
    found = subprocess.run(['pnpm', 'exec', 'tsx', str(script)], cwd=REPO/'packages/calibration',
                           capture_output=True, text=True)
    if found.returncode: raise AssertionError(found.stderr[-2000:])
    return [{'position': c['position'], 'path': str(Path(c['path']).relative_to(repo)), 'sha256': c['sha256']}
            for c in json.loads(found.stdout.strip().splitlines()[-1])]


class RealOwnerRecords(unittest.TestCase):
    """owner_intrinsic_records on the real G0 pair and real candidate documents (DL5o)."""

    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory(); cls.repo = Path(cls.temp.name).resolve()
        for relative in [f'{G0}/references.json', *(f'{G0}/references/documents/{d}.json' for d in (
                'b2d074d2df2444a614304d11e906b5f91d8968bce161efbd8f34fc8da5be9186',
                '940384c06f73df1cbe2554e395d1db2a09c23a7bb6a57cdb2094807718483735',
                '0eac5b294cc235e2ba03841472211e63f85d36258a20951bef6f974931cda445',
                '5cec8c9612012a8988e37ee51a80bcc8de35b306f6f8464d596dfdbbdbcef0d2'))]:
            (cls.repo/relative).parent.mkdir(parents=True, exist_ok=True); shutil.copyfile(REPO/relative, cls.repo/relative)
        cls.references = B.D.pin(cls.repo, cls.repo/G0/'references.json')

    @classmethod
    def tearDownClass(cls): cls.temp.cleanup()

    def records(self, name, charts):
        repo = self.repo/name; repo.mkdir()
        for path in (self.repo/G0).rglob('*.json'):
            target = repo/path.relative_to(self.repo); target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(path, target)
        cohort = build_candidates(repo, charts)
        pin = B.owner_intrinsic_records(repo, self.references, cohort, repo/'records')
        doc = B.D.load(B.D.checked(repo, pin))
        self.assertEqual(doc['candidateDeclarations'], [B.plain(c) for c in cohort])
        return repo, doc, {k: {n: B.D.load(B.D.checked(repo, p)) for n, p in v.items() if n in ('activeEntries', 'methods')}
                           for k, v in doc['recededRecords'].items()}

    def test_identity_candidate_records(self):
        repo, doc, read = self.records('identity', None)
        self.assertEqual(sorted(doc['recededRecords']), ['0.25', '0.5'])
        self.assertEqual(doc['recededRecords']['0.25']['beforeActive']['sha256'][:12], 'b2d074d2df24')
        self.assertEqual(doc['recededRecords']['0.5']['beforeReceded']['sha256'][:12], '5cec8c961201')
        quarter, half = read['0.25'], read['0.5']
        self.assertEqual(sorted(quarter['activeEntries']['retainedMeasuredEntries']), sorted([
            'backdropToneResponseThick', 'optics.regular.tintAlpha', 'sizeScatterScaleGain', 'sizeScatterSpanMax',
            'sizeScatterSpanMax2x', 'tintAlphaFar1x', 'tintAlphaFar2x']))
        self.assertEqual(half['activeEntries']['retainedMeasuredEntries'], {})  # family-keyed: the port's
        for value in (quarter, half): self.assertEqual(value['activeEntries']['fittedEntries'], {})
        self.assertEqual(len(quarter['methods']['methods']), 16)  # W49a's holds, verbatim readings
        self.assertTrue(all(set(m) == {'held'} for m in quarter['methods']['methods'].values()))
        self.assertEqual(sorted(half['methods']['methods']), FIVE)

    def test_chart_candidate_records(self):
        charts = {'active': [[.1, .12, .18, .24]]*3, 'receded': [[.05, .08, .14, .2]]*3}
        repo, doc, read = self.records('chart', charts)
        for position, value in read.items():
            fitted = value['activeEntries']['fittedEntries']
            self.assertEqual(sorted(fitted), sorted(B.CHART))
            self.assertTrue(all(e['status'] == 'measured' and e['method'] for e in fitted.values()))
            methods = value['methods']['methods']
            for leaf in B.CHART: self.assertIsInstance(methods[leaf], list)
            self.assertEqual(sorted(k for k, m in methods.items() if isinstance(m, dict)),
                             FIVE if position == '0.5' else sorted(k for k in methods if k not in B.CHART))
        # Candidate endpoint shas bind each envelope (owner/intrinsic.ts checkRecordApplicability).
        for position, value in doc['recededRecords'].items():
            cohort = {B.D.load(B.D.checked(repo, c))['glassTintAmount']: c for c in doc['candidateDeclarations']}
            endpoints = B.D.load(B.D.checked(repo, cohort[float(position)]))['endpoints']
            self.assertEqual(read[position]['activeEntries']['endpointSha256'], endpoints['active.dark']['sha256'])
            self.assertEqual(read[position]['methods']['endpointSha256'], endpoints['receded.dark']['sha256'])

    def test_a_leaf_keyed_record_off_its_patch_leaf_is_blocked(self):
        before = B.D.load(REPO/G0/'references/documents/b2d074d2df2444a614304d11e906b5f91d8968bce161efbd8f34fc8da5be9186.json')
        before['entries']['optics.regular.tintAlpha']['value'] = 0.123456
        with self.assertRaises(B.Blocked):
            B.owner_envelopes(before, {'patch': {}, 'entries': {}}, {'patch': {}, 'entries': {}}, 'a'*64, 'b'*64)
        family = B.D.load(REPO/G0/'references/documents/0eac5b294cc235e2ba03841472211e63f85d36258a20951bef6f974931cda445.json')
        self.assertEqual(B.owner_envelopes(family, {'patch': {}, 'entries': {}}, {'patch': {}, 'entries': {}},
                                           'a'*64, 'b'*64)[0]['retainedMeasuredEntries'], {})


class SyntheticBatches(unittest.TestCase):
    """Every built batch passes current3 validate_batch and LIVE _live_batch on livekit's root."""

    def test_built_batches_are_admitted_and_equal_the_declared_phases(self):
        world = T.K.EndToEnd(self)
        decl = T.declarations(world)
        transport = T.transport(world, decl)
        plans = B.exposure_plans(decl, world.outputs['exposure'])
        built = {}
        for phase in ('fit', 'gate', 'exposure'):
            doc = B.build(decl, phase, T.candidate(world), transport, None if phase == 'fit' else world.intrinsic,
                          plans if phase == 'exposure' else None)
            path = world.repo/f'live-run-batches/{phase}.json'; B.write_once(path, doc)
            batch, expected = world.C.D.validate_batch(world.doc, path, phase)
            world.D._live_batch(world.doc, batch, built.get('gate'))
            built[phase] = batch
            self.assertEqual(sorted({tuple(k[:3]) for k in map(lambda c: [c[k] for k in B.KEY], expected)}),
                             decl.cells(phase))
        for phase in ('gate', 'exposure'):
            self.assertEqual(B.members(built[phase]), B.members(json.loads(world.batches[phase].read_text())))
        self.assertLessEqual(set(B.members(built['fit'])), set(B.members(built['gate'])))
        self.assertTrue(any(r['sceneSource'] == 'canonical' for r in built['fit']['runs']))
        # A withheld set in the fit, or exposure intrinsic records other than the gate's, refuse.
        bad = copy.deepcopy(built['fit']); bad['runs'][0]['sets'].append('holdout')
        path = world.repo/'live-run-batches/bad-fit.json'; B.write_once(path, bad)
        with self.assertRaises(ValueError): world.C.D.validate_batch(world.doc, path, 'fit')
        other = copy.deepcopy(built['exposure']); other['ownerIntrinsicRecords'] = world.references
        with self.assertRaisesRegex(ValueError, 'intrinsic'): world.D._live_batch(world.doc, other, built['gate'])


if __name__ == '__main__':
    unittest.main()
