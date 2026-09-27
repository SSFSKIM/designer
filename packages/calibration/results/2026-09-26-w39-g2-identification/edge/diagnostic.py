"""Uniform versus gradient tail diagnostics; no new fit and not a survival test.

The transmission estimate is an encoded secant between the lower and upper
no-glass quartiles in the central d<=-14 domain, measured in the same pixel sets
on glass. It is neither a fitted edge coefficient nor physical linear alpha.
Multiplying it by local no-glass departure estimates the scalar-conditioner's
missing body gradient; any remaining error is still diagnostic, not a new law.
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
W=np.array([.2126,.7152,.0722])
p=argparse.ArgumentParser();p.add_argument('archive');p.add_argument('cache');args=p.parse_args()
support=json.loads(gzip.decompress((HERE/'support.json.gz').read_bytes()))
manifest=json.loads((Path(args.cache)/'manifest.json').read_text())
lookup={(r['cell'],r['member']):r for r in manifest['records']}
rows=[]
for row in support['rows']:
 sid=row['cell'].split('/',1)[1]
 if not sid.startswith(('g128-','g255-','v90-','v270-')):continue
 r=lookup[(row['cell'],row['member'])];g=manifest['geometries'][r['geometry']]
 shape=g['shape'];y=shape['frame_origin'][1]+shape['size'][1]/2
 position={70:'top',140:'centre',210:'bottom'}.get(y,'other')
 rows.append({**row,'backgroundDomain':'uniform' if sid.startswith(('g128-','g255-')) else 'gradient',
              'position':position,'centreY':y})
summary=[]
for scheme in ['light','dark']:
 for pose in ['rest','inactive']:
  for scale in [1,2]:
   for role in ['calibration','validation']:
    for domain in ['uniform','gradient']:
     for position in ['top','centre','bottom']:
      for side in ['top','bottom','left','right','arcs']:
       rr=[r for r in rows if r['scheme']==scheme and r['pose']==pose and r['scale']==scale and r['role']==role
           and r['backgroundDomain']==domain and r['position']==position
           and (r['part']=='arc' if side=='arcs' else r['side']==side) and r['status']=='measured']
       worst=max(rr,key=lambda r:max(r['residualRGB'])) if rr else None
       summary.append(dict(scheme=scheme,pose=pose,scale=scale,role=role,backgroundDomain=domain,position=position,side=side,
          measuredBins=len(rr),status='measured' if rr else 'UNMEASURED-no-admitted-bin-in-this-tail-cut',
          maximumCodes=max(worst['residualRGB']) if worst else None,worst=worst))
w,reader=native.guarded(args.archive,('calibration','validation'))
estimates=[]
for cell in sorted({r['cell'] for r in rows if r['backgroundDomain']=='gradient'}):
 runs,states=native.archive.unbundle(reader.read(cell,'crop'))
 runs=[r for r in runs if r['admitted'] and r['protocol']=='normal'];assert len(runs)==7
 payloads={key:native.archive.unpack(states[key]) for key in {r['state'] for r in runs}}
 first=next(iter(payloads.values()));scale=first['scale'];shapes=native.readers.shapes_of(first['component'])
 geo=native.readers.geometry(first['rgb'].shape[:2],shapes,scale)
 rgb=np.median(np.stack([payloads[r['state']]['rgb'] for r in runs]),axis=0)
 bg=first['noGlass'].astype(float)
 assert all(np.array_equal(bg,p['noGlass']) for p in payloads.values())
 for member,shape in enumerate(shapes):
  centre=(geo.member==member)&(geo.d<=-14*scale)
  bgvalues=bg[centre]@W;lo,hi=np.quantile(bgvalues,[.25,.75])
  low=centre&(bg@W<=lo);high=centre&(bg@W>=hi)
  nativeLow=np.median(rgb[low],axis=0);nativeHigh=np.median(rgb[high],axis=0)
  bgLow=np.median(bg[low],axis=0);bgHigh=np.median(bg[high],axis=0)
  contrast=float((bgHigh-bgLow)@W)
  if contrast<=0:raise ValueError('UNMEASURED gradient transmission: no central reference contrast')
  transmission=float((nativeHigh-nativeLow)@W/contrast)
  bgCentre=np.median(bg[centre],axis=0);nativeCentre=np.median(rgb[centre],axis=0)
  bins,labels=native.readers.edge_bins(geo,member)
  bykey={(b['part'],b['side'],b['bin'],b['shell']):i for i,b in enumerate(bins)}
  for row in rows:
   if row['cell']!=cell or row['member']!=member or row['status']!='measured':continue
   mask=labels==bykey[(row['part'],row['side'],row['bin'],row['shell'])]
   bgMean=bg[mask].mean(axis=0);nativeMean=rgb[mask].mean(axis=0)
   original=nativeMean-np.array(row['bodyRGB']);explained=transmission*(bgMean-bgCentre)
   remainder=original-explained
   estimates.append(dict(cell=cell,member=member,scale=scale,scheme=row['scheme'],pose=row['pose'],position=row['position'],
     part=row['part'],side=row['side'],bin=row['bin'],shell=row['shell'],pixels=row['pixels'],
     centralDomain='d<=-14 CSS px, own member',centrePixels=int(centre.sum()),
     lowerQuartilePixels=int(low.sum()),upperQuartilePixels=int(high.sum()),
     nativeLowRGB=nativeLow.tolist(),nativeHighRGB=nativeHigh.tolist(),noGlassLowRGB=bgLow.tolist(),noGlassHighRGB=bgHigh.tolist(),
     encodedSecantTransmission=transmission,noGlassCentreRGB=bgCentre.tolist(),nativeCentreRGB=nativeCentre.tolist(),
     conditionerRGB=row['bodyRGB'],noGlassShellMeanRGB=bgMean.tolist(),nativeShellMeanRGB=nativeMean.tolist(),
     observedSignedExcessRGB=original.tolist(),estimatedLocalBodyContributionRGB=explained.tolist(),
     remainingSignedExcessRGB=remainder.tolist(),assumptions='locally affine encoded response and a spatially uniform secant; central boundary contamination and code quantisation remain possible; not fitted, not survival'))
print(json.dumps(dict(inventorySha256=reader.generation,diagnosticOnly=True,supportRows=rows,stratified=summary,
 gradientEstimates=estimates),allow_nan=False))
