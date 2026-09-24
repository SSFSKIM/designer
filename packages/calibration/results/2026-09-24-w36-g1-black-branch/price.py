"""Price the actual scratch pixels against frozen stops; never move a bound (§5.179)."""
import base64,gzip,hashlib,importlib.util,io,json,statistics,sys
from pathlib import Path
import numpy as np
from PIL import Image
HERE=Path(__file__).resolve().parent;CAL=HERE.parent.parent;ROOT=HERE.parents[3]
sys.path.insert(0,str(HERE.parent/'2026-09-24-w35-g0-edge-cut'))
import edge
from w35_readers import WebReader,CanonicalNativeReader
G0=HERE.parent/'2026-09-24-w36-g0-level-cut'
plans=json.loads((HERE/'candidate-plans.json').read_text())
projection={r['cell']:r for r in json.loads((HERE/'projection.json').read_text())}
base=json.loads((CAL/'results/matrix.json').read_text())
old={(c['key']['profileKey']+'/'+c['key']['sceneId'],c['key']['web']['renderer']):c for c in base['cells']}
def readjson(p):return json.loads(p.read_text())
def save(name,value):
    with (HERE/name).open('x') as f:json.dump(value,f,indent=2,allow_nan=False);f.write('\n')
def image(raw):return np.asarray(Image.open(io.BytesIO(raw)).convert('RGB'))
def val(c,k):return c.get('material',{}).get(k,{}).get('value')
cn=CanonicalNativeReader();shipped=WebReader.canonical('/Users/new/Developer/GitHub/designer/packages/calibration/web-captures')
new={};raws={};comparisons=[];grey=[];failures=[]
baseDeep={r['cell']:r for r in readjson(G0/'deep-cut.json')}
wave=edge.W.default_wave();repeat=wave.reader(edge.G1/'repeat')
for plan in plans:
    path=Path(plan['root']);matrix=readjson(path/'matrix.json')
    for c in matrix['cells']:
        if c['key']['web']['renderer']=='webgpu':new[c['key']['profileKey']+'/'+c['key']['sceneId']]=c
    for sid in plan['scenes']:
        cell=plan['profile']+'/'+sid;origin=projection[cell]['origin']
        reader=WebReader.w34(path/'web-captures') if origin=='w34' else WebReader.canonical(path/'web-captures')
        raw=reader.read(cell);im=image(raw);raws[cell]=raw
        meta=json.loads(reader.read(cell,'metadata'));report=json.loads(reader.read(cell,'report'))
        assert meta['deterministic'] and meta['repeatNoise']==0 and meta['gpuAdapter']=='apple/metal-3' and not report['fallback']
        if origin=='w34':
            crop=json.loads(gzip.decompress(repeat.read(cell,'crop')))
            run=next(r for r in crop['runs'] if r['admitted'] and r['protocol']=='normal')
            p=edge.I.unpack(base64.b64decode(crop['states'][run['state']]))
            mask=edge.geometry(p)[0]<=-6*p['scale'];median=np.median(im[mask],0)
            before=baseDeep[cell];native=np.array(before['nativeMedian']);black=sid.startswith('grey-0__')
            passes=bool(np.max(abs(median-native))<=1) if black else median.tolist()==before['webMedian']
            row=dict(cell=cell,native=native.tolist(),shipped=before['webMedian'],candidate=median.tolist(),miss=(median-native).tolist(),black=black,passStop=passes,spread=(im[mask].max(0)-im[mask].min(0)).tolist())
            grey.append(row)
            if not passes:failures.append(dict(stop='black <=1 code or non-black regression',**row))
        else:
            try:prior=shipped.read(cell)
            except FileNotFoundError:prior=None
            before=old.get((cell,'webgpu'));current=new.get(cell)
            axes=['shape','material','perceptual','shadow']
            same={a:current.get(a)==before.get(a) for a in axes} if current and before else None
            row=dict(cell=cell,pngSame=None if prior is None else raw==prior,oldSha256=None if prior is None else hashlib.sha256(prior).hexdigest(),newSha256=hashlib.sha256(raw).hexdigest(),axesSame=same,matrixRowPresent=current is not None,baselineRowPresent=before is not None)
            comparisons.append(row)
# L1 uses the frozen snapshot, no shape-predicate drop.
l1=[]
for b in readjson(G0/'l1-baseline.json'):
    c=new.get(b['cell']);n=val(c or {},'interiorMeanNative');w=val(c or {},'interiorMeanWeb')
    err=None if n is None or w is None else abs(w-n)
    growth=None if err is None or b['absoluteError'] is None else err-b['absoluteError']
    existing=b['absoluteError'] is not None and b['absoluteError']>.055
    passes=(err is None and b['absoluteError'] is None) or (err is not None and growth is not None and growth<=.005 and (err<=.055 or existing))
    row=dict(cell=b['cell'],baselineError=b['absoluteError'],error=err,growth=growth,existingAbsoluteMiss=existing,passStop=passes)
    l1.append(row)
    if not passes:failures.append(dict(stop='L1',**row))
# The adopted M1 population is fixed; M2 compares this wave to W33, not W32.
m1=[];beds={}
for b in readjson(HERE.parent/'2026-09-22-w33-g1b-rim-fit/chroma-cut.json')['cells']:
    cell=b['profile']+'/'+b['scene'];c=new[cell];before=old[(cell,'webgpu')]
    ratio=val(c,'chromaStructureRatioWeb')/val(c,'chromaStructureRatioNative')
    ratio0=val(before,'chromaStructureRatioWeb')/val(before,'chromaStructureRatioNative')
    delta=val(c,'interiorStdDevWeb')/val(before,'interiorStdDevWeb')-1
    passes=abs(delta)<=.02 and (.6<=ratio<=1.4 or not .6<=ratio0<=1.4)
    row=dict(cell=cell,bed=b['scheme']+'|'+b['pose'],R=ratio,baselineR=ratio0,structureDelta=delta,passStop=passes)
    m1.append(row);beds.setdefault(row['bed'],[]).append(ratio)
    if not passes:failures.append(dict(stop='M1/M2',**row))
medians={b:statistics.median(v) for b,v in beds.items()}
for b,v in medians.items():
    if not .8<=v<=1.2:failures.append(dict(stop='M1 median',bed=b,value=v))
# C1 reads the original admitted population and bands through the unchanged reader.
spec=importlib.util.spec_from_file_location('exterior',HERE.parent/'2026-09-22-w33-g1b-rim-fit/exterior-cut.py');ext=importlib.util.module_from_spec(spec);spec.loader.exec_module(ext)
c1rows=[];groups={}
for b in readjson(HERE.parent/'2026-09-22-w33-g1b-rim-fit/exterior-cut.json')['rows']:
    if b['tier']!='webgpu' or '-standard-' not in b['profile'] or b['span'] not in [96,128,160]:continue
    cell=b['profile']+'/'+b['scene'];c=new.get(cell)
    if c is None:raise RuntimeError('C1 missing '+cell)
    reading=ext.shape_error({**b,'shadow':c['shadow']})
    row=dict(cell=cell,bed=b['bed'],span=b['span'],T=reading['T'],baselineT=b['T'],bands=list(reading['bandsUsed']),admitted=list(reading['admitted']))
    c1rows.append(row)
    if reading['T'] is not None and reading['bandsUsed']==reading['admitted']:
        groups.setdefault((b['bed'],b['span']),[]).append(reading['T'])
c1=[dict(bed=b,span=s,T=sorted(v)[len(v)//2],passStop=sorted(v)[len(v)//2]<=.0042) for (b,s),v in sorted(groups.items())]
for row in c1:
    if not row['passStop']:failures.append(dict(stop='C1',**row))
# X1: same two box-exterior masks and fixed native/backdrop black pixels as adoption.
x1=[]
for b in readjson(HERE.parent/'2026-09-22-w33-g2-landing/black-cut.json')['cells']:
    cell=b['profile']+'/'+b['scene'];n=image(cn.read(cell));bg=image(cn.read(cell,'background'));w=image(raws[cell])
    scale=2 if '-2x-' in b['profile'] else 1;scene=cn.roles.scenes[b['scene']];comp=cn.roles.spec['components'][scene['component']]
    width,height=comp['size'];dx,dy=comp.get('offset',[0,0]);x0=((320-width)/2+dx)*scale;y0=((200-height)/2+dy)*scale;x1p=x0+width*scale;y1=y0+height*scale
    y,x=np.indices(n.shape[:2]);eligible=np.all(n==0,2)&np.all(bg==0,2)
    masks=dict(integer=np.maximum.reduce([x0-x,x-(x1p-1),y0-y,y-(y1-1)])>=2*scale,
       analytic=np.hypot(np.maximum.reduce([x0-(x+.5),x+.5-x1p,np.zeros_like(x)]),np.maximum.reduce([y0-(y+.5),y+.5-y1,np.zeros_like(y)]))>=2*scale)
    row=dict(cell=cell)
    for kind,mask in masks.items():
        selected=eligible&mask;maximum=w.max(2);row[kind]=dict(pixels=int(selected.sum()),aboveZero=int(np.sum(selected&(maximum>0))),aboveOne=int(np.sum(selected&(maximum>1))))
        assert row[kind]['pixels']==b[kind]['pixels']
        if row[kind]['aboveZero'] or row[kind]['aboveOne']:failures.append(dict(stop='X1',cell=cell,mask=kind,**row[kind]))
    x1.append(row)
summary=dict(captured=len(raws),canonical=len(comparisons),black=sum(r['black'] for r in grey),
    canonicalByteComparisons=sum(r['pngSame'] is not None for r in comparisons),canonicalByteChanges=[r['cell'] for r in comparisons if r['pngSame'] is False],
    axisChanges=[r for r in comparisons if r['axesSame'] and not all(r['axesSame'].values())],
    L1=dict(population=len(l1),measured=sum(r['error'] is not None for r in l1),maxGrowth=max(r['growth'] for r in l1 if r['growth'] is not None),absoluteMisses=[r for r in l1 if r['error'] is not None and r['error']>.055]),
    M1=medians,M2MaxFraction=max(abs(r['structureDelta']) for r in m1),C1=c1,X1Cells=len(x1),failures=failures,
    predicate='Shape fields and PNG identity priced explicitly; no predicate declaration is edited before seal/read.',
    B1='All shadow leaves unchanged; the candidate patch moves only black strength and ordinates.')
for name,value in [('price-gpu-summary.json',summary),('price-gpu-pixels.json',comparisons),('price-greys.json',grey),('price-l1.json',l1),('price-m1-m2.json',m1),('price-c1.json',c1rows),('price-x1.json',x1)]:save(name,value)
print(json.dumps(summary,indent=2));raise SystemExit(1 if failures else 0)
