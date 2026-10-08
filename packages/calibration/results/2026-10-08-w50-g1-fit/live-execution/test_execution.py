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
import time
import unittest
H=Path(__file__).resolve().parent

def module(name):
    s=importlib.util.spec_from_file_location('unit_'+name,H/(name+'.py'));m=importlib.util.module_from_spec(s);sys.modules[s.name]=m;s.loader.exec_module(m);return m

class Fixture(unittest.TestCase):
    def setUp(self):
        t=tempfile.TemporaryDirectory();self.addCleanup(t.cleanup);self.repo=Path(t.name).resolve();self.output=self.repo/'outside'
        # Phase outputs (and the creation admission's quarantine beside them) are outside the repo.
        self.addCleanup(lambda repo=self.repo:[__import__('shutil').rmtree(p,ignore_errors=True)
                                               for p in repo.parent.glob(repo.name+'-*')])
        self.D=module('dispatch');self.C=module('common');self.L=module('lifecycle');self.Q=module('quarantine')
        self.D._CORE={'C':self.C,'L':self.L,'Q':self.Q}
        self.oldlock=self.C.D.GPU_LOCK;self.C.D.GPU_LOCK=self.repo/'lease';self.addCleanup(setattr,self.C.D,'GPU_LOCK',self.oldlock)
        def put(name,value):
            p=self.repo/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(value));return p
        self.put=put;pin=lambda p:self.C.D.pin(self.repo,p)
        candidate=pin(put('candidate',{'synthetic':'candidate'}));current=pin(put('baseline',{'synthetic':'baseline'}))
        self.candidate,self.current=candidate,current
        records={name:pin(put(f'intrinsic/{name}.json',{'synthetic':name})) for name in ('beforeActive','beforeReceded','methods','activeEntries')}
        self.intrinsic=pin(put('intrinsic.json',{'candidateDeclarations':[candidate],'recededRecords':{'0.25':records,'0.5':records}}))
        self.batch={'phase':'exposure','cohort':[candidate],'ownerIntrinsicRecords':self.intrinsic,'runs':[{'id':'r','profile':'apple-macos-27.0-1x-dark-standard-glass0.25',
            'renderer':'css','sceneSource':'canonical','candidate':candidate,'baselineCandidate':current,'scenes':['one','two'],
            'sets':['holdout'],'captureRoot':'unused','matrixPath':'unused'}]}
        self.root=put('root.json',{});self.batch_path=put('batch.json',self.batch)
        self.contract=self.repo/'phase.json'
        put('phase.json',{'outputMarker':self.L.claim_output(self.output,self.contract)})
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
admits=[]
refuse=[]
stops=[]
verified=[]
def admit(context,config):
 sys.modules['w50_g1_dispatch'].require_native_admission(context)
 admits.append(context['stage'])
 if refuse:raise ValueError(refuse.pop())
def prepare(context,config):
 global calls
 calls+=1
 sys.modules['w50_g1_dispatch'].require_native_preparation(context)
 print('NATIVE_SECRET_12345.875')
 return {'ready':not stops,'complete':True,'stops':list(stops),'native':'NATIVE_SECRET_12345.875','artifacts':[]}
def verify(context,payload,config):
 assert payload['native']=='NATIVE_SECRET_12345.875'
 verified.append((context['stage'],payload['ready']))
''')
        owner=self.repo/'owner.py';owner.write_text('''import sys
admits=[]
refuse=[]
hooks=[]
def admit(context,config):
 sys.modules['w50_g1_dispatch'].require_owner_admission(context)
 admits.append((context['stage'],context['contract'] is not None,context['executionClaim'] is not None))
 print('NATIVE_SECRET_12345.875')
 for hook in hooks:hook(context)
 if refuse:raise ValueError(refuse.pop())
 return {'admitted':True}
def evaluate(context,captures,config):
 return {'report':{'owner':'synthetic'},'snapshot':None}
''')
        judge=self.repo/'judge.py';judge.write_text('''def evaluate(context,evidence,config):
 return {'status':'NEITHER','synthetic':'judge'}
''')
        fit=self.repo/'fit.py';fit.write_text('''derived=[]
def fit_record(root,completed):
 if len(completed)!=1:raise ValueError('one point')
 return dict(derived[0],completed=completed)
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
        self.native=self.D.source(native,'unit_native');self.owner=self.D.source(owner,'unit_owner');self.fit=self.D.source(fit,'unit_fit')
        self.components={'native':self.native,'owner':self.owner,'fit':self.fit,'capture':self.D.source(capture,'unit_capture'),
            'measurement':self.D.source(measurement,'unit_measurement'),'judge':self.D.source(judge,'unit_judge')}
        self.D._component=lambda doc,role:(self.components[role],{})
    def orphan(self):
        capture=self.components['capture'];original=capture.capture
        def crash(*args):
            original(*args);raise ValueError('simulated crash after durable source receipt')
        capture.capture=crash
        a=self.store.plan();self.D.execute_attempt(self.root,self.contract,a)
        capture.capture=original
        self.assertEqual(self.store.status()['retained'],0)
        return a
    def failure(self,ordinal=1):
        return json.loads((self.store.attempts/f'{ordinal:06d}'/'failure.json').read_text())
    def killed(self):
        """A claim left by a process that died holding its lease (SIGKILL: no failure record)."""
        dead=subprocess.Popen([sys.executable,'-c','pass']);dead.wait()
        a=self.store.plan();token=self.token(dead.pid)
        folder=self.store.attempts/'000001'
        self.L.write_once(folder/'started.json',{'attempt':self.L.pin(folder/'contract.json'),
            'logicalContract':self.L.pin(self.contract),'pid':dead.pid,'gpuLease':token,'output':str(self.store.output)})
        self.L.write_once(Path(str(self.contract)+'.started.json'),{'contractSha256':self.D.sha(self.contract),
            'batchSha256':self.D.sha(self.batch_path),'phase':'exposure','pid':dead.pid,'gpuLease':token,
            'output':str(self.store.output),'numericalAdmission':self.C.D.pin(self.repo,self.numerical)})
        return a,token,dead.pid
    def create(self,batch,output,gate_batch=None,fit_record=None):
        """create_phase with the root/pre-fit/gate admissions as explicit fixture boundaries."""
        path=self.put(batch['phase']+'-batch.json',batch);D=self.C.D;gate=self.repo/'gate.json'
        self.put('gate.json.result.json',{'synthetic':'gate result'})
        gate_batch=self.put('sealed-gate-batch.json',gate_batch or {**self.batch,'phase':'gate'})
        self.D.root_doc=lambda root:self.doc;self.D.verify_prefit=lambda root,doc:{'synthetic':'prefit'}
        D.validate_batch=lambda doc,p,phase:(json.loads(Path(p).read_text()),[])
        D.validate_fit_record=lambda *args:None
        self.C.checked_gate_result=lambda root,doc:(gate,{})
        D.sealed=lambda p:{'cohort':batch['cohort'],'batch':D.pin(self.repo,gate_batch)}
        return self.D.create_phase(self.root,path,output,fit_record)
    def token(self,pid):return f'W50 pid={pid} owner={os.urandom(16).hex()}\n'


class Execution(Fixture):
    def test_status_suppresses_source_diagnostics_and_exception_values(self):
        def noisy(*args):
            print('NATIVE_SECRET_12345.875');raise ValueError('NATIVE_SECRET_12345.875')
        self.D._phase=noisy
        out=io.StringIO()
        with contextlib.redirect_stdout(out),contextlib.redirect_stderr(out):
            status=self.D.public_status(self.root,self.contract)
        self.assertEqual(status['code'],'REFUSED');self.assertNotIn('NATIVE_SECRET',out.getvalue()+str(status))
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
    def test_native_admission_refusal_is_recoverable_and_writes_no_native_marker(self):
        self.native.refuse.append('synthetic missing archive asset')
        a=self.store.plan();first=self.D.execute_attempt(self.root,self.contract,a)
        self.assertEqual(first['code'],'INSTRUMENT_FAULT');self.assertEqual(self.native.calls,0)
        self.assertFalse((self.store.home/'native.started.json').exists())
        self.assertEqual(self.failure()['code'],'INSTRUMENT_FAULT')
        b=self.D.prepare_attempt(self.root,self.contract);self.assertEqual(b['ordinal'],2)
        second=self.D.execute_attempt(self.root,self.contract,b)
        self.assertEqual(second['code'],'ATTEMPT_COMPLETE');self.assertEqual(self.native.calls,1)
        self.assertEqual(self.native.admits,['native-admission','native-admission'])
        self.assertTrue(self.store.status()['nativeComplete'])
    def test_native_admission_capability_is_pre_marker_and_payload_free(self):
        with self.C.D.owned_gpu_lock():
            self.D._LEASE=self.C.D._LEASE
            try:
                a=self.store.plan();claim=self.store.start(a,self.D._LEASE['token'])
                data=self.D._phase()
                self.L.write_once(Path(str(self.contract)+'.started.json'),{'numericalAdmission':None})
                ctx=self.D._context(self.root,self.contract,data,'native-admission',claim,a['members'])
                self.D.require_native_admission(ctx)
                for call in (lambda:self.D.qualification_native(ctx),lambda:self.D.require_native_preparation(ctx),
                        lambda:self.D.require_render_admission(ctx,a['members'][0]['run']),
                        lambda:self.D.require_payload(ctx,{'path':'x','sha256':'0'*64})):
                    with self.assertRaises(ValueError):call()
                self.store.start_native(a)
                with self.assertRaisesRegex(ValueError,'before the one-shot native marker'):self.D.require_native_admission(ctx)
            finally:self.D._ACTIVE=None;self.D._LEASE=None
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
        stale=self.failure()['stale'];self.assertTrue(stale.pop('stopLease').startswith(f'W50 pid={os.getpid()} '))
        self.assertEqual(stale,{'pid':pid,'gpuLease':token,'lock':'removed-same-token'})
        with self.assertRaises(ValueError):self.D.stop_stale_attempt(self.root,self.contract,'INSTRUMENT_FAULT')
        b=self.D.prepare_attempt(self.root,self.contract);self.assertEqual(len(b['members']),4)
        self.assertEqual(self.D.execute_attempt(self.root,self.contract,b)['code'],'ATTEMPT_COMPLETE')
    def test_live_claim_process_is_never_stopped_as_stale(self):
        a=self.store.plan();folder=self.store.attempts/'000001'
        self.L.write_once(folder/'started.json',{'attempt':self.L.pin(folder/'contract.json'),
            'logicalContract':self.L.pin(self.contract),'pid':os.getpid(),'gpuLease':self.token(os.getpid())})
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
        self.assertEqual(self.endpoint_calls,[(self.candidate['sha256'],False),(self.current['sha256'],True)])
        capture=self.components['capture'];original=capture.capture
        def changed(*args):
            self.numerical.write_text('{"changed":true}');return original(*args)
        capture.capture=changed
        b=self.D.prepare_attempt(self.root,self.contract)
        self.assertEqual(self.D.execute_attempt(self.root,self.contract,b)['code'],'INSTRUMENT_FAULT')
        self.assertEqual(self.store.status()['retained'],1)
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


STOP={'cell':'apple-macos-27.0-1x-dark-standard-glass0.25/one','statistic':'deep8','reason':'NATIVE_SPREAD_EXCEEDS_ONE_CODE'}


class PreSeal(Fixture):
    """The pre-seal review's findings (W50 G1, DL4/DL5k), each against the real dispatcher."""
    def captured(self):
        """Attempt 1 stops on its current lane by the fixture's design; attempt 2 completes."""
        a=self.store.plan();self.assertEqual(self.D.execute_attempt(self.root,self.contract,a)['code'],'INSTRUMENT_FAULT')
        b=self.D.prepare_attempt(self.root,self.contract)
        self.assertEqual(self.D.execute_attempt(self.root,self.contract,b)['code'],'ATTEMPT_COMPLETE')
    def analysable(self):
        calls=[]
        self.components['measurement'].evaluate=lambda ctx,captures,config:calls.append('measure') or {'m':1}
        self.C.validate_report=lambda *a,**k:None
        self.admission.validate_captures=lambda batch,captures,output:{'members':['synthetic'],'artifacts':[]}
        return calls
    def exposure_output(self,name='-exposure'):
        output=self.repo.parent/(self.repo.name+name)
        self.addCleanup(lambda:__import__('shutil').rmtree(output,ignore_errors=True));return output
    def dead(self):
        process=subprocess.Popen([sys.executable,'-c','pass']);process.wait();return process.pid

    # P1: the owner is admitted before every one-shot marker.
    def test_owner_refusal_at_exposure_creation_seals_nothing(self):
        slot=self.repo/self.C.D.SLOTS['exposure'];output=self.exposure_output()
        self.owner.refuse.append('synthetic drifted owner input NATIVE_SECRET_12345.875')
        out=io.StringIO()
        with contextlib.redirect_stdout(out),contextlib.redirect_stderr(out),\
                self.assertRaisesRegex(ValueError,'quarantined') as refused:self.create(self.batch,output)
        self.assertFalse(slot.exists());self.assertFalse(output.exists());self.assertFalse(self.C.D.GPU_LOCK.exists())
        # The admission's streams and its refusal are quarantined beside the fresh output.
        self.assertNotIn('NATIVE_SECRET',out.getvalue()+str(refused.exception))
        logs=sorted(Path(str(output)+'.admission').glob('owner-admission-*.log'))
        self.assertIn('drifted',logs[0].read_text());self.assertIn('NATIVE_SECRET',logs[0].read_text())
        with contextlib.redirect_stdout(out):self.create(self.batch,output)
        self.assertEqual(len(list(Path(str(output)+'.admission').glob('*.log'))),2)
        self.assertEqual(self.owner.admits,[('owner-admission',False,False)]*2)
    def test_owner_is_admitted_at_the_gate_creation_only(self):
        """The gate batch freezes the intrinsic records, so the owner is admitted (and its refusal
        quarantined) at the gate's creation; a gate grants owner admission at creation only."""
        D=self.C.D;gate={**self.batch,'phase':'gate'};gate['runs']=[{k:v for k,v in self.batch['runs'][0].items() if k!='baselineCandidate'}]
        self.D.result_for=lambda contract:{};one=[D.pin(self.repo,self.put('fit/one.json.result.json',{'synthetic':'fit result'}))]
        self.fit.derived[:]=[{'schema':'w50-g1-fit-record-1','selected':[self.candidate]}]
        record=self.put('fit-record.json',{**self.fit.derived[0],'completed':one})
        slot=self.repo/D.SLOTS['gate'];output=self.exposure_output('-gate')
        self.owner.refuse.append('synthetic refused intrinsic records')
        with self.assertRaisesRegex(ValueError,'quarantined'):self.create(gate,output,gate_batch=gate,fit_record=record)
        self.assertFalse(slot.exists());self.assertFalse(output.exists())
        self.create(gate,output,gate_batch=gate,fit_record=record);self.assertTrue(slot.exists())
        self.assertEqual(self.owner.admits,[('owner-admission',False,False)]*2)
        with self.C.D.owned_gpu_lock():
            self.D._LEASE=self.C.D._LEASE
            try:
                a=self.store.plan();claim=self.store.start(a,self.D._LEASE['token'])
                self.L.write_once(Path(str(self.contract)+'.started.json'),{'numericalAdmission':None})
                data=(self.doc,{**self.body,'phase':'gate'},self.batch_path,self.batch,[],self.store)
                ctx=self.D._context(self.root,self.contract,data,'owner-admission',claim)
                with self.assertRaisesRegex(ValueError,'No live owner'):self.D.require_owner_admission(ctx)
            finally:self.D._ACTIVE=None;self.D._LEASE=None
    def test_owner_refusal_before_the_native_marker_is_a_recoverable_stop(self):
        self.owner.refuse.append('synthetic drifted owner input')
        a=self.store.plan();self.assertEqual(self.D.execute_attempt(self.root,self.contract,a)['code'],'INSTRUMENT_FAULT')
        self.assertFalse((self.store.home/'native.started.json').exists());self.assertEqual(self.native.calls,0)
        b=self.D.prepare_attempt(self.root,self.contract);self.assertEqual(b['ordinal'],2)
        self.assertEqual(self.D.execute_attempt(self.root,self.contract,b)['code'],'ATTEMPT_COMPLETE')
        self.assertEqual(self.native.calls,1);self.assertEqual(self.owner.admits,[('owner-admission',True,True)]*2)
    def test_owner_refusal_before_the_analysis_marker_starts_nothing(self):
        self.captured();self.owner.admits.clear();self.owner.refuse.append('NATIVE_SECRET_12345.875')
        out=io.StringIO()
        with contextlib.redirect_stdout(out),contextlib.redirect_stderr(out):
            refused=self.D.execute_analysis(self.root,self.contract)
        self.assertEqual(refused,{'schema':'w50-live-public-event-1','code':'REFUSED','phase':'exposure'})
        self.assertFalse(self.store.analysis_marker.exists());self.assertNotIn('NATIVE_SECRET',out.getvalue()+str(refused))
        self.assertEqual(self.D.execute_analysis(self.root,self.contract)['code'],'ANALYSIS_STOPPED')
        self.assertTrue(self.store.analysis_marker.exists())
        self.assertEqual(self.owner.admits,[('owner-admission',True,False)]*2)
    def test_owner_admission_capability_is_payload_free_and_ends_at_the_analysis_marker(self):
        with self.C.D.owned_gpu_lock():
            self.D._LEASE=self.C.D._LEASE
            try:
                a=self.store.plan();claim=self.store.start(a,self.D._LEASE['token']);data=self.D._phase()
                self.L.write_once(Path(str(self.contract)+'.started.json'),{'numericalAdmission':None})
                ctx=self.D._context(self.root,self.contract,data,'owner-admission',claim,a['members'])
                self.D.require_owner_admission(ctx)
                for call in (lambda:self.D.qualification_native(ctx),lambda:self.D.require_native_admission(ctx),
                        lambda:self.D.require_native_preparation(ctx),lambda:self.D.require_render_admission(ctx,a['members'][0]['run']),
                        lambda:self.D.require_read_admission(ctx,a['members'][0]['run']),
                        lambda:self.D.require_payload(ctx,{'path':'x','sha256':'0'*64})):
                    with self.assertRaises(ValueError):call()
                native=self.D._context(self.root,self.contract,data,'native-admission',claim)
                with self.assertRaisesRegex(ValueError,'owner admission'):self.D.require_owner_admission(native)
                ctx=self.D._context(self.root,self.contract,data,'owner-admission',claim)
                self.L.write_once(self.store.analysis_marker,{'synthetic':'marker'})
                with self.assertRaisesRegex(ValueError,'before the analysis marker'):self.D.require_owner_admission(ctx)
                fit=(self.doc,{**self.body,'phase':'fit'},self.batch_path,self.batch,[],self.store)
                ctx=self.D._context(self.root,self.contract,fit,'owner-admission',claim)
                with self.assertRaisesRegex(ValueError,'No live owner'):self.D.require_owner_admission(ctx)
            finally:self.D._ACTIVE=None;self.D._LEASE=None

    # P1: intrinsic records are checked before any slot exists.
    def test_intrinsic_records_refuse_before_any_slot_or_output(self):
        D=self.C.D;pin=lambda p:D.pin(self.repo,p)
        def records(**change):
            value={'candidateDeclarations':[self.candidate],'recededRecords':json.loads((self.repo/'intrinsic.json').read_text())['recededRecords'],**change}
            return pin(self.put('intrinsic-variant.json',value))
        gone={'path':'intrinsic/absent.json','sha256':'0'*64}
        good=json.loads((self.repo/'intrinsic.json').read_text())['recededRecords']['0.25']
        cases={'missing':lambda b:b.pop('ownerIntrinsicRecords'),
               'not a pin':lambda b:b.update(ownerIntrinsicRecords={**self.intrinsic,'extra':1}),
               'unresolvable':lambda b:b.update(ownerIntrinsicRecords=gone),
               'declarations':lambda b:b.update(ownerIntrinsicRecords=records(candidateDeclarations=[self.current])),
               'duplicate declaration':lambda b:b.update(ownerIntrinsicRecords=records(candidateDeclarations=[self.candidate]*2)),
               'one position':lambda b:b.update(ownerIntrinsicRecords=records(recededRecords={'0.25':good})),
               'record pin':lambda b:b.update(ownerIntrinsicRecords=records(recededRecords={'0.25':good,'0.5':{**good,'methods':gone}}))}
        for phase in ('gate','exposure'):
            for name,mutate in cases.items():
                batch=json.loads(json.dumps({**self.batch,'phase':phase}));mutate(batch)
                gate=batch if phase=='gate' else None
                output=self.exposure_output('-'+phase);slot=self.repo/D.SLOTS[phase]
                self.fit.derived[:]=[{'schema':'record'}];record=self.put('fit-record.json',{'schema':'record','completed':[]})
                with self.subTest(phase=phase,case=name),self.assertRaises(ValueError):
                    self.create(batch,output,gate_batch=gate,fit_record=record if phase=='gate' else None)
                self.assertFalse(slot.exists());self.assertFalse(output.exists())
        other=records();other_batch={**self.batch,'ownerIntrinsicRecords':other}
        with self.assertRaisesRegex(ValueError,'frozen gate batch'):self.create(other_batch,self.exposure_output())
        self.assertFalse((self.repo/D.SLOTS['exposure']).exists());self.assertEqual(self.owner.admits,[])

    def test_intrinsic_declarations_compare_as_the_owner_child_resolves_them(self):
        """Second pre-seal review P3: the owner's Node child resolves pins lexically against the
        repository (path.resolve), so a symlinked spelling of a cohort document is another
        declaration there; it refuses here too, while a lexically equal spelling is admitted."""
        D=self.C.D;(self.repo/'alias').symlink_to(self.repo);(self.repo/'sub').mkdir()
        receded=json.loads((self.repo/'intrinsic.json').read_text())['recededRecords']
        def batch(path):
            declaration={'path':path,'sha256':self.candidate['sha256']}
            records=D.pin(self.repo,self.put('intrinsic-'+path.replace('/','-')+'.json',
                                             {'candidateDeclarations':[declaration],'recededRecords':receded}))
            return {**self.batch,'ownerIntrinsicRecords':records}
        linked=batch('alias/'+self.candidate['path'])
        with self.assertRaisesRegex(ValueError,'differ from the candidate cohort'):
            self.create(linked,self.exposure_output(),gate_batch=linked)
        lexical=batch('sub/../'+self.candidate['path'])
        self.create(lexical,self.exposure_output(),gate_batch=lexical)

    # P2: a lease its dead holder left behind is released by every entry, and only such a lease.
    def test_lock_left_by_a_killed_reconciliation_is_released_and_its_successor_adopts(self):
        self.orphan();failure=self.store.attempts/'000001/failure.json';pid=self.dead();token=self.token(pid)
        home=self.store.home/'reconciliations'/self.D.sha(failure)/'000001'
        self.L.write_once(home/'started.json',{'pid':pid,'gpuLease':token});self.C.D.GPU_LOCK.write_text(token)
        b=self.D.prepare_attempt(self.root,self.contract);self.assertEqual(len(b['members']),3)
        self.assertTrue(json.loads((home/'failure.json').read_text())['stale']);self.assertFalse(self.C.D.GPU_LOCK.exists())
        self.assertEqual(self.D.execute_attempt(self.root,self.contract,b)['code'],'ATTEMPT_COMPLETE')
    def test_lock_left_between_lock_and_claim_is_released_by_every_entry(self):
        lock=self.C.D.GPU_LOCK
        a=self.store.plan();lock.write_text(self.token(self.dead()))
        self.assertEqual(self.D.execute_attempt(self.root,self.contract,a)['code'],'INSTRUMENT_FAULT')
        b=self.D.prepare_attempt(self.root,self.contract);lock.write_text(self.token(self.dead()))
        self.assertEqual(self.D.execute_attempt(self.root,self.contract,b)['code'],'ATTEMPT_COMPLETE')
        lock.write_text(self.token(self.dead()))
        self.assertEqual(self.D.execute_analysis(self.root,self.contract)['code'],'ANALYSIS_STOPPED')
        lock.write_text(self.token(self.dead()))
        self.create(self.batch,self.exposure_output());self.assertFalse(lock.exists())
    def test_stale_stop_lease_is_released_and_recorded(self):
        a,token,pid=self.killed();self.C.D.GPU_LOCK.write_text(self.token(self.dead()))
        self.D.stop_stale_attempt(self.root,self.contract,'INSTRUMENT_FAULT')
        stale=self.failure()['stale'];self.assertEqual(stale['lock'],'removed-dead-holder')
        self.assertTrue(stale['stopLease'].startswith(f'W50 pid={os.getpid()} '));self.assertFalse(self.C.D.GPU_LOCK.exists())
    def test_a_live_or_foreign_lock_is_never_touched(self):
        lock=self.C.D.GPU_LOCK;a=self.store.plan()
        for held in (self.token(os.getpid()),self.token(1),'W50 pid=1 owner=x\n',f'W50 pid={self.dead()} owner=not-hex\n','2026-10-09T01:00:00+00:00\n'):
            lock.write_text(held)
            with self.subTest(held=held):
                self.assertEqual(self.D._release_stale_lock(),'held')
                with self.assertRaises(FileExistsError):self.D.execute_attempt(self.root,self.contract,a)
                self.assertEqual(lock.read_text(),held)
        self.assertFalse((self.store.attempts/'000001/started.json').exists())
    def test_a_lock_replaced_while_checked_is_not_removed(self):
        lock=self.C.D.GPU_LOCK;lock.write_text(self.token(self.dead()));successor=self.token(os.getpid())
        original=self.D._alive
        def swapped(pid,since):
            lock.unlink();lock.write_text(successor);return original(pid,since)
        self.D._alive=swapped
        self.assertEqual(self.D._release_stale_lock(),'held');self.assertEqual(lock.read_text(),successor)

    # Second pre-seal review P2: release and acquisition are one critical section.
    RIVAL='''import json,sys,types
from pathlib import Path
def load(path,name):
    m=types.ModuleType(name);m.__file__=path;sys.modules[name]=m
    exec(compile(Path(path).read_bytes(),path,'exec'),m.__dict__);return m
C=load(sys.argv[1]+'/common.py','rival_common');C.D.GPU_LOCK=Path(sys.argv[2])
D=load(sys.argv[1]+'/dispatch.py','rival_dispatch');D._CORE={'C':C}
if sys.argv[3]=='unguarded':
    import contextlib;D._lease_mutex=contextlib.nullcontext
try:
    with D._gpu_lease() as released:
        print(json.dumps(['acquired',released]),flush=True);sys.stdin.readline()
except FileExistsError:print(json.dumps(['held']),flush=True)
'''
    def race(self,mode,full):
        """This dispatcher (P2) reads a dead lease; in its stat-to-unlink window a rival process (P1)
        runs its own release and acquisition. Returns P1's first line seen in the window, P2's
        result, P1's final line and the lock's token afterwards."""
        import select
        lock=self.C.D.GPU_LOCK;lock.write_text(self.token(self.dead()));seen={}
        rival=subprocess.Popen([sys.executable,'-I','-B','-c',self.RIVAL,str(H),str(lock),mode],
                               stdin=subprocess.PIPE,stdout=subprocess.PIPE,text=True)
        self.addCleanup(rival.kill)
        real=os
        class Window:
            def __getattr__(self,name):return getattr(real,name)
            def stat(self,path,*args,**kwargs):
                value=real.stat(path,*args,**kwargs)
                if 'line' not in seen:
                    # The window: after this re-stat, before the unlink it licenses.
                    ready,_,_=select.select([rival.stdout],[],[],1.0 if mode=='guarded' else 30)
                    seen['line']=json.loads(rival.stdout.readline()) if ready else None
                return value
        self.D.os=Window();name=lambda released:released[0] if isinstance(released,tuple) else released
        try:
            if full:
                with self.D._gpu_lease() as released:result=(name(released),lock.read_text())
            else:result=(name(self.D._release_stale_lock()),None)
        finally:self.D.os=real
        after=lock.read_text() if lock.exists() else None
        rest,_=rival.communicate('done\n',timeout=30)
        final=[json.loads(line) for line in rest.splitlines()]
        return seen['line'],result,final,after
    def test_unguarded_stale_release_removes_a_rivals_fresh_lease(self):
        """The reviewer's interleaving, without the mutex: the rival's fresh lease is deleted."""
        window,result,_,after=self.race('unguarded',full=False)
        self.assertEqual(window,['acquired',['removed',window[1][1]]])
        self.assertEqual(result,('removed',None));self.assertIsNone(after)
    def test_a_stale_release_never_removes_a_rivals_fresh_lease(self):
        """With the mutex the rival waits for the whole release: it never acquires inside the
        window, and afterwards it acquires only if this dispatcher took no lease, else it is held."""
        window,result,final,after=self.race('guarded',full=False)
        self.assertIsNone(window);self.assertEqual(result,('removed',None))
        self.assertEqual(final,[['acquired','absent']])
        window,result,final,after=self.race('guarded',full=True)
        self.assertIsNone(window);self.assertEqual(result[0],'removed')
        self.assertTrue(result[1].startswith(f'W50 pid={os.getpid()} '));self.assertEqual(final,[['held']])
        self.assertFalse(self.C.D.GPU_LOCK.exists())
    def test_a_lost_lease_writes_neither_one_shot_marker(self):
        """Lease loss after the last capability check and before a one-shot marker writes no
        marker: the attempt is a recoverable LEASE_LOST stop, the analysis a LEASE_LOST event."""
        lock=self.C.D.GPU_LOCK;original=self.D._context
        def native(root,contract,data,stage,*rest):
            ctx=original(root,contract,data,stage,*rest)
            if stage=='native':lock.unlink()
            return ctx
        self.D._context=native
        a=self.store.plan();self.assertEqual(self.D.execute_attempt(self.root,self.contract,a)['code'],'LEASE_LOST')
        self.D._context=original
        self.assertFalse((self.store.home/'native.started.json').exists());self.assertEqual(self.native.calls,0)
        self.assertEqual(self.failure()['code'],'LEASE_LOST')
        b=self.D.prepare_attempt(self.root,self.contract)
        self.assertEqual(self.D.execute_attempt(self.root,self.contract,b)['code'],'ATTEMPT_COMPLETE')
        self.assertEqual(self.native.calls,1)
        run=self.Q.run_private
        def admitted(log,callback):
            value=run(log,callback)
            if 'owner-admission' in str(log):lock.unlink()
            return value
        self.Q.run_private=admitted
        try:event=self.D.execute_analysis(self.root,self.contract)
        finally:self.Q.run_private=run
        self.assertEqual(event,{'schema':'w50-live-public-event-1','code':'LEASE_LOST','phase':'exposure'})
        self.assertFalse(self.store.analysis_marker.exists())
        self.assertEqual(self.D.execute_analysis(self.root,self.contract)['code'],'ANALYSIS_STOPPED')

    # P3: a reused PID is not the claim's writer.
    def sleeper(self):
        child=subprocess.Popen([sys.executable,'-c','import time;time.sleep(60)'])
        self.addCleanup(child.wait);self.addCleanup(child.kill);return child
    def test_a_reused_pid_is_not_the_claims_writer(self):
        child=self.sleeper()
        claim=self.repo/'claim.json';claim.write_text('{}')
        self.assertTrue(self.D._alive(child.pid,os.stat(claim).st_mtime))
        os.utime(claim,(time.time()-100,time.time()-100))
        self.assertFalse(self.D._alive(child.pid,os.stat(claim).st_mtime))
        self.assertTrue(self.D._alive(os.getpid(),0));self.assertTrue(self.D._alive(1,time.time()))
        zombie=subprocess.Popen([sys.executable,'-c','pass']);self.addCleanup(zombie.wait)
        while os.waitid(os.P_PID,zombie.pid,os.WEXITED|os.WNOWAIT) is None:pass
        self.assertFalse(self.D._alive(zombie.pid,time.time()))
    def test_reused_pid_claims_are_preserved_as_stale_attempts_and_reconciliations(self):
        child=self.sleeper();a=self.store.plan();folder=self.store.attempts/'000001'
        self.L.write_once(folder/'started.json',{'attempt':self.L.pin(folder/'contract.json'),'logicalContract':self.L.pin(self.contract),
            'pid':child.pid,'gpuLease':self.token(child.pid)})
        os.utime(folder/'started.json',(time.time()-100,time.time()-100))
        self.D.stop_stale_attempt(self.root,self.contract,'INSTRUMENT_FAULT');self.assertEqual(self.failure()['stale']['pid'],child.pid)
        self.setUp();self.orphan();failure=self.store.attempts/'000001/failure.json'  # a fresh phase with an orphan
        home=self.store.home/'reconciliations'/self.D.sha(failure)/'000001'
        self.L.write_once(home/'started.json',{'pid':child.pid,'gpuLease':self.token(child.pid)})
        os.utime(home/'started.json',(time.time()-100,time.time()-100))
        self.assertEqual(len(self.D.prepare_attempt(self.root,self.contract)['members']),3)
        self.assertTrue(json.loads((home/'failure.json').read_text())['stale'])

    # P3: a successor adopts after a reconciliation stopped between its two writes.
    def test_successor_adopts_after_a_reconciliation_stopped_between_its_writes(self):
        self.orphan();L=self.L;original=L.write_once
        def stopped(path,value):
            if Path(path).parent.name=='recovered' and Path(path).is_relative_to(self.store.attempts):raise RuntimeError('killed')
            return original(path,value)
        L.write_once=stopped
        with self.assertRaisesRegex(ValueError,'quarantined'):self.D.prepare_attempt(self.root,self.contract)
        L.write_once=original
        self.assertEqual(len(self.D.prepare_attempt(self.root,self.contract)['members']),3)
        copies=sorted(p.relative_to(self.output) for p in (self.output/'quarantine/recovered').rglob('*.json'))
        self.assertEqual([p.parts[-2] for p in copies],['000001','000002'])
        self.assertEqual(Path(self.store.checkpoints()[0]['payload']['path']).parent.name,'000002')

    # P3: everything that can refuse is built before its marker.
    def test_analysis_context_refusal_burns_no_marker(self):
        self.captured();refs=self.repo/'references.json';original=refs.read_bytes()
        refs.write_text('{"changed": true}')
        with self.assertRaises(ValueError):self.D.execute_analysis(self.root,self.contract)
        self.assertFalse(self.store.analysis_marker.exists());self.assertFalse(self.C.D.GPU_LOCK.exists())
        refs.write_bytes(original);self.assertEqual(self.D.execute_analysis(self.root,self.contract)['code'],'ANALYSIS_STOPPED')
    def test_native_context_refusal_writes_no_native_marker(self):
        refs=self.repo/'references.json';original=refs.read_bytes()
        self.owner.hooks.append(lambda context:refs.write_text('{"changed": true}'))
        a=self.store.plan();self.assertEqual(self.D.execute_attempt(self.root,self.contract,a)['code'],'INSTRUMENT_FAULT')
        self.assertFalse((self.store.home/'native.started.json').exists());self.assertEqual(self.native.calls,0)
        refs.write_bytes(original);self.owner.hooks.clear()
        b=self.D.prepare_attempt(self.root,self.contract)
        self.assertEqual(self.D.execute_attempt(self.root,self.contract,b)['code'],'ATTEMPT_COMPLETE')

    # P3: the gate takes only the one fit point (DL4).
    def test_gate_takes_only_the_fit_record_its_fit_role_derives(self):
        D=self.C.D;gate={**self.batch,'phase':'gate'};gate['runs']=[{k:v for k,v in self.batch['runs'][0].items() if k!='baselineCandidate'}]
        result=self.put('fit/one.json.result.json',{'synthetic':'fit result'});second=self.put('fit/two.json.result.json',{'other':1})
        self.D.result_for=lambda contract:{}
        one=[D.pin(self.repo,result)];self.fit.derived[:]=[{'schema':'w50-g1-fit-record-1','selected':[self.candidate]}]
        slot=self.repo/D.SLOTS['gate']
        for name,record in (('two completed',{**self.fit.derived[0],'completed':one+[D.pin(self.repo,second)]}),
                            ('not derived',{**self.fit.derived[0],'completed':one,'selection':'chosen elsewhere'}),
                            ('no completion',{**self.fit.derived[0]})):
            with self.subTest(name),self.assertRaises(ValueError):
                self.create(gate,self.exposure_output('-gate'),gate_batch=gate,fit_record=self.put('fit-record.json',record))
            self.assertFalse(slot.exists())
        self.create(gate,self.exposure_output('-gate'),gate_batch=gate,fit_record=self.put('fit-record.json',{**self.fit.derived[0],'completed':one}))
        self.assertTrue(slot.exists())

    # P3: a finished result, native read or contract is completed, never replayed.
    def test_result_written_before_its_sidecar_is_sealed_not_replayed(self):
        self.captured();calls=self.analysable();D=self.C.D;original=D.write_sealed
        def killed(path,value):D.write_once(path,value);raise RuntimeError('killed before sidecar')
        D.write_sealed=killed
        self.assertEqual(self.D.execute_analysis(self.root,self.contract)['code'],'ANALYSIS_STOPPED');D.write_sealed=original
        result=Path(str(self.contract)+'.result.json');self.assertFalse(Path(str(result)+'.sha256').exists())
        self.assertEqual(self.D.execute_analysis(self.root,self.contract)['code'],'ANALYSIS_COMPLETE')
        self.assertEqual(calls,['measure']);D.sealed(result)
        self.assertEqual(self.D.prepare_attempt(self.root,self.contract)['schema'],'w50-live-phase-complete-1')
        with self.assertRaisesRegex(ValueError,'already started'):self.D._seal_interrupted_result(self.root,self.contract,self.D._phase())
    def test_torn_or_rebound_unsealed_result_is_never_sealed(self):
        self.captured();self.analysable();D=self.C.D;original=D.write_sealed
        D.write_sealed=lambda path,value:(D.write_once(path,value),(_ for _ in ()).throw(RuntimeError('killed')))
        self.D.execute_analysis(self.root,self.contract);D.write_sealed=original
        result=Path(str(self.contract)+'.result.json');raw=result.read_bytes();value=json.loads(raw)
        for bad in (raw[:-2],json.dumps(value).encode()+b'\n',
                    (json.dumps({**value,'claimSha256':'0'*64},indent=2)+'\n').encode(),
                    (json.dumps({**value,'report':{**value['report'],'status':'PASS'},'captures':{**value['captures'],'captures':[]}},indent=2)+'\n').encode()):
            result.write_bytes(bad)
            with self.subTest(bad=bad[:40]):
                self.assertEqual(self.D.execute_analysis(self.root,self.contract)['code'],'ANALYSIS_STOPPED')
                self.assertFalse(Path(str(result)+'.sha256').exists())
    def test_native_payload_written_before_its_marker_is_finalised_not_replayed(self):
        L=self.L;original=L.write_once
        def killed(path,value):
            if Path(path).name=='native.complete.json':raise RuntimeError('killed')
            return original(path,value)
        L.write_once=killed
        a=self.store.plan();self.assertEqual(self.D.execute_attempt(self.root,self.contract,a)['code'],'INSTRUMENT_FAULT')
        L.write_once=original
        self.assertEqual(self.store.native_state(),'durable')
        b=self.D.prepare_attempt(self.root,self.contract);self.assertEqual(b['ordinal'],2)
        self.assertEqual(self.D.execute_attempt(self.root,self.contract,b)['code'],'ATTEMPT_COMPLETE')
        self.assertEqual(self.native.calls,1);self.assertIn(('qualification',True),self.native.verified)
        marker=json.loads((self.store.home/'native.complete.json').read_text())
        self.assertEqual(marker['recoveredBy'],self.L.pin(self.store.attempts/'000002/started.json'))
    def test_contract_written_before_its_sidecar_completes_its_seal(self):
        D=self.C.D;original=D.write_sealed;output=self.exposure_output();slot=self.repo/D.SLOTS['exposure']
        def killed(path,value):D.write_once(path,value);raise RuntimeError('killed before sidecar')
        D.write_sealed=killed
        with self.assertRaisesRegex(RuntimeError,'killed'):self.create(self.batch,output)
        D.write_sealed=original
        self.assertTrue(slot.exists());self.assertFalse(Path(str(slot)+'.sha256').exists())
        with self.assertRaisesRegex(ValueError,'fresh external output|already exists'):self.create(self.batch,self.exposure_output('-other'))
        self.assertFalse(Path(str(slot)+'.sha256').exists())
        self.create(self.batch,output);self.assertEqual(json.loads(slot.read_text())['logicalOutput'],str(output))
        self.assertTrue(Path(str(slot)+'.sha256').exists())

    # P3: a clean completion is a status, not an error.
    def test_prepare_after_clean_completion_reports_ready_then_complete(self):
        self.captured();self.analysable()
        self.assertEqual(self.D.prepare_attempt(self.root,self.contract),
            {'schema':'w50-live-capture-ready-1','logicalContract':self.L.pin(self.contract)})
        self.assertEqual(self.D.execute_analysis(self.root,self.contract)['code'],'ANALYSIS_COMPLETE')
        self.assertEqual(self.D.prepare_attempt(self.root,self.contract),
            {'schema':'w50-live-phase-complete-1','logicalContract':self.L.pin(self.contract)})

    # DL5n: a completed not-ready read is a checkpoint; a read that did not complete stops.
    def test_completed_not_ready_native_read_is_checkpointed_and_reaches_analysis(self):
        def run():
            out=io.StringIO()
            with contextlib.redirect_stdout(out),contextlib.redirect_stderr(out):
                a=self.store.plan();first=self.D.execute_attempt(self.root,self.contract,a)
                b=self.D.prepare_attempt(self.root,self.contract);second=self.D.execute_attempt(self.root,self.contract,b)
                status=self.store.status();ready=self.D.prepare_attempt(self.root,self.contract)
            return [first,second,status,{**ready,'logicalContract':None}],out.getvalue()
        ready_public,_=run()
        self.setUp();self.native.stops.append(STOP)
        public,text=run()
        self.assertEqual(public,ready_public);self.assertNotIn('NATIVE_SPREAD',text+str(public))
        self.assertEqual(json.loads(self.store._native_payload().read_text())['stops'],[STOP])
        self.assertEqual(self.native.calls,1);self.assertIn(('qualification',False),self.native.verified)
        calls=self.analysable();self.assertEqual(self.D.execute_analysis(self.root,self.contract)['code'],'ANALYSIS_COMPLETE')
        self.assertEqual(calls,['measure'])
    def test_native_read_that_did_not_complete_stops_and_never_replays(self):
        bad={'exception':lambda payload:(_ for _ in ()).throw(OSError('disk')),
             'value-bearing stop':lambda payload:{**payload,'ready':False,'stops':[{**STOP,'repeat':{'spread':0.75}}]},
             'not complete':lambda payload:{**payload,'complete':False},
             'ready with stops':lambda payload:{**payload,'stops':[STOP]}}
        for name,change in bad.items():
            with self.subTest(name):
                self.setUp();original=self.native.prepare
                self.native.prepare=lambda context,config:change(original(context,config))
                a=self.store.plan();self.assertEqual(self.D.execute_attempt(self.root,self.contract,a)['code'],'INSTRUMENT_FAULT')
                self.assertEqual(self.store.native_state(),'incomplete');self.assertFalse((self.store.home/'native.complete.json').exists())
                with self.assertRaisesRegex(ValueError,'cannot be replayed'):self.D.prepare_attempt(self.root,self.contract)
                with self.assertRaisesRegex(ValueError,'no replay'):self.store.plan()
                self.assertEqual(self.native.calls,1)

if __name__=='__main__':unittest.main()
