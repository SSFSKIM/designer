"""Synthetic phase persistence: no production root, pixels, native read or renderer."""
import copy
import json
import importlib.util
from pathlib import Path
import tempfile
import unittest
H=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('lifecycle',H/'lifecycle.py');L=importlib.util.module_from_spec(s);s.loader.exec_module(L)

class Lifecycle(unittest.TestCase):
    def setUp(self):
        t=tempfile.TemporaryDirectory();self.addCleanup(t.cleanup);self.home=Path(t.name).resolve()
        self.contract=self.home/'phase.json';self.output=self.home/'output'
        self.candidate={'path':'candidate.json','sha256':'a'*64}
        self.batch={'phase':'exposure','cohort':[self.candidate],'runs':[{'id':'r','profile':'profile','renderer':'css',
            'sceneSource':'canonical','candidate':self.candidate,'baselineCandidate':{'path':'current.json','sha256':'b'*64},
            'scenes':['one','two'],'sets':['holdout'],'captureRoot':'unused','matrixPath':'unused'}]}
        marker=L.claim_output(self.output,self.contract)
        L.write_once(self.contract,{'phase':'exposure','batch':self.batch,'output':str(self.output),'outputMarker':marker})
        self.store=L.Store(self.contract,self.batch,self.output)
    def test_attempt_derives_exact_lanes_and_remaining_with_stable_phase(self):
        a=self.store.plan();self.assertEqual(len(a['members']),4)
        self.assertEqual({m['lane'] for m in a['members']},{'candidate','current'})
        self.store.start(a,'lease');self.store.start_native(a);self.store.complete_native({'ready':True,'CANARY':1234})
        first=a['members'][0];record={'member':first['id'],'CANARY':9876}
        self.store.checkpoint(a,first,record,[])
        self.store.stop(a,'INSTRUMENT_FAULT')
        b=self.store.plan();self.assertEqual(len(b['members']),3)
        self.assertNotIn(first['id'],{m['id'] for m in b['members']})
        self.assertEqual(b['logicalContract'],a['logicalContract'])
        self.assertEqual(b['output'],a['output'])
        self.assertEqual(len(b['retained']),1)
        self.assertEqual(self.store.status()['retained'],1)
        self.assertNotIn('CANARY',str(self.store.status()))
    def test_native_started_without_complete_cannot_be_replayed(self):
        a=self.store.plan();self.store.start(a,'lease');self.store.start_native(a)
        self.store.stop(a,'INSTRUMENT_FAULT')
        with self.assertRaises(ValueError):self.store.plan()
    def test_native_checkpoint_requires_a_real_native_start(self):
        with self.assertRaises(ValueError):self.store.complete_native({'ready':True})
    def test_recovered_checkpoint_keeps_burned_attempt_and_separate_revalidation_claim(self):
        a=self.store.plan();self.store.start(a,'lease');self.store.stop(a,'INSTRUMENT_FAULT')
        folder=self.store._attempt_dir(a)
        claim=L.write_once(self.store.home/'reconcile.started.json',{'schema':'w50-live-reconciliation-claim-1',
            'logicalContract':L.pin(self.contract),'failedAttempt':L.pin(folder/'contract.json'),'failure':L.pin(folder/'failure.json')})
        self.store.adopt(a,a['members'][0],{'durableOriginal':True},[],claim)
        cp=self.store.checkpoints()[0]
        self.assertEqual(cp['attempt'],L.pin(folder/'contract.json'))
        self.assertEqual(cp['claim'],L.pin(folder/'started.json'))
        self.assertEqual(cp['revalidationClaim'],claim)
        b=self.store.plan();self.assertEqual(len(b['members']),3)
    def test_partial_population_never_opens_analysis(self):
        a=self.store.plan();self.store.start(a,'lease')
        with self.assertRaises(ValueError):self.store.start_analysis('lease')
        self.assertFalse(self.store.analysis_marker.exists())
    def test_complete_union_preserves_origins_and_marker_burns_recovery(self):
        a=self.store.plan();self.store.start(a,'lease');self.store.start_native(a);self.store.complete_native({'ready':True})
        for m in a['members']:self.store.checkpoint(a,m,{'member':m['id']},[])
        self.store.finish(a)
        union=self.store.complete_union();self.assertEqual(len(union['members']),4)
        marker=self.store.start_analysis('new-lease');self.assertEqual(marker['logicalContract'],a['logicalContract'])
        with self.assertRaises(ValueError):self.store.plan()
        with self.assertRaises(FileExistsError):self.store.start_analysis('another-lease')
    def test_direct_attempt_cannot_skip_append_only_predecessor(self):
        a=self.store.plan();old=self.store.attempts/'000001/contract.json';old.unlink()
        a['ordinal']=2;a['members']=[self.store._member(m,2) for m in self.store.population]
        L.write_once(self.store.attempts/'000002/contract.json',a)
        with self.assertRaises(ValueError):self.store.start(a,'lease')
    def test_direct_attempt_file_cannot_substitute_a_derived_run(self):
        a=self.store.plan();a['members'][0]['run']['scenes']=['invented']
        path=self.store.attempts/'000001/contract.json';path.write_text(json.dumps(a))
        with self.assertRaises(ValueError):self.store.start(a,'lease')
    def test_checkpoint_cannot_substitute_member_or_duplicate_it(self):
        a=self.store.plan();self.store.start(a,'lease');m=a['members'][0]
        wrong=copy.deepcopy(m);wrong['run']['scenes']=['invented']
        with self.assertRaises(ValueError):self.store.checkpoint(a,wrong,{},[])
        self.store.checkpoint(a,m,{},[])
        with self.assertRaises(FileExistsError):self.store.checkpoint(a,m,{},[])
    def test_unstopped_claim_and_changed_retained_bytes_refuse_recovery(self):
        a=self.store.plan();self.store.start(a,'lease')
        with self.assertRaises(ValueError):self.store.plan()
        self.store.checkpoint(a,a['members'][0],{},[]);self.store.stop(a,'INSTRUMENT_FAULT')
        checkpoint=self.store.checkpoints()[0];Path(checkpoint['payload']['path']).write_text('changed')
        with self.assertRaises(ValueError):self.store.plan()
    def test_exposure_run_without_its_baseline_refuses_as_a_shape_error(self):
        broken=copy.deepcopy(self.batch);broken['runs'][0].pop('baselineCandidate')
        with self.assertRaisesRegex(ValueError,'baseline'):L.Store(self.contract,broken,self.output)
        fit={**copy.deepcopy(broken),'phase':'fit'}
        self.assertEqual(len(L.Store(self.contract,fit,self.output).population),2)
    def test_output_is_claimed_exclusively_by_one_contract(self):
        with self.assertRaises(FileExistsError):L.claim_output(self.output,self.home/'other.json')
        other=self.home/'other.json';L.write_once(other,{'phase':'exposure','outputMarker':L.pin(self.output/L.OUTPUT_MARKER)})
        shared=L.Store(other,self.batch,self.output);a=shared.plan()
        with self.assertRaisesRegex(ValueError,'exclusively'):shared.start(a,'lease')
        unmarked=self.home/'unmarked.json';L.write_once(unmarked,{'phase':'exposure'})
        loose=L.Store(unmarked,self.batch,self.home/'loose');b=loose.plan()
        with self.assertRaisesRegex(ValueError,'exclusively'):loose.start(b,'lease')
        self.store.start(self.store.plan(),'lease')
    def test_completed_attempt_cannot_be_rewritten_as_a_stop(self):
        a=self.store.plan();self.store.start(a,'lease');self.store.start_native(a);self.store.complete_native({'ready':True})
        for m in a['members']:self.store.checkpoint(a,m,{'member':m['id']},[])
        self.store.finish(a)
        with self.assertRaises(ValueError):self.store.stop(a,'INSTRUMENT_FAULT')

if __name__=='__main__':unittest.main()
