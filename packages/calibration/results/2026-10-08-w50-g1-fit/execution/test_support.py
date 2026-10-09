"""Complete synthetic candidate/provenance fixtures; never reads material or pixel evidence."""
import hashlib
import json
from pathlib import Path
import shutil

BASE = Path('packages/calibration/results/2026-10-08-w50-g0-declaration')
RUNTIME = [str(BASE/'audit/numerical.ts'), 'pnpm-lock.yaml', 'packages/platform-web/src/optics.ts',
           'packages/renderer-webgpu/src/material.ts', 'packages/calibration/scripts/candidate-document.ts',
           'packages/platform-web/src/material-document.ts']
PROJECTION = ('id','candidateSha256','position','pose','dpr','span','role','profile','renderer','scene','variant')


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def build(repo, original_g0, proofs):
    all_pins = {}
    def put(name, data, collect=False):
        path=repo/name; path.parent.mkdir(parents=True,exist_ok=True)
        path.write_text(json.dumps(data,sort_keys=True)+'\n')
        pin={'path':str(name),'sha256':sha(path)}
        if collect: all_pins[str(name)]=pin
        return pin
    def pin(path): return {'path':str(path.relative_to(repo)),'sha256':sha(path)}
    runtime=[put(name,{'syntheticSource':name},True) for name in RUNTIME]
    witness=put(BASE/'audit/runtime-closure.json',{'schema':'w50-numerical-runtime-closure-1','sources':runtime})
    guards=[]
    for name in ('runner.py','numerical_guard.py'):
        path=repo/BASE/'audit'/name; shutil.copyfile(original_g0/'audit'/name,path); guards.append(pin(path))
    originals=[]; candidates=[]; baselines=[]
    for position in (.25,.5):
        endpoints={}; base_endpoints={}
        for pose in ('active','receded'):
            for scheme in ('light','dark'):
                suffix='-receded' if pose=='receded' else ''
                profile=f'apple-macos-27.0-1x-{scheme}-standard-glass{position}{suffix}'
                original={'profileKey':profile,'patch':{'heldLeaf':3},'cssTierMapping':{'value':0}}
                originals.append(put(f'packages/calibration/profiles/{profile}.json',original))
                baseline={**original,'profileKey':profile.replace(f'glass{position}',f'glass{position:.3f}')}
                name=f'baseline/{position}-{pose}-{scheme}.json'; ep=put(name,baseline)
                base_endpoints[f'{pose}.{scheme}']={'path':Path(name).name,'sha256':ep['sha256']}
                patch={'heldLeaf':3}
                if scheme=='dark': patch.update(lowEndStrength=1,lowEnd44=[0,.1,.2,.3],
                                                lowEnd96=[0,.1,.2,.3],lowEnd160=[0,.1,.2,.3])
                name=f'candidate/{position}-{pose}-{scheme}.json'
                ep=put(name,{**baseline,'patch':patch},True)
                endpoints[f'{pose}.{scheme}']={'path':Path(name).name,'sha256':ep['sha256']}
        common={'kind':'vitrea-candidate-material-document','schemaVersion':1,'glassTintAmount':position,
                'cssTierMappingSha256':'0'*64}
        baselines.append(put(f'baseline/{position}.json',{**common,'endpoints':base_endpoints}))
        candidates.append({'position':position,**put(f'candidate/{position}.json',{**common,'endpoints':endpoints},True)})
    pixel=put('synthetic-pixel.json',{'synthetic':True})
    rows=[]; records=[]
    hashes=sorted(c['sha256'] for c in candidates)
    for c in candidates:
        position=c['position']
        for scale in (1,2):
            profile=f'apple-macos-27.0-{scale}x-dark-standard-glass{position}'
            for pose in ('active','receded'):
                scene=f'impulse__rrect-ml__{"rest" if pose=="active" else "inactive"}'
                identity=f'{profile}|webgpu|{scene}'
                record=dict(id=identity,profile=profile,renderer='webgpu',scene=scene,variant='regular',
                            position=position,pose=pose,dpr=scale,span=128,role='calibration',
                            candidateSha256=c['sha256'],encodedLuminance=.01,linearLuminance=.001,rgb=[.001]*3)
                evidence=put(f'evidence/{len(records)}.json',{'schema':'w50-measured-tone-argument-1',**record},True)
                records.append({**record,'evidence':evidence})
                rows.append(dict(profile=profile,renderer='webgpu',scene=scene,role='calibration'))
            for scene,role in [('blind','blind'),('history','historical-prediction-check')]:
                rows.append(dict(profile=profile,renderer='webgpu',scene=scene,role=role))
    for row in rows:
        row.update(statistic='T1-full-silhouette',support='silhouette',currentGeneration='g',
                   currentDocumentPair={'active':'a'},historical=[],B=None,status='UNMEASURED',
                   nativeEvidence=pixel,currentEvidence=pixel)
    refs=put(BASE/'references.json',{'schema':'w50-reference-inventory-1','cells':rows},True)
    manifest=put(BASE/'bed/manifest.json',{'cells':[]})
    required=sorted(r['id'] for r in records)
    arguments=put('arguments.json',{'schema':'w50-structured-arguments-1','candidateSha256s':hashes,
                  'references':refs,'requiredIds':required,'records':records},True)
    cohort=put('numerical-cohort.json',{'schema':'w50-numerical-cohort-1','candidates':candidates,
               'structuredArguments':arguments},True)
    report=dict(schema='w50-candidate-numerical-referee-1',status='PASS',producer=runtime[0],
                runtimeSources=runtime,cohort=cohort,argumentManifest=arguments,referenceInventory=refs,
                candidateDocuments=candidates,candidateSha256s=hashes,requiredStructuredArgumentIds=required,
                structuredArgumentIds=required,structuredArguments=[{k:r[k] for k in PROJECTION} for r in records],
                sources=list(all_pins.values()),domain={'inputCodeMin':0,'inputCodeMax':64,'stepCode':1/64,
                'spanMin':32,'spanMax':224,'scales':[1,2],'positions':[.25,.5],'poses':['active','receded']},
                samples=6325768,maxRunningDrawdownCode=0,minimumRequestedNeutral=0,fixedJoinPass=True,
                standDownPass=True,structuredArgumentPass=True,negativeRequests=[],
                structuredCoverage=sorted(f'{p}:{pose}:{s}' for p in (.25,.5) for pose in ('active','receded') for s in (1,2)))
    numerical=put('numerical-proof.json',report)
    sources=[refs,manifest,witness,*guards,*runtime,*originals]
    one=put(BASE/'declaration.json',{'sources':sources,'references':'references.json','native':{'manifest':'bed/manifest.json'}})
    domain={'strength':1,'endpoints':['active.dark.0.25','receded.dark.0.25','active.dark.0.5','receded.dark.0.5'],
            'rows':[44,96,160],'inputCodes':[0,8,28,40],'ordinateRange':[0,1]}
    two=put(BASE/'fit-declaration.json',{'sources':sources,'references':'references.json',
            'partOneSha256':one['sha256'],'requiredEvidence':list(proofs),'candidateDomain':domain})
    return dict(one=repo/one['path'],two=repo/two['path'],refs=repo/refs['path'],manifest=repo/manifest['path'],
                rows=rows,cohort=[{k:c[k] for k in ('path','sha256')} for c in candidates],baselines=baselines,
                numerical=numerical,pixel=repo/pixel['path'])
