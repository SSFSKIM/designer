"""Post-authentication projection boundary on synthetic records, not a full799 capture fixture.

Admission/repeat/pixel validators have their own component fixtures. These tests isolate the
projection's row-preservation and API-routing contract with an already-admitted snapshot.
"""
import copy
import hashlib
import json
from pathlib import Path
import tempfile
import types
import unittest
from unittest.mock import patch

HERE=Path(__file__).resolve().parent


def source(path,name):
    value=types.ModuleType(name);value.__file__=str(path)
    exec(compile(path.read_bytes(),str(path),'exec'),value.__dict__)
    return value


def pin(name,letter):return {'path':name,'sha256':letter*64}


class ProjectionBoundaryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.m=source(HERE/'composed_completion.py','composed_reference_projection_tests')

    def fixture(self,directory):
        repo=Path(directory).resolve()
        rows=[dict(profile='p',renderer='webgpu',scene='canonical',statistic='T1-low',role='gate',
            currentEvidence=None,currentMetadata=None,native=.1,current=.2,B=.003,
            fidelity={'statistic':'T1-fine','native':.3,'current':.4,'reference':.5},
            support='Original support prose',historical=[{'frozen':.6}],missing=['Original missing description']),
            dict(profile='p',renderer='webgpu',scene='canonical',statistic='T1-full-silhouette',role='gate',
                 currentEvidence=pin('/synthetic/known.png','7'),currentMetadata=None,native=None,current=None,B=None,
                 support='Another original support',historical=[]),
            dict(profile='p',renderer='webgpu',scene='historical',statistic='low-end-path-level',
                 role='historical-prediction-check',currentEvidence=pin('/synthetic/history.png','8'),
                 currentMetadata=pin('/synthetic/history.json','9'),native=[1,2,3],current=[2,3,4],B=1,historical=[])]
        original=repo/'original.json';original.write_text(json.dumps({'cells':rows})+'\n')
        references={'path':'original.json','sha256':hashlib.sha256(original.read_bytes()).hexdigest()}
        instrument=pin('actual-canonical/root.json','a');composition=pin('composition.json','f')
        candidate=pin('original/candidate.json','c')
        member=dict(instrument=instrument,batch=pin('actual-canonical/batch.json','1'),
            contract=pin('actual-canonical/contract.json','2'),claim=pin('actual-canonical/started.json','3'),
            result=pin('actual-canonical/result.json','4'),output='/synthetic/output',
            run=dict(profile='p',renderer='webgpu',candidate=candidate,sceneSource='canonical',scenes=['canonical']),
            receipt=dict(profile='p',renderer='webgpu',scene='canonical',candidate=candidate,sceneSource='canonical',
                lane='current',origin={'kind':'fresh-canonical-recovery'},repeatPair=pin('/synthetic/pair.json','b'),
                repeatAdmission=pin('/synthetic/proof.json','d')))
        admitted=dict(composition=composition,originalInstrument=pin('actual-newbed/root.json','e'),
            originalRoot={'references':references},members=[member],candidates={candidate['sha256']:{'full':'endpoints'}})
        anchors=dict(currentComposition=composition,currentInstruments=[admitted['originalInstrument'],instrument],
            currentResults=[pin('actual-newbed/result.json','5'),member['result']],
            chainPins=[composition,admitted['originalInstrument'],instrument,member['batch'],member['result']])
        provenance=dict(capture=pin('/synthetic/current.png','6'),cell=pin('/synthetic/current.json','0'),
            report=pin('/synthetic/report.json','9'),repeatPair=member['receipt']['repeatPair'],
            repeatAdmission=member['receipt']['repeatAdmission'],reading='first',
            geometryDomain='canonical-reported-bounds-not-native-mask-equivalence',
            reportedSurfaces=[{'bounds':{'x':100,'y':78,'width':122,'height':46}}])
        return repo,rows,admitted,anchors,provenance

    def exercise(self,repo,rows,admitted,anchors,provenance):
        calls=[]
        def bind(actual,member,original):
            self.assertIs(actual,admitted);self.assertEqual(original,rows)
            calls.append(('bind',member['instrument']))
        def capture(member,candidate,*,argument_required):
            self.assertFalse(argument_required);self.assertEqual(candidate,{'full':'endpoints'})
            calls.append(('capture',member['instrument']))
            return {},{'scene':'canonical','pose':'active'},b'synthetic',[],copy.deepcopy(provenance)
        with (patch.object(self.m.C,'admit_composition',return_value=admitted),
              patch.object(self.m.C,'anchors',return_value=anchors),
              patch.object(self.m.C,'bind_member',side_effect=bind),
              patch.object(self.m.C.A,'capture_inputs',side_effect=capture)):
            result=self.m.complete_current_projection(repo,rows,admitted['composition'])
        return result,calls

    def test_fill_only_null_current_slots_keep_numerics_known_pins_support_and_history(self):
        with tempfile.TemporaryDirectory() as td:
            repo,rows,admitted,anchors,provenance=self.fixture(td);before=copy.deepcopy(rows)
            result,calls=self.exercise(repo,rows,admitted,anchors,provenance)
            self.assertEqual(rows,before);self.assertEqual(result['originalRows'],before)
            expected=copy.deepcopy(before)
            expected[0].update(currentEvidence=provenance['capture'],currentMetadata=provenance['cell'])
            expected[1]['currentMetadata']=provenance['cell']
            self.assertEqual(result['rows'],expected)
            self.assertEqual(result['schema'],'w50-admitted-current-reference-projection-2')
            self.assertEqual(result['completedKeys'],[[r[k] for k in ('profile','renderer','scene','statistic')]
                                                     for r in rows[:2]])
            for name,value in anchors.items():self.assertEqual(result[name],value)
            self.assertNotIn('currentInstrument',result)
            self.assertEqual(calls,[('bind',admitted['members'][0]['instrument']),
                                    ('capture',admitted['members'][0]['instrument'])])
            self.assertEqual(len(result['memberProvenance']),2)
            for record in result['memberProvenance']:
                for name in ('instrument','batch','contract','claim','result','run','receipt','output'):
                    self.assertEqual(record[name],admitted['members'][0][name])
                self.assertEqual(record['provenance'],provenance)

    def test_absent_original_fields_are_not_created_as_if_they_were_null_slots(self):
        with tempfile.TemporaryDirectory() as td:
            repo,rows,admitted,anchors,provenance=self.fixture(td)
            rows[0].pop('currentEvidence');rows[1].pop('currentMetadata')
            original=repo/'original.json';original.write_text(json.dumps({'cells':rows})+'\n')
            admitted['originalRoot']['references']['sha256']=hashlib.sha256(original.read_bytes()).hexdigest()
            result,_=self.exercise(repo,rows,admitted,anchors,provenance)
            expected=copy.deepcopy(rows);expected[0]['currentMetadata']=provenance['cell']
            self.assertEqual(result['rows'],expected)
            self.assertEqual(result['completedKeys'],[[rows[0][k] for k in ('profile','renderer','scene','statistic')]])

    def test_original_row_override_duplicate_or_missing_actual_canonical_member_refuses(self):
        for mutation in ('numeric','nonnull-pin','duplicate','wrong-source','missing'):
            with self.subTest(mutation=mutation),tempfile.TemporaryDirectory() as td:
                repo,rows,admitted,anchors,provenance=self.fixture(td)
                if mutation=='numeric':rows[0]['B']=100
                elif mutation=='nonnull-pin':rows[1]['currentEvidence']=pin('/forged.png','1')
                elif mutation=='duplicate':rows.append(copy.deepcopy(rows[0]))
                elif mutation=='wrong-source':admitted['members'][0]['run']['sceneSource']='w50'
                else:admitted['members']=[]
                with self.assertRaises(ValueError):self.exercise(repo,rows,admitted,anchors,provenance)

    def test_failed_actual_artifact_admission_cannot_emit_a_projection(self):
        with tempfile.TemporaryDirectory() as td:
            repo,rows,admitted,anchors,_=self.fixture(td)
            with (patch.object(self.m.C,'admit_composition',return_value=admitted),
                  patch.object(self.m.C,'bind_member'),
                  patch.object(self.m.C.A,'capture_inputs',side_effect=ValueError('second report invalid'))):
                with self.assertRaisesRegex(ValueError,'second report invalid'):
                    self.m.complete_current_projection(repo,rows,admitted['composition'])

    def test_source_probe_routes_only_source_metadata_without_composition_admission(self):
        composition=pin('composition.json','f')
        with (patch.object(self.m.C,'source_probe',return_value={'status':'SOURCE_ONLY'}) as probe,
              patch.object(self.m.C,'admit_composition',side_effect=AssertionError('must not admit'))):
            self.assertEqual(self.m.source_probe(composition,repo='/synthetic'),{'status':'SOURCE_ONLY'})
            probe.assert_called_once_with(repo='/synthetic',composition_pin=composition)


class ArchivedProjectionTests(unittest.TestCase):
    """Real immutable archived-pair binding/capture after the isolated composition boundary."""
    @classmethod
    def setUpClass(cls):
        cls.m=source(HERE/'composed_completion.py','archived_composed_reference_tests')
        cls.f=source(HERE.parent/'current-analysis-composed/synthetic.py','archived_projection_fixture')

    def fixture(self):return self.f.fixture(self,self.m.C)

    def complete(self,fixture):
        admitted=fixture['admitted'];rows=fixture['rows'][1:]
        with patch.object(self.m.C,'admit_composition',return_value=admitted):
            return self.m.complete_current_projection(fixture['repo'],rows,admitted['composition'])

    def test_real_repeat_binding_and_both_report_capture_preserve_canonical_actual_bounds(self):
        fixture=self.fixture();original=copy.deepcopy(fixture['rows'][1:]);result=self.complete(fixture)
        member=fixture['admitted']['members'][1];artifacts=member['receipt']['artifacts']
        expected=copy.deepcopy(original)
        expected[0].update(currentEvidence=artifacts['png'],currentMetadata=artifacts['cell'])
        self.assertEqual(result['originalRows'],original);self.assertEqual(result['rows'],expected)
        self.assertEqual(fixture['rows'][1:],original)
        self.assertEqual(result['currentInstruments'],[r['pin'] for r in fixture['admitted']['roots']])
        self.assertNotIn('currentInstrument',result)
        provenance=result['memberProvenance'][0]
        self.assertEqual(provenance['instrument'],member['instrument'])
        self.assertEqual(provenance['batch'],member['batch'])
        self.assertEqual(provenance['result'],member['result'])
        actual=provenance['provenance']
        self.assertEqual(actual['repeatPair'],member['receipt']['repeatPair'])
        self.assertEqual(actual['repeatAdmission'],member['receipt']['repeatAdmission'])
        self.assertEqual(actual['reading'],'first')
        self.assertEqual(actual['reportedSurfaces'][0]['bounds']['width'],122)
        self.assertEqual(actual['reportedSurfaces'][0]['bounds']['height'],46)
        self.assertEqual(actual['geometryDomain'],'canonical-reported-bounds-not-native-mask-equivalence')
        bound=self.m.C.A.bound_repeat(member)
        self.assertEqual(bound.pair['proof']['executionRootSha256'],member['instrument']['sha256'])
        self.assertNotEqual(bound.pair['proof']['executionRootSha256'],
                            fixture['admitted']['members'][0]['instrument']['sha256'])

    def test_swapped_member_root_refuses_before_archived_binding(self):
        fixture=self.fixture();members=fixture['admitted']['members']
        members[1]['instrument']=copy.deepcopy(members[0]['instrument'])
        with self.assertRaisesRegex(ValueError,'member'):self.complete(fixture)

    def test_changed_second_report_bytes_refuse_without_emitting_artifact_projection(self):
        fixture=self.fixture();member=fixture['admitted']['members'][1]
        pair=json.loads(Path(member['receipt']['repeatPair']['path']).read_bytes())
        Path(pair['second']['report']['path']).write_text('{}')
        original=copy.deepcopy(fixture['rows'][1:])
        with self.assertRaises(ValueError):self.complete(fixture)
        self.assertEqual(fixture['rows'][1:],original)


if __name__=='__main__':unittest.main()
