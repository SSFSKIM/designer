"""W50 capture adapter API v1; imported only by the prospective G1 dispatcher.

execute(context) captures admitted candidates; execute_current(context) captures complete
current-material documents at gate zero, with only the candidate profileKey namespace changed. Neither is a numerical referee or a landing verdict.
The production driver supplies scene placement, candidate assembly, and actual tone reports.
No independent raster generator or screenshot-average surrogate is used here.
"""
import hashlib
import importlib.util
import json
import math
import os
from pathlib import Path
import re
import subprocess
import sys

HERE = Path(__file__).resolve().parent
CAL = HERE.parents[2]
ROOT = CAL.parents[1]
G0 = CAL / 'results/2026-10-08-w50-g0-declaration'
PROFILE = re.compile(r'apple-macos-27\.0-([12])x-dark-standard-glass(0\.25|0\.5)')
HASH = re.compile(r'[a-f0-9]{64}')


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read_json(path):
    return json.loads(Path(path).read_text())


def write_new(path, value):
    with Path(path).open('x') as stream:
        stream.write(json.dumps(value, indent=2, allow_nan=False) + '\n')


def pin_file(pin, base=ROOT):
    path = (base / pin['path']).resolve()
    if not HASH.fullmatch(pin['sha256']) or sha(path) != pin['sha256']:
        raise ValueError(f'Changed pinned file: {path}')
    return path


def external(path):
    path = Path(path)
    resolved = path.resolve()
    if (not path.is_absolute() or resolved.is_relative_to(ROOT) or
        any((parent/'.git').exists() for parent in (resolved,*resolved.parents))):
        raise ValueError('Explicit scratch path outside every checkout required')
    return resolved


def scene_plan(run, phase='fit'):
    match = PROFILE.fullmatch(run.get('profile', ''))
    if not match or run.get('renderer') not in ('webgpu', 'css'):
        raise ValueError('Unsupported dark profile or renderer')
    source = run.get('sceneSource')
    if source != 'w50':
        raise ValueError('DL5f replacement adapter admits W50 NEWBED only; canonical keeps its original adapter')
    path = G0/'bed/scenes-w50.json' if source == 'w50' else ROOT/'apps/reference-apple/scenes.json'
    doc = read_json(path)
    expected = {'width':512, 'height':384} if source == 'w50' else {'width':320, 'height':200}
    if doc['canvas'] != expected:
        raise ValueError('Scene canvas changed')
    scenes = run.get('scenes', [])
    if not scenes or len(set(scenes)) != len(scenes):
        raise ValueError('Empty/duplicate scene batch')
    allowed = {'calibration', 'validation', 'recorded', 'probe'}
    if phase == 'exposure' or (phase == 'current' and source == 'canonical'):
        allowed.add('holdout')
    if not run.get('sets') or not set(run['sets']) <= allowed:
        raise ValueError('Withheld or unknown set outside exposure')
    by_id = {s['id']:s for s in doc['scenes']}
    planned = []
    for sid in scenes:
        s = by_id.get(sid)
        roles = [key for key, ids in doc['split'].items() if sid in ids]
        if s is None or len(roles) != 1 or roles[0] not in run['sets']:
            raise ValueError(f'Unknown or wrong-set scene: {sid}')
        if s['state'] not in ('rest', 'inactive'):
            raise ValueError('Only declared rest/inactive low-end scenes are admitted')
        c = doc['components'][s['component']]
        # This instrument reads single-surface response inputs. Composite canonical cells
        # need their own per-surface identity declaration, not an arbitrary first surface.
        if c['kind'] not in ('capsule', 'rrect'):
            raise ValueError('Only single capsule/rrect cells are admitted')
        w, h = c['size']
        planned.append(dict(scene=sid, role=roles[0], background=s['background'],
            component=c, span=min(w,h), pose='receded' if s['state']=='inactive' else 'active',
            geometry=dict(x=(expected['width']-w)/2,y=(expected['height']-h)/2,width=w,height=h)))
    return dict(source=source, scenesPath=str(path), scenesSha256=sha(path), canvas=expected,
                dpr=int(match[1]), position=float(match[2]), scenes=planned)


def encode(linear):
    return 12.92*linear if linear <= .0031308 else 1.055*linear**(1/2.4)-.055


def unit(value):
    return type(value) in (int,float) and math.isfinite(value) and 0 <= value <= 1


def validate_report(envelope, run, endpoint, *, abscissa='silhouette', phase='fit'):
    """Read the actual solve input, refusing hints, fallbacks and missing reductions.

    Source-mode level is already decode(mean(encoded luma)), not mean(linear luma).
    Encoding that recorded scalar recovers the solve's encoded argument; the independent
    linear mean and RGB are kept verbatim. Silhouette mode reads all three GPU/CPU lanes.
    """
    plan = scene_plan(run, phase)
    p = envelope['page']
    spec = next((s for s in plan['scenes'] if s['scene']==p.get('sceneId')), None)
    if spec is None: raise ValueError('Report outside immutable run')
    if envelope.get('fallback') or envelope.get('problems') or p.get('problems'):
        raise ValueError('Capture fallback/problems are not admitted')
    pixels = [plan['canvas']['width']*plan['dpr'],plan['canvas']['height']*plan['dpr']]
    if (p.get('canvas') != plan['canvas'] or p.get('pixelSize') != pixels or
        p.get('devicePixelRatio') != plan['dpr'] or p.get('requestedScale') != plan['dpr'] or
        p.get('requestedRenderer') != run['renderer'] or p.get('colorScheme') != 'dark' or
        p.get('materialMode') != 'candidate' or
        p.get('windowActivation') != ('inactive' if spec['pose']=='receded' else 'active')):
        raise ValueError('Wrong canvas, scale, candidate mode, renderer or pose')
    stamp = p.get('candidateDocument') or {}
    if stamp.get('mode') != 'candidate' or stamp.get('declarationSha256') != run['candidate']['sha256'][:12]:
        raise ValueError('Wrong candidate bytes in page')
    if p.get('requestedBackdropLevel') is not None or p.get('requestedBackdropMode') != 'texture':
        raise ValueError('Author-hinted or DOM-probed tone is not the declared measured argument')
    policy = p.get('accessibilityPolicy',{})
    if any(policy.get(key) is not False for key in ('reducedTransparency','increasedContrast','forcedColors')):
        raise ValueError('Actual accessibility policy differs from the standard profile')
    background = p.get('background', {})
    if (background.get('id') != spec['background'] or
        [background.get('naturalWidth'),background.get('naturalHeight')] != pixels):
        raise ValueError('Wrong backdrop raster/dimensions')
    groups, surfaces = p.get('groups', []), p.get('surfaces', [])
    if len(groups)!=1 or len(surfaces)!=1 or surfaces[0].get('bounds') != spec['geometry']:
        raise ValueError('Wrong surface population or actual placement')
    g, surface = groups[0], surfaces[0]
    shape = spec['component']
    family = 'capsule' if shape['kind']=='capsule' else 'fixed-rounded-rect'
    radius = spec['span']/2 if shape['kind']=='capsule' else shape['radius']
    if surface.get('family') != family or surface.get('radius') != radius:
        raise ValueError('Wrong declared shape family or corner radius')
    state = g.get('state') or {}
    if surface['groupId'] != g['id'] or state.get('activeRenderer') != run['renderer'] or state.get('health') != 'ok':
        raise ValueError('Wrong actual drawn group')
    if state.get('samplingBackend') != ('gpu-texture' if run['renderer']=='webgpu' else 'css-backdrop'):
        raise ValueError('Wrong actual sampling backend')
    for material in (p.get('material') or {}, state.get('materialDocument') or {}):
        if (material.get('tuned') is not False or material.get('glassTintAmount') != plan['position'] or
            material.get('profileKey') != endpoint['profileKey'] or
            material.get('resolvedMaterialSha256') != endpoint['resolvedMaterialSha256']):
            raise ValueError('Wrong drawn endpoint, digest, position or tuned state')
    if abscissa == 'silhouette':
        readings = state.get('backdropToneAbscissae', [])
        if len(readings)!=1 or readings[0].get('surfaceId') != surface['nodeId']:
            raise ValueError('UNMEASURED: missing actual surface argument')
        a = readings[0]
        if a.get('kind')!='silhouette' or not a.get('sampleCount',0)>0:
            raise ValueError('UNMEASURED: hint or empty reduction')
        e, y, rgb = a['encodedLuminance'],a['linearLuminance'],a['color']
        provenance = dict(a)
    elif abscissa == 'source':
        a = g.get('backdropTone')
        if not a or not unit(a.get('level')):
            raise ValueError('UNMEASURED: no source solve argument')
        e,y,rgb = encode(a['level']),a['linearLuminance'],a['rgb']
        provenance = dict(kind='source',level=a['level'],operation='srgb_encode(recorded decoded encoded-mean level)')
    else:
        raise ValueError('Unregistered abscissa mode')
    if not unit(e) or not unit(y) or not isinstance(rgb,list) or len(rgb)!=3 or not all(unit(v) for v in rgb):
        raise ValueError('Nonfinite or out-of-domain actual argument')
    luma = sum(c*w for c,w in zip(rgb,(.2126,.7152,.0722)))
    u=2**-24
    if abs(luma-y) > 8*u/(1-8*u)*max(*rgb,y)+8*2**-149:
        raise ValueError('Independent linear mean/RGB disagree')
    return [dict(id=f'{run["profile"]}|{run["renderer"]}|{spec["scene"]}',
        profile=run['profile'],renderer=run['renderer'],scene=spec['scene'],variant='regular',
        pose=spec['pose'],position=plan['position'],dpr=plan['dpr'],span=spec['span'],role=spec['role'],
        candidateSha256=run['candidate']['sha256'],encodedLuminance=e,linearLuminance=y,rgb=rgb,
        provenance=provenance)]


def _require(context, phase):
    dispatcher = sys.modules.get('w50_g1_dispatch')
    if dispatcher is None:
        raise ValueError('Only a registered dispatcher context may invoke this adapter')
    dispatcher.require_context(context)
    if context['phase'] not in phase:
        raise ValueError('Wrong execution lane')


def execute(context):
    _require(context, ('fit','gate','exposure'))
    return _capture(context, current=False)


def execute_current(context):
    _require(context, ('current',))
    return _capture(context, current=True)


def validate_current_endpoint(value, source, position):
    wanted = source['profileKey'].replace(f'glass{position:g}',f'glass{position:.3f}')
    if (value.get('profileKey') != wanted or value != {**source,'profileKey':wanted} or
        value.get('patch',{}).get('lowEndStrength',0) != 0):
        raise ValueError('Current material permits only numeric-equivalent candidate profileKey')


def candidate_info(pin, position, *, current=False):
    path = pin_file(pin)
    doc = read_json(path)
    slots = {f'{pose}.{scheme}' for pose in ('active','receded') for scheme in ('light','dark')}
    if (doc.get('kind') != 'vitrea-candidate-material-document' or doc.get('schemaVersion') != 1 or
        doc.get('glassTintAmount') != position or set(doc.get('endpoints',{})) != slots or
        not HASH.fullmatch(doc.get('cssTierMappingSha256',''))):
        raise ValueError('Incomplete or wrong-position candidate document')
    endpoints = {}
    for slot in sorted(slots):
        endpoint = pin_file(doc['endpoints'][slot],path.parent)
        value = read_json(endpoint)
        if not value.get('profileKey') or not re.fullmatch('[a-f0-9]{16}',value.get('resolvedMaterialSha256','')):
            raise ValueError('Endpoint lacks profile/digest provenance')
        pose,scheme = slot.split('.')
        if current:
            shipped = CAL/f'profiles/apple-macos-27.0-1x-{scheme}-standard-glass{position:g}{"-receded" if pose=="receded" else ""}.json'
            validate_current_endpoint(value,read_json(shipped),position)
        endpoints[slot] = dict(path=str(endpoint),sha256=sha(endpoint),
            profileKey=value['profileKey'],resolvedMaterialSha256=value['resolvedMaterialSha256'],
            patch=value.get('patch',{}))
        if current:
            endpoints[slot]['currentSource'] = dict(path=str(shipped),sha256=sha(shipped))
    # Driver readCandidateDocument independently assembles and checks all four endpoint
    # digests and CSS mapping BEFORE opening Chromium. This is not a parallel digest codec.
    return dict(path=str(path),sha256=sha(path),endpoints=endpoints)


def fixture_info(run, plan):
    fixture = run['fixtures']
    root = external(fixture['path'])
    manifest = pin_file(dict(path=str(root/'manifest.json'),sha256=fixture['manifestSha256']))
    index = read_json(manifest).get('backgrounds',{})
    selected = []
    for scene in plan['scenes']:
        key = f'{scene["background"]}@{plan["dpr"]}x'
        pin = fixture['backgrounds'].get(key)
        if pin is None or index.get(key) != pin['path']:
            raise ValueError('Missing explicit same-scale pinned backdrop (no unscaled fallback)')
        path = pin_file(pin,root)
        if not path.is_relative_to(root): raise ValueError('Backdrop escapes fixture tree')
        selected.append(dict(key=key,path=str(path),sha256=pin['sha256']))
    return dict(path=str(root),manifestSha256=sha(manifest),backgrounds=selected)


def load_source(path, name):
    module = importlib.util.module_from_spec(importlib.util.spec_from_file_location(name,path))
    exec(compile(path.read_bytes(),str(path),'exec'),module.__dict__)
    return module


def source_probe():
    """Exercise source-only planning and all Python imports for the prospective seal.

    Loading the observer is not observing the machine: only classify() is exercised on
    synthetic rows. The parent probe combines this closure with fitting/statistical imports.
    """
    census = load_source(CAL/'results/2026-10-02-w43-g3-refit/stage/census.py','w50_web_census')
    if census.classify([]) != {'refuse':[],'annotate':[]}:
        raise ValueError('Unexpected empty census classification')
    plan = scene_plan(dict(profile='apple-macos-27.0-1x-dark-standard-glass0.25',
        renderer='css',sceneSource='w50',scenes=['cell-grey-004-s096__rest'],sets=['calibration']))
    return dict(status='SOURCE_ONLY',canvas=plan['canvas'])


def _capture(context, *, current):
    if Path(context['repo']).resolve() != ROOT:
        raise ValueError('Dispatcher repository differs from adapter repository')
    runs = context['batch']['runs']
    if len({run['sceneSource'] for run in runs}) != 1:
        raise ValueError('Canonical and W50 canvases require separate immutable batches')
    captures = []
    for run in runs:
        captures.extend(_capture_run(context,run,current=current))
        if context['phase']=='exposure' and run.get('baselineCandidate') is not None:
            if run['baselineCandidate'] not in context['baselineDocuments']:
                raise ValueError('Exposure baseline not registered at root')
            baseline = {**run,'candidate':run['baselineCandidate'],
                        'captureRoot':str(Path(run['captureRoot'])/'baseline'),
                        'matrixPath':str(Path(run['matrixPath']).with_name(Path(run['matrixPath']).stem+'-baseline.json'))}
            captures.extend(_capture_run(context,baseline,current=True))
    return dict(schema='w50-web-captures-1',status='CAPTURED',measurement='capture-completeness-only',phase=context['phase'],
                candidateSha256s=sorted({r['candidate']['sha256'] for r in runs}),captures=captures)


def capture_environment(environ):
    """Compiler selectors cannot bypass the pinned import graph through inherited state."""
    return {k:v for k,v in environ.items()
        if not k.startswith(('VITREA_','W50_','ESBUILD_','TSX_'))
        and k not in ('NODE_OPTIONS','NODE_PATH')}


def _capture_run(context, run, *, current):
    _require(context, ('current','fit','gate','exposure'))
    # The dispatcher owns the complete-cohort numerical admission and one GPU lease;
    # a baseline derivative is authorised there without opening a second exposure.
    sys.modules['w50_g1_dispatch'].require_render_admission(context,run,current=current)
    plan = scene_plan(run,context['phase'])
    candidate = candidate_info(run['candidate'],plan['position'],current=current)
    fixture = fixture_info(run,plan)
    closure_pin = run['webSourceClosure']
    if closure_pin not in context['inputs']:
        raise ValueError('Node/Vite source closure is not a prospective root input')
    closure_path = pin_file(closure_pin)
    closure = read_json(closure_path)
    for pin in closure['sources']: pin_file(pin)
    source_pins = {p['path']:p['sha256'] for p in closure['sources']}
    required = [Path(plan['scenesPath']),ROOT/'pnpm-lock.yaml',
        CAL/'scripts/capture-web.ts',CAL/'web/vite.config.ts',HERE/'node-guard.mjs',HERE/'vite-guard.mjs',HERE/'host.mjs']
    for path in required:
        if source_pins.get(str(path.relative_to(ROOT))) != sha(path):
            raise ValueError(f'Capture source absent from Node/Vite closure: {path}')
    output, matrix = external(run['captureRoot']), external(run['matrixPath'])
    if output.exists() or matrix.exists():
        raise ValueError('Capture root and scratch manifest are write-once')
    output.mkdir(parents=True)
    matrix.parent.mkdir(parents=True,exist_ok=True)
    census = load_source(CAL/'results/2026-10-02-w43-g3-refit/stage/census.py','w50_web_census')
    records = []
    for spec in plan['scenes']:
        scene = spec['scene']
        observed = census.observe()
        # A per-cell census is before the driver, which owns/tears down its own browser.
        write_new(output/f'census-{scene}.json',observed)
        if observed.get('passes') is not True:
            raise ValueError(f'Classifying census refused: {observed.get("refusals")}')
        slot = f'{spec["pose"]}.dark'
        endpoint = candidate['endpoints'][slot]
        active = candidate['endpoints']['active.dark']['patch']
        resolved_abscissa = {**active,**endpoint['patch']}.get('backdropToneAbscissa','source')
        abscissa = 'silhouette' if isinstance(resolved_abscissa,dict) else resolved_abscissa
        env = capture_environment(os.environ)
        env.update(VITREA_SCENES=plan['scenesPath'],VITREA_FIXTURES=fixture['path'],
            VITREA_WEB_CAPTURES=str(output),VITREA_MATRIX_PATH=str(matrix),
            W50_WEB_ROOT=str(ROOT),W50_WEB_CLOSURE=str(closure_path),
            W50_WEB_CLOSURE_SHA256=closure_pin['sha256'])
        argv = ['node','--import','tsx','--import',str(HERE/'node-guard.mjs'),
            str(CAL/'scripts/capture-web.ts'),'--renderer',run['renderer'],'--scale',str(plan['dpr']),
            '--color-scheme','dark','--frames','32','--candidate-document',candidate['path'],
            '--out',str(output),scene]
        write_new(output/f'request-{scene}.json',dict(argv=argv,sceneSource=plan['source'],
            scenesSha256=plan['scenesSha256'],candidate=run['candidate'],fixture=fixture,
            lane='current' if current else 'candidate'))
        with (output/f'capture-{scene}.log').open('x') as log:
            result = subprocess.run(argv,cwd=CAL,env=env,stdout=log,stderr=subprocess.STDOUT)
        if result.returncode:
            raise ValueError(f'Capture refused for {scene}; see scratch log')
        # Recheck source/candidate/backdrop bytes after the process as well as inside Node/Vite.
        for pin in closure['sources']: pin_file(pin)
        candidate_info(run['candidate'],plan['position'],current=current)
        fixture_info(run,plan)
        folder = output/scene
        report_path = folder/f'report__{run["renderer"]}.json'
        report = read_json(report_path)
        args = validate_report(report,run,endpoint,abscissa=abscissa,phase=context['phase'])
        cell_path = folder/f'cell__{run["renderer"]}.json'
        cell = read_json(cell_path)
        png = folder/f'{scene}__{run["renderer"]}.png'
        if cell.get('renderer')!=run['renderer'] or cell.get('colorSpace')!='srgb' or not cell.get('deterministic') or cell.get('repeatNoise')!=0:
            raise ValueError('Wrong tier/colour space or unstable capture')
        artifacts = {name:dict(path=str(path),sha256=sha(path)) for name,path in
                     [('png',png),('report',report_path),('cell',cell_path)]}
        # Check signature/dimensions without a pixel read or a second image codec.
        raw = png.read_bytes()
        expected=(plan['canvas']['width']*plan['dpr'],plan['canvas']['height']*plan['dpr'])
        if raw[:8]!=b'\x89PNG\r\n\x1a\n' or tuple(int.from_bytes(raw[i:i+4],'big') for i in (16,20))!=expected:
            raise ValueError('PNG dimensions differ from declared canvas')
        for argument in args:
            argument['provenance'].update(report=artifacts['report'],capture=artifacts['png'],
                sceneSource=plan['source'],scenesSha256=plan['scenesSha256'],
                candidateDocument=run['candidate'],baseline=current,
                endpoint={k:v for k,v in endpoint.items() if k!='patch'})
        record=dict(profile=run['profile'],renderer=run['renderer'],scene=scene,
            candidate=run['candidate'],lane='current' if current else 'candidate',
            sceneSource=plan['source'],canvas=plan['canvas'],dpr=plan['dpr'],
            artifacts=artifacts,arguments=args,background=next(b for b in fixture['backgrounds']
                if b['key']==f'{spec["background"]}@{plan["dpr"]}x'))
        write_new(folder/'w50-capture.json',record)
        records.append(record)
    # An explicit scratch adapter manifest, NOT a schema-5 calibration matrix or publication.
    write_new(matrix,dict(schema='w50-web-capture-index-1',captures=records))
    return records
