import sys,json,gzip
from pathlib import Path
import numpy as np
sys.dont_write_bytecode=True
G2=Path('/Users/new/Developer/GitHub/designer/packages/calibration/results/2026-09-26-w39-g2-identification')
sys.path.insert(0,str(G2)); import native
ROOT=Path('/Users/new/.cache/vitrea-archives/489db938a1e234a772ba7223d24fbaf76d137ef5d9e5b2421ed84a86894426b5/extracted/archive')
w,r=native.guarded(ROOT,('calibration',))
rows=[]; cells=[]
for cell,kind in sorted(r.entries):
 if kind!='statistics':continue
 sid=cell.split('/',1)[1]
 if sid not in r.allowed or native.wave.native_only(w.component(sid)):continue
 records=[a for a in native.archive.recorded_statistics(r,cell) if a['admitted'] and a['protocol']=='normal']
 if not records:continue
 assert len(records)==7
 stats=[a['statistics'] for a in records]; first=stats[0]; comp=w.component(sid)
 cells.append(dict(cell=cell,scene=w.scenes[sid],component=comp,scheme=first['scheme'],pose=first['pose'],scale=first['scale']))
 for member,m in enumerate(first['members']):
  ms=[s['members'][member] for s in stats]
  deep=np.median([s['deep']['medianRGB'] for s in ms],axis=0)
  for i,b in enumerate(m['bins']):
   if b['shell'] is not None and not -3<=b['shell']<=3: continue
   if not b['pixels']:continue
   means=np.array([s['bins'][i]['meanRGB'] for s in ms]); bg=np.array([s['noGlassBins'][i]['meanRGB'] for s in ms]); cov=[v for v in m['coverage'].get('bins',[]) if (v['part'],v['side'],v['bin'],v['shell'])==(b['part'],b['side'],b['bin'],b['shell'])]
   rows.append(dict(cell=cell,member=member,background=w.scenes[sid]['background'],scheme=first['scheme'],pose=first['pose'],scale=first['scale'],**{k:b[k] for k in ['part','side','bin','shell','pixels','status']},deepRGB=deep.tolist(),native=np.median(means,axis=0).tolist(),backgroundRGB=np.median(bg,axis=0).tolist(),delta=np.median(means-bg,axis=0).tolist(),bar=(.5+.5*np.ptp(means-bg,axis=0)).tolist(),opaqueAlpha=cov[0]['alpha'] if cov else None))
out=Path('/Users/new/vitrea-w41/grounding/stroke')
(out/'reading.json').write_text(json.dumps(dict(inventory=r.generation,cells=cells,rows=rows)))
print(len(cells),len(rows),r.generation)
