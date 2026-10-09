"""Synthetic two-root consumer boundaries; no production composition or capture is opened."""
import copy
from pathlib import Path
import types
import unittest
from unittest.mock import patch

HERE=Path(__file__).resolve().parent


def source(path,name):
    value=types.ModuleType(name);value.__file__=str(path)
    exec(compile(path.read_bytes(),str(path),'exec'),value.__dict__)
    return value


def pin(path,letter): return {'path':path,'sha256':letter*64}


def topology():
    roots=[pin('actual-newbed/root.json','a'),pin('actual-canonical/root.json','b')]
    candidates=[pin('original-gate0.json','c')]
    chains=[];members=[];results=[];documents=[]
    for i,(root,kind) in enumerate(zip(roots,('w50','canonical'))):
        batch=pin(f'actual-{i}/batch.json',str(i+1));contract=pin(f'actual-{i}/contract.json',str(i+3))
        result=pin(contract['path']+'.result.json',str(i+5));claim=pin(contract['path']+'.started.json',str(i+7))
        chain=dict(instrument=root,batch=batch,contract=contract,result=result);chains.append(chain)
        run=dict(id=f'run-{i}',profile='p',renderer='webgpu',candidate=candidates[0],
                 sceneSource=kind,scenes=[f's{i}'])
        receipt=dict(profile='p',renderer='webgpu',scene=f's{i}',candidate=candidates[0],
                     sceneSource=kind,lane='current',origin={'kind':'fresh'})
        members.append(dict(instrument=root,run=run,receipt=receipt,output=f'/synthetic/output-{i}',
                            batch=batch,contract=contract,claim=claim,result=result))
        captures=dict(status='CAPTURED',captures=[copy.deepcopy(receipt)],candidateSha256s=['c'*64])
        results.append(dict(pin=result,document=dict(contractSha256=contract['sha256'],claimSha256=claim['sha256'],
            report={'status':'CAPTURED','captures':captures},captures=captures)))
        documents.append(dict(pin=root,document=dict(repo='synthetic',bootstrap=pin(f'actual-{i}/dispatch.py','d'),
            baselineDocuments=candidates,references=pin('original-references.json','e'))))
    manifest=dict(schema='w50-completed-current-composition-1',originalInstrument=roots[0],chains=chains)
    composition=pin('composition.json','f')
    raw=dict(chainPins=[composition,*roots,*[c['result'] for c in chains]],roots=documents,
             resultDocuments=results,candidates=candidates,members=members)
    return raw,manifest,composition


class TopologyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls): cls.m=source(HERE/'analysis.py','composed_analysis_test')

    def test_anchors_keep_both_actual_roots_and_results_without_virtual_root(self):
        raw,manifest,composition=topology();before=copy.deepcopy(raw)
        admitted=self.m.index_composition(raw,manifest,composition)
        anchors=self.m.anchors(admitted)
        self.assertEqual(anchors,dict(currentComposition=composition,
            currentInstruments=[r['pin'] for r in raw['roots']],
            currentResults=[r['pin'] for r in raw['resultDocuments']],chainPins=raw['chainPins']))
        self.assertNotIn('currentInstrument',anchors);self.assertNotIn('root',admitted)
        self.assertEqual(raw,before)

    def test_member_instrument_and_result_cannot_be_swapped_between_actual_chains(self):
        for mutation in ('instrument','result','contract','duplicate-root','missing-result','root-order'):
            with self.subTest(mutation=mutation):
                raw,manifest,composition=topology()
                if mutation in ('instrument','result','contract'):
                    raw['members'][0][mutation]=raw['members'][1][mutation]
                elif mutation=='duplicate-root':raw['roots'][1]=copy.deepcopy(raw['roots'][0])
                elif mutation=='missing-result':raw['resultDocuments'].pop()
                else:raw['roots'].reverse()
                with self.assertRaises(ValueError):self.m.index_composition(raw,manifest,composition)

    def test_member_mutation_after_composition_is_rejected_before_repeat_binding(self):
        raw,manifest,composition=topology();admitted=self.m.index_composition(raw,manifest,composition)
        member=admitted['members'][0];member['instrument']=admitted['members'][1]['instrument']
        with patch.object(self.m.A,'bind_completed_repeat',side_effect=AssertionError('must not bind')):
            with self.assertRaisesRegex(ValueError,'member'):
                self.m.bind_member(admitted,member,[])

    def test_each_member_selects_its_actual_root_and_actual_result_for_immutable_binder(self):
        raw,manifest,composition=topology();admitted=self.m.index_composition(raw,manifest,composition)
        for item in raw['roots']: admitted['_dispatchers'][self.m.pin_key(item['pin'])]=object()
        with patch.object(self.m.A,'bind_completed_repeat') as bound:
            for i,member in enumerate(admitted['members']):
                self.m.bind_member(admitted,member,[])
                args,kwargs=bound.call_args
                self.assertEqual(args[0],raw['roots'][i]['document'])
                self.assertEqual(args[1],member['instrument'])
                self.assertIs(args[2],member)
                self.assertEqual(kwargs['result'],raw['resultDocuments'][i]['document'])

    def test_composition_failure_precedes_native_contract_or_any_measurement(self):
        with (patch.object(self.m.C,'validate_completed_current',side_effect=ValueError('second completed result missing')),
              patch.object(self.m.A,'native_contract',side_effect=AssertionError('native must remain unread'))):
            with self.assertRaisesRegex(ValueError,'second completed'):
                self.m.read_completed(dict(currentComposition=pin('synthetic-composition.json','f')))


if __name__=='__main__':unittest.main()
