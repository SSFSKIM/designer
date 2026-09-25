"""Match the normal repeat bar to each actual whole-pixel closure/diagnostic bin."""
import base64,gzip,json
import numpy as np
import identify
from law import HERE,edge
reader=edge.W.default_wave().reader(edge.G1/'repeat');result=[]
for r in identify.inputs():
 crop=json.loads(gzip.decompress(reader.read(r['cell'],'crop')))
 runs=[x for x in crop['runs'] if x['admitted'] and x['protocol']=='normal']
 states={s:edge.I.unpack(base64.b64decode(crop['states'][s])) for s in {x['state'] for x in runs}}
 p=states[runs[0]['state']];d,nx,ny,arc,angle,whole=edge.geometry(p);scale=p['scale']
 whole=whole if r['circular'] else (~arc)&(np.maximum(abs(nx),abs(ny))>1-1e-10)&(d<=-.5+1e-10)
 bins=[]
 for b in r['bins']:
  mask=whole&(arc if b['part']=='arc' else ~arc)&(angle==b['bin'])&(d>=b['shell'])&(d<b['shell']+1)
  assert int(mask.sum())==b['pixels']
  # Repeated identical states still have their run mapping below. Deduplication
  # saves arithmetic only: max over every run pair equals max over state pairs.
  values=np.zeros(3) if len(states)==1 else edge.bar([s['rgb'][mask] for s in states.values()])
  if b['admissible']:assert np.all(values<=1),'one-code tau needs a correction, not a rewrite'
  bins.append(dict(part=b['part'],shell=b['shell'],bin=b['bin'],pixels=b['pixels'],admissible=b['admissible'],barRGB=values.tolist(),tauRGB=np.maximum(1,values).tolist()))
 result.append(dict(cell=r['cell'],role=r['role'],closure=r['circular'],runStates=[x['state'] for x in runs],bins=bins))
edge.save(HERE/'closure-bars.json.gz',result)
maximum=max(max(b['barRGB']) for r in result for b in r['bins'] if b['admissible'])
print(json.dumps(dict(cells=len(result),bins=sum(len(r['bins']) for r in result),admittedMaximum=maximum,allToleranceOne=True)))
