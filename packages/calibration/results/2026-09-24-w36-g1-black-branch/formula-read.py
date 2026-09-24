"""Price the conditional formula independently of the admitted black branch (§5.179 DL2)."""
import io,json,statistics,sys
from pathlib import Path
import numpy as np
from PIL import Image
HERE=Path(__file__).resolve().parent;CAL=HERE.parent.parent
sys.path.insert(0,str(HERE.parent/'2026-09-23-w34-g0-contour-bed'))
from w35_readers import WebReader,CanonicalNativeReader
plans=json.loads((HERE/'formula-plans.json').read_text())['plans']
priorPlans={p['profile']:p for p in json.loads((HERE/'candidate-plans.json').read_text())}
projection={p['cell']:p for p in json.loads((HERE/'projection.json').read_text())}
old={(c['key']['profileKey']+'/'+c['key']['sceneId'],c['key']['web']['renderer']):c for c in json.loads((CAL/'results/matrix.json').read_text())['cells']}
new={};rows=[];failures=[];controls=[];coherence=[];cn=CanonicalNativeReader()
def value(c,k):return c.get('material',{}).get(k,{}).get('value')
def conditioned(c):
    s=c.get('shape');v=lambda k:s.get(k,{}).get('value',float('nan'))
    return s is None or (v('silhouetteAreaNative')>=.95*v('componentRegionArea') and v('silhouetteAreaWeb')>=.95*v('componentRegionArea') and v('silhouetteBodiesNative')<=v('componentRegionBodies') and v('silhouetteBodiesWeb')<=v('componentRegionBodies'))
for plan in plans:
    for c in json.loads((Path(plan['root'])/'matrix.json').read_text())['cells']:
        new[c['key']['profileKey']+'/'+c['key']['sceneId'],c['key']['web']['renderer']]=c
    reader=WebReader.canonical(Path(plan['root'])/'web-captures');prior=WebReader.canonical(Path(priorPlans[plan['profile']]['root'])/'web-captures')
    for sid in plan['scenes']:
        cell=plan['profile']+'/'+sid;cn.roles.admit(cell)
        bg=np.asarray(Image.open(io.BytesIO(cn.read(cell,'background'))).convert('RGB'))
        achromatic=bool(np.all(bg[:,:,0]==bg[:,:,1]) and np.all(bg[:,:,1]==bg[:,:,2]))
        if achromatic:
            now=json.loads(reader.read(cell,'report'));before=json.loads(prior.read(cell,'report'))
            tones=lambda r:[g['state'].get('backdropToneAbscissae') for g in r['page']['groups']]
            control=dict(cell=cell,pngSame=reader.read(cell)==prior.read(cell),packedReadingsSame=tones(now)==tones(before));controls.append(control)
            if not all([control['pngSame'],control['packedReadingsSame']]):failures.append(dict(stop='achromatic identity',**control))
        before=old.get((cell,'webgpu'));current=new.get((cell,'webgpu'))
        if before and current:
            n=value(current,'interiorMeanNative');w=value(current,'interiorMeanWeb');n0=value(before,'interiorMeanNative');w0=value(before,'interiorMeanWeb')
            if None not in [n,w,n0,w0]:
                error=abs(w-n);baseline=abs(w0-n0);growth=error-baseline
                isL1=projection[cell]['originalRole'] in ['calibration','validation']
                row=dict(cell=cell,role=projection[cell]['originalRole'],native=n,baselineWeb=w0,candidateWeb=w,baselineError=baseline,error=error,growth=growth,scope='L1' if isL1 else 'probe regression')
                rows.append(row)
                if growth>.005 or (isL1 and error>.055 and baseline<=.055):failures.append(dict(stop='L1/growth',**row))
        css=new.get((cell,'css'))
        if css:
            v=css.get('coherence',{});d=v.get('crossTierOklabDeltaEMean',{}).get('value');ratio=v.get('interiorLevelRatioGpuOverCss',{}).get('value')
            row=dict(cell=cell,deltaE=d,ratio=ratio,conditioned=conditioned(css));coherence.append(row)
            if d is not None and d>.05 or ratio is not None and row['conditioned'] and not .8<=ratio<=1.25:failures.append(dict(stop='tier coherence',**row))
m1=[];beds={}
for b in json.loads((HERE.parent/'2026-09-22-w33-g1b-rim-fit/chroma-cut.json').read_text())['cells']:
    cell=b['profile']+'/'+b['scene'];before=old[cell,'webgpu'];current=new.get((cell,'webgpu'),before)
    ratio=value(current,'chromaStructureRatioWeb')/value(current,'chromaStructureRatioNative');ratio0=value(before,'chromaStructureRatioWeb')/value(before,'chromaStructureRatioNative')
    delta=value(current,'interiorStdDevWeb')/value(before,'interiorStdDevWeb')-1
    row=dict(cell=cell,bed=b['scheme']+'|'+b['pose'],R=ratio,baselineR=ratio0,structureDelta=delta,rendered=(cell,'webgpu') in new);m1.append(row);beds.setdefault(row['bed'],[]).append(ratio)
    if abs(delta)>.02:failures.append(dict(stop='M2',**row))
    if not .6<=ratio<=1.4 and .6<=ratio0<=1.4:failures.append(dict(stop='M1 cell',**row))
medians={k:statistics.median(v) for k,v in beds.items()}
for b,v in medians.items():
    if not .8<=v<=1.2:failures.append(dict(stop='M1 median',bed=b,value=v))
result=dict(cellsPerTier=sum(len(p['scenes']) for p in plans),rows=rows,M1=medians,photo=m1,achromaticControls=controls,coherence=coherence,failures=failures,
    outcome='DECLINED: restore old formula, black branch alone may seal' if failures else 'PASS: requires a macOS27-only selection before seal')
with (HERE/'formula-reading.json').open('x') as f:json.dump(result,f,indent=2);f.write('\n')
print(json.dumps(dict(cellsPerTier=result['cellsPerTier'],M1=medians,failures=failures,outcome=result['outcome']),indent=2))
