"""Static evidence may be imported; historical source proofs never become live authority."""
import gzip
import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import types
import unittest
from unittest.mock import patch

HERE = Path(__file__).resolve().parent

def module():
    spec = importlib.util.spec_from_file_location('w51_static_test',HERE/'static.py')
    result = importlib.util.module_from_spec(spec); spec.loader.exec_module(result); return result

class StaticTests(unittest.TestCase):
    def setUp(self):
        self.s = module(); self.temp = tempfile.TemporaryDirectory(); self.addCleanup(self.temp.cleanup)
        self.home = Path(self.temp.name).resolve()
    def put(self, name, value):
        path=self.home/name; path.write_text(json.dumps(value)); return {'path':str(path),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}

    def test_exposed_batch_authentication_never_needs_historical_instrument(self):
        batch=self.put('batch.json', {'schema':'w50-native-read-batch-1','exports':[{'role':'calibration'}]})
        context={'repo':str(self.home),'inputs':[batch]}
        live=types.SimpleNamespace(require_context=lambda c: self.assertIs(c,context))
        with patch.dict('sys.modules', {'w50_g1_dispatch':live}):
            result=self.s.native_batch(context,{'batch':batch,'instrument':{'path':'must-not-open'}})
        self.assertEqual(result['exports'],[{'role':'calibration'}])

    def test_unbound_or_blind_static_batch_refuses(self):
        batch=self.put('batch.json', {'schema':'w50-native-read-batch-1','exports':[{'role':'blind'}]})
        context={'repo':str(self.home),'inputs':[batch]}
        live=types.SimpleNamespace(require_context=lambda c: None)
        with patch.dict('sys.modules', {'w50_g1_dispatch':live}):
            with self.assertRaises(ValueError): self.s.native_batch(context,{'batch':batch})
            with self.assertRaises(ValueError): self.s.native_batch({**context,'inputs':[]},{'batch':batch})

if __name__ == '__main__': unittest.main()
