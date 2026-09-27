"""Guarded archive to disposable fitting arrays; never a new native capture.

The cache is a reproducible projection, not the record. Every input retains its
archive state hashes, inventory and attested geometry. No holdout cache is made.
"""
import argparse
import dataclasses
import gzip
import hashlib
import json
from pathlib import Path
import sys
import numpy as np
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent))
import native
import basis

p=argparse.ArgumentParser();p.add_argument('archive');p.add_argument('cache');args=p.parse_args()
cache=Path(args.cache).resolve();cache.mkdir(exist_ok=False)
w,r=native.guarded(args.archive,('calibration','validation'))
records=[];geometries={}
for cell,kind in sorted(r.entries):
 if kind!='crop':continue
 sid=cell.split('/',1)[1]
 if sid not in r.allowed or native.wave.native_only(w.component(sid)):continue
 runs,states=native.archive.unbundle(r.read(cell,'crop'))
 runs=[run for run in runs if run['admitted'] and run['protocol']=='normal']
 if not runs:continue
 assert len(runs)==7
 stats=json.loads(gzip.decompress(r.read(cell,'statistics')))['statistics']
 chosen=sorted({run['state'] for run in runs});payloads={key:native.archive.unpack(states[key]) for key in chosen}
 first=payloads[chosen[0]];scale=first['scale'];shapes=native.readers.shapes_of(first['component'])
 geo=native.readers.geometry(first['rgb'].shape[:2],shapes,scale)
 for member,shape in enumerate(shapes):
  bins,labels=native.readers.edge_bins(geo,member)
  required=len(bins)-4
  ix=np.flatnonzero((labels>=0)&(labels<required));binids=labels.ravel()[ix]
  yy,xx=np.unravel_index(ix,labels.shape);xy=np.column_stack((xx,yy))
  geometry=dict(shape=dataclasses.asdict(shape),scale=scale,xy=xy.tolist())
  gsha=hashlib.sha256(json.dumps(geometry,sort_keys=True).encode()).hexdigest()[:16]
  if gsha not in geometries:
   t,ny=basis.samples(shape,xy,scale,8,native.readers)
   np.savez_compressed(cache/(gsha+'.npz'),t=t,ny=ny,binids=binids,xy=xy,
       inside=geo.d.ravel()[ix]<0)
   geometries[gsha]=dict(shape=dataclasses.asdict(shape),scale=scale,bins=bins[:required])
  deeps=np.array([stats[run['state']]['members'][member]['deep']['medianRGB'] for run in runs])
  deep=np.median(deeps,axis=0)
  nativepix=np.stack([payloads[k]['rgb'].reshape(-1,3)[ix] for k in chosen]).astype(float)
  stateix=np.array([chosen.index(run['state']) for run in runs])
  median=np.median(nativepix[stateix],axis=0)
  # Bar uses all seven bin means before any plurality. Validate against the record.
  bar=[]
  for bi,bn in enumerate(bins[:required]):
   if not bn['pixels']:bar.append([.5]*3);continue
   mask=binids==bi
   means=np.array([nativepix[chosen.index(run['state'])][mask].mean(0) for run in runs])
   for run,mean in zip(runs,means):
    recorded=stats[run['state']]['members'][member]['bins'][bi]['meanRGB']
    np.testing.assert_allclose(mean,recorded,rtol=0,atol=1e-12)
   bar.append((.5+.5*np.ptp(means,axis=0)).tolist())
  rid=hashlib.sha256((cell+str(member)).encode()).hexdigest()[:16]
  np.savez_compressed(cache/(rid+'.npz'),native=median,states=nativepix,stateix=stateix,
      backdrop=first['noGlass'].reshape(-1,3)[ix].astype(float),deep=deep,bar=np.array(bar))
  records.append(dict(id=rid,geometry=gsha,cell=cell,member=member,role=w.roles[sid],scheme=first['scheme'],pose=first['pose'],
      scale=scale,span=min(shape.size),backgroundKind=first['backgroundKind'],stateHashes=chosen,normalRunStateIndices=stateix.tolist()))
  print(cell,member,'prepared',file=sys.stderr,flush=True)
manifest=dict(inventorySha256=r.generation,archive=str(r.root),rawRootDenied=str(Path.home()/'vitrea-w39'),
 records=records,geometries=geometries)
with (cache/'manifest.json').open('x') as f:json.dump(manifest,f)
print(json.dumps(dict(inventorySha256=r.generation,cells=len({r['cell'] for r in records}),members=len(records),
 geometries=len(geometries),cache=str(cache),cacheManifestSha256=hashlib.sha256((cache/'manifest.json').read_bytes()).hexdigest()),indent=2))
