"""Schema2 producer joins over disposable two-chain metadata, never capture/statistic reads."""
import copy
import hashlib
import json
from pathlib import Path
import tempfile
import types
import unittest

HERE=Path(__file__).resolve().parent


def module(path,name):
    value=types.ModuleType(name);value.__file__=str(path)
    exec(compile(path.read_bytes(),str(path),'exec'),value.__dict__)
    return value


T=module(HERE/'test_bound.py','composed_bound_fixture')


class ComposedBoundTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.b=module(HERE/'bound.py','composed_bound_under_test')

    def fixture(self,directory):
        root,binding,put=T.BoundTests().fixture(directory)
        chains=[];roots=[];chain_pins=[]
        for number in (1,2):
            prefix=f'chain{number}'
            batch=put(prefix+'/batch.json',{'runs':[]})
            input_pin=put(prefix+'/original-input.json',{'original':number})
            instrument=put(prefix+'/current-instrument-root.json',{
                'schema':'w50-g1-current-instrument-root-1','inputs':[input_pin],
                'currentBatches':[batch]})
            instrument_path=Path(instrument['path'])
            sidecar=Path(str(instrument_path)+'.sha256')
            sidecar.write_text(f'{instrument["sha256"]}  {instrument_path.name}\n')
            contract=put(prefix+'/current-instrument/'+batch['sha256']+'.json',{
                'schema':'w50-g1-phase-contract-1','phase':'current','batch':batch,
                'executionRootSha256':instrument['sha256']})
            contract_path=Path(contract['path'])
            contract_sidecar=Path(str(contract_path)+'.sha256')
            contract_sidecar.write_text(f'{contract["sha256"]}  {contract_path.name}\n')
            claim=put(str(contract_path.relative_to(root))+'.started.json',{'output':str(root/'synthetic-output')})
            result=put(str(contract_path.relative_to(root))+'.result.json',{'synthetic':'capture-only metadata'})
            result_path=Path(result['path']);result_sidecar=Path(str(result_path)+'.sha256')
            result_sidecar.write_text(f'{result["sha256"]}  {result_path.name}\n')
            pin=lambda p:{'path':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
            chains.append(dict(instrument=instrument,batch=batch,contract=contract,result=result))
            roots.append(instrument)
            chain_pins.extend([instrument,batch,result,pin(sidecar),contract,pin(contract_sidecar),claim,
                               pin(result_sidecar),input_pin])
        composition=put('composition.json',dict(schema='w50-completed-current-composition-1',
            originalInstrument=roots[0],chains=chains))
        anchors=dict(currentComposition=composition,currentInstruments=roots,
                     currentResults=[c['result'] for c in chains],chainPins=[composition,*chain_pins])
        current=json.loads(Path(binding['currentAnalysis']['path']).read_bytes())
        current.pop('currentInstrument');current.update(schema='w50-completed-current-evidence-2',**anchors)
        config=put('current-config.json',dict(schema='w50-composed-current-config-1',
            currentComposition=composition,native=current['native'],originals=current['originals'],
            output=str(root/'current-output.json')))
        producer_root=json.loads(Path(binding['currentAnalysisRoot']['path']).read_bytes())
        producer_root.update(schema='w50-completed-current-root-2',config=config)
        binding['currentAnalysisRoot']=put('current-root.json',producer_root)
        current.update(config=config,instrumentRootSha256=binding['currentAnalysisRoot']['sha256'])
        binding['currentAnalysis']=put('current-output.json',current)
        canonical=json.loads(Path(binding['canonicalReferences']['path']).read_bytes())
        canonical['currentArtifactProjection']=dict(schema='w50-admitted-current-reference-projection-2',
            originalRows=copy.deepcopy(canonical['originalReferences']),
            rows=copy.deepcopy(canonical['originalReferences']),completedKeys=[],memberProvenance=[],**anchors)
        binding['canonicalReferences']=put('canonical-output.json',canonical)
        return root,binding,put

    def mutate(self,binding,put,name,change):
        value=json.loads(Path(binding[name]['path']).read_bytes());change(value)
        binding[name]=put(Path(binding[name]['path']).name,value)

    def test_actual_two_chain_anchors_join_without_a_virtual_current_instrument(self):
        with tempfile.TemporaryDirectory() as td:
            root,binding,_=self.fixture(td)
            result=self.b.assemble_registered(root,binding,artifact_root=root/'artifacts')
            self.assertEqual(result['counts'],{'owners':1,'newbed':1,'canonical':1,'blind':1})
            self.assertEqual(result['completed']['cells'][2]['status'],'SEALED_BLIND')
            self.assertIsNone(result['completed']['cells'][2]['nativeEvidence'])
            self.assertFalse((root/'artifacts').exists())
            self.assertNotIn('currentInstrument',json.loads(Path(binding['currentAnalysis']['path']).read_bytes()))

    def test_changed_descriptor_pin_roots_results_or_missing_chain_refuse(self):
        for mutation in ('composition-bytes','swapped-roots','swapped-results','missing-chain','missing-chain-pin',
                         'extra-chain-pin','missing-sidecar','virtual-instrument'):
            with self.subTest(mutation=mutation),tempfile.TemporaryDirectory() as td:
                root,binding,put=self.fixture(td)
                if mutation=='composition-bytes':(root/'composition.json').write_text('{}')
                elif mutation=='missing-sidecar':(root/'chain2/current-instrument-root.json.sha256').unlink()
                else:
                    def change(current):
                        if mutation=='swapped-roots':current['currentInstruments'].reverse()
                        elif mutation=='swapped-results':current['currentResults'].reverse()
                        elif mutation=='missing-chain':current['currentResults'].pop()
                        elif mutation=='missing-chain-pin':current['chainPins'].pop()
                        elif mutation=='extra-chain-pin':current['chainPins'].append(current['currentResults'][0])
                        else:current['currentInstrument']=current['currentInstruments'][0]
                    self.mutate(binding,put,'currentAnalysis',change)
                with self.assertRaises(ValueError):self.b.assemble_registered(root,binding,artifact_root=root/'artifacts')
                self.assertFalse((root/'artifacts').exists())

    def test_one_chain_descriptor_refuses_even_when_all_registered_producer_pins_are_coherent(self):
        with tempfile.TemporaryDirectory() as td:
            root,binding,put=self.fixture(td)
            composition=json.loads((root/'composition.json').read_bytes());composition['chains'].pop()
            composition_pin=put('composition.json',composition)
            config=json.loads((root/'current-config.json').read_bytes())
            config['currentComposition']=composition_pin;config_pin=put('current-config.json',config)
            producer=json.loads((root/'current-root.json').read_bytes());producer['config']=config_pin
            binding['currentAnalysisRoot']=put('current-root.json',producer)
            current=json.loads((root/'current-output.json').read_bytes())
            current.update(currentComposition=composition_pin,config=config_pin,
                           instrumentRootSha256=binding['currentAnalysisRoot']['sha256'])
            current['currentInstruments'].pop();current['currentResults'].pop()
            current['chainPins']=[composition_pin,*current['chainPins'][1:10]]
            binding['currentAnalysis']=put('current-output.json',current)
            canonical=json.loads((root/'canonical-output.json').read_bytes())
            for name in ('currentComposition','currentInstruments','currentResults','chainPins'):
                canonical['currentArtifactProjection'][name]=copy.deepcopy(current[name])
            binding['canonicalReferences']=put('canonical-output.json',canonical)
            with self.assertRaisesRegex(ValueError,'two ordered actual completed chains'):
                self.b.assemble_registered(root,binding,artifact_root=root/'artifacts')

    def test_canonical_projection_must_share_analysis_composition_and_exact_ordered_chains(self):
        for mutation in ('composition','roots','results','pins','schema','originals','row-known-field'):
            with self.subTest(mutation=mutation),tempfile.TemporaryDirectory() as td:
                root,binding,put=self.fixture(td)
                def change(canonical):
                    p=canonical['currentArtifactProjection']
                    if mutation=='composition':p['currentComposition']={'path':'other.json','sha256':'0'*64}
                    elif mutation=='roots':p['currentInstruments'].reverse()
                    elif mutation=='results':p['currentResults'].reverse()
                    elif mutation=='pins':p['chainPins'].pop()
                    elif mutation=='schema':p['schema']='w50-admitted-current-reference-projection-1'
                    elif mutation=='originals':p['originalRows'][0]['support']='changed prose'
                    else:p['rows'][0]['B']=.123
                self.mutate(binding,put,'canonicalReferences',change)
                with self.assertRaises(ValueError):self.b.assemble_registered(root,binding,artifact_root=root/'artifacts')

    def test_schema2_output_cannot_use_schema1_producer_to_bypass_composition_binding(self):
        with tempfile.TemporaryDirectory() as td:
            root,binding,put=T.BoundTests().fixture(td)
            self.mutate(binding,put,'currentAnalysis',lambda d:d.update(schema='w50-completed-current-evidence-2'))
            with self.assertRaises(ValueError):
                self.b.assemble_registered(root,binding,artifact_root=root/'artifacts')

    def test_schema1_registered_join_remains_unchanged(self):
        with tempfile.TemporaryDirectory() as td:
            root,binding,_=T.BoundTests().fixture(td)
            result=self.b.assemble_registered(root,binding,artifact_root=root/'artifacts')
            self.assertEqual(result['counts'],{'owners':1,'newbed':1,'canonical':1,'blind':1})


if __name__=='__main__':unittest.main()
