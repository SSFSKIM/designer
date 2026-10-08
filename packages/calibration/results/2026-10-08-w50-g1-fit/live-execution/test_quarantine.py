import contextlib
import importlib.util
import io
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
H=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('quarantine',H/'quarantine.py');Q=importlib.util.module_from_spec(s);s.loader.exec_module(Q)
SECRET='NATIVE_CANARY_87654321.125'

class Quarantine(unittest.TestCase):
    def setUp(self):
        t=tempfile.TemporaryDirectory();self.addCleanup(t.cleanup);self.root=Path(t.name).resolve()
    def test_python_and_child_streams_and_exception_detail_never_escape(self):
        public=io.StringIO()
        def worker():
            print(SECRET);print(SECRET,file=sys.stderr)
            subprocess.run([sys.executable,'-c',f'import sys;print({SECRET!r});print({SECRET!r},file=sys.stderr)'],check=True)
            raise ValueError({'nested':{'nativeRepeat':SECRET}})
        with contextlib.redirect_stdout(public),contextlib.redirect_stderr(public):
            ok,value=Q.run_private(self.root/'quarantine/error.log',worker)
        self.assertFalse(ok);self.assertEqual(value,{'code':'INSTRUMENT_FAULT'})
        self.assertNotIn(SECRET,public.getvalue())
        self.assertIn(SECRET,(self.root/'quarantine/error.log').read_text())
    def test_success_payload_is_not_the_public_projection(self):
        ok,value=Q.run_private(self.root/'quarantine/success.log',lambda:{'native':SECRET})
        self.assertTrue(ok)
        public=Q.public_event('CAPTURE_QUALIFIED',phase='exposure',attempt=1,member='a'*64)
        self.assertNotIn(SECRET,str(public));self.assertNotIn('native',public)
        with self.assertRaises(ValueError):Q.public_event('CAPTURE_QUALIFIED',native=value)
    def test_numeric_status_fields_cannot_smuggle_exception_text(self):
        for field in ('attempt','retained','remaining','analysisStarted','nativeComplete','member'):
            with self.assertRaises(ValueError):Q.public_event('REFUSED',**{field:SECRET})
    def test_unknown_error_strings_cannot_be_published(self):
        with self.assertRaises(ValueError):Q.public_event(SECRET,phase='exposure')
    def test_payload_gate_is_live_capability_not_presence_of_a_marker(self):
        context={'stage':'analysis'}
        p=self.root/'payload.json';p.write_text('{"native":"'+SECRET+'"}')
        old=sys.modules.pop('w50_g1_dispatch',None)
        try:
            with self.assertRaises(ValueError):Q.read_payload(context,{'path':str(p),'sha256':Q.sha(p)})
        finally:
            if old is not None:sys.modules['w50_g1_dispatch']=old

if __name__=='__main__':unittest.main()
