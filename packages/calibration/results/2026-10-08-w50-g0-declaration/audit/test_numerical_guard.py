"""Numerical provenance is a closed measured cohort, not a PASS flag with an arbitrary pin."""
import copy
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('numerical_guard', HERE / 'numerical_guard.py')
G = importlib.util.module_from_spec(spec)
spec.loader.exec_module(G)
spec = importlib.util.spec_from_file_location('numerical_runner', HERE / 'runner.py')
R = importlib.util.module_from_spec(spec)
spec.loader.exec_module(R)


class NumericalProvenance(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.all = {}
        runtime = []
        for name in G.REQUIRED_RUNTIME:
            pin = self.put(name, {'syntheticSource': name})
            runtime.append(pin)
        producer = next(p for p in runtime if p['path'] == G.PRODUCER)
        self.put(G.CLOSURE, {'schema': 'w50-numerical-runtime-closure-1', 'sources': runtime})
        # The runtime witness is root-pinned, not a producer input in the report's union.
        self.all.pop(G.CLOSURE)
        candidates = []
        for position in (0.25, 0.5):
            endpoints = {}
            for pose in ('active', 'receded'):
                for scheme in ('light', 'dark'):
                    name = f'candidate/{position}-{pose}-{scheme}.json'
                    suffix = '-receded' if pose == 'receded' else ''
                    key = f'apple-macos-27.0-1x-{scheme}-standard-glass{position:.3f}{suffix}'
                    endpoint = self.put(name, {'profileKey': key,
                                              'patch': {'lowEndStrength': 1 if scheme == 'dark' else 0}})
                    endpoints[f'{pose}.{scheme}'] = {'path': Path(name).name, 'sha256': endpoint['sha256']}
            pin = self.put(f'candidate/{position}.json', {'kind': 'vitrea-candidate-material-document',
                'schemaVersion': 1, 'glassTintAmount': position, 'endpoints': endpoints})
            candidates.append({'position': position, **pin})
        hashes = sorted(c['sha256'] for c in candidates)
        refs, records = [], []
        for candidate in candidates:
            position = candidate['position']
            for pose in ('active', 'receded'):
                scene = f'impulse__rrect-ml__{"rest" if pose == "active" else "inactive"}'
                for scale in (1, 2):
                    profile = f'apple-macos-27.0-{scale}x-dark-standard-glass{position}'
                    identity = f'{profile}|webgpu|{scene}'
                    row = {'id': identity, 'profile': profile, 'renderer': 'webgpu', 'scene': scene,
                           'variant': 'regular', 'position': position, 'pose': pose, 'dpr': scale,
                           'span': 128, 'role': 'gate', 'candidateSha256': candidate['sha256'],
                           'encodedLuminance': 0.01, 'linearLuminance': 0.001, 'rgb': [0.001]*3}
                    evidence = self.put(f'evidence/{len(records)}.json',
                        {'schema': 'w50-measured-tone-argument-1', **row})
                    records.append({**row, 'evidence': evidence})
                    refs.append({'profile': profile, 'renderer': 'webgpu', 'scene': scene, 'role': 'gate'})
        references = self.put(G.REFERENCES, {'schema': 'w50-reference-inventory-1', 'cells': refs})
        required = sorted(r['id'] for r in records)
        arguments = self.put('arguments.json', {'schema': 'w50-structured-arguments-1',
            'candidateSha256s': hashes, 'references': references, 'requiredIds': required, 'records': records})
        cohort = self.put('cohort.json', {'schema': 'w50-numerical-cohort-1',
            'candidates': candidates, 'structuredArguments': arguments})
        projection = [{k: r[k] for k in G.ARGUMENT_PROJECTION} for r in records]
        self.report = {'producer': producer, 'runtimeSources': runtime,
            'cohort': cohort, 'argumentManifest': arguments, 'referenceInventory': references,
            'candidateDocuments': candidates,
            'candidateSha256s': hashes, 'requiredStructuredArgumentIds': required,
            'structuredArgumentIds': required, 'structuredArguments': projection,
            'sources': list(self.all.values())}
        self.report.update(schema='w50-candidate-numerical-referee-1', status='PASS',
            domain={'inputCodeMin': 0, 'inputCodeMax': 64, 'stepCode': 1/64, 'spanMin': 32,
                    'spanMax': 224, 'scales': [1,2], 'positions': [0.25,0.5],
                    'poses': ['active','receded']}, samples=6325768,
            maxRunningDrawdownCode=0, minimumRequestedNeutral=0,
            fixedJoinPass=True, standDownPass=True, structuredArgumentPass=True,
            negativeRequests=[], structuredCoverage=sorted(
                f'{position}:{pose}:{dpr}' for position in (0.25, 0.5)
                for pose in ('active', 'receded') for dpr in (1, 2)))
        self.candidate = hashes[0]

    def tearDown(self):
        self.tmp.cleanup()

    def put(self, name, data):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(data, sort_keys=True) + '\n')
        pin = {'path': name, 'sha256': G.sha(path)}
        self.all[name] = pin
        return pin

    def test_measured_f32_arguments_keep_their_values_and_scene_scoped_input(self):
        record = {'encodedLuminance': 0.250980406999588,
                  'linearLuminance': 0.051269459, 'rgb': [0.051269458] * 3}
        original = copy.deepcopy(record)
        G.validate_tone_values(record)
        self.assertEqual(record, original)
        with self.assertRaises(ValueError):
            G.validate_tone_values({**record, 'linearLuminance': 0.0513})
        with self.assertRaises(ValueError):
            G.validate_tone_values({**record, 'encodedLuminance': 1.01})

    def test_nonshipped_endpoint_spelling_keeps_numeric_position_and_exact_pose(self):
        for position in (0.25, 0.5):
            active = f'apple-macos-27.0-1x-dark-standard-glass{position:.3f}'
            G.validate_endpoint_identity(active, 'active.dark', position)
            G.validate_endpoint_identity(active + '-receded', 'receded.dark', position)
            for key, slot in ((active + '-receded', 'active.dark'),
                              (active, 'receded.dark'),
                              (active.replace('27.0', '26.5'), 'active.dark'),
                              (active.replace('1x', '2x'), 'active.dark'),
                              (active.replace('dark', 'light'), 'active.dark'),
                              (active.replace(f'{position:.3f}', '0.750'), 'active.dark'),
                              (active.replace(f'{position:.3f}', str(position)), 'active.dark')):
                with self.subTest(key=key, slot=slot), self.assertRaises(ValueError):
                    G.validate_endpoint_identity(key, slot, position)

    def test_complete_pinned_cohort_is_accepted(self):
        G.validate_provenance(self.report, self.candidate, self.root)
        R.validate_numerical_referee(self.report, self.candidate, self.root)

    def test_runner_refuses_bad_numbers_even_with_complete_provenance(self):
        for key, value in [('minimumRequestedNeutral', -0.00001),
                           ('maxRunningDrawdownCode', 0.00011), ('samples', 100),
                           ('fixedJoinPass', False), ('standDownPass', False),
                           ('negativeRequests', [{'minimum': -0.1}]), ('structuredCoverage', [])]:
            changed = {**self.report, key: value}
            with self.subTest(key=key), self.assertRaises(ValueError):
                R.validate_numerical_referee(changed, self.candidate, self.root)

    def test_arbitrary_unchanged_source_cannot_stand_in_for_producer(self):
        with self.assertRaises(ValueError):
            G.validate_provenance({'sources': [self.report['sources'][0]]}, self.candidate, self.root)

    def test_missing_or_extra_reported_argument_refused(self):
        for field in ('structuredArgumentIds', 'requiredStructuredArgumentIds', 'structuredArguments'):
            changed = copy.deepcopy(self.report)
            changed[field].pop()
            with self.subTest(field=field), self.assertRaises(ValueError):
                G.validate_provenance(changed, self.candidate, self.root)

    def test_candidate_position_or_unpinned_bytes_refused(self):
        changed = copy.deepcopy(self.report)
        changed['candidateDocuments'][0]['position'] = 0.5
        with self.assertRaises(ValueError):
            G.validate_provenance(changed, self.candidate, self.root)
        path = self.root / self.report['candidateDocuments'][0]['path']
        path.write_text('{}')
        with self.assertRaises(ValueError):
            G.validate_provenance(self.report, self.candidate, self.root)

    def test_changed_measured_record_and_missing_runtime_dependency_refused(self):
        path = self.root / 'evidence/0.json'
        original = path.read_bytes()
        self.put('evidence/0.json', {'schema': 'w50-measured-tone-argument-1', 'encodedLuminance': 0})
        with self.assertRaises(ValueError):
            G.validate_provenance(self.report, self.candidate, self.root)
        path.write_bytes(original)
        changed = copy.deepcopy(self.report)
        changed['runtimeSources'].pop()
        with self.assertRaises(ValueError):
            G.validate_provenance(changed, self.candidate, self.root)

    def test_even_rehashed_partial_manifest_cannot_drop_fixed_reference_target(self):
        changed = copy.deepcopy(self.report)
        manifest_path = self.root / changed['argumentManifest']['path']
        manifest = json.loads(manifest_path.read_text())
        manifest['records'].pop()
        manifest['requiredIds'] = sorted(r['id'] for r in manifest['records'])
        arguments = self.put('arguments.json', manifest)
        cohort_path = self.root / changed['cohort']['path']
        cohort = json.loads(cohort_path.read_text())
        cohort['structuredArguments'] = arguments
        changed['argumentManifest'] = arguments
        changed['cohort'] = self.put('cohort.json', cohort)
        changed['structuredArgumentIds'] = manifest['requiredIds']
        changed['requiredStructuredArgumentIds'] = manifest['requiredIds']
        changed['structuredArguments'] = changed['structuredArguments'][:-1]
        changed['sources'] = list(self.all.values())
        with self.assertRaises(ValueError):
            G.validate_provenance(changed, self.candidate, self.root)


if __name__ == '__main__':
    unittest.main()
