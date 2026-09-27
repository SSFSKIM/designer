import sys
sys.dont_write_bytecode=True
from analyse import *
sys.path.insert(0,'/Users/new/Developer/GitHub/designer/packages/calibration/results/2026-09-26-w39-g2-identification')
import native
root=Path('/Users/new/.cache/vitrea-archives/489db938a1e234a772ba7223d24fbaf76d137ef5d9e5b2421ed84a86894426b5/extracted/archive')
w,reader=native.guarded(root,('calibration',))
materials=json.loads((Path(native.__file__).parent/'instrument/resolved-materials.json').read_text())
results=[]
for cell,c in cells.items():
 if c['scene']['background'] not in ['g128','g255'] or c['pose']!='rest' or c['component']!={'kind':'capsule-circular','size':[120,44],'position':[160,140]}:continue
 runs,states=native.archive.unbundle(reader.read(cell,'crop')); runs=[r for r in runs if r['admitted'] and r['protocol']=='normal']; assert len(runs)==7
 p=native.archive.unpack(states[runs[0]['state']]);shapes=native.readers.shapes_of(p['component']);s=p['scale']; hw=p['rgb'].shape[:2]
 geo=native.readers.geometry(hw,shapes,s);bins,labels=native.readers.edge_bins(geo)
 material=materials[c['scheme']+'-active'];m=material['outerShadow'];span=44
 t=np.clip((span-material['sizeSpanMin'])/(material['sizeSpanMax']-material['sizeSpanMin']),0,1); k=t*t*(3-2*t);blend=k*k*(3-2*k)
 b=p['noGlass'][0,0,1];thin=m['thinOcclusionMid'] if b==128 else m['thinOcclusionBright'];occ=(1-blend)*thin+blend*m['thickOcclusionAt96'];alpha=1-(1-occ)**(1/2.4)
 sigma=m['sigmaPx']+max(m['sigmaThinOffsetPx'],m['sigmaSlopePerSpan']*(44-m['sigmaSpanRefPx']))
 shift=native.readers.geometry(hw,shapes,s,translation=(0,m['offsetPx']*s))
 d=shift.d/s-m['spreadPx'];x=-d/sigma; fall=.5*(1+np.tanh(np.clip(.7978845608028654*(x+.044715*x**3),-20,20)))
 pred=-float(b)*alpha*fall
 for i,bn in enumerate(bins):
  if bn['pixels'] and bn['shell'] in [0,1,2,3] and ((bn['part']=='arc' and bn['bin'] in [0,4,8,12]) or bn['part']=='straight'):
   rr=next(r for r in rows if r['cell']==cell and r['part']==bn['part'] and r['shell']==bn['shell'] and r['bin']==bn['bin'])
   val=float(pred[labels==i].mean());results.append(dict(cell=cell,scheme=c['scheme'],scale=s,bg=c['scene']['background'],part=bn['part'],bin=bn['bin'],shell=bn['shell'],native=rr['delta'][1],shadow=val,residual=rr['delta'][1]-val,sigma=sigma,alpha=alpha))
(scratch/'shadow-reading.json').write_text(json.dumps(results))
for r in results:
 if r['shell']==0:print(r['scheme'],r['scale'],r['bg'],r['part'],r['bin'],'native/shadow/remain',*(round(r[k],5) for k in ['native','shadow','residual']),'sigma/alpha',r['sigma'],r['alpha'])
