"""Required exterior rings beside ordinary-fill coverage, without registration fitting.

An encoded body/background unmix is only an occupancy ESTIMATE. Values outside
[0,1] cannot be physical area coverage: a contour with a different level can
produce them. We keep the algebraic length and explicitly refuse to turn it
into a measured glass-path displacement in that case. Opaque coverage is read
on the control's own background/path and is never transferred to glass.
"""
import argparse
import gzip
import json
from pathlib import Path
import sys
import numpy as np
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent))
import native
p=argparse.ArgumentParser();p.add_argument('archive');args=p.parse_args()
w,r=native.guarded(args.archive,('calibration','validation'))
rows=[];profiles=[]
for cell,kind in sorted(r.entries):
 if kind!='statistics':continue
 sid=cell.split('/',1)[1]
 if sid not in r.allowed or native.wave.native_only(w.component(sid)):continue
 records=[a for a in native.archive.recorded_statistics(r,cell) if a['admitted'] and a['protocol']=='normal']
 if not records:continue
 assert len(records)==7
 states=[a['statistics'] for a in records];first=states[0]
 for member,m in enumerate(first['members']):
  deep=np.median([s['members'][member]['deep']['medianRGB'] for s in states],axis=0)
  coverage=m['coverage'];covmap={(b['part'],b['side'],b['bin'],b['shell']):b for b in coverage.get('bins',[])}
  for i,b in enumerate(m['bins']):
   if b['part']=='boundary' or b['shell']<0 or b['status']!='measured':continue
   mean=np.median([s['members'][member]['bins'][i]['meanRGB'] for s in states],axis=0)
   background=np.array(m['noGlassBins'][i]['meanRGB'])
   delta=deep-background;norm=float(delta@delta)
   alpha=float((mean-background)@delta/norm) if norm else None
   per=[float((mean[j]-background[j])/delta[j]) if abs(delta[j])>1e-12 else None for j in range(3)]
   cb=covmap.get((b['part'],b['side'],b['bin'],b['shell']))
   rows.append(dict(cell=cell,member=member,scheme=first['scheme'],pose=first['pose'],scale=first['scale'],role=w.roles[sid],
      part=b['part'],side=b['side'],bin=b['bin'],shell=b['shell'],pixels=b['pixels'],bodyRGB=deep.tolist(),
      nativeMeanRGB=mean.tolist(),noGlassMeanRGB=background.tolist(),signedNativeMinusReferenceRGB=(mean-background).tolist(),
      impliedCoverageRGB=per,impliedCoverageLeastSquaresScalar=alpha,
      physicallyAdmissibleConstantDeepCoverage=alpha is not None and 0<=alpha<=1 and all(v is None or 0<=v<=1 for v in per),
      opaqueCoverageAlpha=None if cb is None else cb['alpha'],opaqueCoveragePixels=None if cb is None else cb['pixels'],
      opaqueControlSceneId=coverage.get('controlSceneId'),opaqueFrameOriginCss=coverage.get('frameOriginCss'),
      qualification='required outside shell, not excluded boundary stratum; implied coverage is algebraic, not a fitted displacement'))
  if first['backgroundKind']!='solid':continue
  background=np.array(first['noGlassFrame']['medianRGB']);delta=deep-background;norm=float(delta@delta)
  if norm==0:continue
  for side,pr in m['profiles'].items():
   op=coverage.get('edges',{}).get(side,{})
   if pr['status']!='measured' or op.get('status')!='measured':continue
   means=np.median([s['members'][member]['profiles'][side]['meanRGB'] for s in states],axis=0)
   alpha=(means-background)@delta/norm;coords=np.array(pr['coords'],float)
   outside=np.clip(pr['pathEdge']-coords if pr['inward']>0 else coords+1-pr['pathEdge'],0,1)
   owncoords=np.array(op['coords'],float)
   ownoutside=np.clip(op['pathEdge']-owncoords if op['inward']>0 else owncoords+1-op['pathEdge'],0,1)
   opaquealpha=np.array(op['meanRGB']);exterior=outside>0
   valid=bool(np.all((alpha[exterior]>=0)&(alpha[exterior]<=1)))
   profiles.append(dict(cell=cell,member=member,scheme=first['scheme'],pose=first['pose'],scale=first['scale'],role=w.roles[sid],side=side,mode=pr['mode'],
     glassSuppliedEdgeDevicePx=pr['pathEdge'],opaqueSuppliedEdgeDevicePx=op['pathEdge'],
     opaqueMeasuredEdgeDevicePx=op['measuredEdge'],opaqueOffsetDevicePx=op['offset'],
     opaqueExtraFilledLengthDevicePx=float(opaquealpha@ownoutside),
     algebraicGlassExtraLengthDevicePx=float(alpha@outside),
     physicalGlassExtraLengthDevicePx=float(alpha@outside) if valid else None,
     glassOccupancyStatus='conditional-constant-deep-estimate' if valid else 'UNIDENTIFIABLE-not-constant-deep-coverage',
     exteriorImpliedAlphaRange=[float(alpha[exterior].min()),float(alpha[exterior].max())],
     coords=pr['coords'],glassImpliedAlpha=alpha.tolist(),nativeMeanRGB=means.tolist(),
     noGlassRGB=background.tolist(),bodyRGB=deep.tolist(),opaqueProfile=op,
     qualification='No per-run alignment or opaque-to-glass registration transfer. Encoded constant-body mixture only; another boundary colour invalidates occupancy.'))
print(json.dumps(dict(inventorySha256=r.generation,rawRootDenied=str(Path.home()/'vitrea-w39'),diagnosticOnly=True,
 rows=rows,profiles=profiles),allow_nan=False))
