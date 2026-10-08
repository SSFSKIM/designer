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
        self.active=self.put('active.json',{'synthetic':'original active'})
        self.receded=self.put('receded.json',{'synthetic':'original receded'})
        documents={p['path']:p['sha256'] for p in (self.active,self.receded)}
        self.web=dict(renderer=self.row['renderer'],sceneId=self.row['scene'],capturePath=
            f'materialProfile={self.active["path"]} sha256:{self.active["sha256"][:12]} '
            f'recededProfile={self.receded["path"]} sha256:{self.receded["sha256"][:12]}')
        self.matrix={'schemaVersion':5,'cells':[{'key':{'profileKey':self.row['profile'],
            'sceneId':self.row['scene'],'web':self.web},'state':'rest'}]}
        matrix=self.put('matrix.json',self.matrix)
        capture=dict(web=self.put('web.png',{'synthetic':'original current pixels'}),
            native=self.put('native.png',{'synthetic':'original native pixels'}),
            backdrop=self.put('backdrop.png',{'synthetic':'original backdrop'}),
            metadata=self.put('metadata.json',self.web),documents=documents.copy())
        self.inputs=dict(declaration=declaration,current=[{'matrix':matrix,'documents':documents}],
            references=[{'matrix':self.put('reference-matrix.json',self.matrix),'documents':documents.copy()}],captures={self.identity:capture},
            referenceCaptures={},python='not-executed')
        self.row.update(currentDocumentPair={'active.dark':self.active['sha256'],'receded.dark':self.receded['sha256']},
            currentGeneration=self.active['sha256'][:12]+'-'+self.receded['sha256'][:12],
            currentEvidence=copy.deepcopy(capture['web']),currentMetadata=copy.deepcopy(capture['metadata']),
            nativeEvidence=copy.deepcopy(capture['native']))
        inputs=self.put('inputs.json',self.inputs)
        axes={a:dict(state='NOT_APPLICABLE',reason='Outside source-owned population') for a in self.snapshot['axes']}
        axes['M1']=dict(state='MEASURED',verdict='failure',native=.1,candidate=.4,R=4)
        self.aggregate='M1/0.25/dark/rest'
        self.report=dict(cells={self.identity:axes},aggregates={self.aggregate:dict(state='MEASURED',verdict='failure',median=4,cells=2)},
            provenance=dict(owner=self.owner,current=self.inputs['current'],fixedReferences=self.inputs['references'],declaration=declaration),
            intrinsic={a:dict(state='UNMEASURED',reason='Intrinsic candidate check is separate') for a in ('X75','X76')},
            noNewTrade='Source owner laws retained')
        report=self.put('report.json',self.report)
        self.projection=dict(schema='w50-owner-evidence-1',row={k:self.row[k] for k in KEY},cellId=self.identity,inputsPin=inputs,
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

    def repin_inputs(self):
        self.inputs['current'][0]['matrix']=self.put('matrix.json',self.matrix)
        self.projection['inputsPin']=self.put('inputs.json',self.inputs)
        self.report['provenance'].update(current=copy.deepcopy(self.inputs['current']),
            fixedReferences=copy.deepcopy(self.inputs['references']))
        self.repin()

    def repin(self):
        self.projection['reportPin']=self.put('report.json',self.report)
        self.projection['contractsPin']=self.contract=self.put('contracts.json',self.snapshot)
        self.evidence=self.put('evidence.json',self.projection)

    def test_measured_failure_is_real_current_evidence_not_a_failed_preparation(self):
        self.check()

    def test_valid_same_generation_accepts_active_alias_and_receded_qualified_identity(self):
        self.check()
        self.row['currentGeneration']=self.active['sha256'][:12]
        self.check()

    def test_wrong_active_or_receded_generation_is_not_current_even_with_coherent_pins(self):
        for role in ('active','receded'):
            with self.subTest(role=role):
                before_inputs=copy.deepcopy(self.inputs); before_matrix=copy.deepcopy(self.matrix)
                other=self.put(f'other-{role}.json',{'synthetic':'retired '+role})
                old=self.active if role=='active' else self.receded
                descriptor='materialProfile' if role=='active' else 'recededProfile'
                self.matrix['cells'][0]['key']['web']['capturePath']=self.matrix['cells'][0]['key']['web']['capturePath'].replace(
                    f'{descriptor}={old["path"]} sha256:{old["sha256"][:12]}',
                    f'{descriptor}={other["path"]} sha256:{other["sha256"][:12]}')
                for docs in (self.inputs['current'][0]['documents'],self.inputs['captures'][self.identity]['documents']):
                    del docs[old['path']]; docs[other['path']]=other['sha256']
                self.inputs['captures'][self.identity]['metadata']=self.put('retired-metadata.json',self.matrix['cells'][0]['key']['web'])
                self.repin_inputs()
                with self.assertRaises(ValueError): self.check()
                self.inputs=before_inputs; self.matrix=before_matrix; self.repin_inputs()

    def test_wrong_current_capture_or_metadata_cannot_complete_original_reference(self):
        for field in ('web','metadata'):
            before=copy.deepcopy(self.inputs)
            content=self.web if field=='metadata' else {'synthetic':'another generation pixels'}
            self.inputs['captures'][self.identity][field]=self.put('other-'+field+'.json',content)
            self.repin_inputs()
            with self.subTest(field=field),self.assertRaises(ValueError): self.check()
            self.inputs=before; self.repin_inputs()

    def test_full_document_hash_cannot_hide_behind_matching_twelve_hex_descriptor(self):
        for role in ('active','receded'):
            original=self.active if role=='active' else self.receded
            changed=original['sha256'][:12]+('a' if original['sha256'][12]!='a' else 'b')+original['sha256'][13:]
            before=copy.deepcopy(self.inputs)
            self.inputs['current'][0]['documents'][original['path']]=changed
            self.inputs['captures'][self.identity]['documents'][original['path']]=changed
            self.repin_inputs()
            with self.subTest(role=role),self.assertRaisesRegex(ValueError,'document pair differs'):
                self.check()
            self.inputs=before; self.repin_inputs()

    def test_missing_original_metadata_is_not_permission_to_pick_another_generation(self):
        self.row.pop('currentMetadata')
        with self.assertRaises(ValueError): self.check()

    def test_wrong_generation_label_and_descriptor_role_swap_are_refused(self):
        self.row['currentGeneration']='c'*12+'-'+'d'*12
        with self.assertRaises(ValueError): self.check()
        self.row['currentGeneration']=self.active['sha256'][:12]
        self.matrix['cells'][0]['key']['web']['capturePath']=(
            f'materialProfile={self.receded["path"]} sha256:{self.receded["sha256"][:12]} '
            f'recededProfile={self.active["path"]} sha256:{self.active["sha256"][:12]}')
        self.repin_inputs()
        with self.assertRaises(ValueError): self.check()

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
                  'role':'gate','historical':[]}
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
