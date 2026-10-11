"""DL5 scalar policy code executes inside the same permanently closed source guard."""
import json
from pathlib import Path
import runpy
import subprocess
import sys
import unittest

HERE = Path(__file__).resolve().parent


class PolicyProbeTests(unittest.TestCase):
    def test_source_only_discovery_then_closed_probe_exercises_policy(self):
        build = runpy.run_path(str(HERE/'build.py'))
        closure = build['discover']()
        child = '''import json,runpy,sys
from pathlib import Path
here=Path(sys.argv[1]); expected=json.loads(sys.stdin.read())
guard=runpy.run_path(str(here/'guard.py'))
guard['enforce'](here.parents[3],expected)
probe=runpy.run_path(str(here/'probe.py'))
print(json.dumps(probe['exercise']()))
'''
        result = subprocess.run([sys.executable, '-I', '-B', '-c', child, str(HERE)],
            input=json.dumps(closure['sources']), capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout), {'status':'SOURCE_ONLY', 'landingPolicy':'WITHIN'})


if __name__ == '__main__': unittest.main()
