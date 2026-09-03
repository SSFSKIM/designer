"""W12 G2 whole-bed scan: the scratch matrix against the 0.3.0 bed, the stops of claims 5.51 section 3."""
import json, sys, os
import numpy as np
from PIL import Image
T='/Users/new/.claude/jobs/5c70e47f/tmp/w12'
R='/Users/new/Developer/GitHub/designer'
OLD=json.load(open('/Users/new/.claude/jobs/5c70e47f/tmp/matrix-w11c-g2-close.json'))['cells']
NEW=json.load(open(f'{T}/matrix-g2.json'))['cells']
def key(c): return (c['key']['profileKey'], c['key']['web']['renderer'], c['key']['sceneId'])
def latest(cells):
    out={}
    for c in cells:
        k=key(c)
        if k not in out or c['capturedAt']>out[k]['capturedAt']: out[k]=c
    return out
old=latest(OLD); new=latest(NEW)
print(f'cells: old {len(old)} new {len(new)}; missing in new: {sorted(set(old)-set(new))[:5]} ({len(set(old)-set(new))}); extra: {len(set(new)-set(old))}')
def m(c,ax,k):
    v=c.get(ax,{}).get(k); return v['value'] if isinstance(v,dict) else None
def backdrop(scene): return scene.split('__')[0]
def cls(scene):
    b=backdrop(scene)
    if b in ('light-solid','dark-solid','mid-dark-solid'): return 'solid'
    return b
rows=[]
for k in sorted(set(old)&set(new)):
    o,n=old[k],new[k]
    d=lambda ax,kk: (None if m(o,ax,kk) is None or m(n,ax,kk) is None else m(n,ax,kk)-m(o,ax,kk))
    rows.append((k, m(o,'perceptual','ssimMean'), m(n,'perceptual','ssimMean'), d('perceptual','ssimMean'), d('perceptual','oklabDeltaEMean'), d('perceptual','oklabDeltaEP95'), d('material','interiorMeanWeb'), d('shape','silhouetteIoU'), d('shape','contourDistanceP95')))
print('\n== class summary (max |Δ| over cells): class, tier, n, ΔSSIM, Δ(ΔE mean), Δ(ΔE p95), Δlevel')
import collections
agg=collections.defaultdict(list)
for r in rows: agg[(cls(r[0][2]), r[0][1])].append(r)
for (c,t),rs in sorted(agg.items()):
    mx=lambda i: max((abs(r[i]) for r in rs if r[i] is not None), default=0)
    print(f'  {c:13s} {t:7s} n={len(rs):3d}  ΔSSIM {mx(3):.4f}  ΔΔE {mx(4):.4f}  ΔΔEp95 {mx(5):.4f}  Δlevel {mx(6):.4f}')
print('\n== cells with |ΔSSIM| > 0.005 (profile, renderer, scene: before → after)')
for r in sorted(rows, key=lambda r: -(abs(r[3]) if r[3] else 0)):
    if r[3] is not None and abs(r[3])>0.005: print(f'  {r[0][0]:44s} {r[0][1]:6s} {r[0][2]:46s} {r[1]:.4f} → {r[2]:.4f} ({r[3]:+.4f})')
print('\n== checkerboard texture rows before → after (prediction)')
pred={('1x','rrect-md'):0.970,('1x','rrect-ml'):0.946,('1x','rrect-lg'):0.942,('2x','rrect-md'):0.950,('2x','rrect-ml'):0.918,('2x','rrect-lg'):0.918,('1x','capsule-button'):0.985,('2x','capsule-button'):0.983}
for scale in ('1x','2x'):
    for comp in ('rrect-sm','capsule-button','rrect-md','rrect-ml','rrect-lg','glass-over-glass','toolbar-group'):
        k=(f'apple-macos-26.5-{scale}-light-standard','webgpu',f'checkerboard__{comp}__rest')
        if k in old and k in new:
            print(f'  {scale} {comp:17s} {m(old[k],"perceptual","ssimMean"):.4f} → {m(new[k],"perceptual","ssimMean"):.4f}   predicted {pred.get((scale,comp),"—")}')
print('\n== captures: max code-value delta per class/renderer, and CSS identity')
def cap(root,prof,scene,rend): return f'{root}/{prof}/{scene}/{scene}__{rend}.png'
capagg=collections.defaultdict(lambda:[0,0,0])  # n, changed, maxdelta
worst=[]
for k in sorted(set(old)&set(new)):
    prof,rend,scene=k
    a=cap(f'{R}/packages/calibration/web-captures',prof,scene,rend); b=cap(f'{T}/web-captures-g2',prof,scene,rend)
    if not (os.path.exists(a) and os.path.exists(b)): continue
    A=np.asarray(Image.open(a).convert('RGBA')).astype(int); B=np.asarray(Image.open(b).convert('RGBA')).astype(int)
    if A.shape!=B.shape: print('  shape mismatch',k); continue
    dd=int(np.abs(A-B).max()); ch=int((np.abs(A-B).max(axis=2)>0).sum())
    e=capagg[(cls(scene),rend)]; e[0]+=1; e[1]+= (dd>0); e[2]=max(e[2],dd)
    worst.append((dd,ch,k))
for (c,r),(n,chg,mx) in sorted(capagg.items()): print(f'  {c:13s} {r:6s} n={n:3d} changed={chg:3d} max code value={mx}')
print('  CSS captures that differ:', [(k, d, ch) for d,ch,k in worst if k[1]=='css' and d>0][:10])
print('  solid GPU captures that differ by > 1:', [(k, d) for d,ch,k in worst if cls(k[2])=='solid' and k[1]=='webgpu' and d>1][:10])
print('\n== small-span texture rows (stop: below the 0.3.0 SSIM by > 0.005)')
for k in sorted(set(old)&set(new)):
    if k[1]!='webgpu': continue
    if any(x in k[2] for x in ('rrect-sm','capsule-button','toolbar-group')):
        o=m(old[k],'perceptual','ssimMean'); n=m(new[k],'perceptual','ssimMean')
        if o is not None and n is not None and n < o-0.005: print('  STOP', k, f'{o:.4f} → {n:.4f}')
print('  (done)')
