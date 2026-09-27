import sys
sys.dont_write_bytecode=True
from analyse import *
sys.path.insert(0,'/Users/new/Developer/GitHub/designer/packages/calibration/results/2026-09-26-w39-g2-identification');import native
w,reader=native.guarded(Path('/Users/new/.cache/vitrea-archives/489db938a1e234a772ba7223d24fbaf76d137ef5d9e5b2421ed84a86894426b5/extracted/archive'),('calibration',))
for cell,c in cells.items():
 if c['scene']['background']!='g128' or c['component']!={'kind':'capsule-circular','size':[120,44],'position':[160,140]}:continue
 runs,states=native.archive.unbundle(reader.read(cell,'crop'));runs=[r for r in runs if r['admitted'] and r['protocol']=='normal'];assert len(runs)==7
 ps={k:native.archive.unpack(v) for k,v in states.items() if k in {r['state'] for r in runs}}
 p=ps[runs[0]['state']];s=p['scale'];geo=native.readers.geometry(p['rgb'].shape[:2],native.readers.shapes_of(p['component']),s)
 bs,_=native.readers.edge_bins(geo);print('BOUNDARY',c['scheme'],c['pose'],s,[(b['side'],b['pixels']) for b in bs if b['part']=='boundary'])
 for bn in [0,4,12]:
  mask=~geo.whole&~geo.outside&(geo.angle==bn); means=np.array([ps[r['state']]['rgb'][mask].mean(axis=0) for r in runs]); med=np.median(means,axis=0)
  print('STRADDLE ARC',bn,int(mask.sum()),'RGB',med,'bar',.5+.5*np.ptp(means,axis=0),'distanceRange',np.min(geo.d[mask]),np.max(geo.d[mask]))
