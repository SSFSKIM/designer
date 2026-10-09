"""Synthetic role trees/images only. No archive locator, native export or renderer is used."""
import copy
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import numpy as np
from PIL import Image

HERE = Path(__file__).resolve().parent
PROFILE = 'apple-macos-27.0-1x-dark-standard-glass0.5'
DECLARATION = '1'*64


def load():
    spec = importlib.util.spec_from_file_location('w50_native_reader_test', HERE/'reader.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def bed():
    canvas = {'width': 512, 'height': 384}
    definitions = [('uniform', 'grey-000', 44, 'calibration'),
                   ('structured', 'impulse-sparse', 96, 'calibration'),
                   ('span', 'grey-028', 128, 'validation'),
                   ('span', 'grey-028', 224, 'blind'),
                   ('uniform', 'grey-007', 44, 'blind')]
    cells, refs, scenes = [], {}, []
    split = {k: [] for k in ('calibration', 'validation', 'holdout', 'recorded', 'probe')}
    for family, background, span, role in definitions:
        scene = f'cell-{background}-s{span:03}__rest'
        reference = f'{PROFILE}/ref-{background}__rest'
        cells.append(dict(id=f'{PROFILE}/{scene}', scene=scene, profile=PROFILE, family=family,
                          background=background, span=span, role=role, pose='active', scale=1,
                          glass=.5, passName='bed-test', reference=reference, runs=[1, 2, 3]))
        scenes.append(dict(id=scene, background=background, component=f'span-{span}', state='rest'))
        split['holdout' if role == 'blind' else role].append(scene)
        if reference not in refs:
            refs[reference] = dict(id=reference, scene=f'ref-{background}__rest', profile=PROFILE,
                                   background=background, passName='bed-test', run=1, roles=[])
        refs[reference]['roles'].append(role)
    for ref in refs.values():
        ref['roles'] = sorted(set(ref['roles']))
        scenes.append(dict(id=ref['scene'], background=ref['background'], component='none', state='rest'))
        split['recorded'].append(ref['scene'])
    doc = dict(version=1, canvas=canvas, components={
        'none': {'kind': 'none'}, 'span-44': {'kind': 'capsule', 'size': [120, 44]},
        'span-96': {'kind': 'rrect', 'size': [168, 96], 'radius': 20.4},
        'span-128': {'kind': 'rrect', 'size': [224, 128], 'radius': 27.2},
        'span-224': {'kind': 'rrect', 'size': [392, 224], 'radius': 47.6}},
        backgrounds={'grey-000': {'kind': 'solid', 'srgb': [0, 0, 0]},
                     'grey-028': {'kind': 'solid', 'srgb': [28, 28, 28]},
                     'grey-007': {'kind': 'solid', 'srgb': [7, 7, 7]},
                     'impulse-sparse': {'kind': 'impulse', 'background': [0]*3,
                                        'foreground': [255]*3, 'size': 4, 'spacing': 96}},
        scenes=scenes, split=split,
        profiles=[dict(key=PROFILE, scenes=[s['id'] for s in scenes])])
    manifest = dict(schema='w50-native-bed-1', canvas=canvas, cells=cells,
                    references=list(refs.values()),
                    repeatRule=dict(runs=3, maxRequiredSpreadCodes=1, barFloorCodes=.5))
    return manifest, doc


def fixture_row(cell, run, doc, role, level=20):
    is_ref = 'roles' in cell
    scene = next(s for s in doc['scenes'] if s['id'] == cell['scene'])
    component = doc['components'][scene['component']]
    paths = []
    if not is_ref:
        w, h = component['size']
        paths = [dict(kind=component['kind'], frameOrigin=[(512-w)/2, (384-h)/2],
                      rect=[0, 0, w, h], opaque=False, elements=[])]
    # Structured synthetic glass must clear the established 0.02 linear silhouette threshold.
    if not is_ref and cell['family'] == 'structured':
        level += 50
    if not is_ref and cell['family'] == 'span':
        level += 50
    rgb = np.full((384, 512, 3), level, dtype=np.uint8)
    if is_ref:
        bg = doc['backgrounds'][cell['background']]
        rgb[:] = bg.get('srgb', [0, 0, 0])
        if bg['kind'] == 'impulse':
            rgb[48:52, 48:52] = 255
    stream = io.BytesIO(); Image.fromarray(rgb).save(stream, format='PNG')
    native_file = f'{PROFILE}/{cell["scene"]}.png'
    frame = [100., 200., 512., 384.]
    native = dict(sceneId=cell['scene'], file=native_file, fixtureSet='recorded' if is_ref else role,
                  width=512, height=384, captureMethod='screencapturekit', materialRendered=True,
                  deterministic=True, presentedActive=True, hidIdleSeconds=100.,
                  capturedAt='2026-10-08T00:00:00Z', suppliedPaths=paths,
                  windowFrame=dict(coordinateSpace='appkit-global-bottom-left', actual=frame,
                                   requested=frame, backingScaleFactor=1.),
                  presentation=None, extraAttestation={'preserve': ['all', 'metadata']})
    row = dict(path=f'{cell["passName"]}/run-{run}/{native_file}', sha256=sha(stream.getvalue()),
               roles=[role], kind='frame', cell=cell['id'], run=run, native=native,
               declarationSha256=DECLARATION, manifestSha256=str(run)*64)
    return row, stream.getvalue()


def tree(root, role, manifest, doc, levels=(20, 21, 20)):
    rows = []
    for cell in manifest['cells']:
        if cell['role'] == role:
            for run in (1, 2, 3):
                row, raw = fixture_row(cell, run, doc, role, levels[run-1])
                path = root/row['path']; path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(raw); rows.append(row)
    for ref in manifest['references']:
        if role in ref['roles']:
            row, raw = fixture_row(ref, 1, doc, role)
            path = root/row['path']; path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(raw); rows.append(row)
    return reseal(root, rows), rows


def reseal(root, rows):
    raw = (json.dumps(dict(schema='w50-role-archive-1', files=rows), indent=2)+'\n').encode()
    (root/'index.json').write_bytes(raw)
    (root/'index.sha256').write_text(sha(raw)+'  index.json\n')
    return sha(raw)


class ReaderTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.r = load()

    def analyse(self, root, index, role, manifest, doc):
        return self.r.read_role_export(root, index, role, manifest, doc,
                                       expected_declaration_sha256=DECLARATION)

    def test_role_read_groups_runs_preserves_evidence_and_keeps_dependencies_separate(self):
        manifest, doc = bed()
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); digest, rows = tree(root, 'calibration', manifest, doc)
            report = self.analyse(root, digest, 'calibration', manifest, doc)
        self.assertTrue(report['ready'])
        self.assertEqual(report['role'], 'calibration')
        self.assertEqual(len(report['cells']), 2)
        self.assertEqual(len(report['dependencies']), 2)
        first = next(c for c in report['cells'] if c['family'] == 'uniform')
        self.assertEqual([r['run'] for r in first['runs']], [1, 2, 3])
        self.assertEqual(first['statistics']['deep8-channel-median']['value'], [20, 20, 20])
        self.assertEqual(first['statistics']['deep8-channel-median']['repeat']['spreadCodes'], [1, 1, 1])
        self.assertEqual(first['runs'][0]['evidence'], rows[0])
        self.assertNotIn('statistics', report['dependencies'][0])
        keyed = self.r.reference_rows(report)
        self.assertEqual(len(keyed), 14)  # 2 renderers * (2 uniform + 5 structured).
        self.assertEqual(keyed[0]['role'], 'calibration')
        self.assertNotIn('B', keyed[0])
        self.assertEqual({r['nativeIdentity'] for r in keyed}, {c['id'] for c in report['cells']})

    def test_aggregation_is_coordinatewise_and_independent_of_role_or_pooled_pixels(self):
        runs = []
        # Each channel's middle run is different; neither channel averaging nor choosing one
        # representative frame recovers the required [20, 40, 80] median statistic.
        for run, value, role in ((1, [20, 60, 80], 'calibration'),
                                 (2, [30, 40, 70], 'validation'),
                                 (3, [10, 20, 90], 'calibration')):
            runs.append({'run': run, 'evidence': {'roles': [role]}, 'readings': {
                'statistics': {'deep8-channel-median': {'status': 'MEASURED', 'support': 'deep8',
                    'units': 'encoded-RGB-codes', 'value': value}}}})
        summary = self.r.aggregate_runs(runs)
        self.assertEqual(summary['deep8-channel-median']['value'], [20, 40, 80])
        self.assertEqual(summary['deep8-channel-median']['runValues'],
                         [[20, 60, 80], [30, 40, 70], [10, 20, 90]])
        different_roles = copy.deepcopy(runs)
        for run in different_roles:
            run['evidence']['roles'] = ['validation']
        self.assertEqual(self.r.aggregate_runs(different_roles), summary)
        self.assertFalse(summary['deep8-channel-median']['repeat']['passes'])

    def test_reported_span_rows_are_exact_keys_b_null_and_level_rows_still_required(self):
        manifest, doc = bed()
        keys = self.r.reported_reference_keys(manifest, doc)
        self.assertEqual(len(keys), 12)  # 2 span cells * 2 renderers * 3 statistics, incl blind IDs.
        expected_scene = 'cell-grey-028-s128__rest'
        self.assertIn((PROFILE, 'webgpu', expected_scene, 'T1-full-silhouette'), keys)
        self.assertNotIn((PROFILE, 'webgpu', expected_scene, 'deep8-channel-median'), keys)
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); digest, _ = tree(root, 'validation', manifest, doc)
            report = self.analyse(root, digest, 'validation', manifest, doc)
        self.assertEqual(len(report['cells']), 1)
        rows = self.r.reference_rows(report)
        for row in rows:
            if row['statistic'] in ('deep8-channel-median', 'central8-channel-median'):
                self.assertEqual(row['status'], 'MEASURED')
                self.assertTrue(row['required'])
            else:
                self.assertEqual(row['status'], 'REPORTED')
                self.assertIsNone(row['B'])
                self.assertFalse(row['required'])
                self.assertIsNotNone(row['native'])
        self.assertEqual(report['cells'][0]['runs'][0]['readings']['supports']['deep8'],
                         report['cells'][0]['runs'][0]['readings']['supports']['deep8_far24'])

    def test_required_repeat_spread_refuses_readiness_but_retains_all_readings(self):
        manifest, doc = bed()
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); digest, _ = tree(root, 'calibration', manifest, doc, (20, 22, 20))
            report = self.analyse(root, digest, 'calibration', manifest, doc)
        self.assertFalse(report['ready'])
        self.assertTrue(any(s['statistic'] == 'deep8-channel-median' for s in report['stops']))
        self.assertEqual(len(report['cells'][0]['runs']), 3)

    def test_hashes_changed_frames_and_unlisted_files_refuse_before_decode(self):
        manifest, doc = bed()
        for change in ('index', 'frame', 'extra', 'sidecar'):
            with self.subTest(change=change), tempfile.TemporaryDirectory() as td:
                root = Path(td); digest, rows = tree(root, 'calibration', manifest, doc)
                if change == 'index':
                    digest = 'f'*64
                elif change == 'frame':
                    (root/rows[0]['path']).write_bytes(b'changed')
                elif change == 'extra':
                    (root/'extra.png').write_bytes(b'not a role frame')
                else:
                    (root/'index.sha256').write_text('untrusted sidecar')
                with patch.object(self.r.S, 'decode_png', side_effect=AssertionError('pixel decode')):
                    with self.assertRaises(ValueError):
                        self.analyse(root, digest, 'calibration', manifest, doc)

    def test_blind_raw_mixed_or_wrong_role_membership_refuses_before_any_frame_read(self):
        manifest, doc = bed()
        for change in ('blind-api', 'wrong-role', 'mixed-role', 'blind-cell', 'exclusive-ref', 'operational'):
            with self.subTest(change=change), tempfile.TemporaryDirectory() as td:
                root = Path(td); digest, rows = tree(root, 'calibration', manifest, doc)
                role = 'calibration'
                if change == 'blind-api':
                    role = 'blind'
                elif change == 'wrong-role':
                    role = 'validation'
                elif change == 'mixed-role':
                    rows[0]['roles'].append('blind')
                elif change in ('blind-cell', 'exclusive-ref'):
                    if change == 'blind-cell':
                        cell = next(c for c in manifest['cells'] if c['role'] == 'blind')
                    else:
                        cell = next(c for c in manifest['references'] if c['roles'] == ['blind'])
                    row, raw = fixture_row(cell, 1, doc, 'calibration')
                    path = root/row['path']; path.parent.mkdir(parents=True, exist_ok=True)
                    path.write_bytes(raw); rows.append(row)
                else:
                    rows[0]['kind'] = 'attestation'
                digest = reseal(root, rows)
                with patch.object(self.r.S, 'decode_png', side_effect=AssertionError('pixel decode')):
                    with self.assertRaises(ValueError):
                        self.analyse(root, digest, role, manifest, doc)

    def test_missing_extra_duplicate_or_relabelled_repetitions_are_refused(self):
        manifest, doc = bed()
        for change in ('missing', 'fourth', 'duplicate', 'relabelled', 'reference-repeat'):
            with self.subTest(change=change), tempfile.TemporaryDirectory() as td:
                root = Path(td); _, rows = tree(root, 'calibration', manifest, doc)
                if change == 'missing':
                    rows.pop(0)
                elif change == 'duplicate':
                    rows.append(copy.deepcopy(rows[0]))
                elif change == 'fourth':
                    row = copy.deepcopy(rows[0]); row['run'] = 4; rows.append(row)
                elif change == 'reference-repeat':
                    rows[-1]['run'] = 2
                else:
                    rows[0]['run'] = 2
                digest = reseal(root, rows)
                with self.assertRaises(ValueError):
                    self.analyse(root, digest, 'calibration', manifest, doc)

    def test_metadata_declaration_and_path_attestation_cannot_be_substituted(self):
        manifest, doc = bed()
        for change in ('scene', 'size', 'origin', 'kind', 'pose', 'declaration', 'file', 'manifest'):
            with self.subTest(change=change), tempfile.TemporaryDirectory() as td:
                root = Path(td); _, rows = tree(root, 'calibration', manifest, doc)
                row = rows[0]
                if change == 'scene': row['native']['sceneId'] = 'other'
                elif change == 'size': row['native']['width'] = 511
                elif change == 'origin': row['native']['suppliedPaths'][0]['frameOrigin'][0] += 1
                elif change == 'kind': row['native']['suppliedPaths'][0]['kind'] = 'rrect'
                elif change == 'pose': row['native']['presentedActive'] = False
                elif change == 'declaration': row['declarationSha256'] = '0'*64
                elif change == 'file': row['native']['file'] = '../escaped.png'
                else: row['manifestSha256'] = '9'*64  # same admitted run now has conflicting manifest pins.
                digest = reseal(root, rows)
                with patch.object(self.r.S, 'decode_png', side_effect=AssertionError('pixel decode')):
                    with self.assertRaises(ValueError):
                        self.analyse(root, digest, 'calibration', manifest, doc)

    def test_paths_and_symlinks_cannot_escape_even_with_a_resealed_index(self):
        manifest, doc = bed()
        for change in ('absolute', 'parent', 'symlink'):
            with self.subTest(change=change), tempfile.TemporaryDirectory() as td:
                root = Path(td); _, rows = tree(root, 'calibration', manifest, doc)
                if change == 'absolute': rows[0]['path'] = '/outside.png'
                elif change == 'parent': rows[0]['path'] = '../outside.png'
                else:
                    file = root/rows[0]['path']; raw = file.read_bytes(); file.unlink()
                    target = root/'target'; target.write_bytes(raw); file.symlink_to(target)
                digest = reseal(root, rows)
                with self.assertRaises(ValueError):
                    self.analyse(root, digest, 'calibration', manifest, doc)

    def test_actual_png_dimensions_are_checked_not_only_native_metadata(self):
        manifest, doc = bed()
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); _, rows = tree(root, 'calibration', manifest, doc)
            out = io.BytesIO(); Image.new('RGB', (511, 384)).save(out, format='PNG')
            (root/rows[0]['path']).write_bytes(out.getvalue()); rows[0]['sha256'] = sha(out.getvalue())
            digest = reseal(root, rows)
            with self.assertRaises(ValueError):
                self.analyse(root, digest, 'calibration', manifest, doc)


if __name__ == '__main__':
    unittest.main()
