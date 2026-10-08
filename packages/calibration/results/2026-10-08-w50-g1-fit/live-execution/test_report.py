"""The LIVE report validator's wiring in common.py (W50 DL5m item 4); its verdict behaviour is
exercised on synthetic judge reports in judge/test_live.py (UnmeasuredReportedTests)."""
import ast
import importlib.util
import inspect
from pathlib import Path
import sys
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


class Wiring(unittest.TestCase):
    def test_gate_result_check_is_current3s_own_with_only_the_validator_rebound(self):
        original=function(inspect.getsource(R.D.checked_gate_result))
        live=Unqualify().visit(function(inspect.getsource(R.checked_gate_result)))
        self.assertEqual(ast.dump(live),ast.dump(original))
        self.assertIs(R.checked_gate_result.__globals__['validate_report'],R.validate_report)

    def test_every_live_report_validation_goes_through_the_live_validator(self):
        tree=ast.parse((H/'dispatch.py').read_text())
        uses=[n for n in ast.walk(tree) if isinstance(n,ast.Attribute) and n.attr in ('validate_report','checked_gate_result')]
        # create_phase and _phase read the gate; analysis and an interrupted result's seal validate.
        self.assertEqual(len(uses),4)
        for node in uses:
            self.assertEqual(ast.unparse(node.value),"_CORE['C']")

if __name__=='__main__':unittest.main()
