"""Synthetic selection and provenance-binding tests; no actual values or artefacts are read."""
import copy
import importlib.util
import json
from pathlib import Path
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


if __name__ == '__main__': unittest.main()
