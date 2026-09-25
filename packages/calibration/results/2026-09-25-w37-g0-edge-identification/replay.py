"""W37 memo reproduction, unchanged estimators through W35 guarded readers (§5.181)."""
import sys,json,gzip,io,base64,hashlib,collections
from pathlib import Path
import numpy as np
from PIL import Image
HERE=Path(__file__).resolve().parent; R=HERE.parents[3]; C=R/'packages/calibration'; E=C/'results/2026-09-24-w35-g0-edge-cut'; A=C/'results/2026-09-23-w34-g1-contour-sitting'
sys.path.insert(0,str(E)); import edge
wave=edge.W.default_wave(); probe=wave.reader(A/'probe'); repeat=wave.reader(A/'repeat')
profiles=json.loads(gzip.decompress((E/'profiles.json.gz').read_bytes()))
assert all(wave.roles[r['cell'].split('/')[1]] in ('calibration','validation') for r in profiles)
res=[]; maxdiff=0
for rec in profiles:
 cell=rec['cell']; scene=cell.split('/')[1]
 if rec['backgroundKind']!='solid':continue
 crop=json.loads(gzip.decompress(repeat.read(cell,'crop')))
 run=next(r for r in crop['runs'] if r['admitted'] and r['protocol']=='normal')
 raw=base64.b64decode(crop['states'][run['state']]);assert hashlib.sha256(raw).hexdigest()==run['state']
 p=edge.I.unpack(raw); d,nx,ny,arc,angle,whole=edge.geometry(p); scale=p['scale']
 n=np.asarray(Image.open(io.BytesIO(probe.read(cell,'png'))).convert('RGB'),float)
 beta=np.median(n[d<=-6*scale],0);assert np.array_equal(beta,rec['deep']['nativeMedian'])
 row={'cell':cell,'role':wave.roles[scene],'scale':scale,'deep':beta.tolist(),'rows':[],'angular':[]}
 for label,sel in [('top',~arc&(ny<-.5)),('bottom',~arc&(ny>.5)),('left',~arc&(nx<-.5)),('right',~arc&(nx>.5))]:
  for shell in range(-6*scale,0):
   m=sel&(d>=shell)&(d<shell+1)
   if not m.any():continue
   rgb=n[m].mean(0)
   row['rows'].append({'side':label,'shell':shell,'pixels':int(m.sum()),'rgb':rgb.tolist(),'excess':(rgb-beta).tolist()})
   old=next((s for s in rec['sides'] if s['side']==label and s['shell']==shell),None)
   if old:maxdiff=max(maxdiff,float(abs(rgb-old['nativeRGB']).max()))
 for shell in range(-2*scale,0):
  for b in range(16):
   m=arc&(angle==b)&(d>=shell)&(d<shell+1)&whole
   if not m.any():continue
   rgb=n[m].mean(0);item={'shell':shell,'bin':b,'pixels':int(m.sum()),'excess':(rgb-beta).tolist(),'distanceMeanCss':float(d[m].mean()/scale),'absNyMean':float(abs(ny[m]).mean()),'nySquaredMean':float((ny[m]**2).mean())}
   row['angular'].append(item)
   old=next(x for x in rec['angular'] if x['part']=='arc' and x['shell']==shell and x['bin']==b)
   maxdiff=max(maxdiff,float(abs(rgb-old['wholeNativeRGB']).max()))
 res.append(row)
 print('replayed',cell,flush=True)
output={'source':str(A),'guard':str(edge.G0/'wave.py'),'cells':len(res),'roles':dict(collections.Counter(r['role'] for r in res)),'maxDifferenceFromW35':maxdiff,'rows':res}
edge.save(HERE/'native-replay.json.gz',output)
print('COMPLETE',output['cells'],output['roles'],'maxdiff',maxdiff)
