"""Synthetic source-owned owner evidence: null B is a law binding, not a waiver."""
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

KEY=('profile','renderer','scene','statistic')
HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('owner_checker',HERE/'owner_evidence.py')
O=importlib.util.module_from_spec(spec); spec.loader.exec_module(O)


class OwnerEvidence(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        self.repo=Path(self.tmp.name)
        self.owner=self.put('owner.ts',{'synthetic':'source-owned owner laws'})
        self.reader=self.put('reader.ts',{'synthetic':'source-owned reader'})
        self.row=dict(profile='apple-macos-27.0-1x-dark-standard-glass0.25',renderer='webgpu',
                      scene='photo__rrect-md__rest',statistic='owner-contracts')
        self.identity='/'.join(self.row[k] for k in ('profile','renderer','scene'))
        schema=dict(requiredFinite=[],requiredArrays=[],conditionalFinite=[],unmeasuredExceptions=[],aggregate=None)
        self.snapshot=dict(schema='w50-owner-contracts-1',ownerSource=self.owner,readerSources={'reader':self.reader},
            axes={axis:dict(sourceSelectors=[axis+'/source-law'],limits={'sourceLaw':axis},
                           applicability={'sourceSelection':True},exclusions={},readingSchema=copy.deepcopy(schema))
                  for axis in ('M1','M2','C1','X1','L1','E2','coherence')},
            intrinsic={axis:{'sourcePin':self.reader,'candidateCheckRequired':True} for axis in ('X75','X76')})
        self.snapshot['axes']['M1']['readingSchema'].update(requiredFinite=['native','candidate','R'],
            aggregate={'requiredFinite':['median','cells'],'nonemptyObjects':[]})
        contract=self.put('contracts.json',self.snapshot)
        declaration=self.put('scenes.json',{'scenes':[{'id':self.row['scene'],'state':'rest'}]})
        matrix=self.put('matrix.json',{'schemaVersion':5,'cells':[{'key':{
            'profileKey':self.row['profile'],'sceneId':self.row['scene'],'web':{'renderer':self.row['renderer']}},
            'state':'rest'}]})
        self.inputs=dict(declaration=declaration,current=[{'matrix':matrix,'documents':{}}],
                         references=[{'matrix':matrix,'documents':{}}],captures={},referenceCaptures={},python='not-executed')
        inputs=self.put('inputs.json',self.inputs)
        axes={a:dict(state='NOT_APPLICABLE',reason='Outside source-owned population') for a in self.snapshot['axes']}
        axes['M1']=dict(state='MEASURED',verdict='failure',native=.1,candidate=.4,R=4)
        self.aggregate='M1/0.25/dark/rest'
        self.report=dict(cells={self.identity:axes},aggregates={self.aggregate:dict(state='MEASURED',verdict='failure',median=4,cells=2)},
            provenance=dict(owner=self.owner,current=self.inputs['current'],fixedReferences=self.inputs['references'],declaration=declaration),
            intrinsic={a:dict(state='UNMEASURED',reason='Intrinsic candidate check is separate') for a in ('X75','X76')},
            noNewTrade='Source owner laws retained')
        report=self.put('report.json',self.report)
        self.projection=dict(schema='w50-owner-evidence-1',row=copy.deepcopy(self.row),cellId=self.identity,inputsPin=inputs,
            reportPin=report,contractsPin=contract,ownerSource=self.owner,
            axes={a:dict(evidence=axes[a],**{k:v for k,v in c.items() if k!='sourceSelectors'}) for a,c in self.snapshot['axes'].items()},
            aggregateKeys=[self.aggregate],intrinsic={a:dict(contract=c,evidence=self.report['intrinsic'][a],
                referenceReading='NOT_APPLICABLE',candidateCheckRequired=True) for a,c in self.snapshot['intrinsic'].items()})
        self.contract=contract
        self.evidence=self.put('evidence.json',self.projection)

    def put(self,name,value):
        path=self.repo/name; path.write_text(json.dumps(value)+'\n')
        return {'path':name,'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}

    def check(self):
        validator=O.OwnerEvidence(self.repo,self.contract,self.owner)
        validator.validate(self.row,self.evidence)
        validator.finish()

    def repin(self):
        self.projection['reportPin']=self.put('report.json',self.report)
        self.projection['contractsPin']=self.contract=self.put('contracts.json',self.snapshot)
        self.evidence=self.put('evidence.json',self.projection)

    def test_measured_failure_is_real_current_evidence_not_a_failed_preparation(self):
        self.check()

    def test_wrong_cell_or_contract_scope_is_refused(self):
        for mutate in (lambda p:p['row'].update(scene='other'),
                       lambda p:p.update(cellId='other'),
                       lambda p:p['axes'].pop('E2'),
                       lambda p:p['axes']['M1']['limits'].update(inventedBudget=1)):
            original=copy.deepcopy(self.projection); mutate(self.projection)
            self.evidence=self.put('evidence.json',self.projection)
            with self.assertRaises(ValueError): self.check()
            self.projection=original

    def test_absent_nonfinite_or_flag_only_measured_reading_is_refused(self):
        for value in (None,float('nan'),True):
            self.report['cells'][self.identity]['M1']['candidate']=value
            self.projection['axes']['M1']['evidence']=copy.deepcopy(self.report['cells'][self.identity]['M1'])
            self.repin()
            with self.subTest(value=value),self.assertRaises(ValueError): self.check()
        self.report['cells'][self.identity]['M1']={'state':'MEASURED','verdict':'within'}
        self.projection['axes']['M1']['evidence']=self.report['cells'][self.identity]['M1']; self.repin()
        with self.assertRaises(ValueError): self.check()

    def test_source_pin_and_raw_prepare_report_are_authority(self):
        self.projection['axes']['M1']['evidence']={**self.report['cells'][self.identity]['M1'],'candidate':.2}
        self.evidence=self.put('evidence.json',self.projection)
        with self.assertRaises(ValueError): self.check()
        self.projection['axes']['M1']['evidence']=self.report['cells'][self.identity]['M1']
        self.snapshot['ownerSource']=self.reader; self.repin()
        with self.assertRaises(ValueError): self.check()

    def test_missing_or_partial_aggregate_cannot_become_complete_current_evidence(self):
        for aggregate in ({'state':'UNMEASURED','reason':'partial bed'},
                          {'state':'MEASURED','verdict':'within'}):
            self.report['aggregates'][self.aggregate]=aggregate; self.repin()
            with self.assertRaises(ValueError): self.check()
        self.report['aggregates'][self.aggregate]={'state':'MEASURED','median':4,'cells':2}
        self.projection['aggregateKeys']=[]; self.repin()
        with self.assertRaises(ValueError): self.check()

    def test_only_source_named_unmeasured_exceptions_are_allowed(self):
        axis='L1'; identity=self.row['profile']+'/'+self.row['scene']
        exception={'kind':'named-cell','identity':'profile/scene','keys':[identity],
                   'evidenceEquals':{'namedExclusion':True}}
        self.snapshot['axes'][axis]['readingSchema']['unmeasuredExceptions']=[exception]
        evidence={'state':'UNMEASURED','reason':'Source-owned absent mean','namedExclusion':True}
        self.report['cells'][self.identity][axis]=evidence
        self.projection['axes'][axis]['evidence']=evidence
        self.projection['axes'][axis]['readingSchema']=self.snapshot['axes'][axis]['readingSchema']
        self.repin(); self.check()
        self.report['cells'][self.identity][axis]['namedExclusion']=False; self.repin()
        with self.assertRaises(ValueError): self.check()

    def test_null_owner_budget_requires_complete_matching_owner_evidence(self):
        spec=importlib.util.spec_from_file_location('owner_prefit',HERE/'prefit.py')
        P=importlib.util.module_from_spec(spec); spec.loader.exec_module(P)
        original={**self.row,'status':'UNMEASURED','B':None,'support':'original owner scope',
                  'role':'gate','currentDocumentPair':{'active':'a'},'currentGeneration':'g',
                  'historical':[],'nativeEvidence':self.owner,'currentEvidence':self.reader}
        completed={**original,'status':'MEASURED','ownerEvidence':self.evidence}
        keys=[[original[k] for k in KEY]]
        def check(row=completed):
            P.validate_completion({'cells':[original]},{'cells':[row]},[],self.repo,
                owner_budget_keys=keys,owner_contracts=self.contract,owner_source=self.owner)
        check()
        for bad in ({**completed,'B':1},{**completed,'status':'REPORTED'},
                    {k:v for k,v in completed.items() if k!='ownerEvidence'}):
            with self.assertRaises(ValueError): check(bad)
        original['native']=.5; completed['native']=.6
        with self.assertRaises(ValueError): check()

    def test_other_rows_do_not_inherit_null_owner_budget(self):
        spec=importlib.util.spec_from_file_location('other_prefit',HERE/'prefit.py')
        P=importlib.util.module_from_spec(spec); spec.loader.exec_module(P)
        row={**self.row,'statistic':'T1-full-silhouette','role':'gate','support':'silhouette',
             'currentDocumentPair':{'active':'a'},'historical':[],'B':None,'status':'UNMEASURED',
             'nativeEvidence':self.owner,'currentEvidence':self.reader}
        complete={**row,'native':1,'current':1,'status':'MEASURED','ownerEvidence':self.evidence}
        with self.assertRaises(ValueError):
            P.validate_completion({'cells':[row]},{'cells':[complete]},[],self.repo,
                owner_budget_keys=[],owner_contracts=self.contract,owner_source=self.owner)

    def test_intrinsic_checks_are_never_fabricated_scalar_reference_readings(self):
        self.projection['intrinsic']['X75']['referenceReading']=0
        self.evidence=self.put('evidence.json',self.projection)
        with self.assertRaises(ValueError): self.check()


if __name__=='__main__': unittest.main()
