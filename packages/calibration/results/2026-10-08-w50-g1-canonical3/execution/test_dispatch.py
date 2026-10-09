"""Synthetic capability/one-shot tests: no real GPU or capture subprocess."""
import copy
import importlib.util
from pathlib import Path
import sys
import subprocess
import tempfile
import unittest

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('canonical3_dispatch_test',HERE/'dispatch.py')
D=importlib.util.module_from_spec(spec);sys.modules[spec.name]=D;spec.loader.exec_module(D)

class Capability(unittest.TestCase):
    def setUp(self):
        t=tempfile.TemporaryDirectory();self.addCleanup(t.cleanup);self.repo=Path(t.name).resolve()
        self.oldlock=D.C.D.GPU_LOCK;D.C.D.GPU_LOCK=self.repo/'lease'
        self.addCleanup(setattr,D.C.D,'GPU_LOCK',self.oldlock)
        self.addCleanup(setattr,D,'_ACTIVE',None)
        self.contract=self.repo/'contract.json';self.contract.write_text('{}')
        self.batch=self.repo/'batch.json';self.batch.write_text('{}')
        self.context={'contract':str(self.contract),'batchPath':str(self.batch),'phase':'current'}
    def activate(self):
        D._ACTIVE=(self.context,copy.deepcopy(self.context),D.sha(self.contract),D.sha(self.batch),{})
    def test_direct_and_copied_context_cannot_authorize_transport(self):
        with self.assertRaises(ValueError):D.require_context(self.context)
        with D.C.D.owned_gpu_lock():
            self.activate();self.assertIs(D.require_context(self.context),self.context)
            with self.assertRaises(ValueError):D.require_context(copy.deepcopy(self.context))
        with self.assertRaises(ValueError):D.require_context(self.context)
    def test_mutated_context_or_batch_loses_authority(self):
        with D.C.D.owned_gpu_lock():
            self.activate();self.context['invented']=True
            with self.assertRaises(ValueError):D.require_context(self.context)
            del self.context['invented'];self.batch.write_text('{"changed":true}')
            with self.assertRaises(ValueError):D.require_context(self.context)
    def test_foreign_lease_is_not_removed(self):
        D.C.D.GPU_LOCK.write_text('foreign')
        with self.assertRaises(FileExistsError):
            with D.C.D.owned_gpu_lock():pass
        self.assertEqual(D.C.D.GPU_LOCK.read_text(),'foreign')
    def test_recovery_preserves_original_interpreter_and_package_environment(self):
        prior={'closure':{'environment':{'python':'original','packages':[['numpy','pinned']]}}}
        D.preserve_environment(prior,copy.deepcopy(prior['closure']))
        for changed in ({'python':'other','packages':[['numpy','pinned']]},{'python':'original','packages':[]}):
            with self.assertRaises(ValueError):D.preserve_environment(prior,{'environment':changed})
    def test_cli_refuses_live_phases_and_incomplete_execute(self):
        for args in (['gate'],['execute']):
            result=subprocess.run([sys.executable,'-I','-B',str(HERE/'dispatch.py'),*args],capture_output=True,text=True)
            self.assertNotEqual(result.returncode,0)
    def test_recovery_dispatcher_has_no_fit_gate_or_exposure_contract(self):
        for name in ('fit_contract','gate_contract','exposure_contract','seal_root'):
            self.assertFalse(hasattr(D,name))

if __name__=='__main__':unittest.main()
