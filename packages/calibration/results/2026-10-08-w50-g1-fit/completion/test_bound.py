"""Registered metadata/output joins on disposable JSON; never read a real capture or report."""
import copy
import gzip
import hashlib
import json
from pathlib import Path
import tempfile
import types
import unittest

HERE=Path(__file__).resolve().parent
FIT=HERE.parent
EXECUTION=FIT.parent/'2026-10-08-w50-g1-current2/execution'


def module(path,name):
    value=types.ModuleType(name); value.__file__=str(path)
    exec(compile(path.read_bytes(),str(path),'exec'),value.__dict__)
    return value


T=module(HERE/'test_assembler.py','assembly_synthetic_records')
T.FullJoinTests.a=T.load()


class BoundTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls): cls.b=module(HERE/'bound.py','bound_assembly_tests')

    def fixture(self,directory,canonical_only=False):
        root=Path(directory).resolve()
        def put(name,value,compressed=False):
            path=root/name; path.parent.mkdir(parents=True,exist_ok=True)
            raw=(json.dumps(value,sort_keys=True)+'\n').encode()
            path.write_bytes(gzip.compress(raw,mtime=0) if compressed else raw)
            return {'path':str(path),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
        original,current,canonical,index,owner,documents,provenance=T.FullJoinTests().fixture()
        if canonical_only:
            original['cells']=original['cells'][2:]
            current['referenceEvidence']=[]; owner['rows']=[]; index['rows']=[]
            for row in original['cells']:
                if row['role']!='blind':
                    for field in ('nativeEvidence','currentEvidence','currentMetadata'):
                        row[field]=put(field+'.json',{'synthetic':'pinned capture metadata'})
            canonical['originalReferences']=[copy.deepcopy(original['cells'][1])]
            canonical['partitions']['gate']=[T.canonical_record(original['cells'][1],T.CanonicalJoins().readings())]
        manifest=put('manifest.json',{'cells':[]})
        original['inputs']={'bed':manifest}; original_pin=put('original.json',original)
        contracts=put('contracts.json',{'sourceOwned':'synthetic'})
        source=put('owner-source.json',{'sourceOwned':'synthetic'})
        owner.update(inventoryPin=original_pin,contractsPin=contracts)
        for row in owner['rows']: row.update(contractsPin=contracts,ownerSource=source)
        owner_pin=put('owner-batch.json.gz',owner,True)
        if owner['rows']:
            row_pin=put('owner-row.json.gz',owner['rows'][0],True)
            index['rows']=[{'key':index['rows'][0]['key'],'evidence':row_pin}]
        index['source']=owner_pin
        index_pin=put('owner-index.json',index)
        producer=put('producer-source.json',{'source':'synthetic'})
        sources={producer['path']:producer['sha256']}
        original_pins={'references':original_pin}
        current.update(originals=original_pins,currentInstrument=T.pin('/synthetic/current-instrument.json'),
                       currentResults=[T.pin('/synthetic/result1.json'),T.pin('/synthetic/result2.json')],
                       native={'synthetic':'registered native metadata'},chainPins=[])
        config=put('current-config.json',{'current':{'instrument':current['currentInstrument'],
            'results':current['currentResults']},'originals':original_pins,'native':current['native'],
            'output':str(root/'current-output.json')})
        current_root=put('current-root.json',dict(schema='w50-completed-current-root-1',config=config,
                                                 closure={'sources':sources}))
        current.update(instrumentRootSha256=current_root['sha256'],config=config,sourcePins=sources)
        current_pin=put('current-output.json',current)
        canonical['inputs']={'inventory':original_pin}
        batch=put('canonical-batch.json',{'inputs':canonical['inputs'],'selectedKeys':canonical['selectedKeys']})
        contract=put('canonical-contract.json',{'batch':batch})
        canonical_root=put('canonical-root.json',dict(schema='w50-reference-instrument-root-1',
            inputs=canonical['inputs'],batch=batch,contract=contract,sources=sources))
        canonical.update(instrumentRootSha256=canonical_root['sha256'],batch=batch,contract=contract,sourcePins=sources)
        canonical_pin=put('canonical-output.json',canonical)
        validator={'path':str(EXECUTION/'prefit.py'),'sha256':hashlib.sha256((EXECUTION/'prefit.py').read_bytes()).hexdigest()}
        source_pins={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in
            (HERE/'bound.py',HERE/'assembler.py',EXECUTION/'prefit.py',EXECUTION/'native_evidence.py',EXECUTION/'owner_evidence.py')}
        binding=dict(original=original_pin,manifest=manifest,currentAnalysis=current_pin,currentAnalysisRoot=current_root,
            canonicalReferences=canonical_pin,canonicalReferencesRoot=canonical_root,ownerIndex=index_pin,
            ownerContracts=contracts,ownerSource=source,validator=validator,sourcePins=source_pins,
            reportedKeys=[],emptySupportKeys=[])
        return root,binding,put

    def test_all_registered_outputs_and_decompressed_owner_members_join_without_readers(self):
        with tempfile.TemporaryDirectory() as td:
            root,binding,_=self.fixture(td)
            result=self.b.assemble_registered(root,binding,artifact_root=root/'artifacts')
            self.assertEqual(result['counts'],{'owners':1,'newbed':1,'canonical':1,'blind':1})
            self.assertEqual(result['sourcePins'],binding['sourcePins'])
            self.assertEqual(result['inputs']['original'],binding['original'])
            self.assertFalse((root/'artifacts').exists())
            self.assertNotIn('PASS',result.values())

    def test_changed_source_or_report_binding_refuses_before_assembly(self):
        for mutation in ('source','current-root','canonical-root','selected','owner-member','output-path'):
            with self.subTest(mutation=mutation),tempfile.TemporaryDirectory() as td:
                root,binding,put=self.fixture(td)
                if mutation=='source': binding['sourcePins'][str(HERE/'assembler.py')]='0'*64
                elif mutation=='current-root':
                    report=json.loads(Path(binding['currentAnalysis']['path']).read_bytes())
                    report['instrumentRootSha256']='0'*64;binding['currentAnalysis']=put('current-output.json',report)
                elif mutation=='canonical-root':
                    report=json.loads(Path(binding['canonicalReferences']['path']).read_bytes())
                    report['inputs']['inventory']=T.pin('/another/original.json')
                    binding['canonicalReferences']=put('canonical-output.json',report)
                elif mutation=='selected':
                    report=json.loads(Path(binding['canonicalReferences']['path']).read_bytes())
                    report['selectedKeys']=[];binding['canonicalReferences']=put('canonical-output.json',report)
                elif mutation=='owner-member':
                    row=json.loads(gzip.decompress((root/'owner-row.json.gz').read_bytes()))
                    row['axes']={'silentlyChanged':123};pin=put('owner-row.json.gz',row,True)
                    index=json.loads(Path(binding['ownerIndex']['path']).read_bytes());index['rows'][0]['evidence']=pin
                    binding['ownerIndex']=put('owner-index.json',index)
                else:
                    pin=binding['currentAnalysis']; value=json.loads(Path(pin['path']).read_bytes())
                    binding['currentAnalysis']=put('other-output.json',value)
                with self.assertRaises(ValueError): self.b.assemble_registered(root,binding,artifact_root=root/'artifacts')
                self.assertFalse((root/'artifacts').exists())

    def test_corrected_validator_checks_assembled_typed_fidelity_and_original_blind_nulls(self):
        with tempfile.TemporaryDirectory() as td:
            root,binding,_=self.fixture(td,canonical_only=True)
            result=self.b.assemble_registered(root,binding,artifact_root=root/'artifacts')
            self.b.materialize_artifacts(result)
            checked=self.b.validate_registered(root,binding,result)
            self.assertEqual(checked['status'],'REFERENCE_VALIDATION_ONLY')
            changed=copy.deepcopy(result);changed['completed']['cells'][1]['current']=.999
            with self.assertRaisesRegex(ValueError,'deterministic assembly'):
                self.b.validate_registered(root,binding,changed)
            changed=copy.deepcopy(result);changed['completed']['cells'][0]['current']=1
            with self.assertRaises(ValueError):self.b.validate_registered(root,binding,changed)

    def test_materialization_is_content_addressed_and_write_once(self):
        with tempfile.TemporaryDirectory() as td:
            root,binding,_=self.fixture(td)
            result=self.b.assemble_registered(root,binding,artifact_root=root/'artifacts')
            written=self.b.materialize_artifacts(result)
            self.assertEqual(set(p['path'] for p in written),set(result['artifacts']))
            for pin in written:
                self.assertEqual(hashlib.sha256(Path(pin['path']).read_bytes()).hexdigest(),pin['sha256'])
            with self.assertRaises(FileExistsError):self.b.materialize_artifacts(result)


if __name__=='__main__':unittest.main()
