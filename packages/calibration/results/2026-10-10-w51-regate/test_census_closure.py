"""Closure discovery must cover the late census imports on both real launch paths.

Only capability and operating-system reads are supplied by the test. The adapters, import
loaders, observer, transitive observer imports, classifier and permanent guard are real.
A synthetic refusing census stops each path before it could launch a renderer.
"""
import json
import os
from pathlib import Path
import runpy
import subprocess
import sys
import tempfile
import unittest

HERE=Path(__file__).resolve().parent
R=runpy.run_path(str(HERE/'root.py'))

CHILD=r'''
import copy,json,os,runpy,sys,types
from pathlib import Path
here=Path(sys.argv[1]);home=Path(sys.argv[2]);lane=sys.argv[3]
expected=json.loads(sys.stdin.read());repo=here.parents[3]
guard=runpy.run_path(str(here/'guard.py'));guard['enforce'](repo,expected)
r=runpy.run_path(str(here/'root.py'))
# These are immutable declaration/transport inputs, not historical capture authority.
root=r['load'](here/'execution-root.final-draft.json')
science=r['load'](r['checked'](repo,root['datasets']['real']))
batch=r['load'](r['checked'](repo,root['batches']['real-rehearsal']))
context={'repo':str(repo),'phase':'gate','inputs':science['inputs'],'output':str(home)}
run=copy.deepcopy(next(item for item in batch['runs'] if item['sceneSource']==lane))
run['scenes']=run['scenes'][:1];run['captureRoot']=str(home/'captures');run['matrixPath']=str(home/'matrix.json')
def require_context(value):
    if value is not context:raise AssertionError('Wrong context')
def require_render(value,actual,current=False):
    require_context(value)
    if actual!=run or current:raise AssertionError('Wrong member')
sys.modules['w50_g1_dispatch']=types.SimpleNamespace(require_context=require_context,
    require_render_admission=require_render)
adapter=r['source'](here/('canonical' if lane=='canonical' else 'web')/'adapter.py','w51_census_test_'+lane)
import subprocess
calls=[]
def operating_system(args,**kwargs):
    calls.append(args)
    if args[0]=='defaults':
        output='1' if args[-1]=='reduceTransparency' else '0.5' if args[-1]=='NSGlassTintAmount' else '0'
    elif args[0]=='ps':output=f'{os.getpid()} 1 python-source-probe\n'
    elif args[0]=='ioreg':output='"HIDIdleTime" = 60000000000'
    else:raise AssertionError('Renderer or unexpected command reached: '+str(args))
    return subprocess.CompletedProcess(args,0,output,'')
subprocess.run=operating_system
try:
    if lane=='canonical':
        Path(run['captureRoot']).mkdir()
        adapter.launch_cells(context,run,[],{},Path(run['captureRoot']))
    else:adapter._capture_run(context,run,current=False)
except ValueError as error:
    if 'Classifying census refused' not in str(error):raise
else:raise AssertionError('Synthetic refusal did not stop launch')
record=json.loads((Path(run['captureRoot'])/('census-'+run['scenes'][0]+'.json')).read_bytes())
assert record['passes'] is False and record['refusals']==['reduceTransparency']
assert {command[0] for command in calls}=={'defaults','ps','ioreg'}
assert not list(home.rglob('*.png'))
print('GUARDED_CENSUS_REFUSAL '+lane)
'''


class CensusClosureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.closure=R['source'](HERE/'build.py','w51_census_discovery').discover()

    def child(self,lane,sources):
        with tempfile.TemporaryDirectory() as directory:
            return subprocess.run([sys.executable,'-I','-B','-c',CHILD,str(HERE),
                str(Path(directory).resolve()),lane],input=json.dumps(sources),capture_output=True,text=True)

    def test_both_launch_paths_reach_refusing_census_under_discovered_guard(self):
        for lane in ('canonical','w50'):
            with self.subTest(lane=lane):
                result=self.child(lane,self.closure['sources'])
                self.assertEqual(result.returncode,0,result.stderr)
                self.assertEqual(result.stdout.strip(),'GUARDED_CENSUS_REFUSAL '+lane)

    def test_omitted_transitive_observer_is_still_refused(self):
        sources=dict(self.closure['sources'])
        missing='packages/calibration/results/2026-09-26-w39-g0-colour-edge-bed/record-machine.py'
        sources.pop(missing,None)
        result=self.child('canonical',sources)
        self.assertNotEqual(result.returncode,0)
        self.assertIn('Changed or unsealed executed import: '+missing,result.stderr)

if __name__=='__main__':unittest.main()
