import copy
import importlib.util
from pathlib import Path
import sys
import tempfile
import types
import unittest
H=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('live_dispatch_test',H/'dispatch.py');D=importlib.util.module_from_spec(s);sys.modules[s.name]=D;s.loader.exec_module(D)

class Capability(unittest.TestCase):
    def setUp(self):
        t=tempfile.TemporaryDirectory();self.addCleanup(t.cleanup);self.p=Path(t.name).resolve()/'claim';self.p.write_text('{}')
        self.old=D._CORE;D._CORE={'C':types.SimpleNamespace(D=types.SimpleNamespace(lease_owned=lambda:True))}
        self.addCleanup(setattr,D,'_CORE',self.old);self.addCleanup(setattr,D,'_ACTIVE',None)
        self.ctx={'stage':'capture','contract':str(self.p),'batchPath':str(self.p),'executionClaim':{'path':str(self.p),'sha256':D.sha(self.p)}}
    def activate(self):
        D._ACTIVE={'context':self.ctx,'snapshot':copy.deepcopy(self.ctx),'hashes':[(str(self.p),D.sha(self.p))],
            'members':[],'payloads':[]}
    def test_forged_and_mutated_context_cannot_read_payload_or_launch(self):
        with self.assertRaises(ValueError):D.require_context(self.ctx)
        self.activate();D.require_context(self.ctx)
        with self.assertRaises(ValueError):D.require_context(copy.deepcopy(self.ctx))
        self.ctx['stage']='analysis'
        with self.assertRaises(ValueError):D.require_context(self.ctx)
    def test_marker_or_analysis_label_alone_cannot_unseal_arbitrary_payload(self):
        self.ctx['stage']='analysis';self.activate()
        with self.assertRaises(ValueError):D.require_payload(self.ctx,{'path':str(self.p),'sha256':D.sha(self.p)})
    def test_only_registered_complete_union_payload_is_readable_in_analysis(self):
        self.ctx['stage']='analysis';self.activate();item={'path':str(self.p),'sha256':D.sha(self.p)}
        D._ACTIVE['payloads']=[item];D.require_payload(self.ctx,item)
        self.ctx['stage']='capture';D._ACTIVE['snapshot']=copy.deepcopy(self.ctx)
        with self.assertRaises(ValueError):D.require_payload(self.ctx,item)
    def test_changed_execution_claim_revokes_capability(self):
        self.activate();self.p.write_text('{"changed":true}')
        with self.assertRaises(ValueError):D.require_context(self.ctx)

if __name__=='__main__':unittest.main()
