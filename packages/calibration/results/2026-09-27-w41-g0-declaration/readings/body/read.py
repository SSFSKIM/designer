import sys
sys.dont_write_bytecode=True
from pathlib import Path
import json,gzip,re
import numpy as np
R=Path('/Users/new/Developer/GitHub/designer/packages/calibration/results')
G0=R/'2026-09-26-w39-g0-colour-edge-bed';G2=R/'2026-09-26-w39-g2-identification'
sys.path[:0]=[str(G2),str(G2/'instrument'),str(G2/'body-correction')]
import native,body
from solver import solve_h3
from scipy.optimize import least_squares
root=Path.home()/'.cache/vitrea-archives/489db938a1e234a772ba7223d24fbaf76d137ef5d9e5b2421ed84a86894426b5/extracted'
# Find inventory location through metadata only.
roots=list(root.rglob('inventory.json'));assert len(roots)==1
w,reader=native.guarded(roots[0].parent,('calibration',))
out=Path.home()/'vitrea-w41/grounding/body'
rows=[]; gradients=[]
for cell,kind in sorted(reader.entries):
 sid=cell.split('/',1)[1]
 if kind!='crop' or sid not in reader.allowed:continue
 c=w.component(sid);bg=w.spec['backgrounds'][w.scenes[sid]['background']]
 if c['kind']=='none' or c.get('opaque'):continue
 if '-colour__' not in sid and bg['kind']=='solid':continue
 if bg['kind']!='solid' and c['kind']!='capsule-circular':continue
 runs,states=native.archive.unbundle(reader.read(cell,'crop'))
 runs=[r for r in runs if r['admitted'] and r['protocol']=='normal'];assert len(runs)==7
 payloads={k:native.archive.unpack(v) for k,v in states.items() if k in {r['state'] for r in runs}}
 p=next(iter(payloads.values()));sh=native.readers.shapes_of(p['component']);geo=native.readers.geometry(p['rgb'].shape[:2],sh,p['scale'])
 if bg['kind']=='solid':
  vals=np.array([native.readers.deep_body(payloads[r['state']]['rgb'],geo,0)['medianRGB'] for r in runs]);saved=json.loads(gzip.decompress(reader.read(cell,'statistics')))['statistics']
  for r,v in zip(runs,vals):assert v.tolist()==saved[r['state']]['members'][0]['deep']['medianRGB']
  rows.append(dict(cell=cell,sid=sid,scheme=p['scheme'],pose=p['pose'],scale=p['scale'],input=bg['srgb'],median=np.median(vals,axis=0).tolist(),bar=(.5+.5*np.ptp(vals,axis=0)).tolist(),runs=vals.tolist()))
 else:
  # Central straight band, trimmed 14 CSS px from either arc join; interior depths >=6/10/14.
  shape=sh[0];scale=p['scale'];x0,y0,x1,y1=shape.rect(scale);radius=min(shape.size)/2*scale
  xx=np.arange(p['rgb'].shape[1])+.5;band=(xx>=x0+radius+14*scale)&(xx<=x1-radius-14*scale)
  yy=np.arange(p['rgb'].shape[0])+.5;keep=(yy>=y0+6*scale)&(yy<=y1-6*scale)
  vals=np.array([payloads[r['state']]['rgb'][keep][:,band].mean(axis=1) for r in runs]);refs=np.array([payloads[r['state']]['noGlass'][keep][:,band].mean(axis=1) for r in runs])
  gradients.append(dict(cell=cell,sid=sid,scheme=p['scheme'],pose=p['pose'],scale=scale,background=bg,depth=np.minimum(yy[keep]-y0,y1-yy[keep]).tolist(),y=((yy[keep]-(y0+y1)/2)/scale).tolist(),median=np.median(vals,axis=0).tolist(),bar=(.5+.5*np.ptp(vals,axis=0)).tolist(),reference=np.median(refs,axis=0).tolist(),runs=vals.tolist()))
print('rows',len(rows),'gradients',len(gradients),flush=True)
(out/'readings.json').write_text(json.dumps(dict(generation=reader.generation,roles=['calibration'],rows=rows,gradients=gradients)))
fits=[]
for scheme in ['light','dark']:
 for pose in ['rest','inactive']:
  rr=[r for r in rows if r['scheme']==scheme and r['pose']==pose]
  f=np.array([np.mean([r['median'] for r in rr if r['sid'].startswith(f'neutral-{k}-colour')]) for k in [40,56,72,88,104,128,150]])/255
  cc=[r for r in rr if min(r['median'])>5 and max(r['median'])<250]
  x=np.array([r['input'] for r in cc])/255;y=np.array([r['median'] for r in cc])
  fit=solve_h3(x,f,y);q=fit['coefficients'];pred=body.h3(x,f,q)*255
  fits.append(dict(scheme=scheme,pose=pose,neutral=(f*255).tolist(),fit=fit,rows=[dict(cell=r['cell'],sid=r['sid'],scale=r['scale'],native=r['median'],input=r['input'],pred=p.tolist(),residual=(p-v).tolist()) for r,p,v in zip(cc,pred,y)]))
  print(scheme,pose,fit['upperCodes'],'F',f*255,flush=True)
(out/'h3.json').write_text(json.dumps(fits))
