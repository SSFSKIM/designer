"""Exercise configured original/current2 source probes, never real roots or measured data."""
import copy
import json
from pathlib import Path
import subprocess
import tempfile
import types
import unittest
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
FIT = HERE.parent
CURRENT2 = FIT.parent/'2026-10-08-w50-g1-current2'


def source(path, name):
    module = types.ModuleType(name); module.__file__ = str(path)
    exec(compile(path.read_bytes(), str(path), 'exec'), module.__dict__)
    return module


R = source(HERE/'run.py', 'synthetic_selected_probe')


class ProbeTests(unittest.TestCase):
    def fixture(self, repo, replacement):
        # Copy SOURCE only. No descriptor, capture, report, result, statistic or failed-attempt data.
        for directory in (FIT/'current-analysis', FIT/'native', FIT/'measurement', FIT/'web', FIT/'canonical',
                          FIT/'execution', R.G0/'audit', CURRENT2/'execution', CURRENT2/'web'):
            for path in directory.glob('*.py'):
                destination = repo/path.relative_to(R.REPO); destination.parent.mkdir(parents=True,exist_ok=True)
                destination.write_bytes(path.read_bytes())
        for path in (FIT/'current_probe.py', FIT/'current_router.py', CURRENT2/'current_probe.py',
                     CURRENT2/'current_router.py', FIT.parent/'2026-10-02-w43-g3-refit/stage/census.py',
                     FIT.parent/'2026-09-27-w41-g1-identification/x6/observe.py',
                     FIT.parent/'2026-09-26-w39-g0-colour-edge-bed/record-machine.py',
                     FIT.parent/'2026-10-03-w44-g0-declaration/port/interior.py'):
            destination = repo/path.relative_to(R.REPO); destination.parent.mkdir(parents=True,exist_ok=True)
            destination.write_bytes(path.read_bytes())
        fit = repo/FIT.relative_to(R.REPO); g0 = repo/R.G0.relative_to(R.REPO)
        scene = dict(id='cell-grey-004-s096__rest', state='rest', component='rrect', background='grey')
        document = dict(canvas={'width':512,'height':384}, scenes=[scene], split={'calibration':[scene['id']]},
                        components={'rrect':dict(kind='rrect',size=[96,96],radius=20)})
        p = g0/'bed/scenes-w50.json'; p.parent.mkdir(); p.write_text(json.dumps(document))
        selected = repo/(CURRENT2 if replacement else FIT).relative_to(R.REPO)
        bootstrap = selected/'execution/dispatch.py'; probe = selected/'current_probe.py'
        guard = source(g0/'audit/closure.py', 'synthetic_discovery_guard')
        closure = guard.discover(repo, probe)
        descriptor = dict(bootstrap=R.pin(repo,bootstrap),probe=R.pin(repo,probe),closure=closure)
        root_path = bootstrap.parent/'synthetic-descriptor.json'; root_path.write_text(json.dumps(descriptor))
        return fit,g0,root_path,descriptor

    def discover(self, repo, fit, g0, path):
        with patch.multiple(R, REPO=repo, FIT=fit, HERE=fit/'current-analysis',
                            PROBE=fit/'current-analysis/probe.py', GUARD=g0/'audit/closure.py'):
            return R.discover({'instrument':R.pin(repo,path)})

    def test_exact_descriptor_probe_exercises_replacement_and_actual_read_guard_enforces_it(self):
        for replacement in (False,True):
            with self.subTest(replacement=replacement), tempfile.TemporaryDirectory() as td:
                repo = Path(td).resolve(); fit,g0,path,descriptor = self.fixture(repo,replacement)
                closure = self.discover(repo,fit,g0,path)
                self.assertIn(descriptor['probe']['path'],closure['sources'])
                if replacement:
                    replacement_path = path.parent/'replacement.py'
                    relative = str(replacement_path.relative_to(repo))
                    self.assertIn(relative,closure['sources'])
                    # Enforce in a fresh isolated child: the permanent audit hook must not leak
                    # into other tests. This is source loading, not root_doc or a live wrapper.
                    program = """import json, pathlib, types, sys
repo=pathlib.Path(sys.argv[1]); expected=json.loads(sys.argv[2])
def source(path,name):
    m=types.ModuleType(name); m.__file__=str(path)
    exec(compile(path.read_bytes(),str(path),'exec'),m.__dict__); return m
source(pathlib.Path(sys.argv[3]),'guard').enforce(repo,expected)
source(pathlib.Path(sys.argv[4]),'replacement')
source(pathlib.Path(sys.argv[5]),'full_probe')
print('SOURCE_ONLY_UNDER_ENFORCE')
"""
                    args = [str(R.source(R.GUARD,'source_guard').PYTHON),'-I','-B','-c',program,str(repo),
                            json.dumps(closure['sources']),str(g0/'audit/closure.py'),str(replacement_path),
                            str(repo/descriptor['probe']['path'])]
                    result = subprocess.run(args,capture_output=True,text=True)
                    self.assertEqual(result.returncode,0,result.stderr)
                    self.assertEqual(result.stdout.strip(),'SOURCE_ONLY_UNDER_ENFORCE')
                    expected = copy.deepcopy(closure['sources']); expected.pop(relative)
                    args[6] = json.dumps(expected)
                    rejected = subprocess.run(args,capture_output=True,text=True)
                    self.assertNotEqual(rejected.returncode,0)
                    self.assertIn('unsealed',rejected.stderr)

    def test_descriptor_probe_pin_must_be_exact_and_inside_its_original_closure(self):
        for mutation in ('pin','closure'):
            with self.subTest(mutation=mutation), tempfile.TemporaryDirectory() as td:
                repo = Path(td).resolve(); fit,g0,path,descriptor = self.fixture(repo,True)
                if mutation=='pin': descriptor['probe']['sha256']='0'*64
                else: descriptor['closure']['sources'].pop(descriptor['probe']['path'])
                path.write_text(json.dumps(descriptor))
                with self.assertRaises(ValueError): self.discover(repo,fit,g0,path)


if __name__=='__main__': unittest.main()
