"""DL5h archived consumers: real synthetic pair proof, pinned result chain and copied origins."""
import copy
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

HERE=Path(__file__).resolve().parent
FIT=HERE.parent


def source(path,name):
    import types
    module=types.ModuleType(name);module.__file__=str(path);sys.modules[name]=module
    exec(compile(path.read_bytes(),str(path),'exec'),module.__dict__)
    return module


F=source(FIT/'measurement/test_repeat.py','archived_pair_fixture')


class ArchivedRepeatTests(unittest.TestCase):
    def fixture(self):
        f=F.PairFixture(self,current=True)
        a=source(f.fit/'current-analysis/analysis.py','archived_pair_consumer')
        folder=Path(f.record['artifacts']['png']['path']).parent
        contract=Path(f.context['contract']);batch=Path(f.context['batchPath'])
        f.record['origin']={'kind':'fresh-attempt3'}
        captures=dict(status='CAPTURED',candidateSha256s=[f.candidate['sha256']],captures=[f.record])
        claim=Path(str(contract)+'.started.json')
        F.write(claim,dict(phase='current',contractSha256=f.D.sha(contract),batchSha256=f.D.sha(batch),
                          output=str(f.output),numericalAdmission=None,pid=123,gpuLease='completed-test-lease'))
        d3=source(F.CURRENT/'execution/dispatch.py','archived_result_inventory')
        artifact_pins=[copy.deepcopy(p) for p in f.record['artifacts'].values()]
        result=Path(str(contract)+'.result.json')
        f.D.write_sealed(result,dict(contractSha256=f.D.sha(contract),claimSha256=f.D.sha(claim),
            report={'status':'CAPTURED','captures':captures},captures=captures,
            captureReceipt={'members':[['synthetic-member']],'artifacts':artifact_pins},
            repeatReceipt=d3.repeat_artifact_pins(f.repo,captures)))
        # A genuine sealed result/claim/contract link, not a reconstructed live dispatcher.
        f.D.result_for(contract)
        member=dict(run=f.run,receipt=f.record,output=str(f.output),result=f.pin(result),
                    contract=f.pin(contract),claim=f.pin(claim),batch=f.pin(batch))
        root=f.D.sealed(f.root);rows=f.D.load(f.repo/root['references']['path'])['cells']
        candidate=f.M.A.candidate_info(f.candidate,.5)
        candidate=dict(document=f.candidate,position=.5,endpoints=candidate['endpoints'],
                       originalDocumentPair={'active.dark':'a'*64,'receded.dark':'b'*64})
        f.D._ACTIVE=None
        self.enterContext(patch.dict(sys.modules,{'w50_g1_dispatch':None}))
        return f,a,root,rows,member,candidate

    def test_archived_banded_pair_retains_first_reading_and_validates_without_live_context(self):
        f,a,root,rows,member,candidate=self.fixture()
        a.bind_completed_repeat(root,f.pin(f.root),member,rows)
        plan,spec,raw,arguments,provenance=a.capture_inputs(member,candidate)
        self.assertEqual(raw,Path(f.record['artifacts']['png']['path']).read_bytes())
        self.assertEqual(provenance['repeatAdmission'],f.record['repeatAdmission'])
        self.assertEqual(provenance['reading'],'first')
        self.assertEqual(arguments[0]['linearLuminance'],.2)
        self.assertFalse(json.loads(Path(f.record['artifacts']['cell']['path']).read_bytes())['deterministic'])

    def test_missing_chain_wrong_row_and_unbound_second_or_fault_proof_refuse(self):
        for mutation in ('result','claim','record','second','fault','registration'):
            with self.subTest(mutation=mutation):
                f,a,root,rows,member,candidate=self.fixture()
                if mutation=='result':
                    member['result']={**member['result'],'sha256':'0'*64}
                elif mutation=='claim':
                    Path(f.repo/member['claim']['path']).write_text('{}')
                elif mutation=='record':
                    member['receipt']=copy.deepcopy(member['receipt']);member['receipt']['scene']='other'
                elif mutation=='second':
                    pair=json.loads(Path(f.record['repeatPair']['path']).read_bytes())
                    Path(pair['second']['image']['path']).write_bytes(b'changed')
                elif mutation=='fault':
                    f.record['repeatAdmission']=F.write(Path(f.record['repeatAdmission']['path']),
                        {'schema':'w50-repeat-fault-1','status':'INSTRUMENT_FAULT'})
                else:
                    root=copy.deepcopy(root);root['repeatAdmission']['config']={'path':'unbound','sha256':'0'*64}
                with self.assertRaises(ValueError):a.bind_completed_repeat(root,f.pin(f.root),member,rows)

    def test_mutating_receipt_after_archival_admission_cannot_select_second_image(self):
        f,a,root,rows,member,candidate=self.fixture()
        a.bind_completed_repeat(root,f.pin(f.root),member,rows)
        pair=json.loads(Path(f.record['repeatPair']['path']).read_bytes())
        member['receipt']['artifacts']['png']=pair['second']['image']
        with self.assertRaises(ValueError):a.capture_inputs(member,candidate)

    def test_both_archived_pages_are_checked_with_original_pure_report_validator(self):
        f,a,root,rows,member,candidate=self.fixture()
        pair_path=Path(f.record['repeatPair']['path']);pair=json.loads(pair_path.read_bytes())
        second=Path(pair['second']['report']['path']);page=json.loads(second.read_bytes())
        page['groups'][0]['state']['materialDocument']['resolvedMaterialSha256']='0'*16
        pair['second']['report']=F.write(second,page)
        f.record['repeatPair']=F.write(pair_path,pair)
        proof_path=Path(f.record['repeatAdmission']['path']);proof=json.loads(proof_path.read_bytes())
        proof.update(manifest=f.record['repeatPair'],pair=pair)
        f.record['repeatAdmission']=F.write(proof_path,proof)
        # Re-pin the synthetic archival result to reach semantic page validation, not hash refusal.
        result_path=f.repo/member['result']['path'];result=json.loads(result_path.read_bytes())
        d3=source(F.CURRENT/'execution/dispatch.py','archived_changed_page_inventory')
        result['captures']['captures']=[f.record];result['report']['captures']=result['captures']
        result['repeatReceipt']=d3.repeat_artifact_pins(f.repo,result['captures'])
        F.write(result_path,result);Path(str(result_path)+'.sha256').write_text(f'{f.D.sha(result_path)}  {result_path.name}\n')
        member['result']=f.pin(result_path)
        a.bind_completed_repeat(root,f.pin(f.root),member,rows)
        with self.assertRaisesRegex(ValueError,'endpoint|digest'):
            a.capture_inputs(member,candidate)

    def test_unproved_false_metadata_does_not_gain_an_archived_path(self):
        f,a,_,_,member,candidate=self.fixture()
        with self.assertRaises(ValueError):a.capture_inputs(member,candidate)


class LegacyRepeatTests(unittest.TestCase):
    def fixture(self):
        import shutil
        f=F.PairFixture(self,current=True,identical=True)
        a=source(f.fit/'current-analysis/analysis.py','archived_legacy_consumer')
        original=copy.deepcopy(f.record['artifacts'])
        receipt=copy.deepcopy(f.record)
        receipt.pop('repeatPair')
        previous=f.fit/'synthetic/previous-root.json';F.write(previous,f.root.read_bytes())
        original_evidence={'request':F.write(f.fit/'synthetic/old-request.json',{'synthetic':'original request'})}
        prior_root=f.pin(previous);prior_claim={'path':'synthetic/prior-claim','sha256':'1'*64}
        prior_failure={'path':'synthetic/prior-failure','sha256':'2'*64}
        receipt['origin']=dict(kind='retained-attempt2',ordinal=1,priorRoot=prior_root,priorClaim=prior_claim,
            priorFailure=prior_failure,originalArtifacts=original,originalEvidence=original_evidence)
        receipt['repeatAdmission']=dict(schema='w50-legacy-byte-identical-1',mode='legacy-byte-identical',
            reading='first',first=original['png'],originalEqualityAttestation=original['cell'],
            deterministic=True,repeatNoise=0,secondRetained=False)
        folder=f.output/'retained-attempt2'/receipt['profile']/receipt['scene']/receipt['renderer']
        folder.mkdir(parents=True)
        for name,pin in original.items():receipt['artifacts'][name]=F.write(folder/Path(pin['path']).name,
                                                                         Path(pin['path']).read_bytes())
        target=f.current/'execution/dispatch.py';target.parent.mkdir(parents=True)
        shutil.copyfile(F.CURRENT/'execution/dispatch.py',target)
        d3=source(target,'archived_legacy_dispatch')
        batch=Path(f.context['batchPath']);contract=Path(f.context['contract'])
        root=f.D.sealed(f.root)
        root.update(bootstrap=f.pin(target),currentBatches=[f.pin(batch)],
            recovery={'retained':[dict(batchIndex=0,ordinal=1,profile=receipt['profile'],renderer=receipt['renderer'],
                scene=receipt['scene'],artifacts=original,originalEvidence=original_evidence)]},
            recoveryAttempt=dict(priorRoot=prior_root,priorClaim=prior_claim,priorFailure=prior_failure))
        F.write(f.root,root);Path(str(f.root)+'.sha256').write_text(f'{f.D.sha(f.root)}  {f.root.name}\n')
        claim=Path(str(contract)+'.started.json');F.write(claim,dict(phase='current',contractSha256=f.D.sha(contract),
            batchSha256=f.D.sha(batch),output=str(f.output),numericalAdmission=None))
        captures=dict(status='CAPTURED',candidateSha256s=[f.candidate['sha256']],captures=[receipt])
        result=Path(str(contract)+'.result.json')
        f.D.write_sealed(result,dict(contractSha256=f.D.sha(contract),claimSha256=f.D.sha(claim),
            report={'status':'CAPTURED','captures':captures},captures=captures,
            captureReceipt={'members':[['synthetic-member']],'artifacts':list(receipt['artifacts'].values())},
            repeatReceipt=[]))
        member=dict(run=f.run,receipt=receipt,output=str(f.output),result=f.pin(result),
            contract=f.pin(contract),claim=f.pin(claim),batch=f.pin(batch))
        rows=f.D.load(f.repo/root['references']['path'])['cells']
        candidate=dict(document=f.candidate,position=.5,
            endpoints=f.M.A.candidate_info(f.candidate,.5,current=True)['endpoints'],
            originalDocumentPair={'active.dark':'a'*64,'receded.dark':'b'*64})
        f.D._ACTIVE=None
        self.enterContext(patch.dict(sys.modules,{'w50_g1_dispatch':None}))
        return f,a,root,rows,member,candidate

    def test_exact_recovery_origin_admits_only_canonical_retained_copy_location(self):
        f,a,root,rows,member,candidate=self.fixture()
        a.bind_completed_repeat(root,f.pin(f.root),member,rows)
        _,_,raw,arguments,provenance=a.capture_inputs(member,candidate)
        self.assertEqual(raw,Path(member['receipt']['origin']['originalArtifacts']['png']['path']).read_bytes())
        self.assertEqual(provenance['origin'],member['receipt']['origin'])
        self.assertEqual(provenance['repeatAdmission']['mode'],'legacy-byte-identical')
        self.assertFalse(provenance['repeatAdmission']['secondRetained'])
        self.assertNotIn('repeatPair',provenance)
        self.assertEqual(arguments[0]['linearLuminance'],.2)

    def test_unbound_origin_changed_original_or_manufactured_second_cannot_admit_a_copy(self):
        for mutation in ('origin','original','second','unbound'):
            with self.subTest(mutation=mutation):
                f,a,root,rows,member,candidate=self.fixture()
                if mutation=='origin':member['receipt']['origin']['ordinal']=2
                elif mutation=='original':
                    Path(member['receipt']['origin']['originalArtifacts']['png']['path']).write_bytes(b'changed')
                elif mutation=='second':member['receipt']['repeatPair']={'path':'invented','sha256':'0'*64}
                if mutation=='unbound':
                    with self.assertRaises(ValueError):a.capture_inputs(member,candidate)
                else:
                    with self.assertRaises(ValueError):a.bind_completed_repeat(root,f.pin(f.root),member,rows)


class FreshCanonicalRepeatTests(unittest.TestCase):
    def fixture(self):
        import numpy as np
        f=F.PairFixture(self,current=True)
        native_fixture=source(F.FIT/'references/test_canonical.py','archived_canonical_native_fixture')
        canonical_config,scenes,_,_=native_fixture.trees(f.directory/'canonical-native')
        scenes_path=f.repo/'apps/reference-apple/scenes.json';F.write(scenes_path,scenes)
        scene='text__r__rest';profile=f.profile;tier='webgpu'
        run=dict(f.run,sceneSource='canonical',scenes=[scene],captureRoot=str(f.output/'canonical'),
                 matrixPath=str(f.output/'canonical-matrix.json'))
        native_path=Path(canonical_config['fixtureRoot'])/profile/(scene+'.png')
        row=dict(profile=profile,renderer=tier,scene=scene,statistic='T1-low',stratum='T',role='gate',
                 nativeEvidence=native_fixture.pin(native_path),B=None)
        root=f.D.sealed(f.root)
        references=f.repo/root['references']['path'];original=f.D.load(references)['cells']
        F.write(references,dict(schema='w50-reference-inventory-1',cells=original+[row]))
        root['references']=f.pin(references)
        canonical=f.fit/'synthetic/canonical-config.json';F.write(canonical,canonical_config)
        config=f.repo/root['repeatAdmission']['config']['path'];value=f.D.load(config)
        value.update(references=root['references'],canonical=f.pin(canonical));F.write(config,value)
        root['repeatAdmission']['config']=f.pin(config)
        F.write(f.root,root);Path(str(f.root)+'.sha256').write_text(f'{f.D.sha(f.root)}  {f.root.name}\n')
        candidate=f.M.A.candidate_info(f.candidate,.5,current=True)
        endpoint=candidate['endpoints']['active.dark']
        folder=Path(run['captureRoot'])/profile/scene;folder.mkdir(parents=True)
        first=np.full((200,320,3),20,dtype=np.uint8);second=first.copy();second[0,0,0]=21
        noise=1/(200*320*4)
        old=f.D.load(Path(f.record['artifacts']['report']['path']))['page']
        page=copy.deepcopy(old)
        page.update(sceneId=scene,canvas={'width':320,'height':200},pixelSize=[320,200],pressed=False,tint=None,
                    transparentPage=False,background=dict(id='solid',naturalWidth=320,naturalHeight=200))
        page['groups'][0]['configuredSource']='texture'
        page['surfaces'][0]['bounds']=dict(x=76,y=52,width=168,height=96)
        pair=dict(schema=1,kind='w50-retained-repeat-pair',reading='first',scene=scene,renderer=tier,
                  deterministic=False,repeatNoise=noise)
        for side,suffix,image in (('first','',first),('second','__repeat',second)):
            pair[side]=dict(image=F.write(folder/f'{scene}__{tier}{suffix}.png',F.png(image)),
                            report=F.write(folder/f'page__{tier}__{side}.json',page))
        metadata=dict(renderer=tier,colorSpace='srgb',deterministic=False,repeatNoise=noise,
            capturePath=f'candidateDocument={f.candidate["path"]} declarationSha256={f.candidate["sha256"][:12]}')
        matrix_row=dict(key=dict(profileKey=profile,sceneId=scene,web=metadata),fixtureSet='calibration')
        matrix=F.write(Path(run['matrixPath']),dict(schemaVersion=5,cells=[matrix_row]))
        artifacts=dict(png=pair['first']['image'],report=F.write(folder/f'report__{tier}.json',
            dict(page=page,fallback=False,problems=[])),cell=F.write(folder/f'cell__{tier}.json',metadata))
        pair_pin=F.write(folder/f'repeat__{tier}.json',pair)
        artifacts['files']=[dict(path=str(p),sha256=f.D.sha(p)) for p in sorted(folder.iterdir())]
        artifacts['transport']=[F.write(Path(run['captureRoot'])/filename,{'synthetic':'transport'}) for filename in (
            f'census-{scene}.json',f'request-{scene}.json',f'exit-{scene}.json',f'compare-{scene}.log',
            f'capture-{scene}.log',f'fresh-{scene}.json','request.json','native-request.json',f'native-admission-{scene}.json')]
        record=dict(profile=profile,renderer=tier,scene=scene,candidate=f.candidate,lane='current',sceneSource='canonical',
                    artifacts=artifacts,repeatPair=pair_pin,matrix=matrix,row=matrix_row,endpoint=endpoint,
                    origin={'kind':'fresh-attempt3'})
        batch=Path(f.context['batchPath']);F.write(batch,{'phase':'current','runs':[run]})
        f.context.update(batch={'phase':'current','runs':[run]},repeatAdmission=root['repeatAdmission'],
                         inputs=f.context['inputs']+[root['repeatAdmission']['config']])
        f.D._ACTIVE=(f.context,copy.deepcopy(f.context),f.D.sha(f.context['contract']),f.D.sha(batch),True,root,None)
        record['repeatAdmission']=f.P.admit_pair(f.context,run,record,pair_pin)
        contract=Path(f.context['contract']);claim=Path(str(contract)+'.started.json')
        F.write(claim,dict(phase='current',contractSha256=f.D.sha(contract),batchSha256=f.D.sha(batch),
                          output=str(f.output),numericalAdmission=None))
        captures=dict(status='CAPTURED',candidateSha256s=[f.candidate['sha256']],captures=[record])
        result=Path(str(contract)+'.result.json');d3=source(F.CURRENT/'execution/dispatch.py','canonical_repeat_inventory')
        f.D.write_sealed(result,dict(contractSha256=f.D.sha(contract),claimSha256=f.D.sha(claim),
            report={'status':'CAPTURED','captures':captures},captures=captures,
            captureReceipt={'members':[['synthetic-member']],'artifacts':[artifacts[k] for k in ('png','report','cell')]},
            repeatReceipt=d3.repeat_artifact_pins(f.repo,captures)))
        member=dict(run=run,receipt=record,output=str(f.output),result=f.pin(result),contract=f.pin(contract),
                    claim=f.pin(claim),batch=f.pin(batch))
        original_pair={};endpoints={}
        for slot,ep in candidate['endpoints'].items():
            pose,scheme=slot.split('.');suffix='-receded' if pose=='receded' else ''
            path=f.repo/'packages/calibration/profiles'/f'apple-macos-27.0-1x-{scheme}-standard-glass0.5{suffix}.json'
            endpoints[slot]=dict(ep,source=f.pin(path),candidateEndpoint=f.pin(Path(ep['path'])))
            if scheme=='dark':original_pair[slot]=f.D.sha(path)
        candidate=dict(document=f.candidate,position=.5,endpoints=endpoints,originalDocumentPair=original_pair)
        a=source(f.fit/'current-analysis/analysis.py','archived_fresh_canonical_consumer')
        f.D._ACTIVE=None;self.enterContext(patch.dict(sys.modules,{'w50_g1_dispatch':None}))
        return f,a,root,original+[row],member,candidate

    def test_fresh_canonical_nine_transport_pins_and_banded_repeat_keep_first_reading(self):
        f,a,root,rows,member,candidate=self.fixture()
        a.bind_completed_repeat(root,f.pin(f.root),member,rows)
        _,_,raw,arguments,provenance=a.capture_inputs(member,candidate)
        self.assertEqual(raw,Path(member['receipt']['artifacts']['png']['path']).read_bytes())
        self.assertEqual(len(provenance['artifacts']['transport']),9)
        self.assertEqual(provenance['reading'],'first')
        self.assertFalse(member['receipt']['row']['key']['web']['deterministic'])
        self.assertGreater(member['receipt']['row']['key']['web']['repeatNoise'],0)
        self.assertEqual(arguments[0]['linearLuminance'],.2)
        self.assertEqual(arguments[0]['span'],96)
        self.assertEqual(arguments[0]['rgb'],[.2]*3)

    def test_fresh_canonical_cannot_drop_or_substitute_its_new_transport_pins(self):
        f,a,root,rows,member,candidate=self.fixture()
        a.bind_completed_repeat(root,f.pin(f.root),member,rows)
        member['receipt']['artifacts']['transport'].pop()
        with self.assertRaises(ValueError):a.capture_inputs(member,candidate)


if __name__=='__main__':unittest.main()
