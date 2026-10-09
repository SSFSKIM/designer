"""Typed three-run provenance preserves original G0 prose and every native source field."""
import copy
from pathlib import Path
import types
import unittest

HERE = Path(__file__).resolve().parent


def source(path):
    module = types.ModuleType('w50_synthetic_three_run_producer'); module.__file__ = str(path)
    exec(compile(path.read_bytes(), str(path), 'exec'), module.__dict__)
    return module


class NativeEvidenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls): cls.e = source(HERE/'native_evidence.py')

    def fixture(self):
        row = dict(profile='profile', renderer='css', scene='cell', statistic='deep8-channel-median',
            nativeIdentity='profile/cell', referenceIdentity='profile/no-glass', role='validation',
            support='Original supplied path >=8 CSS px inward; independent central square.',
            currentDocumentPair={'active.dark': 'a'*64, 'receded.dark': 'b'*64}, B=None)
        evidence = [dict(path=f'pass/run-{n}/profile/cell.png', sha256=str(n)*64, roles=['validation'],
            kind='frame', cell='profile/cell', run=n, declarationSha256='d'*64, manifestSha256='e'*64,
            native=dict(sceneId='cell', suppliedPaths=[{'kind': 'rrect', 'elements': [1, 2, 3]}],
                        extraAttestation={'preserve': ['opaque', 'metadata']})) for n in (1, 2, 3)]
        cell = dict(id='profile/cell', profile='profile', scene='cell', role='validation',
            reference='profile/no-glass', statistics={'deep8-channel-median': {'value': [20, 20, 20]}},
            runs=[dict(run=n, dependency='profile/no-glass', evidence=record, readings={'not': 'envelope'})
                  for n, record in zip((1, 2, 3), evidence)])
        provenance = dict(nativeRead={'path': 'identification/validation.json.gz', 'sha256': 'f'*64},
            nativeBatch={'path': 'native/read-batch.json', 'sha256': 'a'*64},
            nativeExport={'role': 'validation', 'root': '/synthetic/validation', 'indexSha256': 'b'*64})
        return row, cell, provenance

    def test_envelope_keeps_original_prose_and_all_three_full_native_records(self):
        row, cell, provenance = self.fixture(); before = copy.deepcopy((row, cell, provenance))
        result = self.e.envelope(row, cell, provenance)
        self.assertEqual(result, dict(schema='w50-native-three-run-evidence-1', profile='profile',
            scene='cell', statistic='deep8-channel-median', nativeIdentity='profile/cell',
            referenceIdentity='profile/no-glass', role='validation', support=row['support'],
            runs=[copy.deepcopy(run['evidence']) for run in cell['runs']], **provenance))
        self.assertEqual((row, cell, provenance), before)
        result['runs'][0]['native']['extraAttestation']['preserve'].append('changed')
        self.assertEqual((row, cell, provenance), before)
        self.assertNotIn('value', result); self.assertNotIn('B', result)

    def test_additive_current_projection_carries_envelope_beside_original_reference(self):
        row, cell, provenance = self.fixture()
        row.update(currentGeneration='original-generation', nativeEvidence=None, currentEvidence=None)
        before = copy.deepcopy(row)
        analysis = source(HERE/'analysis.py')
        measured = dict(profile=row['profile'], renderer=row['renderer'], scene=row['scene'], role=row['role'],
                        statistics={row['statistic']: {'value': [30, 30, 30], 'support': 'deep8'}})
        result = analysis.project_native_rows([row], measured, provenance, cell)
        self.assertEqual(result[0]['originalReference'], before)
        self.assertEqual(result[0]['nativeEvidenceEnvelope'], self.e.envelope(row, cell, provenance))
        self.assertEqual(result[0]['measurement']['support'], 'deep8')
        self.assertEqual(result[0]['nativeEvidenceEnvelope']['support'], row['support'])
        self.assertIsNone(result[0]['originalReference']['nativeEvidence'])
        self.assertEqual(row, before)

    def test_refuses_omitted_reordered_or_different_role_runs(self):
        for mutation in ('missing', 'reordered', 'role', 'dependency', 'nativeIdentity', 'statistic'):
            with self.subTest(mutation=mutation):
                row, cell, provenance = self.fixture()
                if mutation == 'missing': cell['runs'].pop()
                elif mutation == 'reordered': cell['runs'].reverse()
                elif mutation == 'role': cell['runs'][1]['evidence']['roles'] = ['blind']
                elif mutation == 'dependency': cell['runs'][1]['dependency'] = 'other/no-glass'
                elif mutation == 'nativeIdentity': row['nativeIdentity'] = 'other/cell'
                else: row['statistic'] = 'different-statistic'
                with self.assertRaises(ValueError): self.e.envelope(row, cell, provenance)

    def test_rejects_changed_support_or_document_as_png_and_unpinned_report(self):
        for mutation in ('support', 'document', 'report', 'export'):
            with self.subTest(mutation=mutation):
                row, cell, provenance = self.fixture()
                if mutation == 'support': row['support'] = {'mask': 'deep8'}
                elif mutation == 'document': cell['runs'][0]['evidence']['path'] = 'profile.json'
                elif mutation == 'report': provenance['nativeRead']['sha256'] = 'not-a-pin'
                else: provenance['nativeExport']['role'] = 'blind'
                with self.assertRaises(ValueError): self.e.envelope(row, cell, provenance)


if __name__ == '__main__': unittest.main()
