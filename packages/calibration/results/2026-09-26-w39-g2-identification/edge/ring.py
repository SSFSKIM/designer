"""Measured exterior contour table, with repeat bars; no fit or registration.

Declared circular120x44 placements/columns and radius22 rrect ladder only,
backgrounds grey128/grey255/vertical gradients, calibration and validation.
All16 arc normals and four sides are explicit, including deficient populations.
At1x shells0/1; at2x shells0..3. These are required outside bins, not the
straddling-pixel diagnostic boundary stratum. Their observations do not identify
a physical extra width or a body/background mixture.
"""
import json
from pathlib import Path
import sys
import numpy as np
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent))
import native
w,r=native.guarded(sys.argv[1],('calibration','validation'))
rows=[]
for cell,kind in sorted(r.entries):
 if kind!='statistics':continue
 sid=cell.split('/',1)[1]
 if sid not in r.allowed or native.wave.native_only(w.component(sid)):continue
 scene=w.scenes[sid];bg=scene['background'];component=w.component(sid)
 if bg not in ['g128','g255','v90','v270']:continue
 items=component['items'] if component['kind']=='column' else [component]
 keep=[i for i,s in enumerate(items) if (s['kind']=='capsule-circular' and s['size']==[120,44]) or
        (s['kind']=='rrect' and s.get('radius')==22)]
 if not keep:continue
 records=[a for a in native.archive.recorded_statistics(r,cell) if a['admitted'] and a['protocol']=='normal']
 if not records:continue
 assert len(records)==7
 stats=[a['statistics'] for a in records];first=stats[0];scale=first['scale']
 for member in keep:
  ms=[s['members'][member] for s in stats];shape=first['shapes'][member]
  deep=np.median([m['deep']['medianRGB'] for m in ms],axis=0)
  for index,b in enumerate(ms[0]['bins']):
   if b['part']=='boundary' or b['shell']<0 or b['shell']>=2*scale:continue
   base=dict(cell=cell,member=member,role=w.roles[sid],scheme=first['scheme'],pose=first['pose'],scale=scale,
       background=bg,componentKind=items[member]['kind'],sizeCss=items[member]['size'],
       frameOriginCss=shape['frameOriginCss'],part=b['part'],side=b['side'],bin=b['bin'],normalDegrees=b['bin']*22.5,
       shell=b['shell'],pixels=b['pixels'],geometryStatus=b['status'],deepRGB=deep.tolist(),
       opaqueControl=ms[0]['coverage'].get('controlSceneId'))
   if not b['pixels']:
    rows.append({**base,'status':'UNMEASURED-absent-bin','signedMeanRGB':None,'barRGB':None});continue
   means=np.array([m['bins'][index]['meanRGB'] for m in ms]);bgmeans=np.array([m['noGlassBins'][index]['meanRGB'] for m in ms])
   mn=np.min([m['bins'][index]['minimumRGB'] for m in ms],axis=0);mx=np.max([m['bins'][index]['maximumRGB'] for m in ms],axis=0)
   cov=[v for v in ms[0]['coverage']['bins'] if (v['part'],v['side'],v['bin'],v['shell'])==(b['part'],b['side'],b['bin'],b['shell'])]
   rows.append({**base,'status':'diagnostic-observed' if b['status']=='measured' else 'UNMEASURED-population',
     'nativeMeanRGB':np.median(means,axis=0).tolist(),'noGlassMeanRGB':np.median(bgmeans,axis=0).tolist(),
     'signedMeanRGB':np.median(means-bgmeans,axis=0).tolist(),'barRGB':(.5+.5*np.ptp(means,axis=0)).tolist(),
     'runSignedMeansRGB':(means-bgmeans).tolist(),'nativeMinimumRGB':mn.tolist(),'nativeMaximumRGB':mx.tolist(),
     'channelsContainingCensoredPixels':np.flatnonzero((mn<=5)|(mx>=250)).tolist(),
     'opaqueCoverageAlpha':cov[0]['alpha'] if cov else None})
print(json.dumps(dict(inventorySha256=r.generation,rawRootDenied=str(Path.home()/'vitrea-w39'),
 fitted=False,scope='circular120x44 placements and columns; radius22 rrect44/64/96; only declared background/geometry pairs',
 absentDesign='No rrect/gradient pair was declared; grey255 bottom and circular200 witness are holdout and unread.',
 rows=rows),allow_nan=False))
