"""Real attempt/qualification/quarantine execution with synthetic admitted authority.

Root/prefit/numerical admission is an explicit fixture boundary; no production root or
candidate bytes are supplied. The journal, exclusive lease, contexts, checkpoint reads,
source callbacks and no-replay native behavior below are the real implementation.
"""
import copy
import importlib.util
import io
import contextlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
H=Path(__file__).resolve().parent

def module(name):
    s=importlib.util.spec_from_file_location('unit_'+name,H/(name+'.py'));m=importlib.util.module_from_spec(s);sys.modules[s.name]=m;s.loader.exec_module(m);return m

class Execution(unittest.TestCase):
    def setUp(self):
        t=tempfile.TemporaryDirectory();self.addCleanup(t.cleanup);self.repo=Path(t.name).resolve();self.output=self.repo/'outside'
        self.D=module('dispatch');self.C=module('common');self.L=module('lifecycle');self.Q=module('quarantine')
        self.D._CORE={'C':self.C,'L':self.L,'Q':self.Q}
        self.oldlock=self.C.D.GPU_LOCK;self.C.D.GPU_LOCK=self.repo/'lease';self.addCleanup(setattr,self.C.D,'GPU_LOCK',self.oldlock)
        candidate={'path':'candidate','sha256':'a'*64};current={'path':'baseline','sha256':'b'*64}
        self.batch={'phase':'exposure','cohort':[candidate],'runs':[{'id':'r','profile':'apple-macos-27.0-1x-dark-standard-glass0.25',
            'renderer':'css','sceneSource':'canonical','candidate':candidate,'baselineCandidate':current,'scenes':['one','two'],
            'sets':['holdout'],'captureRoot':'unused','matrixPath':'unused'}]}
        def put(name,value):
            p=self.repo/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(value));return p
        self.root=put('root.json',{});self.batch_path=put('batch.json',self.batch)
        self.contract=self.repo/'phase.json'
        put('phase.json',{'outputMarker':self.L.claim_output(self.output,self.contract)})
        self.put=put
        refs=put('references.json',{'cells':[{'profile':self.batch['runs'][0]['profile'],'renderer':'css','scene':s,'statistic':'x'} for s in ('one','two')]})
        gate=put('gate.json',{});gate_result=put('gate.result.json',{})
        self.doc={'repo':str(self.repo),'inputs':[],'baselineDocuments':[current],'repeatAdmission':{},
            'phaseDependencies':{'ownerUnionKeys':[]},'references':self.C.D.pin(self.repo,refs),'instruments':{}}
        self.body={'phase':'exposure','gateContract':self.C.D.pin(self.repo,gate),'gateResult':self.C.D.pin(self.repo,gate_result)}
        self.store=self.L.Store(self.contract,self.batch,self.output)
        self.D._phase=lambda *args:(self.doc,self.body,self.batch_path,self.batch,[],self.store)
        self.D.result_for=lambda *args:{'captures':{},'report':{}}
        self.numerical=put('numerical.json',{'synthetic':'admission'})
        self.admission=admission=module('admission')
        admission.validate_numerical=lambda *args:self.C.D.pin(self.repo,self.numerical)
        self.endpoint_calls=[]
        admission.endpoints=lambda doc,item,current=False:self.endpoint_calls.append((item['sha256'],current))
        self.D.admission_module=lambda doc:admission
        native=self.repo/'native.py';native.write_text('''import sys
calls=0
def prepare(context,config):
 global calls
 calls+=1
 sys.modules['w50_g1_dispatch'].require_native_preparation(context)
 print('NATIVE_SECRET_12345.875')
 return {'ready':True,'native':'NATIVE_SECRET_12345.875','artifacts':[]}
def verify(context,payload,config):
 assert payload['native']=='NATIVE_SECRET_12345.875'
''')
        capture=self.repo/'capture.py';capture.write_text('''from pathlib import Path
import hashlib,json,sys
def put(path,value):
 path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(value));return {'path':str(path),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
def capture(context,member,config):
 d=sys.modules['w50_g1_dispatch'];d.require_render_admission(context,member['run'],current=member['lane']=='current')
 if '000001' in context['executionClaim']['path'] and member['lane']=='current':
  print('NATIVE_SECRET_12345.875');raise ValueError({'nativeRepeat':'NATIVE_SECRET_12345.875'})
 run=member['run'];base=Path(run['captureRoot']);scene=member['scene'];tier=run['renderer'];candidate=run['candidate']
 artifacts={k:put(base/(k+'.json'),v) for k,v in {'png':{},'cell':{'capturePath':'declarationSha256='+candidate['sha256'][:12]},
 'report':{'page':{'sceneId':scene,'requestedRenderer':tier,'devicePixelRatio':1,'candidateDocument':{'declarationSha256':candidate['sha256'][:12]}}}}.items()}
 record={'profile':run['profile'],'renderer':tier,'scene':scene,'lane':member['lane'],'candidate':candidate,'artifacts':artifacts,'secret':'NATIVE_SECRET_12345.875'}
 pair=put(base/'pair.json',{'first':artifacts['png']})
 proof=put(base/'repeat-admission__css.json',{'manifest':pair,'pair':{'first':artifacts['png']},'originalArtifacts':artifacts})
 record.update(repeatPair=pair,repeatAdmission=proof)
 put(base/'original-record.json',record)
 return {'record':record,'artifacts':list(artifacts.values())}
def recover(context,member,config):
 p=Path(member['run']['captureRoot'])/'original-record.json'
 if not p.exists():return None
 record=json.loads(p.read_text())
 return {'record':record,'artifacts':list(record['artifacts'].values())+[{'path':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}]}
def verify(context,member,record,config):
 assert record['secret']=='NATIVE_SECRET_12345.875'
''')
        measurement=self.repo/'measurement.py';measurement.write_text("def evaluate(context,captures,config):\n print('NATIVE_SECRET_12345.875')\n raise ValueError('synthetic analysis stop')\n")
        self.native=self.D.source(native,'unit_native')
        self.components={'native':self.native,'capture':self.D.source(capture,'unit_capture'),'measurement':self.D.source(measurement,'unit_measurement')}
        self.D._component=lambda doc,role:(self.components[role],{})
    def test_status_suppresses_source_diagnostics_and_exception_values(self):
        def noisy(*args):
            print('NATIVE_SECRET_12345.875');raise ValueError('NATIVE_SECRET_12345.875')
        self.D._phase=noisy
        out=io.StringIO()
        with contextlib.redirect_stdout(out),contextlib.redirect_stderr(out):
            status=self.D.public_status(self.root,self.contract)
        self.assertEqual(status['code'],'REFUSED');self.assertNotIn('NATIVE_SECRET',out.getvalue()+str(status))
    def orphan(self):
        capture=self.components['capture'];original=capture.capture
        def crash(*args):
            original(*args);raise ValueError('simulated crash after durable source receipt')
        capture.capture=crash
        a=self.store.plan();self.D.execute_attempt(self.root,self.contract,a)
        capture.capture=original
        self.assertEqual(self.store.status()['retained'],0)
        return a
    def test_durable_source_receipt_is_adopted_without_second_capture(self):
        a=self.orphan();b=self.D.prepare_attempt(self.root,self.contract)
        self.assertEqual(len(b['members']),3)
        cp=self.store.checkpoints()[0]
        self.assertEqual(cp['member'],a['members'][0]);self.assertIn('revalidationClaim',cp)
        self.assertEqual(self.native.calls,1)
    def test_recovered_record_cannot_replace_declared_member_identity(self):
        self.orphan();capture=self.components['capture'];original=capture.recover
        def wrong(*args):
            result=original(*args);result['record']['scene']='another-scene';return result
        capture.recover=wrong
        with self.assertRaises(ValueError):self.D.prepare_attempt(self.root,self.contract)
        self.assertEqual(self.store.status()['retained'],0)
    def test_unrecoverable_source_admission_stops_instead_of_rerendering(self):
        self.orphan();self.components['capture'].recover=lambda *args:None
        with self.assertRaises(ValueError):self.D.prepare_attempt(self.root,self.contract)
        self.assertEqual(len(self.store._contracts()),1)
    def test_missing_repeat_receipts_cannot_be_checkpointed_as_validated(self):
        capture=self.components['capture'];original=capture.capture
        def missing(*args):
            got=original(*args);got['record'].pop('repeatAdmission');return got
        capture.capture=missing
        a=self.store.plan();event=self.D.execute_attempt(self.root,self.contract,a)
        self.assertEqual(event['code'],'INSTRUMENT_FAULT')
        self.assertEqual(self.store.status()['retained'],0)
    def test_recovery_keeps_native_and_member_once_without_public_values(self):
        out=io.StringIO()
        with contextlib.redirect_stdout(out),contextlib.redirect_stderr(out):
            a=self.store.plan();first=self.D.execute_attempt(self.root,self.contract,a)
            self.assertEqual(first['code'],'INSTRUMENT_FAULT');self.assertEqual(self.store.status()['retained'],1)
            b=self.store.plan();second=self.D.execute_attempt(self.root,self.contract,b)
            self.assertEqual(second['code'],'ATTEMPT_COMPLETE');self.assertEqual(self.native.calls,1)
            self.assertEqual(self.store.status()['remaining'],0)
            stopped=self.D.execute_analysis(self.root,self.contract)
            self.assertEqual(stopped['code'],'ANALYSIS_STOPPED')
            with self.assertRaises(ValueError):self.store.plan()
        self.assertNotIn('NATIVE_SECRET',out.getvalue())
        self.assertNotIn('NATIVE_SECRET',str(first)+str(second)+str(self.store.status()))
        self.assertTrue(self.store.analysis_marker.exists())
    def failure(self,ordinal=1):
        return json.loads((self.store.attempts/f'{ordinal:06d}'/'failure.json').read_text())

    # An interrupted or killed attempt stays recoverable (DL5k).
    def test_interrupt_outside_worker_preserves_the_claimed_attempt_as_a_stop(self):
        original=self.Q.run_private
        def interrupted(*args):raise KeyboardInterrupt()
        self.Q.run_private=interrupted
        a=self.store.plan()
        with self.assertRaises(KeyboardInterrupt):self.D.execute_attempt(self.root,self.contract,a)
        self.Q.run_private=original
        self.assertEqual(self.failure()['code'],'INSTRUMENT_FAULT')
        b=self.D.prepare_attempt(self.root,self.contract);self.assertEqual(b['ordinal'],2)
        self.assertEqual(self.D.execute_attempt(self.root,self.contract,b)['code'],'ATTEMPT_COMPLETE')
    def killed(self):
        """A claim left by a process that died holding its lease (SIGKILL: no failure record)."""
        dead=subprocess.Popen([sys.executable,'-c','pass']);dead.wait()
        a=self.store.plan();token=f'W50 pid={dead.pid} owner=killed\n'
        folder=self.store.attempts/'000001'
        self.L.write_once(folder/'started.json',{'attempt':self.L.pin(folder/'contract.json'),
            'logicalContract':self.L.pin(self.contract),'pid':dead.pid,'gpuLease':token,'output':str(self.store.output)})
        self.L.write_once(Path(str(self.contract)+'.started.json'),{'contractSha256':self.D.sha(self.contract),
            'batchSha256':self.D.sha(self.batch_path),'phase':'exposure','pid':dead.pid,'gpuLease':token,
            'output':str(self.store.output),'numericalAdmission':self.C.D.pin(self.repo,self.numerical)})
        return a,token,dead.pid
    def test_killed_attempt_is_wedged_until_its_process_and_lease_are_proven_gone(self):
        a,token,pid=self.killed()
        with self.assertRaisesRegex(ValueError,'preserved stop'):self.D.prepare_attempt(self.root,self.contract)
        lock=self.C.D.GPU_LOCK
        lock.write_text('W50 pid=1 owner=someone-else\n')
        with self.assertRaisesRegex(ValueError,'another lease'):self.D.stop_stale_attempt(self.root,self.contract,'INSTRUMENT_FAULT')
        self.assertEqual(lock.read_text(),'W50 pid=1 owner=someone-else\n')
        lock.write_text(token)
        event=self.D.stop_stale_attempt(self.root,self.contract,'INSTRUMENT_FAULT')
        self.assertEqual(event,{'schema':'w50-live-public-event-1','code':'INSTRUMENT_FAULT','phase':'exposure','attempt':1})
        self.assertFalse(lock.exists())
        self.assertEqual(self.failure()['stale'],{'pid':pid,'gpuLease':token,'lock':'removed-same-token'})
        with self.assertRaises(ValueError):self.D.stop_stale_attempt(self.root,self.contract,'INSTRUMENT_FAULT')
        b=self.D.prepare_attempt(self.root,self.contract);self.assertEqual(len(b['members']),4)
        self.assertEqual(self.D.execute_attempt(self.root,self.contract,b)['code'],'ATTEMPT_COMPLETE')
    def test_live_claim_process_is_never_stopped_as_stale(self):
        a=self.store.plan();folder=self.store.attempts/'000001'
        self.L.write_once(folder/'started.json',{'attempt':self.L.pin(folder/'contract.json'),
            'logicalContract':self.L.pin(self.contract),'pid':os.getpid(),'gpuLease':f'W50 pid={os.getpid()} owner=x\n'})
        with self.assertRaisesRegex(ValueError,'still own'):self.D.stop_stale_attempt(self.root,self.contract,'INSTRUMENT_FAULT')
        self.assertFalse((folder/'failure.json').exists())
    def test_census_refusal_and_lease_loss_are_distinct_stops(self):
        capture=self.components['capture'];original=capture.capture
        def refused(context,member,config):
            raise sys.modules['w50_g1_dispatch'].CensusRefused('foreign renderer NATIVE_SECRET_12345.875')
        capture.capture=refused
        a=self.store.plan();self.assertEqual(self.D.execute_attempt(self.root,self.contract,a)['code'],'CENSUS_REFUSED')
        self.assertEqual(self.failure(1)['code'],'CENSUS_REFUSED')
        def lost(context,member,config):
            self.C.D.GPU_LOCK.unlink();return original(context,member,config)
        capture.capture=lost
        b=self.D.prepare_attempt(self.root,self.contract)
        self.assertEqual(self.D.execute_attempt(self.root,self.contract,b)['code'],'LEASE_LOST')
        self.assertEqual(self.failure(2)['code'],'LEASE_LOST')

    def legacy(self,strip):
        capture=self.components['capture'];original=capture.capture
        def legacy(*args):
            got=original(*args);got['record']['origin']={'kind':'retained-attempt2'}
            if strip:got['record'].pop('repeatPair');got['record'].pop('repeatAdmission')
            return got
        capture.capture=legacy
        a=self.store.plan()
        self.assertEqual(self.D.execute_attempt(self.root,self.contract,a)['code'],'INSTRUMENT_FAULT')
        self.assertEqual(self.store.status()['retained'],0)
    def test_live_member_with_legacy_origin_cannot_skip_its_repeat_pins(self):self.legacy(True)
    def test_live_member_admits_no_legacy_origin_even_with_pins(self):self.legacy(False)

    def test_stopped_reconciliation_is_preserved_and_a_successor_names_it(self):
        self.orphan();capture=self.components['capture'];original=capture.recover
        def transient(*args):raise ValueError('transient NATIVE_SECRET_12345.875')
        capture.recover=transient
        with self.assertRaisesRegex(ValueError,'quarantined'):self.D.prepare_attempt(self.root,self.contract)
        self.assertEqual(len(self.store._contracts()),1)
        capture.recover=original
        b=self.D.prepare_attempt(self.root,self.contract);self.assertEqual(len(b['members']),3)
        runs=sorted(p for p in (self.store.home/'reconciliations').glob('*/*') if p.is_dir())
        self.assertEqual([p.name for p in runs],['000001','000002'])
        first=json.loads((runs[0]/'failure.json').read_text())
        self.assertEqual(first['claim'],self.L.pin(runs[0]/'started.json'))
        self.assertTrue(Path(first['log']['path']).is_file())
        second=json.loads((runs[1]/'started.json').read_text())
        self.assertEqual(second['predecessor'],{'claim':self.L.pin(runs[0]/'started.json'),'failure':self.L.pin(runs[0]/'failure.json')})
        self.assertTrue((runs[1]/'complete.json').exists())
        self.assertEqual(self.store.checkpoints()[0]['revalidationClaim'],self.L.pin(runs[1]/'started.json'))
    def test_killed_reconciliation_is_preserved_when_its_process_is_gone(self):
        self.orphan();failure=self.store.attempts/'000001/failure.json'
        dead=subprocess.Popen([sys.executable,'-c','pass']);dead.wait()
        home=self.store.home/'reconciliations'/self.D.sha(failure)/'000001'
        self.L.write_once(home/'started.json',{'pid':dead.pid})
        b=self.D.prepare_attempt(self.root,self.contract);self.assertEqual(len(b['members']),3)
        self.assertTrue(json.loads((home/'failure.json').read_text())['stale'])

    def test_render_admission_rechecks_endpoints_and_numerical_admission(self):
        a=self.store.plan();self.assertEqual(self.D.execute_attempt(self.root,self.contract,a)['code'],'INSTRUMENT_FAULT')
        self.assertEqual(self.endpoint_calls,[('a'*64,False),('b'*64,True)])
        capture=self.components['capture'];original=capture.capture
        def changed(*args):
            self.numerical.write_text('{"changed":true}');return original(*args)
        capture.capture=changed
        b=self.D.prepare_attempt(self.root,self.contract)
        self.assertEqual(self.D.execute_attempt(self.root,self.contract,b)['code'],'INSTRUMENT_FAULT')
        self.assertEqual(self.store.status()['retained'],1)
    def create(self,batch,output):
        """create_phase with the root/pre-fit/gate admissions as explicit fixture boundaries."""
        path=self.put('exposure-batch.json',batch);D=self.C.D;gate=self.repo/'gate.json'
        self.put('gate.json.result.json',{'synthetic':'gate result'})
        self.D.root_doc=lambda root:self.doc;self.D.verify_prefit=lambda root,doc:{'synthetic':'prefit'}
        D.validate_batch=lambda doc,p,phase:(json.loads(Path(p).read_text()),[])
        D.checked_gate_result=lambda root,doc:(gate,{});D.sealed=lambda p:{'cohort':batch['cohort']}
        return self.D.create_phase(self.root,path,output)
    def test_malformed_exposure_contract_refuses_before_its_one_shot_slot_is_sealed(self):
        slot=self.repo/self.C.D.SLOTS['exposure'];output=self.repo.parent/(self.repo.name+'-exposure')
        self.addCleanup(lambda:__import__('shutil').rmtree(output,ignore_errors=True))
        broken=copy.deepcopy(self.batch);broken['runs'][0].pop('baselineCandidate')
        with self.assertRaisesRegex(ValueError,'baseline'):self.create(broken,output)
        self.assertFalse(slot.exists());self.assertFalse(output.exists())
        foreign=copy.deepcopy(self.batch);foreign['runs'][0]['baselineCandidate']={'path':'foreign','sha256':'9'*64}
        with self.assertRaisesRegex(ValueError,'baseline'):self.create(foreign,output)
        self.assertFalse(slot.exists());self.assertFalse(output.exists())
        self.create(self.batch,output)
        body=json.loads(slot.read_text())
        self.assertEqual(body['outputMarker'],self.L.pin(output/self.L.OUTPUT_MARKER))
        self.assertEqual(json.loads((output/self.L.OUTPUT_MARKER).read_text())['contract'],str(slot))
        again=self.repo.parent/(self.repo.name+'-again')
        with self.assertRaises(ValueError):self.create(self.batch,again)
        self.assertFalse(again.exists())
    def test_changed_gate_result_revokes_exposure_capture(self):
        capture=self.components['capture'];original=capture.capture
        def changed(*args):
            Path(self.repo/'gate.result.json').write_text('{"changed":true}');return original(*args)
        capture.capture=changed
        a=self.store.plan();self.assertEqual(self.D.execute_attempt(self.root,self.contract,a)['code'],'INSTRUMENT_FAULT')
        self.assertEqual(self.store.status()['retained'],0)

if __name__=='__main__':unittest.main()
