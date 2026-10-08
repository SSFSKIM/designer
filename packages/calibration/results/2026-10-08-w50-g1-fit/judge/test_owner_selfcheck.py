"""The owner self-check on the committed owner evidence (DL5m 1 and 5; DL5o).

Current read as the candidate passes every owner-contract cell, context cell and aggregate at
the report the judge config pins, through the judge's own grade_owner_report, and X75/X76 are
GRADED on the hypothetical identity candidate through the frozen owner engine (DL5o): twelve
X75 endpoints and X76 at both positions PASS. The superseded evidence reproduces the defect
7e621f344 fixed (eight context cells UNMEASURED on L1); an identity candidate missing one
required hold FAILS X76 at its position instead of being counted; and a report off the pinned
membership refuses. Statuses, counts and identities only.
"""
import copy
import json
import tempfile
from pathlib import Path
import sys
import types
import unittest

HERE = Path(__file__).resolve().parent
OWNER = HERE.parent/'owner'
INVENTORY = HERE.parents[1]/'2026-10-08-w50-g0-declaration/references.json'
NAMED = sorted(f'apple-macos-27.0-{s}x-dark-standard-glass{g}/webgpu/dark-solid__{c}__inactive'
               for s in (1, 2) for g in ('0.25', '0.5') for c in ('capsule-button', 'rrect-md'))
AGGREGATES = ['C1', 'M1/0.25/dark/inactive', 'M1/0.25/dark/rest', 'M1/0.5/dark/inactive', 'M1/0.5/dark/rest']


def source(path, name):
    module = types.ModuleType(name)
    module.__file__ = str(path)
    sys.modules[name] = module
    exec(compile(Path(path).read_bytes(), str(path), 'exec', dont_inherit=True), module.__dict__)
    return module


S = source(HERE/'owner_selfcheck.py', 'w50_owner_selfcheck_under_test')


def read(path): return S.J.parse(Path(path).read_bytes())


class OwnerSelfcheckTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.keys = S.owner_keys(read(INVENTORY))

    def test_current_as_candidate_passes_every_owner_check_at_the_pinned_report(self):
        result = S.selfcheck(HERE/'config.json')
        self.assertEqual(result['status'], 'PASS')
        self.assertEqual(result['counts'], {'cells': 745, 'ownerCells': 640, 'contextCells': 105, 'aggregates': 5})
        self.assertEqual(result['statuses'], {'ownerCells': {'PASS': 640}, 'contextCells': {'PASS': 105},
                                              'aggregates': {'PASS': 5}, 'intrinsic': {'PASS': 14}})
        self.assertEqual([a['name'] for a in result['aggregates']], AGGREGATES)
        self.assertEqual(result['notPassing'], [])
        self.assertEqual(sorted((i['name'], i['member']) for i in result['intrinsic'] if i['name'] == 'X76'),
                         [('X76', '0.25'), ('X76', '0.5')])
        self.assertEqual(sum(i['name'] == 'X75' for i in result['intrinsic']), 12)
        # DL5o (a): at 0.5 the historical family entries hold; only the unrecorded leaves need holds.
        self.assertEqual(result['familyHolds']['0.5']['heldByFamily'],
                         {'backdropToneAnchorX': 'backdropToneResponse', 'outerShadow.liftAmplitude': 'outerShadow',
                          'outerShadow.thinOcclusionDark': 'outerShadow'})
        self.assertEqual(result['familyHolds']['0.25']['heldByFamily'], {})

    def test_an_identity_candidate_missing_a_required_hold_fails_x76_rather_than_being_counted(self):
        identity = read(S.IDENTITY)
        with tempfile.TemporaryDirectory() as scratch:
            methods = read(S.REPO/identity['recededRecords']['0.5']['methods']['path'])
            del methods['methods']['backdropToneBlackStrength']
            path = Path(scratch)/'receded-methods.json'
            path.write_text(json.dumps(methods))
            identity['recededRecords']['0.5']['methods'] = {'path': str(path), 'sha256': S.sha(path)}
            records = Path(scratch)/'records.json'
            records.write_text(json.dumps(identity))
            result = S.selfcheck(HERE/'config.json', S.OWNER_CONFIG, records)
        self.assertEqual(result['status'], 'FAIL')
        self.assertEqual([i for i in result['intrinsic'] if i['status'] != 'PASS'],
                         [{'name': 'X76', 'member': '0.5', 'status': 'FAIL'}])
        self.assertEqual(result['familyHolds']['0.5']['missing'], ['backdropToneBlackStrength'])

    def test_without_intrinsic_evidence_the_placeholder_is_counted_not_graded(self):
        report = read(OWNER/'evidence-r3/prepare.json')
        result = S.grade(report, read(OWNER/'evidence-r3/contracts.json'), self.keys, S.membership_of(report))
        self.assertEqual(result['intrinsicNotGraded'], {'UNMEASURED': 4})
        self.assertNotIn('intrinsic', result)

    def test_superseded_evidence_reproduces_the_eight_unmeasured_context_cells(self):
        report = read(OWNER/'evidence/prepare.json')
        result = S.grade(report, read(OWNER/'evidence/contracts.json'), self.keys, S.membership_of(report))
        self.assertEqual(result['status'], 'FAIL')
        self.assertEqual(result['statuses'], {'ownerCells': {'PASS': 640}, 'contextCells': {'PASS': 97, 'UNMEASURED': 8},
                                              'aggregates': {'PASS': 5}})
        self.assertEqual(result['notPassing'], [{'id': i, 'axes': ['L1']} for i in NAMED])

    def test_a_report_off_the_pinned_membership_refuses(self):
        report = read(OWNER/'evidence-r3/prepare.json')
        contracts = read(OWNER/'evidence-r3/contracts.json')
        membership = S.membership_of(report)
        context = next(i for i in sorted(report['cells']) if i not in {'/'.join(k[:3]) for k in self.keys})
        for label, change in (('dropped context cell', lambda r: r['cells'].pop(context)),
                              ('dropped aggregate', lambda r: r['aggregates'].pop('M1/0.5/dark/rest')),
                              ('dropped C1', lambda r: r['aggregates'].pop('C1')),
                              ('added cell', lambda r: r['cells'].__setitem__('p/webgpu/s', r['cells'][context]))):
            with self.subTest(label):
                changed = copy.deepcopy(report); change(changed)
                with self.assertRaisesRegex(ValueError, 'membership'):
                    S.grade(changed, contracts, self.keys, membership)


if __name__ == '__main__':
    unittest.main()
