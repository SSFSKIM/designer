"""Synthetic contracts only. No production contracts, pixels or statistics are read."""
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('test_dispatch_impl', HERE / 'dispatch.py')
D = importlib.util.module_from_spec(spec)
spec.loader.exec_module(D)
spec = importlib.util.spec_from_file_location('support', HERE/'test_support.py')
F = importlib.util.module_from_spec(spec); spec.loader.exec_module(F)


def seal_sidecar(path):
    Path(str(path)+'.sha256').write_text(f'{D.sha(path)}  {path.name}\n')


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value) + '\n')
    return path


class Lifecycle(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        self.repo = Path(self.tmp.name) / 'repo'; self.repo.mkdir()
        self.home = self.repo / 'execution'; self.home.mkdir()
        for name in ('dispatch.py', 'guard.py', 'prefit.py', 'admission.py', 'owner_evidence.py'):
            shutil.copyfile(HERE / name, self.home / name)
        self.adapter = self.repo / 'adapter.py'
        self.adapter.write_text('from w50_g1_dispatch import require_context, require_render_admission\n'
            'from pathlib import Path\nimport importlib.util\n'
            'def execute(context):\n require_context(context)\n'
            ' late=Path(context["repo"])/"late.py"\n'
            ' if late.exists():\n'
            '  spec=importlib.util.spec_from_file_location("late",late)\n'
            '  mod=importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)\n'
            ' if (Path(context["repo"])/"mutate.flag").exists():\n'
            '  context["batch"]["runs"][0]["scenes"]=["blind"]; require_context(context)\n'
            ' if (Path(context["repo"])/"crash.flag").exists(): raise RuntimeError("interrupted")\n'
            ' if (Path(context["repo"])/"incomplete.flag").exists(): return {"status":"UNMEASURED"}\n'
            ' records=[]\n'
            ' import json,hashlib\n'
            ' for run in context["batch"]["runs"]:\n'
            '  require_render_admission(context,run,current=context["phase"]=="current")\n'
            '  for scene in run["scenes"]:\n'
            '   artifacts={}\n'
            '   for name in ("cell","report","png"):\n'
            '    p=Path(context["output"])/(str(len(records))+"-"+name)\n'
            '    stamp="f"*12 if (Path(context["repo"])/"false-stamp.flag").exists() else run["candidate"]["sha256"][:12]\n'
            '    actual_scene="other" if (Path(context["repo"])/"false-scene.flag").exists() else scene\n'
            '    p.write_text(json.dumps({"page":{"candidateDocument":{"declarationSha256":stamp},"sceneId":actual_scene,"requestedRenderer":run["renderer"],"devicePixelRatio":2 if "-2x-" in run["profile"] else 1},"capturePath":"declarationSha256="+stamp}))\n'
            '    artifacts[name]={"path":str(p),"sha256":hashlib.sha256(p.read_bytes()).hexdigest()}\n'
            '   records.append(dict(profile=run["profile"],renderer=run["renderer"],scene=scene,candidate=run["candidate"],lane="current" if context["phase"]=="current" else "candidate",artifacts=artifacts))\n'
            ' if (Path(context["repo"])/"omit-capture.flag").exists(): records.pop()\n'
            ' return {"status":"CAPTURED","candidateSha256s":sorted(p["sha256"] for p in context["batch"]["cohort"]),"captures":records}\n'
            'def execute_current(context):\n return execute(context)\n')
        (self.repo / 'judge.py').write_text('from pathlib import Path\n'
            'def evaluate(context, captures):\n'
            ' failed=(Path(context["repo"])/"neither.flag").exists()\n'
            ' reported=(Path(context["repo"])/"reported.flag").exists()\n'
            ' gate=context["phase"]=="gate"\n'
            ' rows=context["expectedCells"] if gate else context["unionExpectedCells"]\n'
            ' if not gate:\n'
            '  assert context["gateCaptures"]["status"]=="CAPTURED" and context["gateCaptures"]["captures"]\n'
            '  assert context["gateReport"]["status"]=="PASS_EXPOSED_OWNER_PENDING"\n'
            ' return {"status":"NEITHER" if failed else "PASS_EXPOSED_OWNER_PENDING" if gate else "PASS",'
            ' "candidateSha256s":sorted(p["sha256"] for p in context["batch"]["cohort"]),'
            ' "pendingOwnerKeys":context["phaseDependencies"]["pendingOwnerKeys"] if gate else [],'
            ' "ownerChecks":"PENDING_FULL_UNION" if gate else "FULL_UNION",'
            ' "gateResult":context["gateResult"],'
            ' "cells":[dict(c,status="REPORTED" if reported else "FAIL" if failed else "PENDING_OWNER_UNION" if gate and c["statistic"]=="owner-contracts" else "PASS") for c in rows]}\n')
        (self.repo/'fit.py').write_text('from w50_g1_dispatch import require_context\n'
            'from pathlib import Path\nimport importlib.util\n'
            'def evaluate(context,captures):\n require_context(context)\n'
            ' late=Path(context["repo"])/"late-fitter.py"\n'
            ' if late.exists():\n'
            '  spec=importlib.util.spec_from_file_location("late_fitter",late)\n'
            '  mod=importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)\n'
            ' return {"status":"PASS" if (Path(context["repo"])/"fit-pass.flag").exists() else "ANALYSED",'
            ' "captureStatus":captures["status"],"phase":context["phase"]}\n')
        self.probe = self.repo / 'probe.py'
        self.probe.write_text('import importlib.util, sys\nfrom pathlib import Path\n'
            'r=Path(__file__).parent\n'
            'def load(name,path):\n s=importlib.util.spec_from_file_location(name,r/path); '
            'm=importlib.util.module_from_spec(s); sys.modules[name]=m; s.loader.exec_module(m); return m\n'
            'load("w50_g1_dispatch","execution/dispatch.py")\n'
            'load("prefit","execution/prefit.py").numerical_shape([1,2,3])\n'
            'load("owner_evidence","execution/owner_evidence.py")\n'
            'load("adapter","adapter.py")\nload("judge","judge.py")\nload("fit","fit.py")\n'
            'load("admission","execution/admission.py")\n'
            'load("runner","packages/calibration/results/2026-10-08-w50-g0-declaration/audit/runner.py")\n')
        fixture=F.build(self.repo,HERE.parents[1]/'2026-10-08-w50-g0-declaration',D.PROOFS)
        for name in ('one','two','refs','manifest','rows','cohort','baselines','numerical'):
            setattr(self,name,fixture[name])
        pixel=fixture['pixel']; self.candidate=self.repo/self.cohort[0]['path']
        for path in (self.one, self.two): seal_sidecar(path)
        current_probe=self.repo/'current-probe.py'
        current_probe.write_text('import importlib.util,sys\nfrom pathlib import Path\nr=Path(__file__).parent\n'
            'def load(name,path):\n s=importlib.util.spec_from_file_location(name,r/path);m=importlib.util.module_from_spec(s);sys.modules[name]=m;s.loader.exec_module(m)\n'
            'load("w50_g1_dispatch","execution/dispatch.py")\nload("admission","execution/admission.py")\nload("adapter","adapter.py")\n')
        current_sources={str(p.relative_to(self.repo)):D.sha(p) for p in
            [self.home/n for n in ('dispatch.py','guard.py','admission.py')]+[self.adapter,current_probe]}
        self.current_batch=self.batch('current',['exposed'])
        self.current_root=D.seal_current_root(self.repo,self.home,self.one,self.two,self.refs,self.manifest,
            self.adapter,current_probe,current_sources,self.baselines,[D.pin(self.repo,self.current_batch)])
        self.root=self.current_root
        current_contract=D.current_contract(self.current_root,self.current_batch)
        captured=self.execute(current_contract,self.current_batch,'-bootstrap')
        self.assertEqual(captured.returncode,0,captured.stderr)
        self.current_results=[D.pin(self.repo,Path(str(current_contract)+'.result.json'))]
        self.sources = {str(p.relative_to(self.repo)): D.sha(p) for p in self.repo.rglob('*.py') if p!=current_probe}
        self.root = D.seal_root(self.repo, self.home, self.one, self.two, self.refs, self.manifest,
            self.adapter, self.repo / 'judge.py', self.probe, self.sources, [],
            baseline_documents=self.baselines,current_instrument=self.current_root,current_results=self.current_results,
            instruments={name:D.pin(self.repo,p) for name,p in
                         [('fit',self.repo/'fit.py'),('measurement',self.repo/'judge.py'),
                          ('bands',self.home/'prefit.py')]})
        completed = copy.deepcopy(json.loads(self.refs.read_text()))
        for row in completed['cells']:
            if row['role'] == 'blind': row['status'] = 'SEALED_BLIND'
            else: row.update(native=1, current=2, B=1, status='MEASURED')
        complete = write(self.repo / 'complete.json', completed)
        proofs = {}
        for kind in D.PROOFS:
            p = write(self.repo / f'proof-{kind}.json', dict(schema='w50-prefit-proof-1', kind=kind,
                status='PASS', checks=[{'id': 'synthetic', 'status': 'PASS'}],
                sources=[D.pin(self.repo, self.probe)], outputs=[D.pin(self.repo, pixel)]))
            proofs[kind] = D.pin(self.repo, p)
        evidence = write(self.home / 'pre-fit-evidence.json', dict(partTwoSha256=D.sha(self.two),
            references=D.pin(self.repo, complete), evidence=proofs,
            sources=[D.pin(self.repo, p) for p in (self.root, Path(str(self.root)+'.sha256'))],
            executionClosure=json.loads(self.root.read_text())['closure']))
        seal_sidecar(evidence)
        self.fit_batch = self.batch('fit', ['exposed'])

    def batch(self, phase, scenes, cohort=None, suffix=''):
        selected=cohort or (self.baselines if phase=='current' else self.cohort)
        expanded=[]
        for scene in scenes:
            expanded.extend(['impulse__rrect-ml__rest','impulse__rrect-ml__inactive'] if scene=='exposed' else [scene])
        runs=[]
        for i,candidate in enumerate(selected):
            position=json.loads((self.repo/candidate['path']).read_text()).get('glassTintAmount',.25)
            for scale in (1,2):
                runs.append(dict(id=f'run{i}-{scale}',profile=f'apple-macos-27.0-{scale}x-dark-standard-glass{position}',
                    renderer='webgpu',scenes=expanded,sets=['holdout'] if phase=='exposure' else ['calibration'],
                    candidate=candidate,numericalReferee=self.numerical))
        return write(self.repo/f'{phase}-batch{suffix}.json',dict(schema='w50-g1-batch-1',phase=phase,
                                                              cohort=selected,runs=runs))

    def execute(self, contract, batch, suffix=''):
        output = Path(self.tmp.name) / ('out-' + contract.stem + suffix)
        # Only the test harness substitutes a private lock; the production CLI fixes /tmp/w49-gpu.lock.
        harness = ('import importlib.util,sys; from pathlib import Path; '
            's=importlib.util.spec_from_file_location("w50_g1_dispatch",sys.argv[1]); '
            'd=importlib.util.module_from_spec(s); sys.modules[s.name]=d; s.loader.exec_module(d); '
            'd.GPU_LOCK=Path(sys.argv[6]); d.execute(*map(Path,sys.argv[2:6]))')
        return subprocess.run([sys.executable,'-I','-B','-c',harness,str(self.home/'dispatch.py'),
            str(self.root),str(contract),str(batch),str(output),str(Path(self.tmp.name)/'gpu.lock')],
            capture_output=True,text=True)

    def gate(self):
        fit = D.fit_contract(self.root, self.fit_batch)
        result = self.execute(fit, self.fit_batch)
        self.assertEqual(result.returncode, 0, result.stderr)
        record = write(self.repo / 'fit-record.json', dict(schema='w50-g1-fit-record-1',
            executionRootSha256=D.sha(self.root), selected=self.cohort,
            completed=[D.pin(self.repo, Path(str(fit)+'.result.json'))]))
        batch = self.batch('gate', ['exposed'])
        return D.gate_contract(self.root, batch, record), batch

    def test_fit_gate_exposure_each_claimed_once(self):
        gate, batch = self.gate()
        with self.assertRaises((ValueError, FileExistsError)):
            D.gate_contract(self.root, batch, self.repo / 'fit-record.json')
        result = self.execute(gate, batch); self.assertEqual(result.returncode, 0, result.stderr)
        self.assertNotEqual(self.execute(gate, batch, '-again').returncode, 0)
        exposure_batch = self.batch('exposure', ['blind', 'history'])
        exposure = D.exposure_contract(self.root, exposure_batch)
        with self.assertRaises((ValueError, FileExistsError)):
            D.exposure_contract(self.root, exposure_batch)
        result = self.execute(exposure, exposure_batch); self.assertEqual(result.returncode, 0, result.stderr)
        self.assertNotEqual(self.execute(exposure, exposure_batch, '-again').returncode, 0)

    def test_exposure_requires_completed_passing_gate_identical_bytes_and_exact_membership(self):
        gate, batch = self.gate()
        exposure = self.batch('exposure', ['blind', 'history'])
        with self.assertRaises(ValueError): D.exposure_contract(self.root, exposure)
        result = self.execute(gate, batch); self.assertEqual(result.returncode, 0, result.stderr)
        for scenes in (['blind'], ['history'], ['blind', 'history', 'exposed']):
            with self.assertRaises(ValueError):
                D.exposure_contract(self.root, self.batch('exposure', scenes))
        other = write(self.repo / 'other.json', {'synthetic': 2})
        with self.assertRaises(ValueError):
            D.exposure_contract(self.root, self.batch('exposure', ['blind', 'history'],
                                                     [D.pin(self.repo, other)]))

    def test_neither_cannot_create_exposure(self):
        gate, batch = self.gate(); (self.repo/'neither.flag').touch()
        result=self.execute(gate,batch); self.assertEqual(result.returncode,0,result.stderr)
        self.assertEqual(D.result_for(gate)['report']['status'],'NEITHER')
        with self.assertRaises(ValueError):
            D.exposure_contract(self.root, self.batch('exposure', ['blind','history']))

    def test_gate_cannot_waive_nonexempt_rows_as_reported(self):
        gate,batch=self.gate(); (self.repo/'reported.flag').touch()
        result=self.execute(gate,batch)
        self.assertNotEqual(result.returncode,0)
        self.assertIn('Overbroad reported-row',result.stderr)

    def test_interrupted_exposure_burns_attempt(self):
        gate,batch=self.gate(); self.assertEqual(self.execute(gate,batch).returncode,0)
        batch=self.batch('exposure',['blind','history']); contract=D.exposure_contract(self.root,batch)
        (self.repo/'crash.flag').touch(); self.assertNotEqual(self.execute(contract,batch).returncode,0)
        (self.repo/'crash.flag').unlink()
        self.assertTrue(Path(str(contract)+'.started.json').exists())
        self.assertNotEqual(self.execute(contract,batch,'-retry').returncode,0)

    def test_live_root_cannot_open_a_legacy_current_lane(self):
        (self.home/'pre-fit-evidence.json').unlink()
        batch=self.batch('current',['exposed'],suffix='-not-registered')
        with self.assertRaisesRegex(ValueError,'cannot be promoted or interchanged'):
            D.current_contract(self.root,batch)

    def test_current_documents_must_be_prospectively_pinned_baselines(self):
        other=write(self.repo/'late-current.json',{'synthetic':2})
        batch=self.batch('current',['exposed'],[D.pin(self.repo,other)])
        with self.assertRaises(ValueError): D.current_contract(self.root,batch)

    def test_changed_batch_and_withheld_or_unknown_cell_refused(self):
        contract = D.fit_contract(self.root, self.fit_batch)
        write(self.fit_batch, {'changed': True})
        self.assertNotEqual(self.execute(contract, self.fit_batch).returncode, 0)
        for scene in ('blind', 'history', 'unknown'):
            with self.assertRaises(ValueError): D.fit_contract(self.root, self.batch('fit', [scene]))
        batch = self.batch('fit', ['exposed']); doc=json.loads(batch.read_text())
        doc['runs'][0]['sets']=['holdout']; write(batch,doc)
        with self.assertRaises(ValueError): D.fit_contract(self.root,batch)

    def test_direct_capability_and_forged_contract_refused(self):
        with self.assertRaises(ValueError): D.require_context({'phase': 'fit'})
        contract = D.fit_contract(self.root, self.fit_batch)
        forged = write(self.home / 'forged.json', json.loads(contract.read_text()))
        seal_sidecar(forged)
        self.assertNotEqual(self.execute(forged,self.fit_batch).returncode,0)

    def test_changed_import_and_new_late_import_refused_before_execution(self):
        contract = D.fit_contract(self.root, self.fit_batch)
        self.adapter.write_text(self.adapter.read_text()+'\nraise RuntimeError("MUST NOT EXECUTE")\n')
        result = self.execute(contract,self.fit_batch)
        self.assertNotEqual(result.returncode,0); self.assertNotIn('RuntimeError: MUST NOT',result.stderr)

    def test_new_late_import_cannot_execute_and_attempt_stays_claimed(self):
        contract = D.fit_contract(self.root, self.fit_batch)
        marker = Path(self.tmp.name) / 'executed'
        (self.repo/'late.py').write_text(f'from pathlib import Path\nPath({str(marker)!r}).touch()\n')
        result = self.execute(contract, self.fit_batch)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('unsealed executed import', result.stderr)
        self.assertFalse(marker.exists())
        self.assertTrue(Path(str(contract)+'.started.json').exists())
        (self.repo/'late.py').unlink()
        self.assertNotEqual(self.execute(contract, self.fit_batch, '-retry').returncode, 0)

    def test_mutated_context_cannot_add_out_of_batch_cell(self):
        contract = D.fit_contract(self.root, self.fit_batch)
        (self.repo/'mutate.flag').touch()
        result = self.execute(contract,self.fit_batch)
        self.assertNotEqual(result.returncode,0)
        self.assertIn('context was mutated',result.stderr)

    def test_interrupted_gate_is_not_retryable_or_exposable(self):
        gate,batch = self.gate(); (self.repo/'crash.flag').touch()
        self.assertNotEqual(self.execute(gate,batch).returncode,0)
        self.assertTrue(Path(str(gate)+'.started.json').exists())
        (self.repo/'crash.flag').unlink()
        self.assertNotEqual(self.execute(gate,batch,'-retry').returncode,0)
        with self.assertRaises(ValueError):
            D.exposure_contract(self.root,self.batch('exposure',['blind','history']))

    def test_seal_refuses_substituted_inventory_and_manifest(self):
        rootdoc=json.loads(self.root.read_text())
        self.root.unlink(); Path(str(self.root)+'.sha256').unlink()
        other_refs=write(self.repo/'other-refs.json',json.loads(self.refs.read_text()))
        other_manifest=write(self.repo/'other-manifest.json',json.loads(self.manifest.read_text()))
        for refs,manifest in [(other_refs,self.manifest),(self.refs,other_manifest)]:
            with self.subTest(refs=refs,manifest=manifest),self.assertRaises(ValueError):
                D.seal_root(self.repo,self.home,self.one,self.two,refs,manifest,
                    self.adapter,self.repo/'judge.py',self.probe,self.sources,[],
                    baseline_documents=self.baselines,instruments=rootdoc['instruments'])

    def test_live_root_omitting_current_results_cannot_execute_candidates(self):
        doc=json.loads(self.root.read_text()); doc.pop('currentResults',None)
        write(self.root,doc); seal_sidecar(self.root)
        with self.assertRaises(ValueError): D.root_doc(self.root)

    def test_current_result_must_also_be_an_explicit_live_root_input(self):
        contract=D.fit_contract(self.root,self.fit_batch)
        doc=json.loads(self.root.read_text()); doc['inputs'].remove(self.current_results[0])
        write(self.root,doc); seal_sidecar(self.root)
        forged=json.loads(contract.read_text()); forged['executionRootSha256']=D.sha(self.root)
        write(contract,forged); seal_sidecar(contract)
        result=self.execute(contract,self.fit_batch)
        self.assertNotEqual(result.returncode,0)
        self.assertIn('omitted current-only instrument/results',result.stderr)
        self.assertFalse(Path(str(contract)+'.started.json').exists())

    def test_changed_current_capture_cannot_support_any_live_candidate(self):
        result=json.loads((self.repo/self.current_results[0]['path']).read_text())
        artifact=Path(result['captureReceipt']['artifacts'][0]['path'])
        artifact.write_bytes(artifact.read_bytes()+b'changed')
        with self.assertRaises(ValueError): D.root_doc(self.root)

    def test_changed_inventory_identity_is_not_authorized_by_a_new_root_pin(self):
        doc=json.loads(self.root.read_text())
        substitute=write(self.repo/'substitute-refs.json',{'cells':[]})
        doc['references']=D.pin(self.repo,substitute); write(self.root,doc); seal_sidecar(self.root)
        with self.assertRaises(ValueError): D.root_doc(self.root)

    def test_changed_manifest_identity_is_not_authorized_by_a_new_root_pin(self):
        doc=json.loads(self.root.read_text())
        substitute=write(self.repo/'substitute-manifest.json',{'cells':[]})
        doc['manifest']=D.pin(self.repo,substitute); write(self.root,doc); seal_sidecar(self.root)
        with self.assertRaises(ValueError): D.root_doc(self.root)

    def test_unused_candidate_cannot_join_selected_cohort(self):
        batch=json.loads(self.fit_batch.read_text())
        other=write(self.repo/'unused.json',{'synthetic':2})
        batch['cohort'].append(D.pin(self.repo,other)); write(self.fit_batch,batch)
        with self.assertRaises(ValueError): D.fit_contract(self.root,self.fit_batch)

    def test_missing_numerical_proof_stops_before_adapter_capability(self):
        batch=json.loads(self.fit_batch.read_text())
        for run in batch['runs']: run.pop('numericalReferee',None)
        write(self.fit_batch,batch)
        contract=D.fit_contract(self.root,self.fit_batch)
        result=self.execute(contract,self.fit_batch)
        self.assertNotEqual(result.returncode,0)
        self.assertFalse(Path(str(contract)+'.result.json').exists())

    def test_live_domain_refuses_held_leaf_gate0_and_malformed_rows(self):
        candidate=self.repo/self.cohort[0]['path']; original=json.loads(candidate.read_text())
        endpoint=candidate.parent/original['endpoints']['active.dark']['path']
        original_endpoint=json.loads(endpoint.read_text())
        for field,value in [('heldLeaf',4),('lowEndStrength',0),('lowEnd44',[.2,.1,.3,.4]),('lowEnd96',[0,1])]:
            changed=copy.deepcopy(original_endpoint); changed['patch'][field]=value; write(endpoint,changed)
            body=copy.deepcopy(original); body['endpoints']['active.dark']['sha256']=D.sha(endpoint); write(candidate,body)
            candidates=[D.pin(self.repo,candidate),self.cohort[1]]
            batch=self.batch('fit',['exposed'],candidates)
            with self.subTest(field=field),self.assertRaises(ValueError): D.fit_contract(self.root,batch)
        write(endpoint,original_endpoint); write(candidate,original)

    def test_other_cohort_numerical_proof_stops_before_capability(self):
        proof=self.repo/self.numerical['path']; value=json.loads(proof.read_text())
        value['candidateSha256s']=[self.cohort[0]['sha256'],'f'*64]; write(proof,value)
        self.numerical=D.pin(self.repo,proof)
        batch=self.batch('fit',['exposed']); contract=D.fit_contract(self.root,batch)
        result=self.execute(contract,batch)
        self.assertNotEqual(result.returncode,0)
        self.assertIn('Numerical admission cohort differs',result.stderr)
        self.assertFalse(Path(str(contract)+'.started.json').exists())

    def test_missing_capture_member_cannot_complete_fit(self):
        contract=D.fit_contract(self.root,self.fit_batch); (self.repo/'omit-capture.flag').touch()
        result=self.execute(contract,self.fit_batch)
        self.assertNotEqual(result.returncode,0)
        self.assertFalse(Path(str(contract)+'.result.json').exists())

    def test_false_candidate_capture_stamp_cannot_complete_fit(self):
        contract=D.fit_contract(self.root,self.fit_batch); (self.repo/'false-stamp.flag').touch()
        result=self.execute(contract,self.fit_batch)
        self.assertNotEqual(result.returncode,0)
        self.assertFalse(Path(str(contract)+'.result.json').exists())

    def test_capture_report_cannot_relabel_another_rendered_scene(self):
        contract=D.fit_contract(self.root,self.fit_batch); (self.repo/'false-scene.flag').touch()
        result=self.execute(contract,self.fit_batch)
        self.assertNotEqual(result.returncode,0)
        self.assertFalse(Path(str(contract)+'.result.json').exists())

    def test_foreign_gpu_lock_is_preserved_before_capability(self):
        lock=Path(self.tmp.name)/'gpu.lock'; lock.write_text('foreign owner')
        contract=D.fit_contract(self.root,self.fit_batch)
        result=self.execute(contract,self.fit_batch)
        self.assertNotEqual(result.returncode,0)
        self.assertEqual(lock.read_text(),'foreign owner')
        self.assertFalse(Path(str(contract)+'.started.json').exists())

    def test_replaced_gpu_lock_is_not_unlinked_by_old_owner(self):
        previous=D.GPU_LOCK; D.GPU_LOCK=Path(self.tmp.name)/'private-lock'
        try:
            with D.owned_gpu_lock():
                self.assertTrue(D.lease_owned())
                D.GPU_LOCK.unlink(); D.GPU_LOCK.write_text('replacement owner')
                self.assertFalse(D.lease_owned())
            self.assertEqual(D.GPU_LOCK.read_text(),'replacement owner')
        finally: D.GPU_LOCK=previous

    def test_fit_analysis_runs_under_same_capability_without_gate_verdict(self):
        contract=D.fit_contract(self.root,self.fit_batch)
        result=self.execute(contract,self.fit_batch); self.assertEqual(result.returncode,0,result.stderr)
        report=D.result_for(contract)['report']
        self.assertEqual(report['status'],'CAPTURED')
        self.assertEqual(report.get('analysis'),
                         {'status':'ANALYSED','captureStatus':'CAPTURED','phase':'fit'})

    def test_fit_analysis_new_late_import_refused_before_module_executes(self):
        contract=D.fit_contract(self.root,self.fit_batch)
        marker=Path(self.tmp.name)/'fitter-executed'
        (self.repo/'late-fitter.py').write_text(f'from pathlib import Path\nPath({str(marker)!r}).touch()\n')
        result=self.execute(contract,self.fit_batch)
        self.assertNotEqual(result.returncode,0)
        self.assertIn('unsealed executed import',result.stderr)
        self.assertFalse(marker.exists())
        self.assertTrue(Path(str(contract)+'.started.json').exists())
        self.assertFalse(Path(str(contract)+'.result.json').exists())

    def test_changed_fitter_source_refused_before_module_executes(self):
        contract=D.fit_contract(self.root,self.fit_batch)
        fitter=self.repo/'fit.py'
        fitter.write_text(fitter.read_text()+'\nraise RuntimeError("MUST NOT EXECUTE")\n')
        result=self.execute(contract,self.fit_batch)
        self.assertNotEqual(result.returncode,0)
        self.assertNotIn('RuntimeError: MUST NOT EXECUTE',result.stderr)
        self.assertFalse(Path(str(contract)+'.started.json').exists())

    def test_fit_analysis_cannot_claim_gate_pass(self):
        contract=D.fit_contract(self.root,self.fit_batch); (self.repo/'fit-pass.flag').touch()
        result=self.execute(contract,self.fit_batch)
        self.assertNotEqual(result.returncode,0)
        self.assertFalse(Path(str(contract)+'.result.json').exists())

    def test_root_cannot_omit_fit_measurement_and_band_entry_sources(self):
        self.root.unlink(); Path(str(self.root)+'.sha256').unlink()
        with self.assertRaises(ValueError):
            D.seal_root(self.repo,self.home,self.one,self.two,self.refs,self.manifest,
                        self.adapter,self.repo/'judge.py',self.probe,self.sources,[],
                        baseline_documents=self.baselines)

    def test_incomplete_adapter_does_not_complete_a_fit(self):
        contract=D.fit_contract(self.root,self.fit_batch); (self.repo/'incomplete.flag').touch()
        result=self.execute(contract,self.fit_batch)
        self.assertNotEqual(result.returncode,0)
        self.assertFalse(Path(str(contract)+'.result.json').exists())

    def mixed_phase_fixture(self):
        refs=copy.deepcopy(self.rows)
        for row in self.rows:
            if row['scene']=='history':
                refs.extend([dict(row,renderer=tier,statistic='owner-contracts',role='gate')
                             for tier in ('webgpu','css')])
            if row['scene']=='impulse__rrect-ml__rest':
                refs.append(dict(row,statistic='owner-contracts',role='gate'))
        path=write(self.repo/'mixed-refs.json',{'cells':refs})
        doc=D.root_doc(self.root); doc['references']=D.pin(self.repo,path)
        doc['phaseDependencies']=D.derive_phase_dependencies(refs)
        gate=self.batch('gate',['exposed'])
        exposure=self.batch('exposure',['blind','history']); batch=json.loads(exposure.read_text())
        batch['runs'] += [dict(run,id=run['id']+'-css',renderer='css',scenes=['history'])
                          for run in list(batch['runs'])]
        write(exposure,batch)
        return doc,refs,gate,exposure

    def test_mixed_dependency_is_not_early_captured_and_no_original_key_is_lost(self):
        doc,refs,gate,exposure=self.mixed_phase_fixture()
        _,gate_rows=D.validate_batch(doc,gate,'gate')
        _,exposure_rows=D.validate_batch(doc,exposure,'exposure')
        keys=lambda rows:{tuple(r[k] for k in D.KEY) for r in rows}
        self.assertFalse(keys(gate_rows)&keys(exposure_rows))
        self.assertEqual(keys(gate_rows)|keys(exposure_rows),keys(refs))
        self.assertEqual(len(doc['phaseDependencies']['pendingOwnerKeys']),8)
        self.assertEqual(len(doc['phaseDependencies']['ownerUnionKeys']),12)
        fit=self.batch('fit',['history']); batch=json.loads(fit.read_text())
        for run in batch['runs']: run['renderer']='css'
        write(fit,batch)
        with self.assertRaises(ValueError): D.validate_batch(doc,fit,'fit')
        bad=copy.deepcopy(doc); del bad['phaseDependencies']
        with self.assertRaises(ValueError): D.validate_batch(bad,exposure,'exposure')
        batch=json.loads(exposure.read_text()); batch['runs']=[r for r in batch['runs'] if r['renderer']=='webgpu']
        write(exposure,batch)
        with self.assertRaises(ValueError): D.validate_batch(doc,exposure,'exposure')

    def test_pending_owner_gate_and_final_union_have_distinct_complete_contracts(self):
        doc,refs,gate,exposure=self.mixed_phase_fixture()
        gate_batch,gate_rows=D.validate_batch(doc,gate,'gate')
        exposure_batch,exposure_rows=D.validate_batch(doc,exposure,'exposure')
        pending=doc['phaseDependencies']['pendingOwnerKeys']
        report={'status':D.GATE_SUCCESS,'ownerChecks':'PENDING_FULL_UNION','pendingOwnerKeys':pending,
                'candidateSha256s':sorted(c['sha256'] for c in self.cohort),
                'cells':[dict(c,status='PENDING_OWNER_UNION' if c['statistic']=='owner-contracts' else 'PASS')
                         for c in gate_rows]}
        D.validate_report(doc,gate_batch,gate_rows,report)
        for wrong in ([],list(reversed(pending))):
            with self.assertRaises(ValueError):
                D.validate_report(doc,gate_batch,gate_rows,{**report,'pendingOwnerKeys':wrong})
        false_partial=copy.deepcopy(report)
        for cell in false_partial['cells']:
            if cell['statistic']=='owner-contracts': cell['status']='PASS'
        with self.assertRaises(ValueError): D.validate_report(doc,gate_batch,gate_rows,false_partial)
        failed=copy.deepcopy(report); failed['cells'][0]['status']='FAIL'
        with self.assertRaises(ValueError): D.validate_report(doc,gate_batch,gate_rows,failed)
        gatepin={'path':'gate.result.json','sha256':'a'*64}
        final={'status':'PASS','ownerChecks':'FULL_UNION','pendingOwnerKeys':[],
               'candidateSha256s':report['candidateSha256s'],'gateResult':gatepin,
               'cells':[dict(c,status='PASS') for c in refs]}
        D.validate_report(doc,exposure_batch,exposure_rows,final,gate_result=gatepin)
        for bad in ({**final,'cells':[dict(c,status='PASS') for c in exposure_rows]},
                    {**final,'gateResult':{'path':'other','sha256':'b'*64}},
                    {**final,'ownerChecks':'PENDING_FULL_UNION'}):
            with self.assertRaises(ValueError):
                D.validate_report(doc,exposure_batch,exposure_rows,bad,gate_result=gatepin)

    def test_exposure_result_binds_frozen_gate_captures_and_complete_union(self):
        gate,batch=self.gate(); result=self.execute(gate,batch)
        self.assertEqual(result.returncode,0,result.stderr)
        gate_data=D.result_for(gate)
        self.assertEqual(gate_data['report']['status'],D.GATE_SUCCESS)
        self.assertTrue(gate_data['captures']['captures'])
        batch=self.batch('exposure',['blind','history']); exposure=D.exposure_contract(self.root,batch)
        result=self.execute(exposure,batch); self.assertEqual(result.returncode,0,result.stderr)
        report=D.result_for(exposure)['report']
        self.assertEqual(report['gateResult'],D.pin(self.repo,Path(str(gate)+'.result.json')))
        self.assertEqual({tuple(r[k] for k in D.KEY) for r in report['cells']},
                         {tuple(r[k] for k in D.KEY) for r in self.rows})

    def test_gate_cannot_claim_an_unqualified_final_pass(self):
        doc=D.root_doc(self.root); batch=self.batch('gate',['exposed'])
        batch,expected=D.validate_batch(doc,batch,'gate')
        report={'status':'PASS','candidateSha256s':sorted(c['sha256'] for c in self.cohort),
                'cells':[dict(c,status='PASS') for c in expected]}
        with self.assertRaises(ValueError): D.validate_report(doc,batch,expected,report)

    def test_gate_and_exposure_empty_rows_require_exact_native_witness(self):
        spec=importlib.util.spec_from_file_location('empty_fixture_tests',HERE/'test_prefit.py')
        helpers=importlib.util.module_from_spec(spec); spec.loader.exec_module(helpers)
        for blind in (False,True):
            fixture=helpers.Completion('runTest'); fixture.setUp(); self.addCleanup(fixture.doCleanups)
            identity=fixture.empty_fixture(blind=blind); row=copy.deepcopy(fixture.done['cells'][0])
            witness=fixture.repo/'empty-witness.json'; value=json.loads(witness.read_text())
            value['nativeRead']['path']=str(fixture.repo/value['nativeRead']['path']); write(witness,value)
            row.update(candidate=None,emptySupportWitness={'path':str(witness),'sha256':D.sha(witness)})
            refs=write(self.repo/'empty-report-refs.json',{'cells':fixture.original['cells']})
            doc=D.root_doc(self.root); doc.update(references=D.pin(self.repo,refs),
                reportedKeys=[identity],emptySupportKeys=[identity])
            batch={'cohort':self.cohort,'phase':'exposure' if blind else 'gate'}
            gatepin={'path':'synthetic-gate-result.json','sha256':'a'*64}
            report={'status':'PASS' if blind else D.GATE_SUCCESS,
                'candidateSha256s':sorted(c['sha256'] for c in self.cohort),'cells':[row],
                'ownerChecks':'FULL_UNION' if blind else 'PENDING_FULL_UNION','pendingOwnerKeys':[],
                'gateResult':gatepin}
            D.validate_report(doc,batch,[{k:row[k] for k in D.KEY}],report,gate_result=gatepin)
            row['candidate']=0
            with self.assertRaises(ValueError): D.validate_report(doc,batch,[row],report,gate_result=gatepin)
            row['candidate']=None; doc['emptySupportKeys']=[]
            with self.assertRaises(ValueError): D.validate_report(doc,batch,[row],report,gate_result=gatepin)

    def test_reported_rows_require_real_readings_even_at_exposure(self):
        row={k:self.rows[0][k] for k in D.KEY}; doc=D.root_doc(self.root)
        doc['reportedKeys']=[[row[k] for k in D.KEY]]
        batch=json.loads(self.fit_batch.read_text()); batch['phase']='gate'
        gatepin=None
        report={'status':D.GATE_SUCCESS,'ownerChecks':'PENDING_FULL_UNION','pendingOwnerKeys':[],'candidateSha256s':sorted(p['sha256'] for p in self.cohort),
                'cells':[dict(row,status='REPORTED',B=None)]}
        with self.assertRaises(ValueError): D.validate_report(doc,batch,[row],report,gate_result=gatepin)
        report['cells'][0].update(native=0,current=0,candidate=0)
        D.validate_report(doc,batch,[row],report,gate_result=gatepin)
        report['cells'][0]['candidate']=float('nan')
        with self.assertRaises(ValueError): D.validate_report(doc,batch,[row],report,gate_result=gatepin)

    def test_gate_entrypoint_rechecks_fit_selection_not_just_wrapper(self):
        record=write(self.repo/'empty-fit.json',dict(schema='w50-g1-fit-record-1',
            executionRootSha256=D.sha(self.root),selected=self.cohort,completed=[]))
        batch=self.batch('gate',['exposed'])
        contract=D.create_contract(self.root,batch,'gate',{'fitRecord':D.pin(self.repo,record)})
        result=self.execute(contract,batch)
        self.assertNotEqual(result.returncode,0)
        self.assertFalse(Path(str(contract)+'.started.json').exists())

    def test_direct_adapter_invocation_lacks_capability(self):
        sys.modules['w50_g1_dispatch']=D
        spec=importlib.util.spec_from_file_location('direct_adapter',self.adapter)
        adapter=importlib.util.module_from_spec(spec); spec.loader.exec_module(adapter)
        with self.assertRaises(ValueError): adapter.execute({'phase':'fit','repo':str(self.repo)})

    def test_unknown_and_empty_composite_readings_are_not_completion(self):
        complete=self.repo/'complete.json'; value=json.loads(complete.read_text())
        value['cells'][0]['native']={}; write(complete,value)
        with self.assertRaises(ValueError): D.fit_contract(self.root,self.fit_batch)

    def test_all_twelve_proofs_and_exercised_closure_required(self):
        evidence=self.home/'pre-fit-evidence.json'; original=json.loads(evidence.read_text())
        for kind in D.PROOFS:
            bad=copy.deepcopy(original); del bad['evidence'][kind]; write(evidence,bad); seal_sidecar(evidence)
            with self.subTest(kind=kind), self.assertRaises(ValueError): D.fit_contract(self.root,self.fit_batch)
        bad=copy.deepcopy(original); bad['executionClosure']['sources']={}; write(evidence,bad); seal_sidecar(evidence)
        with self.assertRaises(ValueError): D.fit_contract(self.root,self.fit_batch)


if __name__ == '__main__':
    unittest.main()
