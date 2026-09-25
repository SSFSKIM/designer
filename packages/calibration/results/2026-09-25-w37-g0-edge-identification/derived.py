"""Reproduced memo tables, native-conditioned old rim and W36 provenance (§5.181)."""
import base64,gzip,hashlib,json,subprocess,sys
from pathlib import Path
import numpy as np
import identify
from law import HERE,edge
OLD=identify.OLD;CAL=identify.CAL;ROOT=identify.ROOT


def save(path,value):
    if '--verify' in sys.argv:
        raw=path.read_bytes();prior=json.loads(gzip.decompress(raw) if path.suffix=='.gz' else raw)
        assert prior==value,path.name+' changed'
    else:edge.save(path,value)


def main():
    replay=json.loads(gzip.decompress((HERE/'native-replay.json.gz').read_bytes()))
    pins=json.loads((HERE/'grounding-pins.json').read_text())
    digest=lambda value:hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    assert digest(replay['rows'])==pins['nativeRows'];assert replay['maxDifferenceFromW35']==0
    diag=json.loads((HERE/'diagnostics.json').read_text());assert digest(diag)==pins['diagnostics']
    comparisons=dict(cells=replay['cells'],roles=replay['roles'],nativeNumericMaxDifference=0,diagnosticsEqual=True)
    table=[];css=[];surface=[];inactive=[]
    for r in replay['rows']:
        profile,sid=r['cell'].split('/');scheme='dark' if '-dark-' in profile else 'light'
        colour,geometry,pose=sid.split('__')
        for row in r['rows']:
            if row['shell'] < -r['scale']:continue
            table.append(dict(cell=r['cell'],role=r['role'],scheme=scheme,scale=r['scale'],side=row['side'],shell=row['shell'],pixels=row['pixels'],deep=r['deep'],rgb=row['rgb'],excess=row['excess']))
        if geometry=='circular-120' and pose=='rest' and r['scale']==2:
            for side in ['top','bottom']:
                pair=[q for q in r['rows'] if q['side']==side and q['shell'] in [-2,-1]]
                if len(pair)!=2:continue
                outputs=np.array([q['rgb'] for q in pair])
                css.append(dict(cell=r['cell'],side=side,colour=colour,scheme=scheme,rowsRGB=outputs.tolist(),constantOutputMinimaxCodes=((outputs.max(0)-outputs.min(0))/2).tolist(),bestConstantRGB=((outputs.max(0)+outputs.min(0))/2).tolist(),scope='single constant inset covering two full straight rows; not arbitrary multi-shadow radial projections'))
        if colour in ['grey-128','grey-255','red'] and pose=='rest':
            surface.append(dict(cell=r['cell'],role=r['role'],geometry=geometry,scale=r['scale'],scheme=scheme,deep=r['deep'],top=[q for q in r['rows'] if q['side']=='top']))
        if geometry.startswith('circular') and pose=='inactive':
            maximum=max(abs(v) for q in r['rows'] if q['side'] in ['top','bottom'] for v in q['excess'])
            inactive.append(dict(cell=r['cell'],maxStraightExcess=maximum))
    save(HERE/'memo-reproduction.json',comparisons);save(HERE/'line-tables.json',table)
    save(HERE/'css-bound.json',css);save(HERE/'surface-transfer.json',surface);save(HERE/'inactive-control.json',inactive)
    # Replay the expanded 2x dark maximum from all seven admitted normal runs.
    bars=json.loads(gzip.decompress((OLD/'deep-bars.json.gz').read_bytes()))
    candidates=[r for r in bars if r['protocol']=='normal' and '-2x-dark-' in r['cell']]
    record=max(candidates,key=lambda r:max(max(b['barRGB']) for b in r['bins']))
    witness=max(record['bins'],key=lambda b:max(b['barRGB']))
    reader=edge.W.default_wave().reader(edge.G1/'repeat')
    crop=json.loads(gzip.decompress(reader.read(record['cell'],'crop')))
    runs=[r for r in crop['runs'] if r['admitted'] and r['protocol']=='normal']
    states={s:edge.I.unpack(base64.b64decode(crop['states'][s])) for s in {r['state'] for r in runs}}
    p=states[runs[0]['state']];d,nx,ny,arc,angle,whole=edge.geometry(p)
    mask=(arc if witness['part']=='arc' else ~arc)&(angle==witness['bin'])&(d>=witness['shell'])&(d<witness['shell']+1)
    values=edge.bar([states[r['state']]['rgb'][mask] for r in runs]);assert np.array_equal(values,witness['barRGB'])
    save(HERE/'expanded-bar-replay.json',dict(cell=record['cell'],runs=len(runs),bin=witness,recomputedRGB=values.tolist()))
    # Retained W36 black cells are pre-seal price, never relabelled canonical.
    G=HERE.parent/'2026-09-24-w36-g1-black-branch';seal=json.loads((G/'sealed-manifest.json').read_text())['documents']
    plans={p['profile']:p for p in json.loads((G/'candidate-plans.json').read_text())};proof=[]
    for r in diag['w36BlackReplay']:
        profile,sid=r['cell'].split('/');scheme='dark' if '-dark-' in profile else 'light'
        active=f'apple-macos-27.0-1x-{scheme}-standard-glass0.5.json';receded=active.replace('.json','-receded.json')
        adoc=json.loads((CAL/'profiles'/active).read_text());rdoc=json.loads((CAL/'profiles'/receded).read_text())
        base=json.loads(subprocess.check_output(['git','-C',str(ROOT),'show','2f49d390^:packages/calibration/profiles/'+active]))
        web=edge.WebReader.w34(Path(plans[profile]['root'])/'web-captures')
        report=json.loads(web.read(r['cell'],'report'));meta=json.loads(web.read(r['cell'],'metadata'))
        assert {**base['patch'],**report['materialProfile']['patch']}==adoc['patch']
        assert report['recededProfile']['patch']==rdoc['patch']
        assert meta['deterministic'] and meta['repeatNoise']==0
        assert meta['gpuAdapter']=='apple/metal-3' and not report['fallback']
        for key in ['materialProfile','recededProfile']:
            assert hashlib.sha256(Path(report[key]['path']).read_bytes()).hexdigest()[:12]==report[key]['sha256']
        for name in [active,receded]:assert hashlib.sha256((CAL/'profiles'/name).read_bytes()).hexdigest()==seal[name]['fileSha256']
        proof.append(dict(cell=r['cell'],deep=r['deep'],activeSha=seal[active]['fileSha256'],recededSha=seal[receded]['fileSha256'],
            provenance='preserved pre-seal W36 price; base+tune and receded patch equal shipped law, deterministic Metal; NOT new canonical capture'))
    save(HERE/'provenance.json',proof)
    materials=json.loads((G/'resolved-materials.json').read_text());oldrows=[]
    for r in identify.inputs():
        if not r['active']:continue
        material=materials[f"apple-macos-27.0-1x-{r['scheme']}-standard-glass0.5"]
        optics=material['optics']['regular'];u=np.clip((r['span']-material['sizeSpanMin'])/(material['sizeSpanMax']-material['sizeSpanMin']),0,1);k=u*u*(3-2*u)
        reach=min(8*(1+(material['lensSizeGainMax']-1)*k),r['span']/2)
        width=optics['rimWidth'] if r['scale']==1 else optics['rimWidth2x']
        axis=material['rimLitAxis'];lit=np.maximum(abs(r['nx']*axis[0]+r['ny']*axis[1])*np.sqrt(2),1e-6)**optics['rimLitExponent']
        along=np.maximum(1+optics['rimAlongSideSlope']*k*r['along'],0)
        options=dict(width=width,shadow_alpha=optics['shadowAlpha'],shadow_depth=optics['shadowDepth']*(1+(material['sizeShadowGainMax']-1)*k),shadow_reach=reach,lit=lit,along=along)
        body=edge.decode(r['body']/255)
        full=edge.forward(body,r['d'],1,a=optics['rimAlpha'],g=optics['rimLevelGain'],**options)['encoded']
        shadow=edge.forward(body,r['d'],1,a=0,g=0,**options)['encoded']
        for bn in r['bins']:
            ids=bn['indices'];oldrows.append(dict(cell=r['cell'],part=bn['part'],shell=bn['shell'],bin=bn['bin'],pixels=bn['pixels'],admissible=bn['admissible'],closure=r['circular'],
                rimContributionRGB=(full[ids]-shadow[ids]).mean(0).tolist(),shadowContributionRGB=(shadow[ids]-r['body']).mean(0).tolist(),oldExcessRGB=(full[ids]-r['body']).mean(0).tolist(),nativeExcessRGB=(r['native'][ids]-r['body']).mean(0).tolist()))
    save(HERE/'old-rim.json.gz',dict(conditioning='native deep; decomposition of inherited forward, not a current render',rows=oldrows))
    print('memo',comparisons,'bar',values,'inactive max',max(r['maxStraightExcess'] for r in inactive),'black provenance',len(proof),'old rim bins',len(oldrows))
if __name__=='__main__':main()
