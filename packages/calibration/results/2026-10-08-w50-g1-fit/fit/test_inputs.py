"""Synthetic selection and provenance-binding tests; no actual values or artefacts are read."""
import copy
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

spec = importlib.util.spec_from_file_location('w50_fit_inputs', Path(__file__).with_name('inputs.py'))
I = importlib.util.module_from_spec(spec)
spec.loader.exec_module(I)


def pin(name, digit='a'):
    return {'path': name, 'sha256': digit*64}


def fixture():
    cells, scenes, refs = [], [], []
    reports = {r: {'schema': 'w50-native-role-read-1', 'role': r, 'ready': True, 'stops': [],
                    'declarationSha256': 'a'*64, 'cells': []} for r in ('calibration', 'validation')}
    for position in (.25, .5):
        for pose in ('active', 'receded'):
            for scale in (1, 2):
                for level, span, role in ((0, 44, 'calibration'), (8, 96, 'calibration'),
                                           (28, 160, 'calibration'), (40, 44, 'validation'),
                                           (4, 128, 'validation'), (64, 160, 'calibration')):
                    scene = f'cell-grey-{level:03}-s{span:03}__'+('rest' if pose == 'active' else 'inactive')
                    profile = f'apple-macos-27.0-{scale}x-dark-standard-glass{position}'
                    cell = dict(id=profile+'/'+scene, profile=profile, scene=scene, family='span' if span==128 else 'uniform',
                                role=role, span=span, scale=scale, pose=pose, glass=position,
                                background=f'grey-{level}', reference=profile+'/ref', runs=[1,2,3])
                    cells.append(cell)
                    if scene not in [s['id'] for s in scenes]:
                        scenes.append(dict(id=scene, background=cell['background']))
                    stats = {name: dict(status='MEASURED', measurementStatus='MEASURED', required=True,
                        units='encoded-RGB-codes', support=support, value=[level+10, level+11, level+12])
                        for name, support in (('deep8-channel-median', 'deep8'), ('central8-channel-median', 'center8'))}
                    runs = [dict(run=i, dependency=cell['reference'], evidence=dict(run=i, cell=cell['id']))
                            for i in (1,2,3)]
                    reports[role]['cells'].append({**cell, 'statistics': stats, 'runs': runs})
                    for name in stats:
                        refs.append({**cell, 'renderer': 'webgpu', 'statistic': name})
    backgrounds = {f'grey-{v}': {'kind': 'solid', 'srgb': [v, v, v]} for v in (0, 4, 8, 28, 40, 64)}
    return {'cells': cells}, {'scenes': scenes, 'backgrounds': backgrounds}, reports, {'cells': refs}


class SelectionTests(unittest.TestCase):
    def test_selects_exact_exposed_uniform_span_channels_scales_and_four_endpoints(self):
        manifest, scenes, reports, refs = fixture()
        observations = I.uniform_observations(manifest, scenes, reports, refs, 'a'*64)
        self.assertEqual(len(observations), 4*2*5*2*3)
        self.assertEqual({o['endpoint'] for o in observations}, set(I.ENDPOINTS))
        self.assertEqual({o['dpr'] for o in observations}, {1, 2})
        self.assertEqual({o['statistic'] for o in observations}, {'deep8-channel-median', 'central8-channel-median'})
        self.assertEqual({o['channel'] for o in observations}, {'R', 'G', 'B'})
        self.assertTrue(all(o['inputCode'] <= 40 for o in observations))
        self.assertEqual([o['value'] for o in observations[:3]], [10, 11, 12])

    def test_no_missing_duplicate_withheld_wrong_support_or_inferred_target_is_admitted(self):
        for mutation in ('missing', 'duplicate', 'withheld', 'support', 'nonfinite', 'native-kind', 'reference-role'):
            m, s, reports, refs = fixture()
            row = reports['calibration']['cells'][0]
            if mutation=='missing': reports['calibration']['cells'].pop(0)
            if mutation=='duplicate': reports['calibration']['cells'].append(copy.deepcopy(row))
            if mutation=='withheld': row['role']='blind'
            if mutation=='support': row['statistics']['central8-channel-median']['support']='central8'
            if mutation=='nonfinite': row['statistics']['deep8-channel-median']['value'][0]=float('nan')
            if mutation=='native-kind': s['backgrounds']['grey-0']['srgb']=[0, 0, 1]
            if mutation=='reference-role': refs['cells'][0]['role']='historical-prediction-check'
            with self.subTest(mutation=mutation), self.assertRaises(ValueError):
                I.uniform_observations(m, s, reports, refs, 'a'*64)

    def test_fixed_join_population_cannot_omit_actual_span_or_scale(self):
        joins = {e: [dict(span=s, dpr=d, value=90) for d in (1, 2) for s in range(32, 225)] for e in I.ENDPOINTS}
        self.assertEqual(len(I.join_observations(joins)), 4*386)
        joins[I.ENDPOINTS[0]].pop()
        with self.assertRaises(ValueError): I.join_observations(joins)


class BindingTests(unittest.TestCase):
    def fixture(self):
        captured = [dict(position=p, **pin(f'gate0/{p}.json', d)) for p, d in ((.25,'a'),(.5,'b'))]
        evaluation = [dict(position=p, **pin(f'candidate/{p}.json', d)) for p, d in ((.25,'c'),(.5,'d'))]
        records, required = [], {}
        for before in captured:
            profile=f'apple-macos-27.0-1x-dark-standard-glass{before["position"]}'
            scene='cell-grey-000-s044__rest'; identity=f'{profile}|webgpu|{scene}'
            record=dict(id=identity, profile=profile, renderer='webgpu', scene=scene, role='calibration',
                position=before['position'], pose='active', dpr=1, span=44, variant='regular',
                candidateSha256=before['sha256'], encodedLuminance=0, linearLuminance=0, rgb=[0,0,0],
                provenance=dict(capture=pin('external/capture.png'), report=pin('external/report.json'),
                                candidateDocument={k:before[k] for k in ('path','sha256')}))
            records.append(record); required[identity]=record
        proofs = [dict(schema='w50-held-sampling-proof-1', position=b['position'],
            capturedCandidate={k:b[k] for k in ('path','sha256')},
            evaluationCandidate={k:a[k] for k in ('path','sha256')},
            heldMaterialSha256='e'*64, lightEndpointSha256s=['f'*64,'0'*64], cssTierMappingSha256='1'*64)
            for b,a in zip(captured,evaluation)]
        return records, required, captured, evaluation, proofs

    def test_binding_preserves_original_capture_identity_and_only_adds_evaluation_wrapper(self):
        records, required, captured, evaluation, proofs = self.fixture()
        original=copy.deepcopy(records)
        out=I.evaluation_arguments(records, required, captured, evaluation, proofs, pin('current-result.json'))
        self.assertEqual(records, original)
        for old, wrapped in zip(records, out):
            self.assertEqual(wrapped['capturedArgument'], old)
            self.assertEqual(wrapped['capturedCandidateSha256'], old['candidateSha256'])
            self.assertEqual(wrapped['provenance'], old['provenance'])
            self.assertNotEqual(wrapped['candidateSha256'], old['candidateSha256'])
            self.assertEqual(wrapped['evaluationCandidateSha256'], wrapped['candidateSha256'])
            self.assertEqual(wrapped['argumentSemantics'], 'EVALUATED_CANDIDATE_USING_HELD_GATE0_SAMPLING')
            self.assertEqual(wrapped['currentCandidate'], old['provenance']['candidateDocument'])
            self.assertEqual(len(wrapped['capturedArgumentSha256']), 64)

    def test_missing_members_changed_capture_identity_or_unproved_sampling_refuse(self):
        for mutation in ('missing', 'duplicate', 'identity', 'proof', 'capture', 'role'):
            records, required, captured, evaluation, proofs = self.fixture()
            if mutation=='missing': records.pop()
            if mutation=='duplicate': records.append(copy.deepcopy(records[0]))
            if mutation=='identity': records[0]['candidateSha256']='9'*64
            if mutation=='proof': proofs[0]['capturedCandidate']=pin('another.json')
            if mutation=='capture': records[0]['provenance'].pop('capture')
            if mutation=='role': records[0]['role']='blind'
            with self.subTest(mutation=mutation), self.assertRaises(ValueError):
                I.evaluation_arguments(records, required, captured, evaluation, proofs, pin('current-result.json'))



GUARD = Path(__file__).resolve().parents[2]/'2026-10-08-w50-g0-declaration/audit/numerical_guard.py'
guard_spec = importlib.util.spec_from_file_location('w50_frozen_numerical_guard', GUARD)
G = importlib.util.module_from_spec(guard_spec)
guard_spec.loader.exec_module(G)


class CanonicalRoleBindingTests(unittest.TestCase):
    """DL5p on records shaped like the completed current read, verified by the frozen G0 guard.

    The canonical-scene rows carry their scenes.json split (calibration, probe) where G0 binds
    gate; the W50-bed rows already carry G0's role. Synthetic values, real record shape.
    """
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name).resolve(); self.pins = {}
        runtime = [self.put(name, {'syntheticSource': name}) for name in G.REQUIRED_RUNTIME]
        self.producer = next(p for p in runtime if p['path'] == G.PRODUCER)
        self.runtime = runtime
        self.put(G.CLOSURE, {'schema': 'w50-numerical-runtime-closure-1', 'sources': runtime})
        self.pins.pop(G.CLOSURE)
        self.evaluation, self.captured = [], []
        for position in (0.25, 0.5):
            endpoints = {}
            for pose in ('active', 'receded'):
                for scheme in ('light', 'dark'):
                    name = f'candidate/{position}-{pose}-{scheme}.json'
                    key = (f'apple-macos-27.0-1x-{scheme}-standard-glass{position:.3f}' +
                           ('-receded' if pose == 'receded' else ''))
                    item = self.put(name, {'profileKey': key,
                                           'patch': {'lowEndStrength': 1 if scheme == 'dark' else 0}})
                    endpoints[f'{pose}.{scheme}'] = {'path': Path(name).name, 'sha256': item['sha256']}
            item = self.put(f'candidate/{position}.json', {'kind': 'vitrea-candidate-material-document',
                'schemaVersion': 1, 'glassTintAmount': position, 'endpoints': endpoints})
            self.evaluation.append({'position': position, **item})
            self.captured.append(dict(position=position, **pin(f'gate0/{position}.json', '3' if position == .25 else '4')))
        self.records, cells = [], []
        for before in self.captured:
            position = before['position']
            for pose, suffix in (('active', 'rest'), ('receded', 'inactive')):
                for scale in (1, 2):
                    profile = f'apple-macos-27.0-{scale}x-dark-standard-glass{position}'
                    split = 'calibration' if scale == 1 else 'probe'
                    for scene, role, required, source in (
                            (f'dark-solid__capsule-button__{suffix}', split, 'gate', 'canonical'),
                            (f'cell-grey-008-s044__{suffix}', 'calibration', 'calibration', 'w50')):
                        for renderer in ('webgpu', 'css'):
                            identity = f'{profile}|{renderer}|{scene}'
                            provenance = dict(sceneSource=source, candidateDocument={k: before[k] for k in ('path', 'sha256')},
                                capture=pin('external/capture.png', '5'), report=pin('external/report.json', '6'))
                            if source == 'canonical':
                                provenance['originalRow'] = dict(fixtureSet=role, state=suffix, tier='dom')
                            self.records.append(dict(id=identity, profile=profile, renderer=renderer,
                                scene=scene, variant='regular', pose=pose, position=position, dpr=scale,
                                span=44, role=role, candidateSha256=before['sha256'],
                                encodedLuminance=0.01, linearLuminance=0.001, rgb=[0.001]*3,
                                provenance=provenance))
                            cells.append(dict(profile=profile, renderer=renderer, scene=scene, role=required,
                                              statistic='mean'))
        self.inventory = {'schema': 'w50-reference-inventory-1', 'cells': cells}
        self.required = G.required_arguments(self.inventory)
        self.proofs = [dict(schema='w50-held-sampling-proof-1', position=b['position'],
            capturedCandidate={k: b[k] for k in ('path', 'sha256')},
            evaluationCandidate={k: a[k] for k in ('path', 'sha256')},
            heldMaterialSha256='e'*64, lightEndpointSha256s=['f'*64, '0'*64], cssTierMappingSha256='1'*64)
            for b, a in zip(self.captured, self.evaluation)]

    def put(self, name, data):
        path = self.root/name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(data, sort_keys=True)+'\n')
        self.pins[name] = {'path': name, 'sha256': G.sha(path)}
        return self.pins[name]

    def bind(self, records=None):
        return I.evaluation_arguments(self.records if records is None else records, self.required,
            self.captured, self.evaluation, self.proofs, pin('live-inputs/completed-current.json'))

    def verify(self, wrapped):
        """Persist as execution.bind_arguments does, then run the unchanged G0 verification."""
        wrapped = copy.deepcopy(wrapped)
        references = self.put(G.REFERENCES, self.inventory)
        for index, record in enumerate(wrapped):
            record['evidence'] = self.put(f'numerical/argument-{index:04}.json',
                                          {'schema': 'w50-measured-tone-argument-1', **record})
        hashes = sorted(c['sha256'] for c in self.evaluation)
        ids = sorted(self.required)
        manifest = self.put('numerical/arguments.json', {'schema': 'w50-structured-arguments-1',
            'candidateSha256s': hashes, 'references': references, 'requiredIds': ids, 'records': wrapped})
        cohort = self.put('numerical/cohort.json', {'schema': 'w50-numerical-cohort-1',
            'candidates': self.evaluation, 'structuredArguments': manifest})
        report = dict(producer=self.producer, runtimeSources=self.runtime, cohort=cohort,
            argumentManifest=manifest, referenceInventory=references, candidateDocuments=self.evaluation,
            candidateSha256s=hashes, requiredStructuredArgumentIds=ids, structuredArgumentIds=ids,
            structuredArguments=[{k: r[k] for k in G.ARGUMENT_PROJECTION} for r in wrapped],
            structuredCoverage=sorted(f'{p}:{pose}:{d}' for p in (0.25, 0.5)
                                      for pose in ('active', 'receded') for d in (1, 2)),
            negativeRequests=[], sources=list(self.pins.values()))
        G.validate_provenance(report, hashes[0], self.root)

    def test_frozen_guard_refuses_the_captured_split_role_unnormalised(self):
        wrapped = self.bind()
        for record in wrapped:
            if 'roleBinding' in record:
                record['role'] = record['roleBinding']['capturedRole']
        with self.assertRaisesRegex(ValueError, 'Measured argument identity differs'):
            self.verify(wrapped)

    def test_frozen_guard_accepts_normalised_canonical_records_with_captured_bytes_kept(self):
        original = copy.deepcopy(self.records)
        wrapped = self.bind()
        self.assertEqual(self.records, original)
        self.verify(wrapped)
        by_id = {r['id']: r for r in original}
        normalised = [r for r in wrapped if 'roleBinding' in r]
        self.assertEqual(len(normalised), 16)
        self.assertEqual({r['roleBinding']['capturedRole'] for r in normalised}, {'calibration', 'probe'})
        for record in wrapped:
            source = by_id[record['id']]
            self.assertEqual(record['role'], self.required[record['id']]['role'])
            self.assertEqual(record['capturedArgument'], source)
            self.assertEqual(record['capturedArgumentSha256'], I.digest(source))
            self.assertEqual(record['provenance'], source['provenance'])
            if source['provenance']['sceneSource'] == 'w50':
                self.assertNotIn('roleBinding', record)
            else:
                self.assertEqual(record['roleBinding'], dict(capturedRole=source['role'], boundRole='gate',
                    basis='provenance.originalRow.fixtureSet', ruling='DL5p'))
                self.assertEqual(record['capturedArgument']['role'], source['role'])

    def test_frozen_guard_refuses_a_holdout_or_historical_bound_role(self):
        for role in ('holdout', 'historical-prediction-check', 'blind'):
            wrapped = self.bind()
            target = next(r for r in wrapped if 'roleBinding' in r)
            target['role'] = role
            with self.subTest(role=role), self.assertRaisesRegex(ValueError, 'Measured argument identity differs'):
                self.verify(wrapped)

    def test_binder_refuses_every_role_disagreement_outside_the_canonical_gate_seam(self):
        def canonical(records):
            return next(r for r in records if r['provenance']['sceneSource'] == 'canonical')
        for mutation in ('holdout', 'historical', 'blind', 'fixtureSet', 'noOriginalRow', 'newbed',
                         'requiredNotGate', 'requiredWithheld'):
            records = copy.deepcopy(self.records); record = canonical(records)
            required = self.required
            if mutation in ('holdout', 'historical', 'blind'):
                role = {'holdout': 'holdout', 'historical': 'historical-prediction-check'}.get(mutation, mutation)
                record['role'] = role; record['provenance']['originalRow']['fixtureSet'] = role
            if mutation == 'fixtureSet': record['provenance']['originalRow']['fixtureSet'] = (
                'probe' if record['role'] == 'calibration' else 'calibration')
            if mutation == 'noOriginalRow': record['provenance'].pop('originalRow')
            if mutation == 'newbed': record['provenance']['sceneSource'] = 'w50'
            if mutation in ('requiredNotGate', 'requiredWithheld'):
                required = copy.deepcopy(self.required)
                required[record['id']]['role'] = 'validation' if mutation == 'requiredNotGate' else 'blind'
            with self.subTest(mutation=mutation), self.assertRaisesRegex(ValueError, 'withheld reference identity'):
                I.evaluation_arguments(records, required, self.captured, self.evaluation, self.proofs,
                                       pin('live-inputs/completed-current.json'))


if __name__ == '__main__': unittest.main()
