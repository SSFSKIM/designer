"""Synthetic bootstrap fixtures only: never load the checkout's inventory or data."""
import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

HERE = Path(__file__).resolve().parent


def load_run():
    spec = importlib.util.spec_from_file_location('owner_run', HERE/'run.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class BootstrapTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='w50-owner-synthetic-')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()/'repo'
        self.root.mkdir()
        self.run = load_run()
        self.run.ROOT = self.root
        self.run.HERE = self.root/'owner'
        self.run.HERE.mkdir()
        self.run.INVENTORY = self.root/'inventory.json'
        self.run.PYTHON = str(Path('/Users/new/vitrea-w49/py/bin/python'))
        for path in self.run.required_sources():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text('{}' if path.suffix == '.json' else '# synthetic source\n')
        self.config = self.put('config.json', {'declaration': self.pin('declaration.json', {}),
            'current': [], 'references': [], 'captures': {}, 'referenceCaptures': {},
            'python': str(self.run.HERE/'python-shim')})
        cells = [{'profile': 'synthetic', 'renderer': 'webgpu', 'scene': f'scene-{i}',
                  'statistic': 'owner-contracts'} for i in range(640)]
        self.inventory = self.put('inventory.json', {'schema': 'w50-reference-inventory-1', 'cells': cells})
        self.run.INVENTORY_SHA256 = self.run.sha(self.inventory)
        self.request = self.put('request.json', {'mode': 'prepare', 'inputsPin': self.pin(self.config)})
        self.closure = self.put('closure.json', {'sources': [self.relpin(p) for p in self.run.required_sources()]})
        self.doc = {'schema': 'w50-owner-instrument-root-1', 'request': self.pin(self.request),
            'config': self.pin(self.config), 'inventory': self.pin(self.inventory),
            'ownerKeys': sorted(f"synthetic/webgpu/scene-{i}" for i in range(640)),
            'closure': self.pin(self.closure), 'output': str(self.root.parent/'result.json'),
            'node': {'path': '/synthetic/node', 'sha256': '0'*64},
            'pythonEnvironment': {}}
        original = json.loads(self.config.read_bytes())
        original['declaration']['sha256'] = None
        self.metadata = self.put('owner/inputs-metadata.json', {
            'schema': 'w50-owner-inputs-metadata-1', 'status': 'BLOCKED',
            'inventoryPin': self.pin(self.inventory), 'ownerKeys': self.doc['ownerKeys'],
            'inputs': original, 'witnessRequirements': [{'path': str(self.root/'declaration.json'),
                'kind': 'synthetic', 'cells': ['synthetic/webgpu/scene-0']}]})
        self.run.METADATA_SHA256 = self.run.sha(self.metadata)
        self.witness = self.put('byte-witness.json', {'schema': 'w50-owner-byte-witness-1',
            'metadataConfig': self.pin(self.metadata), 'resolvedInputs': self.pin(self.config),
            'sourcePins': {}, 'originalVerified': [], 'fresh': [{**self.pin(self.root/'declaration.json'),
                'kind': 'synthetic', 'cells': ['synthetic/webgpu/scene-0'],
                'historicalCaptureTimePin': False, 'witnessKind': 'prospective-byte-only'}]})
        self.doc['inputWitness'] = self.pin(self.witness)
        self.instrument = self.put('instrument.json', self.doc)

    def put(self, name, value):
        path = self.root/name
        path.write_text(json.dumps(value))
        return path

    def pin(self, path, value=None):
        path = Path(path)
        if not path.is_absolute():
            path = self.root/path
        if value is not None:
            path.write_text(json.dumps(value))
        return {'path': str(path), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}

    def relpin(self, path):
        return {**self.pin(path), 'path': str(path.relative_to(self.root))}

    def verify(self):
        # Runtime verification is separately subprocess-tested; these fixtures have no numeric runtime.
        return self.run.validate(self.instrument, self.run.sha(self.instrument))

    def repin_root(self):
        self.put('instrument.json', self.doc)

    def test_accepts_complete_fixed_membership(self):
        doc, request, sources = self.verify()
        self.assertEqual(request['mode'], 'prepare')
        self.assertEqual(len(doc['ownerKeys']), 640)
        self.assertIn('owner/run.py', sources)

    def test_unregistered_root_hash_refused(self):
        with self.assertRaisesRegex(ValueError, 'registered'):
            self.run.validate(self.instrument, '0'*64)

    def test_changed_source_refused_before_any_helper(self):
        (self.run.HERE/'edge.py').write_text('raise RuntimeError("SIDE EFFECT")')
        with self.assertRaisesRegex(ValueError, 'Changed'):
            self.verify()

    def test_changed_request_or_config_or_manifest_refused(self):
        for path in [self.request, self.config, self.root/'package.json']:
            with self.subTest(path=path):
                original = path.read_bytes()
                path.write_bytes(original+b' ')
                with self.assertRaisesRegex(ValueError, 'Changed'):
                    self.verify()
                path.write_bytes(original)

    def test_subset_or_different_keys_refused_even_with_registered_root(self):
        for keys in [self.doc['ownerKeys'][:-1], ['wrong']*640]:
            self.doc['ownerKeys'] = keys
            self.repin_root()
            with self.assertRaisesRegex(ValueError, 'membership'):
                self.verify()

    def test_request_cannot_substitute_pinned_config_or_choose_row(self):
        for request in [{'mode': 'prepare', 'inputsPin': self.pin(self.inventory)},
                        {'mode': 'project-current', 'row': {}}]:
            self.put('request.json', request)
            self.doc['request'] = self.pin(self.request)
            self.repin_root()
            with self.assertRaisesRegex(ValueError, 'request'):
                self.verify()

    def test_replacement_inventory_cannot_redefine_membership(self):
        self.inventory.write_text('{"cells": []}')
        self.doc['inventory'] = self.pin(self.inventory)
        self.repin_root()
        with self.assertRaisesRegex(ValueError, 'original inventory'):
            self.verify()

    def test_occupied_output_refused_without_overwrite(self):
        output = Path(self.doc['output'])
        output.write_text('retained')
        with self.assertRaisesRegex(ValueError, 'Output exists'):
            self.verify()
        self.assertEqual(output.read_text(), 'retained')

    def test_witness_cannot_rewrite_original_config_fields(self):
        config = json.loads(self.config.read_bytes())
        config['current'] = [{'new': 'subset'}]
        self.put('config.json', config)
        self.doc['config'] = self.pin(self.config)
        self.put('request.json', {'mode': 'prepare', 'inputsPin': self.pin(self.config)})
        self.doc['request'] = self.pin(self.request)
        witness = json.loads(self.witness.read_bytes())
        witness['resolvedInputs'] = self.pin(self.config)
        self.put('byte-witness.json', witness)
        self.doc['inputWitness'] = self.pin(self.witness)
        self.repin_root()
        with self.assertRaisesRegex(ValueError, 'original metadata'):
            self.verify()

    def test_witness_cannot_omit_required_fresh_byte_evidence(self):
        witness = json.loads(self.witness.read_bytes())
        witness['fresh'] = []
        self.put('byte-witness.json', witness)
        self.doc['inputWitness'] = self.pin(self.witness)
        self.repin_root()
        with self.assertRaisesRegex(ValueError, 'fresh witness'):
            self.verify()

    def test_blocked_metadata_and_null_pins_are_not_executable_inputs(self):
        for invalid in [json.loads(self.metadata.read_bytes()),
                        json.loads(self.metadata.read_bytes())['inputs']]:
            self.put('config.json', invalid)
            self.doc['config'] = self.pin(self.config)
            self.put('request.json', {'mode': 'prepare', 'inputsPin': self.pin(self.config)})
            self.doc['request'] = self.pin(self.request)
            self.repin_root()
            with self.assertRaises(ValueError):
                self.verify()

    def test_raw_numeric_request_refused(self):
        self.put('request.json', {'mode': 'prepare', 'inputsPin': self.pin(self.config), 'report': 12})
        self.doc['request'] = self.pin(self.request)
        self.repin_root()
        with self.assertRaisesRegex(ValueError, 'request'):
            self.verify()


if __name__ == '__main__':
    unittest.main()
