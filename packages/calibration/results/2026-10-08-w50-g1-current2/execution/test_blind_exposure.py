"""Exposure boundary tests with synthetic PNGs and one test-only capability issuer."""
import copy
import importlib.util
import json
from pathlib import Path
import sys
import types
import unittest
from unittest.mock import patch

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('native_fixture',HERE/'test_native_evidence.py')
F=importlib.util.module_from_spec(spec);spec.loader.exec_module(F)
spec=importlib.util.spec_from_file_location('blind_exposure',HERE/'blind_exposure.py')
E=importlib.util.module_from_spec(spec);spec.loader.exec_module(E)


class ExposureEvidence(unittest.TestCase):
    def setUp(self):
        f=F.NativeEnvelope('runTest');f.setUp();self.addCleanup(f.doCleanups)
        self.f=f;self.repo=f.repo;self.output=self.repo/'scratch';self.output.mkdir()
        self.candidate=f.put('candidate.json',{'synthetic':'same live cohort'})
        self.baseline=f.put('baseline.json',{'synthetic':'registered baseline'})
        self.original={k:v for k,v in f.row.items() if k!='native'}
        self.original.update(role='blind',nativeEvidence=None,currentEvidence=None,currentMetadata=None,
                             currentDocumentPair={'active.dark':'a'*64,'receded.dark':'b'*64},B=None,status='UNMEASURED')
        self.references={'cells':[self.original]}
        self.reference_pin=f.put('references.json',self.references)
        self.manifest=f.put('manifest.json',{'references':[{'id':f.row['referenceIdentity'],'roles':['blind']}]})
        root=f.put('root.json',{'references':self.reference_pin,'manifest':self.manifest,
            'baselineDocuments':[self.baseline]})
        run=dict(profile=f.row['profile'],renderer='webgpu',scenes=[f.row['scene']],candidate=self.candidate,
                 baselineCandidate=self.baseline,captureRoot=str(self.output/'candidate'),matrixPath=str(self.output/'matrix.json'))
        self.batch=f.put('exposure-batch.json',{'phase':'exposure','cohort':[self.candidate],'runs':[run]})
        contract=f.put('contract.json',{'phase':'exposure'})
        claim=f.put('contract.json.started.json',{'phase':'exposure'})
        self.context=dict(repo=str(self.repo),phase='exposure',executionRoot=root['path'],
            contract=contract['path'],batchPath=self.batch['path'],output=str(self.output),
            batch=json.loads(Path(self.batch['path']).read_text()),baselineDocuments=[self.baseline],inputs=[])
        config=f.put('blind-config.json',{'schema':'w50-native-exposure-inputs-1','partOne':f.declaration,'manifest':self.manifest})
        self.context['inputs']=[config]
        native_claim=f.put('native-claim.json',{'schema':'w50-native-blind-claim-1','role':'blind',
            'dispatcherContract':contract,'dispatcherClaim':claim,'batch':self.batch,'config':config})
        for r in f.index['files']:r['roles']=['blind']
        f.index_pin=f.put('export/index.json',f.index)
        config=f.put('blind-config.json',{'schema':'w50-native-exposure-inputs-1','partOne':f.declaration,
            'manifest':self.manifest,'archiveRoot':str(f.export),'archiveIndexSha256':f.index_pin['sha256']})
        self.context['inputs']=[config]
        native_claim=f.put('native-claim.json',{'schema':'w50-native-blind-claim-1','role':'blind',
            'dispatcherContract':contract,'dispatcherClaim':claim,'batch':self.batch,'config':config})
        f.report.update(role='blind',indexSha256=f.index_pin['sha256'])
        cell=f.report['cells'][0];cell['role']='blind'
        for r in cell['runs']:r['evidence']['roles']=['blind']
        f.report['dependencies'][0]['evidence']['roles']=['blind']
        native_read=f.put_gz('native-read.json.gz',f.report)
        export={'role':'blind','root':str(f.export),'indexSha256':f.index_pin['sha256']}
        artifact=f.put('blind-artifacts.json',{'schema':'w50-native-exposure-artifacts-1','role':'blind','ready':True,
            'nativeRead':native_read,'claim':native_claim,'export':{'path':str(f.export),'indexSha256':f.index_pin['sha256']}})
        envelope={k:self.original[k] for k in ('profile','scene','nativeIdentity','referenceIdentity','role','support','statistic')}
        envelope.update(schema='w50-native-three-run-evidence-1',runs=[r['evidence'] for r in cell['runs']],
            nativeRead=native_read,nativeExposure=artifact,nativeExport=export)
        native=f.put('blind-envelope.json',envelope)
        self.rows=[{**self.original,'nativeEvidence':native,'native':[1,2,3],
            'currentCapture':self.capture('current',self.baseline),
            'candidateCapture':self.capture('candidate',self.candidate)}]
        def require(context):
            if context is not self.context:raise ValueError('No test runtime capability')
        def read(path):return json.loads(Path(path).read_text())
        def admitted(context,run,current=False):
            require(context)
            want=self.context['batch']['runs'][0]
            if current:
                want={**want,'candidate':self.baseline,'captureRoot':str(Path(want['captureRoot'])/'baseline'),
                      'matrixPath':str(Path(want['matrixPath']).with_name('matrix-baseline.json'))}
            if run!=want:raise ValueError('Foreign run')
        self.dispatcher=types.SimpleNamespace(require_context=require,require_render_admission=admitted,sealed=read,
            baseline_run=lambda r:{**r,'candidate':r['baselineCandidate'],'captureRoot':str(Path(r['captureRoot'])/'baseline'),
                                  'matrixPath':str(Path(r['matrixPath']).with_name('matrix-baseline.json'))})

    def capture(self,lane,candidate):
        f=self.f;folder=self.output/lane;folder.mkdir()
        image=folder/'capture.png';image.write_bytes(F.png())
        metadata={'sceneId':f.row['scene'],'renderer':'webgpu','pixelSize':[512,384],
            'capturePath':'candidateDocument='+candidate['path']+' declarationSha256='+candidate['sha256'][:12]}
        report={'page':{'sceneId':f.row['scene'],'requestedRenderer':'webgpu','devicePixelRatio':1,
            'materialMode':'candidate','candidateDocument':{'mode':'candidate','declarationSha256':candidate['sha256'][:12]}}}
        cell=f.put(str(folder/'cell.json'),metadata);page=f.put(str(folder/'report.json'),report)
        return {'profile':f.row['profile'],'renderer':'webgpu','scene':f.row['scene'],'lane':lane,'candidate':candidate,
                'artifacts':{'png':{'path':str(image),'sha256':F.N.sha(image)},'cell':cell,'report':page}}

    def validate(self,rows=None,context=None):
        with patch.dict(sys.modules,{'w50_g1_dispatch':self.dispatcher}):
            return E.validate_blind_exposure(self.context if context is None else context,self.rows if rows is None else rows)

    def test_exact_native_current_candidate_blind_evidence_passes_only_in_exposure(self):
        result=self.validate();self.assertEqual(result['status'],'BOUND_BLIND_EVIDENCE')
        self.assertEqual(result['cells'],1)
        with self.assertRaises(ValueError):self.validate(context=dict(self.context))
        self.context['phase']='fit'
        with self.assertRaises(ValueError):self.validate()

    def test_real_dispatcher_capability_lease_and_material_binding_guard_actual_evidence(self):
        # Start at the post-admission boundary using the ACTUAL dispatcher capability and
        # lease implementations. All documents, claims and image bytes remain synthetic;
        # no compare/capture process is invoked and no real instrument root is modified.
        import shutil
        spec=importlib.util.spec_from_file_location('exposure_test_real_dispatch',HERE/'dispatch.py')
        dispatcher=importlib.util.module_from_spec(spec);spec.loader.exec_module(dispatcher)
        old=HERE.parents[1]/'2026-10-08-w50-g1-fit'
        spec=importlib.util.spec_from_file_location('exposure_test_candidate_fixture',old/'execution/test_support.py')
        support=importlib.util.module_from_spec(spec);spec.loader.exec_module(support)
        fixture=support.build(self.repo,old.parent/'2026-10-08-w50-g0-declaration',dispatcher.PROOFS)
        self.candidate=fixture['cohort'][0];self.baseline=fixture['baselines'][0]
        run=self.context['batch']['runs'][0]
        run.update(candidate=self.candidate,baselineCandidate=self.baseline)
        self.context['batch']['cohort']=fixture['cohort'];self.context['baselineDocuments']=fixture['baselines']
        batch_path=Path(self.context['batchPath']);batch_path.write_text(json.dumps(self.context['batch']))
        self.batch={'path':str(batch_path),'sha256':F.N.sha(batch_path)}
        native_pin=self.rows[0]['nativeEvidence'];envelope=json.loads(Path(native_pin['path']).read_text())
        artifact=json.loads(Path(envelope['nativeExposure']['path']).read_text())
        claim=json.loads(Path(artifact['claim']['path']).read_text());claim['batch']=self.batch
        artifact['claim']=self.f.put('native-claim.json',claim)
        envelope['nativeExposure']=self.f.put('blind-artifacts.json',artifact)
        self.rows[0]['nativeEvidence']=self.f.put('blind-envelope.json',envelope)
        for name,pin in [('currentCapture',self.baseline),('candidateCapture',self.candidate)]:
            capture=self.rows[0][name];capture['candidate']=pin
            for kind in ('cell','report'):
                path=Path(capture['artifacts'][kind]['path']);doc=json.loads(path.read_text())
                if kind=='cell':doc['capturePath']='declarationSha256='+pin['sha256'][:12]
                else:doc['page']['candidateDocument']['declarationSha256']=pin['sha256'][:12]
                capture['artifacts'][kind]=self.f.put(str(path),doc)
        boot=self.repo/'bootstrap';boot.mkdir()
        for name in ('dispatch.py','admission.py'):shutil.copyfile(HERE/name,boot/name)
        root={'repo':str(self.repo.resolve()),'references':self.reference_pin,'manifest':self.manifest,
              'baselineDocuments':fixture['baselines'],'bootstrap':dispatcher.pin(self.repo,boot/'dispatch.py'),
              'partTwo':dispatcher.pin(self.repo,fixture['two'])}
        root_path=Path(self.context['executionRoot']);root_path.write_text(json.dumps(root))
        Path(str(root_path)+'.sha256').write_text(f'{F.N.sha(root_path)}  {root_path.name}\n')
        dispatcher.GPU_LOCK=self.repo/'private-test-gpu.lock'
        with patch.dict(sys.modules,{'w50_g1_dispatch':dispatcher}),dispatcher.owned_gpu_lock():
            dispatcher._ACTIVE=(self.context,copy.deepcopy(self.context),F.N.sha(self.context['contract']),
                F.N.sha(self.context['batchPath']),True,root,fixture['numerical'])
            try:
                self.assertEqual(E.validate_blind_exposure(self.context,self.rows)['cells'],1)
                missing=copy.deepcopy(self.rows);missing[0]['candidateCapture']['artifacts']['png'].pop('sha256')
                with self.assertRaisesRegex(ValueError,'content pin'):
                    E.validate_blind_exposure(self.context,missing)
                pin=self.rows[0]['candidateCapture']['artifacts']['report'];doc=json.loads(Path(pin['path']).read_text())
                doc['page']['candidateDocument']['declarationSha256']=self.baseline['sha256'][:12]
                self.rows[0]['candidateCapture']['artifacts']['report']=self.f.put(pin['path'],doc)
                with self.assertRaisesRegex(ValueError,'same actual draw'):
                    E.validate_blind_exposure(self.context,self.rows)
            finally:dispatcher._ACTIVE=None
        self.assertFalse(dispatcher.GPU_LOCK.exists())

    def test_missing_row_or_any_missing_native_current_candidate_pin_blocks(self):
        with self.assertRaises(ValueError):self.validate(rows=[])
        for name in ('nativeEvidence','currentCapture','candidateCapture'):
            rows=copy.deepcopy(self.rows);rows[0].pop(name)
            with self.subTest(name=name),self.assertRaises(ValueError):self.validate(rows)
        rows=copy.deepcopy(self.rows);rows[0]['candidateCapture']['artifacts']['png'].pop('sha256')
        with self.assertRaises(ValueError):self.validate(rows)

    def test_other_candidate_or_other_scene_cannot_supply_blind_pixels(self):
        for field,value in [('candidate',self.baseline),('scene','other')]:
            rows=copy.deepcopy(self.rows);rows[0]['candidateCapture'][field]=value
            with self.subTest(field=field),self.assertRaises(ValueError):self.validate(rows)

    def test_document_cannot_stand_in_for_png_even_when_it_is_content_pinned(self):
        rows=copy.deepcopy(self.rows);rows[0]['currentCapture']['artifacts']['png']=self.baseline
        with self.assertRaises(ValueError):self.validate(rows)

    def test_wrong_capture_stamp_and_wrong_native_pixel_hash_block_exposure(self):
        pin=self.rows[0]['candidateCapture']['artifacts']['report']
        report=json.loads(Path(pin['path']).read_text())
        report['page']['candidateDocument']['declarationSha256']=self.baseline['sha256'][:12]
        self.rows[0]['candidateCapture']['artifacts']['report']=self.f.put(pin['path'],report)
        with self.assertRaises(ValueError):self.validate()
        report['page']['candidateDocument']['declarationSha256']=self.candidate['sha256'][:12]
        self.rows[0]['candidateCapture']['artifacts']['report']=self.f.put(pin['path'],report)
        frame=self.f.export/self.f.index['files'][0]['path'];frame.write_bytes(b'changed native')
        with self.assertRaises(ValueError):self.validate()

    def test_blind_repeated_nested_run_refuses_even_with_repinned_exposure_chain(self):
        self.assertEqual(self.validate()['status'],'BOUND_BLIND_EVIDENCE')
        envelope=json.loads(Path(self.rows[0]['nativeEvidence']['path']).read_text())
        artifact=json.loads(Path(envelope['nativeExposure']['path']).read_text())
        runs=self.f.report['cells'][0]['runs']
        # Genuine original-archive run-1 evidence must not satisfy all three outer labels.
        first=copy.deepcopy(runs[0]['evidence'])
        for run in runs:run['evidence']=copy.deepcopy(first)
        native_read=self.f.put_gz('native-read.json.gz',self.f.report)
        artifact['nativeRead']=native_read
        envelope.update(nativeRead=native_read,runs=[r['evidence'] for r in runs],
                        nativeExposure=self.f.put('blind-artifacts.json',artifact))
        self.rows[0]['nativeEvidence']=self.f.put('blind-envelope.json',envelope)
        with self.assertRaisesRegex(ValueError,'run'):self.validate()

    def test_native_claim_must_belong_to_this_exact_exposure(self):
        envelope=json.loads(Path(self.rows[0]['nativeEvidence']['path']).read_text())
        artifact=json.loads(Path(envelope['nativeExposure']['path']).read_text())
        claim=json.loads(Path(artifact['claim']['path']).read_text())
        claim['batch']=self.f.put('other-batch.json',{'phase':'exposure'})
        artifact['claim']=self.f.put('native-claim.json',claim)
        envelope['nativeExposure']=self.f.put('blind-artifacts.json',artifact)
        self.rows[0]['nativeEvidence']=self.f.put('blind-envelope.json',envelope)
        with self.assertRaises(ValueError):self.validate()


if __name__=='__main__':unittest.main()
