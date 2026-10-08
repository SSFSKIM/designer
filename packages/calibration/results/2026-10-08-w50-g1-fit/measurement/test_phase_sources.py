"""Generated arrays/temporary artifacts exercise the new source wrappers, not real capture trees."""
import copy
import hashlib
import io
import json
from pathlib import Path
import tempfile
import types
import unittest
from unittest.mock import patch

import numpy as np
from PIL import Image

HERE = Path(__file__).resolve().parent


def source(path, name):
    module = types.ModuleType(name); module.__file__ = str(path)
    exec(compile(path.read_bytes(), str(path), 'exec', dont_inherit=True), module.__dict__)
    return module


S = source(HERE/'phase_sources.py', 'w50_phase_source_tests')


def png(rgb):
    stream = io.BytesIO(); Image.fromarray(rgb).save(stream, format='PNG')
    return stream.getvalue()


def write(path, value):
    raw = value if isinstance(value, bytes) else (json.dumps(value)+'\n').encode()
    path.parent.mkdir(parents=True, exist_ok=True); path.write_bytes(raw)
    return {'path': str(path), 'sha256': hashlib.sha256(raw).hexdigest()}


class SourceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(); self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name).resolve()
        self.output = self.base/'output'; self.output.mkdir()
        self.profile = 'synthetic'
        self.scene = 'cell'
        self.canvas = {'width': 64, 'height': 64}
        self.component = {'kind': 'rrect', 'size': [48, 48], 'radius': 0}
        self.background = np.zeros((64, 64, 3), dtype=np.uint8)
        self.native = self.background.copy(); self.native[8:56, 8:56] = 128
        self.first = self.background.copy(); self.first[:, 32:] = 255
        self.run = {'id': 'synthetic', 'sceneSource': 'w50', 'profile': self.profile, 'renderer': 'webgpu',
            'scenes': [self.scene], 'sets': ['holdout'], 'candidate': {'path': 'candidate.json', 'sha256': 'a'*64},
            'captureRoot': str(self.output/'capture'), 'matrixPath': str(self.output/'matrix.json')}
        self.receipt = {k: self.run[k] for k in ('sceneSource', 'profile', 'renderer', 'candidate')}
        self.receipt.update(scene=self.scene, lane='candidate')
        self.context = {'phase': 'exposure', 'repo': str(self.base), 'output': str(self.output),
                        'executionRoot': str(self.base/'root.json')}
        self.reader = S.PhaseSources.__new__(S.PhaseSources)
        self.reader.context = self.context; self.reader.output = self.output; self.reader.repo = self.base
        self.reader.root = {}; self.reader.config = {}; self.reader.canonical_cache = {}
        self.reader.dispatcher = types.SimpleNamespace(require_render_admission=lambda *a, **k: None)
        self.plan = {'dpr': 1, 'position': .25, 'canvas': self.canvas,
            'scenes': [{'scene': self.scene, 'pose': 'active', 'span': 48}]}
        self.spec = self.plan['scenes'][0]
        self.reader.scenes = {'canvas': self.canvas, 'scenes': [{'id': self.scene,
            'background': 'background', 'component': 'rectangle', 'state': 'rest'}],
            'components': {'rectangle': self.component}, 'backgrounds': {'background': {'kind': 'solid'}}}
        self.material = {'documentPair': {'activeSha256': 'b'*64, 'recededSha256': 'c'*64}}
        self.evidence = {'material': self.material, 'capture': {'path': str(self.output/'first.png'), 'sha256': 'd'*64}}
        self.reader.authenticate = lambda *a: (self.plan, self.spec, {'png': png(self.first)}, self.evidence.copy())
        self.cell = self.native_cell()

    def native_cell(self):
        runs = []
        for run in (1, 2, 3):
            mask = np.ones((64, 64), dtype=bool)
            if run == 2: mask[:, 32:] = False
            if run == 3: mask[:, :32] = False
            readings = S.M.R.S.read_frame(self.native, self.background, self.component,
                self.canvas, 1, include_structured=True, silhouette_mask=mask)
            runs.append({'run': run, 'dependency': 'synthetic/reference', 'readings': readings,
                'evidence': {'run': run, 'cell': 'synthetic/cell', 'roles': ['blind'],
                    'path': f'run-{run}/cell.png', 'sha256': str(run)*64}})
        return {'id': 'synthetic/cell', 'reference': 'synthetic/reference', 'profile': self.profile,
            'scene': self.scene, 'role': 'blind', 'pose': 'active', 'scale': 1, 'span': 48,
            'glass': .25, 'level': 4, 'family': 'span', 'runs': runs,
            'statistics': S.M.R.aggregate_runs(runs)}

    def blind_rows(self):
        return [{'profile': self.profile, 'renderer': 'webgpu', 'scene': self.scene,
            'statistic': name, 'role': 'blind', 'support': 'Original support prose.',
            'nativeIdentity': self.cell['id'], 'referenceIdentity': self.cell['reference']}
            for name in self.cell['statistics']]

    def authentication_fixture(self):
        folder = Path(self.run['captureRoot'])/self.scene
        metadata = {'renderer': 'webgpu', 'colorSpace': 'srgb',
            'capturePath': 'candidateDocument=synthetic declarationSha256=aaaaaaaaaaaa',
            'deterministic': False, 'repeatNoise': .00001}
        page = {'sceneId': self.scene, 'material': {'profileKey': 'actual'},
            'groups': [{'id': 'group', 'state': {'samplingBackend': 'gpu-texture'}}]}
        self.receipt['artifacts'] = {
            'png': write(folder/'cell__webgpu.png', png(self.first)),
            'report': write(folder/'report__webgpu.json', {'page': page}),
            'cell': write(folder/'cell__webgpu.json', metadata)}
        self.receipt['repeatPair'] = write(folder/'repeat__webgpu.json', {'synthetic': 'pair'})
        self.receipt['repeatAdmission'] = write(folder/'repeat-admission__webgpu.json', {'synthetic': 'proof'})
        endpoints = {slot: {'path': '/synthetic/'+slot+'.json', 'sha256': str(index)*64,
            'profileKey': 'actual-'+slot, 'resolvedMaterialSha256': 'a'*16, 'patch': {}}
            for index, slot in enumerate(('active.dark', 'receded.dark', 'active.light', 'receded.light'), 1)}
        return metadata, {'endpoints': endpoints}, page

    def test_authenticator_delegates_both_page_proof_without_rewriting_honest_noise(self):
        metadata, candidate, page = self.authentication_fixture()
        with patch.object(S.W, 'scene_plan', return_value=self.plan), \
             patch.object(S.W, 'candidate_info', return_value=candidate), \
             patch.object(S.M, 'verify_live_repeat', return_value={'reading': 'first'}) as verify:
            _, _, blobs, evidence = S.PhaseSources.authenticate(self.reader, self.run, self.receipt)
        verify.assert_called_once_with(self.context, self.run, self.receipt, metadata)
        self.assertEqual(S.M._json(blobs['cell']), metadata)
        self.assertEqual(evidence['capture'], self.receipt['artifacts']['png'])
        self.assertEqual(evidence['material']['reportedMaterial'], page['material'])
        self.assertEqual(evidence['material']['samplingBackends'],
                         [{'groupId': 'group', 'samplingBackend': 'gpu-texture'}])
        self.assertEqual(evidence['reading'], 'first')

    def test_bad_pair_proof_or_changed_first_image_stops_before_any_measurement(self):
        _, candidate, _ = self.authentication_fixture()
        with patch.object(S.W, 'scene_plan', return_value=self.plan), \
             patch.object(S.W, 'candidate_info', return_value=candidate), \
             patch.object(S.M, 'verify_live_repeat', side_effect=ValueError('second-page source refusal')):
            with self.assertRaisesRegex(ValueError, 'second-page'):
                S.PhaseSources.authenticate(self.reader, self.run, self.receipt)
        Path(self.receipt['artifacts']['png']['path']).write_bytes(png(np.zeros_like(self.first)))
        with patch.object(S.W, 'scene_plan', return_value=self.plan), \
             patch.object(S.M, 'verify_live_repeat') as verify:
            with self.assertRaisesRegex(ValueError, 'Changed'):
                S.PhaseSources.authenticate(self.reader, self.run, self.receipt)
        verify.assert_not_called()

    def test_blind_wrapper_reuses_actual_chain_and_three_different_native_t1_masks(self):
        rows = self.blind_rows()
        provenance = {'nativeExposure': {'path': str(self.output/'artifacts.json'), 'sha256': 'e'*64},
                      'nativeRead': {'path': str(self.output/'native.json'), 'sha256': 'f'*64}}
        with patch.object(S.B, 'blind_cell', return_value=(self.cell, {'synthetic': 'dependency'},
                                                         self.base, provenance)) as authority, \
             patch.object(S.M.R, 'read_verified_frame', return_value=self.background):
            result = self.reader.measure_member(self.run, self.receipt, rows)
        authority.assert_called_once_with(self.context, self.run, rows[0], self.reader.scenes)
        reading = result['statistics']['T1-full-silhouette']
        self.assertEqual(reading['runValues'], [.5, 0, 0])
        self.assertEqual(reading['value'], 0)
        self.assertEqual(len({w['maskPackedBitsSha256'] for w in reading['nativeSupportWitnesses']}), 3)
        self.assertEqual(reading['nativeRuns'], [r['evidence'] for r in self.cell['runs']])
        self.assertEqual(result['declaration']['inputCode'], 4)
        self.assertEqual(result['declaration']['family'], 'span')
        self.assertEqual(result['evidence']['nativeExposure'], provenance['nativeExposure'])
        self.assertEqual(self.cell['role'], 'blind')

    def test_blind_baseline_is_measured_from_its_own_first_image_on_the_same_masks(self):
        self.first[:] = 128
        baseline = dict(self.receipt, lane='current')
        with patch.object(S.B, 'blind_cell', return_value=(self.cell, {}, self.base, {})), \
             patch.object(S.M.R, 'read_verified_frame', return_value=self.background):
            result = self.reader.measure_member(self.run, baseline, self.blind_rows())
        self.assertEqual(result['statistics']['T1-full-silhouette']['runValues'], [0, 0, 0])
        self.assertEqual(result['statistics']['deep8-channel-median']['value'], [128, 128, 128])

    def test_blind_helper_refuses_wrong_phase_and_changed_original_statistic_membership(self):
        with patch.object(S.B, 'blind_cell', return_value=(self.cell, {}, self.base, {})) as authority:
            self.context['phase'] = 'gate'
            with self.assertRaises(ValueError): self.reader.blind(self.run, self.receipt, self.blind_rows())
            authority.assert_not_called()
            self.context['phase'] = 'exposure'
            with self.assertRaises(ValueError): self.reader.blind(self.run, self.receipt, self.blind_rows()[:-1])

    def test_blind_envelope_keeps_true_runs_role_claim_chain_and_has_no_exposed_batch(self):
        artifact = {'nativeRead': {'path': str(self.output/'native.json'), 'sha256': 'f'*64},
                    'export': {'path': str(self.output/'role-export'), 'indexSha256': 'e'*64}}
        artifact_pin = write(self.output/'artifacts.json', artifact)
        measured = {'nativeCell': self.cell, 'evidence': {'nativeExposure': artifact_pin,
                                                        'nativeRead': artifact['nativeRead']}}
        row = self.blind_rows()[0]
        envelope = self.reader.blind_envelope(row, measured)
        self.assertEqual(envelope['runs'], [r['evidence'] for r in self.cell['runs']])
        self.assertEqual(envelope['role'], 'blind'); self.assertNotIn('nativeBatch', envelope)
        self.assertEqual(envelope['nativeExposure'], artifact_pin)
        self.assertEqual(envelope['nativeExport']['role'], 'blind')
        self.assertEqual(envelope['support'], row['support'])
        with self.assertRaises(ValueError): self.reader.blind_envelope(dict(row, role='validation'), measured)

    def canonical_fixture(self, name, *, text=False):
        self.run['sceneSource'] = 'canonical'; self.receipt['sceneSource'] = 'canonical'
        native_pin = write(self.base/'native.png', png(self.native))
        background_pin = write(self.base/'background.png', png(self.background))
        current_pin = write(self.base/'current.png', png(np.full_like(self.native, 128)))
        scene = {'id': self.scene, 'background': 'background', 'component': 'rectangle', 'state': 'rest'}
        doc = {'canvas': self.canvas, 'scenes': [scene], 'components': {'rectangle': self.component},
               'backgrounds': {'background': {'kind': 'solid'}}}
        scenes_pin = write(self.base/'canonical-scenes.json', doc)
        self.plan.update(components=doc['components'], scenes=[scene], scheme='dark')
        self.spec = scene
        published = S.R.M.canonical_read(self.native, self.background, self.component,
            self.canvas, 1, web_rgb=np.full_like(self.native, 128), text=text)
        evidence = S.R.M.evidence_reading(published, [published]*7)
        row = {'profile': self.profile, 'renderer': 'webgpu', 'scene': self.scene,
            'statistic': name, 'role': 'gate', 'support': 'Original canonical prose.',
            'currentGeneration': 'frozen', 'currentDocumentPair': {'active.dark': 'a'*64, 'receded.dark': 'b'*64},
            'historical': [], 'nativeEvidence': native_pin, 'currentEvidence': current_pin}
        report = dict(row, reference=copy.deepcopy(row), status='MEASURED', readings=evidence,
            publishedReading=published, pins={'native': native_pin, 'background': background_pin,
                'current': current_pin, 'currentMetadata': None, 'scenes': scenes_pin})
        self.reader.canonical = {tuple(row[k] for k in S.KEY): report}
        self.reader.config = {'canonicalReferenceEvidence': {'path': str(self.base/'report.json'), 'sha256': 'c'*64}}
        self.reader.authenticate = lambda *a: (self.plan, self.spec, {'png': png(self.first)}, self.evidence.copy())
        return row, report, scenes_pin

    def test_canonical_candidate_uses_first_image_and_original_native_mask_without_rebasing_current(self):
        row, report, scenes_pin = self.canonical_fixture('T1-full-silhouette')
        frozen = copy.deepcopy(report)
        with patch.object(S.C, 'SCENES', Path(scenes_pin['path'])):
            result = self.reader.canonical_member(self.run, self.receipt, [row])
        self.assertEqual(result['statistics']['T1-full-silhouette']['value'], .5)
        self.assertEqual(result['statistics']['T1-full-silhouette']['nativeValue'], 0)
        current, _ = self.reader.current_measurement(row, name='T1-full-silhouette')
        self.assertEqual(current['value'], 0)
        self.assertEqual(report, frozen)
        self.assertEqual(result['statistics']['T1-full-silhouette']['nativeImage'], row['nativeEvidence'])

    def test_canonical_text_retains_low_and_fine_independently_and_compound_key_is_not_flattened(self):
        row, _, scenes_pin = self.canonical_fixture('T1-low', text=True)
        with patch.object(S.C, 'SCENES', Path(scenes_pin['path'])):
            result = self.reader.canonical_member(self.run, self.receipt, [row])
        self.assertIn('T1-low', result['statistics']); self.assertIn('T1-fine', result['statistics'])
        self.assertNotEqual(result['statistics']['T1-low']['value'], result['statistics']['T1-fine']['value'])
        self.assertEqual(result['statistics']['T1-low']['support'], 'eroded4')
        row, _, scenes_pin = self.canonical_fixture('low-end-path-level')
        with patch.object(S.C, 'SCENES', Path(scenes_pin['path'])):
            result = self.reader.canonical_member(self.run, self.receipt, [row])
        self.assertEqual(row['statistic'], 'low-end-path-level')
        self.assertEqual(result['declaration']['family'], 'solid')
        self.assertEqual(result['statistics']['deep8-channel-median']['value'], [127.5]*3)

    def frozen_fixture(self, name, *, text=False):
        row, report, scenes_pin = self.canonical_fixture(name, text=text)
        profile = 'apple-macos-27.0-1x-dark-standard-glass0.25'
        row.update(profile=profile, native=0., current=0., B=.01)
        report.update(profile=profile, reference=copy.deepcopy(row))
        self.run['profile'] = profile; self.receipt['profile'] = profile
        self.reader.canonical = {tuple(row[k] for k in S.KEY): report}
        self.receipt['matrix'] = write(self.output/'matrix.json', {'synthetic': 'authenticated matrix'})
        self.receipt['row'] = {'material': {'interiorStdDevWeb': {'value': .49, 'units': 'luminance'}}}
        self.evidence['capture'] = {'path': str(self.output/'first.png'), 'sha256': 'd'*64}
        return row, report, scenes_pin

    def test_frozen_full_t1_keeps_authenticated_production_value_separate_from_numpy(self):
        row, report, scenes_pin = self.frozen_fixture('T1-full-silhouette')
        original = copy.deepcopy(row)
        with patch.object(S.C, 'SCENES', Path(scenes_pin['path'])):
            result = self.reader.canonical_member(self.run, self.receipt, [row])
        reading = result['statistics']['T1-full-silhouette']
        self.assertEqual(reading['value'], .5)
        owned = reading['productionStatistic']
        self.assertEqual(owned['value'], .49)
        self.assertEqual(owned['estimator'], 'PRODUCTION_TS_INTERIOR_LEVEL')
        self.assertEqual(owned['field'], 'material.interiorStdDevWeb')
        self.assertEqual(owned['capture'], self.evidence['capture'])
        self.assertEqual(owned['matrix'], self.receipt['matrix'])
        self.assertEqual(owned['reading'], 'first'); self.assertEqual(row, original)
        self.assertEqual(report['reference'], original)

    def test_frozen_text_keeps_original_gaussian_producer_and_never_borrows_full_matrix_metric(self):
        row, _, scenes_pin = self.frozen_fixture('T1-low', text=True)
        with patch.object(S.C, 'SCENES', Path(scenes_pin['path'])):
            result = self.reader.canonical_member(self.run, self.receipt, [row])
        low = result['statistics']['T1-low']
        self.assertEqual(low['productionStatistic']['value'], low['value'])
        self.assertEqual(low['productionStatistic']['estimator'], 'CANONICAL_NUMPY_GAUSSIAN_LOW')
        self.assertNotEqual(low['value'], .49)
        self.assertNotIn('productionStatistic', result['statistics']['T1-fine'])

    def test_frozen_production_field_wrong_units_refuses_and_absent_metric_stays_unmeasured(self):
        row, _, scenes_pin = self.frozen_fixture('T1-full-silhouette')
        self.receipt['row']['material']['interiorStdDevWeb']['units'] = 'encoded-luma-codes'
        with patch.object(S.C, 'SCENES', Path(scenes_pin['path'])):
            with self.assertRaises(ValueError): self.reader.canonical_member(self.run, self.receipt, [row])
        self.receipt['row']['material'] = None
        with patch.object(S.C, 'SCENES', Path(scenes_pin['path'])):
            result = self.reader.canonical_member(self.run, self.receipt, [row])
        self.assertIsNone(result['statistics']['T1-full-silhouette']['productionStatistic']['value'])
        self.assertEqual(result['statistics']['T1-full-silhouette']['value'], .5)

    def test_canonical_pinned_support_witness_mismatch_stops_instead_of_substituting_web_support(self):
        row, report, scenes_pin = self.canonical_fixture('T1-full-silhouette')
        report['publishedReading']['supports']['full-silhouette']['pixels'] += 1
        with patch.object(S.C, 'SCENES', Path(scenes_pin['path'])):
            with self.assertRaisesRegex(ValueError, 'support'):
                self.reader.canonical_member(self.run, self.receipt, [row])


if __name__ == '__main__':
    unittest.main()
