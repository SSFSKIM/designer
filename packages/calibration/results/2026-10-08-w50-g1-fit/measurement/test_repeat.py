"""DL5h consumers over disposable source-relocated native trees and real pair admission."""
import copy
import gzip
import hashlib
import io
import json
from pathlib import Path
import shutil
import sys
import tempfile
import types
import unittest
from unittest.mock import patch

import numpy as np
from PIL import Image

HERE=Path(__file__).resolve().parent
FIT=HERE.parent
RESULTS=FIT.parent
CURRENT=RESULTS/'2026-10-08-w50-g1-current3'


def source(path,name):
    module=types.ModuleType(name);module.__file__=str(path)
    sys.modules[name]=module
    exec(compile(path.read_bytes(),str(path),'exec'),module.__dict__)
    return module


def write(path,value):
    path.parent.mkdir(parents=True,exist_ok=True)
    raw=value if isinstance(value,bytes) else (json.dumps(value,allow_nan=False)+'\n').encode()
    path.write_bytes(raw)
    return {'path':str(path),'sha256':hashlib.sha256(raw).hexdigest()}


def png(rgb):
    stream=io.BytesIO();Image.fromarray(rgb).save(stream,format='PNG');return stream.getvalue()


class PairFixture:
    """Source-only relocation plus the actual synthetic native bootstrap and role reader."""
    def __init__(self,case,*,current=False,identical=False):
        temporary=case.enterContext(tempfile.TemporaryDirectory())
        self.directory=Path(temporary).resolve()
        F=source(FIT/'native/test_bootstrap.py','consumer_native_bootstrap_fixture')
        fixture=F.BootstrapTests()
        self.repo,self.native,batch=fixture.fixture(self.directory)
        fixture.seal(self.native,batch)
        self.repo=self.repo.resolve()
        base=self.repo/'packages/calibration/results'
        self.fit=base/FIT.name;self.current=base/CURRENT.name
        paths=[('current-analysis',n) for n in ('analysis.py','run.py','native_evidence.py')]
        paths += [('measurement','capture.py'),('web','adapter.py'),('canonical','adapter.py')]
        paths += [('references',n) for n in ('canonical.py','statistics.py')]
        paths += [('execution',n) for n in ('dispatch.py','admission.py')]
        for folder,name in paths:
            target=self.fit/folder/name;target.parent.mkdir(parents=True,exist_ok=True)
            shutil.copyfile(FIT/folder/name,target)
        for folder,names in [('repeat',('admission.py','sources.py','core.py')),('web',('adapter.py',)),
                             ('canonical',('adapter.py',))]:
            for name in names:
                target=self.current/folder/name;target.parent.mkdir(parents=True,exist_ok=True)
                shutil.copyfile(CURRENT/folder/name,target)
        for relative in ('2026-10-08-w50-g0-declaration/audit/numerical_guard.py',
                         '2026-10-01-w43-g0-declaration/bed/sitting/w43_archive.py'):
            target=base/relative;target.parent.mkdir(parents=True,exist_ok=True)
            shutil.copyfile(RESULTS/relative,target)
        self.M=source(self.fit/'measurement/capture.py','consumer_measurement')
        self.P=source(self.current/'repeat/admission.py','consumer_pair_admission')
        self.D=source(self.fit/'execution/dispatch.py','consumer_actual_dispatch')
        def pin(path):
            item={'path':str(path.relative_to(self.repo)),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
            return item
        self.pin=pin
        native_batch=json.loads(batch.read_bytes())
        self.native_config={name:pin(self.native/filename) for name,filename in (
            ('instrument','instrument-root.json'),('contract','execution-contract.json'),('batch','read-batch.json'))}
        self.native_config['reports']={}
        manifest=json.loads((self.repo/native_batch['inputs']['manifest']['path']).read_bytes())
        scenes=json.loads((self.repo/native_batch['inputs']['scenes']['path']).read_bytes())
        reports={}
        for export in native_batch['exports']:
            report=self.M.R.read_role_export(export['root'],export['indexSha256'],export['role'],manifest,scenes,
                expected_declaration_sha256=native_batch['inputs']['declaration']['sha256'])
            path=self.fit/'synthetic'/f'{export["role"]}.json.gz'
            write(path,gzip.compress(json.dumps(report).encode(),mtime=0))
            self.native_config['reports'][export['role']]=pin(path);reports[export['role']]=report
        self.cell=next(c for c in reports['calibration']['cells'] if c['family']=='structured')
        self.profile=self.cell['profile'];self.scene=self.cell['scene']
        candidate_path=self.fit/'synthetic/candidate.json';slots={}
        original_dir=self.fit/'synthetic/profiles'
        original_pins=[]
        for pose in ('active','receded'):
            for scheme in ('light','dark'):
                suffix='-receded' if pose=='receded' else ''
                key=f'apple-macos-27.0-1x-{scheme}-standard-glass0.5{suffix}'
                old=dict(profileKey=key,resolvedMaterialSha256='b'*16,patch={'backdropToneAbscissa':'silhouette'})
                oldpath=original_dir/(key+'.json');write(oldpath,old);original_pins.append(pin(oldpath))
                if current:write(self.repo/'packages/calibration/profiles'/(key+'.json'),old)
                patch_values=dict(old['patch'])
                if scheme=='dark' and not current:
                    patch_values.update(lowEndStrength=1,lowEnd44=[0]*4,lowEnd96=[0]*4,lowEnd160=[0]*4)
                endpoint={**old,'profileKey':key.replace('glass0.5','glass0.500'),'patch':patch_values}
                endpoint_path=candidate_path.with_name(pose+'.'+scheme+'.json');write(endpoint_path,endpoint)
                slots[pose+'.'+scheme]={'path':endpoint_path.name,'sha256':hashlib.sha256(endpoint_path.read_bytes()).hexdigest()}
        write(candidate_path,dict(kind='vitrea-candidate-material-document',schemaVersion=1,glassTintAmount=.5,
                                 endpoints=slots,cssTierMappingSha256='c'*64))
        self.candidate=pin(candidate_path)
        self.output=self.directory/'output';self.output.mkdir()
        self.run=dict(id='synthetic',profile=self.profile,renderer='webgpu',sceneSource='w50',
                      candidate=self.candidate,scenes=[self.scene],sets=['calibration'],
                      captureRoot=str(self.output/'captures'))
        endpoint=self.M.A.candidate_info(self.candidate,.5)['endpoints']['active.dark']
        spec=self.M.A.scene_plan(self.run)['scenes'][0]
        material={k:endpoint[k] for k in ('profileKey','resolvedMaterialSha256')}
        material.update(glassTintAmount=.5,tuned=False)
        page=dict(sceneId=self.scene,requestedRenderer='webgpu',canvas=scenes['canvas'],pixelSize=[512,384],
            devicePixelRatio=1,requestedScale=1,colorScheme='dark',materialMode='candidate',windowActivation='active',
            material=material,candidateDocument={'mode':'candidate','declarationSha256':self.candidate['sha256'][:12]},
            requestedBackdropMode='texture',requestedBackdropLevel=None,
            background=dict(id=spec['background'],naturalWidth=512,naturalHeight=384),
            accessibilityPolicy=dict(reducedTransparency=False,increasedContrast=False,forcedColors=False),problems=[],
            surfaces=[dict(nodeId='s',groupId='g',family='fixed-rounded-rect',radius=20.4,bounds=spec['geometry'])],
            groups=[dict(id='g',state=dict(activeRenderer='webgpu',samplingBackend='gpu-texture',health='ok',
                materialDocument=material,backdropToneAbscissae=[dict(surfaceId='s',kind='silhouette',sampleCount=10,
                    encodedLuminance=.1,linearLuminance=.2,color=[.2]*3)]))])
        self.first=np.full((384,512,3),20,dtype=np.uint8)
        second=self.first.copy()
        if not identical:second[0,0,0]=21
        noise=float(np.abs(self.first.astype('int16')-second.astype('int16')).sum()/(384*512*4))
        folder=Path(self.run['captureRoot'])/self.scene;folder.mkdir(parents=True)
        pair=dict(schema=1,kind='w50-retained-repeat-pair',reading='first',scene=self.scene,renderer='webgpu',
                  deterministic=identical,repeatNoise=noise)
        for side,suffix,image in (('first','',self.first),('second','__repeat',second)):
            pair[side]=dict(image=write(folder/f'{self.scene}__webgpu{suffix}.png',png(image)),
                            report=write(folder/f'page__webgpu__{side}.json',page))
        metadata=dict(renderer='webgpu',colorSpace='srgb',deterministic=identical,repeatNoise=noise,
                      capturePath=f'declarationSha256={self.candidate["sha256"][:12]}')
        self.metadata=metadata
        artifacts=dict(png=pair['first']['image'],report=write(folder/'report__webgpu.json',
            dict(page=page,fallback=False,problems=[])),cell=write(folder/'cell__webgpu.json',metadata))
        self.record=dict(profile=self.profile,renderer='webgpu',scene=self.scene,candidate=self.candidate,
            lane='current' if current else 'candidate',sceneSource='w50',canvas=scenes['canvas'],dpr=1,artifacts=artifacts,
            repeatPair=write(folder/'repeat__webgpu.json',pair))
        rows=[dict(profile=self.profile,renderer='webgpu',scene=self.scene,statistic=name,role='calibration')
              for name in self.cell['statistics']]
        refs=self.fit/'synthetic/references.json';write(refs,dict(cells=rows))
        config=self.fit/'synthetic/repeat-config.json'
        write(config,dict(schema='w50-repeat-config-1',references=pin(refs),native=self.native_config))
        binding=dict(entrypoint=pin(self.current/'repeat/admission.py'),config=pin(config))
        live=self.fit/'synthetic/live/g0'
        one=live/'declaration.json';two=live/'fit-declaration.json'
        write(one,dict(sources=[native_batch['inputs']['scenes']]))
        write(two,dict(sources=original_pins+[native_batch['inputs']['scenes']]))
        self.root=self.fit/'synthetic/root.json'
        doc=dict(repo=str(self.repo),bootstrap=pin(self.fit/'execution/dispatch.py'),
                 repeatAdmission=binding,references=pin(refs),partOne=pin(one),partTwo=pin(two),
                 closure={'sources':{binding['entrypoint']['path']:binding['entrypoint']['sha256']}})
        self.D.write_sealed(self.root,doc)
        phase='current' if current else 'fit'
        contract=self.fit/'synthetic/contract.json';write(contract,{'phase':phase})
        batch_path=self.fit/'synthetic/batch.json';write(batch_path,{'phase':phase,'runs':[self.run]})
        numerical=self.fit/'synthetic/numerical.json';write(numerical,{'synthetic':'already-admitted'})
        inputs=[binding['config'],self.native_config['reports']['calibration'],self.native_config['batch']]
        self.context=dict(repo=str(self.repo),phase=phase,executionRoot=str(self.root),contract=str(contract),
            batchPath=str(batch_path),batch={'phase':phase,'runs':[self.run]},output=str(self.output),
            repeatAdmission=binding,inputs=inputs,baselineDocuments=[])
        self.D.GPU_LOCK=self.directory/'synthetic-lease'
        case.enterContext(self.D.owned_gpu_lock())
        self.D._ACTIVE=(self.context,copy.deepcopy(self.context),self.D.sha(contract),self.D.sha(batch_path),
                        True,doc,pin(numerical))
        case.addCleanup(setattr,self.D,'_ACTIVE',None)
        case.enterContext(patch.dict(sys.modules,{'w50_g1_dispatch':self.D}))
        self.record['repeatAdmission']=self.P.admit_pair(self.context,self.run,self.record,self.record['repeatPair'])
        self.scenes_pin=native_batch['inputs']['scenes']

    def measure(self):
        return self.M.measure_capture(self.context,self.native_config['reports']['calibration'],
            self.record,self.scenes_pin,native_batch_pin=self.native_config['batch'])


class LiveRepeatTests(unittest.TestCase):
    def test_real_source_admitted_nonidentical_pair_keeps_first_png_and_false_metadata(self):
        fixture=PairFixture(self)
        result=fixture.measure()
        self.assertEqual(result['statistics']['deep8-channel-median']['value'],[20]*3)
        self.assertEqual(result['evidence']['capture'],fixture.record['artifacts']['png'])
        self.assertEqual(result['evidence']['repeatAdmission'],fixture.record['repeatAdmission'])
        self.assertFalse(json.loads(Path(fixture.record['artifacts']['cell']['path']).read_bytes())['deterministic'])
        self.assertEqual(fixture.P.verify_receipt(fixture.context,fixture.run,fixture.record)['mode'],'native-repeat-band')

    def test_unproved_false_wrong_member_altered_second_and_fault_receipt_are_rejected(self):
        fixture=PairFixture(self)
        for mutation in ('missing','second','row','fault','binding'):
            record=copy.deepcopy(fixture.record)
            restored=None
            if mutation=='missing':fixture.record.pop('repeatAdmission')
            elif mutation=='second':
                p=Path(fixture.record['repeatPair']['path']);pair=json.loads(p.read_bytes())
                p=Path(pair['second']['image']['path']);restored=(p,p.read_bytes());p.write_bytes(b'changed')
            elif mutation=='row':fixture.record['repeatAdmission']=dict(fixture.record['repeatAdmission'],sha256='0'*64)
            elif mutation=='fault':
                path=Path(fixture.record['repeatAdmission']['path']);restored=(path,path.read_bytes())
                fixture.record['repeatAdmission']=write(path,{'schema':'w50-repeat-fault-1','status':'INSTRUMENT_FAULT'})
            else:
                fixture.context['repeatAdmission']={**fixture.context['repeatAdmission'],'config':{'path':'unbound','sha256':'0'*64}}
            with self.subTest(mutation=mutation),self.assertRaises(ValueError):fixture.measure()
            if restored:restored[0].write_bytes(restored[1])
            fixture.record=record
            if mutation=='binding':fixture.context['repeatAdmission']=fixture.D._ACTIVE[1]['repeatAdmission']


if __name__=='__main__':unittest.main()
