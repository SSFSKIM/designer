"""W13 X6 baseline: the scratch bed against the canonical matrix, and the four-way SSIM split."""
import json, collections, statistics

CANON='/Users/new/Developer/GitHub/designer/packages/calibration/results/matrix.json'
SCRATCH='/Users/new/.claude/jobs/5c70e47f/tmp/w13/matrix-x6-baseline.json'
NEW={'ssimBand','ssimBandWindows','ssimInterior','ssimInteriorWindows','ssimOutside','ssimOutsideWindows'}

def load(p):
    m=json.load(open(p)); out={}
    for c in m['cells']:
        k=(c['key']['profileKey'], c['key']['sceneId'], c['key']['web']['renderer'])
        if k not in out or c['capturedAt']>out[k]['capturedAt']: out[k]=c
    return m,out

cm,canon=load(CANON); sm,scr=load(SCRATCH)
print('canonical schema',cm['schemaVersion'],len(canon),'cells; scratch schema',sm['schemaVersion'],len(scr),'cells')

def walk(node, path, acc):
    if isinstance(node,dict):
        if set(node.keys())=={'value','units'}: acc[path]=(node['value'],node['units']); return
        for k,v in node.items(): walk(v,path+'.'+k,acc)
    elif isinstance(node,list):
        for i,v in enumerate(node): walk(v,path+f'[{i}]',acc)
    else: acc[path]=node

print('cells in canonical not in scratch:',len(set(canon)-set(scr)))
print('cells in scratch not in canonical:',len(set(scr)-set(canon)))
diffs=[]; worst=0.0; compared=0
for k,c in canon.items():
    if k not in scr: continue
    a={}; b={}
    walk({x:y for x,y in c.items() if x!='capturedAt'},'',a)
    walk({x:y for x,y in scr[k].items() if x!='capturedAt'},'',b)
    for p,v in a.items():
        if p not in b: diffs.append((k,p,v,'ABSENT')); continue
        w=b[p]
        if isinstance(v,tuple) and isinstance(w,tuple):
            compared+=1
            if v[1]!=w[1] or v[0]!=w[0]:
                d=abs(v[0]-w[0]); worst=max(worst,d); diffs.append((k,p,v[0],w[0]))
        elif v!=w: diffs.append((k,p,v,w))
    for p in b:
        if p not in a and p.rsplit('.',1)[-1] not in NEW: diffs.append((k,p,'ABSENT',b[p]))
print(f'compared {compared} metric values; {len(diffs)} differences; worst |delta| = {worst!r}')
for d in diffs[:40]: print('  DIFF',d)

def val(cell,name):
    v=cell.get('perceptual',{}).get(name)
    return None if v is None else v['value']

def fmt(x,n=4): return '—' if x is None else f'{x:.{n}f}'
def pct(x): return '—' if x is None else f'{100*x:.1f}%'

def split(cell):
    """band / interior / outside / far field: (mean, windows, deficit) each."""
    w,h=cell['key']['web']['pixelSize']; total=(w-10)*(h-10)
    out={}
    counted=0; countedSum=0.0
    for name in ('Band','Interior','Outside'):
        m=val(cell,'ssim'+name); n=val(cell,'ssim'+name+'Windows')
        if m is None: out[name.lower()]=(None,0,0.0); continue
        out[name.lower()]=(m,n,(1-m)*n); counted+=n; countedSum+=m*n
    far=total-counted
    if far>0:
        fm=(val(cell,'ssimMean')*total-countedSum)/far
        out['far']=(fm,far,(1-fm)*far)
    else: out['far']=(None,0,0.0)
    out['total']=total
    return out

CHECKER=['rrect-sm','capsule-button','rrect-md','rrect-ml','rrect-lg','glass-over-glass','toolbar-group']
CELLS=[(f'checkerboard__{c}__rest',c) for c in CHECKER]+[('photo__rrect-md__rest','photo rrect-md'),('hc-text__rrect-md__rest','hc-text rrect-md')]

print()
print('### Checkerboard cells, light standard')
print()
print('| cell | scale | tier | ssimMean | ssimBand | ssimInterior | ssimOutside | band px | interior px | outside px | band share of silhouette deficit | outside share of crop deficit |')
print('|---|---|---|---|---|---|---|---|---|---|---|---|')
for scene,label in CELLS:
    if not scene.startswith('checkerboard'): continue
    for scale in ('1x','2x'):
        for r,t in (('webgpu','texture'),('css','dom')):
            c=scr[(f'apple-macos-26.5-{scale}-light-standard',scene,r)]
            s=split(c)
            sil=s['band'][2]+s['interior'][2]
            crop=sil+s['outside'][2]+s['far'][2]
            print(f'| {label} | {scale} | {t} | {fmt(val(c,"ssimMean"))} | {fmt(s["band"][0])} | {fmt(s["interior"][0])} | '
                  f'{fmt(s["outside"][0])} | {s["band"][1] or "—"} | {s["interior"][1] or "—"} | {s["outside"][1] or "—"} | '
                  f'{pct(None if sil==0 else s["band"][2]/sil)} | {pct(None if crop==0 else s["outside"][2]/crop)} |')

print()
print('### photo and hc-text, rrect-md, light standard')
print()
print('| scene | scale | tier | ssimMean | ssimBand | ssimInterior | ssimOutside | band share of silhouette deficit | outside share of crop deficit |')
print('|---|---|---|---|---|---|---|---|---|')
for scene,label in CELLS:
    if scene.startswith('checkerboard'): continue
    for scale in ('1x','2x'):
        for r,t in (('webgpu','texture'),('css','dom')):
            c=scr[(f'apple-macos-26.5-{scale}-light-standard',scene,r)]
            s=split(c); sil=s['band'][2]+s['interior'][2]; crop=sil+s['outside'][2]+s['far'][2]
            print(f'| {label} | {scale} | {t} | {fmt(val(c,"ssimMean"))} | {fmt(s["band"][0])} | {fmt(s["interior"][0])} | '
                  f'{fmt(s["outside"][0])} | {pct(s["band"][2]/sil)} | {pct(s["outside"][2]/crop)} |')

print()
print('### The four-way split as deficit points ((1 - ssim) x windows) and shares of the crop')
print()
print('| cell | scale | tier | band | interior | outside | far field | band % | interior % | outside % | far % |')
print('|---|---|---|---|---|---|---|---|---|---|---|')
for scene,label in CELLS:
    for scale in ('1x','2x'):
        for r,t in (('webgpu','texture'),('css','dom')):
            c=scr[(f'apple-macos-26.5-{scale}-light-standard',scene,r)]
            s=split(c)
            d=[s['band'][2],s['interior'][2],s['outside'][2],s['far'][2]]
            tot=sum(d)
            print(f'| {label} | {scale} | {t} | ' + ' | '.join(f'{x:.0f}' for x in d) + ' | '
                  + ' | '.join(pct(x/tot) for x in d) + ' |')

print()
print('### Whole bed: ssimBand − ssimInterior by backdrop class and tier')
print()
print('| backdrop | tier | cells with both rows | min | median | mean | max | band-only cells | cells with no rows |')
print('|---|---|---|---|---|---|---|---|---|')
buckets=collections.defaultdict(list); bandonly=collections.Counter(); norows=collections.Counter()
neg=pos=0; positives=[]
for k,c in scr.items():
    backdrop=k[1].split('__')[0]
    if backdrop.endswith('solid'): backdrop='solid'
    tier=c['tier']; b=val(c,'ssimBand'); i=val(c,'ssimInterior')
    if b is None: norows[(backdrop,tier)]+=1
    elif i is None: bandonly[(backdrop,tier)]+=1
    else:
        buckets[(backdrop,tier)].append(b-i)
        if b-i<0: neg+=1
        else: pos+=1; positives.append((round(b-i,4),k,tier))
for kk in sorted(set(list(buckets)+list(bandonly)+list(norows))):
    v=sorted(buckets.get(kk,[]))
    if v: print(f'| {kk[0]} | {kk[1]} | {len(v)} | {v[0]:+.4f} | {statistics.median(v):+.4f} | {statistics.fmean(v):+.4f} | {v[-1]:+.4f} | {bandonly[kk]} | {norows[kk]} |')
    else: print(f'| {kk[0]} | {kk[1]} | 0 | — | — | — | — | {bandonly[kk]} | {norows[kk]} |')
print()
print('band worse on',neg,'of',neg+pos,'cells with both rows; band better on',pos)
for x in sorted(positives,reverse=True): print('  ',x)

print()
print('### Whole bed: ssimOutside − ssimBand by backdrop class and tier (the two halves of one edge)')
print()
print('| backdrop | tier | n | min | median | mean | max |')
print('|---|---|---|---|---|---|---|')
b2=collections.defaultdict(list)
for k,c in scr.items():
    backdrop=k[1].split('__')[0]
    if backdrop.endswith('solid'): backdrop='solid'
    o=val(c,'ssimOutside'); b=val(c,'ssimBand')
    if o is not None and b is not None: b2[(backdrop,c['tier'])].append(o-b)
for kk in sorted(b2):
    v=sorted(b2[kk])
    print(f'| {kk[0]} | {kk[1]} | {len(v)} | {v[0]:+.4f} | {statistics.median(v):+.4f} | {statistics.fmean(v):+.4f} | {v[-1]:+.4f} |')
