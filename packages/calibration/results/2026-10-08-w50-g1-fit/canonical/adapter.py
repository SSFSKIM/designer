"""Dispatcher-bound canonical compare transport; CAPTURED is never a gate verdict.

Runs use sceneSource=canonical, explicit fresh external captureRoot/matrixPath, and
webSourceClosure pinned in root inputs. The dispatcher admits the complete numerical cohort
and owns one GPU lease before issuing its render capability. Current references use execute_current;
blind baselines are only captured beside their candidate in the claimed exposure.
The parent routing adapter may call capture_run with the ORIGINAL context and registered run.
No source/fixture override, publication, retry or process-control interface is exposed.
"""
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import subprocess
import sys

HERE = Path(__file__).resolve().parent
CAL = HERE.parents[2]
ROOT = CAL.parents[1]
WEB = HERE.parent/'web'
SCENES = ROOT/'apps/reference-apple/scenes.json'
PROFILE = re.compile(r'apple-macos-27\.0-([12])x-(light|dark)-(standard|reduced-transparency|increased-contrast-coupled)-glass(0\.25|0\.5)')


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read(path):
    def invalid(value): raise ValueError(f'Nonfinite JSON: {value}')
    return json.loads(Path(path).read_text(),parse_constant=invalid)


def write(path,value):
    with Path(path).open('x') as f:
        json.dump(value,f,indent=2,allow_nan=False); f.write('\n')


def load_source(path,name):
    m=importlib.util.module_from_spec(importlib.util.spec_from_file_location(name,path))
    exec(compile(path.read_bytes(),str(path),'exec'),m.__dict__)
    return m


def require(context):
    dispatcher=sys.modules.get('w50_g1_dispatch')
    if dispatcher is None: raise ValueError('Dispatcher capability required')
    dispatcher.require_context(context)
    if Path(context['repo']).resolve()!=ROOT: raise ValueError('Wrong repository')
    return dispatcher


def scene_plan(run,phase,document=None):
    m=PROFILE.fullmatch(run.get('profile',''))
    if run.get('sceneSource')!='canonical' or not m or run.get('renderer') not in ('webgpu','css'):
        raise ValueError('Unsupported canonical run')
    doc=read(SCENES) if document is None else document
    if doc['canvas']!={'width':320,'height':200}: raise ValueError('Wrong canonical canvas')
    profile=next((p for p in doc['profiles'] if p['key']==run['profile']),None)
    allowed={'calibration','validation','recorded','probe'}
    if phase in ('current','exposure'): allowed.add('holdout')
    ids=run.get('scenes',[])
    if not profile or not ids or len(ids)!=len(set(ids)) or not run.get('sets') or not set(run['sets'])<=allowed:
        raise ValueError('Invalid canonical membership or withheld set')
    planned=[]
    for sid in ids:
        scene=next((s for s in doc['scenes'] if s['id']==sid),None)
        roles=[k for k,v in doc['split'].items() if sid in v]
        if scene is None or (profile['scenes']!='all' and sid not in profile['scenes']) or len(roles)!=1 or roles[0] not in run['sets']:
            raise ValueError('Scene outside declared profile or split')
        planned.append({**scene,'fixtureSet':roles[0]})
    return dict(scenes=planned,dpr=int(m[1]),scheme=m[2],a11y=m[3],position=float(m[4]),
                canvas=doc['canvas'],tints=doc.get('tints',{}),components=doc['components'])


def capture_environment(root,closure,digest,captures,matrix,guard):
    env={k:v for k,v in os.environ.items() if not k.startswith(('VITREA_','W50_')) and k not in ('NODE_OPTIONS','NODE_PATH')}
    env.update(VITREA_SCENES=str(Path(root)/'apps/reference-apple/scenes.json'),
        VITREA_WEB_CAPTURES=str(captures),VITREA_MATRIX_PATH=str(matrix),
        W50_WEB_ROOT=str(root),W50_WEB_CLOSURE=str(closure),W50_WEB_CLOSURE_SHA256=digest,
        # compare spawns npx/tsx: inheritance is essential at that second Node boundary.
        NODE_OPTIONS='--import='+Path(guard).as_uri())
    return env


def validate_matrix(matrix,run,candidate):
    if matrix.get('schemaVersion')!=5: raise ValueError('Expected schema-5 measurement matrix')
    rows=matrix.get('cells',[])
    keys=[(r['key']['profileKey'],r['key']['web']['renderer'],r['key']['sceneId']) for r in rows]
    expected={(run['profile'],run['renderer'],s) for s in run['scenes']}
    if len(keys)!=len(expected) or set(keys)!=expected: raise ValueError('Measured membership differs from run')
    # Match capture-web.ts candidateLabel's exact relative-path spelling.
    shown=os.path.relpath(candidate,ROOT)
    if shown.startswith('..'): shown=str(candidate)
    stamp=f'candidateDocument={shown} declarationSha256={run["candidate"]["sha256"][:12]}'
    for row in rows:
        capture=row['key']['web'].get('capturePath','')
        if stamp not in capture or 'crossPosition=' in capture or row['fixtureSet'] not in run['sets']:
            raise ValueError('Candidate or split provenance differs')
    return rows


def validate_report(envelope,run,plan,scene,endpoint):
    p=envelope['page']
    pose='inactive' if scene['state']=='inactive' else 'active'
    policy=dict(reducedTransparency=plan['a11y']!='standard',
        increasedContrast=plan['a11y']=='increased-contrast-coupled',forcedColors=False)
    expected=dict(sceneId=scene['id'],materialMode='candidate',colorScheme=plan['scheme'],
        windowActivation=pose,requestedRenderer=run['renderer'],canvas=plan['canvas'],
        pixelSize=[320*plan['dpr'],200*plan['dpr']],devicePixelRatio=plan['dpr'],requestedScale=plan['dpr'],
        pressed=scene['state']=='pressed' or scene.get('interaction')=='pressed',transparentPage=False)
    if envelope.get('fallback') or envelope.get('problems') or p.get('problems') or any(p.get(k)!=v for k,v in expected.items()):
        raise ValueError('Wrong actual capture identity, pose or fallback')
    if any(p.get('accessibilityPolicy',{}).get(k) is not v for k,v in policy.items()):
        raise ValueError('Wrong actual accessibility policy')
    tint=plan['tints'].get(scene.get('tint'))
    expected_tint=None if tint is None else f'rgb({" ".join(str(v) for v in tint["srgb"])} / {tint.get("alpha",1)})'
    if p.get('tint')!=expected_tint: raise ValueError('Wrong actual author tint')
    stamp=p.get('candidateDocument') or {}
    if stamp.get('mode')!='candidate' or stamp.get('declarationSha256')!=run['candidate']['sha256'][:12]:
        raise ValueError('Wrong candidate stamp')
    groups=p.get('groups',[]); surfaces=p.get('surfaces',[])
    gids=[g['id'] for g in groups]
    component=plan['components'][scene['component']]
    expected_surfaces=(len(component['items']) if component['kind']=='group' else
                       2 if component['kind']=='stack' else 1)
    if (not groups or len(surfaces)!=expected_surfaces or len(gids)!=len(set(gids)) or
        len({s['nodeId'] for s in surfaces})!=len(surfaces) or
        {s['groupId'] for s in surfaces}!=set(gids)):
        raise ValueError('Missing/invalid drawn group population')
    for group in groups:
        state=group.get('state') or {}
        if state.get('activeRenderer')!=run['renderer'] or state.get('health')!='ok':
            raise ValueError('Wrong actual drawn tier or unhealthy group')
    for material in [p.get('material',{}),*(g['state'].get('materialDocument',{}) for g in groups)]:
        if (material.get('tuned') is not False or material.get('glassTintAmount')!=plan['position'] or
            any(material.get(k)!=endpoint[k] for k in ('profileKey','resolvedMaterialSha256'))):
            raise ValueError('Wrong actual endpoint, digest, position or tuning')


def capture_artifacts(folder,scene,tier,web,dpr):
    meta=folder/f'cell__{tier}.json'; report=folder/f'report__{tier}.json'
    png=folder/f'{scene["id"]}__{tier}.png'
    if read(meta)!=web or web.get('renderer')!=tier or web.get('colorSpace')!='srgb' or web.get('deterministic') is not True or web.get('repeatNoise')!=0:
        raise ValueError('Capture metadata differs, is unstable, or has wrong tier/colour space')
    with png.open('rb') as f: header=f.read(24)
    if header[:8]!=b'\x89PNG\r\n\x1a\n' or tuple(int.from_bytes(header[i:i+4],'big') for i in (16,20))!=(320*dpr,200*dpr):
        raise ValueError('Capture dimensions differ from canonical raster')
    artifacts={name:dict(path=str(p),sha256=sha(p)) for name,p in [('cell',meta),('report',report),('png',png)]}
    artifacts['files']=[dict(path=str(p),sha256=sha(p)) for p in sorted(folder.iterdir()) if p.is_file()]
    return artifacts


def source_probe():
    web=load_source(WEB/'adapter.py','w50_canonical_web_probe')
    census=load_source(CAL/'results/2026-10-02-w43-g3-refit/stage/census.py','w50_canonical_census_probe')
    if census.classify([])!={'refuse':[],'annotate':[]}: raise ValueError('Census probe failed')
    return dict(status='SOURCE_ONLY',candidateReader=callable(web.candidate_info))


def launch_cells(context,run,argv,env,captures):
    """One guarded compare capture per census; accumulate only in this run's fresh matrix."""
    census=load_source(CAL/'results/2026-10-02-w43-g3-refit/stage/census.py','w50_canonical_census')
    for scene in run['scenes']:
        require(context)
        observed=census.observe(); write(captures/f'census-{scene}.json',observed)
        if observed.get('passes') is not True: raise ValueError('Classifying census refused')
        command=list(argv); command[command.index('--scene')+1]=scene
        if '--receipt' in command:
            command[command.index('--receipt')+1]=str(captures/f'native-admission-{scene}.json')
        write(captures/f'request-{scene}.json',dict(argv=command))
        with (captures/f'compare-{scene}.log').open('x') as log:
            result=subprocess.run(command,cwd=CAL,env=env,stdout=log,stderr=subprocess.STDOUT)
        write(captures/f'exit-{scene}.json',dict(returncode=result.returncode))
        if result.returncode: raise ValueError('Compare failed; partial scratch evidence retained')


def validate_destinations(output,captures,matrix):
    output=Path(output).resolve()
    if (not captures.resolve().is_relative_to(output) or not matrix.resolve().is_relative_to(output) or
        captures.exists() or matrix.exists() or matrix.resolve().is_relative_to(captures.resolve()) or
        captures.resolve().is_relative_to(matrix.resolve())):
        raise ValueError('Fresh disjoint scratch paths inside claimed invocation required')


def native_request(context,run,dispatcher):
    # The root owns the original inventory; no caller-supplied replacement native pins.
    root=read(context['executionRoot'])
    inventory=read(dispatcher.checked(ROOT,root['references']))
    pins=[]
    for scene in run['scenes']:
        matching=[r for r in inventory['cells'] if (r['profile'],r['renderer'],r['scene'])==
                  (run['profile'],run['renderer'],scene)]
        evidence=[r.get('nativeEvidence') for r in matching]
        if not evidence or any(not p or p!=evidence[0] for p in evidence):
            raise ValueError('Missing or conflicting original selected native pins')
        p=evidence[0]
        # Do not hash or open PNGs here: the bounded Node preflight owns those selected reads.
        pins.append(dict(scene=scene,path=str((ROOT/p['path']).resolve()),sha256=p['sha256']))
    return dict(profile=run['profile'],scenes=run['scenes'],sets=run['sets'],native=pins)


def capture_run(context,run,*,current=False):
    dispatcher=require(context)
    dispatcher.require_render_admission(context,run,current=current)
    plan=scene_plan(run,context['phase'])
    web=load_source(WEB/'adapter.py','w50_canonical_web')
    candidate=web.candidate_info(run['candidate'],plan['position'],current=current)
    closure_pin=run['webSourceClosure']
    if closure_pin not in context['inputs']: raise ValueError('Unregistered Node/Vite closure')
    closure_path=dispatcher.checked(ROOT,closure_pin)
    closure=read(closure_path)
    pins={p['path']:p['sha256'] for p in closure['sources']}
    required=[SCENES,ROOT/'pnpm-lock.yaml',CAL/'package.json',CAL/'cli/compare.ts',CAL/'scripts/capture-web.ts',
              CAL/'web/vite.config.ts',WEB/'node-guard.mjs',WEB/'vite-guard.mjs',
              HERE/'compare.ts',HERE/'native-admission.ts']
    for p in required:
        if pins.get(str(p.relative_to(ROOT)))!=sha(p): raise ValueError(f'Missing closure input {p}')
    for p in closure['sources']: dispatcher.checked(ROOT,p)
    captures,matrix=web.external(run['captureRoot']),web.external(run['matrixPath'])
    validate_destinations(context['output'],captures,matrix)
    captures.mkdir(parents=True,exist_ok=False); matrix.parent.mkdir(parents=True,exist_ok=True)
    admission=captures/'native-request.json'
    write(admission,native_request(context,run,dispatcher))
    argv=['node','--import','tsx',str(HERE/'compare.ts'),'--admission',str(admission),
          '--receipt',str(captures/'native-admission.json'),'--','--profile',run['profile'],
          '--renderer',run['renderer'],'--candidate-document',candidate['path'],
          '--set',','.join(run['sets']),'--scene',','.join(run['scenes']),
          '--alpha','--write-partial','--out-matrix',str(matrix)]
    env=capture_environment(ROOT,closure_path,closure_pin['sha256'],captures,matrix,WEB/'node-guard.mjs')
    env['W50_NATIVE_REQUEST_SHA256']=sha(admission)
    write(captures/'request.json',dict(argv=argv,run=run,phase=context['phase'],lane='current' if current else 'candidate',
        contractSha256=sha(context['contract']),batchSha256=sha(context['batchPath']),scenesSha256=sha(SCENES)))
    launch_cells(context,run,argv,env,captures)
    require(context)
    for p in closure['sources']: dispatcher.checked(ROOT,p)
    web.candidate_info(run['candidate'],plan['position'],current=current)
    rows=validate_matrix(read(matrix),run,Path(candidate['path']))
    records=[]
    for row in rows:
        scene=next(s for s in plan['scenes'] if s['id']==row['key']['sceneId'])
        if row['fixtureSet']!=scene['fixtureSet']: raise ValueError('Scene split differs')
        folder=captures/run['profile']/scene['id']; tier=run['renderer']
        endpoint=candidate['endpoints'][f'{"receded" if scene["state"]=="inactive" else "active"}.{plan["scheme"]}']
        validate_report(read(folder/f'report__{tier}.json'),run,plan,scene,endpoint)
        artifacts=capture_artifacts(folder,scene,tier,row['key']['web'],plan['dpr'])
        artifacts['transport']=[dict(path=str(p),sha256=sha(p)) for p in (
            captures/f'census-{scene["id"]}.json',captures/f'request-{scene["id"]}.json',
            captures/f'exit-{scene["id"]}.json',captures/f'compare-{scene["id"]}.log',
            captures/'request.json',captures/'native-request.json',
            captures/f'native-admission-{scene["id"]}.json')]
        records.append(dict(profile=run['profile'],renderer=tier,scene=scene['id'],sceneSource='canonical',
            lane='current' if current else 'candidate',candidate=run['candidate'],endpoint=endpoint,
            matrix=dict(path=str(matrix),sha256=sha(matrix)),row=row,artifacts=artifacts,
            coherenceStatus=('NOT_APPLICABLE' if tier=='webgpu' else
                             'MEASURED' if row.get('coherence') is not None else 'UNMEASURED')))
    write(captures/'complete.json',dict(status='CAPTURED',captures=records,matrixSha256=sha(matrix)))
    return records


def baseline_run(run):
    return {**run,'candidate':run['baselineCandidate'],
            'captureRoot':str(Path(run['captureRoot'])/'baseline'),
            'matrixPath':str(Path(run['matrixPath']).with_name(Path(run['matrixPath']).stem+'-baseline.json'))}


def _execute(context,current):
    require(context)
    if current!=(context['phase']=='current'): raise ValueError('Wrong current/candidate lane')
    records=[]
    for run in context['batch']['runs']:
        records.extend(capture_run(context,run,current=current))
        if context['phase']=='exposure' and run.get('baselineCandidate') is not None:
            records.extend(capture_run(context,baseline_run(run),current=True))
    return dict(schema='w50-canonical-captures-1',status='CAPTURED',measurement='capture-completeness-only',
        candidateSha256s=sorted(p['sha256'] for p in context['batch']['cohort']),captures=records)


def execute(context): return _execute(context,False)
def execute_current(context): return _execute(context,True)
