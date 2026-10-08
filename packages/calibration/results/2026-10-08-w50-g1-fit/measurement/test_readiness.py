"""DL5n / DL5m (4) on synthetic arrays and a synthetic one-shot preparation; no real native data.

The preparation chain is exposure/test_prepare.py's synthetic archive, prepared by the sealed
preparation exactly as current3 repeat/test_blind.py uses it; a not-ready read is that read with
its readiness rewritten to the native role's not-ready form (ready false, stops carrying repeat).
"""
import copy
import hashlib
import importlib.util
import inspect
import json
from pathlib import Path
import sys
import types
import unittest
from unittest.mock import patch

import numpy as np

HERE = Path(__file__).resolve().parent
FIT = HERE.parent
CURRENT3 = FIT.parent/'2026-10-08-w50-g1-current3'
CANARY = 987.654321
CANARY_TEXT = '987.654321'


def source(path, name):
    module = types.ModuleType(name); module.__file__ = str(path)
    exec(compile(Path(path).read_bytes(), str(path), 'exec', dont_inherit=True), module.__dict__)
    return module


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec); sys.modules[name] = module
    spec.loader.exec_module(module); return module


RD = source(HERE/'readiness.py', 'w50_readiness_tests')
Q = source(HERE/'projection.py', 'w50_readiness_projection_tests')
SEALED = source(HERE/'capture.py', 'w50_readiness_sealed_evaluator')
TC = source(HERE/'test_capture.py', 'w50_readiness_capture_fixtures')
COMPONENT = {'kind': 'rrect', 'size': [168, 96], 'radius': 20.4}


def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def silhouette(*, empty):
    mask = np.zeros((384, 512), dtype=bool)
    if not empty: mask[180, 200:202] = True
    return mask


def structured(empties, *, reported):
    """test_capture's structured impulse cell with a chosen silhouette per run."""
    cell, masks, background = TC.native_cell(empty=True)
    rgb = np.full((384, 512, 3), 70, dtype=np.uint8)
    for run, empty in zip(cell['runs'], empties):
        run['readings'] = TC.R.S.read_frame(rgb, background, COMPONENT, TC.CANVAS, 1, impulse=True,
            include_structured=True, silhouette_mask=silhouette(empty=empty))
    cell['statistics'] = TC.R.aggregate_runs(cell['runs'], reported=reported)
    return cell, masks


def uniform():
    background = np.full((384, 512, 3), 4, dtype=np.uint8)
    rgb = np.full((384, 512, 3), 9, dtype=np.uint8)
    runs = [dict(run=n, dependency='synthetic/ref', evidence={'sha256': str(n)*64},
                 readings=TC.R.S.read_frame(rgb, background, COMPONENT, TC.CANVAS, 1)) for n in (1, 2, 3)]
    masks = TC.R.S.analytical_masks(COMPONENT, TC.CANVAS, 1, (384, 512), background=background)
    del masks['deep8_far24']
    cell = dict(id=TC.PROFILE+'/cell-grey-004-s096__rest', profile=TC.PROFILE, scene='cell-grey-004-s096__rest',
                family='uniform', role='blind', pose='active', scale=1, runs=runs,
                statistics=TC.R.aggregate_runs(runs))
    return cell, masks


def web():
    image = np.full((384, 512, 3), [10, 20, 30], dtype=np.uint8)
    image[188:196, 252:260] = [30, 40, 50]
    image[180, 200] = 0; image[180, 201] = 255
    return image


class EvaluatorTests(unittest.TestCase):
    """readiness.evaluate_supports against the sealed capture.evaluate_native_supports."""

    def test_without_stops_or_incomplete_reported_keys_it_is_the_sealed_evaluator(self):
        cases = {'structured': (TC.native_cell()[0], TC.native_cell()[1]),
                 'eligible-style empty reported T1': structured([True]*3, reported=True),
                 'uniform': uniform()}
        for label, (cell, masks) in cases.items():
            for renderer in ('webgpu', 'css'):
                with self.subTest(label, renderer=renderer):
                    self.assertEqual(RD.evaluate_supports(web(), cell, masks, renderer=renderer),
                                     SEALED.evaluate_native_supports(web(), cell, masks, renderer=renderer))

    def test_a_stopped_statistic_is_not_computed_and_reads_native_not_ready(self):
        """A spread stop: the native aggregate still has a value and a repeat; neither travels."""
        cell, masks, _ = TC.native_cell()
        sealed = SEALED.evaluate_native_supports(web(), cell, masks, renderer='webgpu')
        cell['statistics']['deep8-channel-median'].update(value=[CANARY]*3,
            repeat={'spreadCodes': [CANARY]*3, 'passes': False})
        read = []
        original = RD.M.R.S.read_support
        def counted(rgb, mask, **kwargs):
            read.append(int(mask.sum())); return original(rgb, mask, **kwargs)
        with patch.object(RD.M.R.S, 'read_support', counted):
            result = RD.evaluate_supports(web(), cell, masks, renderer='webgpu', stopped={'deep8-channel-median'})
        stopped = result['statistics']['deep8-channel-median']
        self.assertEqual((stopped['status'], stopped['measurementStatus'], stopped['reason'], stopped['required']),
                         ('UNMEASURED', 'UNMEASURED', 'NATIVE_NOT_READY', True))
        for field in ('value', 'runValues', 'nativeValue', 'nativeRepeat'):
            self.assertIsNone(stopped[field])
        self.assertEqual(stopped['nativeSupportWitnesses'],
                         sealed['statistics']['deep8-channel-median']['nativeSupportWitnesses'])
        for name, item in result['statistics'].items():
            if name != 'deep8-channel-median': self.assertEqual(item, sealed['statistics'][name])
        self.assertEqual(len(read), 3*3)
        self.assertTrue(all('deep8' not in r['readings']['supports'] for r in result['runs']))
        self.assertTrue(all('deep8-channel-median' not in r['readings']['statistics'] for r in result['runs']))
        self.assertNotIn(CANARY_TEXT, json.dumps(result))

    def test_a_stopped_required_t1_with_no_native_silhouette_does_not_raise(self):
        cell, masks = structured([True]*3, reported=False)
        with self.assertRaisesRegex(ValueError, 'empty required native support'):
            SEALED.evaluate_native_supports(web(), cell, masks, renderer='webgpu')
        result = RD.evaluate_supports(web(), cell, masks, renderer='css', stopped={'T1-full-silhouette'})
        t1 = result['statistics']['T1-full-silhouette']
        self.assertEqual((t1['measurementStatus'], t1['reason'], t1['value']), ('UNMEASURED', 'NATIVE_NOT_READY', None))
        self.assertEqual([w['pixels'] for w in t1['nativeSupportWitnesses']], [0]*3)
        self.assertEqual(result['statistics']['deep8-channel-median']['measurementStatus'], 'MEASURED')

    def test_a_stop_names_only_a_required_statistic_and_an_unstopped_empty_required_one_still_refuses(self):
        cell, masks = structured([True]*3, reported=True)
        for stop in ({'T1-full-silhouette'}, {'T1-low'}):
            with self.subTest(stop=stop), self.assertRaisesRegex(ValueError, 'required statistic'):
                RD.evaluate_supports(web(), cell, masks, renderer='webgpu', stopped=stop)
        cell, masks = structured([True]*3, reported=False)
        with self.assertRaisesRegex(ValueError, 'empty required native support'):
            RD.evaluate_supports(web(), cell, masks, renderer='webgpu', stopped={'deep8-channel-median'})

    def test_a_reported_t1_empty_in_only_some_runs_is_an_incomplete_reading(self):
        for empties in ([True, True, False], [False, True, False]):
            with self.subTest(empties=empties):
                cell, masks = structured(empties, reported=True)
                with self.assertRaisesRegex(ValueError, 'three exact zero-support witnesses'):
                    SEALED.evaluate_native_supports(web(), cell, masks, renderer='webgpu')
                result = RD.evaluate_supports(web(), cell, masks, renderer='webgpu')
                t1 = result['statistics']['T1-full-silhouette']
                self.assertEqual((t1['status'], t1['measurementStatus'], t1['reason'], t1['required'], t1['B']),
                                 ('UNMEASURED_REPORTED', 'UNMEASURED', 'INCOMPLETE_READING', False, None))
                self.assertIsNone(t1['value'])
                self.assertEqual([w['pixels'] == 0 for w in t1['nativeSupportWitnesses']], empties)


class ProjectionTests(unittest.TestCase):
    """projection.reading maps the evaluator's two unread kinds to every side UNMEASURED."""

    def statistic(self, empties, *, reported, stopped=()):
        cell, masks = structured(empties, reported=reported)
        result = RD.evaluate_supports(web(), cell, masks, renderer='webgpu', stopped=set(stopped))
        statistic = result['statistics']['T1-full-silhouette']
        statistic['nativeRuns'] = [{'run': n, 'sha256': str(n)*64} for n in (1, 2, 3)]
        return statistic

    def evidence(self, digit):
        return {'capture': {'path': '/synthetic/first.png', 'sha256': digit*64},
                'material': {'documentPair': {'activeSha256': 'b'*64, 'recededSha256': 'c'*64}}}

    def reading(self, statistic, *, reported, eligible=False):
        return Q.reading(statistic, copy.deepcopy(statistic), self.evidence('a'), self.evidence('d'),
                         reported=reported, eligible_empty=eligible)

    def assert_unread(self, result, reason):
        self.assertEqual((result['measurementStatus'], result['reason']), ('UNMEASURED', reason))
        for side in Q.SIDES:
            self.assertIsNone(result[side])
            self.assertEqual((result[side+'MeasurementStatus'], result[side+'Reason']), ('UNMEASURED', reason))
        self.assertEqual((result['code'], result['bar'], result['B']), (None, None, None))
        self.assertNotIn('readingDefects', result)

    def test_a_stopped_required_key_reads_unmeasured_native_not_ready_on_every_side(self):
        result = self.reading(self.statistic([True]*3, reported=False, stopped={'T1-full-silhouette'}), reported=False)
        self.assert_unread(result, 'NATIVE_NOT_READY')
        self.assertFalse(result['reported'])

    def test_an_incomplete_reported_key_reads_unmeasured_incomplete_reading(self):
        partial = self.reading(self.statistic([True, True, False], reported=True), reported=True, eligible=True)
        self.assert_unread(partial, 'INCOMPLETE_READING')
        empty = self.statistic([True]*3, reported=True)
        self.assertEqual(empty['measurementStatus'], 'UNMEASURED_EMPTY_SUPPORT')
        ineligible = self.reading(empty, reported=True)
        self.assert_unread(ineligible, 'INCOMPLETE_READING')
        self.assertTrue(ineligible['reported'])

    def test_an_eligible_empty_key_keeps_its_exact_empty_support_reading(self):
        result = self.reading(self.statistic([True]*3, reported=True), reported=True, eligible=True)
        self.assertEqual((result['measurementStatus'], result['nativeMeasurementStatus'],
                          result['candidateMeasurementStatus']), ('UNMEASURED_EMPTY_SUPPORT',)*3)
        self.assertNotIn('reason', result); self.assertNotIn('nativeReason', result)
        self.assertEqual([w['pixels'] for w in result['nativeSupportWitnesses']], [0]*3)

    def test_a_stop_on_a_reported_key_or_an_incomplete_gated_key_refuses(self):
        with self.assertRaisesRegex(ValueError, 'native stop names a required key'):
            self.reading(self.statistic([True]*3, reported=False, stopped={'T1-full-silhouette'}), reported=True)
        with self.assertRaisesRegex(ValueError, 'native stop names a required key'):
            self.reading(self.statistic([True, True, False], reported=True), reported=False)


class ReadinessChainTests(unittest.TestCase):
    """The not-ready read through the actual one-shot preparation chain (synthetic archive)."""

    def setUp(self):
        old = sys.modules.get('w50_g1_dispatch')
        def restore():
            if old is None: sys.modules.pop('w50_g1_dispatch', None)
            else: sys.modules['w50_g1_dispatch'] = old
        self.addCleanup(restore)
        F = load('w50_readiness_prepare_fixture', FIT/'exposure/test_prepare.py')
        self.fixture = F.ExposureTests('test_one_shot_blind_read_keeps_original_roles_real_supports_and_hash_pinned_fixtures')
        self.fixture.setUp(); self.addCleanup(self.fixture.doCleanups)
        self.artifacts = self.fixture.prepare()
        self.context = self.fixture.context
        self.report_path = Path(self.artifacts['nativeRead']['path'])
        report = json.loads(self.report_path.read_bytes())
        self.cell = next(c for c in report['cells'] if c['family'] == 'structured')
        self.row = dict(profile=self.cell['profile'], renderer='webgpu', scene=self.cell['scene'], role='blind',
            statistic='T1-full-silhouette', nativeIdentity=self.cell['id'], referenceIdentity=self.cell['reference'],
            support='Original support prose.')
        self.run = dict(self.fixture.run, nativeExposureConfig=self.fixture.pin(self.fixture.config))
        self.sealed = source(CURRENT3/'repeat/sources.py', 'w50_readiness_sealed_blind_cell')
        self.stops = [(self.cell['id'], 'T1-full-silhouette', 'UNMEASURED_UNAUTHORISED_POPULATION'),
                      (self.cell['id'], 'deep8-channel-median', 'NATIVE_SPREAD_EXCEEDS_ONE_CODE')]

    def payload(self, artifacts, stops):
        pins = [artifacts['artifactManifest'], artifacts['claim'], artifacts['nativeRead']]
        return {'ready': not stops, 'complete': True, 'stops': stops, 'nativeExposure': artifacts, 'artifacts': pins}

    def readiness(self, payload):
        return RD.native_readiness(self.context, types.SimpleNamespace(qualification_native=lambda context: payload))

    def not_ready(self):
        """The prepared read rewritten as the native role writes a completed not-ready read: the
        report and its artifact manifest ready false, each stop with its repeat values."""
        report = json.loads(self.report_path.read_bytes())
        report['ready'] = False
        report['stops'] = [{'cell': c, 'statistic': s, 'reason': r, 'repeat': {'spreadCodes': [CANARY]*3}}
                           for c, s, r in self.stops]
        self.report_path.write_text(json.dumps(report, sort_keys=True, indent=2)+'\n')
        manifest_path = Path(self.artifacts['artifactManifest']['path'])
        manifest = json.loads(manifest_path.read_bytes())
        manifest.update(ready=False, nativeRead={'path': str(self.report_path), 'sha256': sha(self.report_path)})
        manifest_path.write_text(json.dumps(manifest, sort_keys=True, indent=2)+'\n')
        artifacts = dict(manifest, artifactManifest={'path': str(manifest_path), 'sha256': sha(manifest_path)})
        return artifacts, [{'cell': c, 'statistic': s, 'reason': r} for c, s, r in self.stops]

    def envelope(self, artifacts):
        """phase_sources.blind_envelope's typed three-run envelope for this row."""
        value = {'schema': 'w50-native-three-run-evidence-1',
            **{k: self.row[k] for k in ('profile', 'scene', 'statistic', 'nativeIdentity', 'referenceIdentity', 'role', 'support')},
            'runs': [r['evidence'] for r in self.cell['runs']], 'nativeRead': artifacts['nativeRead'],
            'nativeExposure': artifacts['artifactManifest'],
            'nativeExport': {'role': 'blind', 'root': artifacts['export']['path'], 'indexSha256': artifacts['export']['indexSha256']}}
        path = self.fixture.output/'envelope.json'; path.write_text(json.dumps(value))
        return {'path': str(path), 'sha256': sha(path)}

    def evidence(self, readiness=None):
        E = source(CURRENT3/'execution/native_evidence.py', 'w50_readiness_typed_evidence')
        base = E.NativeEvidence if readiness is None else RD.readiness_view(E.NativeEvidence, readiness)
        return base(self.context['repo'], self.fixture.pin(self.fixture.manifest_path))

    def blind_cell(self, readiness):
        return RD.blind_cell(self.context, self.run, self.row, self.fixture.scenes, readiness)

    def test_a_ready_checkpoint_reads_exactly_as_the_sealed_blind_source(self):
        readiness = self.readiness(self.payload(self.artifacts, []))
        self.assertIs(RD.readiness_view(object, readiness), object)
        self.assertEqual(self.blind_cell(readiness),
                         self.sealed.blind_cell(self.context, self.run, self.row, self.fixture.scenes))
        checker = self.evidence(readiness)
        checker.validate(self.row, self.envelope(self.artifacts), exposure=self.context); checker.finish()

    def test_a_not_ready_read_is_admitted_with_exactly_its_checkpointed_stops(self):
        artifacts, stops = self.not_ready()
        with self.assertRaises(ValueError):
            self.sealed.blind_cell(self.context, self.run, self.row, self.fixture.scenes)
        envelope = self.envelope(artifacts)
        with self.assertRaises(ValueError):
            self.evidence().validate(self.row, envelope, exposure=self.context)
        readiness = self.readiness(self.payload(artifacts, stops))
        cell, dependency, export, provenance = self.blind_cell(readiness)
        self.assertEqual(cell, self.cell)
        self.assertEqual(provenance, {'nativeExposure': artifacts['artifactManifest'], 'nativeRead': artifacts['nativeRead']})
        self.assertEqual(RD.stopped(readiness, cell['id']), {'T1-full-silhouette', 'deep8-channel-median'})
        checker = self.evidence(readiness)
        checker.validate(self.row, envelope, exposure=self.context); checker.finish()

    def test_stops_or_readiness_differing_from_the_checkpoint_refuse_without_a_value(self):
        artifacts, stops = self.not_ready()
        envelope = self.envelope(artifacts)
        other = dict(stops[0], statistic='central8-channel-median')
        cases = {'a stop missing': (artifacts, stops[:1]), 'a stop added': (artifacts, stops+[other]),
                 'another reason': (artifacts, [dict(stops[0], reason=stops[1]['reason']), stops[1]]),
                 'reordered': (artifacts, stops[::-1]),
                 # A checkpoint claiming ready over a read whose own bytes are not: the sealed checks decide.
                 'claimed ready': (dict(artifacts, ready=True), [])}
        for label, (named, listed) in cases.items():
            readiness = self.readiness(self.payload(named, listed))
            with self.subTest(label, reader='blind_cell'), self.assertRaises(ValueError) as caught:
                self.blind_cell(readiness)
            self.assertNotIn(CANARY_TEXT, str(caught.exception))
            with self.subTest(label, reader='typed evidence'), self.assertRaises(ValueError) as caught:
                self.evidence(readiness).validate(self.row, envelope, exposure=self.context)
            self.assertNotIn(CANARY_TEXT, str(caught.exception))

    def test_a_not_ready_read_named_by_another_manifest_refuses(self):
        artifacts, stops = self.not_ready()
        moved = dict(artifacts, artifactManifest=dict(artifacts['artifactManifest'], sha256='0'*64))
        with self.assertRaisesRegex(ValueError, 'native checkpoint'):
            self.blind_cell(self.readiness(self.payload(moved, stops)))

    def test_the_checkpoint_shape_and_layout_are_exact(self):
        artifacts, stops = self.not_ready()
        good = self.payload(artifacts, stops)
        elsewhere = dict(artifacts, nativeRead={'path': str(self.fixture.output/'native-read.json'), 'sha256': 'a'*64})
        cases = {'incomplete': dict(good, complete=False), 'ready with stops': dict(good, ready=True),
                 'not ready without stops': dict(good, stops=[]),
                 'a stop with its values': dict(good, stops=[dict(stops[0], repeat=None), stops[1]]),
                 'a duplicate stop': dict(good, stops=[stops[0], stops[0]]),
                 'an unknown reason': dict(good, stops=[dict(stops[0], reason='OTHER'), stops[1]]),
                 'readiness differs from its artifacts': dict(good, nativeExposure=dict(artifacts, ready=True)),
                 'another layout': dict(good, nativeExposure=elsewhere),
                 'an unpinned document': dict(good, artifacts=good['artifacts'][1:])}
        self.assertEqual(self.readiness(good)['stops'], stops)
        for label, payload in cases.items():
            with self.subTest(label), self.assertRaises(ValueError):
                self.readiness(payload)

    def test_the_drop_in_for_the_repeat_helper_reads_the_live_checkpoint(self):
        """Item d: checkpointed_blind_cell has the sealed blind_cell's signature and reads its
        readiness from the dispatcher's own checkpoint."""
        self.assertEqual(list(inspect.signature(RD.checkpointed_blind_cell).parameters),
                         list(inspect.signature(self.sealed.blind_cell).parameters))
        artifacts, stops = self.not_ready()
        dispatcher = sys.modules['w50_g1_dispatch']
        with patch.object(dispatcher, 'qualification_native', create=True,
                          side_effect=lambda context: self.payload(artifacts, stops)):
            cell, _, _, _ = RD.checkpointed_blind_cell(self.context, self.run, self.row, self.fixture.scenes)
        self.assertEqual(cell, self.cell)


if __name__ == '__main__':
    unittest.main()
