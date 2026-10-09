"""Real immutable archival binder/pages on generated files, after isolated composition admission."""
import copy
import json
from pathlib import Path
import types
import unittest

HERE=Path(__file__).resolve().parent


def source(path,name):
    module=types.ModuleType(name);module.__file__=str(path)
    exec(compile(path.read_bytes(),str(path),'exec'),module.__dict__)
    return module


class ArchivedCompositionTests(unittest.TestCase):
    def setUp(self):
        self.c=source(HERE/'analysis.py','archived_composed_consumer')
        self.f=source(HERE/'synthetic.py','archived_composed_fixture').fixture(self,self.c)

    def test_actual_roots_bind_their_own_real_pairs_and_validate_both_reports_without_live_context(self):
        admitted=self.f['admitted']
        for i,member in enumerate(admitted['members']):
            self.c.bind_member(admitted,member,self.f['rows'])
            _,_,raw,arguments,provenance=self.c.A.capture_inputs(member,self.f['candidate'])
            self.assertEqual(raw,Path(member['receipt']['artifacts']['png']['path']).read_bytes())
            self.assertEqual(provenance['reading'],'first')
            self.assertEqual(provenance['repeatAdmission'],member['receipt']['repeatAdmission'])
            self.assertEqual(arguments[0]['span'],44 if i==0 else 46)
            proof=json.loads(Path(member['receipt']['repeatAdmission']['path']).read_bytes())
            self.assertEqual(proof['executionRootSha256'],member['instrument']['sha256'])
            own=self.c.member_provenance(admitted,member)
            self.assertEqual(own['instrument'],admitted['roots'][i]['pin'])
            self.assertEqual(own['result'],admitted['resultDocuments'][i]['pin'])
            self.assertEqual(own['currentComposition'],admitted['composition'])
        self.assertNotEqual(admitted['members'][0]['instrument'],admitted['members'][1]['instrument'])

    def test_swapped_actual_instrument_refuses_before_archived_pair_is_read(self):
        admitted=self.f['admitted'];member=admitted['members'][1]
        member['instrument']=copy.deepcopy(admitted['members'][0]['instrument'])
        with self.assertRaisesRegex(ValueError,'member'):
            self.c.bind_member(admitted,member,self.f['rows'])

    def test_changed_second_report_is_not_hidden_by_a_complete_first_capture(self):
        admitted=self.f['admitted'];member=admitted['members'][1]
        pair=json.loads(Path(member['receipt']['repeatPair']['path']).read_bytes())
        Path(pair['second']['report']['path']).write_text('{}')
        with self.assertRaises(ValueError):self.c.bind_member(admitted,member,self.f['rows'])


if __name__=='__main__':unittest.main()
