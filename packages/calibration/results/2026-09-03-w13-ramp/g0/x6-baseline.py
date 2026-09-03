import json, sys, collections

CANON='/Users/new/Developer/GitHub/designer/packages/calibration/results/matrix.json'
SCRATCH='/Users/new/.claude/jobs/5c70e47f/tmp/w13/matrix-x6-baseline.json'

def load(p):
    m=json.load(open(p))
    out={}
    for c in m['cells']:
        k=(c['key']['profileKey'], c['key']['sceneId'], c['key']['web']['renderer'])
        if k not in out or c['capturedAt']>out[k]['capturedAt']: out[k]=c
    return m,out

cm,canon=load(CANON)
sm,scr=load(SCRATCH)
print('canonical schema',cm['schemaVersion'],len(canon),'cells; scratch schema',sm['schemaVersion'],len(scr),'cells')

NEW={'ssimBand','ssimBandWindows','ssimInterior','ssimInteriorWindows'}

def walk(node, path, acc):
    if isinstance(node,dict):
        if set(node.keys())=={'value','units'}:
            acc[path]=(node['value'],node['units']); return
        for k,v in node.items(): walk(v,path+'.'+k,acc)
    elif isinstance(node,list):
        for i,v in enumerate(node): walk(v,path+f'[{i}]',acc)
    else:
        acc[path]=node

missing=[k for k in canon if k not in scr]
extra=[k for k in scr if k not in canon]
print('cells in canonical not in scratch:',len(missing), missing[:5])
print('cells in scratch not in canonical:',len(extra), extra[:5])

diffs=[]; worst=0.0; compared=0
for k,c in canon.items():
    if k not in scr: continue
    a={}; b={}
    walk({x:y for x,y in c.items() if x!='capturedAt'},'',a)
    walk({x:y for x,y in scr[k].items() if x!='capturedAt'},'',b)
    for p,v in a.items():
        if p not in b:
            diffs.append((k,p,v,'ABSENT')); continue
        w=b[p]
        if isinstance(v,tuple) and isinstance(w,tuple):
            compared+=1
            if v[1]!=w[1] or v[0]!=w[0]:
                d=abs(v[0]-w[0]); worst=max(worst,d)
                if d>0: diffs.append((k,p,v[0],w[0]))
        elif v!=w:
            diffs.append((k,p,v,w))
    for p in b:
        if p not in a and p.rsplit('.',1)[-1] not in NEW:
            diffs.append((k,p,'ABSENT',b[p]))
print(f'compared {compared} metric values; {len(diffs)} differences; worst |delta| = {worst!r}')
for d in diffs[:40]: print('  DIFF',d)

# ---- baseline tables ----
def val(cell,name):
    p=cell.get('perceptual',{})
    v=p.get(name)
    return None if v is None else v['value']

def outside(cell):
    """The SSIM the two rows do NOT cover: windows centred outside the silhouette."""
    w,h=cell['key']['web']['pixelSize']
    total=(w-10)*(h-10)
    b=val(cell,'ssimBand'); i=val(cell,'ssimInterior')
    if b is None: return None,None
    nb=val(cell,'ssimBandWindows'); ni=0 if i is None else val(cell,'ssimInteriorWindows')
    inside=b*nb+(0 if i is None else i*ni)
    n=nb+ni
    if total<=n: return None,None
    return (val(cell,'ssimMean')*total-inside)/(total-n), total-n

def fmt(x,n=4):
    return '—' if x is None else f'{x:.{n}f}'

CHECKER=['rrect-sm','capsule-button','rrect-md','rrect-ml','rrect-lg','glass-over-glass','toolbar-group']
rows=[]
print()
print('### Checkerboard cells, light standard')
print()
print('| cell | scale | tier | ssimMean | ssimBand | ssimInterior | band px | interior px | band share of deficit | ssimOutside | outside px |')
print('|---|---|---|---|---|---|---|---|---|---|---|')
def share(c):
    b=val(c,'ssimBand'); i=val(c,'ssimInterior')
    bn=val(c,'ssimBandWindows'); inn=val(c,'ssimInteriorWindows')
    if b is None: return None
    bd=(1-b)*bn
    idf=0.0 if i is None else (1-i)*inn
    tot=bd+idf
    return None if tot==0 else bd/tot
for comp in CHECKER:
    for scale in ('1x','2x'):
        for renderer,tier in (('webgpu','texture'),('css','dom')):
            k=(f'apple-macos-26.5-{scale}-light-standard', f'checkerboard__{comp}__rest', renderer)
            c=scr.get(k)
            if c is None:
                print(f'| {comp} | {scale} | {tier} | (absent) | | | | | |'); continue
            s=share(c)
            print(f'| {comp} | {scale} | {tier} | {fmt(val(c,"ssimMean"))} | {fmt(val(c,"ssimBand"))} | '
                  f'{fmt(val(c,"ssimInterior"))} | {fmt(val(c,"ssimBandWindows"),0)} | {fmt(val(c,"ssimInteriorWindows"),0)} | '
                  f'{"—" if s is None else f"{100*s:.1f}%"} | {fmt(outside(c)[0])} | {fmt(outside(c)[1],0)} |')
print()
print('### photo and hc-text, rrect-md, light standard')
print()
print('| scene | scale | tier | ssimMean | ssimBand | ssimInterior | band px | interior px | band share | ssimOutside |')
print('|---|---|---|---|---|---|---|---|---|---|')
for scene in ('photo__rrect-md__rest','hc-text__rrect-md__rest'):
    for scale in ('1x','2x'):
        for renderer,tier in (('webgpu','texture'),('css','dom')):
            c=scr.get((f'apple-macos-26.5-{scale}-light-standard',scene,renderer))
            if c is None:
                print(f'| {scene} | {scale} | {tier} | (absent) | | | | | |'); continue
            s=share(c)
            print(f'| {scene} | {scale} | {tier} | {fmt(val(c,"ssimMean"))} | {fmt(val(c,"ssimBand"))} | '
                  f'{fmt(val(c,"ssimInterior"))} | {fmt(val(c,"ssimBandWindows"),0)} | {fmt(val(c,"ssimInteriorWindows"),0)} | '
                  f'{"—" if s is None else f"{100*s:.1f}%"} | {fmt(outside(c)[0])} |')

# whole-bed distribution of ssimBand - ssimInterior by backdrop class and tier
print()
print('### Whole bed: ssimBand − ssimInterior by backdrop class and tier')
print()
print('| backdrop | tier | cells with both rows | min | median | mean | max | cells band-only | cells no rows |')
print('|---|---|---|---|---|---|---|---|---|')
buckets=collections.defaultdict(list)
bandonly=collections.Counter(); norows=collections.Counter()
for k,c in scr.items():
    backdrop=k[1].split('__')[0]
    if backdrop.endswith('solid'): backdrop='solid'
    tier=c['tier']
    b=val(c,'ssimBand'); i=val(c,'ssimInterior')
    if b is None: norows[(backdrop,tier)]+=1
    elif i is None: bandonly[(backdrop,tier)]+=1
    else: buckets[(backdrop,tier)].append(b-i)
keys=sorted(set(list(buckets)+list(bandonly)+list(norows)))
import statistics
for kk in keys:
    v=sorted(buckets.get(kk,[]))
    if v:
        print(f'| {kk[0]} | {kk[1]} | {len(v)} | {v[0]:+.4f} | {statistics.median(v):+.4f} | {statistics.fmean(v):+.4f} | {v[-1]:+.4f} | {bandonly[kk]} | {norows[kk]} |')
    else:
        print(f'| {kk[0]} | {kk[1]} | 0 | — | — | — | — | {bandonly[kk]} | {norows[kk]} |')
