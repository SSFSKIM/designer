"""Refusal tests: a draft or partial reference set must never authorise fitting."""
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('w50_declare', HERE / 'declare.py')
D = importlib.util.module_from_spec(spec)
spec.loader.exec_module(D)


class Declaration(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.directory = self.root / 'declaration'
        self.directory.mkdir()
        self.source = self.root / 'instrument.py'
        self.source.write_text('value = 1\n')
        sources = [{'path': 'instrument.py', 'sha256': D.sha(self.source)}]
        self.one = {'schema': 'w50-declaration-1', 'sources': sources,
                    'scope': ['dark.glass0.25', 'dark.glass0.5']}
        self.write('declaration.json', self.one)
        self.two = {'schema': 'w50-fit-declaration-1', 'sources': sources,
                    'partOneSha256': D.sha(self.directory / 'declaration.json'),
                    'noPostGateAmendment': True, 'onFailure': D.FAILURE,
                    'references': 'references.json', 'requiredEvidence': ['references'],
                    'conditionalX41': D.X41_SCOPE}
        self.write('fit-declaration.json', self.two)

    def tearDown(self):
        self.tmp.cleanup()

    def write(self, name, value):
        (self.directory / name).write_text(json.dumps(value) + '\n')

    def seal(self):
        D.seal(self.directory, self.root, self.root / 'activity')

    def test_unsealed_draft_cannot_authorise_native_launch(self):
        with self.assertRaises((ValueError, FileNotFoundError)):
            D.verify(self.directory, self.root)

    def test_changed_instrument_refused_even_before_seal(self):
        self.source.write_text('value = 2\n')
        with self.assertRaisesRegex(ValueError, 'source'):
            self.seal()

    def test_part_two_cannot_bind_another_part_one(self):
        self.two['partOneSha256'] = '0' * 64
        self.write('fit-declaration.json', self.two)
        with self.assertRaisesRegex(ValueError, 'part one'):
            self.seal()

    def test_post_gate_amendment_and_extra_x41_scope_refused(self):
        for field, value in [('noPostGateAmendment', False),
                             ('conditionalX41', {**D.X41_SCOPE, 'light': 'allowed'})]:
            with self.subTest(field=field):
                changed = {**self.two, field: value}
                self.write('fit-declaration.json', changed)
                with self.assertRaises(ValueError):
                    self.seal()

    def test_native_seal_does_not_bless_missing_prefit_evidence(self):
        self.seal()
        D.verify(self.directory, self.root, phase='native')
        with self.assertRaises((ValueError, FileNotFoundError)):
            D.verify(self.directory, self.root, phase='fit')

    def test_no_reseal_or_seal_after_activity(self):
        self.seal()
        with self.assertRaisesRegex(ValueError, 'Existing'):
            self.seal()
        for p in self.directory.glob('*.sha256'):
            p.unlink()
        activity = self.root / 'activity'
        activity.mkdir()
        (activity / 'capture.json').write_text('{}')
        with self.assertRaisesRegex(ValueError, 'activity'):
            self.seal()

    def test_escaped_source_refused(self):
        self.one['sources'][0]['path'] = '../outside.py'
        self.write('declaration.json', self.one)
        with self.assertRaisesRegex(ValueError, 'source'):
            self.seal()

    def test_blind_reference_requires_hashes_but_refuses_early_statistics(self):
        evidence = self.root / 'archive.json'
        evidence.write_text('admitted archive bytes')
        pin = {'path': str(evidence), 'sha256': D.sha(evidence)}
        cell = {'profile': 'p', 'renderer': 'webgpu', 'scene': 's', 'statistic': 'T1',
                'status': 'SEALED_BLIND', 'role': 'blind', 'B': None,
                'nativeEvidence': pin, 'currentEvidence': pin, 'support': 'deep8',
                'currentDocumentPair': {'active.dark': 'a'*64, 'receded.dark': 'b'*64}}
        D.validate_references({'cells': [cell]}, self.root)
        with self.assertRaisesRegex(ValueError, 'blind'):
            D.validate_references({'cells': [{**cell, 'native': 23}]}, self.root)

    def test_self_sealed_web_contract_is_not_authorised_by_native_root(self):
        audit = self.directory / 'audit'
        audit.mkdir()
        contract = audit / 'execution-contract.json'
        contract.write_text('{}\n')
        sidecar = Path(str(contract) + '.sha256')
        sidecar.write_text(f'{D.sha(contract)}  {contract.name}\n')
        with self.assertRaisesRegex(ValueError, 'pre-fit'):
            D.require_execution_contract({'sources': []}, self.directory, self.root)
        pins = [{'path': str(p.relative_to(self.root)), 'sha256': D.sha(p)}
                for p in (contract, sidecar)]
        D.require_execution_contract({'sources': pins}, self.directory, self.root)
        contract.write_text('{"newBatch":true}\n')
        sidecar.write_text(f'{D.sha(contract)}  {contract.name}\n')
        with self.assertRaises(ValueError):
            D.require_execution_contract({'sources': pins}, self.directory, self.root)

    def test_placeholder_proof_cannot_complete_prefit_gate(self):
        for proof in ({}, {'status': 'PASS'}, {'status': 'UNMEASURED', 'kind': 'newBedRendererAdapter'}):
            with self.subTest(proof=proof), self.assertRaises(ValueError):
                D.validate_proof(proof, 'newBedRendererAdapter', self.root)

    def test_reference_validator_refuses_duplicate_missing_and_nonfinite(self):
        cell = {'profile': 'p', 'renderer': 'webgpu', 'scene': 's', 'statistic': 'T1',
                'status': 'UNMEASURED', 'B': None}
        for rows in ([cell], [cell, cell], [{**cell, 'status': 'MEASURED', 'B': float('nan')}]):
            with self.subTest(rows=rows), self.assertRaises(ValueError):
                D.validate_references({'cells': rows}, self.root)


if __name__ == '__main__':
    unittest.main()
