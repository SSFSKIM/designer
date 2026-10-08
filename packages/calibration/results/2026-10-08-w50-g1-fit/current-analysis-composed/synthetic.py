"""Two independent archived-pair component fixtures, with generated images and no live context.

These exercise consumer root ownership and immutable repeat/report validation AFTER the
composition authority boundary. They are not a full799-member historical recovery fixture.
Only Python source bytes are copied from the sealed source graph; all data is generated here.
"""
import copy
import hashlib
import io
import json
from pathlib import Path
import shutil
import tempfile
import types
from unittest.mock import patch

HERE=Path(__file__).resolve().parent
REPO=HERE.parents[4]
FIT=HERE.parent


def source(path,name):
    module=types.ModuleType(name);module.__file__=str(path)
    exec(compile(path.read_bytes(),str(path),'exec'),module.__dict__)
    return module


def fixture(test, composed):
    directory=test.enterContext(tempfile.TemporaryDirectory());repo=Path(directory).resolve()
    root_metadata=REPO/'packages/calibration/results/2026-10-08-w50-g1-canonical3/execution/current-instrument-root.json'
    # A source-only inventory read: no input/result/capture named by the root is opened.
    graph=json.loads(root_metadata.read_bytes())['closure']['sources']
    for relative,digest in graph.items():
        original=REPO/relative;raw=original.read_bytes()
        if original.suffix!='.py' or hashlib.sha256(raw).hexdigest()!=digest:
            raise ValueError('Synthetic exercise requires unchanged sealed Python source')
        target=repo/relative;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(raw)
    fit=repo/FIT.relative_to(REPO)
    a=source(fit/'current-analysis/analysis.py','composed_synthetic_immutable_reader')
    test.enterContext(patch.object(composed,'REPO',repo))
    test.enterContext(patch.object(composed,'A',a))
    test.enterContext(patch.object(composed,'B',a.B))
    def put(path,value):
        path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
        raw=value if isinstance(value,bytes) else (json.dumps(value,sort_keys=True)+'\n').encode()
        path.write_bytes(raw)
        return {'path':str(path),'sha256':hashlib.sha256(raw).hexdigest()}
    def pin(path):return {'path':str(Path(path).relative_to(repo)),'sha256':a.B.sha(path)}
    def sealed(path,value):
        put(path,value);Path(str(path)+'.sha256').write_text(f'{a.B.sha(path)}  {Path(path).name}\n')
        return pin(path)
    def png(width,height):
        from PIL import Image
        stream=io.BytesIO();Image.new('RGB',(width,height),(20,20,20)).save(stream,format='PNG')
        return stream.getvalue()
    profile='apple-macos-27.0-1x-dark-standard-glass0.25'
    endpoints={};candidate_endpoints={};original_pair={}
    for pose in ('active','receded'):
        suffix='-receded' if pose=='receded' else ''
        original_path=repo/f'profiles/{pose}.json'
        original={'profileKey':profile+suffix,'resolvedMaterialSha256':'c'*16,
                  'patch':{'backdropToneAbscissa':'source'}}
        put(original_path,original)
        path=repo/f'gate0/{pose}.json';put(path,{**original,'profileKey':profile.replace('0.25','0.250')+suffix})
        item=pin(path);candidate_endpoints[pose+'.dark']={'path':path.name,'sha256':item['sha256']}
        endpoints[pose+'.dark']={**json.loads(path.read_bytes()),'source':pin(original_path),'candidateEndpoint':item}
        original_pair[pose+'.dark']=a.B.sha(original_path)
    candidate_path=repo/'gate0/candidate.json'
    put(candidate_path,{'syntheticCandidate':True,'endpoints':candidate_endpoints})
    candidate_pin=pin(candidate_path)
    candidate=dict(document=candidate_pin,position=.25,endpoints=endpoints,originalDocumentPair=original_pair)
    scenes=['cell-grey-004-s044__inactive','dark-solid__rrect-sm__inactive']
    component={'kind':'rrect','size':[120,44],'radius':10}
    for canvas,scene,source_path in (({'width':512,'height':384},scenes[0],a.M.A.G0/'bed/scenes-w50.json'),
                                   ({'width':320,'height':200},scenes[1],a.C.SCENES)):
        put(source_path,dict(canvas=canvas,profiles=[{'key':profile,'scenes':[scene]}],components={'shape':component},
            scenes=[{'id':scene,'component':'shape','state':'inactive','background':'dark-solid'}],
            split={'calibration':[scene]},tints={},backgrounds={'dark-solid':{'kind':'solid'}}))
    rows=[]
    for i,scene in enumerate(scenes):
        rows.append(dict(profile=profile,renderer='css',scene=scene,
            statistic='deep8-channel-median' if i==0 else 'low-end-path-level',
            role='calibration' if i==0 else 'gate',support='Original synthetic support prose',
            currentDocumentPair=original_pair,currentGeneration='synthetic',historical=[],B=None,
            nativeEvidence=None,currentEvidence=None,currentMetadata=None,status='UNMEASURED'))
    references=repo/'original-references.json';put(references,{'schema':'w50-reference-inventory-1','cells':rows})
    helper=fit.parent/'2026-10-08-w50-g1-current3/repeat/admission.py'
    repeat=source(helper,'composed_synthetic_archival_repeat')
    root_entries=[];result_entries=[];members=[];chains=[];chain_pins=[]
    for i,scene in enumerate(scenes):
        kind='w50' if i==0 else 'canonical';width,height=(512,384) if i==0 else (320,200)
        home=repo/f'actual-instrument-{i}';output=repo/f'actual-output-{i}';capture_root=output/'captures'
        run=dict(id=f'actual-run-{i}',profile=profile,renderer='css',candidate=candidate_pin,sceneSource=kind,
                 scenes=[scene],sets=['calibration'],captureRoot=str(capture_root))
        if kind=='canonical':run['matrixPath']=str(output/'matrix.json')
        batch_path=home/'batch.json';put(batch_path,{'schema':'w50-g1-batch-1','phase':'current',
            'cohort':[candidate_pin],'runs':[run]});batch_pin=pin(batch_path)
        config=home/'repeat-config.json';put(config,{'schema':'synthetic-archived-config','references':pin(references)})
        bootstrap=(fit.parent/('2026-10-08-w50-g1-current3' if i==0 else '2026-10-08-w50-g1-canonical3')/'execution/dispatch.py')
        root=dict(schema='w50-g1-current-instrument-root-1',repo=str(repo),bootstrap=pin(bootstrap),
            baselineDocuments=[candidate_pin],references=pin(references),currentBatches=[batch_pin],
            repeatAdmission={'entrypoint':pin(helper),'config':pin(config)},closure={'sources':graph})
        root_path=home/'current-instrument-root.json';root_pin=sealed(root_path,root)
        contract_path=home/'contract.json'
        contract_pin=sealed(contract_path,dict(schema='w50-g1-phase-contract-1',phase='current',
            executionRootSha256=root_pin['sha256'],batch=batch_pin,cohort=[candidate_pin]))
        claim_path=Path(str(contract_path)+'.started.json')
        put(claim_path,dict(phase='current',contractSha256=contract_pin['sha256'],batchSha256=batch_pin['sha256'],
                            output=str(output),numericalAdmission=None));claim_pin=pin(claim_path)
        endpoint=endpoints['receded.dark']
        material=dict(profileKey=endpoint['profileKey'],resolvedMaterialSha256=endpoint['resolvedMaterialSha256'],
                      glassTintAmount=.25,tuned=False)
        bounds=dict(x=(width-120)/2,y=(height-44)/2,width=120 if kind=='w50' else 122,height=44 if kind=='w50' else 46)
        page=dict(sceneId=scene,materialMode='candidate',candidateDocument=dict(mode='candidate',declarationSha256=candidate_pin['sha256'][:12]),
            colorScheme='dark',windowActivation='inactive',material=copy.deepcopy(material),requestedRenderer='css',
            canvas={'width':width,'height':height},pixelSize=[width,height],devicePixelRatio=1,requestedScale=1,
            pressed=False,tint=None,transparentPage=False,problems=[],requestedBackdropMode='texture',requestedBackdropLevel=None,
            accessibilityPolicy=dict(reducedTransparency=False,increasedContrast=False,forcedColors=False),
            background=dict(id='dark-solid',naturalWidth=width,naturalHeight=height),
            groups=[dict(id='g',configuredSource='texture',backdropTone=dict(level=.010022825574869039,linearLuminance=.2,rgb=[.2]*3),
                state=dict(activeRenderer='css',health='ok',samplingBackend='css-backdrop',materialDocument=copy.deepcopy(material)))],
            surfaces=[dict(nodeId='s',groupId='g',family='fixed-rounded-rect',radius=10,bounds=bounds)])
        folder=capture_root/(profile if kind=='canonical' else '')/scene
        pair=dict(schema=1,kind='w50-retained-repeat-pair',reading='first',scene=scene,renderer='css',
                  deterministic=True,repeatNoise=0)
        for side,suffix in (('first',''),('second','__repeat')):
            pair[side]=dict(image=put(folder/f'{scene}__css{suffix}.png',png(width,height)),
                            report=put(folder/f'page__css__{side}.json',page))
        metadata=dict(renderer='css',colorSpace='srgb',deterministic=True,repeatNoise=0,
            capturePath=f'candidateDocument={candidate_pin["path"]} declarationSha256={candidate_pin["sha256"][:12]}')
        artifacts=dict(png=pair['first']['image'],report=put(folder/'report__css.json',dict(page=page,fallback=False,problems=[])),
                       cell=put(folder/'cell__css.json',metadata))
        pair_pin=put(folder/'repeat__css.json',pair)
        receipt=dict(profile=profile,renderer='css',scene=scene,candidate=candidate_pin,lane='current',sceneSource=kind,
            artifacts=artifacts,repeatPair=pair_pin,origin={'kind':'fresh-attempt3' if i==0 else 'fresh-canonical-recovery'})
        if kind=='w50':receipt.update(canvas={'width':width,'height':height},dpr=1)
        else:
            row=dict(key=dict(profileKey=profile,sceneId=scene,web=metadata),fixtureSet='calibration')
            receipt.update(matrix=put(run['matrixPath'],{'schemaVersion':5,'cells':[row]}),row=row,
                endpoint=dict(path=str(repo/endpoint['candidateEndpoint']['path']),sha256=endpoint['candidateEndpoint']['sha256'],
                    profileKey=endpoint['profileKey'],resolvedMaterialSha256=endpoint['resolvedMaterialSha256'],patch=endpoint['patch'],
                    currentSource=dict(path=str(repo/endpoint['source']['path']),sha256=endpoint['source']['sha256'])))
            artifacts['files']=[put(p,p.read_bytes()) for p in sorted(folder.iterdir()) if p.is_file()]
            artifacts['transport']=[put(capture_root/name,{'synthetic':'transport'}) for name in (
                f'census-{scene}.json',f'request-{scene}.json',f'exit-{scene}.json',f'compare-{scene}.log',
                f'capture-{scene}.log',f'fresh-{scene}.json','request.json','native-request.json',f'native-admission-{scene}.json')]
        binding=dict(executionRootSha256=root_pin['sha256'],contractSha256=contract_pin['sha256'],batchSha256=batch_pin['sha256'],
                     config=root['repeatAdmission']['config'],declaredRows=[rows[i]])
        if kind=='canonical':binding['canonicalBackgroundKind']='solid'
        retained=repeat.read_retained_pair(output,run,receipt,pair_pin)
        proof=repeat.proof_metadata(binding,receipt,pair_pin,retained)
        receipt['repeatAdmission']=put(folder/'repeat-admission__css.json',proof)
        captures=dict(status='CAPTURED',candidateSha256s=[candidate_pin['sha256']],captures=[receipt])
        result_doc=dict(contractSha256=contract_pin['sha256'],claimSha256=claim_pin['sha256'],
            captures=captures,report={'status':'CAPTURED','captures':captures},
            captureReceipt={'members':[[profile,'css',scene]],'artifacts':[artifacts[k] for k in ('png','report','cell')]},
            repeatReceipt=[pair_pin,receipt['repeatAdmission'],*[pair[s][k] for s in ('first','second') for k in ('image','report')]])
        result_path=Path(str(contract_path)+'.result.json');result_pin=sealed(result_path,result_doc)
        root_entries.append({'pin':root_pin,'document':root});result_entries.append({'pin':result_pin,'document':result_doc})
        members.append(dict(instrument=root_pin,run=run,receipt=receipt,output=str(output),batch=batch_pin,
                            contract=contract_pin,claim=claim_pin,result=result_pin))
        chains.append(dict(instrument=root_pin,batch=batch_pin,contract=contract_pin,result=result_pin))
        chain_pins.extend([root_pin,batch_pin,contract_pin,claim_pin,result_pin])
    manifest=dict(schema='w50-completed-current-composition-1',originalInstrument=root_entries[0]['pin'],chains=chains)
    descriptor=repo/'synthetic-composition.json';put(descriptor,manifest);composition_pin=pin(descriptor)
    raw=dict(chainPins=[composition_pin,*chain_pins],roots=root_entries,resultDocuments=result_entries,
             candidates=[candidate_pin],members=members)
    admitted=composed.index_composition(raw,manifest,composition_pin)
    admitted['candidates']={candidate_pin['sha256']:candidate}
    return dict(repo=repo,admitted=admitted,rows=rows,candidate=candidate,put=put,pin=pin,repeat=repeat)
