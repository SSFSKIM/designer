"""Independent fixture bytes, real statistic supports and the production target preflight.

Breaks caught: reused real identities, copying native into current, missing own repeats,
empty far24/eroded supports, fabricated statistics and incomplete target membership.
No stage, source admission or judge is mocked here; lifecycle proof belongs to run.py.
"""
import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import tempfile
import unittest

HERE = Path(__file__).resolve().parent


def load_module(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def read(path):
    return json.loads(path.read_bytes())


class SyntheticFixture(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.G = load_module(HERE/'generate.py', 'w51_synthetic_generator')
        cls.tmp = tempfile.TemporaryDirectory(prefix='.test-fixture-', dir=HERE)
        cls.output = Path(cls.tmp.name)
        cls.G.build(cls.output)
        cls.inventory = read(cls.output/'inventory.json')
        cls.population = read(cls.output/'population.json')
        cls.scenes = read(cls.output/'scenes.json')
        cls.records = read(cls.output/'canonical-reference-evidence.json')['partitions']['gate']

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_new_scene_geometry_and_exact_population_never_relabels_apple_evidence(self):
        real = read(HERE.parents[4]/'apps/reference-apple/scenes.json')
        real_scenes = {s['id'] for s in real['scenes']}
        self.assertTrue(real_scenes.isdisjoint(s['id'] for s in self.scenes['scenes']))
        self.assertTrue(set(real['components']).isdisjoint(self.scenes['components']))
        self.assertNotIn(self.scenes['components']['rrect-synthetic']['size'],
                         [v.get('size') for v in real['components'].values() if isinstance(v, dict)])
        keys = sorted([r[k] for k in self.G.KEY] for r in self.inventory['cells'])
        self.assertEqual(keys, self.population['statisticKeys'])
        self.assertEqual(sorted({tuple(k[:3]) for k in keys}),
                         [tuple(k) for k in self.population['physicalCells']])
        self.assertEqual(self.population['physicalCount'], 8)
        self.assertEqual(self.population['statisticCount'], 12)
        for row in self.inventory['cells']:
            self.assertEqual(row['dataOrigin'], 'synthetic')
            self.assertEqual(row['role'], 'gate')
            self.assertTrue(row['scene'].startswith('w51-synthetic-'))
            self.assertNotIn('nativeIdentity', row)
        for name, generation in self.inventory['generations'].items():
            self.assertTrue(name.startswith('w51-synthetic-'))
            self.assertEqual(generation['dataOrigin'], 'synthetic')
            for pin in generation['fixtureIdentityPins'].values():
                self.assertEqual(read(Path(pin['path']))['dataOrigin'], 'synthetic')
                self.assertEqual(self.G.pin(Path(pin['path'])), pin)

    def test_fixture_hashes_and_cells_are_disjoint_from_real_reference_metadata(self):
        # This is an exposed identity inventory, not a capture or analytical gate payload.
        real = read(HERE.parent.parent/'2026-10-08-w50-g0-declaration/references.json')
        real_cells = {tuple(r[k] for k in self.G.KEY[:3]) for r in real['cells']}
        self.assertTrue(real_cells.isdisjoint(tuple(k) for k in self.population['physicalCells']))
        self.assertTrue(set(real['generations']).isdisjoint(self.inventory['generations']))
        real_hashes = {value for generation in real['generations'].values()
                       for value in generation['documentPair'].values()}
        real_hashes.update(r[field]['sha256'] for r in real['cells']
                          for field in ('nativeEvidence', 'currentEvidence', 'currentMetadata')
                          if r.get(field))
        fixture_hashes = {item['sha256'] for item in read(self.output/'fixture.json')['files']}
        self.assertTrue(real_hashes.isdisjoint(fixture_hashes))
        for item in read(self.output/'fixture.json')['files']:
            self.assertTrue(Path(item['path']).is_relative_to(self.output))

    def test_output_cannot_enter_real_consumer_directories(self):
        with self.assertRaises(ValueError):
            self.G.build(HERE.parent.parent/'generations')
        with self.assertRaises(ValueError):
            self.G.build(HERE)

    def test_each_impulse_has_same_source_companions_and_seven_own_repeats(self):
        physical = {}
        for record in self.records:
            identity = tuple(record[k] for k in self.G.KEY[:3])
            physical.setdefault(identity, []).append(record)
            self.assertEqual(record['status'], 'MEASURED')
            self.assertEqual(len(record['runs']), 7)
            self.assertEqual([r['label'] for r in record['runs']], ['r'+str(i) for i in range(1, 8)])
            self.assertEqual(len({r['frame']['path'] for r in record['runs']}), 7)
            self.assertNotEqual(record['pins']['native']['sha256'], record['pins']['current']['sha256'])
            for run in record['runs']:
                self.assertEqual(run['dataOrigin'], 'synthetic')
                self.assertEqual(self.G.pin(Path(run['frame']['path'])), run['frame'])
        for identity, records in physical.items():
            if 'synthetic-impulse__' not in identity[2]:
                continue
            self.assertEqual({r['statistic'] for r in records},
                             {'T1-full-silhouette', 'low-end-path-level'})
            self.assertEqual(records[0]['pins'], records[1]['pins'])
            support = records[0]['publishedReading']['supports']['deep8_far24']
            self.assertGreater(support['pixels'], 0)

    def test_generated_pngs_reproduce_every_stored_support_band_and_budget(self):
        scientific = self.G.statistics()
        scene_by = {s['id']: s for s in self.scenes['scenes']}
        for record in self.records:
            spec = scene_by[record['scene']]
            member_has_low = any(r['profile'] == record['profile'] and r['scene'] == record['scene']
                                 and r['statistic'] == 'T1-low' for r in self.records)
            options = dict(text=member_has_low,
                           impulse=self.scenes['backgrounds'][spec['background']]['kind'] == 'impulse')
            pixels = lambda pin: scientific.S.decode_png(Path(pin['path']).read_bytes())
            background = pixels(record['pins']['background'])
            component = self.scenes['components'][spec['component']]
            scale = 2 if '-2x-' in record['profile'] else 1
            published = scientific.canonical_read(pixels(record['pins']['native']), background,
                component, self.scenes['canvas'], scale, web_rgb=pixels(record['pins']['current']), **options)
            repeats = [scientific.canonical_read(pixels(run['frame']), background,
                component, self.scenes['canvas'], scale, **options) for run in record['runs']]
            self.assertTrue(published == record['publishedReading'], 'Stored published support differs')
            self.assertTrue(scientific.evidence_reading(published, repeats) == record['readings'],
                            'Stored statistic or native budget differs')
            for reading in record['readings'].values():
                self.assertEqual(reading['status'], 'MEASURED')
                self.assertIsNotNone(reading['repeat'])
        text = next(r for r in self.records if r['statistic'] == 'T1-low')
        self.assertGreater(text['publishedReading']['supports']['eroded4']['pixels'], 0)
        self.assertGreater(text['readings']['T1-low']['native'], 0)
        self.assertGreater(text['readings']['T1-fine']['native'], 0)
        self.assertNotEqual(text['readings']['T1-low']['native'], text['readings']['T1-fine']['native'])

    def test_fine_member_covers_frozen_gaussian_low_projection_and_real_routing(self):
        records = [r for r in self.records if '-2x-' in r['profile']
                   and r['profile'].endswith('glass0.25') and 'synthetic-fine__' in r['scene']]
        self.assertEqual({r['statistic'] for r in records}, {'T1-full-silhouette', 'T1-low'})
        full = next(r for r in records if r['statistic'] == 'T1-full-silhouette')
        low = next(r for r in records if r['statistic'] == 'T1-low')
        self.assertEqual(full['pins'], low['pins'])
        self.assertTrue(full['publishedReading'] == low['publishedReading'])
        self.assertEqual(low['reference']['fidelity']['statistic'], 'T1-fine')
        fit = HERE.parent.parent/'2026-10-08-w50-g1-fit'
        projection = load_module(fit/'measurement/projection.py', 'w51_fixture_projection')
        rules = load_module(fit/'judge/rules.py', 'w51_fixture_rules')
        original = low['reference']
        inventory_pin = self.G.pin(self.output/'inventory.json')
        pair = original['currentDocumentPair']
        evidence = {'capture': low['pins']['current'], 'cell': low['pins']['currentMetadata'],
                    'material': {'documentPair': {'activeSha256': pair['active.dark'],
                                                 'recededSha256': pair['receded.dark']}}}
        readings = {}
        for name in ('T1-low', 'T1-fine'):
            frozen = low['readings'][name]
            support = low['publishedReading']['supports'][frozen['support']]
            statistic = {**low['publishedReading']['web']['statistics'][name],
                'measurementStatus': 'MEASURED', 'nativeValue': frozen['native'],
                'nativeRepeat': frozen['repeat'], 'required': True,
                'nativeSupportWitnesses': [{k: support[k] for k in
                    ('maskShape', 'maskPackedBitsSha256', 'pixels')}], 'nativeImage': low['pins']['native']}
            readings[name] = projection.reading(statistic, statistic, evidence, evidence,
                                                reported=False, eligible_empty=False)
        # A pure-function operand built from this fixture's PNG reading, NOT a capture receipt
        # or execution stage. The static reference report pins its source in the matrix slot.
        production = {'estimator': 'CANONICAL_NUMPY_GAUSSIAN_LOW', 'statistic': 'T1-low',
            'producer': 'packages/calibration/results/2026-10-08-w50-g1-fit/references/statistics.py#canonical_read',
            'field': 'web.statistics.T1-low', 'reading': 'first', 'capture': low['pins']['current'],
            'matrix': self.G.pin(self.output/'canonical-reference-evidence.json'),
            'scene': low['scene'], 'units': 'linear-luma', 'value': low['readings']['T1-low']['current']}
        self.assertTrue(projection.frozen_scope(original))
        with self.assertRaises(ValueError):
            projection.frozen_primary(original, original, readings['T1-low'], None, inventory_pin)
        wrong = {**production, 'estimator': 'PRODUCTION_TS_INTERIOR_LEVEL'}
        with self.assertRaises(ValueError):
            projection.frozen_primary(original, original, readings['T1-low'], wrong, inventory_pin)
        readings['T1-low'] = projection.frozen_primary(
            original, original, readings['T1-low'], production, inventory_pin)
        self.assertEqual(readings['T1-low']['candidateEstimator'], 'CANONICAL_NUMPY_GAUSSIAN_LOW')
        self.assertEqual(readings['T1-low']['routingOperands'], 'ORIGINAL_INVENTORY')
        self.assertEqual(readings['T1-low']['evidence']['candidate']['productionStatistic'], production)
        routed = rules.route_row({**original, 'sceneSource': 'canonical', 'family': 'texture',
            'originalReference': original, 'reference': original, 'readings': readings},
            inventory_sha256=inventory_pin['sha256'])
        self.assertTrue(routed['complete'])
        self.assertEqual(routed['status'], 'WITHIN')
        self.assertEqual([(c['rule'], c['statistic']) for c in routed['checks']],
                         [('canonical-T1-growth', 'T1-low')])
        self.assertEqual({d['statistic'] for d in routed['diagnostics']}, {'T1-low', 'T1-fine'})

    def test_real_target_preflight_has_all_six_groups_and_rejects_a_missing_member(self):
        target = load_module(HERE.parent.parent/'2026-10-08-w50-g1-fit/judge/targets.py',
                             'w51_synthetic_targets')
        cut = read(self.output/'targets-cut.json')
        config = read(self.output/'targets-config.json')
        groups = target.population(self.inventory, cut, config)
        self.assertEqual(set(groups), {(name, scale) for name in ('C rest', 'F inactive', 'P')
                                       for scale in (1, 2)})
        self.assertTrue(all(len(members) == 1 for members in groups.values()))
        target.contracts(self.inventory, self.G.pin(self.output/'inventory.json'), cut, config, {})
        changed = copy.deepcopy(cut)
        changed['T1']['cells'].pop()
        with self.assertRaises(ValueError):
            target.population(self.inventory, changed, config)

    def test_completion_is_same_inventory_with_no_newbed_rows(self):
        complete = read(self.output/'completed-references.json')
        self.assertEqual(complete['cells'], self.inventory['cells'])
        current = read(self.output/'completed-current-evidence.json')
        self.assertEqual(current['schema'], 'w50-completed-current-evidence-2')
        self.assertEqual(current['status'], 'EVIDENCE_ONLY')
        self.assertEqual(current['referenceEvidence'], [])
        self.assertEqual(current['dataOrigin'], 'synthetic')

    def test_native_fixture_passes_actual_production_admission_without_rendering(self):
        self.assertEqual(self.scenes['canvas'], {'width': 320, 'height': 200})
        fixture = read(self.output/'native-fixtures/manifest.json')
        self.assertEqual(fixture['dataOrigin'], 'synthetic')
        for record in self.records:
            native_path = self.output/'native-fixtures'/record['profile']/(record['scene']+'.png')
            self.assertEqual(self.G.pin(native_path), record['pins']['native'])
        result = subprocess.run([str(HERE.parents[2]/'node_modules/.bin/tsx'),
            str(HERE/'check_native.ts'), str(self.output)], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        current = read(self.output/'completed-current-evidence.json')
        self.assertEqual(set(current['native']['reports']), {'calibration', 'validation'})
        for role, pin in current['native']['reports'].items():
            report = read(Path(pin['path']))
            self.assertEqual(report['schema'], 'w50-native-role-read-1')
            self.assertEqual(report['role'], role)
            self.assertEqual(report['cells'], [])
            self.assertEqual(report['dataOrigin'], 'synthetic')

    def test_rebuild_is_deterministic_and_pin_complete(self):
        before = {str(p.relative_to(self.output)): self.G.pin(p)['sha256']
                  for p in self.output.rglob('*') if p.is_file()}
        self.G.build(self.output)
        after = {str(p.relative_to(self.output)): self.G.pin(p)['sha256']
                 for p in self.output.rglob('*') if p.is_file()}
        self.assertEqual(before, after)
        fixture = read(self.output/'fixture.json')
        for item in fixture['files']:
            self.assertEqual(self.G.pin(Path(item['path'])), item)


if __name__ == '__main__':
    unittest.main()
