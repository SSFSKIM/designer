import importlib.util
from pathlib import Path
import unittest
import types
H=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('authority',H/'authority.py');A=importlib.util.module_from_spec(s);s.loader.exec_module(A)
class Authority(unittest.TestCase):
    def test_initializer_is_not_a_post_capture_fitter_placeholder(self):
        initializer=types.SimpleNamespace(initialize=lambda:None,assemble=lambda:None,bind_arguments=lambda:None)
        A.instrument_interface('initializer',initializer)
        with self.assertRaises(ValueError):A.instrument_interface('fit',initializer)
        with self.assertRaises(ValueError):A.instrument_interface('capture',types.SimpleNamespace(capture=lambda:None,verify=lambda:None))
    def test_missing_real_components_cannot_form_live_root(self):
        for roles in ({},{'fit':{}},{r:{} for r in A.ROLES}):
            with self.assertRaises(ValueError):A.instrument_shape(roles)
    def test_prospective_components_have_both_source_and_config_not_status_placeholders(self):
        p={'path':'source.py','sha256':'a'*64};c={'path':'config.json','sha256':'b'*64}
        roles={r:{'entrypoint':p,'config':c} for r in A.ROLES};A.instrument_shape(roles)
        for field in ('entrypoint','config'):
            broken={**roles,'judge':{**roles['judge'],field:{'status':'PENDING'}}}
            with self.assertRaises(ValueError):A.instrument_shape(broken)
if __name__=='__main__':unittest.main()
