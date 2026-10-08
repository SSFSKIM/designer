"""Synthetic routing checks; no source adapter launches or real captures."""
import importlib.util
from pathlib import Path
from types import SimpleNamespace
import sys
import unittest
from unittest.mock import patch

PATH = Path(__file__).with_name('current_router.py')
spec = importlib.util.spec_from_file_location('w50_current_router_test', PATH)
R = importlib.util.module_from_spec(spec)
spec.loader.exec_module(R)


class RouterTests(unittest.TestCase):
    def context(self, sources=('w50', 'canonical')):
        docs = [{'path':'a.json','sha256':'a'*64}, {'path':'b.json','sha256':'b'*64}]
        return {'phase':'current','batch':{'phase':'current','cohort':docs,
                'runs':[{'id':str(i),'sceneSource':s,'candidate':docs[i % 2]}
                        for i,s in enumerate(sources)]}}

    def test_keeps_one_context_and_routes_registered_runs_without_rewriting_them(self):
        context=self.context(); calls=[]
        def capture(ctx,run,*,current):
            self.assertIs(ctx,context); self.assertTrue(current)
            self.assertTrue(any(run is r for r in context['batch']['runs']))
            calls.append(run['sceneSource']); return [{'source':run['sceneSource']}]
        modules={name:SimpleNamespace(capture_run=capture,_capture_run=capture) for name in ('w50','canonical')}
        def require(ctx): self.assertIs(ctx,context)
        with patch.dict(sys.modules,{'w50_g1_dispatch':SimpleNamespace(require_context=require)}), patch.object(R,'adapters',return_value=modules):
            result=R.execute_current(context)
        self.assertEqual(calls,['w50','canonical'])
        self.assertEqual(result['status'],'CAPTURED')
        self.assertEqual(result['candidateSha256s'],['a'*64,'b'*64])
        self.assertEqual(result['captures'],[{'source':'w50'},{'source':'canonical'}])

    def test_refuses_candidate_phases_before_loading_capture_helpers(self):
        for phase in ('fit','gate','exposure'):
            context=self.context(); context['phase']=phase
            with patch.dict(sys.modules,{'w50_g1_dispatch':SimpleNamespace(require_context=lambda c:None)}), patch.object(R,'adapters',side_effect=AssertionError('helper executed')):
                with self.assertRaises(ValueError): R.execute_current(context)

    def test_refuses_unknown_source_before_any_partial_capture(self):
        context=self.context(('w50','unknown'))
        with patch.dict(sys.modules,{'w50_g1_dispatch':SimpleNamespace(require_context=lambda c:None)}), patch.object(R,'adapters',side_effect=AssertionError('helper executed')):
            with self.assertRaises(ValueError): R.execute_current(context)

    def test_refuses_without_a_live_dispatcher_before_helper_import(self):
        with patch.dict(sys.modules,{'w50_g1_dispatch':None}), patch.object(R,'adapters',side_effect=AssertionError('helper executed')):
            with self.assertRaises(ValueError): R.execute_current(self.context())


if __name__=='__main__': unittest.main()
