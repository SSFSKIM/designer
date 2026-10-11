"""Prepare an unsealed W51 root from static scientific inputs and source-only discovery.

This never captures, judges, imports a historical root as execution authority, or writes a
source seal. Only W51-owned draft metadata is written. The coordinator seals after integration.
"""
import copy
import gzip
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import types

HERE=Path(__file__).resolve().parent
spec=types.ModuleType('w51_builder_root');spec.__file__=str(HERE/'root.py')
exec(compile((HERE/'root.py').read_bytes(),spec.__file__,'exec'),spec.__dict__)
R=spec;REPO=R.REPO;FIT=R.FIT;CURRENT=R.CURRENT
BUNDLE=HERE/'bundle'


def write(name,value):
    path=R.ordinary(BUNDLE/name);path.parent.mkdir(parents=True,exist_ok=True)
    path.write_bytes(R.encoded(value));return R.pin(path)


def nested_pins(value):
    if isinstance(value,dict):
        if isinstance(value.get('path'),str) and isinstance(value.get('sha256'),str):yield {'path':value['path'],'sha256':value['sha256']}
        else:
            for v in value.values():yield from nested_pins(v)
    elif isinstance(value,list):
        for v in value:yield from nested_pins(v)


def unique(pins):
    found={}
    for item in pins:
        key=json.dumps(item,sort_keys=True);found[key]=item
    return list(found.values())


def discover():
    script='''import json,runpy,sys\nfrom pathlib import Path\nrepo,here=map(Path,sys.argv[1:])\ng=runpy.run_path(str(here/'guard.py'))\nobserved=g['enforce'](repo,None)\nrunpy.run_path(str(here/'probe.py'),run_name='__main__')\nprint(json.dumps({'sources':dict(sorted(observed.items())),'environment':g['environment']()}))\n'''
    child=subprocess.run([sys.executable,'-I','-B','-c',script,str(REPO),str(HERE)],capture_output=True,text=True)
    if child.returncode:raise ValueError('Source-only discovery failed: '+child.stderr)
    return json.loads(child.stdout)


def file_pin(path):return {'path':str(Path(path).resolve()),'sha256':R.sha(path)}


def static_external(science,canonical,originals,fixture_configs):
    """Exact opened external reference files only; no historical current/gate capture walk."""
    pins=[];gate={tuple(k) for k in science['phaseDependencies']['gateKeys']}
    for row in originals['cells']:
        if tuple(row[k] for k in R.KEY) in gate and row.get('nativeEvidence'):
            pins.append(row['nativeEvidence'])
    for rows in canonical['partitions'].values():
        for row in rows:
            if tuple(row[k] for k in R.KEY) not in gate:continue
            pins.extend(row['pins'][k] for k in ('native','background','scenes','publishedManifest') if k in row['pins'])
            pins.extend(r['frame'] for r in row['runs'])
    native=R.load(R.checked(REPO,science['measurementConfig']))['native']
    batch=R.load(R.checked(REPO,native['batch']))
    for export in batch.get('exports',[]):
        if export['role'] not in ('calibration','validation'):raise ValueError('Blind export in static bundle')
        root=Path(export['root']);index_pin={'path':str(root/'index.json'),'sha256':export['indexSha256']}
        pins.append(index_pin)
        index=R.load(R.checked(REPO,index_pin))
        pins.append({'path':str(root/'index.sha256'),
                     'sha256':hashlib.sha256((export['indexSha256']+'  index.json\n').encode()).hexdigest()})
        pins.extend({'path':str(root/r['path']),'sha256':r['sha256']} for r in index['files'])
        report=json.loads(gzip.decompress(R.checked(REPO,native['reports'][export['role']]).read_bytes()))
        for cell in report['cells']:
            pins.extend({'path':str(root/r['evidence']['path']),'sha256':r['evidence']['sha256']} for r in cell['runs'])
        pins.extend({'path':str(root/d['evidence']['path']),'sha256':d['evidence']['sha256']} for d in report['dependencies'])
    newbed=R.load(R.checked(REPO,native['scenes']))
    scenes={s['id']:s for s in newbed['scenes']};needed={}
    for row in originals['cells']:
        if tuple(row[k] for k in R.KEY) not in gate or not row.get('nativeIdentity'):continue
        scene=scenes[row['scene']];pose='receded' if scene['state']=='inactive' else 'active'
        scale=2 if '-2x-' in row['profile'] else 1
        needed.setdefault((row['profile'],pose),set()).add(f'{scene["background"]}@{scale}x')
    for item in fixture_configs:
        keys=needed.get((item['profile'],item['pose']),set())
        if not keys:continue
        fixture=item['fixtures'];root=Path(fixture['path'])
        pins.append({'path':str(root/'manifest.json'),'sha256':fixture['manifestSha256']})
        pins.extend({'path':str(root/fixture['backgrounds'][k]['path']),
                     'sha256':fixture['backgrounds'][k]['sha256']} for k in sorted(keys))
    result=[]
    for item in unique(pins):
        path=R.checked(REPO,item)
        if not path.is_relative_to(REPO):result.append(file_pin(path))
    return unique(result)


def phases(rows):
    withheld={(r['profile'],r['scene']) for r in rows if r['role'] in ('blind','historical-prediction-check')}
    key=lambda r:[r[k] for k in R.KEY]
    groups=[]
    for profile,scene in sorted(withheld):
        selected=[r for r in rows if (r['profile'],r['scene'])==(profile,scene)]
        groups.append({'profile':profile,'scene':scene,'keys':[key(r) for r in selected],
            'withheldKeys':[key(r) for r in selected if r['role'] in ('blind','historical-prediction-check')],
            'deferredKeys':[key(r) for r in selected if r['role'] not in ('blind','historical-prediction-check')]})
    return {'schema':'w50-phase-dependencies-1','groups':groups,
        'gateKeys':[key(r) for r in rows if (r['profile'],r['scene']) not in withheld],
        'exposureKeys':[key(r) for r in rows if (r['profile'],r['scene']) in withheld],
        'pendingOwnerKeys':[key(r) for r in rows if (r['profile'],r['scene']) in withheld and r['statistic']=='owner-contracts'
                            and r['role'] not in ('blind','historical-prediction-check')],
        'ownerUnionKeys':[key(r) for r in rows if r['statistic']=='owner-contracts']}


def run_batches(science,population,cohort,numerical,templates,canonical_closure,newbed_closure,native_manifest):
    canonical=R.load(R.checked(REPO,science['scenes']))
    newbed=R.load(R.checked(REPO,R.load(R.checked(REPO,science['measurementConfig']))['native']['scenes']))
    docs={'canonical':canonical,'w50':newbed}
    by={n:{s['id']:s for s in d['scenes']} for n,d in docs.items()
        if n=='canonical' or d['canvas']=={'width':512,'height':384}}
    groups={}
    for p,t,s in population['physicalCells']:
        choices=[n for n,rows in by.items() if s in rows]
        if len(choices)!=1:raise ValueError('Scene belongs to ambiguous dataset sources')
        name=choices[0];pose='inactive' if by[name][s]['state']=='inactive' else 'rest'
        groups.setdefault((name,p,t,pose if name=='w50' else ''),[]).append(s)
    runs=[]
    for (name,p,t,pose),scenes in sorted(groups.items()):
        position=float(p.rsplit('glass',1)[1]);candidate=cohort[position]
        roles=[k for k,v in docs[name]['split'].items() if not k.startswith('$') and set(scenes)&set(v)]
        run={'id':f'run-{len(runs):03d}','profile':p,'renderer':t,'sceneSource':name,'scenes':sorted(scenes),
             'sets':roles,'candidate':candidate,'numericalReferee':numerical,
             'webSourceClosure':canonical_closure if name=='canonical' else newbed_closure}
        if name=='canonical':run.update(scenesDocument=science['scenes'],nativeManifest=native_manifest)
        else:
            choices=[r for r in templates if r['sceneSource']=='w50' and r['profile']==p and
                     ('inactive' if r['scenes'][0].endswith('__inactive') else 'rest')==pose]
            if not choices:raise ValueError('Missing fixed new-bed fixture template')
            run['fixtures']=copy.deepcopy(choices[0]['fixtures'])
        runs.append(run)
    return {'schema':'w50-g1-batch-1','phase':'gate','cohort':list(cohort.values()),'runs':runs}


def node_closure(original,scenes):
    value=copy.deepcopy(R.load(R.checked(REPO,original)))
    pins=list(value['sources'])
    pins.extend([R.pin(HERE/'canonical/compare.ts'),R.pin(HERE/'canonical/native-admission.ts'),
                 R.pin(HERE/'web/capture-web.ts'),R.pin(HERE/'render-admission.mjs'),scenes])
    # Node/Vite indexes source paths relative to its repository root, even when a dataset
    # preserves an absolute historical/reference pin for the same bytes.
    value['sources']=unique(R.pin(R.checked(REPO,p)) for p in pins)
    return value


def build(output):
    global BUNDLE
    output=Path(output).absolute()
    BUNDLE=HERE/'bundle'/output.stem
    if not output.is_relative_to(HERE) or output.resolve()!=output:raise ValueError('Draft root must remain W51-owned')
    if Path(str(output)+'.sha256').exists() or (output.parent/'execution-slots/gate.json').exists():
        raise ValueError('A sealed or used root cannot be rebuilt')
    declaration=HERE/'declaration-v2';frozen=R.load(declaration/'inputs.json')
    original=R.load(R.checked(REPO,frozen['sourceRootProvenance']))
    # The old root contributes static field values only; no old admission module is invoked.
    fields=('partOne','partTwo','references','manifest','candidateDomain','phaseDependencies','reportedKeys',
            'emptySupportKeys','ownerBudgetKeys','ownerContracts','currentComposition','baselineDocuments','newBedHost')
    real={k:copy.deepcopy(original[k]) for k in fields};real.update(repo=str(REPO),dataOrigin='measured-native')
    restored={}
    for item in frozen['restorableLiveInputs']:
        compressed=R.checked(REPO,item['committedArchive']).read_bytes();raw=gzip.decompress(compressed)
        if hashlib.sha256(raw).hexdigest()!=item['decompressedSha256']:raise ValueError('Static archive differs')
        # The bundle preserves archive bytes and restores the byte-identical JSON on read.
        # This avoids publishing hundreds of megabytes of redundant decompressed evidence.
        dest=R.ordinary(BUNDLE/'real'/(Path(item['required']['path']).name+'.gz'))
        dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(compressed)
        restored[Path(item['required']['path']).name]=R.pin(dest)
    measurement=R.load(FIT/'live-roles/measurement-config.json')
    measurement['completedReferences']=restored['completed-references-r3.json']
    measurement['completedCurrentEvidence']=restored['completed-current.json']
    real['currentEvidence']=measurement['completedCurrentEvidence']
    real['scenes']=R.pin(REPO/'apps/reference-apple/scenes.json')
    real['measurementConfig']=write('real/measurement-config.json',measurement)
    synthetic=HERE/'synthetic/generated';fixture=R.load(synthetic/'fixture.json')
    synthetic_pins=list(nested_pins(fixture.get('files',{})))
    for item in synthetic_pins:R.checked(REPO,item)
    synth={k:copy.deepcopy(real[k]) for k in ('partOne','partTwo','candidateDomain','ownerContracts','baselineDocuments','newBedHost')}
    synth.update(repo=str(REPO),dataOrigin='synthetic',references=file_pin(synthetic/'inventory.json'),
        manifest=file_pin(synthetic/'native-manifest.json'),scenes=file_pin(synthetic/'scenes.json'),
        currentComposition=file_pin(synthetic/'current-composition.json'),currentEvidence=file_pin(synthetic/'completed-current-evidence.json'),
        reportedKeys=[],emptySupportKeys=[],ownerBudgetKeys=[])
    synth['phaseDependencies']=phases(R.load(synthetic/'inventory.json')['cells'])
    current=R.load(synthetic/'completed-current-evidence.json')
    sm={'schema':'w50-phase-measurement-inputs-1','completedReferences':R.pin(synthetic/'completed-references.json'),
        'completedCurrentEvidence':synth['currentEvidence'],'canonicalReferenceEvidence':R.pin(synthetic/'canonical-reference-evidence.json'),
        'native':{'batch':current['native']['batch'],'scenes':current['originals']['scenes'],'reports':current['native']['reports']}}
    synth['measurementConfig']=write('synthetic/measurement-config.json',sm)
    imported_fit=R.pin(declaration/'inputs.json')
    cohort={m['position']:R.pin(R.checked(REPO,m['declaration'])) for m in frozen['candidate']['cohort']}
    fit_batch=R.load(R.checked(REPO,frozen['fitEvidence']['batch']));templates=fit_batch['runs']
    numerical=templates[0]['numericalReferee']
    numerical_inventory=R.load(R.checked(REPO,numerical))['referenceInventory']
    R.checked(REPO,numerical_inventory)
    transports={n:next(r['webSourceClosure'] for r in templates if r['sceneSource']==n) for n in ('w50','canonical')}
    captures=write('capture-config.json',{'schema':'w50-live-capture-config-1','transports':{
        'w50':R.pin(HERE/'web/adapter.py'),'canonical':R.pin(HERE/'canonical/adapter.py')}})
    all_inputs=[R.pin(HERE/'charter-seal-dl5.json'),imported_fit,*frozen['staticInputs'],
                *[p for m in frozen['candidate']['cohort'] for p in [m['declaration'],*m['documents'].values()]],
                *[R.pin(p) for p in HERE.glob('*.py') if not p.name.startswith('test_')]]
    static=R.source(HERE/'static.py','w51_build_static')
    prefit_pins,_=static.prefit_canonical_authority(
        {'repo':str(REPO),'importedFit':imported_fit,'charter':R.pin(HERE/'charter-seal-dl5.json')})
    all_inputs.extend(prefit_pins)
    charter=R.load(R.checked(REPO,R.pin(HERE/'charter-seal-dl5.json')))
    all_inputs.extend(charter['artifacts'])
    datasets={};batches={};populations={
        'real-rehearsal':{'dataset':'real','manifest':R.pin(declaration/'rehearsal-population.json')},
        'synthetic-rehearsal':{'dataset':'synthetic','manifest':R.pin(synthetic/'population.json')},
        'gate':{'dataset':'real','manifest':R.pin(declaration/'gate-population.json')}}
    closure=discover()
    base_inputs=list(all_inputs)
    for name,science,mconfig in (('real',real,measurement),('synthetic',synth,sm)):
        science['closure']=closure
        science['landingPolicy']=charter['landingPolicies'][name]
        policy=R.load(R.checked(REPO,science['landingPolicy']))
        if policy['dataOrigin']!=science['dataOrigin']:
            raise ValueError('Sealed landing policy belongs to another dataset')
        science['numericalInventory']=numerical_inventory
        reference=R.load(R.checked(REPO,science['references']))
        cbytes=R.checked(REPO,mconfig['canonicalReferenceEvidence']).read_bytes()
        canonical=json.loads(gzip.decompress(cbytes) if cbytes.startswith(b'\x1f\x8b') else cbytes)
        repeat=copy.deepcopy(R.load(CURRENT/'inputs/repeat-config.json'))
        repeat['references']=science['references'];repeat['native']=copy.deepcopy(mconfig['native'])
        repeat['canonical']=write(name+'/canonical-repeat.json',{'referenceEvidence':mconfig['canonicalReferenceEvidence'],
                                                               'scenes':science['scenes']})
        repeat_pin=write(name+'/repeat-config.json',repeat)
        science['repeatAdmission']={'entrypoint':R.pin(HERE/'repeat.py'),'config':repeat_pin}
        science['preFitEvidence']=write(name+'/imported-reference-binding.json',
            {'schema':'w51-imported-reference-binding-1','references':mconfig['completedReferences'],'importedFit':imported_fit})
        judge=copy.deepcopy(R.load(FIT/'judge/config.json'))
        if name=='synthetic':
            judge.update(references=science['references'],targets=R.pin(synthetic/'targets-config.json'))
            binding={'original':science['references'],'reportedKeys':[],'emptySupportKeys':[],
                     'ownerContracts':science['ownerContracts']}
            judge['binding']=write(name+'/reference-binding.json',binding)
        judge['landingPolicy']=science['landingPolicy']
        judge_pin=write(name+'/judge-config.json',judge)
        science['instruments']={role:{'entrypoint':R.pin(HERE/(role+'.py')),'config':config}
            for role,config in (('capture',captures),('measurement',science['measurementConfig']),('judge',judge_pin))}
        canonical_closure=write(name+'/canonical-web-closure.json',node_closure(transports['canonical'],science['scenes']))
        newbed_closure=write(name+'/newbed-web-closure.json',node_closure(transports['w50'],mconfig['native']['scenes']))
        native_manifest=next(r['nativeManifest'] for r in templates if r['sceneSource']=='canonical') if name=='real' else file_pin(synthetic/'native-fixtures/manifest.json')
        for population,binding in populations.items():
            if binding['dataset']!=name:continue
            batch=run_batches(science,R.load(R.checked(REPO,binding['manifest'])),cohort,numerical,templates,
                              canonical_closure,newbed_closure,native_manifest)
            batches[population]=write(name+'/'+population+'-batch.json',batch)
        fixtures=R.load(FIT/'inputs/current-fixtures.json')['configurations'] if name=='real' else []
        science['externalInputs']=static_external(science,canonical,reference,fixtures)
        pins=[*base_inputs,*nested_pins(science),*nested_pins(mconfig),*nested_pins(judge),
              *nested_pins(repeat),*policy['sources'],policy['completePopulation'],
              canonical_closure,newbed_closure,native_manifest,science['externalInputs']]
        pins=unique(p for group in pins for p in (group if isinstance(group,list) else [group]))
        # Every direct config's transitive pin is data, not permission to run its historical sources.
        targets=R.load(R.checked(REPO,judge['targets']));pins.extend(nested_pins(targets))
        pins.extend(R.pin(p) for p in (synthetic.rglob('*') if name=='synthetic' else []) if p.is_file())
        science['inputs']=unique(pins)
        for item in science['inputs']:R.checked(REPO,item)
        datasets[name]=write(name+'/dataset.json',science)
        all_inputs.extend(science['inputs']);all_inputs.append(datasets[name])
    differential=write('source-differential.json',R.source(HERE/'semantics.py','w51_build_differential').verify())
    all_inputs.append(differential)
    doc={'schema':'w51-execution-root-1','repo':str(REPO),'rootPath':str(output),'closure':closure,
        'sourceDifferential':differential,'syntheticFixture':R.pin(synthetic/'fixture.json'),
        'charter':R.pin(HERE/'charter-seal-dl5.json'),'importedFit':imported_fit,'cohort':list(cohort.values()),
        'partOne':real['partOne'],'partTwo':real['partTwo'],'candidateDomain':real['candidateDomain'],
        'numerical':numerical,'numericalInventory':numerical_inventory,'datasets':datasets,'populations':populations,'batches':batches,
        'protectedRoots':['/Users/new/vitrea-w50','/Users/new/vitrea-w29-27-run',
            '/Users/new/.cache/vitrea-archives','/Users/new/Developer/GitHub/designer/apps/reference-apple/fixtures'],
        'inputs':unique([*all_inputs,*batches.values(),*[p['manifest'] for p in populations.values()]])}
    output.parent.mkdir(parents=True,exist_ok=True);output.write_bytes(R.encoded(doc))
    print('W51 draft prepared; source-only closure '+str(len(closure['sources']))+' files; no seal or capture.')
    return doc
