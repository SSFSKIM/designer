"""Generated arrays/temporary artifacts exercise the new source wrappers, not real capture trees."""
import copy
import hashlib
import io
import json
from pathlib import Path
import sys
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
        self.reader.dispatcher = types.SimpleNamespace(require_read_admission=lambda *a, **k: None)
        # A ready native checkpoint (readiness.native_readiness's metadata); not-ready reads are
        # exercised against the real preparation chain in test_readiness.py.
        self.reader._readiness = {'ready': True, 'stops': [],
            'artifactManifest': {'path': str(self.output/'native-blind/artifacts.json'), 'sha256': 'e'*64},
            'nativeRead': {'path': str(self.output/'native-blind/native-read.json'), 'sha256': 'f'*64}}
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
             patch.object(S.PhaseSources, 'verify_repeat', return_value={'reading': 'first'}) as verify:
            _, _, blobs, evidence = S.PhaseSources.authenticate(self.reader, self.run, self.receipt)
        verify.assert_called_once_with(self.run, self.receipt)
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
             patch.object(S.PhaseSources, 'verify_repeat', side_effect=ValueError('second-page source refusal')):
            with self.assertRaisesRegex(ValueError, 'second-page'):
                S.PhaseSources.authenticate(self.reader, self.run, self.receipt)
        Path(self.receipt['artifacts']['png']['path']).write_bytes(png(np.zeros_like(self.first)))
        with patch.object(S.W, 'scene_plan', return_value=self.plan), \
             patch.object(S.PhaseSources, 'verify_repeat') as verify:
            with self.assertRaisesRegex(ValueError, 'Changed'):
                S.PhaseSources.authenticate(self.reader, self.run, self.receipt)
        verify.assert_not_called()

    def test_blind_wrapper_reuses_actual_chain_and_three_different_native_t1_masks(self):
        rows = self.blind_rows()
        provenance = {'nativeExposure': {'path': str(self.output/'artifacts.json'), 'sha256': 'e'*64},
                      'nativeRead': {'path': str(self.output/'native.json'), 'sha256': 'f'*64}}
        with patch.object(S.BR, 'blind_cell', return_value=(self.cell, {'synthetic': 'dependency'},
                                                          self.base, provenance)) as authority, \
             patch.object(S.M.R, 'read_verified_frame', return_value=self.background):
            result = self.reader.measure_member(self.run, self.receipt, rows)
        authority.assert_called_once_with(self.context, self.run, rows[0], self.reader.scenes,
                                          self.reader._readiness)
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
        with patch.object(S.BR, 'blind_cell', return_value=(self.cell, {}, self.base, {})), \
             patch.object(S.M.R, 'read_verified_frame', return_value=self.background):
            result = self.reader.measure_member(self.run, baseline, self.blind_rows())
        self.assertEqual(result['statistics']['T1-full-silhouette']['runValues'], [0, 0, 0])
        self.assertEqual(result['statistics']['deep8-channel-median']['value'], [128, 128, 128])

    def test_a_not_ready_checkpoint_stops_only_the_statistics_it_names_on_this_cell(self):
        """DL5n: the blind reader hands the evaluator exactly this cell's checkpointed stops."""
        stop = {'cell': self.cell['id'], 'statistic': 'deep8-channel-median', 'reason': 'NATIVE_SPREAD_EXCEEDS_ONE_CODE'}
        elsewhere = dict(stop, cell='synthetic/other', statistic='central8-channel-median')
        self.reader._readiness = dict(self.reader._readiness, ready=False, stops=[stop, elsewhere])
        with patch.object(S.BR, 'blind_cell', return_value=(self.cell, {}, self.base, {})) as authority, \
             patch.object(S.M.R, 'read_verified_frame', return_value=self.background):
            result = self.reader.measure_member(self.run, self.receipt, self.blind_rows())
        self.assertIs(authority.call_args.args[4], self.reader._readiness)
        stopped = result['statistics']['deep8-channel-median']
        self.assertEqual((stopped['measurementStatus'], stopped['reason'], stopped['value']),
                         ('UNMEASURED', 'NATIVE_NOT_READY', None))
        self.assertEqual(stopped['nativeRuns'], [r['evidence'] for r in self.cell['runs']])
        self.assertEqual({n: s['measurementStatus'] for n, s in result['statistics'].items() if n != stop['statistic']},
                         {n: 'MEASURED' for n in self.cell['statistics'] if n != stop['statistic']})

    def test_typed_blind_evidence_reads_through_the_native_checkpoint(self):
        manifest = write(self.base/'manifest.json', {'synthetic': 'manifest'})
        checker = self.reader.native_evidence(manifest)
        self.assertEqual(type(checker).__name__, 'NativeEvidence')
        self.reader._readiness = dict(self.reader._readiness, ready=False, stops=[
            {'cell': self.cell['id'], 'statistic': 'deep8-channel-median', 'reason': 'NATIVE_SPREAD_EXCEEDS_ONE_CODE'}])
        checker = self.reader.native_evidence(manifest)
        self.assertEqual((type(checker).__name__, type(checker).__mro__[1].__name__),
                         ('CheckpointedNativeEvidence', 'NativeEvidence'))
        self.assertEqual(checker.manifest_pin, manifest)

    def test_blind_helper_refuses_wrong_phase_and_changed_original_statistic_membership(self):
        with patch.object(S.BR, 'blind_cell', return_value=(self.cell, {}, self.base, {})) as authority:
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

    def impulse_companions(self, scale, component, state):
        """Canonical ml/lg geometry with generated pixels only; both records carry all seven reads."""
        self.canvas = {'width': 320, 'height': 200}
        self.component = {'kind': 'rrect', **({'size': [224, 128], 'radius': 27}
            if component == 'rrect-ml' else {'size': [280, 160], 'radius': 34})}
        self.scene = f'impulse__{component}__{state}'
        self.profile = f'apple-macos-27.0-{scale}x-dark-standard-glass0.25'
        shape = (200*scale, 320*scale)
        yy, xx = np.indices(shape)
        self.background = np.zeros((*shape, 3), dtype=np.uint8)
        dots = (yy % (64*scale) < 4*scale) & (xx % (64*scale) < 4*scale)
        self.background[dots] = 255
        path = S.R.M.S.P.signed_distance(self.component, self.canvas, scale, shape) <= 0
        self.native = self.background.copy()
        self.native[path] = 64 if state == 'rest' else 32
        self.native[path & (xx >= 160*scale)] = 128 if state == 'rest' else 96
        self.first = self.background.copy(); self.first[path] = 32
        self.first[path & (xx >= 160*scale)] = 192
        current = self.background.copy(); current[path] = 96
        pins = {name: write(self.base/(name+'.png'), png(rgb)) for name, rgb in
                (('native', self.native), ('background', self.background), ('current', current))}
        scene = {'id': self.scene, 'background': 'impulse', 'component': component, 'state': state}
        doc = {'canvas': self.canvas, 'scenes': [scene], 'components': {component: self.component},
               'backgrounds': {'impulse': {'kind': 'impulse'}}}
        scenes_pin = write(self.base/'impulse-scenes.json', doc)
        pins.update(scenes=scenes_pin, currentMetadata=None)
        self.plan = {'dpr': scale, 'position': .25, 'canvas': self.canvas,
                     'components': doc['components'], 'scenes': [scene], 'scheme': 'dark'}
        self.run.update(sceneSource='canonical', profile=self.profile, scenes=[self.scene])
        self.receipt.update(sceneSource='canonical', profile=self.profile, scene=self.scene,
            matrix=write(self.output/'matrix.json', {'synthetic': 'authenticated first matrix'}),
            row={'material': {'interiorStdDevWeb': {'value': .49, 'units': 'luminance'}}})
        self.evidence['capture'] = write(self.output/'first.png', png(self.first))
        self.reader.authenticate = lambda *a: (self.plan, scene, {'png': png(self.first)}, self.evidence.copy())
        published = S.R.M.canonical_read(self.native, self.background, self.component,
            self.canvas, scale, web_rgb=current, impulse=True)
        readings = S.R.M.evidence_reading(published, [published]*7)
        rows, reports = [], []
        for name in ('T1-full-silhouette', 'low-end-path-level'):
            row = {'profile': self.profile, 'renderer': 'webgpu', 'scene': self.scene,
                'statistic': name, 'role': 'gate', 'support': 'Original impulse support prose.',
                'native': .13, 'current': .17, 'B': .01, 'currentGeneration': 'synthetic-frozen',
                'currentDocumentPair': {'active.dark': 'a'*64, 'receded.dark': 'b'*64},
                'historical': [], 'nativeEvidence': pins['native'], 'currentEvidence': pins['current']}
            report = dict(row, reference=copy.deepcopy(row), status='MEASURED',
                readings=copy.deepcopy(readings), publishedReading=copy.deepcopy(published),
                pins=copy.deepcopy(pins))
            rows.append(row); reports.append(report)
        self.reader.canonical = {tuple(r[k] for k in S.KEY): r for r in reports}
        self.reader.config = {'canonicalReferenceEvidence': {'path': str(self.base/'report.json'), 'sha256': 'c'*64}}
        return rows, reports, scenes_pin

    def impulse_source_reading(self, row, measured):
        current, evidence = self.reader.current_measurement(row, name=row['statistic'])
        return S.Q.reading(measured['statistics'][row['statistic']], current,
            measured['evidence'], evidence, reported=False, eligible_empty=False)

    def test_impulse_companions_preserve_first_image_producer_and_all_diagnostics_in_both_orders(self):
        """DL5r(a): a later path companion must not erase the full-T1 producer binding."""
        names = {'T1-full-silhouette', 'deep8-luma-mean', 'deep8-luma-median',
                 'deep8-channel-median', 'deep8-far24-luma-mean', 'deep8-far24-luma-median',
                 'deep8-far24-channel-median'}
        inventory = {'path': '/synthetic/original-inventory.json', 'sha256': 'e'*64}
        for scale in (1, 2):
            for component in ('rrect-ml', 'rrect-lg'):
                for state in ('rest', 'inactive'):
                    rows, reports, scenes_pin = self.impulse_companions(scale, component, state)
                    frozen_rows, frozen_reports = copy.deepcopy(rows), copy.deepcopy(reports)
                    for report in reports: self.assertEqual(set(report['readings']), names)
                    with patch.object(S.C, 'SCENES', Path(scenes_pin['path'])):
                        alone = self.reader.canonical_member(self.run, self.receipt, [rows[0]])
                        companion = self.reader.canonical_member(self.run, self.receipt, [rows[1]])
                        for order in (rows, rows[::-1]):
                            with self.subTest(scale=scale, component=component, state=state,
                                              order=[r['statistic'] for r in order]):
                                measured = self.reader.canonical_member(self.run, self.receipt, order)
                                source_reading = self.impulse_source_reading(rows[0], measured)
                                owned = measured['statistics']['T1-full-silhouette'].get('productionStatistic')
                                primary = S.Q.frozen_primary(rows[0], reports[0]['reference'],
                                    source_reading, owned, inventory)
                                expected = {'estimator': 'PRODUCTION_TS_INTERIOR_LEVEL',
                                    'statistic': 'T1-full-silhouette',
                                    'producer': 'packages/calibration/src/metrics/material.ts#interiorLevel',
                                    'field': 'material.interiorStdDevWeb', 'reading': 'first',
                                    'capture': self.evidence['capture'], 'matrix': self.receipt['matrix'],
                                    'scene': self.scene, 'units': 'linear-luma', 'value': .49}
                                self.assertEqual(owned, expected)
                                self.assertEqual(owned, alone['statistics']['T1-full-silhouette']['productionStatistic'])
                                diagnostics = copy.deepcopy(measured['statistics'])
                                del diagnostics['T1-full-silhouette']['productionStatistic']
                                baseline = copy.deepcopy(alone['statistics'])
                                del baseline['T1-full-silhouette']['productionStatistic']
                                self.assertEqual(set(diagnostics), names)
                                self.assertEqual(diagnostics, baseline)
                                self.assertEqual(diagnostics, companion['statistics'])
                                self.assertEqual(primary['sourceReading'], source_reading)
                                self.assertEqual((primary['native'], primary['current'], primary['candidate']),
                                                 (.13, .17, .49))
                                self.assertEqual(primary['evidence']['candidate']['productionStatistic'], expected)
                    self.assertEqual(rows, frozen_rows); self.assertEqual(reports, frozen_reports)

    def test_carried_impulse_producer_still_refuses_wrong_identity_units_and_capture(self):
        rows, reports, scenes_pin = self.impulse_companions(1, 'rrect-ml', 'rest')
        inventory = {'path': '/synthetic/original-inventory.json', 'sha256': 'e'*64}
        with patch.object(S.C, 'SCENES', Path(scenes_pin['path'])):
            for order in (rows, rows[::-1]):
                measured = self.reader.canonical_member(self.run, self.receipt, order)
                reading = self.impulse_source_reading(rows[0], measured)
                owned = measured['statistics']['T1-full-silhouette']['productionStatistic']
                for field, value in (('producer', 'another-producer'), ('units', 'encoded-luma-codes'),
                                     ('capture', {'path': '/synthetic/second.png', 'sha256': 'f'*64}),
                                     ('statistic', 'T1-low'), ('reading', 'second'), ('missing', None)):
                    with self.subTest(order=[r['statistic'] for r in order], field=field):
                        bad = None if field == 'missing' else dict(copy.deepcopy(owned), **{field: value})
                        with self.assertRaises(ValueError):
                            S.Q.frozen_primary(rows[0], reports[0]['reference'], reading, bad, inventory)

    def test_absent_first_image_metric_survives_impulse_companions_as_unmeasured_in_both_orders(self):
        rows, reports, scenes_pin = self.impulse_companions(2, 'rrect-lg', 'inactive')
        self.receipt['row']['material'] = None
        inventory = {'path': '/synthetic/original-inventory.json', 'sha256': 'e'*64}
        with patch.object(S.C, 'SCENES', Path(scenes_pin['path'])):
            for order in (rows, rows[::-1]):
                with self.subTest(order=[r['statistic'] for r in order]):
                    measured = self.reader.canonical_member(self.run, self.receipt, order)
                    source_reading = self.impulse_source_reading(rows[0], measured)
                    owned = measured['statistics']['T1-full-silhouette'].get('productionStatistic')
                    primary = S.Q.frozen_primary(rows[0], reports[0]['reference'],
                        source_reading, owned, inventory)
                    self.assertIsNone(owned['value']); self.assertIsNone(primary['candidate'])
                    self.assertEqual(primary['candidateMeasurementStatus'], 'UNMEASURED')
                    self.assertEqual(primary['sourceReading'], source_reading)
                    self.assertIsNotNone(source_reading['candidate'])

    def test_canonical_pinned_support_witness_mismatch_stops_instead_of_substituting_web_support(self):
        row, report, scenes_pin = self.canonical_fixture('T1-full-silhouette')
        report['publishedReading']['supports']['full-silhouette']['pixels'] += 1
        with patch.object(S.C, 'SCENES', Path(scenes_pin['path'])):
            with self.assertRaisesRegex(ValueError, 'support'):
                self.reader.canonical_member(self.run, self.receipt, [row])


FIXTURES = source(HERE/'test_capture.py', 'w50_phase_source_capture_fixtures')
CURRENT3 = HERE.parents[1]/'2026-10-08-w50-g1-current3'


class LiveRepeatTests(unittest.TestCase):
    def test_repeat_verification_is_the_archived_replay_over_both_paired_transports(self):
        reader = S.PhaseSources.__new__(S.PhaseSources)
        reader.context = {'synthetic': 'context'}; reader.dispatcher = types.SimpleNamespace()
        receipt = {'repeatPair': {'path': '/p', 'sha256': 'a'*64}, 'repeatAdmission': {'path': '/q', 'sha256': 'b'*64}}
        with patch.object(S.L, 'archived_pair', return_value={'reading': 'first'}) as replay:
            self.assertEqual(reader.verify_repeat({'run': 1}, receipt), {'reading': 'first'})
        replay.assert_called_once_with(reader.context, reader.dispatcher, {'run': 1}, receipt,
                                       {'canonical': S.C, 'w50': S.W})
        for field in ('repeatPair', 'repeatAdmission'):
            with self.subTest(field=field), patch.object(S.L, 'archived_pair') as replay:
                with self.assertRaisesRegex(ValueError, 'repeat receipts'):
                    reader.verify_repeat({}, {k: v for k, v in receipt.items() if k != field})
                replay.assert_not_called()


class CurrentEvidenceTests(unittest.TestCase):
    """The LIVE root names composed schema-2 current evidence; no singular current instrument."""
    def setUp(self):
        t = tempfile.TemporaryDirectory(); self.addCleanup(t.cleanup)
        self.repo = Path(t.name).resolve()
        self.scenes = write(self.repo/'scenes.json', {'synthetic': 'scenes'})
        self.manifest = write(self.repo/'manifest.json', {'synthetic': 'manifest'})
        self.batch = write(self.repo/'batch.json', {'schema': 'w50-native-read-batch-1',
            'inputs': {'scenes': self.scenes, 'manifest': self.manifest}})
        self.reports = {r: write(self.repo/(r+'.json'), {'role': r}) for r in ('calibration', 'validation')}
        self.references = write(self.repo/'references.json', {'cells': []})
        self.composition = write(self.repo/'composition.json', {'synthetic': 'composition'})
        self.canonical = write(self.repo/'canonical.json', {'schema': 'w50-canonical-reference-evidence-1', 'partitions': {}})
        self.current_doc = {'schema': 'w50-completed-current-evidence-2', 'status': 'EVIDENCE_ONLY',
            'currentComposition': self.composition, 'originals': {'references': self.references, 'scenes': self.scenes},
            'native': {'batch': self.batch, 'reports': self.reports, 'instrument': {'path': 'i', 'sha256': 'c'*64}},
            'referenceEvidence': []}
        self.config = {'completedCurrentEvidence': None, 'canonicalReferenceEvidence': self.canonical,
                       'native': {'batch': self.batch, 'scenes': self.scenes, 'reports': self.reports}}

    def build(self, mutate=None, root_change=None):
        doc = copy.deepcopy(self.current_doc)
        if mutate: mutate(doc)
        current = write(self.repo/'current.json', doc)
        config = dict(self.config, completedCurrentEvidence=current)
        inputs = [current, self.canonical, self.scenes, self.batch, *self.reports.values()]
        root = {'inputs': inputs, 'references': self.references, 'manifest': self.manifest,
                'currentEvidence': current, 'currentComposition': self.composition, **(root_change or {})}
        context = {'repo': str(self.repo), 'output': str(self.repo), 'executionRoot': 'root', 'inputs': inputs}
        live = types.SimpleNamespace(require_context=lambda c: None, sealed=lambda p: root,
                                     checked=lambda repo, pin: Path(pin['path']))
        with patch.dict(sys.modules, {'w50_g1_dispatch': live}):
            return S.PhaseSources(context, root, config)

    def test_composed_root_evidence_is_admitted(self):
        self.assertEqual(self.build().current, {})

    def test_singular_foreign_or_mismatched_current_evidence_refuses(self):
        mutations = {
            'schema1': lambda d: d.update(schema='w50-completed-current-evidence-1'),
            'singular': lambda d: d.update(currentInstrument={'path': 'x', 'sha256': 'd'*64}),
            'composition': lambda d: d.update(currentComposition=self.canonical),
            'references': lambda d: d['originals'].update(references=self.canonical),
            'scenes': lambda d: d['originals'].update(scenes=self.canonical),
            'native-batch': lambda d: d['native'].update(batch=self.canonical),
            'native-reports': lambda d: d['native']['reports'].update(validation=self.canonical),
            'status': lambda d: d.update(status='PASS')}
        for name, mutation in mutations.items():
            with self.subTest(change=name), self.assertRaisesRegex(ValueError, 'composed current evidence'):
                self.build(mutation)
        with self.assertRaisesRegex(ValueError, 'composed current evidence'):
            self.build(root_change={'currentEvidence': self.canonical})


class ExposedEquivalenceTests(unittest.TestCase):
    """measure_exposed is capture.measure_capture on the member's own run, nothing else."""
    def setUp(self):
        self.m = S.M
        FIXTURES.CaptureTests.setUp(self)
        folder = self.scratch/'captures'/FIXTURES.SCENE
        self.receipt['repeatPair'] = FIXTURES.write_pin(folder/'repeat__webgpu.json', {'synthetic': 'pair'})
        self.receipt['repeatAdmission'] = FIXTURES.write_pin(folder/'repeat-admission__webgpu.json', {'synthetic': 'proof'})
        self.proof = {'schema': 'w50-repeat-admission-1', 'synthetic': True}
        self.reads = []
        self.live = types.SimpleNamespace(require_context=lambda c: None, sealed=self.dispatcher.sealed,
            checked=self.dispatcher.checked,
            require_read_admission=lambda c, run, current=False: self.reads.append((run['captureRoot'], current)))

    def original(self):
        with patch.object(S.M, 'verify_live_repeat', return_value=self.proof):
            return S.M.measure_capture(self.context, self.native_report, self.receipt, self.scenes,
                                       native_batch_pin=self.native_batch)

    def live_read(self, run):
        calls = []
        result = S.measure_exposed(self.context, self.live, run, self.native_report, self.receipt, self.scenes,
            native_batch_pin=self.native_batch, verify_repeat=lambda r, rc: calls.append((r, rc)) or self.proof)
        self.assertEqual(calls, [(run, self.receipt)])
        return result

    def test_same_statistics_arguments_and_evidence_as_the_original_reader(self):
        original = self.original()
        self.assertEqual(self.live_read(copy.deepcopy(self.run)), original)
        self.assertEqual(self.reads, [(self.run['captureRoot'], False)])
        self.assertEqual(original['evidence']['repeatAdmission'], self.receipt['repeatAdmission'])

    def test_a_per_member_root_is_unreadable_by_the_original_and_read_identically_here(self):
        """LIVE's lifecycle gives each member its own captureRoot: why the original cannot be wrapped."""
        expected = self.original()
        member = dict(self.run, captureRoot=str(self.scratch/'attempts/000001/quarantine/member/captures'))
        source_dir = self.scratch/'captures'/FIXTURES.SCENE
        target = Path(member['captureRoot'])/FIXTURES.SCENE; target.mkdir(parents=True)
        for name in ('png', 'report', 'cell'):
            old = Path(self.artifacts[name]['path']); new = target/old.name
            new.write_bytes(old.read_bytes()); self.artifacts[name] = dict(self.artifacts[name], path=str(new))
        with self.assertRaisesRegex(ValueError, 'Artifact path differs'):
            self.original()
        result = self.live_read(member)
        for key in ('capture', 'report', 'cell'):
            expected['evidence'][key] = self.artifacts[{'capture': 'png'}.get(key, key)]
        for argument in expected['arguments']:
            argument['provenance'].update(report=self.artifacts['report'], capture=self.artifacts['png'])
        self.assertEqual(result, expected)

    def test_live_member_refusals_precede_any_pixel_decode(self):
        changes = {'foreign-run': lambda run: dict(run, candidate={'path': 'other', 'sha256': 'f'*64}),
                   'wrong-root': lambda run: dict(run, captureRoot=str(self.scratch/'elsewhere')),
                   'unregistered': None}
        for name, change in changes.items():
            with self.subTest(change=name), \
                    patch.object(S.M.R.S, 'decode_png', side_effect=AssertionError('decode')):
                inputs = self.context['inputs']
                if change is None: self.context['inputs'] = []
                with self.assertRaises(ValueError):
                    self.live_read((change or (lambda r: r))(copy.deepcopy(self.run)))
                self.context['inputs'] = inputs
        with patch.object(S.M.R.S, 'decode_png', side_effect=AssertionError('decode')):
            with self.assertRaisesRegex(ValueError, 'verification'):
                S.measure_exposed(self.context, self.live, self.run, self.native_report, self.receipt, self.scenes,
                    native_batch_pin=self.native_batch,
                    verify_repeat=lambda *a: (_ for _ in ()).throw(ValueError('pair verification refused')))


class FakeEvidence:
    """Stand-in for current3 NativeEvidence: only the identity calls DL5g's loop makes."""
    log = []
    def __init__(self, repo, manifest): self.repo = Path(repo); FakeEvidence.log.append(('init', manifest['path']))
    def path(self, pin):
        if not isinstance(pin, dict): raise ValueError('Missing synthetic pin')
        path = Path(pin['path']); path = path if path.is_absolute() else self.repo/path
        if hashlib.sha256(path.read_bytes()).hexdigest() != pin['sha256']: raise ValueError('Changed synthetic pin')
        return path.resolve()
    def read(self, pin): return json.loads(self.path(pin).read_text())
    def check(self, pin): return self.path(pin)
    def png(self, pin, dimensions): FakeEvidence.log.append(('png', dimensions))
    def validate(self, row, pin, exposure=None): FakeEvidence.log.append(('validate', row['statistic']))
    def finish(self): FakeEvidence.log.append(('finish',))


class FakeNativeModule(types.ModuleType):
    NativeEvidence = property(lambda self: FakeEvidence)


class BlindCompletenessTests(unittest.TestCase):
    """validate_blind_rows is current3's DL5g check over the members' own runs."""
    PROFILE = 'apple-macos-27.0-1x-dark-standard-glass0.25'

    def setUp(self):
        t = tempfile.TemporaryDirectory(); self.addCleanup(t.cleanup)
        base = Path(t.name).resolve(); self.repo = base/'repo'; self.output = base/'output'
        self.repo.mkdir(); self.output.mkdir()
        self.candidate = write(self.repo/'candidate.json', {'synthetic': 'candidate'})
        self.baseline = write(self.repo/'baseline.json', {'synthetic': 'baseline'})
        self.manifest = write(self.repo/'manifest.json', {'synthetic': 'manifest'})
        statistics = ('deep8-channel-median', 'T1-full-silhouette')
        provenance = {'role': 'blind', 'support': 'Original prose.', 'nativeIdentity': self.PROFILE+'/blind',
            'referenceIdentity': self.PROFILE+'/ref', 'currentGeneration': 'g', 'currentDocumentPair': {'active.dark': 'a'*64}}
        self.cells = [dict(profile=self.PROFILE, renderer='webgpu', scene='blind', statistic=name, **provenance)
                      for name in statistics]
        self.references = write(self.repo/'references.json', {'cells': self.cells})
        self.root = {'manifest': self.manifest, 'references': self.references, 'baselineDocuments': [self.baseline]}
        self.run = {'id': 'r', 'profile': self.PROFILE, 'renderer': 'webgpu', 'sceneSource': 'w50', 'scenes': ['blind'],
            'sets': ['holdout'], 'candidate': self.candidate, 'baselineCandidate': self.baseline,
            'captureRoot': str(self.output/'unused'), 'matrixPath': str(self.output/'unused.json')}
        self.context = {'repo': str(self.repo), 'output': str(self.output), 'phase': 'exposure', 'executionRoot': 'root',
            'batch': {'phase': 'exposure', 'runs': [self.run], 'cohort': [self.candidate]}}
        self.receipts = {lane: self.receipt(lane, self.candidate if lane == 'candidate' else self.baseline)
                         for lane in ('candidate', 'current')}
        self.rows = [dict(cell, nativeEvidence={'path': 'native.json', 'sha256': 'e'*64},
                          candidateCapture=copy.deepcopy(self.receipts['candidate']),
                          currentCapture=copy.deepcopy(self.receipts['current'])) for cell in self.cells]
        FakeEvidence.log = []

    def receipt(self, lane, candidate):
        folder = self.output/'attempts/000001/quarantine'/lane/'captures/blind'
        metadata = {'sceneId': 'blind', 'renderer': 'webgpu', 'pixelSize': [512, 384],
                    'capturePath': 'declarationSha256='+candidate['sha256'][:12]}
        page = {'sceneId': 'blind', 'requestedRenderer': 'webgpu', 'devicePixelRatio': 1, 'materialMode': 'candidate',
                'candidateDocument': {'mode': 'candidate', 'declarationSha256': candidate['sha256'][:12]}}
        return {'profile': self.PROFILE, 'renderer': 'webgpu', 'scene': 'blind', 'lane': lane, 'candidate': candidate,
            'sceneSource': 'w50', 'artifacts': {'png': write(folder/'blind__webgpu.png', b'png'),
                'cell': write(folder/'cell__webgpu.json', metadata), 'report': write(folder/'report__webgpu.json', {'page': page})}}

    def original(self):
        V = source(CURRENT3/'execution/blind_exposure.py', 'w50_test_original_blind_exposure')
        D = source(CURRENT3/'execution/dispatch.py', 'w50_test_original_dispatch_baseline')
        permissive = types.SimpleNamespace(require_context=lambda c: None, sealed=lambda p: self.root,
            require_render_admission=lambda *a, **k: None, baseline_run=D.baseline_run)
        with patch.dict(sys.modules, {'w50_g1_dispatch': permissive}), \
                patch.object(V.importlib.util, 'module_from_spec', lambda spec: FakeNativeModule('w50_fake_native')):
            return V.validate_blind_exposure(self.context, self.rows)

    def live(self):
        reads = []
        def resolve(context, receipt):
            if receipt != self.receipts.get(receipt.get('lane')): raise ValueError('Receipt is not a source-bound complete-union member')
            member = dict(self.run, scenes=['blind'], candidate=receipt['candidate']); member.pop('baselineCandidate')
            return member
        reader = S.PhaseSources.__new__(S.PhaseSources)
        reader.context = self.context
        reader.dispatcher = types.SimpleNamespace(require_context=lambda c: None, sealed=lambda p: self.root,
            resolve_capture_run=resolve, require_read_admission=lambda c, run, current=False: reads.append((run['candidate'], current)))
        reader.native_evidence = lambda manifest: FakeEvidence(self.context['repo'], manifest)
        result = reader.validate_blind_rows(self.rows)
        self.assertEqual(reads, [(self.candidate, False), (self.baseline, True)]*len(self.rows))
        return result

    def test_same_bound_evidence_as_the_original_check(self):
        original = self.original(); original_log = FakeEvidence.log; FakeEvidence.log = []
        self.assertEqual(self.live(), original)
        self.assertEqual(FakeEvidence.log, original_log)
        self.assertEqual(original['status'], 'BOUND_BLIND_EVIDENCE')

    def test_each_original_refusal_refuses_identically(self):
        mutations = {
            'provenance': lambda rows: rows[0].update(support='changed'),
            'missing-row': lambda rows: rows.pop(),
            'duplicate-row': lambda rows: rows.append(copy.deepcopy(rows[0])),
            'lane': lambda rows: rows[0]['candidateCapture'].update(lane='current'),
            'material': lambda rows: rows[0]['currentCapture'].update(candidate=self.candidate),
            'scene': lambda rows: rows[0]['candidateCapture'].update(scene='other'),
            'outside': lambda rows: rows[0]['candidateCapture']['artifacts'].update(png=self.references),
            'cohort': lambda rows: self.context['batch'].update(cohort=[self.baseline]),
            'baseline': lambda rows: self.root.update(baselineDocuments=[])}
        for name, mutation in mutations.items():
            with self.subTest(change=name):
                saved = (copy.deepcopy(self.rows), copy.deepcopy(self.context), copy.deepcopy(self.root))
                mutation(self.rows)
                with self.assertRaises(ValueError): self.original()
                with self.assertRaises(ValueError): self.live()
                self.rows, self.context, self.root = saved

    def test_a_receipt_differing_from_its_checkpoint_refuses_before_native_evidence(self):
        self.receipts['candidate'] = dict(self.receipts['candidate'], artifacts={})
        with self.assertRaisesRegex(ValueError, 'source-bound'): self.live()
        self.assertNotIn(('validate', self.cells[0]['statistic']), FakeEvidence.log)
        self.context['phase'] = 'gate'
        with self.assertRaisesRegex(ValueError, 'exposure-only'): self.live()


if __name__ == '__main__':
    unittest.main()
