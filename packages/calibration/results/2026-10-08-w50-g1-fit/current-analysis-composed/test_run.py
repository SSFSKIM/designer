"""Stdlib-only composed bootstrap metadata over synthetic descriptors, never real inputs."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import types
import unittest

HERE=Path(__file__).resolve().parent


def source(path,name):
    value=types.ModuleType(name);value.__file__=str(path)
    exec(compile(path.read_bytes(),str(path),'exec'),value.__dict__)
    return value


class BootstrapTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.b=source(HERE/'run.py','composed_bootstrap_test')

    def fixture(self,directory):
        repo=Path(directory).resolve()
        def put(path,value):
            path.parent.mkdir(parents=True,exist_ok=True)
            path.write_bytes(value if isinstance(value,bytes) else json.dumps(value).encode())
            return {'path':str(path.relative_to(repo)),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
        roots=[]
        for name in ('newbed','canonical'):
            home=repo/name/'execution'
            bootstrap=put(home/'dispatch.py',b'pass\n');probe=put(home.parent/'current_probe.py',b'pass\n')
            doc=dict(schema='w50-g1-current-instrument-root-1',repo=str(repo),bootstrap=bootstrap,probe=probe,
                closure={'sources':{p['path']:p['sha256'] for p in (bootstrap,probe)}})
            root_path=home/'current-instrument-root.json'
            root_pin=put(root_path,doc)
            Path(str(root_path)+'.sha256').write_text(f'{root_pin["sha256"]}  {root_path.name}\n')
            roots.append(root_pin)
        manifest=dict(schema='w50-completed-current-composition-1',originalInstrument=roots[0],chains=[
            dict(instrument=p,batch={'path':f'{i}/batch.json','sha256':'a'*64},
                 contract={'path':f'{i}/contract.json','sha256':'b'*64},
                 result={'path':f'{i}/result.json','sha256':'c'*64}) for i,p in enumerate(roots)])
        descriptor=put(repo/'composition.json',manifest)
        return repo,descriptor,manifest,put

    def test_import_does_not_load_numerical_or_image_packages_before_source_admission(self):
        script=('import pathlib,types,sys; p=pathlib.Path(sys.argv[1]);m=types.ModuleType("stdlib_check");'
            'm.__file__=str(p);exec(compile(p.read_bytes(),str(p),"exec"),m.__dict__);'
            'assert not ({"numpy","scipy","PIL"}&set(sys.modules))')
        result=subprocess.run([sys.executable,'-I','-B','-c',script,str(HERE/'run.py')],capture_output=True,text=True)
        self.assertEqual(result.returncode,0,result.stderr)

    def test_source_metadata_checks_both_real_selections_without_opening_result_paths(self):
        with tempfile.TemporaryDirectory() as td:
            repo,pin,manifest,_=self.fixture(td)
            found,roots=self.b.composition_metadata(repo,pin)
            self.assertEqual(found,manifest)
            self.assertEqual([r['pin'] for r in roots],[c['instrument'] for c in manifest['chains']])
            self.assertFalse((repo/'0/result.json').exists())
            self.assertFalse((repo/'1/result.json').exists())

    def test_wrong_composition_root_order_or_changed_source_refuses_before_import(self):
        for mutation in ('same-root','original','source'):
            with self.subTest(mutation=mutation),tempfile.TemporaryDirectory() as td:
                repo,pin,manifest,put=self.fixture(td)
                if mutation=='same-root':manifest['chains'][1]['instrument']=manifest['chains'][0]['instrument']
                elif mutation=='original':manifest['originalInstrument']=manifest['chains'][1]['instrument']
                else:(repo/'canonical/execution/dispatch.py').write_text('raise RuntimeError("not executed")')
                if mutation!='source':pin=put(repo/'composition.json',manifest)
                with self.assertRaises(ValueError):self.b.composition_metadata(repo,pin)

    def test_external_root_hash_is_checked_before_any_config_or_helper(self):
        with tempfile.TemporaryDirectory() as td:
            repo=Path(td).resolve();path=repo/'instrument-root.json';path.write_text('{}')
            with self.assertRaisesRegex(ValueError,'external'):
                self.b.admit_root(path,'0'*64,repo=repo)

    def test_write_once_never_overwrites_and_rejects_nonfinite_before_creation(self):
        with tempfile.TemporaryDirectory() as td:
            path=Path(td).resolve()/'evidence.json';self.b.write_once(path,{'status':'EVIDENCE_ONLY'})
            before=path.read_bytes()
            with self.assertRaises(FileExistsError):self.b.write_once(path,{'status':'PASS'})
            self.assertEqual(path.read_bytes(),before)
            bad=path.parent/'bad.json'
            with self.assertRaises(ValueError):self.b.write_once(bad,{'value':float('nan')})
            self.assertFalse(bad.exists())


if __name__=='__main__':unittest.main()
