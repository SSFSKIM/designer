"""Permanent source guard rejects changed/new code through publication, not just bootstrap."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent

class GuardTests(unittest.TestCase):
    def check(self, action):
        with tempfile.TemporaryDirectory() as folder:
            folder = Path(folder).resolve(); source = folder/'module.py'
            source.write_text('def value(): return 7\n')
            expected = {'module.py':hashlib.sha256(source.read_bytes()).hexdigest()}
            code = '''import json,runpy,sys\nfrom pathlib import Path\ng=runpy.run_path(sys.argv[1])\np=Path(sys.argv[2]); expected=json.loads(sys.argv[3])\ng['enforce'](p,expected)\n'''+action
            return subprocess.run([sys.executable,'-I','-B','-c',code,str(HERE/'guard.py'),str(folder),json.dumps(expected)],
                                  capture_output=True,text=True)

    def test_unchanged_module_then_late_changed_source_refuses(self):
        result = self.check("m=runpy.run_path(str(p/'module.py')); assert m['value']()==7\n(p/'module.py').write_text('def value(): return 8\\n')\nrunpy.run_path(str(p/'module.py'))")
        self.assertNotEqual(result.returncode,0)
        self.assertIn('Changed or unsealed',result.stderr)

    def test_late_new_import_refuses(self):
        result = self.check("(p/'late.py').write_text('value=9\\n')\nrunpy.run_path(str(p/'late.py'))")
        self.assertNotEqual(result.returncode,0)
        self.assertIn('Changed or unsealed',result.stderr)

    def test_guard_stays_live_during_output_writes(self):
        result = self.check("m=runpy.run_path(str(p/'module.py')); (p/'report.json').write_text('{}'); assert m['value']()==7")
        self.assertEqual(result.returncode,0,result.stderr)

if __name__ == '__main__': unittest.main()
