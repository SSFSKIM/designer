import copy
import hashlib
import importlib.util
from pathlib import Path
import tempfile
import unittest
import types
H=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('authority',H/'authority.py');A=importlib.util.module_from_spec(s);s.loader.exec_module(A)
class Authority(unittest.TestCase):
    def test_initializer_is_not_a_post_capture_fitter_placeholder(self):
        initializer=types.SimpleNamespace(initialize=lambda:None,assemble=lambda:None,bind_arguments=lambda:None)
        A.instrument_interface('initializer',initializer)
        with self.assertRaises(ValueError):A.instrument_interface('fit',initializer)
        with self.assertRaises(ValueError):A.instrument_interface('capture',types.SimpleNamespace(capture=lambda:None,verify=lambda:None))
    def test_native_role_must_carry_its_read_only_pre_start_admission(self):
        prepared=types.SimpleNamespace(prepare=lambda:None,verify=lambda:None)
        with self.assertRaisesRegex(ValueError,'role interface'):A.instrument_interface('native',prepared)
        A.instrument_interface('native',types.SimpleNamespace(admit=lambda:None,**vars(prepared)))
    def test_owner_role_must_carry_its_metadata_only_admission(self):
        evaluated=types.SimpleNamespace(evaluate=lambda:None)
        with self.assertRaisesRegex(ValueError,'role interface'):A.instrument_interface('owner',evaluated)
        A.instrument_interface('owner',types.SimpleNamespace(admit=lambda:None,**vars(evaluated)))
    def test_fit_role_must_export_the_record_the_gate_rederives(self):
        evaluated=types.SimpleNamespace(evaluate=lambda:None)
        with self.assertRaisesRegex(ValueError,'role interface'):A.instrument_interface('fit',evaluated)
        A.instrument_interface('fit',types.SimpleNamespace(fit_record=lambda:None,**vars(evaluated)))
    def test_missing_real_components_cannot_form_live_root(self):
        for roles in ({},{'fit':{}},{r:{} for r in A.ROLES}):
            with self.assertRaises(ValueError):A.instrument_shape(roles)
    def test_prospective_components_have_both_source_and_config_not_status_placeholders(self):
        p={'path':'source.py','sha256':'a'*64};c={'path':'config.json','sha256':'b'*64}
        roles={r:{'entrypoint':p,'config':c} for r in A.ROLES};A.instrument_shape(roles)
        for field in ('entrypoint','config'):
            broken={**roles,'judge':{**roles['judge'],field:{'status':'PENDING'}}}
            with self.assertRaises(ValueError):A.instrument_shape(broken)
    def test_root_refuses_singular_current_aliases_before_any_other_admission(self):
        with tempfile.TemporaryDirectory() as t:
            repo=Path(t).resolve()
            path=repo/'packages/calibration/results/2026-10-08-w50-g1-fit/live-execution/execution-root.json'
            doc={'repo':str(repo),'schema':'w50-g1-execution-root-1','lifecycle':'logical-phase-attempts-1',
                 'quarantine':'instrument-api-role-discipline-1'}
            with self.assertRaisesRegex(ValueError,'live component'):A.validate_body(path,doc)
            for alias in ('currentInstrument','currentResults'):
                with self.subTest(alias=alias),self.assertRaisesRegex(ValueError,'Wrong live lifecycle root'):
                    A.validate_body(path,{**doc,alias:{'path':'x','sha256':'a'*64}})


def pin(name):return {'path':name,'sha256':hashlib.sha256(name.encode()).hexdigest()}


class CurrentAuthority(unittest.TestCase):
    def setUp(self):
        roots=[{'pin':pin('current3-root'),'document':{}},{'pin':pin('canonical3-root'),'document':{}}]
        results=[{'pin':pin('current3-result')},{'pin':pin('canonical3-result')}]
        chain=[pin('chain-a'),pin('chain-b'),pin('chain-c')];baseline=[pin('baseline-025'),pin('baseline-05')]
        self.current={'roots':roots,'resultDocuments':results,'chainPins':chain,'candidates':baseline}
        self.doc={'currentComposition':pin('composition'),'currentEvidence':pin('evidence'),
                  'references':pin('references'),'baselineDocuments':copy.deepcopy(baseline)}
        self.doc['inputs']=[self.doc['currentComposition'],self.doc['currentEvidence'],*copy.deepcopy(chain)]
        self.evidence={'schema':'w50-completed-current-evidence-2','status':'EVIDENCE_ONLY',
            'currentComposition':self.doc['currentComposition'],'currentInstruments':[r['pin'] for r in roots],
            'currentResults':[r['pin'] for r in results],'chainPins':copy.deepcopy(chain),
            'originals':{'references':self.doc['references']}}
    def test_exact_ordered_composition_is_admitted(self):
        A.current_authority(self.doc,self.evidence,self.current)
    def test_reordered_missing_or_extra_chain_entries_refuse(self):
        for field in ('currentInstruments','currentResults','chainPins'):
            for mutation in ('reordered','missing','extra'):
                evidence=copy.deepcopy(self.evidence);value=evidence[field]
                if mutation=='reordered':value.reverse()
                elif mutation=='missing':value.pop()
                else:value.append(pin('foreign'))
                with self.subTest(field=field,mutation=mutation),self.assertRaisesRegex(ValueError,'composed authority'):
                    A.current_authority(self.doc,evidence,self.current)
    def test_chain_pin_absent_from_root_inputs_refuses(self):
        for item in (self.doc['currentComposition'],self.doc['currentEvidence'],self.current['chainPins'][1]):
            doc=copy.deepcopy(self.doc);doc['inputs'].remove(item)
            with self.subTest(item=item['path']),self.assertRaisesRegex(ValueError,'omitted from root'):
                A.current_authority(doc,self.evidence,self.current)
    def test_flattened_singular_current_instrument_refuses(self):
        evidence={**self.evidence,'currentInstrument':self.evidence['currentInstruments'][0]}
        with self.assertRaisesRegex(ValueError,'composed authority'):A.current_authority(self.doc,evidence,self.current)

if __name__=='__main__':unittest.main()
