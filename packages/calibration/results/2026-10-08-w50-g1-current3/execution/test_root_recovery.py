"""Seal/entrypoint tests on synthetic roots; no actual current/candidate transport runs."""
import copy
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import unittest

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('partition_fixture',HERE/'test_recovery.py')
F=importlib.util.module_from_spec(spec);spec.loader.exec_module(F)
spec=importlib.util.spec_from_file_location('current3_dispatch',HERE/'dispatch.py')
D=importlib.util.module_from_spec(spec);spec.loader.exec_module(D)
BASE=HERE.parents[1]
spec=importlib.util.spec_from_file_location('current3_material_fixture',BASE/'2026-10-08-w50-g1-fit/execution/test_support.py')
S=importlib.util.module_from_spec(spec);spec.loader.exec_module(S)


class RecoveryRoot(unittest.TestCase):
    def setUp(self):
        self.f=F.RecoveryPartition('runTest');self.f.setUp();self.addCleanup(self.f.doCleanups)
        f=self.f;self.repo=f.repo.resolve();self.home=f.directory.resolve()
        fixture=S.build(self.repo,BASE/'2026-10-08-w50-g0-declaration',D.PROOFS)
        candidate=fixture['baselines'][0]
        host=self.home.parent/'web/host.mjs';host.parent.mkdir();host.write_text('// unchanged host')
        oldhost=self.repo/F.R.PRIOR/'web/host.mjs';oldhost.parent.mkdir(parents=True,exist_ok=True);oldhost.write_bytes(host.read_bytes())
        closure=f.put('fresh-sources.json',{'sources':[D.pin(self.repo,host)]})
        oldroot_path=self.repo/f.oldroot['path'];oldroot=json.loads(oldroot_path.read_text())
        old_batches=[]
        for old,new in zip(oldroot['currentBatches'],f.batches):
            p=self.repo/old['path'];doc=json.loads(p.read_text());doc['cohort']=[candidate];new['cohort']=[candidate]
            for r,n in zip(doc['runs'],new['runs']):r['candidate']=candidate;n['candidate']=candidate;n['webSourceClosure']=closure
            p.write_text(json.dumps(doc)+'\n');old_batches.append(D.pin(self.repo,p))
        oldroot['currentBatches']=old_batches;oldroot['newBedHost']=D.pin(self.repo,oldhost)
        oldroot_path.write_text(json.dumps(oldroot)+'\n');f.seal(oldroot_path);f.oldroot=D.pin(self.repo,oldroot_path)
        contract=f.put(str(F.R.PRIOR/'execution/current-instrument'/f'{old_batches[0]["sha256"]}.json'),
            {'phase':'current','batch':old_batches[0],'cohort':[candidate],'executionRootSha256':f.oldroot['sha256']})
        f.seal(self.repo/contract['path'])
        claim=f.put(contract['path']+'.started.json',{'phase':'current','contractSha256':contract['sha256'],
            'batchSha256':old_batches[0]['sha256'],'output':str(f.tree)})
        proof=json.loads((self.repo/f.proof['path']).read_text())
        proof.update(executionRootSha256=f.oldroot['sha256'],contractSha256=contract['sha256'],claimSha256=claim['sha256'])
        f.proof=f.put(f.proof['path'],proof);f.seal(self.repo/f.proof['path'])
        f.failure.update(root=f.oldroot,contract=contract,claim=claim)
        failure=f.put(str(F.R.PRIOR/'evidence/current-attempt2/failure.json'),f.failure)
        f.authority.update(priorRoot=f.oldroot,priorClaim=claim,priorFailure=failure,gpuReplayProof=f.proof)
        refs=json.loads(fixture['refs'].read_text());template=refs['cells'][0]
        refs['cells']=[{**template,**{k:m[k] for k in ('profile','renderer','scene')}} for m in F.R.flatten(f.batches)]
        fixture['refs'].write_text(json.dumps(refs)+'\n')
        for part in ('one','two'):
            doc=json.loads(fixture[part].read_text())
            doc['sources']=[D.pin(self.repo,fixture['refs']) if p['path']==str(fixture['refs'].relative_to(self.repo)) else p for p in doc['sources']]
            if part=='two':doc['partOneSha256']=D.sha(fixture['one'])
            fixture[part].write_text(json.dumps(doc)+'\n');f.seal(fixture[part])
        self.fixture=fixture;self.batch_paths=[]
        for i,batch in enumerate(f.batches):
            p=self.repo/f'new-batch-{i}.json';p.write_text(json.dumps(batch)+'\n');self.batch_paths.append(p)
        for name in ('dispatch.py','guard.py','admission.py','recovery.py','retained.py'):shutil.copyfile(HERE/name,self.home/name)
        for name in ('current_router.py','current_probe.py'):shutil.copyfile(HERE.parent/name,self.home.parent/name)
        adapter='''def source_probe():return {'status':'SOURCE_ONLY'}
def _capture_run(*args,**kwargs):raise RuntimeError('MUST NOT CAPTURE')
capture_run=_capture_run
'''
        paths=[]
        for p in (self.home.parent/'web/adapter.py',self.home.parent/'canonical/adapter.py'):
            p.parent.mkdir(parents=True,exist_ok=True);p.write_text(adapter);paths.append(p)
        paths.append(self.repo/F.R.PRIOR/'web/adapter.py')
        repeat=self.home.parent/'repeat/admission.py';repeat.parent.mkdir();repeat.write_text(
            "def source_probe():return {'status':'SOURCE_ONLY'}\ndef verify_receipt(*args):raise ValueError('no fake repeat proof')\n")
        paths.append(repeat)
        config=f.put('repeat-config.json',{'schema':'w50-repeat-config-1','references':D.pin(self.repo,fixture['refs'])})
        self.registration={'entrypoint':D.pin(self.repo,repeat),'config':config}
        paths += [self.home/n for n in ('dispatch.py','guard.py','admission.py','recovery.py','retained.py')]
        paths += [self.home.parent/'current_router.py',self.home.parent/'current_probe.py']
        self.sources={str(p.relative_to(self.repo)):D.sha(p) for p in paths}
        self.inputs=[closure];self.candidate=candidate
        self.root=self.seal()

    def seal(self):
        f=self.fixture
        return D.seal_current_root(self.repo,self.home,f['one'],f['two'],f['refs'],f['manifest'],
            self.home.parent/'current_router.py',self.home.parent/'current_probe.py',self.sources,[self.candidate],
            [D.pin(self.repo,p) for p in self.batch_paths],inputs=self.inputs,
            recovery_attempt=self.f.authority,repeat_admission=self.registration)

    def test_root_binds_partition_repeat_policy_and_original_gpu_proof(self):
        root=D.root_doc(self.root)
        self.assertEqual(len(root['recovery']['retained']),501)
        self.assertEqual(len(root['recovery']['fresh']),298)
        self.assertEqual(root['repeatAdmission'],self.registration)
        self.assertIn(self.f.proof,root['inputs'])
        self.assertNotIn('replacementAttempt',root)

    def test_dropping_policy_or_recovery_cannot_self_promote_root(self):
        original=json.loads(self.root.read_text())
        for field in ('repeatAdmission','recoveryAttempt','recovery'):
            changed=copy.deepcopy(original);changed.pop(field)
            self.root.write_text(json.dumps(changed)+'\n');self.f.seal(self.root)
            with self.subTest(field=field),self.assertRaises(ValueError):D.root_doc(self.root)
        self.root.write_text(json.dumps(original)+'\n');self.f.seal(self.root)

    def test_later_canonical_batch_cannot_start_before_newbed_completion(self):
        contract=D.current_contract(self.root,self.batch_paths[1]);output=self.f.tree.parent/'too-early-canonical'
        script=('import sys,importlib.util;from pathlib import Path;'
            's=importlib.util.spec_from_file_location("w50_g1_dispatch",sys.argv[1]);d=importlib.util.module_from_spec(s);'
            'sys.modules[s.name]=d;s.loader.exec_module(d);d.GPU_LOCK=Path(sys.argv[6]);d.execute(*map(Path,sys.argv[2:6]))')
        args=[sys.executable,'-I','-B','-c',script,str(self.home/'dispatch.py'),str(self.root),str(contract),
              str(self.batch_paths[1]),str(output),str(self.f.tree.parent/'test-gpu.lock')]
        result=subprocess.run(args,capture_output=True,text=True)
        self.assertNotEqual(result.returncode,0)
        self.assertNotIn('RuntimeError: MUST NOT CAPTURE',result.stderr)
        self.assertFalse(Path(str(contract)+'.started.json').exists())
        self.assertFalse(output.exists())

    def test_failed_source_readmission_burns_claim_before_any_fresh_draw(self):
        contract=D.current_contract(self.root,self.batch_paths[0]);output=self.f.tree.parent/'recovery-output'
        script=('import sys,importlib.util;from pathlib import Path;'
            's=importlib.util.spec_from_file_location("w50_g1_dispatch",sys.argv[1]);d=importlib.util.module_from_spec(s);'
            'sys.modules[s.name]=d;s.loader.exec_module(d);d.GPU_LOCK=Path(sys.argv[6]);d.execute(*map(Path,sys.argv[2:6]))')
        args=[sys.executable,'-I','-B','-c',script,str(self.home/'dispatch.py'),str(self.root),str(contract),
              str(self.batch_paths[0]),str(output),str(self.f.tree.parent/'test-gpu.lock')]
        result=subprocess.run(args,capture_output=True,text=True)
        self.assertNotEqual(result.returncode,0)
        self.assertNotIn('RuntimeError: MUST NOT CAPTURE',result.stderr)
        self.assertTrue(Path(str(contract)+'.started.json').exists())
        self.assertFalse(Path(str(contract)+'.result.json').exists())
        args[-2]=str(self.f.tree.parent/'retry')
        retry=subprocess.run(args,capture_output=True,text=True)
        self.assertNotEqual(retry.returncode,0)
        self.assertIn('FileExistsError',retry.stderr)


if __name__=='__main__':unittest.main()
