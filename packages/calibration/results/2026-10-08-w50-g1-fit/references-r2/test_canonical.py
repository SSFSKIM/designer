"""Temporary synthetic W29/W43 repositories only; no real canonical or archive data."""
import copy
import gzip
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


def load():
    spec = importlib.util.spec_from_file_location('w50_canonical_reader_tests', HERE/'canonical.py')
    module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    return module


def raw_json(doc): return (json.dumps(doc, indent=2)+'\n').encode()
def digest(raw): return hashlib.sha256(raw).hexdigest()
def put(path, raw): path.parent.mkdir(parents=True, exist_ok=True); path.write_bytes(raw); return path
def pin(path): return {'path': str(path), 'sha256': digest(path.read_bytes())}
def png(rgb):
    stream = io.BytesIO(); Image.fromarray(rgb).save(stream, format='PNG'); return stream.getvalue()


def profile(scale, position): return f'apple-macos-27.0-{scale}x-dark-standard-glass{position}'


def fixture(scene, key, scale, run):
    active = scene.endswith('__rest')
    return dict(sceneId=scene, file=f'{key}/{scene}.png', fixtureSet='calibration',
        capturedAt=f'2026-09-18T00:00:{run:02d}Z', deterministic=True, materialRendered=True,
        captureMethod='screencapturekit', width=320*scale, height=200*scale,
        presentedActive=active, hidIdleSeconds=100,
        presentation=None if active else dict(observedPose='inactive', isKeyWindow=False, appIsActive=False))


def attest(pass_name, phase, spec_hash, scale, position):
    return ''.join(f'{k}={v}\n' for k, v in dict(phase=phase, readAt=phase, **{'pass': pass_name},
        osProductVersion='27.0', osBuild='26A428', glassTintAmount=position,
        reduceTransparency=0, increaseContrast=0, a11yMode='standard', showBorders=0,
        displayplacerMode=68 if scale == 2 else 69, displayModeDeclaredForScale=68 if scale == 2 else 69,
        bundleBinarySha256='a'*64, bundlePath='/synthetic/Reference.app', bundleMinOS='27.0',
        bundleRecordedSdk='27.0', passSpecSha256=spec_hash).items()).encode()


def trees(root):
    scenes = {'version': 1, 'canvas': {'width': 320, 'height': 200},
        'backgrounds': {'solid': {'kind': 'solid', 'srgb': [0]*3}},
        'components': {'r': {'kind': 'rrect', 'size': [168, 96], 'radius': 20.4}},
        'scenes': [dict(id=f'text__r__{state}', background='solid', component='r', state=state)
                   for state in ('rest', 'inactive')],
        'profiles': [dict(key=profile(s, p), colorScheme='dark', a11y='standard',
                          scenes=['text__r__rest', 'text__r__inactive'])
                     for s in (1, 2) for p in ('0.5', '0.25')],
        'split': {'calibration': ['text__r__rest'], 'holdout': ['text__r__inactive'],
                  'validation': [], 'recorded': [], 'probe': []}}
    scene_path = put(root/'scenes.json', raw_json(scenes))
    bank, fixtures, archive = root/'bank', root/'fixtures', root/'archive'
    provenance = {'sittingDir': str(bank), 'passes': {}}
    published = {'profiles': [], 'backgrounds': {}}
    image = np.zeros((200, 320, 3), dtype=np.uint8); image[52:148, 76:244] = 128
    for scale in (1, 2):
        bg = png(np.zeros((200*scale, 320*scale, 3), dtype=np.uint8))
        put(fixtures/f'backgrounds/solid@{scale}x.png', bg)
        published['backgrounds'][f'solid@{scale}x'] = f'backgrounds/solid@{scale}x.png'
        for position in ('0.5', '0.25'):
            published['profiles'].append({'profileKey': profile(scale, position), 'fixtures': []})
        for pose, state in (('active', 'rest'), ('inactive', 'inactive')):
            name = f'standard-{pose}-{scale}x'; key = profile(scale, '0.5'); scene = f'text__r__{state}'
            spec = copy.deepcopy(scenes)
            spec['profiles'] = [p for p in spec['profiles'] if p['key'].endswith('glass0.5')]
            spec_path = put(bank/f'{name}.scenes-27.json', raw_json(spec))
            source_rows = []
            for run in range(1, 8):
                directory = bank/name/f'run-{run}'
                rgb = np.repeat(np.repeat(image, scale, axis=0), scale, axis=1)
                if run < 3: rgb[60*scale:140*scale:2, 85*scale:235*scale] = 200 if run == 1 else 160
                frame = fixture(scene, key, scale, run)
                put(directory/frame['file'], png(rgb)); put(directory/f'backgrounds/solid@{scale}x.png', bg)
                manifest = {'hardware': {'osVersion': 'Version 27.0 (Build 26A428)', 'osBuild': '26A428'},
                    'profiles': [{'profileKey': key, 'colorScheme': 'dark', 'a11yMode': 'standard',
                        'display': {'actualBackingScale': scale, 'requestedScale': scale,
                                    'pixelSize': [320*scale, 200*scale], 'colorSpace': 'kCGColorSpaceSRGB'},
                        'fixtures': [frame]}], 'backgrounds': {f'solid@{scale}x': f'backgrounds/solid@{scale}x.png'}}
                manifest_path = put(directory/'manifest.json', raw_json(manifest))
                opened = put(directory/'attest.read', attest(name, 'open', digest(spec_path.read_bytes()), scale, '0.5'))
                closed = put(directory/'attest.close', attest(name, 'close', digest(spec_path.read_bytes()), scale, '0.5'))
                source_rows.append({'run': f'run-{run}', 'manifestSha256': pin(manifest_path)['sha256'],
                    'cells': 1, 'firstCapturedAt': frame['capturedAt'], 'lastCapturedAt': frame['capturedAt'],
                    'attestReadSha256': pin(opened)['sha256'], 'attestCloseSha256': pin(closed)['sha256']})
                if run == 3:
                    put(fixtures/frame['file'], png(rgb))
                    next(p for p in published['profiles'] if p['profileKey'] == key)['fixtures'].append(copy.deepcopy(frame))
            provenance['passes'][name] = {'runs': source_rows, 'profiles': [key],
                'passSpec': spec_path.name, 'passSpecSha256': pin(spec_path)['sha256']}
    provenance_path = put(root/'provenance.json', raw_json(provenance))
    archive_reader = HERE.parents[1]/'2026-10-01-w43-g0-declaration/bed/sitting/w43_archive.py'
    inventory = {'schema': 'w43-archive-1', 'sitting': 'g1a', 'planSha256': 'b'*64,
                 'producer': {'w43_archive.py': digest(archive_reader.read_bytes())},
                 'sources': {'canonical': 'c'*64}, 'frames': [], 'cells': [], 'runs': [],
                 'operational': [], 'dumps': []}
    seen_frames = set()
    for scale in (1, 2):
        key = profile(scale, '0.25')
        for pose, state in (('active', 'rest'), ('receded', 'inactive')):
            scene = f'text__r__{state}'; cell = key+'/'+scene
            pass_name = f'bed-x0.25-{scale}x-dark-{pose}'
            members = []
            for run in range(1, 8):
                rgb = np.repeat(np.repeat(image, scale, axis=0), scale, axis=1)
                raw = png(rgb); frame_hash = digest(raw)
                bg = png(np.zeros_like(rgb)); bg_hash = digest(bg)
                for data, hashed, kind in ((raw, frame_hash, 'capture'), (bg, bg_hash, 'background')):
                    if hashed not in seen_frames:
                        path = f'frames/{hashed}.png'; put(archive/path, data)
                        inventory['frames'].append({'path': path, 'sha256': hashed, 'kinds': [kind]})
                        seen_frames.add(hashed)
                entry = fixture(scene, key, scale, run)
                manifest = {'hardware': {'osVersion': 'Version 27.0 (Build 26A428)', 'osBuild': '26A428'},
                    'profiles': [{'profileKey': key, 'colorScheme': 'dark', 'a11yMode': 'standard',
                      'display': {'actualBackingScale': scale, 'requestedScale': scale,
                                  'pixelSize': [320*scale, 200*scale], 'colorSpace': 'kCGColorSpaceSRGB'},
                      'fixtures': [entry]}], 'backgrounds': {f'solid@{scale}x': f'backgrounds/solid@{scale}x.png'}}
                manifest_raw = raw_json(manifest); manifest_hash = digest(manifest_raw)
                spec = copy.deepcopy(scenes)
                spec['profiles'] = [p for p in spec['profiles'] if p['key'] == key]
                spec_raw = raw_json(spec); spec_hash = digest(spec_raw)
                spec_path = f'operational/{pass_name}/scenes-run-{run}.json'
                put(archive/spec_path, spec_raw)
                inventory['operational'].append({'path': spec_path, 'sha256': spec_hash})
                op = f'operational/{pass_name}/run-{run}'
                admission = {'schema': 'w43-run-admission-1', 'admitted': True, 'dry': False,
                    'pass': pass_name, 'run': run, 'glass': .25, 'sitting': 'g1a',
                    'planSha256': inventory['planSha256'], 'manifestSha256': manifest_hash,
                    'frames': {cell: frame_hash}, 'declaration': {'predeclaration': False}}
                for filename, data in (('manifest.json', manifest_raw), ('admission.json', raw_json(admission)),
                    ('attest.read', attest(pass_name, 'open', spec_hash, scale, '0.25')),
                    ('attest.close', attest(pass_name, 'close', spec_hash, scale, '0.25'))):
                    path = op+'/'+filename; put(archive/path, data)
                    inventory['operational'].append({'path': path, 'sha256': digest(data)})
                inventory['runs'].append({'pass': pass_name, 'run': run, 'protocol': 'normal',
                    'manifestSha256': manifest_hash, 'admissionSha256': digest(raw_json(admission)),
                    'backgrounds': {f'backgrounds/solid@{scale}x.png': bg_hash}})
                members.append({'pass': pass_name, 'run': run, 'protocol': 'normal', 'frame': frame_hash,
                    'manifestSha256': manifest_hash, 'attestation': {k: v for k, v in entry.items() if k != 'file'}})
                if run == 1:
                    put(fixtures/entry['file'], raw)
                    next(p for p in published['profiles'] if p['profileKey'] == key)['fixtures'].append(copy.deepcopy(entry))
            record = {'schema': inventory['schema'], 'cell': cell, 'role': 'holdout' if state == 'inactive' else 'calibration',
                      'source': 'canonical', 'runs': members, 'statistics': {'ignored': 'not an estimator input'}}
            compressed = gzip.compress(raw_json(record), mtime=0)
            path = f'calibration/{digest(cell.encode())}.cell.json.gz'; put(archive/path, compressed)
            inventory['cells'].append({'cell': cell, 'role': record['role'], 'path': path,
                                      'sha256': digest(compressed), 'runs': 7, 'frames': 1})
    inventory_path = put(archive/'inventory.json', raw_json(inventory))
    fetch = put(root/'fetch.json', raw_json({'tag': 'w43-archive-g1a', 'sha256': 'e'*64,
                                          'inventorySha256': pin(inventory_path)['sha256']}))
    published_path = put(fixtures/'manifest.json', raw_json(published))
    config = {'scenes': pin(scene_path), 'publishedManifest': pin(published_path), 'fixtureRoot': str(fixtures),
              'w29': {'root': str(bank), 'provenance': pin(provenance_path)},
              'w43': {'root': str(archive), 'fetch': pin(fetch)}}
    return config, scenes, published, provenance


class ReaderTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls): cls.c = load()

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(); self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        self.config, self.scenes, self.published, self.provenance = trees(self.root)

    def row(self, position='0.5', state='rest'):
        key = profile(1, position); scene = f'text__r__{state}'
        current = self.root/f'web-{position}-{state}.png'
        put(current, (Path(self.config['fixtureRoot'])/key/(scene+'.png')).read_bytes())
        return {'profile': key, 'renderer': 'webgpu', 'scene': scene, 'stratum': 'T',
                'statistic': 'T1-low', 'role': 'gate' if state == 'rest' else 'historical-prediction-check',
                'nativeEvidence': pin(Path(self.config['fixtureRoot'])/key/(scene+'.png')),
                'currentEvidence': pin(current), 'B': None, 'native': None, 'current': None,
                'fidelity': None, 'historical': []}

    def test_own_seven05_bars_have_committed_metadata_and_fresh_frame_witnesses(self):
        report = self.c.read_references([self.row()], self.config)
        row = report['partitions']['gate'][0]
        self.assertEqual(row['status'], 'MEASURED')
        self.assertEqual(len(row['runs']), 7)
        self.assertEqual(len(report['sources']['w29']['runs']), 28)
        self.assertEqual(row['source']['frameHashBinding'], 'FRESHLY_WITNESSED_NOT_CAPTURE_TIME_PINNED')
        self.assertEqual(row['source']['selectedRuns'], ['r3', 'r4', 'r5', 'r6', 'r7'])
        self.assertEqual(row['reference']['fidelity']['statistic'], 'T1-fine')
        self.assertGreater(row['readings']['T1-low']['repeat']['spreadCodes'], 1)
        self.assertNotIn('passes', row['readings']['T1-low']['repeat'])
        self.assertEqual(row['reference']['B'], row['readings']['T1-low']['B'])
        self.assertNotIn('coefficientInputs', report)

    def test025_uses_own_archive_frames_and_keeps_populated_t1_fields_exact(self):
        original = self.row('0.25')
        original.update(native=.1, current=.2, B=.003, fidelity={'native': .3, 'current': .4, 'reference': .5},
                        historical=[{'value': .6, 'maxGrowthInB': 2}], status='MEASURED')
        report = self.c.read_references([original], self.config)
        row = report['partitions']['gate'][0]
        self.assertEqual(row['reference'], original)
        self.assertEqual(len(row['runs']), 7)
        self.assertEqual(row['source']['frameHashBinding'], 'ARCHIVE_INVENTORY_AND_ADMISSION_PINNED')
        self.assertEqual(row['readings']['deep8-channel-median']['repeat']['units'], 'encoded-RGB-codes')

    def test_historical_rows_have_their_own_partition_and_no_fit_summary(self):
        report = self.c.read_references([self.row(state='inactive')], self.config)
        self.assertEqual(report['partitions']['gate'], [])
        self.assertEqual(len(report['partitions']['historical-prediction-check']), 1)
        self.assertEqual(report['purpose'], 'REFERENCE_EVIDENCE_ONLY_NOT_COEFFICIENT_INPUT')
        with self.assertRaises(ValueError):
            self.c.read_references([{**self.row(), 'role': 'calibration'}], self.config)

    def test_wrong_provenance_attestation_pose_or_published_state_is_unmeasured_before_decode(self):
        for change in ('provenance', 'attestation', 'published-state', 'missing-repeat'):
            with self.subTest(change=change), tempfile.TemporaryDirectory() as td:
                config, _, _, _ = trees(Path(td).resolve()); original = self.row()
                key = profile(1, '0.5'); scene = 'text__r__rest'
                pub = Path(config['fixtureRoot'])/key/(scene+'.png')
                original['nativeEvidence'] = pin(pub)
                original['currentEvidence'] = pin(pub)
                if change == 'provenance': config['w29']['provenance']['sha256'] = '0'*64
                elif change == 'attestation':
                    (Path(config['w29']['root'])/'standard-active-1x/run-1/attest.read').write_text('changed')
                elif change == 'missing-repeat':
                    (Path(config['w29']['root'])/f'standard-active-1x/run-7/{key}/{scene}.png').unlink()
                else:
                    put(pub, png(np.full((200, 320, 3), 42, dtype=np.uint8)))
                    original['nativeEvidence'] = pin(pub); original['currentEvidence'] = pin(pub)
                with patch.object(self.c.M.S, 'decode_png', side_effect=AssertionError('pixel decode')):
                    report = self.c.read_references([original], config)
                self.assertEqual(report['partitions']['gate'][0]['status'], 'UNMEASURED')
                self.assertEqual(report['partitions']['gate'][0]['readings'], {})

    def rebind_w43_inventory(self, inventory):
        path = Path(self.config['w43']['root'])/'inventory.json'; put(path, raw_json(inventory))
        fetch_path = Path(self.config['w43']['fetch']['path'])
        fetch = json.loads(fetch_path.read_bytes()); fetch['inventorySha256'] = pin(path)['sha256']
        put(fetch_path, raw_json(fetch)); self.config['w43']['fetch'] = pin(fetch_path)

    def test_w43_missing_recorded_reader_identity_never_becomes_an_assumed_producer(self):
        original = self.row('0.25')
        inventory = json.loads((Path(self.config['w43']['root'])/'inventory.json').read_bytes())
        del inventory['producer']; self.rebind_w43_inventory(inventory)
        with patch.object(self.c.M.S, 'decode_png', side_effect=AssertionError('pixel decode')):
            report = self.c.read_references([original], self.config)
        self.assertEqual(report['partitions']['gate'][0]['status'], 'UNMEASURED')

    def test_semantic_native_pose_admission_refuses_even_with_coherent_synthetic_metadata_hashes(self):
        original = self.row()
        directory = Path(self.config['w29']['root'])/'standard-active-1x/run-1'
        path = directory/'manifest.json'; manifest = json.loads(path.read_bytes())
        manifest['profiles'][0]['fixtures'][0]['presentedActive'] = False
        put(path, raw_json(manifest))
        provenance_path = Path(self.config['w29']['provenance']['path'])
        provenance = json.loads(provenance_path.read_bytes())
        provenance['passes']['standard-active-1x']['runs'][0]['manifestSha256'] = pin(path)['sha256']
        put(provenance_path, raw_json(provenance)); self.config['w29']['provenance'] = pin(provenance_path)
        with patch.object(self.c.M.S, 'decode_png', side_effect=AssertionError('pixel decode')):
            report = self.c.read_references([original], self.config)
        self.assertEqual(report['partitions']['gate'][0]['status'], 'UNMEASURED')
        self.assertIn('admission', report['sourceFailures']['w29'])

    def test_wrong_published_timestamp_and_changed_source_background_do_not_fall_back(self):
        original = self.row()
        published_path = Path(self.config['publishedManifest']['path'])
        published = json.loads(published_path.read_bytes())
        target = next(p for p in published['profiles'] if p['profileKey'] == original['profile'])
        target['fixtures'][0]['capturedAt'] = '2099-01-01T00:00:00Z'
        put(published_path, raw_json(published)); self.config['publishedManifest'] = pin(published_path)
        with patch.object(self.c.M.S, 'decode_png', side_effect=AssertionError('pixel decode')):
            report = self.c.read_references([original], self.config)
        self.assertEqual(report['partitions']['gate'][0]['status'], 'UNMEASURED')
        self.assertIn('timestamp', report['partitions']['gate'][0]['reason'])
        target['fixtures'][0]['capturedAt'] = '2026-09-18T00:00:03Z'
        put(published_path, raw_json(published)); self.config['publishedManifest'] = pin(published_path)
        bg = Path(self.config['w29']['root'])/'standard-active-1x/run-4/backgrounds/solid@1x.png'
        put(bg, png(np.full((200, 320, 3), 1, dtype=np.uint8)))
        with patch.object(self.c.M.S, 'decode_png', side_effect=AssertionError('pixel decode')):
            report = self.c.read_references([original], self.config)
        self.assertEqual(report['partitions']['gate'][0]['status'], 'UNMEASURED')
        self.assertIn('background', report['partitions']['gate'][0]['reason'])

    def test_w43_source_geometry_cannot_be_replaced_by_a_new_canonical_geometry(self):
        original = self.row('0.25')
        path = Path(self.config['scenes']['path']); scenes = json.loads(path.read_bytes())
        scenes['components']['r']['radius'] = 0
        put(path, raw_json(scenes)); self.config['scenes'] = pin(path)
        with patch.object(self.c.M.S, 'decode_png', side_effect=AssertionError('pixel decode')):
            report = self.c.read_references([original], self.config)
        self.assertEqual(report['partitions']['gate'][0]['status'], 'UNMEASURED')
        self.assertIn('geometry', report['partitions']['gate'][0]['reason'])

    def test_an_annotation_added_after_capture_is_not_a_geometry_change(self):
        original = self.row()
        path = Path(self.config['scenes']['path']); scenes = json.loads(path.read_bytes())
        scenes['components']['r']['$comment-later'] = 'a ruling recorded beside the component'
        scenes['backgrounds'][next(iter(scenes['backgrounds']))]['$comment'] = 'prose'
        put(path, raw_json(scenes)); self.config['scenes'] = pin(path)
        report = self.c.read_references([original], self.config)
        self.assertEqual(report['partitions']['gate'][0]['status'], 'MEASURED')
        scenes['components']['r']['radius'] += 1
        put(path, raw_json(scenes)); self.config['scenes'] = pin(path)
        with patch.object(self.c.M.S, 'decode_png', side_effect=AssertionError('pixel decode')):
            report = self.c.read_references([original], self.config)
        self.assertEqual(report['partitions']['gate'][0]['status'], 'UNMEASURED')
        self.assertIn('geometry', report['partitions']['gate'][0]['reason'])

    def test_a_new512_declaration_is_not_a_canonical_reference_source(self):
        original = self.row()
        path = Path(self.config['scenes']['path']); scenes = json.loads(path.read_bytes())
        scenes['canvas'] = {'width': 512, 'height': 384}
        put(path, raw_json(scenes)); self.config['scenes'] = pin(path)
        with patch.object(self.c.M.S, 'decode_png', side_effect=AssertionError('pixel decode')):
            report = self.c.read_references([original], self.config)
        self.assertEqual(report['partitions']['gate'][0]['status'], 'UNMEASURED')

    def test_source_hash_is_rechecked_at_decode_and_wrong_archive_inventory_is_unmeasured(self):
        row = self.row('0.25')
        self.config['w43']['fetch']['sha256'] = '0'*64
        with patch.object(self.c.M.S, 'decode_png', side_effect=AssertionError('pixel decode')):
            report = self.c.read_references([row], self.config)
        self.assertEqual(report['partitions']['gate'][0]['status'], 'UNMEASURED')
        file = self.root/'synthetic.png'; put(file, png(np.zeros((200, 320, 3), dtype=np.uint8)))
        witnessed = pin(file); file.write_bytes(b'changed')
        with self.assertRaises(ValueError): self.c.decode_verified(witnessed, (200, 320))


if __name__ == '__main__': unittest.main()
