"""Execute copied dispatcher/router against synthetic 42-GPU + CSS transports."""
import copy
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import unittest

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('replacement_fixture',HERE/'test_replacement.py')
F=importlib.util.module_from_spec(spec);spec.loader.exec_module(F)
spec=importlib.util.spec_from_file_location('replacement_dispatch',HERE/'dispatch.py')
D=importlib.util.module_from_spec(spec);sys.modules[spec.name]=D;spec.loader.exec_module(D)
OLD=HERE.parents[1]/'2026-10-08-w50-g1-fit'
spec=importlib.util.spec_from_file_location('original_synthetic_support',OLD/'execution/test_support.py')
S=importlib.util.module_from_spec(spec);spec.loader.exec_module(S)


class AttemptTwo(unittest.TestCase):
    def setUp(self):
        self.fixture=F.Replacement('runTest');self.fixture.setUp();self.addCleanup(self.fixture.doCleanups)
        f=self.fixture;self.repo=f.repo;self.home=f.directory
        for name in ('dispatch','guard','admission','replacement'):
            shutil.copyfile(HERE/f'{name}.py',self.home/f'{name}.py')
        for name in ('current_router.py','current_probe.py'):
            shutil.copyfile(HERE.parent/name,self.home.parent/name)
        self.data=S.build(self.repo,OLD.parent/'2026-10-08-w50-g0-declaration',D.PROOFS)
        self.candidate=self.data['baselines'][0]
        f.run['candidate']=self.candidate;f.batch['cohort']=[self.candidate];f.batch['runs'][0]['candidate']=self.candidate
        # Keep all old synthetic metadata coherent while supplying real gate0 fixture documents.
        failure=f.failure
        oldcontract_path=self.repo/failure['contract']['path'];oldcontract=json.loads(oldcontract_path.read_text())
        oldbatch=self.repo/oldcontract['batch']['path'];body=json.loads(oldbatch.read_text())
        body['cohort']=[self.candidate];body['runs'][0]['candidate']=self.candidate
        oldbatch.write_text(json.dumps(body)+'\n');oldcontract['batch']=D.pin(self.repo,oldbatch);oldcontract['cohort']=[self.candidate]
        oldroot=self.repo/failure['root']['path'];rootdoc=json.loads(oldroot.read_text())
        rootdoc['currentBatches']=[oldcontract['batch']]
        rootdoc['partOne']=D.pin(self.repo,self.data['one']);rootdoc['partTwo']=D.pin(self.repo,self.data['two'])
        oldroot.write_text(json.dumps(rootdoc)+'\n');f.seal(oldroot);failure['root']=D.pin(self.repo,oldroot)
        oldcontract['executionRootSha256']=D.sha(oldroot);oldcontract_path.write_text(json.dumps(oldcontract)+'\n');f.seal(oldcontract_path)
        failure['contract']=D.pin(self.repo,oldcontract_path)
        claim_path=self.repo/failure['claim']['path'];claim=json.loads(claim_path.read_text())
        claim.update(contractSha256=D.sha(oldcontract_path),batchSha256=D.sha(oldbatch));claim_path.write_text(json.dumps(claim)+'\n')
        failure['claim']=D.pin(self.repo,claim_path)
        f.replacement.update(priorRoot=failure['root'],priorClaim=failure['claim'],
            priorFailure=f.put(str(F.R.PRIOR/'evidence/current-attempt1/failure.json'),failure))
        # Extend only synthetic unsealed G0 identities to the 42 scenes of the replay fixture.
        references=json.loads(self.data['refs'].read_text());template=references['cells'][0]
        references['cells']=[dict(template,scene=scene,renderer=tier) for scene in f.scenes for tier in ('webgpu','css')]
        self.data['refs'].write_text(json.dumps(references)+'\n')
        for part in ('one','two'):
            value=json.loads(self.data[part].read_text())
            value['sources']=[D.pin(self.repo,self.data['refs']) if p['path']==str(self.data['refs'].relative_to(self.repo)) else p for p in value['sources']]
            if part=='two':value['partOneSha256']=D.sha(self.data['one'])
            self.data[part].write_text(json.dumps(value)+'\n');f.seal(self.data[part])
        rootdoc['partOne']=D.pin(self.repo,self.data['one']);rootdoc['partTwo']=D.pin(self.repo,self.data['two'])
        oldroot.write_text(json.dumps(rootdoc)+'\n');f.seal(oldroot);failure['root']=D.pin(self.repo,oldroot)
        oldcontract['executionRootSha256']=D.sha(oldroot);oldcontract_path.write_text(json.dumps(oldcontract)+'\n');f.seal(oldcontract_path)
        failure['contract']=D.pin(self.repo,oldcontract_path);claim['contractSha256']=D.sha(oldcontract_path)
        claim_path.write_text(json.dumps(claim)+'\n');failure['claim']=D.pin(self.repo,claim_path)
        f.replacement.update(priorRoot=failure['root'],priorClaim=failure['claim'],
            priorFailure=f.put(str(F.R.PRIOR/'evidence/current-attempt1/failure.json'),failure))
        host=self.home.parent/'web/host.mjs';host.parent.mkdir();host.write_text('// synthetic identical current/candidate host\n')
        closure=f.put('web-closure.json',{'sources':[D.pin(self.repo,host)]})
        self.batch=copy.deepcopy(f.batch);self.batch['runs'][0]['webSourceClosure']=closure
        self.batch['runs'] += [dict(self.batch['runs'][0],id='css-after-replay',renderer='css',scenes=[f.scenes[0]])]
        self.batch_path=self.repo/'replacement-batch.json';self.batch_path.write_text(json.dumps(self.batch)+'\n')
        self.second=copy.deepcopy(self.batch);self.second['runs']=[dict(self.batch['runs'][1],id='canonical-css',sceneSource='canonical')]
        self.second_path=self.repo/'canonical-batch.json';self.second_path.write_text(json.dumps(self.second)+'\n')
        adapter='''from pathlib import Path
import hashlib,json

def source_probe():return {'status':'SOURCE_ONLY'}
def _capture_run(context,run,current=False):
    from w50_g1_dispatch import require_render_admission
    require_render_admission(context,run,current=current)
    records=[]
    for i,scene in enumerate(run['scenes']):
        if run['renderer']=='css':
            if (Path(context['repo'])/'css-crash.flag').exists(): raise ValueError('synthetic CSS failure')
            if not (Path(context['output'])/'gpu-replay-proof.json').exists() and run['sceneSource']=='w50':
                raise ValueError('CSS ran without output replay proof')
            (Path(context['output'])/'css-ran').touch()
        folder=Path(context['output'])/run['id']/scene;folder.mkdir(parents=True)
        raw=f'synthetic-png-{i}'.encode() if run['renderer']=='webgpu' else b'synthetic-css'
        if (Path(context['repo'])/'mismatch.flag').exists() and i==0 and run['renderer']=='webgpu':raw=b'mismatch'
        png=folder/'capture.png';png.write_bytes(raw)
        metadata={'renderer':run['renderer'],'sceneId':scene,'capturePath':'declarationSha256='+run['candidate']['sha256'][:12]}
        report={'page':{'sceneId':scene,'requestedRenderer':run['renderer'],'devicePixelRatio':1,
                       'candidateDocument':{'declarationSha256':run['candidate']['sha256'][:12]}}}
        meta=folder/'cell.json';meta.write_text(json.dumps(metadata))
        page=folder/'report.json';page.write_text(json.dumps(report))
        pins={name:{'path':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
              for name,p in [('png',png),('cell',meta),('report',page)]}
        records.append(dict(profile=run['profile'],renderer=run['renderer'],scene=scene,candidate=run['candidate'],lane='current',artifacts=pins))
    return records
capture_run=_capture_run
'''
        (host.parent/'adapter.py').write_text(adapter)
        canonical=self.repo/F.R.PRIOR/'canonical/adapter.py';canonical.parent.mkdir(parents=True);canonical.write_text(adapter)
        sources=[self.home/n for n in ('dispatch.py','guard.py','admission.py','replacement.py')]
        sources += [self.home.parent/'current_router.py',self.home.parent/'current_probe.py',host.parent/'adapter.py',canonical]
        self.sources={str(p.relative_to(self.repo)):D.sha(p) for p in sources}
        self.root=D.seal_current_root(self.repo,self.home,self.data['one'],self.data['two'],self.data['refs'],self.data['manifest'],
            self.home.parent/'current_router.py',self.home.parent/'current_probe.py',self.sources,[self.candidate],
            [D.pin(self.repo,self.batch_path),D.pin(self.repo,self.second_path)],inputs=[closure],replacement_attempt=f.replacement)

    def execute(self,contract,batch,folder):
        script=('import sys,importlib.util;from pathlib import Path;'
          's=importlib.util.spec_from_file_location("w50_g1_dispatch",sys.argv[1]);'
          'd=importlib.util.module_from_spec(s);sys.modules[s.name]=d;s.loader.exec_module(d);'
          'd.GPU_LOCK=Path(sys.argv[6]);d.execute(*map(Path,sys.argv[2:6]))')
        return subprocess.run([sys.executable,'-I','-B','-c',script,str(self.home/'dispatch.py'),str(self.root),str(contract),
            str(batch),str(self.fixture.output.parent/folder),str(self.fixture.output.parent/'gpu.lock')],text=True,capture_output=True)

    def test_replay_proof_precedes_css_and_binds_completed_attempt(self):
        contract=D.current_contract(self.root,self.batch_path)
        result=self.execute(contract,self.batch_path,'success')
        self.assertEqual(result.returncode,0,result.stderr)
        output=self.fixture.output.parent/'success'
        self.assertTrue((output/'css-ran').exists())
        self.assertEqual((output/'gpu-replay-proof.json').read_bytes(),(self.home/'gpu-replay-proof.json').read_bytes())
        proof=D.read_current_replay(self.root,D.root_doc(self.root),require_complete=True)
        self.assertEqual(len(proof['cells']),42)
        later=D.current_contract(self.root,self.second_path)
        result=self.execute(later,self.second_path,'canonical')
        self.assertEqual(result.returncode,0,result.stderr)
        self.assertTrue((self.fixture.output.parent/'canonical/css-ran').exists())

    def test_mismatch_burns_attempt_before_css_and_refuses_retry(self):
        (self.repo/'mismatch.flag').touch();contract=D.current_contract(self.root,self.batch_path)
        result=self.execute(contract,self.batch_path,'mismatch')
        self.assertNotEqual(result.returncode,0)
        self.assertTrue(Path(str(contract)+'.started.json').exists())
        self.assertFalse((self.fixture.output.parent/'mismatch/css-ran').exists())
        self.assertFalse((self.home/'gpu-replay-proof.json').exists())
        (self.repo/'mismatch.flag').unlink()
        self.assertNotEqual(self.execute(contract,self.batch_path,'retry').returncode,0)

    def test_standalone_canonical_cannot_run_before_gpu_proof(self):
        contract=D.current_contract(self.root,self.second_path)
        result=self.execute(contract,self.second_path,'too-early')
        self.assertNotEqual(result.returncode,0)
        self.assertFalse(Path(str(contract)+'.started.json').exists())
        self.assertFalse((self.fixture.output.parent/'too-early').exists())

    def test_completed_gpu_proof_does_not_unburn_failed_css_batch(self):
        (self.repo/'css-crash.flag').touch()
        first=D.current_contract(self.root,self.batch_path)
        result=self.execute(first,self.batch_path,'css-failed')
        self.assertNotEqual(result.returncode,0)
        self.assertTrue((self.home/'gpu-replay-proof.json').exists())
        self.assertFalse(Path(str(first)+'.result.json').exists())
        later=D.current_contract(self.root,self.second_path)
        self.assertNotEqual(self.execute(later,self.second_path,'no-continuation').returncode,0)
        self.assertFalse(Path(str(later)+'.started.json').exists())
        (self.repo/'css-crash.flag').unlink()
        self.assertNotEqual(self.execute(first,self.batch_path,'no-retry').returncode,0)

    def test_tampered_proof_or_gpu_bytes_block_later_css(self):
        first=D.current_contract(self.root,self.batch_path)
        result=self.execute(first,self.batch_path,'success')
        self.assertEqual(result.returncode,0,result.stderr)
        proof=json.loads((self.home/'gpu-replay-proof.json').read_text())
        Path(proof['cells'][0]['replacementPng']['path']).write_bytes(b'changed after proof')
        later=D.current_contract(self.root,self.second_path)
        self.assertNotEqual(self.execute(later,self.second_path,'changed').returncode,0)
        self.assertFalse(Path(str(later)+'.started.json').exists())

    def test_live_evidence_chain_includes_exact_replay_proof_pins(self):
        first=D.current_contract(self.root,self.batch_path)
        self.assertEqual(self.execute(first,self.batch_path,'first').returncode,0)
        second=D.current_contract(self.root,self.second_path)
        self.assertEqual(self.execute(second,self.second_path,'second').returncode,0)
        results=[D.pin(self.repo,Path(str(c)+'.result.json')) for c in (first,second)]
        pins=D.current_evidence_inputs(self.repo,self.home,D.pin(self.repo,self.root),results)
        self.assertIn(D.pin(self.repo,self.home/'gpu-replay-proof.json'),pins)
        self.assertIn(D.pin(self.repo,self.home/'gpu-replay-proof.json.sha256'),pins)

    def test_root_cannot_drop_newbed_host_from_capture_source_closure(self):
        closure_path=self.repo/self.batch['runs'][0]['webSourceClosure']['path']
        closure_path.write_text(json.dumps({'sources':[]})+'\n')
        new_pin=D.pin(self.repo,closure_path)
        batch=copy.deepcopy(self.batch)
        for run in batch['runs']:run['webSourceClosure']=new_pin
        path=self.repo/'bad-host-batch.json';path.write_text(json.dumps(batch)+'\n')
        doc=json.loads(self.root.read_text())
        doc['currentBatches']=[D.pin(self.repo,path)];doc['inputs'].append(new_pin)
        with self.assertRaises(ValueError):D.validate_batch(doc,path,'current')

    def test_changed_prior_manifest_or_omitted_replacement_authority_refuses_root(self):
        root=json.loads(self.root.read_text());root.pop('replacementAttempt')
        self.root.write_text(json.dumps(root)+'\n');self.fixture.seal(self.root)
        with self.assertRaises(ValueError):D.root_doc(self.root)


if __name__=='__main__':unittest.main()
