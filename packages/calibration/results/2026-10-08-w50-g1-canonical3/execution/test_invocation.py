"""Exercise claim/capability/import guard using a synthetic prevalidated authority.

The original672 recovery is outside this unit boundary; root and cohort validation
are supplied as fixtures, not production bypasses. Actual execution, exclusive lease,
source discovery, claim files and source-bound adapter invocation are exercised.
"""
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('invocation_helpers',HERE/'common.py')
C=importlib.util.module_from_spec(spec);spec.loader.exec_module(C)

class Invocation(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        base=Path(self.temp.name).resolve();self.repo=base/'repo';self.repo.mkdir();self.output=base/'output'
        self.adapter=self.repo/'adapter.py';self.adapter.write_text('''import sys
def execute_current(context):
    dispatcher=sys.modules['w50_g1_dispatch']
    dispatcher.require_context(context)
    raise RuntimeError('synthetic transport instrument fault')
''')
        probe=self.repo/'probe.py';probe.write_text('''from pathlib import Path
import types
p=Path(__file__).with_name('adapter.py');m=types.ModuleType('probe_adapter');m.__file__=str(p)
exec(compile(p.read_bytes(),str(p),'exec'),m.__dict__)
''')
        sources={str(p.relative_to(self.repo)):C.sha(p) for p in (self.adapter,probe)}
        guard=C.source(C.PRIOR/'execution/guard.py','synthetic_guard')
        closure=guard.discover(self.repo,probe,sources)
        self.batch=self.repo/'batch.json';self.batch.write_text(json.dumps({'phase':'current','cohort':[],
            'runs':[{'captureRoot':str(self.output/'captures'),'matrixPath':str(self.output/'matrix.json')}]}))
        self.root=self.repo/'current-instrument-root.json'
        self.doc={'repo':str(self.repo),'closure':closure,'probe':C.pin(self.repo,probe),
            'adapter':C.pin(self.repo,self.adapter),'baselineDocuments':[],'inputs':[],
            'phaseDependencies':{},'repeatAdmission':{}}
        C.write_sealed(self.root,self.doc)
        self.contract=self.repo/'current-instrument'/f'{C.sha(self.batch)}.json'
        C.write_sealed(self.contract,{'schema':'w50-g1-phase-contract-1','executionRootSha256':C.sha(self.root),
            'phase':'current','batch':C.pin(self.repo,self.batch),'cohort':[],'preFitEvidence':None})
        self.lock=base/'unit-lease'
    def run_fixture(self):
        code='''import sys
from pathlib import Path
import importlib.util
s=importlib.util.spec_from_file_location('actual_recovery_dispatch',sys.argv[1]);d=importlib.util.module_from_spec(s);sys.modules[s.name]=d;s.loader.exec_module(d)
root,contract,batch,output=map(Path,sys.argv[2:6]);doc=d.sealed(root)
d.root_doc=lambda path:doc
d.C.D.validate_batch=lambda doc,path,phase:(d.load(path),[])
d.C.D.GPU_LOCK=Path(sys.argv[6])
d.execute(root,contract,batch,output)
'''
        return subprocess.run([sys.executable,'-I','-B','-c',code,str(HERE/'dispatch.py'),str(self.root),
            str(self.contract),str(self.batch),str(self.output),str(self.lock)],capture_output=True,text=True)
    def test_instrument_failure_burns_claim_and_never_creates_result(self):
        result=self.run_fixture()
        self.assertIn('synthetic transport instrument fault',result.stderr)
        self.assertTrue(Path(str(self.contract)+'.started.json').exists())
        self.assertFalse(Path(str(self.contract)+'.result.json').exists());self.assertFalse(self.lock.exists())
        shutil.rmtree(self.output)
        retry=self.run_fixture();self.assertNotEqual(retry.returncode,0)
        self.assertIn('FileExistsError',retry.stderr);self.assertNotIn('synthetic transport instrument fault',retry.stderr)
        self.assertFalse(self.output.exists())
    def test_changed_source_is_refused_before_claim_or_output(self):
        self.adapter.write_text('raise RuntimeError("unregistered helper executed")')
        result=self.run_fixture();self.assertNotEqual(result.returncode,0)
        self.assertNotIn('RuntimeError: unregistered helper executed',result.stderr)
        self.assertFalse(Path(str(self.contract)+'.started.json').exists());self.assertFalse(self.output.exists())

if __name__=='__main__':unittest.main()
