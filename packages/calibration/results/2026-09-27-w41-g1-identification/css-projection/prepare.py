"""Offline public fixtures, proof verification and bounded calval scoring. Never launches a browser."""
import argparse
from collections import Counter
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import uuid
import numpy as np
from PIL import Image
import projection as p

HERE=Path(__file__).resolve().parent
G1=HERE.parent
ROOT=G1.parents[3]
CAPTURES=Path('/Users/new/vitrea-w41/g1-captures/css-projection')
spec=importlib.util.spec_from_file_location('css_e3_scorer',G1/'candidate-e3/scorer.py')
s=importlib.util.module_from_spec(spec);sys.modules[spec.name]=s;spec.loader.exec_module(s)
ROUTES=('plate','affine')


def save(path,value):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('x') as f:json.dump(value,f,indent=2,sort_keys=True,allow_nan=False);f.write('\n')


def text(path,value):
    with Path(path).open('x') as f:f.write(value)


def capture_path(route,scale,cell):
    if route not in ROUTES or scale not in (1,2) or cell not in cells():
        raise ValueError('outside declared projection scope')
    profile,scene=cell.split('/')
    return CAPTURES/route/profile/(scene+'.png')


def cells():
    result={};params=s.parameters()
    for cell in s.base.scope()[0]:
        if s.disposition(cell)!='claimed uniform body':continue
        comp,scale=s.base.component(cell)
        _,background=s.identity(cell);rgb=background['srgb'];l,f,g=p.e3_terms(rgb,params)
        shapes=s.m.readers.shapes_of(comp)
        if len(shapes)!=1 or shapes[0].opaque or comp['kind'] not in ('capsule-circular','rrect'):
            raise ValueError('unsupported CSS geometry; do not invent a supplied-path mirror')
        shape=shapes[0]
        radius=min(shape.size)/2 if comp['kind']=='capsule-circular' else comp['radius']
        plate=p.plate_route(l,f,g)
        x=np.asarray(rgb)/255;css_l=float(x @ p.CSS_W)
        intermediate=css_l+plate['saturation']*(x-css_l)
        plate.update(n=plate['plate']*255,intermediateRGB=(255*intermediate).tolist(),
                     intermediateClips=bool(np.any((intermediate<0)|(intermediate>1))))
        result[cell]=dict(role=s.wave.roles[cell.split('/',1)[1]],scale=scale,rgb=rgb,
            size=list(shape.size),origin=list(shape.frame_origin),radius=radius,kind=comp['kind'],
            L=l,F=f,g=g,k=f-g*l,plate=plate,affine=p.affine_route(g,f-g*l),
            e3RGB=(np.clip(f+g*(np.asarray(rgb)/255-l),0,1)*255).tolist())
    return result


def sources():
    paths=[HERE/'projection.py',HERE/'prepare.py',HERE/'fixture.html',HERE/'parent-relay.json',
           G1/'candidate-e3/scorer.py',G1/'candidate-e3/runtime.json',
           G1/'body/report-1/spatial-selection.json',G1/'baseline/baseline.py',
           G1/'x6/observe.py',HERE/'x6_once.py',G1/'exposure/runner.py',G1/'parent-ruling-css-second-route.json',
           s.W39_BODY/'body.py',s.W39/'supplied-paths.json',s.wave.scenes_path,s.wave.split_path,
           s.G0/'bounds-declaration.txt',s.G0/'instrument/instrument.py',
           s.G0/'instrument/rendered.py',s.W39/'w39_readers.py',s.W39/'wave.py',
           s.W39/'w39_archive.py',s.W39/'replay-archive.py',
           ROOT/'packages/platform-web/src/optics.ts',ROOT/'packages/platform-web/src/css-tier.ts',
           ROOT/'packages/calibration/src/component-region.ts',
           ROOT/'packages/calibration/test/tier-coherence.test.ts']
    return {str(path.relative_to(ROOT)):s.sha(path) for path in paths}


def proof_rows():
    rows=[]
    for prop in ('filter','backdrop-filter'):
        for rgb in ([0,0,0],[64,64,64],[192,192,192]):
            for reverse in (False,True):
                x=np.asarray(rgb)/255
                expected=(np.clip(.5*np.clip(1.5*x,0,1)+.25,0,1) if reverse
                          else np.clip(1.5*(.5*x+.25),0,1))
                rows.append(dict(property=prop,rgb=rgb,
                    filter='brightness(1.5) contrast(0.5)' if reverse else 'contrast(0.5) brightness(1.5)',
                    expectedRGB=(255*expected).tolist(),purpose='order and encoded-sRGB'))
        # Non-primary encoded colours expose saturation, including clipping and the
        # neutral plate placed AFTER saturation, as in the BODY prototype fixture.
        for rgb,alpha,plate in [([85,125,170],0,0),([220,100,70],0,0),
                                ([85,125,170],.25,255),([220,100,70],.25,0)]:
            x=np.asarray(rgb)/255;l=float(x @ p.CSS_W)
            intermediate=l+2*(x-l)
            saturated=np.clip(intermediate,0,1)
            expected=(1-alpha)*saturated+alpha*plate/255
            rows.append(dict(property=prop,rgb=rgb,filter='saturate(2)',
                plateAlpha=alpha,plateRGB=plate,
                intermediateClips=bool(np.any((intermediate<0)|(intermediate>1))),
                expectedRGB=(255*expected).tolist(),purpose='encoded saturation and post-filter neutral plate'))
    for i,row in enumerate(rows):row.update(sample=[32+64*(i%5),28+56*(i//5)])
    return rows


def proof_pixels(image,scale):
    if image.size!=(320*scale,280*scale):raise ValueError('wrong proof frame dimensions')
    image=image.convert('RGB');rows=[]
    for row in proof_rows():
        x,y=row['sample'];actual=np.array(image.getpixel((x*scale,y*scale)))
        error=abs(actual-np.array(row['expectedRGB']))
        rows.append(dict(**row,actualRGB=actual.tolist(),errorCodes=error.tolist(),passes=bool(max(error)<=1)))
    return dict(passes=all(r['passes'] for r in rows),scale=scale,rows=rows,
                toleranceCodes=1,scope='synthetic CSS filter/backdrop-filter order and encoded-sRGB; not native fidelity')


def parse_run_log(raw,*,kind,scale,manifest_sha,config_sha,script_sha,paths,proof_sha=None):
    """Read one full playwright-cli run-code result, never inferred from PNG presence.

    Preserve the unedited CLI output outside public-1; the generated scripts return
    a single W41_CSS_RUN JSON line. CLI wrappers may JSON-quote that result.
    """
    matches=[]
    for line in raw.splitlines():
        candidate=line.strip().strip('`')
        if candidate.startswith('"'):
            try:candidate=json.loads(candidate)
            except json.JSONDecodeError:continue
        if isinstance(candidate,str) and candidate.startswith('W41_CSS_RUN:'):
            matches.append(candidate[len('W41_CSS_RUN:'):])
    if len(matches)!=1:raise ValueError('expected exactly one complete CLI run result')
    try:run=json.loads(matches[0])
    except json.JSONDecodeError as e:raise ValueError('invalid CLI run JSON') from e
    if (run.get('kind')!=kind or run.get('manifestSha256')!=manifest_sha
        or run.get('configSha256')!=config_sha or run.get('scriptSha256')!=script_sha
        or run.get('browserName')!='chromium'
        or not isinstance(run.get('version'),str) or not run['version'][:1].isdigit()
        or not isinstance(run.get('userAgent'),str) or 'Chrome/' not in run['userAgent']
        or run.get('dpr')!=scale or run.get('viewport')!={'width':320,'height':280}):
        raise ValueError('CLI browser, configuration or prepared manifest differs')
    if kind=='capture' and (not isinstance(run.get('runId'),str) or not run['runId']
        or run.get('proofSha256')!=proof_sha
        or not isinstance(run.get('proofRunIds'),list) or len(run['proofRunIds'])!=2):
        raise ValueError('capture run is not bound to proof runs')
    if kind=='proof' and (not isinstance(run.get('runId'),str) or not run['runId']):
        raise ValueError('proof run lacks its identity')
    rows=run.get('rows')
    if not isinstance(rows,list) or len(rows)!=len(paths):raise ValueError('partial CLI run')
    seen=set()
    for row in rows:
        if not isinstance(row,dict):raise ValueError('invalid CLI row')
        key=(row.get('cell'),row.get('route'))
        if (key not in paths or key in seen or row.get('scale')!=scale
            or row.get('path')!=paths[key] or not isinstance(row.get('sha256'),str)
            or len(row['sha256'])!=64 or any(c not in '0123456789abcdef' for c in row['sha256'])):
            raise ValueError('wrong, duplicate or missing screenshot row')
        observed=row.get('observed')
        if (not isinstance(observed,dict) or observed.get('cell')!=key[0]
            or observed.get('route')!=key[1] or observed.get('dpr')!=scale):
            raise ValueError('route/cell/DPR observation differs')
        if kind=='capture' and (observed.get('bodyOnly') is not True
                                or observed.get('productionTier') is not False
                                or not isinstance(observed.get('filter'),str)
                                or not observed['filter']):
            raise ValueError('BODY prototype observation differs')
        seen.add(key)
    return run


def read_run(public,log,kind,scale,paths,proof_sha=None):
    log=Path(log).resolve()
    if not log.is_relative_to((CAPTURES/'cli').resolve()):
        raise ValueError('raw CLI output must remain in the external capture CLI tree')
    manifest_sha=s.sha(public/'manifest.json')
    config_sha=s.sha(public/f'playwright-{scale}x.json')
    script_sha=s.sha(public/f'{kind}-{scale}x.js')
    try:raw=log.read_text()
    except OSError as e:raise ValueError('missing producing CLI output') from e
    return parse_run_log(raw,kind=kind,scale=scale,manifest_sha=manifest_sha,
                         config_sha=config_sha,script_sha=script_sha,paths=paths,proof_sha=proof_sha)


def verify_passed_proof(public,record):
    proof=s.load(public/'proof-passed.json')
    if (proof['passes'] is not True or proof['sources']!=record['sources']
        or proof['publicManifestSha256']!=s.sha(public/'manifest.json')
        or len(proof['results'])!=2):raise ValueError('proof not bound to prepared scope')
    ids=[]
    for scale,result in zip((1,2),proof['results']):
        path=CAPTURES/f'proof-{scale}x.png';log=Path(result['cliLog'])
        if (result['png']!=str(path) or s.sha(log)!=result['cliLogSha256']
            or result['sha256']!=s.sha(path)):
            raise ValueError('proof capture or CLI output changed')
        run=read_run(public,log,'proof',scale,{('proof','proof'):str(path)})
        with Image.open(path) as image:passes=proof_pixels(image,scale)['passes']
        if (run['rows'][0]['sha256']!=result['sha256'] or run['runId']!=result['runId']
            or not passes):
            raise ValueError('proof pixels or screenshot run differ')
        ids.append(run['runId'])
    if ids!=proof['runIds'] or len(set(ids))!=2:raise ValueError('proof run identities changed')
    return proof


def verify_public(public):
    record=s.load(public/'manifest.json')
    if record['sources']!=sources():raise ValueError('prepared source bytes changed')
    if record['cells']!=cells():raise ValueError('public scope or tuple changed')
    for name,digest in record['artifacts'].items():
        if s.sha(public/name)!=digest:raise ValueError('prepared artifact changed: '+name)
    return record


def build(out):
    s.check_runtime();out=Path(out);out.mkdir(parents=True,exist_ok=False)
    declared=cells();source=sources()
    save(out/'cells.json',declared);save(out/'proof-rows.json',proof_rows())
    text(out/'fixture.html',(HERE/'fixture.html').read_text())
    for scale in (1,2):
        config=dict(browser=dict(browserName='chromium',isolated=True,
            launchOptions=dict(channel='chromium',headless=True,args=['--force-color-profile=srgb']),
            contextOptions=dict(viewport=dict(width=320,height=280),deviceScaleFactor=scale,
                                colorScheme='light',reducedMotion='reduce')),
            outputDir=str(CAPTURES/'cli'),outputMode='stdout')
        save(out/f'playwright-{scale}x.json',config)
        common=f'''async page => {{
  const base = 'http://127.0.0.1:8769';
  const scale = {scale};
  const hash = async bytes => page.evaluate(async input => {{
    const digest = await crypto.subtle.digest('SHA-256',new Uint8Array(input));
    return Array.from(new Uint8Array(digest),b=>b.toString(16).padStart(2,'0')).join('');
  }},Array.from(bytes));
  const hashText = text => page.evaluate(async value => {{
    const digest = await crypto.subtle.digest('SHA-256',new TextEncoder().encode(value));
    return Array.from(new Uint8Array(digest),b=>b.toString(16).padStart(2,'0')).join('');
  }},text);
  const browser = page.context().browser();
  const browserName = browser.browserType().name();
  const version = browser.version();
  if (browserName !== 'chromium' || !/^\\d+\\./.test(version)) throw new Error('Not full Chromium');
  await page.setViewportSize({{width:320,height:280}});
  await page.goto(base + '/fixture.html');
  const dpr = await page.evaluate(() => devicePixelRatio);
  const viewport = page.viewportSize();
  if (dpr !== scale || viewport.width !== 320 || viewport.height !== 280)
    throw new Error('Wrong browser viewport or DPR');
  const manifestResponse = await page.request.get(base + '/manifest.json');
  const manifestText = await manifestResponse.text();
  const manifestSha256 = await hashText(manifestText);
  const prepared = JSON.parse(manifestText);
  const configText = await (await page.request.get(base + '/playwright-{scale}x.json')).text();
  const configSha256 = await hashText(configText);
  const config = JSON.parse(configText);
  const fixtureText = await (await page.request.get(base + '/fixture.html')).text();
  const cellsText = await (await page.request.get(base + '/cells.json')).text();
  const proofRowsText = await (await page.request.get(base + '/proof-rows.json')).text();
  if (await hashText(fixtureText) !== prepared.artifacts['fixture.html'] ||
      await hashText(cellsText) !== prepared.artifacts['cells.json'] ||
      await hashText(proofRowsText) !== prepared.artifacts['proof-rows.json'])
    throw new Error('Served fixture is not the prepared fixture');
  if (config.browser.browserName !== browserName ||
      config.browser.launchOptions.channel !== 'chromium' ||
      config.browser.launchOptions.args.join() !== '--force-color-profile=srgb' ||
      config.browser.contextOptions.deviceScaleFactor !== dpr)
    throw new Error('Prepared browser configuration differs');
  const identity = {{manifestSha256,configSha256,browserName,version,dpr,viewport,
    userAgent:await page.evaluate(() => navigator.userAgent)}};
'''
        proof=common+f'''  const scriptSha256 = await hashText(
    await (await page.request.get(base + '/proof-{scale}x.js')).text());
  if (scriptSha256 !== prepared.artifacts['proof-{scale}x.js'])
    throw new Error('Proof script differs from prepared manifest');
  await page.evaluate(() => window.showProof());
  const observed = {{cell:'proof',route:'proof',dpr}};
  const path = {json.dumps(str(CAPTURES/f'proof-{scale}x.png'))};
  const png = await page.screenshot({{path,scale:'device'}});
  const runId = await page.evaluate(() => crypto.randomUUID());
  return 'W41_CSS_RUN:' + JSON.stringify({{kind:'proof',...identity,scriptSha256,runId,
    rows:[{{cell:'proof',route:'proof',scale,path,sha256:await hash(png),observed}}]}});
}}'''
        capture=common+f'''  const scriptSha256 = await hashText(
    await (await page.request.get(base + '/capture-{scale}x.js')).text());
  if (scriptSha256 !== prepared.artifacts['capture-{scale}x.js'])
    throw new Error('Capture script differs from prepared manifest');
'''+'''  const proofResponse = await page.request.get(base + '/proof-passed.json');
  if (!proofResponse.ok()) throw new Error('Both-scale pixel proof must pass first');
  const proofText = await proofResponse.text();
  const proofSha256 = await hashText(proofText);
  const proof = JSON.parse(proofText);
  if (!proof.passes || proof.publicManifestSha256!==manifestSha256 ||
      JSON.stringify(proof.sources)!==JSON.stringify(prepared.sources) || proof.runIds.length!==2)
    throw new Error('Proof not bound to this prepared manifest');
  const cells = await (await page.request.get(base + '/cells.json')).json();
  const rows = [];
  for (const [cell, data] of Object.entries(cells)) {
    if (data.scale !== scale) continue;
    for (const route of ['plate','affine']) {
      await page.evaluate(async ({cell,route}) => window.showCell(cell,route), {cell,route});
      const observed = await page.evaluate(() => window.observed);
      if (observed.cell!==cell || observed.route!==route || observed.dpr!==scale ||
          !observed.bodyOnly || observed.productionTier || !observed.filter)
        throw new Error('Fixture did not draw requested BODY cell');
      const path = '''+json.dumps(str(CAPTURES))+''' + '/' + route + '/' + cell + '.png';
      const png = await page.screenshot({path,scale:'device'});
      rows.push({cell,route,scale,path,sha256:await hash(png),observed});
    }
  }
  const runId = await page.evaluate(() => crypto.randomUUID());
  return 'W41_CSS_RUN:' + JSON.stringify({kind:'capture',...identity,scriptSha256,proofSha256,runId,
    proofRunIds:proof.runIds,rows});
}'''
        text(out/f'proof-{scale}x.js',proof);text(out/f'capture-{scale}x.js',capture)
    artifacts={path.name:s.sha(path) for path in out.iterdir()}
    save(out/'manifest.json',dict(schema='w41-css-body-preparation-1',sources=source,artifacts=artifacts,
        cells=declared,roles=dict(Counter(r['role'] for r in declared.values())),
        preparationId=str(uuid.uuid4()),
        parameterOrigin='unchanged light-inactive tuple; zero fitted coefficients',
        geometryResidual='CSS border-radius silhouette differs from supplied native path; native paths only define measurement masks. Deep body only, not boundary or geometry parity.',
        plateRule='minimum alpha: white if F>L, black if F<L, alpha0 if equal; s=g/(1-alpha)',
        archiveInventorySha256=s.INVENTORY_SHA,nativePayloadReads=0,holdoutOpened=False,
        browsersLaunched=0,productionParity=False,adoption=False))
    print('Prepared',len(declared),'public uniform calval cells; no browser/native reads')


def verify_proof(public,logs):
    record=verify_public(public);results=[];run_ids=[]
    for scale,log in zip((1,2),logs):
        path=CAPTURES/f'proof-{scale}x.png'
        run=read_run(public,log,'proof',scale,{('proof','proof'):str(path)})
        if run['rows'][0]['sha256']!=s.sha(path):raise ValueError('proof screenshot changed')
        with Image.open(path) as image:result=proof_pixels(image,scale)
        results.append(dict(**result,png=str(path),sha256=s.sha(path),
                            cliLog=str(Path(log).resolve()),cliLogSha256=s.sha(log),runId=run['runId']))
        run_ids.append(run['runId'])
    if len(set(run_ids))!=2:raise ValueError('proof runs not independently identified')
    if not all(r['passes'] for r in results):
        save(public/'proof-failed.json',dict(results=results,passes=False))
        raise ValueError('synthetic browser pixel proof failed; no same-cell captures authorized')
    save(public/'proof-passed.json',dict(schema='w41-css-browser-proof-2',passes=True,
        sources=record['sources'],results=results,runIds=run_ids,
        publicManifestSha256=s.sha(public/'manifest.json')))


def capture_manifest(public,out,logs):
    record=verify_public(public);proof=verify_passed_proof(public,record)
    proof_sha=s.sha(public/'proof-passed.json')
    captures={cell:{} for cell in record['cells']};run_logs=[]
    for scale,log in zip((1,2),logs):
        paths={(cell,route):str(capture_path(route,data['scale'],cell))
               for cell,data in record['cells'].items() if data['scale']==scale for route in ROUTES}
        run=read_run(public,log,'capture',scale,paths,proof_sha)
        if run['proofRunIds']!=proof['runIds']:raise ValueError('capture not bound to actual proof runs')
        for row in run['rows']:
            path=Path(row['path'])
            with Image.open(path) as image:
                if image.size!=(320*scale,280*scale):raise ValueError('wrong capture size')
            if s.sha(path)!=row['sha256']:raise ValueError('screenshot differs from producing CLI run')
            captures[row['cell']][row['route']]=dict(png=str(path),sha256=row['sha256'])
        run_logs.append(dict(path=str(Path(log).resolve()),sha256=s.sha(log),runId=run['runId']))
    if len({entry['runId'] for entry in run_logs})!=2:raise ValueError('capture runs not independent')
    save(out,dict(schema='w41-css-body-captures-2',captures=captures,cliRuns=run_logs,
        publicManifest=str(public/'manifest.json'),publicManifestSha256=s.sha(public/'manifest.json'),
        proof=str(public/'proof-passed.json'),proofSha256=proof_sha,
        qualification='BODY-only standalone, not production parity or adoption'))


def verify_capture_manifest(public,captures,record):
    captured=s.load(captures);proof=verify_passed_proof(public,record)
    if (captured['publicManifestSha256']!=s.sha(public/'manifest.json')
        or captured['proofSha256']!=s.sha(public/'proof-passed.json')
        or set(captured['captures'])!=set(record['cells'])
        or len(captured.get('cliRuns',[]))!=2):raise ValueError('capture membership/provenance differs')
    run_ids=[]
    for scale,entry in zip((1,2),captured['cliRuns']):
        log=Path(entry['path'])
        if s.sha(log)!=entry['sha256']:raise ValueError('producing CLI output changed')
        paths={(cell,route):str(capture_path(route,data['scale'],cell))
               for cell,data in record['cells'].items() if data['scale']==scale for route in ROUTES}
        run=read_run(public,log,'capture',scale,paths,s.sha(public/'proof-passed.json'))
        if run['proofRunIds']!=proof['runIds'] or entry['runId']!=run['runId']:
            raise ValueError('capture and proof runs differ')
        run_ids.append(run['runId'])
        for row in run['rows']:
            saved=captured['captures'][row['cell']].get(row['route'])
            if (saved!={'png':row['path'],'sha256':row['sha256']}
                or s.sha(Path(row['path']))!=row['sha256']):
                raise ValueError('capture differs from producing run or manifest')
    if len(set(run_ids))!=2:raise ValueError('capture runs not independent')
    if any(set(routes)!=set(ROUTES) for routes in captured['captures'].values()):
        raise ValueError('route membership differs')
    return captured


def body_projection(web):
    # The inherited projection geometry reader labels the production shadow;
    # this fixture renders only the standalone CSS BODY layer.
    return {**web,'composite':'standalone BODY-only CSS projection; no shadow, border, rim or production layers'}


def score(public,captures,out):
    """Only inherited guarded calval Reader. No receipt, holdout, raw-root route."""
    s.check_runtime();record=verify_public(public)
    # Parse the producing CLI records and verify each screenshot BEFORE a native Reader.
    captured=verify_capture_manifest(public,captures,record)
    out=Path(out);out.mkdir(parents=True,exist_ok=False);scores={}
    for role in ('calibration','validation'):
        reader=s.native_reader(s.ARCHIVE,(role,))
        for cell,data in record['cells'].items():
            if data['role']!=role:continue
            native,states=s.payloads(reader,cell);scores[cell]={}
            for route,row in captured['captures'][cell].items():
                web=body_projection(s.project(cell,Path(row['png'])))
                prediction=dict(members=[dict(member=m['member'],predictedRGB=m['deep']['medianRGB'])
                                         for m in web['members']])
                value=s.numerical(cell,prediction,native,states)
                value['claim']='BODY-only standalone CSS deep reading; no production-tier survival claim'
                scores[cell][route]=dict(deep=value,webProjection=web,
                    algebraicRGB=(255*(p.plate_output(np.asarray(data['rgb'])/255,data['plate'])
                        if route=='plate' else p.affine_output(np.asarray(data['rgb'])/255,data['affine']))).tolist(),
                    e3RGB=data['e3RGB'])
    save(out/'scores.json',scores)
    save(out/'provenance.json',dict(sources=record['sources'],captureManifestSha256=s.sha(captures),
        roles=['calibration','validation'],cells=len(scores),nativeReader='inherited candidate-e3.native_reader',
        rawRootDenied=str(Path.home()/'vitrea-w39'),archiveInventorySha256=s.INVENTORY_SHA,
        fitsPerformed=0,holdoutOpened=False,receipt=False,productionParity=False,
        limitations=['No production sharp/heavy blur mixture, border, rim, shadow or unconditional contrast floor.',
                    'Supplied native paths used only for measurement masks; CSS border-radius renders silhouettes.',
                    'Moving colour before production second blur creates boundary residual; not tested here.',
                    'Deep reading only; web edge bins are diagnostic, no native edge or production veto inferred.']))


def main():
    parser=argparse.ArgumentParser(description=__doc__);sub=parser.add_subparsers(dest='op',required=True)
    buildp=sub.add_parser('public');buildp.add_argument('out',type=Path)
    proof=sub.add_parser('proof');proof.add_argument('public',type=Path)
    proof.add_argument('cli_1x',type=Path);proof.add_argument('cli_2x',type=Path)
    manifest=sub.add_parser('manifest');manifest.add_argument('public',type=Path);manifest.add_argument('out',type=Path)
    manifest.add_argument('cli_1x',type=Path);manifest.add_argument('cli_2x',type=Path)
    scoring=sub.add_parser('score-calval');scoring.add_argument('public',type=Path)
    scoring.add_argument('captures',type=Path);scoring.add_argument('out',type=Path)
    args=parser.parse_args()
    if args.op=='public':build(args.out)
    elif args.op=='proof':verify_proof(args.public,(args.cli_1x,args.cli_2x))
    elif args.op=='manifest':capture_manifest(args.public,args.out,(args.cli_1x,args.cli_2x))
    else:score(args.public,args.captures,args.out)


if __name__=='__main__':main()
