"""Current-only readiness never fabricates a future judge or a candidate admission."""
import copy
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('current_dispatch',HERE/'dispatch.py')
D=importlib.util.module_from_spec(spec); spec.loader.exec_module(D)
spec=importlib.util.spec_from_file_location('current_fixture',HERE/'test_support.py')
F=importlib.util.module_from_spec(spec); spec.loader.exec_module(F)


def write(path,value):
    path.parent.mkdir(parents=True,exist_ok=True); path.write_text(json.dumps(value)+'\n'); return path


def sidecar(path):
    Path(str(path)+'.sha256').write_text(f'{D.sha(path)}  {path.name}\n')


class CurrentOnly(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        self.repo=Path(self.tmp.name)/'repo'; self.repo.mkdir()
        self.home=self.repo/'execution'; self.home.mkdir()
        for name in ('dispatch.py','guard.py','admission.py'):
            shutil.copyfile(HERE/name,self.home/name)
        self.fixture=F.build(self.repo,HERE.parents[1]/'2026-10-08-w50-g0-declaration',D.PROOFS)
        for key in ('one','two'): sidecar(self.fixture[key])
        self.adapter=self.repo/'adapter.py'
        self.adapter.write_text('from w50_g1_dispatch import require_context,require_render_admission\n'
            'from pathlib import Path\nimport hashlib,json,importlib.util\n'
            'def execute_current(context):\n require_context(context)\n'
            ' late=Path(context["repo"])/"late.py"\n'
            ' if late.exists():\n'
            '  s=importlib.util.spec_from_file_location("late",late); m=importlib.util.module_from_spec(s); s.loader.exec_module(m)\n'
            ' records=[]\n'
            ' for run in context["batch"]["runs"]:\n'
            '  require_render_admission(context,run,current=True)\n'
            '  for scene in run["scenes"]:\n'
            '   artifacts={}\n'
            '   for name in ("png","cell","report"):\n'
            '    p=Path(context["output"])/(str(len(records))+name)\n'
            '    p.write_text(json.dumps({"capturePath":"declarationSha256="+run["candidate"]["sha256"][:12],"page":{"candidateDocument":{"declarationSha256":run["candidate"]["sha256"][:12]},"sceneId":scene,"requestedRenderer":run["renderer"],"devicePixelRatio":1}}))\n'
            '    artifacts[name]={"path":str(p),"sha256":hashlib.sha256(p.read_bytes()).hexdigest()}\n'
            '   records.append(dict(profile=run["profile"],renderer=run["renderer"],scene=scene,candidate=run["candidate"],lane="current",artifacts=artifacts))\n'
            ' return {"status":"CAPTURED","candidateSha256s":sorted(p["sha256"] for p in context["batch"]["cohort"]),"captures":records}\n')
        self.probe=self.repo/'current-probe.py'
        self.probe.write_text('from pathlib import Path\nimport importlib.util,sys\nr=Path(__file__).parent\n'
            'def load(name,path):\n s=importlib.util.spec_from_file_location(name,r/path);m=importlib.util.module_from_spec(s);sys.modules[name]=m;s.loader.exec_module(m)\n'
            'load("w50_g1_dispatch","execution/dispatch.py")\n'
            'load("admission","execution/admission.py")\nload("adapter","adapter.py")\n')
        self.sources={str(p.relative_to(self.repo)):D.sha(p) for p in
                      [self.home/n for n in ('dispatch.py','guard.py','admission.py')]+[self.adapter,self.probe]}
        self.batch=self.make_batch('exposed')

    def make_batch(self,scene,phase='current',live=False):
        cohort=self.fixture['cohort'] if live else self.fixture['baselines']
        return write(self.repo/f'{phase}-{scene}.json',dict(schema='w50-g1-batch-1',phase=phase,cohort=cohort,
            runs=[dict(id=f'run{i}',profile=f'apple-macos-27.0-1x-dark-standard-glass{position}',
                       renderer='webgpu',scenes=['impulse__rrect-ml__rest' if scene=='exposed' else scene],
                       sets=['calibration'],candidate=pin)
                  for i,(pin,position) in enumerate(zip(cohort,(.25,.5)))]))

    def seal(self,batch=None):
        f=self.fixture
        return D.seal_current_root(self.repo,self.home,f['one'],f['two'],f['refs'],f['manifest'],
            self.adapter,self.probe,self.sources,f['baselines'],[D.pin(self.repo,batch or self.batch)])

    def execute(self,root,contract,batch):
        script=('import sys,importlib.util;from pathlib import Path;'
                's=importlib.util.spec_from_file_location("w50_g1_dispatch",sys.argv[1]);'
                'd=importlib.util.module_from_spec(s);sys.modules[s.name]=d;s.loader.exec_module(d);'
                'd.GPU_LOCK=Path(sys.argv[6]);d.execute(*map(Path,sys.argv[2:6]))')
        return subprocess.run([sys.executable,'-I','-B','-c',script,str(self.home/'dispatch.py'),
            str(root),str(contract),str(batch),str(Path(self.tmp.name)/'output'),str(Path(self.tmp.name)/'gpu.lock')],
            text=True,capture_output=True)

    def test_current_capture_needs_no_future_judge_fitter_or_prefit(self):
        root=self.seal(); doc=D.root_doc(root)
        self.assertEqual(doc['schema'],'w50-g1-current-instrument-root-1')
        self.assertFalse((self.home/'prefit.py').exists())
        self.assertNotIn('judge',doc); self.assertNotIn('instruments',doc)
        contract=D.current_contract(root,self.batch)
        result=self.execute(root,contract,self.batch); self.assertEqual(result.returncode,0,result.stderr)
        completed=D.result_for(contract)
        self.assertEqual(completed['report']['status'],'CAPTURED')
        self.assertNotIn('analysis',completed['report'])
        self.assertIsNone(json.loads(Path(str(contract)+'.started.json').read_text())['numericalAdmission'])
        self.assertFalse((Path(self.tmp.name)/'gpu.lock').exists())

    def test_every_exposure_closed_group_is_refused_not_only_new_blind(self):
        for scene in ('blind','history'):
            with self.subTest(scene=scene),self.assertRaises(ValueError): self.seal(self.make_batch(scene))

    def test_only_fixed_current_batch_bytes_are_admitted(self):
        root=self.seal()
        other=self.make_batch('impulse__rrect-ml__inactive')
        with self.assertRaises(ValueError): D.current_contract(root,other)
        changed=json.loads(self.batch.read_text()); changed['runs'][0]['id']='changed'; write(self.batch,changed)
        with self.assertRaises(ValueError): D.current_contract(root,self.batch)

    def test_no_live_phase_contract_or_forged_entrypoint_is_admitted(self):
        root=self.seal()
        for phase in ('fit','gate','exposure'):
            batch=self.make_batch('exposed',phase=phase,live=True)
            with self.subTest(phase=phase),self.assertRaises(ValueError): D.create_contract(root,batch,phase)
        batch=self.make_batch('exposed',phase='fit',live=True)
        forged=write(self.home/'fit'/f'{D.sha(batch)}.json',dict(schema='w50-g1-phase-contract-1',phase='fit',
            executionRootSha256=D.sha(root),batch=D.pin(self.repo,batch),cohort=self.fixture['cohort'],preFitEvidence=None))
        sidecar(forged)
        result=self.execute(root,forged,batch); self.assertNotEqual(result.returncode,0)
        self.assertFalse(Path(str(forged)+'.started.json').exists())

    def test_self_reseal_cannot_change_current_root_mode_or_slots(self):
        root=self.seal(); original=json.loads(root.read_text())
        for changed in ({**original,'schema':'w50-g1-execution-root-1'},
                        {**original,'slots':D.SLOTS}, {**original,'judge':D.pin(self.repo,self.adapter)}):
            write(root,changed); sidecar(root)
            with self.assertRaises(ValueError): D.root_doc(root)
        write(root,original); sidecar(root)

    def test_live_gate_one_bytes_are_not_a_current_baseline(self):
        batch=self.make_batch('exposed',live=True)
        with self.assertRaises(ValueError): self.seal(batch)

    def test_registered_live_chart_is_still_not_a_current_baseline(self):
        batch=self.make_batch('exposed',live=True); f=self.fixture
        with self.assertRaises(ValueError):
            D.seal_current_root(self.repo,self.home,f['one'],f['two'],f['refs'],f['manifest'],
                self.adapter,self.probe,self.sources,f['cohort'],[D.pin(self.repo,batch)])

    def test_incomplete_fixed_current_population_cannot_feed_a_live_root(self):
        second=self.make_batch('impulse__rrect-ml__inactive'); f=self.fixture
        root=D.seal_current_root(self.repo,self.home,f['one'],f['two'],f['refs'],f['manifest'],
            self.adapter,self.probe,self.sources,f['baselines'],
            [D.pin(self.repo,self.batch),D.pin(self.repo,second)])
        contract=D.current_contract(root,self.batch)
        result=self.execute(root,contract,self.batch); self.assertEqual(result.returncode,0,result.stderr)
        partial=[D.pin(self.repo,Path(str(contract)+'.result.json'))]
        with self.assertRaises(ValueError):
            D.current_evidence_inputs(self.repo,self.home,D.pin(self.repo,root),partial)

    def test_changed_current_adapter_is_refused_before_import(self):
        root=self.seal(); contract=D.current_contract(root,self.batch)
        self.adapter.write_text(self.adapter.read_text()+'\nraise RuntimeError("MUST NOT EXECUTE")\n')
        result=self.execute(root,contract,self.batch)
        self.assertNotEqual(result.returncode,0)
        self.assertNotIn('RuntimeError: MUST NOT EXECUTE',result.stderr)
        self.assertFalse(Path(str(contract)+'.started.json').exists())

    def test_current_process_guard_and_lease_are_not_optional(self):
        root=self.seal(); contract=D.current_contract(root,self.batch)
        lock=Path(self.tmp.name)/'gpu.lock'; lock.write_text('foreign owner')
        refused=self.execute(root,contract,self.batch)
        self.assertNotEqual(refused.returncode,0); self.assertEqual(lock.read_text(),'foreign owner')
        lock.unlink()
        marker=Path(self.tmp.name)/'unsealed-executed'
        (self.repo/'late.py').write_text(f'from pathlib import Path\nPath({str(marker)!r}).touch()\n')
        refused=self.execute(root,contract,self.batch)
        self.assertNotEqual(refused.returncode,0); self.assertFalse(marker.exists())
        self.assertTrue(Path(str(contract)+'.started.json').exists())

    def test_direct_adapter_context_has_no_dispatcher_authority(self):
        old=sys.modules.get('w50_g1_dispatch'); sys.modules['w50_g1_dispatch']=D
        try:
            spec=importlib.util.spec_from_file_location('direct_current',self.adapter)
            adapter=importlib.util.module_from_spec(spec); spec.loader.exec_module(adapter)
            with self.assertRaises(ValueError): adapter.execute_current({'phase':'current'})
        finally:
            if old is None: sys.modules.pop('w50_g1_dispatch',None)
            else: sys.modules['w50_g1_dispatch']=old


if __name__=='__main__': unittest.main()
