"""Synthetic identity tests; no repository evidence or image bytes are opened."""
import importlib.util
from pathlib import Path
import unittest

SPEC = importlib.util.spec_from_file_location('owner_metadata', Path(__file__).with_name('metadata.py'))
MODULE = importlib.util.module_from_spec(SPEC)


class MetadataTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        SPEC.loader.exec_module(MODULE)

    def test_owner_selection_rejects_duplicates_and_preserves_only_identity(self):
        row = dict(profile='p', renderer='css', scene='s', statistic='owner-contracts',
                   current=999, native=888)
        self.assertEqual(MODULE.owner_rows({'cells': [row]}, 1), [
            dict(profile='p', renderer='css', scene='s', statistic='owner-contracts')])
        with self.assertRaisesRegex(ValueError, 'duplicate'):
            MODULE.owner_rows({'cells': [row, row]}, 2)
        with self.assertRaisesRegex(ValueError, 'count'):
            MODULE.owner_rows({'cells': [row]}, 2)

    def test_document_roles_cannot_be_swapped_or_ambiguous(self):
        descriptor = 'materialProfile=a sha256:aaaaaaaaaaaa recededProfile=b sha256:bbbbbbbbbbbb'
        pair = {'active.dark': 'a' * 64, 'receded.dark': 'b' * 64}
        self.assertEqual(MODULE.document_map(descriptor, pair), {'a': 'a' * 64, 'b': 'b' * 64})
        with self.assertRaisesRegex(ValueError, 'role'):
            MODULE.document_map(descriptor, {'active.dark': 'b' * 64, 'receded.dark': 'a' * 64})
        with self.assertRaisesRegex(ValueError, 'pair'):
            MODULE.document_map(descriptor + ' materialProfile=c sha256:aaaaaaaaaaaa', pair)

    def test_matrix_projection_drops_metric_values(self):
        raw = {'schemaVersion': 5, 'cells': [{
            'key': {'profileKey': 'p', 'sceneId': 's', 'web': {
                'renderer': 'css', 'samplingBackend': 'css-backdrop', 'capturePath': 'descriptor',
                'pixelSize': [320, 200], 'repeatNoise': 777}},
            'fixtureSet': 'probe', 'state': 'rest', 'material': {'secret': 333}}]}
        result = MODULE.matrix_identities(raw)
        self.assertEqual(result, [{'profile': 'p', 'renderer': 'css', 'scene': 's',
            'samplingBackend': 'css-backdrop', 'capturePath': 'descriptor',
            'pixelSize': [320, 200], 'fixtureSet': 'probe', 'state': 'rest'}])
        raw['cells'].append(raw['cells'][0])
        with self.assertRaisesRegex(ValueError, 'duplicate'):
            MODULE.matrix_identities(raw)

    def test_capture_identity_refuses_wrong_scene_backend_or_descriptor(self):
        row = dict(scene='s', renderer='css', samplingBackend='css-backdrop',
                   capturePath='descriptor', pixelSize=[320, 200])
        metadata = dict(sceneId='s', renderer='css', samplingBackend='css-backdrop',
                        capturePath='descriptor', pixelSize=[320, 200], repeatNoise=123)
        MODULE.check_metadata(row, metadata)
        for key in ['sceneId', 'samplingBackend', 'capturePath', 'renderer', 'pixelSize']:
            with self.subTest(key=key), self.assertRaisesRegex(ValueError, 'identity'):
                MODULE.check_metadata(row, {**metadata, key: 'wrong'})

    def test_backdrop_requires_exact_manifest_entry_not_filename_inference(self):
        manifest = {'backgrounds': {'checker@2x': 'backgrounds/checker@2x.png'}}
        self.assertEqual(MODULE.backdrop_from_manifest(manifest, Path('/fixtures'), 'checker', 2),
                         Path('/fixtures/backgrounds/checker@2x.png'))
        with self.assertRaisesRegex(ValueError, 'manifest'):
            MODULE.backdrop_from_manifest(manifest, Path('/fixtures'), 'checker', 1)
        for wrong in ['backgrounds/checker@1x.png', '../outside.png', '/other/checker@2x.png']:
            with self.subTest(wrong=wrong), self.assertRaisesRegex(ValueError, 'manifest'):
                MODULE.backdrop_from_manifest({'backgrounds': {'checker@2x': wrong}},
                                              Path('/fixtures'), 'checker', 2)

    def test_missing_pin_never_turns_into_an_unlabelled_ready_pin(self):
        self.assertEqual(MODULE.copy_pin({'path': '/existing.png', 'sha256': 'a' * 64}),
                         {'path': '/existing.png', 'sha256': 'a' * 64})
        for digest in [None, 'abc', 'a' * 12]:
            with self.assertRaisesRegex(ValueError, 'full SHA'):
                MODULE.copy_pin({'path': '/existing.png', 'sha256': digest})


if __name__ == '__main__':
    unittest.main()
