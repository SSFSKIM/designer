"""The LIVE report validator's wiring in common.py (W50 DL5m item 4); its verdict behaviour is
exercised on synthetic judge reports in judge/test_live.py (UnmeasuredReportedTests)."""
import ast
import copy
import importlib.util
import json
import inspect
from pathlib import Path
import sys
import tempfile
import textwrap
import unittest
H=Path(__file__).resolve().parent

def module(name):
    s=importlib.util.spec_from_file_location('report_test_'+name,H/(name+'.py'));m=importlib.util.module_from_spec(s)
    sys.modules[s.name]=m;s.loader.exec_module(m);return m

R=module('common')


def function(source):
    node=ast.parse(textwrap.dedent(source)).body[0]
    if isinstance(node.body[0],ast.Expr) and isinstance(node.body[0].value,ast.Constant):node.body=node.body[1:]
    return node


class Unqualify(ast.NodeTransformer):
    def visit_Attribute(self,node):
        self.generic_visit(node)
        if isinstance(node.value,ast.Name) and node.value.id=='D':return ast.copy_location(ast.Name(node.attr,node.ctx),node)
        return node


class Restore(ast.NodeTransformer):
    """Replace each occurrence of one expression by another (both given as source text)."""
    def __init__(self,live,original):
        self.live=ast.dump(ast.parse(live,mode='eval').body);self.original=ast.parse(original,mode='eval').body
    def visit(self,node):
        if ast.dump(node)==self.live:return ast.copy_location(copy.deepcopy(self.original),node)
        return super().visit(node)


class Wiring(unittest.TestCase):
    def test_gate_result_check_is_current3s_own_with_only_the_validator_and_slot_rebound(self):
        original=function(inspect.getsource(R.D.checked_gate_result))
        live=Unqualify().visit(function(inspect.getsource(R.checked_gate_result)))
        # The one textual difference: the gate is this root's own slot (DL5o), not the shared name.
        live=Restore("slot(path, 'gate')","Path(path).resolve().parent / SLOTS['gate']").visit(live)
        self.assertEqual(ast.dump(live),ast.dump(original))
        self.assertIs(R.checked_gate_result.__globals__['validate_report'],R.validate_report)
        self.assertIs(R.checked_gate_result.__globals__['slot'],R.slot)

    def test_every_live_report_validation_goes_through_the_live_validator(self):
        tree=ast.parse((H/'dispatch.py').read_text())
        uses=[n for n in ast.walk(tree) if isinstance(n,ast.Attribute) and n.attr in ('validate_report','checked_gate_result')]
        # create_phase and _phase read the gate; analysis and an interrupted result's seal validate.
        self.assertEqual(len(uses),4)
        for node in uses:
            self.assertEqual(ast.unparse(node.value),"_CORE['C']")


class NativeReadiness(unittest.TestCase):
    """Second pre-seal review P3: the readiness an exposure report states binds its stops."""
    P='apple-macos-27.0-1x-dark-standard-glass0.5'
    STOP={'cell':P+'/cell-grey-004-s224__rest','statistic':'deep8-channel-median','reason':'NATIVE_SPREAD_EXCEEDS_ONE_CODE'}
    def setUp(self):
        t=tempfile.TemporaryDirectory();self.addCleanup(t.cleanup);repo=Path(t.name)
        self.keys=[(self.P,r,s,'deep8-channel-median') for r in ('webgpu','css')
                   for s in ('cell-grey-004-s224__rest','cell-grey-007-s224__rest')]
        refs=repo/'references.json';refs.write_text(json.dumps({'cells':[dict(zip(R.D.KEY,k),role='blind') for k in self.keys]}))
        self.doc={'repo':str(repo),'references':R.D.pin(repo,refs),'reportedKeys':[]}
        self.expected=[dict(zip(R.D.KEY,k)) for k in self.keys]
    def report(self,stops=(),status='NEITHER'):
        stopped=sorted(k for k in self.keys if any(k[0]+'/'+k[2]==s['cell'] and k[3]==s['statistic'] for s in stops))
        cells=[dict(zip(R.D.KEY,k),status='PASS') for k in self.keys]
        for cell in cells:
            if tuple(cell[k] for k in R.D.KEY) in stopped:
                cell.update(status='UNMEASURED',cause={'kind':'NATIVE_NOT_READY','reason':'NATIVE_SPREAD_EXCEEDS_ONE_CODE'},
                            **dict.fromkeys(R.NULL_FIELDS))
        return {'phase':'exposure','status':status,'cells':cells,
                'nativeReadiness':{'ready':not stops,'stops':[dict(s) for s in stops],'stoppedKeys':[list(k) for k in stopped]}}
    def test_stated_readiness_and_stops_pass(self):
        R.check_native_not_ready(self.doc,self.report(),self.expected)
        R.check_native_not_ready(self.doc,self.report([self.STOP]),self.expected)
        R.check_native_not_ready(self.doc,{'phase':'gate','status':'PASS_EXPOSED_OWNER_PENDING','cells':[]},self.expected)
    def test_readiness_that_differs_from_its_stops_refuses(self):
        def mutate(change,stops=(self.STOP,)):
            report=self.report(stops);change(report);return report
        cases={
            'not ready, no stopped keys, PASS':lambda r:(r.update(status='PASS'),r['nativeReadiness'].update(stops=[],stoppedKeys=[])),
            'not ready without stops':lambda r:r['nativeReadiness'].update(stops=[],stoppedKeys=[]),
            'not ready on a PASS verdict':lambda r:r.update(status='PASS'),
            'one renderer of a stop':lambda r:r['nativeReadiness']['stoppedKeys'].pop(),
            'an unstopped key listed':lambda r:r['nativeReadiness']['stoppedKeys'].append([self.P,'webgpu','cell-grey-007-s224__rest','deep8-channel-median']),
            'a stop naming no phase key':lambda r:r['nativeReadiness']['stops'].append({**self.STOP,'cell':self.P+'/cell-absent__rest'}),
            'a value-bearing stop':lambda r:r['nativeReadiness']['stops'][0].update(repeat=[1,2,3]),
            'readiness omitted':lambda r:r.pop('nativeReadiness'),
            'a stopped key read PASS':lambda r:next(c for c in r['cells'] if c.get('cause')).update(status='PASS',cause=None),
            'ready beside a stop':lambda r:r['nativeReadiness'].update(ready=True),
        }
        for name,change in cases.items():
            with self.subTest(name),self.assertRaises(ValueError):
                R.check_native_not_ready(self.doc,mutate(change),self.expected)
        with self.assertRaisesRegex(ValueError,'exposure report only'):
            R.check_native_not_ready(self.doc,{'phase':'gate','cells':[],'nativeReadiness':self.report()['nativeReadiness']},self.expected)
    def test_the_live_validator_runs_the_check_before_current3(self):
        report=self.report([self.STOP]);report['nativeReadiness']['stoppedKeys']=[]
        with self.assertRaisesRegex(ValueError,'NATIVE_NOT_READY'):
            R.validate_report(self.doc,{},self.expected,report)

if __name__=='__main__':unittest.main()
