"""Metadata-only closure regression; actual role exports/reports/images are unavailable.

A fresh interpreter collects executed source, not a guessed allowlist. The only actual inputs
this test opens are registered root/contract/batch/config/source metadata. It never opens a
native role report, export index or image, and never renames or removes real evidence.
"""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

HERE=Path(__file__).resolve().parent
REPO=HERE.parents[4]


class SourceProbeTests(unittest.TestCase):
    def test_registered_native_authority_late_imports_join_closure_without_data(self):
        # The data boundary is made absent inside the child, including stat/exists checks.
        # Its real source verifier still checks the registered metadata and synthetic probe.
        program=r'''
import hashlib
import json
import os
from pathlib import Path
import sys
import types

repo=Path(sys.argv[1]).resolve()
here=repo/'packages/calibration/results/2026-10-08-w50-g1-current3/repeat'
config=json.loads((here.parent/'inputs/repeat-config.json').read_bytes())
batch=json.loads((repo/config['native']['batch']['path']).read_bytes())
roots=[Path(e['root']).absolute() for e in batch['exports']]
reports={str((repo/p['path']).absolute()) for p in config['native']['reports'].values()}

def unavailable(path):
    if not isinstance(path,(str,bytes,os.PathLike)):return False
    text=os.fsdecode(path)
    absolute=Path(os.path.abspath(text))
    return absolute.suffix in ('.png','.gz') or str(absolute) in reports or any(
        absolute==root or absolute.is_relative_to(root) for root in roots)

original_stat=os.stat
original_lstat=os.lstat
original_scandir=os.scandir
attempted=[]
def absent(call):
    def wrapped(path,*args,**kwargs):
        if unavailable(path):raise FileNotFoundError('Native evidence is absent during prospective probe')
        return call(path,*args,**kwargs)
    return wrapped
os.stat=absent(original_stat);os.lstat=absent(original_lstat);os.scandir=absent(original_scandir)
observed={}
def record(filename):
    if filename.startswith('<'):return
    path=Path(filename).resolve()
    if path.suffix=='.py' and path.is_relative_to(repo):
        observed[str(path.relative_to(repo))]=hashlib.sha256(path.read_bytes()).hexdigest()

def audit(event,args):
    if event=='open' and unavailable(args[0]):
        attempted.append(os.fsdecode(args[0]))
        raise FileNotFoundError('Native data is absent during prospective probe')
    if event=='exec':record(args[0].co_filename)
sys.addaudithook(audit)
def called(frame,event,arg):
    if event=='call' and frame.f_code.co_filename.startswith(str(repo)+'/'):
        record(frame.f_code.co_filename)
sys.setprofile(called)
path=here/'admission.py'
module=types.ModuleType('repeat_metadata_probe');module.__file__=str(path)
exec(compile(path.read_bytes(),str(path),'exec',dont_inherit=True),module.__dict__)
result=module.source_probe()
sys.setprofile(None)
if attempted:raise AssertionError('Probe attempted to open missing native evidence: '+repr(attempted))
print(json.dumps({'result':result,'sources':observed,'dataOpenAttempts':attempted}))
'''
        with tempfile.TemporaryDirectory() as temp:
            probe=Path(temp)/'probe.py';probe.write_text(program)
            result=subprocess.run([sys.executable,'-I','-B',str(probe),str(REPO)],
                capture_output=True,text=True,timeout=120)
        self.assertEqual(result.returncode,0,result.stderr)
        found=json.loads(result.stdout)
        self.assertEqual(found['result'],{'status':'SOURCE_ONLY'})
        self.assertEqual(found['dataOpenAttempts'],[])
        for relative in (
            'packages/calibration/results/2026-10-08-w50-g1-fit/native/run.py',
            'packages/calibration/results/2026-10-08-w50-g0-declaration/audit/next_wave.py',
            'packages/calibration/results/2026-10-08-w50-g0-declaration/audit/closure.py'):
            self.assertIn(relative,found['sources'])

if __name__=='__main__':unittest.main()
