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
from pathlib import Path
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
        self.root=put('root.json',{});self.contract=put('phase.json',{});self.batch_path=put('batch.json',self.batch)
        refs=put('references.json',{'cells':[{'profile':self.batch['runs'][0]['profile'],'renderer':'css','scene':s,'statistic':'x'} for s in ('one','two')]})
        gate=put('gate.json',{});gate_result=put('gate.result.json',{})
        self.doc={'repo':str(self.repo),'inputs':[],'baselineDocuments':[current],'repeatAdmission':{},
            'phaseDependencies':{'ownerUnionKeys':[]},'references':self.C.D.pin(self.repo,refs),'instruments':{}}
        self.body={'phase':'exposure','gateContract':self.C.D.pin(self.repo,gate),'gateResult':self.C.D.pin(self.repo,gate_result)}
        self.store=self.L.Store(self.contract,self.batch,self.output)
        self.D._phase=lambda *args:(self.doc,self.body,self.batch_path,self.batch,[],self.store)
        self.D.result_for=lambda *args:{'captures':{},'report':{}}
        admission=module('admission');admission.validate_numerical=lambda *args:{'path':'numerical','sha256':'c'*64}
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

if __name__=='__main__':unittest.main()
