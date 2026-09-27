"""A coefficient-independent support check before fitting the declared edge grid.

Every line is zero beyond2.4 CSS px; every shoulder hat is zero at and beyond12.
The signed distance is 1-Lipschitz, so a pixel centre at least12+sqrt(.5)/scale
inside has zero basis at every point of its pixel, including 8x8 and16x16 nodes.
Such a required bin is predicted at its measured deep conditioner for every
coefficient, width, exponent and quadrature. This is a necessary survival test,
not a substitute least-squares fit or a new candidate family.
"""
import argparse
import gzip
import json
import math
from pathlib import Path
import sys
import numpy as np
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent))
import native

p=argparse.ArgumentParser();p.add_argument('archive');args=p.parse_args()
w,r=native.guarded(args.archive,('calibration','validation'))
rows=[]
for cell,kind in sorted(r.entries):
 if kind!='crop':continue
 sid=cell.split('/',1)[1]
 if sid not in r.allowed or native.wave.native_only(w.component(sid)):continue
 runs,states=native.archive.unbundle(r.read(cell,'crop'))
 runs=[run for run in runs if run['admitted'] and run['protocol']=='normal']
 if not runs:continue
 assert len(runs)==7
 stats=json.loads(gzip.decompress(r.read(cell,'statistics')))['statistics']
 chosen=sorted({run['state'] for run in runs})
 payloads={key:native.archive.unpack(states[key]) for key in chosen}
 first=payloads[chosen[0]];scale=first['scale']
 shapes=native.readers.shapes_of(first['component'])
 geo=native.readers.geometry(first['rgb'].shape[:2],shapes,scale)
 for member,shape in enumerate(shapes):
  deep=np.median([stats[run['state']]['members'][member]['deep']['medianRGB'] for run in runs],axis=0)
  bins,labels=native.readers.edge_bins(geo,member)
  for index,bn in enumerate(bins):
   if bn['part']=='boundary' or bn['shell']>=0:continue
   mask=labels==index
   if not mask.any() or np.any(geo.d[mask]/scale> -12-math.sqrt(.5)/scale):continue
   residual={key:abs(payloads[key]['rgb'][mask].astype(float)-deep).mean(axis=0) for key in chosen}
   means=np.array([payloads[run['state']]['rgb'][mask].mean(axis=0) for run in runs])
   bar=.5+.5*np.ptp(means,axis=0);tau=np.maximum(1,bar)
   median_pixels=np.median(np.stack([payloads[run['state']]['rgb'][mask] for run in runs]),axis=0)
   error=abs(median_pixels-deep).mean(axis=0)
   rows.append(dict(cell=cell,role=w.roles[sid],scheme=first['scheme'],pose=first['pose'],scale=scale,
      member=member,part=bn['part'],side=bn['side'],bin=bn['bin'],shell=bn['shell'],pixels=bn['pixels'],status=bn['status'],
      depthCss=bn['depthCss'],bodyRGB=deep.tolist(),nativeMeanRGB=median_pixels.mean(axis=0).tolist(),
      residualRGB=error.tolist(),toleranceRGB=tau.tolist(),
      maximumCentreDistanceCSS=float(np.max(geo.d[mask]/scale)),
      repeatResidualRGB=[residual[run['state']].tolist() for run in runs],
      failedChannels=np.flatnonzero(error>tau+1e-8).tolist() if bn['status']=='measured' else []))
summary=[]
for scheme in ['light','dark']:
 for pose in ['rest','inactive']:
  for scale in [1,2]:
   for role in ['calibration','validation']:
    rr=[b for b in rows if b['scheme']==scheme and b['pose']==pose and b['scale']==scale and b['role']==role and b['status']=='measured']
    worst=max(rr,key=lambda b:max(b['residualRGB']))
    summary.append(dict(scheme=scheme,pose=pose,scale=scale,role=role,bins=len(rr),failedBins=sum(bool(b['failedChannels']) for b in rr),
       maximumCodes=max(worst['residualRGB']),worst=worst))
print(json.dumps(dict(inventorySha256=r.generation,rawRootDenied=str(Path.home()/'vitrea-w39'),
 declaredSupportCSS=12,quadratureIndependent=True,rows=rows,summary=summary),allow_nan=False))
