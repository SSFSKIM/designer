"""Byte-witness tests use synthetic byte blobs, never repository captures."""
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location('byte_witness', HERE / 'byte_witness.py')
M = importlib.util.module_from_spec(SPEC)


def digest(data):
    return hashlib.sha256(data).hexdigest()


class ByteWitnessTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        SPEC.loader.exec_module(M)

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(dir=HERE)
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)

    def blob(self, name, data=b'synthetic, not an image'):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
        return {'path': str(path), 'sha256': digest(data)}

    def test_expected_hash_is_never_replaced(self):
        pin = self.blob('capture.png')
        original = dict(pin)
        Path(pin['path']).write_bytes(b'changed')
        with self.assertRaisesRegex(ValueError, 'hash'):
            M.pinned_bytes(pin)
        self.assertEqual(pin, original)

    def test_external_config_hash_checked_before_json_parse(self):
        pin = self.blob('config.json', b'invalid json')
        with self.assertRaisesRegex(ValueError, 'hash'):
            M.load_config(pin['path'], '0' * 64)

    def test_source_inventory_cannot_be_replaced(self):
        with self.assertRaisesRegex(ValueError, 'original inventory'):
            M.check_config_identity({'schema': 'w50-owner-inputs-metadata-1', 'inventoryPin': {
                'path': '/tmp/references.json', 'sha256': '0' * 64}})

    def test_generation_projection_does_not_emit_measurements(self):
        raw = {'schemaVersion': 5, 'cells': [{'key': {'profileKey': 'p', 'sceneId': 's',
               'web': {'renderer': 'css', 'samplingBackend': 'css-backdrop',
                       'capturePath': 'x', 'pixelSize': [3, 2], 'repeatNoise': 987}},
               'material': {'value': 123}}]}
        pin = self.blob('generation.json', json.dumps(raw).encode())
        self.assertEqual(M.matrix_rows(pin), {'p/css/s': {'profile': 'p', 'scene': 's',
            'renderer': 'css', 'samplingBackend': 'css-backdrop', 'capturePath': 'x', 'pixelSize': [3, 2]}})
        Path(pin['path']).write_bytes(b'changed')
        with self.assertRaisesRegex(ValueError, 'hash'):
            M.matrix_rows(pin)

    def test_metadata_refuses_wrong_generation_or_cell(self):
        row = dict(scene='s', renderer='css', samplingBackend='css-backdrop',
                   capturePath='original', pixelSize=[3, 2])
        metadata = dict(sceneId='s', renderer='css', samplingBackend='css-backdrop',
                        capturePath='original', pixelSize=[3, 2])
        M.check_metadata(row, metadata)
        for field in ['sceneId', 'renderer', 'samplingBackend', 'capturePath', 'pixelSize']:
            with self.subTest(field=field), self.assertRaisesRegex(ValueError, 'metadata'):
                M.check_metadata(row, {**metadata, field: 'changed'})

    def test_fresh_requests_cannot_add_paths_or_change_kind(self):
        expected = {'/allowed.png': {'kind': 'backdrop', 'cells': {'p/css/s'}}}
        request = {'path': '/allowed.png', 'kind': 'backdrop', 'cells': ['p/css/s'],
                   'status': 'FRESH_WITNESS_REQUIRED', 'historicalCaptureTimePin': False}
        with patch.object(M, 'WITNESS_COUNT', 1):
            M.check_requests([request], expected)
            for changed in [{**request, 'path': '/w50/blind/a.png'}, {**request, 'kind': 'historical-web'}]:
                with self.assertRaisesRegex(ValueError, 'request'):
                    M.check_requests([changed], expected)

    def test_path_policy_refuses_symlink_escape_and_blind_paths(self):
        allowed = self.root / 'allowed'
        allowed.mkdir()
        outside = self.blob('outside.png')
        (allowed / 'escape.png').symlink_to(outside['path'])
        with self.assertRaisesRegex(ValueError, 'path'):
            M.allowed_path(allowed / 'escape.png', allowed)
        for path in [allowed / 'w50' / 'blind' / 'a.png', allowed / 'raw' / 'a.png']:
            with self.assertRaisesRegex(ValueError, 'path'):
                M.allowed_path(path, allowed)

    def test_path_policy_refuses_in_tree_raw_blind_aliases_and_root_aliases(self):
        allowed = self.root / 'allowed'
        allowed.mkdir()
        for token in ['raw', 'blind']:
            target = self.blob(f'allowed/{token}/unopened.png')
            alias = allowed / f'{token}-alias.png'
            alias.symlink_to(target['path'])
            with self.subTest(token=token), self.assertRaisesRegex(ValueError, 'path'):
                M.allowed_path(alias, allowed)
            root_alias = self.root / f'{token}-root-alias'
            root_alias.symlink_to(allowed / token, target_is_directory=True)
            with self.subTest(root=token), self.assertRaisesRegex(ValueError, 'path'):
                M.allowed_path(root_alias / 'unopened.png', root_alias)
        ordinary = self.blob('allowed/ordinary.png')
        ordinary_alias = allowed / 'ordinary-alias.png'
        ordinary_alias.symlink_to(ordinary['path'])
        self.assertEqual(M.allowed_path(ordinary_alias, allowed), ordinary_alias)

    def test_write_once_preserves_config_and_refuses_occupied_output(self):
        config = self.blob('config.json', b'{"original":true}')
        witness, inputs = self.root / 'witness.json', self.root / 'inputs.json'
        with patch.object(M, 'HERE', self.root):
            M.write_pair(witness, {'fresh': True}, inputs, {'python': 'shim'})
            before = witness.read_bytes()
            with self.assertRaises(FileExistsError):
                M.write_pair(witness, {}, self.root / 'other.json', {})
            self.assertFalse((self.root / 'other.json').exists())
            self.assertEqual(witness.read_bytes(), before)
            self.assertEqual(Path(config['path']).read_bytes(), b'{"original":true}')
            occupied = self.root / 'occupied.json'
            occupied.write_bytes(b'keep')
            with self.assertRaises(FileExistsError):
                M.write_pair(self.root / 'new.json', {}, occupied, {})
            self.assertFalse((self.root / 'new.json').exists())
            self.assertEqual(occupied.read_bytes(), b'keep')

    def synthetic_config(self, external_control=False):
        fixture_root, canonical = self.root / 'fixtures', self.root / 'captures'
        sources = {'scenes': self.blob('scenes.json', json.dumps({'scenes': [
            {'id': 'solid__shape__rest', 'background': 'solid'}]}).encode()),
            'fixtureManifest': self.blob('fixtures/manifest.json', json.dumps({
                'backgrounds': {'solid@1x': 'backgrounds/solid@1x.png'}}).encode())}
        self.blob('fixtures/backgrounds/solid@1x.png')
        reader = self.blob('metadata.py', b'# synthetic source pin')
        inputs = {'declaration': sources['scenes'], 'current': [], 'references': [],
                  'captures': {}, 'referenceCaptures': {}, 'python': str(self.root / 'python-shim')}
        generations = ['b2d074d2df24-940384c06f73', '0eac5b294cc2', 'd0219cd684bf', 'eab099cc6698']
        membership, checks, cells, requests = {}, [], [], {}
        scene = 'solid__shape__rest'
        for index, generation in enumerate(generations):
            profile = 'apple-macos-27.0-1x-dark-standard-glass' + ('0.25' if index % 2 == 0 else '0.5')
            key = profile + '/css/' + scene
            descriptor = 'materialProfile=active sha256:aaaaaaaaaaaa recededProfile=receded sha256:bbbbbbbbbbbb'
            metadata = {'sceneId': scene, 'renderer': 'css', 'samplingBackend': 'css-backdrop',
                        'capturePath': descriptor, 'pixelSize': [3, 2]}
            envelope = {'schemaVersion': 5, 'cells': [{'key': {'profileKey': profile,
                        'sceneId': scene, 'web': metadata}, 'material': {'unused': 999}}]}
            matrix = self.blob('matrices/' + generation + '.json', json.dumps(envelope).encode())
            documents = {'active': 'a' * 64, 'receded': 'b' * 64}
            reference = index >= 2
            inputs['references' if reference else 'current'].append({'matrix': matrix, 'documents': documents})
            directory = (self.root / 'web-captures-superseded' / generation if reference else canonical) / profile / scene
            if external_control and index == 0:
                directory = self.root / 'original-controls' / profile / scene
            web = self.blob(str(directory.relative_to(self.root) / (scene + '__css.png')))
            meta = self.blob(str(directory.relative_to(self.root) / 'cell__css.json'), json.dumps(metadata).encode())
            native_path = fixture_root / profile / (scene + '.png')
            native = self.blob(str(native_path.relative_to(self.root)))
            backdrop = {'path': str(fixture_root / 'backgrounds/solid@1x.png'), 'sha256': None}
            if not reference:
                cells.append({'profile': profile, 'renderer': 'css', 'scene': scene,
                              'currentGeneration': generation, 'currentEvidence': web,
                              'nativeEvidence': native, 'currentMetadata': meta})
            else:
                web = {**web, 'sha256': None}
                meta = {**meta, 'sha256': None}
            capture = {'web': web, 'native': native, 'metadata': meta,
                       'backdrop': backdrop, 'documents': documents}
            inputs['referenceCaptures' if reference else 'captures'][key] = capture
            membership[generation] = [key]
            checks.append({'cell': key, 'generation': generation, 'metadataPath': meta['path'],
                           'identityMatchesMatrix': True, 'nativePin': native,
                           'nativePairing': 'Original G0 fixture pin matched by profile/scene; not a historical capture-time digest'})
            for field, kind in [('web', 'historical-web'), ('metadata', 'historical-metadata'), ('backdrop', 'backdrop')]:
                pin = capture[field]
                if pin['sha256'] is not None:
                    continue
                request = requests.setdefault(pin['path'], {'path': pin['path'], 'kind': kind, 'cells': [],
                    'status': 'FRESH_WITNESS_REQUIRED', 'historicalCaptureTimePin': False})
                if key not in request['cells']:
                    request['cells'].append(key)
                if field == 'backdrop':
                    request['authority'] = {'manifestPin': sources['fixtureManifest'],
                        'entry': 'backgrounds/solid@1x', 'declaredPath': 'backgrounds/solid@1x.png'}
        inventory = self.blob('packages/calibration/results/2026-10-08-w50-g0-declaration/references.json',
                             json.dumps({'cells': cells, 'generations': {generations[0]: {'captureTree': str(canonical)}}}).encode())
        # Padding tests the actual fixed-size configuration contract without multiplying
        # synthetic image blobs; owner projection is outside this byte-only tool.
        config = {'schema': 'w50-owner-inputs-metadata-1', 'status': 'BLOCKED', 'inventoryPin': inventory,
            'ownerKeys': [f'synthetic-owner-{i}' for i in range(640)], 'inputs': inputs,
            'blockers': [{'code': 'FRESH_WITNESS_REQUIRED'}], 'generationMembership': membership,
            'additionalSources': {'fixtureManifest': sources['fixtureManifest']},
            'witnessRequirements': list(requests.values()), 'captureIdentityChecks': checks}
        config_pin = self.blob('inputs-metadata.json', json.dumps(config).encode())
        return config_pin, inventory, reader, config

    def test_full_synthetic_witness_preserves_config_and_binds_resolved_output(self):
        config_pin, inventory, reader, config = self.synthetic_config()
        before = Path(config_pin['path']).read_bytes()
        witness_path, inputs_path = self.root / 'byte-witness.json', self.root / 'inputs-resolved.json'
        with patch.object(M, 'HERE', self.root), patch.object(M, 'CONFIG_SHA', config_pin['sha256']), \
                patch.object(M, 'INVENTORY_SHA', inventory['sha256']), patch.object(M, 'METADATA_SHA', reader['sha256']), \
                patch.object(M, 'WITNESS_COUNT', 5):
            M.witness(config_pin['path'], config_pin['sha256'], witness_path, inputs_path)
        report = json.loads(witness_path.read_text())
        resolved = json.loads(inputs_path.read_text())
        self.assertEqual(report['schema'], 'w50-owner-byte-witness-1')
        self.assertEqual(report['resolvedInputs']['sha256'], digest(inputs_path.read_bytes()))
        self.assertEqual(report['metadataConfig'], config_pin)
        self.assertEqual(len(report['fresh']), 5)
        self.assertTrue(all(x['witnessKind'] == 'prospective-byte-only' and not x['historicalCaptureTimePin']
                            and len(x['sha256']) == 64 and x['generationMatches'] for x in report['fresh']))
        self.assertEqual(resolved['current'], config['inputs']['current'])
        self.assertEqual(Path(config_pin['path']).read_bytes(), before)

    def test_original_external_controls_are_admitted_without_replacing_pins(self):
        config_pin, inventory, reader, config = self.synthetic_config(external_control=True)
        with patch.object(M, 'HERE', self.root), patch.object(M, 'CONFIG_SHA', config_pin['sha256']), \
                patch.object(M, 'INVENTORY_SHA', inventory['sha256']), patch.object(M, 'METADATA_SHA', reader['sha256']), \
                patch.object(M, 'WITNESS_COUNT', 5):
            M.witness(config_pin['path'], config_pin['sha256'], self.root / 'w.json', self.root / 'i.json')
        report = json.loads((self.root / 'w.json').read_text())
        capture = next(iter(config['inputs']['captures'].values()))
        for field in ['web', 'metadata']:
            self.assertIn(capture[field], report['originalVerified'])
        resolved = json.loads((self.root / 'i.json').read_text())
        self.assertEqual(next(iter(resolved['captures'].values()))['web'], capture['web'])

    def test_external_control_authority_refuses_substitution_and_symlinks(self):
        original = self.blob('original-controls/pinned.png')
        canonical = self.root / 'canonical'
        M.allowed_current_pin(original, original, canonical)
        for substituted in [{**original, 'path': str(self.root / 'other.png')},
                            {**original, 'sha256': '0' * 64}]:
            with self.subTest(pin=substituted), self.assertRaisesRegex(ValueError, 'original'):
                M.allowed_current_pin(substituted, original, canonical)
        alias = self.root / 'original-controls' / 'alias.png'
        alias.symlink_to(original['path'])
        alias_pin = {**original, 'path': str(alias)}
        with self.assertRaisesRegex(ValueError, 'symlink'):
            M.allowed_current_pin(alias_pin, alias_pin, canonical)
        for token in ['raw', 'blind']:
            forbidden = {**original, 'path': str(self.root / token / 'pinned.png')}
            with self.subTest(token=token), self.assertRaisesRegex(ValueError, 'path'):
                M.allowed_current_pin(forbidden, forbidden, canonical)

    def test_full_synthetic_witness_stops_on_changed_original_without_outputs(self):
        config_pin, inventory, reader, config = self.synthetic_config()
        original = next(iter(config['inputs']['captures'].values()))['web']
        Path(original['path']).write_bytes(b'changed current bytes')
        with patch.object(M, 'HERE', self.root), patch.object(M, 'CONFIG_SHA', config_pin['sha256']), \
                patch.object(M, 'INVENTORY_SHA', inventory['sha256']), patch.object(M, 'METADATA_SHA', reader['sha256']), \
                patch.object(M, 'WITNESS_COUNT', 5), self.assertRaisesRegex(ValueError, 'hash'):
            M.witness(config_pin['path'], config_pin['sha256'], self.root / 'w.json', self.root / 'i.json')
        self.assertFalse((self.root / 'w.json').exists())
        self.assertFalse((self.root / 'i.json').exists())

    def test_resolution_copies_and_labels_fresh_pins_without_altering_original(self):
        inputs = {'captures': {'p/css/s': {'web': {'path': '/web.png', 'sha256': None},
                   'native': {'path': '/native.png', 'sha256': 'a' * 64}}}, 'referenceCaptures': {}}
        before = copy.deepcopy(inputs)
        result = M.resolve_inputs(inputs, {'/web.png': 'b' * 64})
        self.assertEqual(result['captures']['p/css/s']['web']['sha256'], 'b' * 64)
        self.assertEqual(result['captures']['p/css/s']['native']['sha256'], 'a' * 64)
        self.assertEqual(inputs, before)
        with self.assertRaisesRegex(ValueError, 'fresh'):
            M.resolve_inputs(inputs, {})


if __name__ == '__main__':
    unittest.main()
