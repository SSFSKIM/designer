"""Deterministic evidence joins on synthetic records only; no analytical reader is invoked."""
import copy
from pathlib import Path
import types
import unittest

HERE = Path(__file__).resolve().parent
PROFILE = 'apple-macos-27.0-1x-dark-standard-glass0.5'


def load():
    module = types.ModuleType('w50_synthetic_completion'); module.__file__ = str(HERE/'assembler.py')
    exec(compile((HERE/'assembler.py').read_bytes(), str(HERE/'assembler.py'), 'exec'), module.__dict__)
    return module


def pin(name, digit='a'): return {'path': name, 'sha256': digit*64}


def original(statistic, *, scene='cell-grey-004-s096__rest', role='calibration', position='0.5'):
    p = PROFILE.replace('glass0.5', 'glass'+position)
    return dict(profile=p, renderer='webgpu', scene=scene, statistic=statistic, role=role,
        support='Original G0 supplied path prose, never the compact mask label.', status='UNMEASURED',
        currentDocumentPair={'active.dark': 'a'*64, 'receded.dark': 'b'*64}, currentGeneration='a'*12,
        nativeEvidence=None, currentEvidence=None, currentMetadata=None, B=None, historical=[],
        missing=['Historical missing description'])


def current_evidence(row, *, value=None, native=None, repeat=None, required=True):
    return dict(**{k: row[k] for k in ('profile','renderer','scene','statistic')}, role=row['role'],
        evidenceKind='completed-current-gate0', originalReference=copy.deepcopy(row),
        currentDocumentPair=copy.deepcopy(row['currentDocumentPair']), currentGeneration=row['currentGeneration'],
        measurement=dict(status='MEASURED' if required else 'REPORTED', measurementStatus='MEASURED',
            required=required, support='deep8', units='encoded-RGB-codes' if isinstance(native,list) else 'linear-luma',
            value=value, nativeValue=native, nativeRepeat=repeat,
            runValues=[copy.deepcopy(value)]*3, nativeSupportWitnesses=[]),
        nativeEvidenceEnvelope=dict(schema='w50-native-three-run-evidence-1',profile=row['profile'],
            scene=row['scene'],statistic=row['statistic'],nativeIdentity=row['nativeIdentity'],
            referenceIdentity=row['referenceIdentity'],role=row['role'],support=row['support'],
            runs=[{'run': n, 'sha256': str(n)*64} for n in (1,2,3)],
            nativeRead=pin('native-role.json.gz'),nativeBatch=pin('native/read-batch.json'),
            nativeExport={'role':row['role'],'root':'/synthetic/native','indexSha256':'b'*64}),
        provenance=dict(capture=pin('/synthetic/current.png','c'),cell=pin('/synthetic/cell.json','d'),
            report=pin('/synthetic/report.json','e'),nativeRead=pin('native-role.json.gz'),
            candidateDocument=pin('actual-gate0.json','f')))


def native_row(statistic='deep8-channel-median'):
    row=original(statistic)
    row.update(nativeIdentity=row['profile']+'/'+row['scene'],referenceIdentity=row['profile']+'/no-glass')
    return row


def canonical_record(row, readings):
    return dict(**{k: row[k] for k in ('profile','renderer','scene','statistic','role')},
        status='MEASURED',reference=copy.deepcopy(row),readings=copy.deepcopy(readings),runs=[{'label':str(n)} for n in range(7)],
        pins=dict(native=row['nativeEvidence'],current=row['currentEvidence'],currentMetadata=row['currentMetadata'],
                  background=pin('/synthetic/background.png'),publishedManifest=pin('/synthetic/manifest.json'),
                  scenes=pin('/synthetic/scenes.json')),source={'kind':'W29','frameHashBinding':'original'})


class NativeJoins(unittest.TestCase):
    @classmethod
    def setUpClass(cls): cls.a=load()
    def artifacts(self): return self.a.Artifacts('/synthetic/completion')

    def test_native_values_and_own_repeat_budget_do_not_replace_original_prose_or_history(self):
        row=native_row(); before=copy.deepcopy(row)
        evidence=current_evidence(row,value=[22,23,24],native=[20,21,22],
            repeat={'spreadCodes':[0,1,0],'barCodes':[.5,.5,.5],'passes':True})
        artifacts=self.artifacts()
        result=self.a.complete_native(row,evidence,artifacts,(),())
        self.assertEqual(result['native'],[20,21,22]); self.assertEqual(result['current'],[22,23,24])
        self.assertEqual(result['B'],1); self.assertEqual(result['status'],'MEASURED')
        self.assertEqual(result['support'],before['support']); self.assertEqual(result['missing'],before['missing'])
        self.assertEqual(result['currentEvidence'],evidence['provenance']['capture'])
        self.assertEqual(result['currentMetadata'],evidence['provenance']['cell'])
        self.assertEqual(row,before)
        self.assertEqual(artifacts.documents[result['nativeEvidence']['path']], evidence['nativeEvidenceEnvelope'])

    def test_t1_budget_uses_own_linear_code_step_not_an_encoded_one_code_floor(self):
        row=native_row('T1-full-silhouette')
        evidence=current_evidence(row,value=.012,native=.01,
            repeat={'codeStepLinear':.002,'barLinear':.0015,'passes':True})
        result=self.a.complete_native(row,evidence,self.artifacts(),(),())
        self.assertEqual(result['B'],.003)
        self.assertEqual(result['nativeRepeat'],evidence['measurement']['nativeRepeat'])

    def test_reported_and_exact_empty_support_keep_null_budget_without_substitution(self):
        row=native_row('T1-full-silhouette'); key=list(self.a.key(row))
        evidence=current_evidence(row,value=.02,native=.01,
            repeat={'codeStepLinear':.002,'barLinear':.001,'passes':True},required=False)
        result=self.a.complete_native(row,evidence,self.artifacts(),[key],[])
        self.assertEqual(result['status'],'REPORTED'); self.assertIsNone(result['B'])
        empty=copy.deepcopy(evidence)
        empty['measurement'].update(status='UNMEASURED_EMPTY_SUPPORT',measurementStatus='UNMEASURED_EMPTY_SUPPORT',
            value=None,nativeValue=None,nativeRepeat=None,runValues=[None]*3,
            nativeSupportWitnesses=[dict(run=n,pixels=0,maskShape=[384,512],maskPackedBitsSha256='0'*64) for n in (1,2,3)])
        artifacts=self.artifacts(); result=self.a.complete_native(row,empty,artifacts,[key],[key])
        self.assertEqual(result['status'],'UNMEASURED_EMPTY_SUPPORT')
        self.assertTrue(all(result[k] is None for k in ('native','current','fidelity','value','B')))
        self.assertEqual(artifacts.documents[result['emptySupportWitness']['path']]['nativeRead'],
                         evidence['provenance']['nativeRead'])
        with self.assertRaises(ValueError): self.a.complete_native(row,empty,self.artifacts(),[key],[])
        empty['measurement']['nativeSupportWitnesses'][0]['pixels']=1
        with self.assertRaises(ValueError): self.a.complete_native(row,empty,self.artifacts(),[key],[key])

    def test_changed_original_pair_non_null_field_or_missing_measurement_is_refused(self):
        row=native_row(); evidence=current_evidence(row,value=[20]*3,native=[21]*3,
            repeat={'spreadCodes':[0]*3,'barCodes':[.5]*3,'passes':True})
        for mutation in ('original','pair','generation','status','native-envelope'):
            with self.subTest(mutation=mutation):
                e=copy.deepcopy(evidence)
                if mutation=='original': e['originalReference']['support']='compact-label'
                elif mutation=='pair': e['currentDocumentPair']['active.dark']='c'*64
                elif mutation=='generation': e['currentGeneration']='other'
                elif mutation=='status': e['measurement']['status']='UNMEASURED'
                else: e['nativeEvidenceEnvelope']['support']='compact-label'
                with self.assertRaises(ValueError): self.a.complete_native(row,e,self.artifacts(),(),())


class CanonicalJoins(unittest.TestCase):
    @classmethod
    def setUpClass(cls): cls.a=load()
    def row(self,statistic='T1-low',position='0.5',scene='hc-text__rrect-md__rest'):
        row=original(statistic,role='gate',position=position,scene=scene)
        row.update(nativeEvidence=pin('/synthetic/native.png'),currentEvidence=pin('/synthetic/current.png'),
                   currentMetadata=pin('/synthetic/cell.json'),stratum='T' if statistic=='T1-low' else 'P')
        return row
    def readings(self):
        return {'T1-low':dict(status='MEASURED',native=.01,current=.02,B=.003,repeat={'B':.003},units='linear-luma'),
                'T1-fine':dict(status='MEASURED',native=.03,current=.04,B=.005,repeat={'B':.005},units='linear-luma')}

    def test_existing_025_t1_and_typed_fidelity_are_literal_pass_through(self):
        row=self.row(position='0.25'); row.update(status='MEASURED',native=.4,current=.5,B=.02,
            fidelity=dict(statistic='T1-fine',native=.6,current=.7,reference=.8),
            historical=[{'documentPair':{'active':'held'},'maxGrowthInB':3,'frozenCurrentGrowthInB':2}])
        before=copy.deepcopy(row)
        result=self.a.complete_canonical(row,canonical_record(row,self.readings()))
        self.assertEqual(result,row); self.assertEqual(row,before)

    def test_new_05_t1_low_requires_own_fine_fidelity_and_keeps_band_budget_provenance(self):
        row=self.row(); record=canonical_record(row,self.readings())
        result=self.a.complete_canonical(row,record)
        self.assertEqual((result['native'],result['current'],result['B']),(.01,.02,.003))
        self.assertEqual(result['fidelity'],dict(statistic='T1-fine',native=.03,current=.04,reference=.04))
        self.assertEqual(result['canonicalReadings'],record['readings'])
        record['readings'].pop('T1-fine')
        with self.assertRaises(ValueError): self.a.complete_canonical(row,record)

    def test_composite_path_keeps_each_budget_and_never_maxes_unequal_stops(self):
        row=self.row('low-end-path-level',scene='impulse__rrect-lg__rest')
        readings={'deep8-far24-luma-mean':dict(status='MEASURED',native=20,current=19,B=1,repeat={'B':1},units='encoded-luma-codes'),
                  'deep8-far24-luma-median':dict(status='MEASURED',native=21,current=20,B=1,repeat={'B':1},units='encoded-luma-codes')}
        result=self.a.complete_canonical(row,canonical_record(row,readings))
        self.assertEqual(result['native'],{'deep8Far24LumaMean':20,'deep8Far24LumaMedian':21})
        self.assertEqual(result['current'],{'deep8Far24LumaMean':19,'deep8Far24LumaMedian':20})
        self.assertEqual(result['B'],1)
        self.assertEqual(result['perFieldBudgets']['deep8Far24LumaMedian']['B'],1)
        readings['deep8-far24-luma-median'].update(B=2,repeat={'B':2})
        with self.assertRaisesRegex(ValueError,'budget'):
            self.a.complete_canonical(row,canonical_record(row,readings))

    def test_dark_solid_channel_budgets_remain_individual_even_when_scalar_is_equal(self):
        row=self.row('low-end-path-level',scene='dark-solid__rrect-lg__rest')
        reading=dict(status='MEASURED',native=[28,28,30],current=[27,28,29],B=[1,1,1],
                     repeat={'B':[1,1,1],'bar':[.5,.5,.5]},units='encoded-RGB-codes',support='deep8')
        record=canonical_record(row,{'deep8-channel-median':reading})
        result=self.a.complete_canonical(row,record)
        self.assertEqual(result['native'],{'deep8ChannelMedian':[28,28,30]})
        self.assertEqual(result['perFieldBudgets']['deep8ChannelMedian']['B'],[1,1,1])
        self.assertEqual(result['perFieldBudgets']['deep8ChannelMedian']['repeat'],reading['repeat'])
        self.assertEqual(result['B'],1)
        record['readings']['deep8-channel-median']['B']=[1,2,1]
        with self.assertRaisesRegex(ValueError,'budget'):self.a.complete_canonical(row,record)

    def test_known_original_budget_and_reference_fields_cannot_be_overridden(self):
        row=self.row(); row['B']=.123
        record=canonical_record(row,self.readings())
        result=self.a.complete_canonical(row,record)
        self.assertEqual(result['B'],.123)
        record['reference']['role']='reference-only'
        with self.assertRaises(ValueError): self.a.complete_canonical(row,record)


class FullJoinTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls): cls.a=load()

    def fixture(self):
        native=native_row()
        canonical=CanonicalJoins().row()
        owner=original('owner-contracts',scene='photo__rrect-lg__rest',role='gate')
        owner.update(nativeEvidence=pin('/synthetic/owner-native.png'),currentEvidence=pin('/synthetic/owner-current.png'),
                     currentMetadata=pin('/synthetic/owner-cell.json'))
        blind=original('deep8-channel-median',scene='cell-grey-007-s044__rest',role='blind')
        blind.update(nativeIdentity=blind['profile']+'/'+blind['scene'],referenceIdentity=blind['profile']+'/no-glass')
        rows=[owner,native,blind,canonical]
        inventory=dict(schema='w50-reference-inventory-1',stage='prospective-before-native',cells=rows,
                       notes=['Original unchanged metadata'])
        provenance={name:pin('/synthetic/'+name+'.json',digit) for name,digit in
            [('original','1'),('currentAnalysis','2'),('canonicalReferences','3'),('ownerIndex','4'),
             ('ownerBatch','5'),('ownerContracts','6'),('ownerSource','7')]}
        current=dict(schema='w50-completed-current-evidence-1',status='EVIDENCE_ONLY',
            originals={'references':provenance['original']},referenceEvidence=[current_evidence(native,
                value=[22,23,24],native=[20,21,22],repeat={'barCodes':[.5]*3,'spreadCodes':[0]*3,'passes':True})])
        record=canonical_record(canonical,CanonicalJoins().readings())
        canon=dict(schema='w50-canonical-reference-evidence-1',purpose='REFERENCE_EVIDENCE_ONLY_NOT_COEFFICIENT_INPUT',
            inputs={'inventory':provenance['original']},originalReferences=[copy.deepcopy(canonical)],
            selectedKeys=[list(self.a.key(canonical))],partitions={'gate':[record],'historical-prediction-check':[],
                                                               'reference-only':[]})
        identity={k:owner[k] for k in self.a.KEY}
        projection=dict(schema='w50-owner-evidence-1',row=identity,cellId='/'.join(owner[k] for k in self.a.KEY[:3]),
            inputsPin=pin('/synthetic/owner-inputs.json'),reportPin=pin('/synthetic/owner-report.json'),
            contractsPin=provenance['ownerContracts'],ownerSource=provenance['ownerSource'],
            axes={'sourceOwned':'opaque preserved'},aggregateKeys=[],intrinsic={'sourceOwned':'opaque preserved'})
        batch=dict(schema='w50-owner-evidence-batch-1',inventoryPin=provenance['original'],
                   inputsPin=projection['inputsPin'],reportPin=projection['reportPin'],
                   contractsPin=projection['contractsPin'],rows=[projection])
        evidence_pin=pin('/synthetic/owner-row.json.gz','8')
        index=dict(schema='w50-owner-projection-index-1',source=provenance['ownerBatch'],
                   rows=[{'key':list(self.a.key(owner)),'evidence':evidence_pin}])
        documents={evidence_pin['path']:projection}
        return inventory,current,canon,index,batch,documents,provenance

    def assemble(self, fixture):
        *inputs,provenance=fixture
        return self.a.assemble(*inputs,provenance=provenance,artifact_root='/synthetic/assembled')

    def test_all_joins_keep_original_order_blind_nulls_and_owner_no_invented_numbers(self):
        fixture=self.fixture(); before=copy.deepcopy(fixture); result=self.assemble(fixture)
        self.assertEqual(fixture,before)
        completed=result['completed']; self.assertEqual(completed['stage'],'prospective-before-native')
        self.assertEqual([self.a.key(r) for r in completed['cells']],
                         [self.a.key(r) for r in fixture[0]['cells']])
        owner,native,blind,canonical=completed['cells']
        self.assertEqual(owner['status'],'MEASURED'); self.assertIsNone(owner['B'])
        self.assertNotIn('native',owner); self.assertNotIn('current',owner)
        self.assertEqual(owner['ownerEvidence'],fixture[3]['rows'][0]['evidence'])
        self.assertEqual(blind,{**fixture[0]['cells'][2],'status':'SEALED_BLIND'})
        self.assertEqual(canonical['fidelity']['reference'],canonical['fidelity']['current'])
        self.assertEqual(canonical['canonicalEvidence']['fidelityReference']['currentDocumentPair'],
                         fixture[0]['cells'][3]['currentDocumentPair'])
        self.assertEqual(result['inputs'],fixture[-1])
        self.assertEqual(result['status'],'ASSEMBLED_EVIDENCE_ONLY')
        self.assertNotIn('PASS',result.values())
        self.assertTrue(result['artifacts'])

    def test_missing_extra_duplicate_or_changed_original_inputs_refuse_entire_join(self):
        for mutation in ('missing-native','duplicate-native','extra-canonical','changed-original','missing-owner',
                         'duplicate-index','wrong-owner-document','wrong-index-source','wrong-inventory'):
            with self.subTest(mutation=mutation):
                fixture=list(self.fixture()); original,current,canon,index,batch,documents,provenance=fixture
                if mutation=='missing-native': current['referenceEvidence'].clear()
                elif mutation=='duplicate-native': current['referenceEvidence']*=2
                elif mutation=='extra-canonical': canon['partitions']['gate'].append(copy.deepcopy(canon['partitions']['gate'][0]))
                elif mutation=='changed-original': canon['originalReferences'][0]['support']='altered'
                elif mutation=='missing-owner': index['rows'].clear()
                elif mutation=='duplicate-index': index['rows']*=2
                elif mutation=='wrong-owner-document': documents[next(iter(documents))]=dict(batch['rows'][0],axes={'invented':1})
                elif mutation=='wrong-index-source': index['source']=pin('/other/batch.json')
                else: current['originals']['references']=pin('/other/references.json')
                with self.assertRaises(ValueError): self.assemble(fixture)


if __name__=='__main__': unittest.main()
