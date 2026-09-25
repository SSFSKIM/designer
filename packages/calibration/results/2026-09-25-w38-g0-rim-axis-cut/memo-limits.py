import sys,json,gzip,base64
from pathlib import Path
import numpy as np
sys.dont_write_bytecode=True
R=Path(__file__).resolve().parents[4];C=R/'packages/calibration';S=Path(__file__).resolve().parent/'memo-reproduction';G=C/'results/2026-09-25-w37-g0-edge-identification'
sys.path.insert(0,str(C/'results/2026-09-24-w35-g0-edge-cut'));import edge
assert not (S/'limits.json').exists(), 'refuse to overwrite recorded replay'
scores=json.loads((S/'scores.json').read_text());rep=json.loads((S/'reproduction.json').read_text());native=json.loads(gzip.decompress((G/'native-replay.json.gz').read_bytes()))['rows'];native={r['cell']:r for r in native if r['role']=='calibration' and r['cell'].endswith('__rest')}
# Necessary-condition bound for any scalar k*body+q with 0<=k<=1, q unrestricted.
# Target must fit every channel within epsilon after clipping and sRGB encoding.
def feasible(b,t,e):
 lo=edge.decode(np.maximum(t-e,0)/255); hi=edge.decode(np.minimum(t+e,255)/255)
 lo=np.where(t-e<=0,-np.inf,lo);hi=np.where(t+e>=255,np.inf,hi)
 kl,kh=0.,1.
 for i in range(3):
  for j in range(3):
   d=b[i]-b[j];rhs=lo[i]-hi[j]
   if not np.isfinite(rhs):continue
   if abs(d)<1e-14:
    if rhs>1e-14:return False
   elif d>0:kl=max(kl,rhs/d)
   else:kh=min(kh,rhs/d)
 return kl<=kh+1e-14
bounds=[]
for r in rep['rows']:
 if not r['admissible'] or r['part']!='straight' or '/grey-' in r['cell'] or '__circular-120__' not in r['cell']:continue
 b=np.array(native[r['cell']]['deep']);t=b+np.array(r['nativeExcessRGB']);bl=edge.decode(b/255);lo,hi=0.,255.
 for _ in range(55):
  mid=(lo+hi)/2
  if feasible(bl,t,mid):hi=mid
  else:lo=mid
 bounds.append({'cell':r['cell'],'shell':r['shell'],'bin':r['bin'],'nativeDeep':b.tolist(),'nativeTarget':t.tolist(),'minimaxLowerBoundCodes':hi})
channel=[]
for scheme in ['light','dark']:
 rows=[r for r in scores['bins'] if r['scheme']==scheme and r['circular']];delta=np.array([r['residualRGB'] for r in rows])-np.array([r['oldResidualRGB'] for r in rows]);channel.append({'scheme':scheme,'better':int((delta<-.5).sum()),'same':int((abs(delta)<=.5).sum()),'worse':int((delta>.5).sum()),'total':delta.size})
cell='apple-macos-27.0-2x-light-standard-glass0.5/grey-128__circular-120__rest';b=np.array(native[cell]['deep']);best=scores['fits'][0]['best']
reader=edge.W.default_wave().reader(edge.G1/'repeat');crop=json.loads(gzip.decompress(reader.read(cell,'crop')));run=next(r for r in crop['runs'] if r['admitted'] and r['protocol']=='normal');p=edge.I.unpack(base64.b64decode(crop['states'][run['state']]));dd,nx,ny,arc,angle,whole=edge.geometry(p)
u=(44-32)/(96-32);k=u*u*(3-2*u);pred=[];depths=[]
for sh in [-2,-1]:
 mask=(~arc)&(angle==12)&(dd>=sh)&(dd<sh+1)&whole;d=dd[mask]/2;depths.append([float(d.min()),float(d.max())]);outrow=edge.forward(edge.decode(b/255),d,1,width=best['widths'][1],a=best['a'],g=best['g'],shadow_depth=best['shadowDepth'],shadow_alpha=best['shadowAlpha'],shadow_reach=8*(1+1.6*k),lit=np.maximum(abs(ny[mask])*np.sqrt(2),1e-6)**best['exponent'])['encoded']-b;pred.append(outrow.mean(0).tolist())

out={'scope':'Calibration-only straight-row necessary bound, any neutral q and physical occlusion 0<=k<=1; not a bound allowing signed amplification k>1','worstBounds':sorted(bounds,key=lambda r:r['minimaxLowerBoundCodes'],reverse=True)[:12], 'channelComparisons':channel, 'grey128Best2xTopExcess':pred, 'grey128TopDepthRangesCss':depths, 'widthOneCentreWeights':[.0625,.5625], 'widthOneAreaMeanWeights':[1/12,7/12]}
print(json.dumps(out,indent=2))
# A weaker but bin-MAE-valid bound, even if q and k vary across the row.
# For concave sRGB encoding, max encoded channel contrast at linear difference D
# is encode(D)-encode(0); additive neutral q cannot increase the linear gap.
contrast=[]
for r in bounds:
 body=np.array(r['nativeDeep']);target=np.array(r['nativeTarget']);bl=edge.decode(body/255)
 for high in range(3):
  for low in range(3):
   if bl[high]<=bl[low]:continue
   maximum=float(255*edge.encode(bl[high]-bl[low]));floor=max(0.,float((target[high]-target[low]-maximum)/2))
   if floor>0:contrast.append({**r,'channels':[high,low],'maximumPredictedEncodedContrast':maximum,'binMAELowerBoundCodes':floor})
out['binContrastBounds']=sorted(contrast,key=lambda r:r['binMAELowerBoundCodes'],reverse=True)[:8]
(S/'limits.json').write_text(json.dumps(out,indent=2));print('CERTIFIED BIN BOUND',out['binContrastBounds'][:1])
