"""The real gate slot cannot be reopened under a new output; analysis is exclusive."""
import importlib.util
from pathlib import Path
import tempfile
import unittest
import hashlib
import json
import subprocess
import sys
import runpy
import contextlib
import io
import os
import types
from unittest.mock import patch

HERE = Path(__file__).resolve().parent

def module():
    spec=importlib.util.spec_from_file_location('w51_runner_test',HERE/'run.py')
    m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m

class RunnerTests(unittest.TestCase):
    def setUp(self):
        self.m=module(); self.temp=tempfile.TemporaryDirectory(); self.addCleanup(self.temp.cleanup)
        self.home=Path(self.temp.name).resolve()
    def test_native_file_descriptor_output_stays_quarantined(self):
        log=self.home/'private.log'
        code="""import os,runpy,sys
from pathlib import Path
m=runpy.run_path(sys.argv[1])
with Path(sys.argv[2]).open('x') as stream, m['private_stream'](stream):
    print('PYTHON_CANARY')
    os.write(1,b'NATIVE_CANARY\\n');os.write(2,b'ERROR_CANARY\\n')
print('PUBLIC_STATUS')
"""
        result=subprocess.run([sys.executable,'-I','-B','-c',code,str(HERE/'run.py'),str(log)],capture_output=True,text=True)
        self.assertEqual(result.returncode,0,result.stderr)
        self.assertEqual(result.stdout,'PUBLIC_STATUS\n');self.assertEqual(result.stderr,'')
        self.assertEqual(set(log.read_text().splitlines()),{'PYTHON_CANARY','NATIVE_CANARY','ERROR_CANARY'})

    def test_direct_engine_construction_cannot_bypass_fence_clearance_or_guard(self):
        with self.assertRaisesRegex(ValueError,'fenced'):
            self.m.Engine({},None,None,None)

    def test_actual_cli_fences_before_a_missing_static_input_and_never_marks_analysis(self):
        guard=runpy.run_path(str(HERE/'guard.py'))
        repo=HERE.parents[3]
        doc=json.loads((HERE/'execution-root.draft.json').read_bytes())
        doc['closure']['environment']=guard['environment']()
        for relative in doc['closure']['sources']:
            doc['closure']['sources'][relative]=hashlib.sha256((repo/relative).read_bytes()).hexdigest()
        doc['inputs']=[{'path':'missing-w51-static-input.json','sha256':'0'*64}]
        root=self.home/'isolated-test-root.json';doc['rootPath']=str(root)
        root.write_text(json.dumps(doc))
        Path(str(root)+'.sha256').write_text(hashlib.sha256(root.read_bytes()).hexdigest()+'  '+root.name+'\n')
        clearance=self.home/'clearance.json';clearance.write_text('{}');output=self.home/'output'
        result=subprocess.run([sys.executable,'-I','-B',str(HERE/'run.py'),'--root',str(root),
            '--population','synthetic-rehearsal','--output',str(output),'--clearance',str(clearance)],
            capture_output=True,text=True)
        self.assertNotEqual(result.returncode,0)
        self.assertEqual(json.loads(result.stdout)['status'],'OPERATIONAL_STOP')
        self.assertTrue((output/'fences/000001.json').is_file())
        self.assertTrue((output/'fences/000001.json.stop.json').is_file())
        self.assertFalse(Path(str(output/'contract.json')+'.phase/analysis.started.json').exists())

    def test_post_marker_admission_fault_is_terminal_and_cannot_consume_twice(self):
        R=self.m.source(HERE/'root.py','w51_fault_test_root')
        J=self.m.source(HERE/'journal.py','w51_fault_test_journal')
        L=self.m.source(HERE/'lifecycle.py','w51_fault_test_store')
        A=self.m.source(R.FIT/'live-execution/admission.py','w51_fault_test_admission')
        output=self.home/'fault-test';contract=output/'contract.json'
        marker=L.claim_output(output,contract)
        candidate={'path':'candidate.json','sha256':'a'*64}
        batch={'phase':'gate','cohort':[candidate],'runs':[{'id':'one','profile':'p','renderer':'webgpu',
            'candidate':candidate,'sceneSource':'canonical','scenes':['s'],'sets':['calibration']}]}
        L.write_once(contract,{'outputMarker':marker})
        store=L.Store(contract,batch,output);attempt=store.plan();store.start(attempt,'unit-lease')
        # Malformed transport evidence is a real admission failure after a real exclusive marker.
        store.checkpoint(attempt,attempt['members'][0],{'deliberately':'incomplete'},[]);store.finish(attempt)
        engine=self.m.Engine.__new__(self.m.Engine)
        engine.R,engine.J,engine.L,engine.A=R,J,L,A
        engine.store,engine.output,engine.batch=store,output,batch
        engine._LEASE={'token':'unit-lease'};engine.context=lambda *args:{}
        engine.policy_authority_hashes=lambda:[]  # This test isolates malformed capture admission.
        identity={'root':'b'*64,'population':'c'*64,'clearance':'d'*64}
        with patch.object(self.m,'lease_owned',return_value=True):
            with self.assertRaises(ValueError):engine.analyze(store.complete_union(),identity)
            before=store.analysis_marker.read_bytes()
            with self.assertRaisesRegex(ValueError,'already consumed'):engine.analyze(store.complete_union(),identity)
        self.assertEqual(store.analysis_marker.read_bytes(),before)
        self.assertEqual(J.terminal(output)['status'],'NEITHER')
        self.assertFalse(J.terminal(output)['judgeCompleted'])

    @contextlib.contextmanager
    def toy_invocation(self, status='PASS_EXPOSED_OWNER_PENDING'):
        """Real invoke/analyze/journal/cleanup, with no renderer or scientific input reader.

        Only the source admission and scientific roles are replaced by isolated toy metadata.
        Restoring early publication in Engine.analyze makes the cleanup-fault tests fail.
        """
        m=self.m;J=m.source(HERE/'journal.py','w51_toy_journal')
        output=self.home/'toy-output';root=self.home/'toy-root.json'
        clearance=self.home/'toy-clearance.json';clearance.write_text('{}')
        doc={'repo':str(self.home),'protectedRoots':[],
             'populations':{'synthetic-rehearsal':{'manifest':{'sha256':'b'*64}}},
             'closure':{'environment':{},'sources':{}}}
        # Bootstrap is genuine: the four source hashes and the toy root seal are checked.
        doc['repo']=str(HERE.parents[3])
        doc['closure']['sources']={str((HERE/name).relative_to(HERE.parents[3])):m.sha(HERE/name)
                                  for name in ('run.py','root.py','journal.py','guard.py')}
        root.write_text(json.dumps(doc))
        Path(str(root)+'.sha256').write_text(f'{m.sha(root)}  {root.name}\n')
        prepared={'output':str(output),'dataset':{'externalInputs':[]}}
        roots=types.SimpleNamespace(prepare=lambda *a:prepared,clearance=lambda *a:None,
            source=lambda *a:types.SimpleNamespace(verify=lambda *a:{'status':'COMPLETE'}))
        guard=types.SimpleNamespace(environment=lambda:{},enforce=lambda *a:None,
                                    external_reads=lambda *a:None)
        original_source=m.source
        def sources(path,name):
            if Path(path).name=='journal.py':return J
            if Path(path).name=='root.py':return roots
            if Path(path).name=='guard.py':return guard
            return original_source(path,name)
        class ToyEngine(m.Engine):
            def __init__(self,p,R,journal,lease):
                self.p=p;self.R=R;self.J=journal;self._LEASE=lease;self.output=output
                self.active=None;self.batch={'cohort':[]}
                marker=Path(str(output/'contract.json')+'.phase/analysis.started.json')
                self.store=types.SimpleNamespace(analysis_marker=marker,home=marker.parent,
                    start_analysis=lambda token:J.write_once(marker,{'lease':token}))
                self.A=types.SimpleNamespace(validate_captures=lambda *a:{})
                self.roles={'measurement':(types.SimpleNamespace(evaluate=lambda *a:{}),{}),
                            'judge':(types.SimpleNamespace(evaluate=lambda *a:{'status':status}),{})}
            def policy_authority_hashes(self):return []  # Toy roles have no scientific inputs.
            def create_contract(self):J.write_once(output/'contract.json',{'toy':True})
            def captures(self):return {'members':[]}
            def context(self,*a):
                ctx={'toy':True};self.active={'context':ctx,'snapshot':dict(ctx),'hashes':[]}
                return ctx
        with patch.object(m,'source',side_effect=sources),patch.object(m,'Engine',ToyEngine), \
                patch.object(m,'GPU_LOCK',self.home/'toy-gpu.lock'):
            yield J,root,output,clearance

    def test_cleanup_faults_with_unwritable_fault_record_never_leave_eligible_success(self):
        for fault in ('prepared-result','context','private-stream','log-close','lease',
                      'serialization','final-install'):
            with self.subTest(fault=fault):
                # Each toy invocation owns a new root/slot/output, exactly as a separate process.
                self.home=self.home/fault;self.home.mkdir()
                with self.toy_invocation() as (J,root,output,clearance),contextlib.ExitStack() as stack:
                    original_sync=J.sync_directory;original_unlink=Path.unlink;original_link=J.os.link
                    def sync(path):
                        if fault=='prepared-result' and (output/'result.json').exists():
                            raise OSError('result preparation failed')
                        return original_sync(path)
                    def unlink(path,*a,**kw):
                        if fault=='lease' and path==self.m.GPU_LOCK:
                            raise OSError('lease cleanup failed')
                        return original_unlink(path,*a,**kw)
                    original_fsync=J.os.fsync
                    def fsync(fd):
                        if fault=='private-stream' and (output/'result.json').exists():
                            logs=list((output/'quarantine').glob('*.log'))
                            if logs and os.fstat(fd).st_ino==logs[0].stat().st_ino:
                                raise OSError('private stream cleanup failed')
                        return original_fsync(fd)
                    def link(src,dst,*a,**kw):
                        if fault=='final-install' and Path(dst)==output/'terminal.json':
                            raise OSError('final installation failed')
                        return original_link(src,dst,*a,**kw)
                    original_context=self.m.Engine.require_context;original_open=Path.open
                    def context(engine,ctx):
                        original_context(engine,ctx)
                        if fault=='context' and (output/'result.json').exists():
                            raise ValueError('final context validation failed')
                    class ClosingLog:
                        def __init__(self,stream):self.stream=stream
                        def __enter__(self):return self.stream.__enter__()
                        def __exit__(self,*a):
                            self.stream.__exit__(*a)
                            if (output/'result.json').exists():raise OSError('log close failed')
                    def open_file(path,*a,**kw):
                        stream=original_open(path,*a,**kw)
                        if fault=='log-close' and path.suffix=='.log' and a and a[0]=='x':
                            return ClosingLog(stream)
                        return stream
                    original_dumps=json.dumps
                    def dumps(value,*a,**kw):
                        if fault=='serialization' and isinstance(value,dict) and value.get('analysisConsumed'):
                            raise ValueError('public result serialization failed')
                        return original_dumps(value,*a,**kw)
                    stack.enter_context(patch.object(json,'dumps',side_effect=dumps))
                    stack.enter_context(patch.object(self.m.Engine,'require_context',new=context))
                    stack.enter_context(patch.object(Path,'open',new=open_file))
                    stack.enter_context(patch.object(J,'sync_directory',side_effect=sync))
                    stack.enter_context(patch.object(Path,'unlink',new=unlink))
                    stack.enter_context(patch.object(J.os,'fsync',side_effect=fsync))
                    stack.enter_context(patch.object(J.os,'link',side_effect=link))
                    stack.enter_context(patch.object(J,'fail',side_effect=OSError('fault disk unavailable')))
                    result=self.m.invoke(root,'synthetic-rehearsal',output,clearance)
                self.assertEqual(result['status'],'NEITHER')
                self.assertFalse(result['judgeCompleted'])
                self.assertFalse((output/'terminal.json').exists())
                self.assertIsNone(J.terminal(output))
                self.assertTrue(Path(str(output/'contract.json')+'.phase/analysis.started.json').exists())
                # Failed fault persistence cannot restore eligibility or enable analysis on restart.
                with self.toy_invocation() as (J,root,output,clearance):
                    result=self.m.invoke(root,'synthetic-rehearsal',output,clearance)
                    self.assertEqual(result['status'],'NEITHER')
                    self.assertFalse(result['judgeCompleted'])

    def test_cli_post_marker_fault_with_failed_logging_and_fault_record_is_not_prefence(self):
        with self.toy_invocation() as (J,root,output,clearance):
            original_sync=J.sync_directory;original_open=Path.open
            def sync(path):
                if (output/'result.json').exists():raise OSError('precommit failure')
                return original_sync(path)
            def open_file(path,*a,**kw):
                if path.suffix=='.log' and a and a[0]=='a':raise OSError('log unavailable')
                return original_open(path,*a,**kw)
            argv=['run.py','--root',str(root),'--population','synthetic-rehearsal',
                  '--output',str(output),'--clearance',str(clearance)]
            public=io.StringIO()
            with patch.object(J,'sync_directory',side_effect=sync), \
                    patch.object(J,'fail',side_effect=OSError('fault unavailable')), \
                    patch.object(Path,'open',new=open_file),patch.object(sys,'argv',argv), \
                    contextlib.redirect_stdout(public):
                code=self.m.main()
            self.assertEqual(code,1)
            self.assertEqual(json.loads(public.getvalue())['status'],'NEITHER')
            self.assertFalse((output/'terminal.json').exists())

    def test_cli_unreadable_marker_cannot_be_reported_as_prefence_refusal(self):
        with self.toy_invocation() as (J,root,output,clearance):
            marker=Path(str(output/'contract.json')+'.phase/analysis.started.json')
            J.write_once(marker,{'spent':True})
            original_stat=os.stat
            def stat(path,*a,**kw):
                if isinstance(path,(str,Path)) and Path(path)==marker:
                    raise PermissionError('marker temporarily unreadable')
                return original_stat(path,*a,**kw)
            argv=['run.py','--root',str(root),'--population','synthetic-rehearsal',
                  '--output',str(output),'--clearance',str(clearance)]
            public=io.StringIO()
            with patch.object(self.m,'bootstrap',side_effect=OSError('root unavailable')), \
                    patch.object(os,'stat',new=stat),patch.object(sys,'argv',argv), \
                    contextlib.redirect_stdout(public):
                code=self.m.main()
            self.assertEqual(code,1)
            self.assertEqual(json.loads(public.getvalue())['status'],'NEITHER')

    def test_committed_scientific_neither_and_pass_survive_directory_sync_failure(self):
        for status in ('NEITHER','PASS_EXPOSED_OWNER_PENDING'):
            with self.subTest(status=status):
                self.home=self.home/status;self.home.mkdir()
                with self.toy_invocation(status) as (J,root,output,clearance):
                    original_sync=J.sync_directory
                    def sync(path):
                        if (output/'terminal.json').exists():raise OSError('committed directory sync failed')
                        return original_sync(path)
                    with patch.object(J,'sync_directory',side_effect=sync):
                        result=self.m.invoke(root,'synthetic-rehearsal',output,clearance)
                    self.assertEqual(result['status'],status)
                    self.assertTrue(result['judgeCompleted'])
                    self.assertEqual(result['publication'],'COMMITTED_WITH_DURABILITY_ERROR')
                    self.assertEqual(J.terminal(output)['status'],status)
                    self.assertFalse((output/'fault.json').exists())

    def test_cli_emit_failure_does_not_revoke_committed_verdict(self):
        with self.toy_invocation() as (J,root,output,clearance):
            argv=['run.py','--root',str(root),'--population','synthetic-rehearsal',
                  '--output',str(output),'--clearance',str(clearance)]
            original_print=print
            def emit(*a,**kw):
                if (output/'terminal.json').exists():raise BrokenPipeError('status pipe closed')
                return original_print(*a,**kw)
            with patch.object(sys,'argv',argv),patch('builtins.print',side_effect=emit):
                code=self.m.main()
            self.assertEqual(code,1)
            self.assertEqual(J.terminal(output)['status'],'PASS_EXPOSED_OWNER_PENDING')
            self.assertFalse((output/'fault.json').exists())

    def test_cli_flushes_only_after_commit_and_flush_failure_is_cosmetic(self):
        with self.toy_invocation() as (J,root,output,clearance):
            argv=['run.py','--root',str(root),'--population','synthetic-rehearsal',
                  '--output',str(output),'--clearance',str(clearance)]
            class BrokenOutput(io.StringIO):
                def write(stream,text):
                    self.assertTrue((output/'terminal.json').exists(), 'verdict printed before commit')
                    return super().write(text)
                def flush(stream):
                    if (output/'terminal.json').exists():raise BrokenPipeError('flush failed')
            public=BrokenOutput();errors=io.StringIO()
            with patch.object(sys,'argv',argv),contextlib.redirect_stdout(public), \
                    contextlib.redirect_stderr(errors):
                code=self.m.main()
            self.assertEqual(code,1)
            self.assertEqual(json.loads(public.getvalue())['status'],'PASS_EXPOSED_OWNER_PENDING')
            self.assertEqual(J.terminal(output)['status'],'PASS_EXPOSED_OWNER_PENDING')
            self.assertFalse((output/'fault.json').exists())
            self.assertIn('terminal.json remains authoritative',errors.getvalue())

    def complete_toy_process(self,root,output,clearance):
        """End the successful toy process's raw lock lifetime before testing a later invocation."""
        original_open=os.open;locks=[]
        def opened(path,*a,**kw):
            fd=original_open(path,*a,**kw)
            if Path(path)==output/'.invocation.lock':locks.append(fd)
            return fd
        with patch.object(os,'open',side_effect=opened):
            result=self.m.invoke(root,'synthetic-rehearsal',output,clearance)
        self.assertTrue(result['judgeCompleted'])
        self.assertEqual(len(locks),1)
        os.close(locks[0])

    def test_later_admission_failure_cannot_revoke_committed_neither_or_pass(self):
        for status in ('NEITHER','PASS_EXPOSED_OWNER_PENDING'):
            with self.subTest(status=status):
                self.home=self.home/status;self.home.mkdir()
                with self.toy_invocation(status) as (J,root,output,clearance):
                    self.complete_toy_process(root,output,clearance)
                    before=J.terminal(output)
                    roots=self.m.source(HERE/'root.py','toy_later_admission')
                    with patch.object(roots,'prepare',side_effect=OSError('later input unavailable')):
                        result=self.m.invoke(root,'synthetic-rehearsal',output,clearance)
                    self.assertEqual(result['status'],status)
                    self.assertTrue(result['judgeCompleted'])
                    self.assertEqual(result['publication'],'COMMITTED_WITH_INVOCATION_ERROR')
                    self.assertEqual(J.terminal(output),before)
                    self.assertFalse((output/'fault.json').exists())

    def test_unreadable_committed_status_is_not_a_new_scientific_neither(self):
        for fault in ('terminal-read','terminal-stat','bootstrap'):
            with self.subTest(fault=fault):
                self.home=self.home/fault;self.home.mkdir()
                with self.toy_invocation() as (J,root,output,clearance):
                    self.complete_toy_process(root,output,clearance)
                    before=J.terminal(output)
                    roots=self.m.source(HERE/'root.py','toy_unreadable_status')
                    original_load=J.load;original_stat=os.stat
                    def load(path):
                        if Path(path)==output/'terminal.json':raise OSError('terminal read unavailable')
                        return original_load(path)
                    def stat(path,*a,**kw):
                        if isinstance(path,(str,Path)) and Path(path)==output/'terminal.json':
                            raise PermissionError('terminal stat unavailable')
                        return original_stat(path,*a,**kw)
                    argv=['run.py','--root',str(root),'--population','synthetic-rehearsal',
                          '--output',str(output),'--clearance',str(clearance)]
                    public=io.StringIO()
                    with contextlib.ExitStack() as stack:
                        stack.enter_context(patch.object(roots,'prepare',side_effect=OSError('admission unavailable')))
                        if fault=='terminal-read':stack.enter_context(patch.object(J,'load',side_effect=load))
                        if fault=='terminal-stat':stack.enter_context(patch.object(os,'stat',side_effect=stat))
                        if fault=='bootstrap':stack.enter_context(patch.object(self.m,'bootstrap',side_effect=OSError('bootstrap unavailable')))
                        stack.enter_context(patch.object(sys,'argv',argv))
                        stack.enter_context(contextlib.redirect_stdout(public))
                        code=self.m.main()
                    self.assertEqual(code,1)
                    self.assertEqual(json.loads(public.getvalue())['status'],'STATUS_UNAVAILABLE')
                    self.assertEqual(J.terminal(output),before)
                    self.assertFalse((output/'fault.json').exists())

    def test_gate_output_cannot_change_after_unique_slot_binding(self):
        root=self.home/'root.json'; root.write_text('{}')
        first=self.home/'first'; second=self.home/'second'
        self.m.bind_slot(root,'gate',first)
        self.m.bind_slot(root,'gate',first)
        with self.assertRaises(ValueError): self.m.bind_slot(root,'gate',second)
    def test_rehearsals_have_explicit_distinct_test_namespaces(self):
        root=self.home/'root.json'; root.write_text('{}')
        a=self.m.bind_slot(root,'synthetic-rehearsal',self.home/'first')
        b=self.m.bind_slot(root,'synthetic-rehearsal',self.home/'second')
        self.assertNotEqual(a,b)
    def test_no_exposure_slot_is_executable(self):
        root=self.home/'root.json'; root.write_text('{}')
        with self.assertRaises(ValueError): self.m.bind_slot(root,'exposure',self.home/'out')

if __name__=='__main__': unittest.main()
